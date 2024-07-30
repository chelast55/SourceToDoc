import pytest

from sourcetodoc.docstring.extractor import Extractor
from sourcetodoc.docstring.extractors.c_type import CType
from sourcetodoc.docstring.extractors.c_libclang_extractor import CLibclangExtractor


@pytest.fixture
def extractor() -> Extractor[CType]:
    return CLibclangExtractor()


single_line_line_comment = """\
// text
void f(void) {}"""

single_line_block_comment = """\
/* text */ void f(void) {}"""

multi_line_line_comment = """\
// text
//
void f(void) {}"""

multi_line_line_comment_actual = """\
// text
//"""

multi_line_block_comment = """\
/* text
 */
void f(void) {}"""

multi_line_block_comment_actual = """\
/* text
 */"""

comment_after_member = """\
int a; /**< a */
       /**< b */
"""


@pytest.mark.parametrize(
    "input,expected",
    [
        (single_line_line_comment, "// text"),
        (single_line_block_comment, "/* text */"),
        (multi_line_line_comment, multi_line_line_comment_actual),
        (multi_line_block_comment, multi_line_block_comment_actual),
        (comment_after_member, "/**< a */\n       /**< b */"),
    ],
)
def test_extract_one_comment(extractor: Extractor[CType], input: str, expected: str):
    comments = list(extractor.extract_comments(input))
    assert len(comments) == 1
    assert comments[0].comment_text == expected


comment_with_indent = """\
    /* text
     */
    void f(void) {}"""


def test_extract_comment_with_indent(extractor: Extractor[CType]):
    comments = list(extractor.extract_comments(comment_with_indent))
    assert len(comments) == 1
    assert comments[0].symbol_indentation == "    "
