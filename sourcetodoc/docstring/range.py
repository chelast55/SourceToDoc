from dataclasses import dataclass
from typing import Callable, Iterable, Self


@dataclass(frozen=True)
class Range:
    """
    Represents the start and end of a string.

    Raises
    ------
    ValueError
        If start or end are negative or if start > end.
    """

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < 0 or self.start > self.end:
            raise ValueError()

    @classmethod
    def is_ascending_order_by_start(cls, ranges: Iterable[Self]) -> bool:
        last_start = -1
        for range in ranges:
            if range.start <= last_start:
                return False
            last_start = range.start
        return True

    @classmethod
    def has_overlap(cls, ranges: Iterable[Self]) -> bool:
        def gt(start: int, last_end: int):
            return start < last_end

        def first_false(start: int, last_end: int):
            nonlocal cmp
            cmp = gt # Replace first_false with gt function
            return False

        cmp: Callable[[int, int], bool] = first_false
        last_end = 0 # Dummy value, first comparison always returns False
        for range in ranges:
            if cmp(range.start, last_end):
                return True
            last_end = range.end
        return False
