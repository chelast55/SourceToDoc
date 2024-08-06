from typing import override

from ..comment_style import CommentStyle
from ..conversion import Conversion, ConvResult, ConvUnsupported
from ..extractor import Comment
from ..extractors.c_type import CType
from ..extractors.cxx_type import CXXType
from .llm import LLM
from .llm_conversion_helper import LLMConversionHelper


class LLMConversion(Conversion[CType | CXXType]):
    """Converts comments on C functions with a LLM."""

    _CXX_INCLUDE_TYPES: set[CXXType] = {
        CXXType.CONSTRUCTOR,
        CXXType.FUNCTION,
        CXXType.FUNCTION_TEMPLATE,
        CXXType.METHOD,
    }

    default_c_system_prompt = "You are a coder that converts comments on c functions to doxygen style comments that start with \"/**\" without changing the text."
    default_cxx_system_prompt = "You are a coder that converts comments on C++ functions to doxygen style comments that start with \"/**\" without changing the text."

    def __init__(self, llm: LLM) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        llm : LLM
            The LLM.
        """
        self.llm_helper = LLMConversionHelper[CType | CXXType](llm)

    @override
    def calc_conversion(self, comment: Comment[CType | CXXType]) -> ConvResult:
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
            `CType.FUNCTION`.
        """
        if comment.symbol_type is CType.FUNCTION:
            return self.llm_helper.calc_conversion_with_llm(
                comment,
                self.__class__.default_c_system_prompt,
                CommentStyle.JAVADOC_BLOCK
            )
        elif comment.symbol_type in self.__class__._CXX_INCLUDE_TYPES:
            return self.llm_helper.calc_conversion_with_llm(
                comment,
                self.__class__.default_cxx_system_prompt,
                CommentStyle.JAVADOC_BLOCK
            )
        else:
            return ConvUnsupported("Comment is not attached to a C function")
