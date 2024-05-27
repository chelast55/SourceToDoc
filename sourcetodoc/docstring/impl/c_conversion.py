import re
from textwrap import indent
from typing import Optional, override

from openai import APIError

from ..conversion import (Conversion, ConversionEmpty, ConversionError,
                          ConversionPresent, ConversionResult,
                          ConversionUnsupported)
from ..extractor import BlockComment, Comment
from .c_extractor import CType
from .llm import LLM


class CLLMFunctionBlockCommentConversion(Conversion[CType]):
    # Matches "/** ... */"
    COMMENT_REGEX: str = r"/\*\*(?:.|\n)*?\*/"
    COMMENT_PATTERN = re.compile(COMMENT_REGEX, re.VERBOSE)

    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        self.system_prompt = "You are a coder that converts comments on c functions to doxygen style comments (Javadoc style) that start with \"/**\" without changing the text."

    @override
    def calc_conversion(self, comment: Comment[CType]) -> ConversionResult[CType]:
        match comment:
            case BlockComment(symbol_type=CType.FUNCTION) as bc if bc.comment_text.startswith("/**"):
                return ConversionEmpty(bc, "Comment starts with \"/**\"")
            case BlockComment(symbol_type=CType.FUNCTION) as bc:
                return self._handle_function_block_comment(bc)
            case _:
                return ConversionUnsupported(comment, "Not a block comment on a function")

    def _handle_function_block_comment(self, bc: BlockComment[CType]) -> ConversionResult[CType]:
        prompt = bc.comment_with_symbol_unindented()

        try:
            llm_output = self.llm.call_llm(self.system_prompt, prompt)
        except APIError as e:
            return ConversionError(bc, e.message)

        new_comment = self._extract_multi_comment(llm_output) # Extract only the "/** ... /*" part
        if new_comment is None:
            return ConversionError(bc, "No '/** ... /*' found in output of LLM", llm_output)

        new_comment = indent(new_comment, bc.indentation) # Add indentation
        new_comment = new_comment.removeprefix(bc.indentation) # Remove indentation on first line
        new_comment = new_comment.replace("/**", "/** AI_GENERATED", 1) # Add "AI_GENERATED" after "/**"
        return ConversionPresent(bc, new_comment)

    @staticmethod
    def _extract_multi_comment(result: str) -> Optional[str]:
        match = CLLMFunctionBlockCommentConversion.COMMENT_PATTERN.search(result)
        if match is not None:
            return match[0]
        else:
            return None
