from typing import Mapping, override

from clang.cindex import Cursor, CursorKind, TranslationUnit

from ..extractor import Extractor, Comment
from .cxx_type import CXXType
from .libclang_extractor import LibclangExtractor


class CXXLibclangExtractor(Extractor[CXXType]):
    """
    Extracts comments from C++ source code that are associated with
    symbols.
    """
    type_map: Mapping[CursorKind, CXXType] = {
        CursorKind.DESTRUCTOR: CXXType.DESTRUCTOR,
        CursorKind.CXX_ACCESS_SPEC_DECL: CXXType.ACCESS_SPECIFIER,
        CursorKind.CLASS_DECL: CXXType.CLASS,
        CursorKind.ENUM_DECL: CXXType.ENUM,
        CursorKind.ENUM_CONSTANT_DECL: CXXType.ENUM_CONSTANT,
        CursorKind.FUNCTION_DECL: CXXType.FUNCTION,
        CursorKind.FUNCTION_TEMPLATE: CXXType.FUNCTION_TEMPLATE,
        CursorKind.VAR_DECL: CXXType.VARIABLE,
        CursorKind.CONSTRUCTOR: CXXType.CONSTRUCTOR,
        CursorKind.CXX_METHOD: CXXType.METHOD,
        CursorKind.NAMESPACE: CXXType.NAMESPACE,
        CursorKind.CLASS_TEMPLATE: CXXType.CLASS_TEMPLATE,
        CursorKind.FIELD_DECL: CXXType.FIELD,
    }

    def __init__(self) -> None:
        self.extractor = LibclangExtractor(
            self.__class__._translation_unit_from_source,
            self.__class__._get_type
        )

    @override
    def extract_comments(self, code: str) -> list[Comment[CXXType]]:
        return self.extractor.extract_comments(code)

    @classmethod
    def _translation_unit_from_source(cls, code: str) -> TranslationUnit:
        fake_path = "unsaved.cpp"
        unsaved = [(fake_path, code)]

        tu: TranslationUnit = TranslationUnit.from_source(  # type: ignore
            fake_path,
            ["-fparse-all-comments"],
            unsaved_files=unsaved,
            options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
        )
        return tu

    @classmethod
    def _get_type(cls, cursor: Cursor) -> CXXType:
        kind: CursorKind = cursor.kind  # type: ignore
        if kind in cls.type_map:
            return cls.type_map[kind]  # type: ignore
        else:
            return CXXType.UNKNOWN
