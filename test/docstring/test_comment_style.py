import pytest

from sourcetodoc.docstring.comment_style import CommentStyle, CommentStyler


_c_line1 = """\
/* a
 * b
 */"""

_c_line2 = """\
/* 
 * a
 * b
 */"""

_c_line3 = """\
/* a
 * b*/"""

_c_line4 = """\
/* 
 * a
 * b*/"""

expected_content = """\
a
b"""

expected_comment = """\
/*
 * a
 * b
 */"""

@pytest.mark.parametrize("input", [_c_line1, _c_line2, _c_line3, _c_line4])
def test_format_style(input: str):
    comment = CommentStyler.parse_comment(input)
    assert comment is not None
    assert comment.style is CommentStyle.C_BLOCK
    assert comment.content == expected_content
    assert comment.construct_comment() == expected_comment

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

_qt_line = """\
//! a
//! b"""

_qt_line_member = """\
//!< a
//!< b"""

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
            (_qt_block, CommentStyle.QT_BLOCK),
            (_qt_block_inline, CommentStyle.QT_BLOCK_INLINE),
            (_qt_block_member_inline, CommentStyle.QT_BLOCK_MEMBER_INLINE),
            (_triple_slash_line, CommentStyle.TRIPLE_SLASH_LINE),
            (_triple_slash_line_member, CommentStyle.TRIPLE_SLASH_LINE_MEMBER),
            (_qt_line, CommentStyle.QT_LINE),
            (_qt_line_member, CommentStyle.QT_LINE_MEMBER),
            (_triple_slash_line_and_c_line, CommentStyle.C_LINE),
            (_qt_block_inline_and_c_block_inline, CommentStyle.C_BLOCK_INLINE)
        ]
    )
def test_parse_line_comments(input: str, style: CommentStyle):
    comment = CommentStyler.parse_comment(input)
    assert comment is not None
    assert comment.style is style
