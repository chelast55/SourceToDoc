from dataclasses import dataclass
from typing import Optional, Protocol

from .extractor import Comment


@dataclass(frozen=True)
class ConvPresent:
    """
    Represents a successful conversion.

    new_comment has the same form as Comment#comment_text.
    """
    new_comment: str
    message: Optional[str] = None


@dataclass(frozen=True)
class ConvEmpty:
    """Represents "conversion was skipped"."""
    message: Optional[str] = None

@dataclass(frozen=True)
class ConvUnsupported:
    """Represents "comment is not supported"."""
    message: Optional[str] = None


@dataclass(frozen=True)
class ConvError:
    """Represents "no conversion found" or "an error occured during conversion"."""
    message: Optional[str] = None


type ConvResult = ConvPresent | ConvEmpty | ConvUnsupported | ConvError


class Conversion[T](Protocol):
    """Calculate new comment texts from old comments."""

    def calc_conversion(self, comment: Comment[T]) -> ConvResult:
        """
        Calculates a new comment text from `comment`.

        Parameters
        ----------
        comment : Comment[T]
            The comment.

        Returns
        -------
        ConversionResult[T]
            A ConvPresent object with the new comment text if a new comment is found.
            A ConvEmpty object if the old comment doesn't have to change.
            A ConvUnsupported object if the input is not supported.
            A ConvError object if an error occured.
        """
        ...
