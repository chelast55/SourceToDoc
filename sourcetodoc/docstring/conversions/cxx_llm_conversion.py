from typing import override

from ..comment_style import CommentStyle
from ..conversion import Conversion, ConvResult, ConvUnsupported
from ..extractors.cxx_extractor import Comment, CXXType
from .llm import LLM
from .llm_conversion_helper import LLMConversionHelper


class CXXLLMConversion(Conversion[CXXType]):
    system_prompt = "You are a coder that converts comments on C++ functions to doxygen style comments that start with \"/**\" without changing the text."

    _INCLUDE_TYPES: set[CXXType] = {
        CXXType.CONSTRUCTOR,
        CXXType.FUNCTION,
        CXXType.FUNCTION_TEMPLATE,
        CXXType.METHOD,
    }

    def __init__(self, llm: LLM) -> None:
        self.llm_helper = LLMConversionHelper[CXXType](llm)

    @override
    def calc_conversion(self, comment: Comment[CXXType]) -> ConvResult:
        if comment.symbol_type in self.__class__._INCLUDE_TYPES:
            return self.llm_helper.calc_conversion_with_llm(
                comment,
                self.__class__.system_prompt,
                CommentStyle.JAVADOC_BLOCK
            )
        else:
            return ConvUnsupported("Comment is not attached to either of those: "
                                   "constructor, function, function template, method")
