from dataclasses import dataclass
from typing import Callable, Iterable, Iterator

from .comment_styler import CommentStyler
from .range import Range
from .replace import Replace


@dataclass(frozen=True)
class CommentReplacement:
    range: Range
    indentation: str
    old_comment: str
    new_comment: str


@dataclass(frozen=True)
class TextReplacement:
    range: Range
    new_text: str


class Replacer:
    """Replaces old comments with new comments."""

    @classmethod
    def replace_comments(
        cls,
        code: str,
        comment_replacements: Iterable[CommentReplacement],
        replace: Replace
        ) -> str:
        """
        Replaces old comments in `code` with new comments given by `comment_replacements` and `replace`.

        `comment_replacements` must be in ascending order without overlap by `range`.

        Returns
        -------
        str
            Code with replaced comments.

        Raises
        ------
        ValueError
            If `comment_replacements` is not in ascending order without overlap by `range`.
        """
        new_comment_func: Callable[[CommentReplacement], str]
        match replace:
            case Replace.REPLACE_OLD_COMMENTS:
                new_comment_func = cls._new_comment_text
            case Replace.APPEND_TO_OLD_COMMENTS:
                new_comment_func = cls._old_new_concatenated
            case Replace.APPEND_TO_OLD_COMMENTS_INLINE:
                new_comment_func = cls._old_new_concatenated_same_block

        text_replacements = (TextReplacement(e.range, new_comment_func(e)) for e in comment_replacements)
        return cls.replace_text(code, text_replacements)

    @classmethod
    def replace_text(cls, text: str, text_replacements: Iterable[TextReplacement]) -> str:
        """
        Replaces parts in `text` given by `text_replacements`.

        `text_replacements` must be in ascending order without overlap by `range`.

        Returns
        -------
        str
            Text with replaced parts.
        
        Raises
        ------
        ValueError
            If `text_replacements` is not in ascending order without overlap by `range`.
        """
        return "".join(cls.replace_text_iter(text, text_replacements))

    @classmethod
    def replace_text_iter(cls, text: str, text_replacements: Iterable[TextReplacement]) -> Iterator[str]:
        """
        Replaces parts in `text` given by `text_replacements`.

        `text_replacements` must be in ascending order without overlap by `range`.
        Concatenate the yielded results to get the entire result like in the `replace_text` method.

        Yields
        ------
        str
            Text with replaced parts.
        
        Raises
        ------
        ValueError
            If `text_replacements` is not in ascending order without overlap by `range`.
        """
        start = 0
        for e in text_replacements:
            end = e.range.start
            if end < start:
                raise ValueError("text_replacements must be in ascending order without overlap")
            yield text[start:end]
            yield e.new_text
            start = e.range.end
        yield text[start:]

    @classmethod
    def _new_comment_text(cls, replacement: CommentReplacement) -> str:
        return replacement.new_comment

    @classmethod
    def _old_new_concatenated(cls, replacement: CommentReplacement) -> str:
        return replacement.old_comment + "\n" + replacement.indentation + replacement.new_comment

    @classmethod
    def _old_new_concatenated_same_block(cls, replacement: CommentReplacement) -> str:
        match CommentStyler.parse_comment(replacement.old_comment):
            case CommentStyler(old_content, _):
                pass
            case None:
                raise RuntimeError

        match CommentStyler.parse_comment(replacement.new_comment):
            case CommentStyler(new_content, new_style):
                concat_content = old_content + "\n\nNEW_COMMENT\n" + new_content
                concat_comment = CommentStyler(
                    concat_content, new_style
                ).construct_comment(replacement.indentation)
            case None:
                raise RuntimeError
        return concat_comment
