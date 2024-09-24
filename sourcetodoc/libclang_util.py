import ctypes
from typing import Iterator

from clang.cindex import (Cursor, SourceLocation, SourceRange, conf,
                          register_function)


def clang_get_comment_range(cursor: Cursor) -> SourceRange:
    return conf.lib.clang_Cursor_getCommentRange(cursor)


def clang_location_is_from_main_file(location: SourceLocation) -> bool:
    return conf.lib.clang_Location_isFromMainFile(location) != 0


def walk_preorder_only_main_file(node: Cursor) -> Iterator[Cursor]:
    yield node
    for child in node.get_children():
        if clang_location_is_from_main_file(child.location):
            for descendant in walk_preorder_only_main_file(child):
                yield descendant


def _register_functions() -> None:
    """
    Adds necessary function bindings in the cindex module.
    """
    register_function(conf.lib, ("clang_Cursor_getCommentRange", [Cursor], SourceRange), False)
    register_function(conf.lib, ("clang_Location_isFromMainFile", [SourceLocation], ctypes.c_int), False)


_register_functions()
