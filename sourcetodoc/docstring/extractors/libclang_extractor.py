from typing import Callable

from clang.cindex import Cursor, TranslationUnit

from ...common.helpers import IndexFinder
from ...libclang_util import (clang_get_comment_range,
                              walk_preorder_only_main_file)
from ..comment_parsing import find_comments_connected
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
        index_finder = IndexFinder(code)

        tu: TranslationUnit = self._translation_unit_from_code(code)

        comments: list[Comment[T]] = []
        comment_ranges: set[Range] = set()
        for node in walk_preorder_only_main_file(tu.cursor):
            comment_text: str | None = node.raw_comment
            if comment_text is None:
                continue
            try:
                symbol_start = index_finder.find_index(node.extent.start.line, node.extent.start.column)
                symbol_end = index_finder.find_index(node.extent.end.line, node.extent.end.column)
                if symbol_start is None or symbol_end is None:
                    raise ValueError("No index was found")
            except ValueError:
                # Try to get the symbol_range by location
                symbol_start = index_finder.find_index(node.location.line, node.location.column)
                symbol_end = symbol_start + len(node.displayname)

            symbol_range = Range(symbol_start, symbol_end)
            symbol_text: str = code[symbol_range.start:symbol_range.end]
            symbol_indentation = self.__class__._get_symbol_indentation(code, symbol_range.start)
            symbol_type = self._get_type(node)

            comment_source_range = clang_get_comment_range(node)
            comment_start = index_finder.find_index(comment_source_range.start.line, comment_source_range.start.column)
            comment_end = index_finder.find_index(comment_source_range.end.line, comment_source_range.end.column)
            comment_range = Range(comment_start, comment_end)

            if comment_range in comment_ranges: # Prevent duplicate comments
                continue

            # To be safe, check if comment_range matches comment_text
            comment_text_by_range = code[comment_range.start:comment_range.end]
            if comment_text_by_range != comment_text:
                raise RuntimeError(f"The extracted indices do not match the actual indices of a comment:"
                      f"\n\"{comment_text}\" (getting the comment with libclang directly)"
                      f"\n!=\n\"{comment_text_by_range}\" (getting the comment with indices: {comment_range}")

            # Get only the last connected comment
            found_comments = tuple(find_comments_connected(code, comment_start, comment_end))
            if not found_comments:
                raise RuntimeError("The comment cannot be parsed")
            last_comment_range, _ = found_comments[-1]
            last_comment_text = code[last_comment_range.start:last_comment_range.end]

            comment = Comment(
                last_comment_text,
                last_comment_range,
                symbol_text,
                symbol_range,
                symbol_type,
                symbol_indentation
            )
            comments.append(comment)
            comment_ranges.add(comment_range)
        comments.sort(key=lambda x: x.comment_range.start)
        return comments

    @staticmethod
    def _get_comment_range_by_offset(cursor: Cursor) -> Range:
        # Warning: cursor.extent.start/end.offset does/did not always correspond to a start/end index of a string in Python.
        # So currently cursor.extent.start/end.line/column is used instead.
        source_range = clang_get_comment_range(cursor)
        return Range(source_range.start.offset, source_range.end.offset) # type: ignore

    @staticmethod
    def _get_symbol_indentation(code: str, symbol_start: int) -> str:
        line_start = code.rfind("\n", 0, symbol_start)
        if line_start == -1:
            return ""
        indent = code[line_start+1:symbol_start]
        if not indent.isspace():
            return ""
        return indent
