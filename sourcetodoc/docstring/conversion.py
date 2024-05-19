from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Protocol

from .extractor import Comment


@dataclass(frozen=True)
class ConversionPresent[T]:
    """
    Represents a successful conversion.

    new_comment has the same form as Comment#comment_text.
    """
    comment: Comment[T]
    new_comment: str
    message: Optional[str] = None


@dataclass(frozen=True)
class ConversionEmpty[T]:
    """
    Represents "no conversion needed".
    """
    comment: Comment[T]
    message: Optional[str] = None

@dataclass(frozen=True)
class ConversionUnsupported[T]:
    """
    Represents "comment is not supported by this converter".
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


class Conversion[T](Protocol):
    def calc_conversion(self, comment: Comment[T]) -> ConversionResult[T]:
        """
        Calculates a new comment from a comment.

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
        Calculates new comments from comments.

        Parameters
        ----------
        comments : Iterable[Comment[T]]

        Yields
        ------
        Iterator[ConversionResult[T]]
            ConversionResult objects with comments with pairwise disjoint comment_range in ascending order.
        """
        return (self.calc_conversion(e) for e in comments)
