import pytest
from sourcetodoc.docstring.command_style import CommandStyle

simple_default = r"\param"

simple_javadoc = "@param"

mixed = r"""\
\brief description

Long description

@param a
@param b

\return result
"""

all_default =r"""\
\brief description

Long description

\param a
\param b

\return result
"""

all_javadoc =r"""\
@brief description

Long description

@param a
@param b

@return result
"""

@pytest.mark.parametrize("expected,text", [
    (simple_default, simple_javadoc),
    (all_default, mixed),
])
def test_sub_to_default_style(expected: str, text: str):
    actual = CommandStyle.sub_to_default_style(text)
    assert expected == actual


@pytest.mark.parametrize("expected,text", [
    (simple_javadoc, simple_default),
    (all_javadoc, mixed),
])
def test_sub_to_javadoc_style(expected: str, text: str):
    actual = CommandStyle.sub_to_javadoc_style(text)
    assert expected == actual
