from typing import Iterable, Iterator, Protocol

from sourcetodoc.docstring.common import Comment


class Filter(Protocol):
    def is_valid(self, comment: Comment) -> bool:
        """
        Returns True if the comment should be converted.

        Parameters
        ----------
        comment : Comment
            The comment.

        Returns
        -------
        bool
        """
        ...

    def filter_comments(self, comments: Iterable[Comment]) -> Iterator[Comment]:
        """
        Returns comments that satisfies the is_valid function.

        Parameters
        ----------
        comments : Iterable[Comment]
            The comments.

        Yields
        ------
        Iterator[Comment]
        """
        return (c for c in comments if self.is_valid(c))
