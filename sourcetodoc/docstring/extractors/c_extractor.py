from enum import Enum, auto
from typing import Protocol, override

from ..extractor import Comment, Extractor

class CType(Enum):
    """Enumeration with C symbol types"""
    FUNCTION = auto()
    STRUCT = auto()
    UNION = auto()
    VARIABLE = auto()
    ENUM = auto()
    ENUM_CONSTANT = auto()
    TYPEDEF = auto()
    UNKNOWN = auto()


class CExtractor(Extractor[CType], Protocol):
    """Extracts comments from C++ source files"""
    @override
    def extract_comments(self, code: str) -> list[Comment[CType]]:
        ...
