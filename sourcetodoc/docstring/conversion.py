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
    """Represents "no conversion needed"."""
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
    def calc_conversion(self, comment: Comment[T]) -> ConvResult:
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
