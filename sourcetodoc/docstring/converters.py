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

c_regex = r".*\.[ch]"
cxx_regex = r".*\.(c(pp|xx|c)|h(pp|xx|h)?)"


def c_comment_style_converter(style: CommentStyle) -> Converter[CType]:
    return Converter[CType](
        CPylibclangExtractor(),
        CommentStyleConversion(style), 
        c_regex
    )


def cxx_comment_style_converter(style: CommentStyle) -> Converter[CXXType]:
    return Converter[CXXType](
        CXXPylibclangExtractor(),
        CommentStyleConversion(style), 
        cxx_regex
    )


def c_function_comment_llm_converter(llm: LLM) -> Converter[CType]:
    return Converter(
        CPylibclangExtractor(),
        CLLMConversion(llm),
        c_regex
    )


def cxx_function_comment_llm_converter(llm: LLM) -> Converter[CXXType]:
    return Converter(
        CXXPylibclangExtractor(),
        CXXLLMConversion(llm),
        cxx_regex
    )


def c_command_style_converter(javadoc_style: bool) -> Converter[CType]:
    return Converter(
        CPylibclangExtractor(),
        CommandStyleConversion(javadoc_style),
        c_regex
    )
