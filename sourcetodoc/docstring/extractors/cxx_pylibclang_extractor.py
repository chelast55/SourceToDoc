from typing import Mapping, override

import pylibclang._C as C
from pylibclang.cindex import (Cursor, CursorKind,  # type: ignore
                               TranslationUnit)

from .cxx_extractor import Comment, CXXExtractor, CXXType
from .pylibclang_extractor import PylibclangExtractor


class CXXPylibclangExtractor(CXXExtractor):
    """
    Extracts comments from C++ source code that are associated with
    symbols.
    """
    type_map: Mapping[C.CXCursorKind, CXXType] = {
        C.CXCursorKind.CXCursor_Destructor: CXXType.DESTRUCTOR,
        C.CXCursorKind.CXCursor_CXXAccessSpecifier: CXXType.ACCESS_SPECIFIER,
        C.CXCursorKind.CXCursor_ClassDecl: CXXType.CLASS,
        C.CXCursorKind.CXCursor_EnumDecl: CXXType.ENUM,
        C.CXCursorKind.CXCursor_FunctionDecl: CXXType.FUNCTION,
        C.CXCursorKind.CXCursor_FunctionTemplate: CXXType.FUNCTION_TEMPLATE,
        C.CXCursorKind.CXCursor_VarDecl: CXXType.VARIABLE,
        C.CXCursorKind.CXCursor_Constructor: CXXType.CONSTRUCTOR,
        C.CXCursorKind.CXCursor_CXXMethod: CXXType.METHOD,
        C.CXCursorKind.CXCursor_Namespace: CXXType.NAMESPACE,
        C.CXCursorKind.CXCursor_ClassTemplate: CXXType.CLASS_TEMPLATE,
        C.CXCursorKind.CXCursor_FieldDecl: CXXType.FIELD,
    }

    def __init__(self) -> None:
        self.extractor = PylibclangExtractor(
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
