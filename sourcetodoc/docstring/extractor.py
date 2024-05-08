from dataclasses import dataclass
from typing import Iterator, Protocol


@dataclass(frozen=True)
class Range:
    """
    Represent the start and end of a string.

    Raises
    ------
    ValueError
        If start or end are negative or if start > end.
    """
    start: int
    end: int

    def __post_init__(self):
        if self.start < 0 or self.end < 0 or self.start > self.end:
            raise ValueError()


@dataclass(frozen=True)
class Comment[T]:
    """
    Represents a comment with its context in a source file.
    """
    comment_text: str # e.g. "/* Hello World /*"
    comment_range: Range # Start and end of the comment in a string
    symbol_text: str # e.g. "void main(void)"
    symbol_type: T # e.g. "function"


class Extractor[T](Protocol):
    def extract_comments(self, code: str) -> Iterator[Comment[T]]:
        """
        Extracts comments from a string.

        Parameters
        ----------
        code : str

        Yields
        ------
        Iterator[Comment[T]]
            The extracted comments with pairwise disjoint comment_range in ascending order.
        """
        ...
