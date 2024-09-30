from typing import override

from ..comment_style import BlockComment, CommentStyle, LineComment
from ..comment_styler import CommentStyler
from ..conversion import (ConvEmpty, Conversion, ConvPresent, ConvResult,
                          ConvUnsupported)
from ..extractor import Comment
from ..extractors.c_type import CType
from ..extractors.cxx_type import CXXType


class DefaultCommentStyleConversion(Conversion[CType | CXXType]):

    @override
    def calc_conversion(self, comment: Comment[CType | CXXType]) -> ConvResult:
        match CommentStyler.parse_comment(comment.comment_text):
            case CommentStyler(_, style) if style.is_doxygen_style():
                return ConvEmpty("The comment has already a Doxygen style")
            case CommentStyler(content, style):
                target_style = self.choose_new_style(style)
                new_comment_text = CommentStyler(content, target_style).construct_comment(comment.symbol_indentation)
                return ConvPresent(new_comment_text)
            case None:
                return ConvUnsupported("The comment cannot be parsed")

    def choose_new_style(self, style: CommentStyle) -> CommentStyle:
        target_style: CommentStyle
        match style.value:
            case LineComment():
                target_style = CommentStyle.TRIPLE_SLASH_LINE
            case BlockComment() as b if b.is_inline:
                target_style = CommentStyle.JAVADOC_BLOCK_INLINE
            case BlockComment():
                target_style = CommentStyle.JAVADOC_BLOCK
        return target_style

    @classmethod
    def _is_member(cls, comment: Comment[CType | CXXType]):
        return comment.symbol_type in {
            CType.ENUM_CONSTANT,
            CType.VARIABLE,
            CType.FIELD,
            CXXType.ENUM_CONSTANT,
            CXXType.VARIABLE,
            CXXType.FIELD,
        }
