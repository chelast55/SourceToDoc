from typing import Iterator, Protocol

from sourcetodoc.docstring.common import Comment


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
