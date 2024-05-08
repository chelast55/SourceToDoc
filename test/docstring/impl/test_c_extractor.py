import pytest

from sourcetodoc.docstring.impl.c_extractor import CExtractor


@pytest.fixture
def extractor() -> CExtractor:
    return CExtractor()


@pytest.fixture
def simple_code() -> str:
    return """\
/* Hello World
 */
void main(void) {}"""


def test_simple_function_pattern(extractor: CExtractor, simple_code: str):
    comments = list(extractor.extract_comments(simple_code))
    assert len(comments) == 1

    expected = """\
/* Hello World
 */"""
    assert comments[0].comment_text == expected
