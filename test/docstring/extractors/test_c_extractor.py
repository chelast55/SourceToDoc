import pytest

from sourcetodoc.docstring.extractors.c_extractor import CExtractor
from sourcetodoc.docstring.extractors.c_pylibclang_extractor import CPylibclangExtractor


@pytest.fixture
def extractor() -> CExtractor:
    return CPylibclangExtractor()


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


@pytest.mark.parametrize(
    "input,expected",
    [
        (single_line_line_comment, "// text"),
        (single_line_block_comment, "/* text */"),
        (multi_line_line_comment, multi_line_line_comment_actual),
        (multi_line_block_comment, multi_line_block_comment_actual),
    ],
)
def test_extract_one_comment(extractor: CExtractor, input: str, expected: str):
    comments = list(extractor.extract_comments(input))
    assert len(comments) == 1
    assert comments[0].comment_text == expected


comment_with_indent = """\
    /* text
     */
    void f(void) {}"""


def test_extract_comment_with_indent(extractor: CExtractor):
    comments = list(extractor.extract_comments(comment_with_indent))
    assert len(comments) == 1
    assert comments[0].symbol_indentation == "    "