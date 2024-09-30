import pytest

from sourcetodoc.docstring.extractor import Extractor
from sourcetodoc.docstring.extractors.c_type import CType
from sourcetodoc.docstring.extractors.c_libclang_extractor import CLibclangExtractor


@pytest.fixture
def extractor() -> Extractor[CType]:
    return CLibclangExtractor()


_single_line_line_comment = """\
// text
void f(void) {}"""

_single_line_block_comment = """\
/* text */ void f(void) {}"""

_multi_line_line_comment = """\
// text
//
void f(void) {}"""

multi_line_line_comment_actual = """\
// text
//"""

_multi_line_block_comment = """\
/* text
 */
void f(void) {}"""

multi_line_block_comment_actual = """\
/* text
 */"""

_comment_after_member = """\
int a; /**< a */
       /**< b */
"""


@pytest.mark.parametrize(
    "input,expected",
    [
        (_single_line_line_comment, "// text"),
        (_single_line_block_comment, "/* text */"),
        (_multi_line_line_comment, multi_line_line_comment_actual),
        (_multi_line_block_comment, multi_line_block_comment_actual),
        (_comment_after_member, "/**< a */\n       /**< b */"),
    ],
)
def test_extract_one_comment(extractor: Extractor[CType], input: str, expected: str):
    comments = list(extractor.extract_comments(input))
    assert 1 == len(comments)
    assert expected == comments[0].comment_text


comment_with_indent = """\
    /* text
     */
    void f(void) {}"""


def test_extract_comment_with_indent(extractor: Extractor[CType]):
    comments = list(extractor.extract_comments(comment_with_indent))
    assert 1 == len(comments)
    assert "    " == comments[0].symbol_indentation
    assert "/* text\n     */" == comments[0].comment_text


_complex = """\
/* comment */
typedef VOID (callback* test)(A a, B b);
"""

def test_complex(extractor: Extractor[CType]):
    comments = list(extractor.extract_comments(_complex))
    assert len(comments) == 1
    assert "/* comment */" == comments[0].comment_text
