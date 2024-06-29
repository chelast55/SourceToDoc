from typing import Any, override

from ..comment_style import CommentStyler

from ..command_style import CommandStyle
from ..conversion import ConvEmpty, ConvUnsupported, Conversion, ConvPresent, ConvResult
from ..extractor import Comment


class CommandStyleConversion(Conversion[Any]):
    """
    Replaces \\command to @command or vice versa in Doxygen style comments.
    """
    def __init__(self, javadoc_style: bool) -> None:
        if javadoc_style:
            self._sub_func = CommandStyle.sub_to_javadoc_style
        else:
            self._sub_func = CommandStyle.sub_to_default_style

    @override
    def calc_conversion(self, comment: Comment[Any]) -> ConvResult:
        match CommentStyler.parse_comment(comment.comment_text):
            case CommentStyler(_, style) if style.is_doxygen_style():
                new_comment_text = self._sub_func(comment.comment_text)
                if comment.comment_text == new_comment_text:
                    return ConvEmpty()
                else:
                    return ConvPresent(new_comment_text)
            case _:
                return ConvUnsupported()
