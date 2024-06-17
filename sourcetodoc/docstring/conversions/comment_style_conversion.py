from typing import Any, override

from ..comment_style import CommentStyle, CommentStyler
from ..conversion import (ConvEmpty, Conversion, ConvPresent, ConvResult,
                          ConvUnsupported)
from ..extractor import Comment


class CommentStyleConversion(Conversion[Any]):
    """
    Changes the comment style of comments.
    """
    def __init__(self, target_style: CommentStyle) -> None:
        self.target_style = target_style
    
    @override
    def calc_conversion(self, comment: Comment[Any]) -> ConvResult:
        match CommentStyler.parse_comment(comment.comment_text):
            case CommentStyler(_, style=self.target_style):
                return ConvEmpty("Comment has already that style")
            case CommentStyler(content, _):
                new_comment_text = CommentStyler(
                    content,
                    self.target_style
                ).construct_comment(comment.symbol_indentation)
                return ConvPresent(new_comment_text)
            case None:
                return ConvUnsupported("Comment can not be parsed")
