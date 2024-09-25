from typing import override

from ..comment_style import CommentStyle, CommentStyler
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
            case CommentStyler(content, _):
                new_comment_text = CommentStyler(content, CommentStyle.JAVADOC_BLOCK).construct_comment(comment.symbol_indentation)
                return ConvPresent(new_comment_text)
            case None:
                return ConvUnsupported("The comment cannot be parsed")

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
