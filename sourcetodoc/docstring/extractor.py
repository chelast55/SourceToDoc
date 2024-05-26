from dataclasses import dataclass
from textwrap import dedent
from typing import Iterator, Protocol


@dataclass(frozen=True)
class Range:
    """
    Represents the start and end of a string.

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
class BlockComment[T]:
    """
    Represents a block comment above a symbol.

    All indentations on a block comment must be equal.

    Example:
    ```
    ␣␣␣␣/*
    ␣␣␣␣ * abc
    ␣␣␣␣ */
    ␣␣␣␣int f(void);
    ```
    where:
    - `"␣␣␣␣"`                      is the indentation,
    - `"/*\\n␣␣␣␣ * abc\\n␣␣␣␣ */"` is the comment_text, and
    - `"int f(void)"`               is the symbol_text.
    """
    comment_text: str # e.g. "/* ... /*" (without the initial indentation)
    comment_range: Range #    ^       ^ Start and end of the comment in a string
    symbol_text: str # e.g. "void f(void)"
    symbol_type: T # e.g. "function"
    indentation: str

    def comment_unindented(self) -> str:
        return dedent(self.indentation + self.comment_text)
    
    def comment_with_symbol_unindented(self) -> str:
        return self.comment_unindented() + "\n" + self.symbol_text


@dataclass(frozen=True)
class CommentAfterMember[T]:
    """
    Represents a comment after a member variable.

    Example:
    ```
    int x;␣␣// a
    ␣␣␣␣␣␣␣␣// b
    ```
    within a struct, where:

    - `"// a\\n␣␣␣␣␣␣␣␣// b"` is the comment_text,
    - `"int x;"`              is the symbol_text, and
    - `"␣␣"`                  is the symbol_comment_spacing.
    """
    comment_text: str # e.g. "// Hello World"
    comment_range: Range # Start and end of the comment in a string
    symbol_text: str # e.g. "int x;"
    symbol_type: T # e.g. "variable member"
    symbol_comment_spacing: str # The string between the symbol and comment


type Comment[T] = BlockComment[T] | CommentAfterMember[T]


class Extractor[T](Protocol):
    def extract_comments(self, code: str) -> Iterator[Comment[T]]:
        """
        Extracts comments from a string.

        Parameters
        ----------
        code : str

        Yields
        ------
        Iterator[Comment[T]]
            The extracted comments with pairwise disjoint comment_range in ascending order.
        """
        ...
