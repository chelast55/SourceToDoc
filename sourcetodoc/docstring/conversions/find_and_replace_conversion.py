from re import Pattern
from typing import Any, override

from ..conversion import ConvEmpty, Conversion, ConvPresent, ConvResult
from ..extractor import Comment


class FindAndReplaceConversion(Conversion[Any]):
    def __init__(self, pattern: Pattern[str], replacement: str) -> None:
        self.pattern = pattern
        self.replacement = replacement

    @override
    def calc_conversion(self, comment: Comment[Any]) -> ConvResult:
        new_comment_text = self.pattern.sub(self.replacement, comment.comment_text)
        if comment.comment_text == new_comment_text:
            return ConvEmpty()
        else:
            return ConvPresent(new_comment_text)
