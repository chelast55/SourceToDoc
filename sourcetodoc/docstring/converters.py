"""This module contains converters"""

from re import Pattern

from .conversions.find_and_replace_conversion import FindAndReplaceConversion
from .comment_style import CommentStyle
from .conversions.c_llm_conversion import CLLMConversion
from .conversions.command_style_conversion import CommandStyleConversion
from .conversions.comment_style_conversion import CommentStyleConversion
from .conversions.cxx_llm_conversion import CXXLLMConversion
from .conversions.llm import LLM
from .converter import Converter
from .extractors.c_extractor import CType
from .extractors.c_pylibclang_extractor import CPylibclangExtractor
from .extractors.cxx_extractor import CXXType
from .extractors.cxx_pylibclang_extractor import CXXPylibclangExtractor

_c_regex = r".*\.[ch]"
_cxx_regex = r".*\.(c(pp|xx|c)|h(pp|xx|h)?)"


def c_comment_style_converter(style: CommentStyle, only_after_member: bool) -> Converter[CType]:
    """Changes the style of comments in C source files to `style`."""
    return Converter[CType](
        CPylibclangExtractor(),
        CommentStyleConversion(style, only_after_member), 
        _c_regex
    )


def cxx_comment_style_converter(style: CommentStyle, only_after_member: bool) -> Converter[CXXType]:
    """Changes the style of comments in C++ source files to `style`."""
    return Converter[CXXType](
        CXXPylibclangExtractor(),
        CommentStyleConversion(style, only_after_member), 
        _cxx_regex
    )


def c_function_comment_llm_converter(llm: LLM) -> Converter[CType]:
    """Converts comments with a LLM in C source files."""
    return Converter(
        CPylibclangExtractor(),
        CLLMConversion(llm),
        _c_regex
    )


def cxx_function_comment_llm_converter(llm: LLM) -> Converter[CXXType]:
    """Converts comments with a LLM in C++ source files."""
    return Converter(
        CXXPylibclangExtractor(),
        CXXLLMConversion(llm),
        _cxx_regex
    )


def c_command_style_converter(javadoc_style: bool) -> Converter[CType]:
    """Changes the command style of comments in C source files."""
    return Converter(
        CPylibclangExtractor(),
        CommandStyleConversion(javadoc_style),
        _c_regex
    )


def cxx_command_style_converter(javadoc_style: bool) -> Converter[CXXType]:
    """Changes the command style of comments in C++ source files."""
    return Converter(
        CXXPylibclangExtractor(),
        CommandStyleConversion(javadoc_style),
        _cxx_regex
    )


def c_find_and_replace_converter(find_pattern: Pattern[str], replacement: str) -> Converter[CType]:
    """Finds and replaces substrings in C source files."""
    return Converter(
        CPylibclangExtractor(),
        FindAndReplaceConversion(find_pattern, replacement),
        _c_regex
    )


def cxx_find_and_replace_converter(find_pattern: Pattern[str], replacement: str) -> Converter[CXXType]:
    """Finds and replaces substrings in C++ source files."""
    return Converter(
        CXXPylibclangExtractor(),
        FindAndReplaceConversion(find_pattern, replacement),
        _cxx_regex
    )
