import pytest

from sourcetodoc.docstring.comment_style import CommentStyle, CommentStyler


input_a = """\
/* a
 * b
 */"""

input_b = """\
/* 
 * a
 * b
 */"""

input_c = """\
/* a
 * b*/"""

input_d = """\
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

@pytest.mark.parametrize("input", [input_a, input_b, input_c, input_d])
def test_format_style(input: str):
    comment = CommentStyler.parse_comment(input)
    assert comment is not None
    assert comment.style is CommentStyle.C_BLOCK
    assert comment.content == expected_content
    assert comment.construct_comment() == expected_comment

line_a = """\
// a
// b"""

line_b = """\
/// a
/// b"""

line_c = """\
//! a
//! b"""

line_d = """\
///< a
///< b"""

line_e = """\
//!< a
//!< b"""

line_f = """\
/// a
// b"""

@pytest.mark.parametrize(
        "input,style",
        [
            (line_a, CommentStyle.C_LINE),
            (line_b, CommentStyle.TRIPLE_SLASH_LINE),
            (line_c, CommentStyle.QT_LINE),
            (line_d, CommentStyle.TRIPLE_SLASH_LINE_MEMBER),
            (line_e, CommentStyle.QT_LINE_MEMBER),
            (line_f, CommentStyle.C_LINE)
        ]
    )
def test_parse_line_comments(input: str, style: CommentStyle):
    comment = CommentStyler.parse_comment(input)
    assert comment is not None
    assert comment.style is style
