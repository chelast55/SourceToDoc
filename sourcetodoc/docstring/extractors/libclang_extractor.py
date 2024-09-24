from typing import Callable

from clang.cindex import Cursor, TranslationUnit

from ..extractor import Comment, Extractor
from ..range import Range
from ...libclang_util import (clang_get_comment_range, walk_preorder_only_main_file)


class LibclangExtractor[T](Extractor[T]):
    """Extracts comments with libclang."""

    def __init__(
            self,
            translation_unit_from_code: Callable[[str],TranslationUnit],
            get_type: Callable[[Cursor], T]
        ) -> None:
        """
        Creates a new object.

        Parameters
        ----------
        translation_unit_from_code : Callable[[str],TranslationUnit]
            Function that creates a translation unit from source code.
        get_type : Callable[[Cursor], T]
            Function that maps `Cursor` to `Comment.symbol_type`.
        """

        self._translation_unit_from_code = translation_unit_from_code
        self._get_type = get_type

    def extract_comments(self, code: str) -> list[Comment[T]]:
        """
        Extracts comments in `code` that are associated with a libclang cursor.

        - `self.translation_unit_from_code` maps `code` to a `TranslationUnit` object.
        - `self.get_type` maps `Cursor` to `Comment.symbol_type`.

        Parameters
        ----------
        code : str
            The source code.

        Returns
        -------
        list[Comment[T]]
            The extracted comments with pairwise disjoint
            `comment_range` in ascending order.
        """
        tu: TranslationUnit = self._translation_unit_from_code(code)

        comments: list[Comment[T]] = []
        comment_ranges: set[Range] = set()
        for node in walk_preorder_only_main_file(tu.cursor):
            comment_text: str | None = node.raw_comment
            if comment_text is None:
                continue
            symbol_start: int = node.extent.start.offset
            symbol_end: int = node.extent.end.offset
            symbol_text: str = code[symbol_start:symbol_end]
            symbol_range = Range(symbol_start, symbol_end)
            symbol_type = self._get_type(node)
            symbol_indentation = self.__class__._get_symbol_indentation(code, symbol_start)
            comment_range = self.__class__._get_comment_range(node)

            if comment_range not in comment_ranges: # Prevent duplicate comments
                comment = Comment(
                    comment_text,
                    comment_range,
                    symbol_text,
                    symbol_range,
                    symbol_type,
                    symbol_indentation
                )
                comments.append(comment)
                comment_ranges.add(comment_range)
        comments.sort(key=lambda x: x.comment_range.start)
        return comments
    
    @classmethod
    def _get_comment_range(cls, cursor: Cursor) -> Range:
        source_range = clang_get_comment_range(cursor)
        return Range(source_range.start.offset, source_range.end.offset) # type: ignore

    @classmethod
    def _get_symbol_indentation(cls, code: str, symbol_start: int) -> str:
        start = symbol_start - 1

        line_start: int = start
        for i in range(start, -1, -1):
            c = code[i]
            if c == "\n":
                line_start = i + 1
                break
            elif not c.isspace():
                return ""

        return code[line_start:symbol_start]
