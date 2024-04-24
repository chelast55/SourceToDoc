from dataclasses import dataclass
from typing import Any, Iterator, Protocol


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
class Comment:
    """
    Represents a comment in a source file.
    """
    text: str # e.g. "/* Hello World /*"
    range: Range # Start and end of the comment in a string
    symbol_text: str # e.g. "void main(void)"
    symbol_type: Any # e.g. "function"


class Extractor(Protocol):
    def extract_comments(self, code: str) -> Iterator[Comment]:
        """
        Extracts comments from a string.

        Parameters
        ----------
        code : str

        Yields
        ------
        Iterator[Comment]
            The extracted comments.
        """
        ...
