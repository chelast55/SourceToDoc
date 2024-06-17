from typing import Iterable
import pytest

from sourcetodoc.docstring.range import Range


@pytest.mark.parametrize("ranges", [
    (
        Range(0, 1),
        Range(1, 2),
        Range(2, 3),
    ),
    (
        Range(3, 6),
        Range(7, 11),
        Range(8, 15),
    )
])
def test_is_ascending_order_by_start(ranges: Iterable[Range]) -> None:
    assert True == Range.is_ascending_order_by_start(ranges)


@pytest.mark.parametrize("ranges", [
    (
        Range(0, 1),
        Range(2, 3),
        Range(1, 2),
    ),
    (
        Range(7, 11),
        Range(3, 6),
        Range(8, 15),
    )
])
def test_not_is_ascending_order_by_start(ranges: Iterable[Range]) -> None:
    assert False == Range.is_ascending_order_by_start(ranges)


@pytest.mark.parametrize("ranges", [
    (
        Range(1, 2),
        Range(1, 2),
    ),
    (
        Range(7, 11),
        Range(3, 6),
    )
])
def test_has_overlap(ranges: Iterable[Range]) -> None:
    assert True == Range.has_overlap(ranges)


@pytest.mark.parametrize("ranges", [
    (
        Range(1, 2),
        Range(2, 3),
    ),
    (
        Range(2, 5),
        Range(7, 11),
    )
])
def test_not_has_overlap(ranges: Iterable[Range]) -> None:
    assert False == Range.has_overlap(ranges)
