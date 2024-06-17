from dataclasses import dataclass
from typing import Protocol

from sourcetodoc.docstring.range import Range


@dataclass(frozen=True)
class Comment[T]:
    """
    Contains a comment associated with a symbol.

    Example:
    ```
        /*
         * abc
         */
    ␣␣␣␣int f(void);
    ```
    where:
    - `"␣␣␣␣"`                      is the symbol_indentation,
    - `"/*\\n␣␣␣␣ * abc\\n␣␣␣␣ */"` is the comment_text, and
    - `"int f(void)"`               is the symbol_text.
    """

    comment_text: str  # e.g. "/* ... /*" (without the initial indentation)
    comment_range: Range  #    ^       ^ Start and end of the comment in a string
    symbol_text: str
    symbol_range: Range  # Start and end of the symbol in a string
    symbol_type: T  # e.g. CType.FUNCTION
    symbol_indentation: str


class Extractor[T](Protocol):
    def extract_comments(self, code: str) -> list[Comment[T]]:
        """
        Extracts comments from a string.

        Parameters
        ----------
        code : str

        Returns
        -------
        list[Comment[T]]
            The extracted comments with pairwise disjoint comment_range in ascending order.
        """
        ...
