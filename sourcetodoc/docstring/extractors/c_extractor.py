from enum import Enum, auto
from typing import Protocol, override

from ..extractor import Comment, Extractor

class CType(Enum):
    FUNCTION = auto()
    STRUCT = auto()
    UNION = auto()
    VARIABLE = auto()
    ENUM = auto()
    ENUM_CONSTANT = auto()
    TYPEDEF = auto()
    UNKNOWN = auto()


class CExtractor(Extractor[CType], Protocol):
    @override
    def extract_comments(self, code: str) -> list[Comment[CType]]:
        ...
