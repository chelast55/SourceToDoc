from typing import override

from ..comment_style import CommentStyle
from ..conversion import Conversion, ConvResult, ConvUnsupported
from ..extractors.c_extractor import Comment, CType
from .llm import LLM
from .llm_conversion_helper import LLMConversionHelper


class CLLMConversion(Conversion[CType]):
    default_system_prompt = "You are a coder that converts comments on c functions to doxygen style comments that start with \"/**\" without changing the text."

    def __init__(self, llm: LLM, system_prompt: str = default_system_prompt) -> None:
        self.llm_helper = LLMConversionHelper[CType](llm)
        self.system_prompt = system_prompt

    @override
    def calc_conversion(self, comment: Comment[CType]) -> ConvResult:
        if comment.symbol_type is CType.FUNCTION:
            return self.llm_helper.calc_conversion_with_llm(
                comment,
                self.__class__.default_system_prompt,
                CommentStyle.JAVADOC_BLOCK
            )
        else:
            return ConvUnsupported("Comment is not attached to a C")
