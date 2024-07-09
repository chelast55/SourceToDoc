from typing import override

from ..comment_style import CommentStyle
from ..conversion import Conversion, ConvResult, ConvUnsupported
from ..extractors.cxx_extractor import Comment, CXXType
from .llm import LLM
from .llm_conversion_helper import LLMConversionHelper


class CXXLLMConversion(Conversion[CXXType]):
    """Converts comments on C++ functions or similar with a LLM."""

    default_system_prompt = "You are a coder that converts comments on C++ functions to doxygen style comments that start with \"/**\" without changing the text."

    _INCLUDE_TYPES: set[CXXType] = {
        CXXType.CONSTRUCTOR,
        CXXType.FUNCTION,
        CXXType.FUNCTION_TEMPLATE,
        CXXType.METHOD,
    }

    def __init__(self, llm: LLM, system_prompt: str = default_system_prompt) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        llm : LLM
            The LLM.
        system_prompt : str, optional
            The system prompt that is passed to the LLM, by default default_system_prompt
        """
        self.llm_helper = LLMConversionHelper[CXXType](llm)
        self.system_prompt = system_prompt

    @override
    def calc_conversion(self, comment: Comment[CXXType]) -> ConvResult:
        """
        Calculates a new Doxygen JavaDoc style comments with a LLM.

        See: `LLMConversionHelper`.

        Parameters
        ----------
        comment : Comment[CXXType]
            The comment.

        Returns
        -------
        ConvResult
            A ConvUnsupported object if `comment.symbol_type` is not
            one of the following types:
            `CXXType.CONSTRUCTOR`,
            `CXXType.FUNCTION`,
            `CXXType.FUNCTION_TEMPLATE`,
            `CXXType.METHOD`.
        """
        if comment.symbol_type in self.__class__._INCLUDE_TYPES:
            return self.llm_helper.calc_conversion_with_llm(
                comment,
                self.system_prompt,
                CommentStyle.JAVADOC_BLOCK
            )
        else:
            return ConvUnsupported("Comment is not attached to either of those: "
                                   "constructor, function, function template, method")
