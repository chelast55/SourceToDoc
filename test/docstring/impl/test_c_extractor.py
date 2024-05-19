import pytest

from sourcetodoc.docstring.impl.c_extractor import CExtractor


@pytest.fixture
def extractor() -> CExtractor:
    return CExtractor()


@pytest.fixture
def single_line_single_comment() -> str:
    return """\
// Hello World
void f(void) {}"""


def test_single_line_comments(extractor: CExtractor, single_line_single_comment: str):
    comments = list(extractor.extract_comments(single_line_single_comment))
    assert len(comments) == 1
    assert comments[0].comment_text == "// Hello World"


@pytest.fixture
def single_line_multi_comment() -> str:
    return """\
/* Hello World */
void f(void) {}"""


def test_single_line_multi_comment(extractor: CExtractor, single_line_multi_comment: str):
    comments = list(extractor.extract_comments(single_line_multi_comment))
    assert len(comments) == 1
    assert comments[0].comment_text == "/* Hello World */"


@pytest.fixture
def multi_line_single_comment() -> str:
    return """\
// Hello World
//
void f(void) {}"""


def test_multi_line_single_comment(extractor: CExtractor, multi_line_single_comment: str):
    comments = list(extractor.extract_comments(multi_line_single_comment))
    assert len(comments) == 1
    assert comments[0].comment_text == """\
// Hello World
//"""



@pytest.fixture
def multi_line_multi_comment() -> str:
    return """\
/* Hello World
 */
void f(void) {}"""


def test_simple_function_pattern(extractor: CExtractor, multi_line_multi_comment: str):
    comments = list(extractor.extract_comments(multi_line_multi_comment))
    assert len(comments) == 1
    assert comments[0].comment_text == """\
/* Hello World
 */"""
