from typing import Mapping, override

from clang.cindex import Cursor, CursorKind, TranslationUnit

from ..extractor import Comment, Extractor
from .c_type import CType
from .libclang_extractor import LibclangExtractor


class CLibclangExtractor(Extractor[CType]):
    """
    Extracts coments from C source code that are associated with
    symbols.
    """
    type_map: Mapping[CursorKind, CType] = {
        CursorKind.FUNCTION_DECL: CType.FUNCTION,
        CursorKind.STRUCT_DECL: CType.STRUCT,
        CursorKind.UNION_DECL: CType.UNION,
        CursorKind.FIELD_DECL: CType.FIELD,
        CursorKind.ENUM_DECL: CType.ENUM,
        CursorKind.ENUM_CONSTANT_DECL: CType.ENUM_CONSTANT,
        CursorKind.VAR_DECL: CType.VARIABLE,
        CursorKind.TYPEDEF_DECL: CType.TYPEDEF,
    }

    def __init__(self) -> None:
        self.extractor = LibclangExtractor(
            self.__class__._translation_unit_from_code,
            self.__class__._get_type
        )

    @override
    def extract_comments(self, code: str) -> list[Comment[CType]]:
        return self.extractor.extract_comments(code)

    @classmethod
    def _translation_unit_from_code(cls, code: str) -> TranslationUnit:
        fake_path = "unsaved.c"
        unsaved = [(fake_path, code)]

        tu: TranslationUnit = TranslationUnit.from_source(  # type: ignore
            fake_path,
            ["-fparse-all-comments"],
            unsaved_files=unsaved,
            options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
        )
        return tu

    @classmethod
    def _get_type(cls, cursor: Cursor) -> CType:
        kind: CursorKind = cursor.kind  # type: ignore
        if kind in cls.type_map:
            return cls.type_map[kind]  # type: ignore
        else:
            return CType.UNKNOWN
