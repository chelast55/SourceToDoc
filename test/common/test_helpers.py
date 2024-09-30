import pytest
from sourcetodoc.common.helpers import IndexFinder

@pytest.mark.parametrize("index,line_column_pair", [
    (0, (1, 1)),
    (1, (1, 2)),
    (2, (1, 3)),
    (None, (1, 4)),
    (None, (2, 1)),
])
def test_find_index_a(index: int, line_column_pair: tuple[int,int]) -> None:
    tmp = IndexFinder("abc")
    assert index == tmp.find_index(line_column_pair[0], line_column_pair[1])


@pytest.mark.parametrize("index,line_column_pair", [
    (0, (1, 1)),
    (1, (1, 2)),
    (2, (1, 3)),
    (3, (1, 4)),
    (None, (1, 5)),
    (None, (2, 1)),
])
def test_find_index_b(index: int, line_column_pair: tuple[int,int]) -> None:
    tmp = IndexFinder("abc\n")
    assert index == tmp.find_index(line_column_pair[0], line_column_pair[1])


_c = """\
abcd
test"""

@pytest.mark.parametrize("index,line_column_pair", [
    (0, (1, 1)),
    (1, (1, 2)),
    (2, (1, 3)),
    (3, (1, 4)),
    (4, (1, 5)),
    (5, (2, 1)),
    (6, (2, 2)),
    (7, (2, 3)),
    (8, (2, 4)),
    (None, (2, 5)),
    (None, (3, 1)),
    (None, (1, 6)),
])
def test_find_index_c(index: int, line_column_pair: tuple[int,int]) -> None:
    tmp = IndexFinder(_c)
    assert index == tmp.find_index(line_column_pair[0], line_column_pair[1])


_d = """\
abcd
test
"""

@pytest.mark.parametrize("index,line_column_pair", [
    (0, (1, 1)),
    (1, (1, 2)),
    (2, (1, 3)),
    (3, (1, 4)),
    (4, (1, 5)),
    (5, (2, 1)),
    (6, (2, 2)),
    (7, (2, 3)),
    (8, (2, 4)),
    (9, (2, 5)),
    (None, (3, 1)),
    (None, (1, 6)),
])
def test_find_index_d(index: int, line_column_pair: tuple[int,int]) -> None:
    tmp = IndexFinder(_d)
    assert index == tmp.find_index(line_column_pair[0], line_column_pair[1])


@pytest.mark.parametrize("index,line_column_pair", {
    (None, (1, 1)),
    (None, (1, 2)),
    (None, (1, 3)),
    (None, (2, 1)),
})
def test_find_index_with_empty_string(index: int, line_column_pair: tuple[int,int]) -> None:
    tmp = IndexFinder("")
    assert index == tmp.find_index(line_column_pair[0], line_column_pair[1])


@pytest.mark.parametrize("index,line_column_pair", {
    (0, (1, 1)),
    (1, (2, 1)),
    (None, (1, 2)),
    (None, (2, 2)),
})
def test_find_index_with_newlines(index: int, line_column_pair: tuple[int,int]) -> None:
    tmp = IndexFinder("\n\n")
    assert index == tmp.find_index(line_column_pair[0], line_column_pair[1])


_code = """\
asdf foie aowehg giuwpa
 aoiwe
wae

fhg


awefijof
"""



def test_find_index_auto() -> None:
    tmp = IndexFinder(_code)
    line = 1
    column = 1
    for i, c in enumerate(_code):
        actual_index = tmp.find_index(line, column)
        assert i == actual_index
        if c == "\n":
            line += 1
            column = 1
        else:
            column += 1
