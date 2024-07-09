from typing import Iterable
import pytest
from sourcetodoc.docstring.range import Range
from sourcetodoc.docstring.replacer import Replacer, TextReplacement


text = "0123456789"


@pytest.mark.parametrize("expected,replacements", [
    ("X123456789", (TextReplacement(Range(0, 1), "X"),)),
    ("0123X56789", (TextReplacement(Range(4, 5), "X"),)),
    ("0ABC9", (TextReplacement(Range(1, 9), "ABC"),)),
    ("X", (TextReplacement(Range(0, 10), "X"),)),
    ("0X23X789", (TextReplacement(Range(1, 2), "X"), TextReplacement(Range(4, 7), "X"))),
])
def test_replace_text(expected: str, replacements: Iterable[TextReplacement]) -> None:
    actual = Replacer.replace_text(text, (replacements))
    assert expected == actual


@pytest.mark.parametrize("replacements", [
    (TextReplacement(Range(0, 1), "X"),TextReplacement(Range(0, 1), "X")),
    (TextReplacement(Range(1, 2), "X"),TextReplacement(Range(1, 3), "X")),
    (TextReplacement(Range(1, 3), "X"),TextReplacement(Range(2, 3), "X")),
    (TextReplacement(Range(0, 3), "X"),TextReplacement(Range(1, 2), "X")),
])
def test_replace_text_overlap(replacements: Iterable[TextReplacement]) -> None:
    with pytest.raises(ValueError):
        Replacer.replace_text(text, (replacements))


@pytest.mark.parametrize("replacements", [
    (TextReplacement(Range(1, 2), "X"),TextReplacement(Range(0, 1), "X")),
    (TextReplacement(Range(4, 7), "X"),TextReplacement(Range(1, 3), "X")),
])
def test_replace_text_not_ascending_order(replacements: Iterable[TextReplacement]) -> None:
    with pytest.raises(ValueError):
        Replacer.replace_text(text, (replacements))
