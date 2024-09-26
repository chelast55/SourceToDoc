from typing import Callable

from clang.cindex import Cursor, TranslationUnit

from ...common.helpers import index_from_coordinates
from ...libclang_util import (clang_get_comment_range,
                              walk_preorder_only_main_file)
from ..extractor import Comment, Extractor
from ..range import Range


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
        
        Raises
        ------
        RuntimeError
            If the extracted indices do not match the actual indices of a comment.
        """
        tu: TranslationUnit = self._translation_unit_from_code(code)

        comments: list[Comment[T]] = []
        comment_ranges: set[Range] = set()
        for node in walk_preorder_only_main_file(tu.cursor):
            comment_text: str | None = node.raw_comment
            if comment_text is None:
                continue
            symbol_range = self.__class__._get_symbol_range_by_line_and_column(code, node)
            symbol_text: str = code[symbol_range.start:symbol_range.end]

            symbol_type = self._get_type(node)
            symbol_indentation = self.__class__._get_symbol_indentation(code, symbol_range.start)
            comment_range = self.__class__._get_comment_range_by_line_and_column(code, node)

            # To be safe
            comment_text_by_range = code[comment_range.start:comment_range.end]
            if comment_text_by_range != comment_text:
                raise RuntimeError(f"The extracted indices do not match the actual indices of a comment:"
                      f"\n\"{comment_text}\" (getting the comment with libclang directly)"
                      f"\n!=\n\"{comment_text_by_range}\" (getting the comment with indices), skip this comment!")

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
    def _get_comment_range_by_offset(cls, cursor: Cursor) -> Range:
        # Warning: offset does/did not always correspond to index of string in Python.
        # Because of this `_get_comment_range_by_line_and_column` is used instead.
        source_range = clang_get_comment_range(cursor)
        return Range(source_range.start.offset, source_range.end.offset) # type: ignore

    @classmethod
    def _get_comment_range_by_line_and_column(cls, code: str, cursor: Cursor) -> Range:
        source_range = clang_get_comment_range(cursor)
        start, end = index_from_coordinates(code, [
            (source_range.start.line, source_range.start.column),
            ((source_range.end.line, source_range.end.column))
        ])
        return Range(start, end) # type: ignore
    
    @classmethod
    def _get_symbol_range_by_line_and_column(cls, code: str, cursor: Cursor) -> Range:
        source_range = cursor.extent
        start, end = index_from_coordinates(code, [
            (source_range.start.line, source_range.start.column),
            ((source_range.end.line, source_range.end.column))
        ])
        return Range(start, end) # type: ignore

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
