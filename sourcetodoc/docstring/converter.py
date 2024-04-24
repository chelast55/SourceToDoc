from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Protocol

from .extractor import Comment


@dataclass(frozen=True)
class ConversionSuccess:
    """
    Represents a successful conversion.
    """
    comment: Comment
    new_docstring: str
    message: Optional[str]


@dataclass(frozen=True)
class ConversionNothing:
    """
    Represents "no conversion needed" or "comment is already a docstring".
    """
    comment: Comment
    message: Optional[str]


@dataclass(frozen=True)
class ConversionError:
    """
    Represents "no conversion found" or "an error occured during conversion".
    """
    comment: Comment
    message: str


type Conversion = ConversionSuccess | ConversionNothing | ConversionError


class Converter(Protocol):
    def calc_docstring(self, comment: Comment) -> Conversion:
        """
        Calculates the docstring from a comment.

        Parameters
        ----------
        comment : Comment

        Returns
        -------
        str
            The new docstring.
        """
        ...

    def calc_conversions(self, comments: Iterable[Comment]) -> Iterator[Conversion]:
        """
        Calculates docstrings from comments.

        Parameters
        ----------
        comments : Iterable[Comment]

        Yields
        ------
        Iterator[Conversion]
        """
        return (self.calc_docstring(e) for e in comments)
