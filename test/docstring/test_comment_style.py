import pytest

from sourcetodoc.docstring.comment_style import CommentStyler


@pytest.fixture
def single_line_block_comment() -> str:
    return """\
//a
//b"""

def test_create_c_single_line_block_comment(single_line_block_comment: str):
    comment = CommentStyler.parse_comment(single_line_block_comment)
    assert comment is not None
    assert comment.comment_content == "a\nb"
    assert comment.construct_comment() == "// a\n// b"
