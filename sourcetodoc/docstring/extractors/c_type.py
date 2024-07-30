from enum import Enum, auto


class CType(Enum):
    """Enumeration with C symbol types"""
    FUNCTION = auto()
    STRUCT = auto()
    UNION = auto()
    FIELD = auto()
    VARIABLE = auto()
    ENUM = auto()
    ENUM_CONSTANT = auto()
    TYPEDEF = auto()
    UNKNOWN = auto()
