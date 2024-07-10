from typing import Mapping, override

import pylibclang._C as C
from pylibclang.cindex import (Cursor, CursorKind,  # type: ignore
                               TranslationUnit)

from .c_extractor import CExtractor, Comment, CType
from .pylibclang_extractor import PylibclangExtractor


class CPylibclangExtractor(CExtractor):
    """
    Extracts coments from C source code that are associated with
    symbols.
    """
    type_map: Mapping[C.CXCursorKind, CType] = {
        C.CXCursorKind.CXCursor_FunctionDecl: CType.FUNCTION,
        C.CXCursorKind.CXCursor_StructDecl: CType.STRUCT,
        C.CXCursorKind.CXCursor_UnionDecl: CType.UNION,
        C.CXCursorKind.CXCursor_FieldDecl: CType.VARIABLE,
        C.CXCursorKind.CXCursor_EnumDecl: CType.ENUM,
        C.CXCursorKind.CXCursor_EnumConstantDecl: CType.ENUM_CONSTANT,
        C.CXCursorKind.CXCursor_VarDecl: CType.VARIABLE,
        C.CXCursorKind.CXCursor_TypedefDecl: CType.TYPEDEF,
    }

    def __init__(self) -> None:
        self.extractor = PylibclangExtractor(
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
