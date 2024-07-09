from dataclasses import dataclass

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
