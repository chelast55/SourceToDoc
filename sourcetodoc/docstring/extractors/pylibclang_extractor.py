from typing import Callable, Iterator, Optional, override

import pylibclang._C as C
from pylibclang.cindex import Cursor, TranslationUnit

from ..extractor import Comment, Extractor
from ..range import Range  # type: ignore


class PylibclangExtractor[T](Extractor[T]):
    def __init__(
            self,
            translation_unit_from_code: Callable[[str],TranslationUnit],
            get_type: Callable[[Cursor], T]
        ) -> None:

        self.translation_unit_from_code = translation_unit_from_code
        self.get_type = get_type

    @override
    def extract_comments(self, code: str) -> list[Comment[T]]:
        tu: TranslationUnit = self.translation_unit_from_code(code)

        result: list[Comment[T]] = []
        comment_ranges: set[Range] = set()
        for node in self.__class__._walk_preorder_only_main_file(tu.cursor):
            comment_text: Optional[str] = node.raw_comment
            if comment_text is None:
                continue
            symbol_start: int = node.extent.start.offset
            symbol_end: int = node.extent.end.offset
            symbol_text: str = code[symbol_start:symbol_end]
            symbol_range = Range(symbol_start, symbol_end)
            symbol_type = self.get_type(node)
            symbol_indentation = self.__class__._get_symbol_indentation(code, symbol_start)
            comment_range = self.__class__._get_comment_range(node)

            # Prevent duplicate comments
            if comment_range not in comment_ranges:
                comment = Comment(
                    comment_text,
                    comment_range,
                    symbol_text,
                    symbol_range,
                    symbol_type,
                    symbol_indentation
                )
                result.append(comment)
                comment_ranges.add(comment_range)

        result.sort(key=lambda x: x.comment_range.start)
        return result
    
    @classmethod
    def _get_comment_range(cls, cursor: Cursor) -> Range:
        source_range = C.clang_Cursor_getCommentRange(cursor) # type: ignore
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

    @classmethod
    def _walk_preorder_only_main_file(cls, node: Cursor) -> Iterator[Cursor]:
        yield node
        for child in node.get_children(): # type: ignore
            if C.clang_Location_isFromMainFile(child.location) != 0: # type: ignore
                for descendant in cls._walk_preorder_only_main_file(child): # type: ignore
                    yield descendant
