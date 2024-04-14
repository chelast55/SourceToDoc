
from sourcetodoc.docstring.common import Comment
from sourcetodoc.docstring.impl.c_extractor import CExtractor


def test_simple_function_pattern():
    extractor: CExtractor = CExtractor()
    code: str = """\
/* Hello World
 */
void main(void) {}"""
    comments: list[Comment] = list(extractor.extract_comments(code))
    assert len(comments) == 1
    expected: str = """\
/* Hello World
 */"""
    assert comments[0].text == expected
