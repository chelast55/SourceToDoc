from typing import Any, override

from ..comment_styler import CommentStyler

from ..comment_style import BlockComment, CommentStyle
from ..conversion import (ConvEmpty, Conversion, ConvPresent, ConvResult,
                          ConvUnsupported)
from ..extractor import Comment
from ..extractors.c_type import CType
from ..extractors.cxx_type import CXXType


class CommentStyleConversion(Conversion[Any]):
    """Changes the comment style of comments."""

    def __init__(self, target_style: CommentStyle, only_after_member: bool = False) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        target_style : CommentStyle
            The comment style to convert into.
        only_after_member : bool
            If set to True, only consider single line comments after
            members, by default False.
        """
        self.target_style = target_style
        self.only_after_member = only_after_member
    
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
        if self.only_after_member:
            if (self.__class__._is_member(comment)
            and self.__class__._is_after_symbol(comment)):
                if self.__class__._is_style_allowed_after_member(self.target_style):
                    if "\n" in comment.comment_text:
                        return ConvUnsupported("Comments with multiple lines after members are not supported")
                    else:
                        return self._calc_conversion_helper(comment)
                else:
                    return ConvEmpty("Specified style is not allowed for after member comments")
            else:
                return ConvEmpty("Comments that are not after members are ignored")
        else:
            if (self.__class__._is_member(comment)
            and self.__class__._is_after_symbol(comment)):
                return ConvEmpty("Comments after members are ignored")
            else:
                return self._calc_conversion_helper(comment)

    def _calc_conversion_helper(self, comment: Comment[Any]) -> ConvResult:
        match CommentStyler.parse_comment(comment.comment_text):
            case CommentStyler(_, style=self.target_style):
                return ConvEmpty("The comment has already that style")
            case CommentStyler(content, _) if content.count("*/") >= 1 and isinstance(self.target_style.value, BlockComment):
                return ConvEmpty("The comment has one or more */")
            case CommentStyler(content, _):
                new_comment_text = CommentStyler(
                    content,
                    self.target_style
                ).construct_comment(comment.symbol_indentation)
                return ConvPresent(new_comment_text)
            case None:
                return ConvUnsupported("The comment cannot be parsed")

    @classmethod
    def _is_member(cls, comment: Comment[Any]):
        return comment.symbol_type in {
            CType.ENUM_CONSTANT,
            CType.VARIABLE,
            CType.FIELD,
            CXXType.ENUM_CONSTANT,
            CXXType.VARIABLE,
            CXXType.FIELD,
        }

    @classmethod
    def _is_after_symbol(cls, comment: Comment[Any]):
        return comment.comment_range.start > comment.symbol_range.end

    @classmethod
    def _is_style_allowed_after_member(cls, style: CommentStyle) -> bool:
        return style in {
            CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE,
            CommentStyle.QT_BLOCK_MEMBER_INLINE,
            CommentStyle.QT_LINE_MEMBER,
            CommentStyle.TRIPLE_SLASH_LINE_MEMBER,
        }
