import re
from textwrap import dedent, indent
from typing import Optional, override

from openai import OpenAI

from ..converter import (ConversionResult, ConversionEmpty, ConversionError,
                         ConversionPresent, Converter)
from ..extractor import BlockComment, Comment, CommentAfterMember
from .c_extractor import MULTI_COMMENT_PATTERN, CType


class CConverter(Converter[CType]):
    def __init__(self, client: OpenAI) -> None:
        self.client = client
        self.multi_comment_matcher = re.compile(MULTI_COMMENT_PATTERN, re.VERBOSE)

    @override
    def calc_docstring(self, comment: Comment[CType]) -> ConversionResult[CType]:
        if type(comment) is BlockComment and comment.comment_text.startswith("/**"):
            return ConversionEmpty(comment)
        
        result = self._convert_comment(comment)

        if result is not None:
            return ConversionPresent(comment, new_comment=result)
        else:
            return ConversionError(comment, message="Error")
    
    def _convert_comment(self, comment: Comment[CType]) -> Optional[str]:
        match comment:
            case BlockComment() as c:
                input = c.initial_comment_indentation + c.comment_text + "\n" + c.initial_comment_indentation + c.symbol_text
                input = dedent(input)
                result = self._call_llm(input)
                result = self._extract_multi_comment(result)
                if result is not None:
                    result = indent(result, c.initial_comment_indentation)
                    result = result.removeprefix(c.initial_comment_indentation)
            case CommentAfterMember() as c:
                raise NotImplementedError # TODO
                text = c.comment_text
                if text.startswith("/**"):
                    result = text.replace("/**", "/**<")
                elif text.startswith("/*"):
                    result = text.replace("/*", "/**<")
                elif text.startswith("//"):
                    result = text.replace("//", "///<")
            
        return result

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
            raise Exception

    def _extract_multi_comment(self, result: str) -> Optional[str]:
        match = self.multi_comment_matcher.search(result)
        if match is not None:
            return match[0]
        else:
            return None
