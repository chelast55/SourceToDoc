from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Protocol

from .extractor import Comment


@dataclass(frozen=True)
class ConversionPresent[T]:
    """
    Represents a successful conversion.
    """
    comment: Comment[T]
    new_comment: str
    message: Optional[str] = None


@dataclass(frozen=True)
class ConversionEmpty[T]:
    """
    Represents "no conversion needed" or "comment is already a docstring".
    """
    comment: Comment[T]
    message: Optional[str] = None

@dataclass(frozen=True)
class ConversionUnsupported[T]:
    """
    Represents "Comment type is not supported by this Converter".
    """
    comment: Comment[T]


@dataclass(frozen=True)
class ConversionError[T]:
    """
    Represents "no conversion found" or "an error occured during conversion".
    """
    comment: Comment[T]
    message: str


type ConversionResult[T] = ConversionPresent[T] | ConversionEmpty[T] | ConversionUnsupported[T] | ConversionError[T]


class Converter[T](Protocol):
    def calc_docstring(self, comment: Comment[T]) -> ConversionResult[T]:
        """
        Calculates a docstring from a comment.

        Parameters
        ----------
        comment : Comment[T]

        Returns
        -------
        ConversionResult[T]
        """
        ...

    def calc_conversions(self, comments: Iterable[Comment[T]]) -> Iterator[ConversionResult[T]]:
        """
        Calculates docstrings from comments.

        Parameters
        ----------
        comments : Iterable[Comment[T]]

        Yields
        ------
        Iterator[ConversionResult[T]]
            ConversionResult objects with comments with pairwise disjoint comment_range in ascending order.
        """
        return (self.calc_docstring(e) for e in comments)
