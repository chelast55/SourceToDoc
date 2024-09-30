import pytest

from sourcetodoc.docstring.comment_styler import CommentStyler
from sourcetodoc.docstring.comment_style import CommentStyle


_c_block1 = """\
/* a
 * b
 */"""

_c_block2 = """\
/* 
 * a
 * b
 */"""

_c_block3 = """\
/* a
 * b*/"""

_c_block4 = """\
/* 
 * a
 * b*/"""

_expected_content = """\
a
b"""

_expected_comment = """\
/*
 * a
 * b
 */"""

@pytest.mark.parametrize("input", [_c_block1, _c_block2, _c_block3, _c_block4])
def test_format_style(input: str):
    comment = CommentStyler.parse_comment(input)
    assert comment is not None
    assert comment.style is CommentStyle.C_BLOCK
    assert comment.content == _expected_content
    assert comment.construct_comment() == _expected_comment


_c_line = """\
// a
// b"""

_c_block = """\
/* a
 * b
 */"""

_c_block_inline = """\
/* a */
/* b */"""

_javadoc_block = """\
/** a
 * b
 */"""

_javadoc_block_inline = """\
/** a */
/** b */"""

_javadoc_block_member_inline = """\
/**< a */
/**< b */"""

_qt_line = """\
//! a
//! b"""

_qt_line_member = """\
//!< a
//!< b"""

_qt_block = """\
/*! a
 * b
 */"""

_qt_block_inline = """\
/*! a */
/*! b */"""

_qt_block_member_inline = """\
/*!< a */
/*!< b */"""

_triple_slash_line = """\
/// a
/// b"""

_triple_slash_line_member = """\
///< a
///< b"""

_triple_slash_line_and_c_line = """\
/// a
// b"""

_qt_block_inline_and_c_block_inline = """\
/*! a */
/* b */"""


@pytest.mark.parametrize(
        "input,style",
        [
            (_c_line, CommentStyle.C_LINE),
            (_c_block, CommentStyle.C_BLOCK),
            (_c_block_inline, CommentStyle.C_BLOCK_INLINE),
            (_javadoc_block, CommentStyle.JAVADOC_BLOCK),
            (_javadoc_block_inline, CommentStyle.JAVADOC_BLOCK_INLINE),
            (_javadoc_block_member_inline, CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE),
            (_qt_line, CommentStyle.QT_LINE),
            (_qt_line_member, CommentStyle.QT_LINE_MEMBER),
            (_qt_block, CommentStyle.QT_BLOCK),
            (_qt_block_inline, CommentStyle.QT_BLOCK_INLINE),
            (_qt_block_member_inline, CommentStyle.QT_BLOCK_MEMBER_INLINE),
            (_triple_slash_line, CommentStyle.TRIPLE_SLASH_LINE),
            (_triple_slash_line_member, CommentStyle.TRIPLE_SLASH_LINE_MEMBER),
            (_triple_slash_line_and_c_line, CommentStyle.C_LINE),
            (_qt_block_inline_and_c_block_inline, CommentStyle.C_BLOCK_INLINE)
        ]
    )
def test_parse_comments(input: str, style: CommentStyle):
    comment = CommentStyler.parse_comment(input)
    assert comment is not None
    assert comment.style is style
