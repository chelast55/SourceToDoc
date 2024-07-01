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
