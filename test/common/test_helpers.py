from typing import Iterable
import pytest
from sourcetodoc.common.helpers import index_from_coordinates


_a = """\
abcd
test
"""

@pytest.mark.parametrize("indices,text,line_column_pairs", [
    ([0], _a, [(1, 1)]),
    ([1], _a, [(1, 2)]),
    ([2], _a, [(1, 3)]),
    ([3], _a, [(1, 4)]),
    ([4], _a, [(1, 5)]),
    ([5], _a, [(2, 1)]),
    ([6], _a, [(2, 2)]),
    ([7], _a, [(2, 3)]),
    ([8], _a, [(2, 4)]),
])
def test_index_from_coordinates(indices: Iterable[int], text: str, line_column_pairs: Iterable[tuple[int,int]]) -> None:
    for index, actual in zip(indices, index_from_coordinates(text, line_column_pairs)):
        assert index == actual
