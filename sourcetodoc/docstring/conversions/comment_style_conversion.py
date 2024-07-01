from typing import Any, override

from ..comment_style import CommentStyle, CommentStyler
from ..conversion import (ConvEmpty, Conversion, ConvPresent, ConvResult,
                          ConvUnsupported)
from ..extractor import Comment


class CommentStyleConversion(Conversion[Any]):
    """Changes the comment style of comments."""

    def __init__(self, target_style: CommentStyle) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        target_style : CommentStyle
            The comment style to convert into.
        """
        self.target_style = target_style
    
    @override
    def calc_conversion(self, comment: Comment[Any]) -> ConvResult:
        """
        Calculates new comments with the specified comment style.

        The comment style is specifed by `self.target_style`.

        Parameters
        ----------
        comment : Comment[Any]
            The comment.

        Returns
        -------
        ConvResult
            A ConvPresent object if `comment` has a different style than
            `self.target_style`, else a ConvEmpty object.
            A ConvUnsupported if `comment` cannot be parsed.
        """
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
                return ConvUnsupported("Comment cannot be parsed")
