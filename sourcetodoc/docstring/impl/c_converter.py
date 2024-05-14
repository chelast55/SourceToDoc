import re
from textwrap import dedent, indent
from typing import Optional, override

from openai import APIError, OpenAI

from ..converter import (ConversionEmpty, ConversionError, ConversionPresent,
                         ConversionResult, ConversionUnsupported, Converter)
from ..extractor import BlockComment, Comment, CommentAfterMember
from .c_extractor import MULTI_COMMENT_PATTERN, CType


class CConverter(Converter[CType]):
    def __init__(self, client: OpenAI) -> None:
        self.client = client
        self.multi_comment_matcher = re.compile(MULTI_COMMENT_PATTERN, re.VERBOSE)

    @override
    def calc_docstring(self, comment: Comment[CType]) -> ConversionResult[CType]:
        match comment:
            case BlockComment() as bc:
                if bc.comment_text.startswith("/**"):
                    return ConversionEmpty(bc)

                # Remove indentation
                input = bc.initial_comment_indentation + bc.comment_text + "\n" + bc.initial_comment_indentation + bc.symbol_text 
                input = dedent(input)

                try:
                    result = self._call_llm(input)
                except APIError as e:
                    return ConversionError(bc, e.message)

                result = self._extract_multi_comment(result) # Extract only the "/** ... /*" part
                if result is not None:
                    result = indent(result, bc.initial_comment_indentation) # Add indentation
                    result = result.removeprefix(bc.initial_comment_indentation) # Remove initial indentation
                    result = result.replace("/**", "/** AI_GENERATED", 1) # Adds "AI_GENERATED" to the beginning of the new comment
                    return ConversionPresent(bc, result)
                else:
                    return ConversionError(bc, "No '/** ... /*' found in output of LLM")

            case CommentAfterMember() as cm:
                return ConversionUnsupported(cm)

    def _call_llm(self, input: str) -> str:
        response = self.client.chat.completions.create(
            model="phi3",
            seed=0, # You convert comments to doxygen style comments. You only change the format of the input comments.
            messages=[
                {"role": "system", "content": "You are a coder that converts comments to doxygen style comments without changing the text."},
                {"role": "user", "content": input}
        ])
        result = response.choices[0].message.content
        if result is not None:
            return result
        else:
            raise RuntimeError

    def _extract_multi_comment(self, result: str) -> Optional[str]:
        match = self.multi_comment_matcher.search(result)
        if match is not None:
            return match[0]
        else:
            return None
