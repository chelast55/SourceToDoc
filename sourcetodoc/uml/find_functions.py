import os
from enum import Enum, auto
from pathlib import Path
from typing import Callable, Iterable, Iterator

from clang.cindex import (CompilationDatabase, CompileCommand, Cursor,
                          CursorKind, TranslationUnit, AccessSpecifier)

from ..libclang_util import walk_preorder_only_main_file
from .function_identifier import FunctionIdentifier


class FindOption(Enum):
    """
    ALL:
        Find all functions.
    EXCLUDE_PRIVATE_AND_PROTECTED:
        Find all public functions.
    ONLY_MAIN_FUNCTION:
        Find all functions that starts with `main(` that is not in a namespace or a class (e.g. `A::main()` will be excluded).
    """
    ALL = auto()
    EXCLUDE_PRIVATE_AND_PROTECTED = auto()
    ONLY_MAIN_FUNCTION = auto()

def _is_private_or_protected(node: Cursor) -> bool:
    return node.access_specifier in {AccessSpecifier.PRIVATE, AccessSpecifier.PROTECTED}

def _always_false(_: Cursor) -> bool:
    return False

def find_functions_with_libclang(compilation_db_dir: Path, find_option: FindOption) -> Iterator[FunctionIdentifier]:
    has_invalid_visibility: Callable[[Cursor], bool]
    if find_option is FindOption.EXCLUDE_PRIVATE_AND_PROTECTED:
        has_invalid_visibility = _is_private_or_protected
    else:
        has_invalid_visibility = _always_false

    # Temporary change of cwd
    saved_cwd: Path = Path.cwd()
    os.chdir(compilation_db_dir)

    found_functions: set[FunctionIdentifier] = set()

    cdb: CompilationDatabase = CompilationDatabase.fromDirectory(str(compilation_db_dir))
    commands: Iterable[CompileCommand] = cdb.getAllCompileCommands() # Includes filenames
    for command in commands:
        # Populate argument list
        file_args: list[str] = []
        for argument in command.arguments:
            file_args.append(argument)
        # Create translation unit
        filename: str = command.filename
        code = Path(filename).read_text()
        tu: TranslationUnit = TranslationUnit.from_source(None, args=file_args, unsaved_files=[(filename, code)])
        # Iterate over AST
        for node in walk_preorder_only_main_file(tu.cursor):
            if _is_non_empty_function(node, code):
                if has_invalid_visibility(node):
                    continue
                # Get identifier in the form "...::<namespace|class>::<function_signature>"
                identifier_items: list[str] = [node.displayname]
                parent: Cursor = node.semantic_parent
                while parent.kind in (CursorKind.NAMESPACE, CursorKind.CLASS_DECL):
                    identifier_items.append(parent.displayname)
                    parent = parent.semantic_parent

                function_identifier = FunctionIdentifier(tuple(reversed(identifier_items)))
                if function_identifier not in found_functions:
                    found_functions.add(function_identifier)
                    yield function_identifier

    # Restore old cwd
    os.chdir(saved_cwd)

def _is_non_empty_function(node: Cursor, code: str) -> bool:
    if node.kind in {
        CursorKind.DESTRUCTOR,
        CursorKind.FUNCTION_DECL,
        CursorKind.FUNCTION_TEMPLATE,
        CursorKind.CONSTRUCTOR,
        CursorKind.CXX_METHOD
    }:
        for child in node.get_children():
            if child.kind == CursorKind.COMPOUND_STMT:
                # Because "child" somehow has no children:
                # Check if function body is not empty
                start = child.extent.start.offset + 1 # + 1 to exclude opening "{"
                end = child.extent.end.offset - 1 # - 1 to exclude closing "}"
                return not code[start:end].isspace() # Is {...} empty?
    return False
