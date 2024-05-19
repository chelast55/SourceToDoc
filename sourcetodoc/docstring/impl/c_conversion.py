import re
from textwrap import dedent, indent
from typing import Optional, override

from openai import APIError, OpenAI

from ..conversion import (ConversionEmpty, ConversionError, ConversionPresent,
                         ConversionResult, ConversionUnsupported, Conversion)
from ..extractor import BlockComment, Comment
from .c_extractor import MULTI_COMMENT_PATTERN, CType


class CConversion(Conversion[CType]):

    multi_comment_matcher = re.compile(MULTI_COMMENT_PATTERN, re.VERBOSE)

    def __init__(self, client: OpenAI) -> None:
        self.client = client

    @override
    def calc_conversion(self, comment: Comment[CType]) -> ConversionResult[CType]:
        match comment:
            case BlockComment() as bc if bc.symbol_type is CType.FUNCTION_MULTI_COMMENT:
                return self.handle_function_block_comment(bc)
            case _:
                return ConversionUnsupported(comment)

    def handle_function_block_comment(self, bc: BlockComment[CType]) -> ConversionResult[CType]:
        if bc.comment_text.startswith("/**"):
            return ConversionEmpty(bc)
        
        # Remove indentation
        input = (bc.initial_comment_indentation + bc.comment_text + "\n" +
                 bc.initial_comment_indentation + bc.symbol_text)
        input = dedent(input)
        try:
            result = self._call_llm(input)
        except APIError as e:
            return ConversionError(bc, e.message)
        result = self._extract_multi_comment(result) # Extract only the "/** ... /*" part
        if result is not None:
            result = indent(result, bc.initial_comment_indentation) # Add indentation
            result = result.removeprefix(bc.initial_comment_indentation) # Remove initial indentation
            result = result.replace("/**", "/** AI_GENERATED", 1) # Adds "AI_GENERATED" after "/**"
            return ConversionPresent(bc, result)
        else:
            return ConversionError(bc, "No '/** ... /*' found in output of LLM")

    def _call_llm(self, input: str) -> str:
        response = self.client.chat.completions.create(
            model="phi3",
            seed=0,
            messages=[
                {"role": "system", "content": "You are a coder that converts comments on c functions to doxygen style comments that start with \"/**\" without changing the text."},
                {"role": "user", "content": input}
        ])
        result = response.choices[0].message.content
        if result is not None:
            return result
        else:
            raise RuntimeError

    @staticmethod
    def _extract_multi_comment(result: str) -> Optional[str]:
        match = CConversion.multi_comment_matcher.search(result)
        if match is not None:
            return match[0]
        else:
            return None
