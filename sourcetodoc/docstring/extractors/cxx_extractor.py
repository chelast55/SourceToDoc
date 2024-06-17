from enum import Enum, auto
from typing import Protocol

from ..extractor import Comment, Extractor


class CXXType(Enum):
    DESTRUCTOR = auto()
    ACCESS_SPECIFIER = auto()
    CLASS = auto()
    ENUM = auto()
    FUNCTION = auto()
    FUNCTION_TEMPLATE = auto()
    VARIABLE = auto()
    CONSTRUCTOR = auto()
    METHOD = auto()
    NAMESPACE = auto()
    CLASS_TEMPLATE = auto()
    FIELD = auto()
    UNKNOWN = auto()


class CXXExtractor(Extractor[CXXType], Protocol):
    def extract_comments(self, code: str) -> list[Comment[CXXType]]:
        ...
