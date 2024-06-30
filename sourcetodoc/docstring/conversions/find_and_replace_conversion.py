from re import Pattern
from typing import Any, override

from ..conversion import ConvEmpty, Conversion, ConvPresent, ConvResult
from ..extractor import Comment


class FindAndReplaceConversion(Conversion[Any]):
    """Converts comments by find and replace."""

    def __init__(self, find_pattern: Pattern[str], replacement: str) -> None:
        """
        Constructs a new object.

        Parameters
        ----------
        find_pattern : Pattern[str]
            The pattern to find substrings.
        replacement : str
            The replacement text.
        """
        self.find_pattern = find_pattern
        self.replacement = replacement

    @override
    def calc_conversion(self, comment: Comment[Any]) -> ConvResult:
        """
        Calculates new comments by finding and replacing substrings.

        Every substring that is matched by `find_pattern` is
        replaced be `replacement`.

        Parameters
        ----------
        comment : Comment[Any]
            The comment.

        Returns
        -------
        ConvResult
            A ConvPresent object if the new comment text has changed,
            else ConvEmpty
        """
        new_comment_text = self.find_pattern.sub(self.replacement, comment.comment_text)
        if comment.comment_text == new_comment_text:
            return ConvEmpty()
        else:
            return ConvPresent(new_comment_text)
