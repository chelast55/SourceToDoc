from typing import Any, override

from ..command_style import CommandStyle
from ..comment_styler import CommentStyler
from ..conversion import (ConvEmpty, Conversion, ConvPresent, ConvResult,
                          ConvUnsupported)
from ..extractor import Comment


class CommandStyleConversion(Conversion[Any]):
    """
    Replaces `\\command` to `@command` or vice versa in Doxygen style comments.
    """
    def __init__(self, javadoc_style: bool) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        javadoc_style : bool
            If set to True, the command style is `@command`, else `\\command`
        """
        if javadoc_style:
            self._sub_func = CommandStyle.sub_to_javadoc_style
        else:
            self._sub_func = CommandStyle.sub_to_default_style

    @override
    def calc_conversion(self, comment: Comment[Any]) -> ConvResult:
        """
        Replaces `\\command` to `@command` or vice versa in Doxygen style comments.

        Parameters
        ----------
        comment : Comment[Any]
            The comment.

        Returns
        -------
        ConvResult
            A ConvPresent object if the style of `comment` is a
            Doxygen style comment and at least one `Xcommand`
            was replaced.
            A ConvEmpty object if no `Xcommand` was replaced.
            A ConvUnsupported object if `comment` is not a
            Doxygen style comment.
        """
        match CommentStyler.parse_comment(comment.comment_text):
            case CommentStyler(_, style) if style.is_doxygen_style():
                new_comment_text = self._sub_func(comment.comment_text)
                if comment.comment_text == new_comment_text:
                    return ConvEmpty()
                else:
                    return ConvPresent(new_comment_text)
            case _:
                return ConvUnsupported()
