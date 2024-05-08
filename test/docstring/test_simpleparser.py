from sourcetodoc.docstring.converter import ConversionPresent
from sourcetodoc.docstring.extractor import Comment, Range
from sourcetodoc.docstring.impl.c_extractor import CType
from sourcetodoc.docstring.simpleparser import replace_old_comments


def test_replace_old_comments():
    code = """\
/* Hello World
 */
void main(void) {}"""

    comment = """\
/* Hello World
 */"""
    
    new_comment = """\
/* Bye World
 */"""

    conversions = [ConversionPresent(
        Comment(comment, Range(0, 18), "void main(void)", CType.FUNCTION),
        new_comment)]
    
    actual = replace_old_comments(code, conversions)

    expected = """\
/* Bye World
 */
void main(void) {}"""

    assert actual == expected