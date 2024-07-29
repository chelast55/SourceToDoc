from enum import Enum, auto


class CXXType(Enum):
    """Enumeration with C++ symbol types"""
    DESTRUCTOR = auto()
    ACCESS_SPECIFIER = auto()
    CLASS = auto()
    ENUM = auto()
    ENUM_CONSTANT = auto()
    FUNCTION = auto()
    FUNCTION_TEMPLATE = auto()
    VARIABLE = auto()
    CONSTRUCTOR = auto()
    METHOD = auto()
    NAMESPACE = auto()
    CLASS_TEMPLATE = auto()
    FIELD = auto()
    UNKNOWN = auto()
