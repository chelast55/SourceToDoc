import re
from typing import Optional, override

from openai import OpenAI

from ..converter import (ConversionResult, ConversionEmpty, ConversionError,
                         ConversionPresent, Converter)
from ..extractor import Comment
from .c_extractor import MULTI_COMMENT_PATTERN, CType


class CConverter(Converter[CType]):
    def __init__(self, client: OpenAI) -> None:
        self.client = client
        self.multi_comment_matcher = re.compile(MULTI_COMMENT_PATTERN, re.VERBOSE)

    @override
    def calc_docstring(self, comment: Comment[CType]) -> ConversionResult[CType]:
        if comment.comment_text.startswith("/**"):
            return ConversionEmpty(comment)
        
        llm_result = self._call_llm(comment)
        if llm_result is not None:
            comment_result = self._extract_multi_comment(llm_result)
            if comment_result is not None:
                return ConversionPresent(comment, new_comment=comment_result)

        return ConversionError(comment, message="Error")

    def _call_llm(self, comment: Comment[CType]):
        response = self.client.chat.completions.create(
            model="phi3",
            seed=0, # You convert comments to doxygen style comments. You only change the format of the input comments.
            messages=[
                {"role": "system", "content": "You are a coder that converts comments to doxygen style comments without changing the text."},
                {"role": "user", "content": comment.comment_text + comment.symbol_text}
        ])
        return response.choices[0].message.content
    
    def _extract_multi_comment(self, result: str) -> Optional[str]:
        match = self.multi_comment_matcher.search(result)
        if match is not None:
            return match[0]
        else:
            return None
