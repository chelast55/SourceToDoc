from typing import Iterable, Iterator, Protocol

from sourcetodoc.docstring.common import Conversion
from sourcetodoc.docstring.common import Comment


class Converter(Protocol):
    def calc_docstring(self, comment: Comment) -> str:
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
        Calculates comments to Conversion objects that contain the new docstring from the comment.

        Parameters
        ----------
        comments : Iterable[Comment]

        Yields
        ------
        Iterator[Conversion]
        """
        return (Conversion(e, self.calc_docstring(e)) for e in comments)
