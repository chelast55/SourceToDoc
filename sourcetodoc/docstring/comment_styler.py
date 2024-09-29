from dataclasses import dataclass
from itertools import chain
from typing import Self

from .comment_content import extract_content
from .comment_parsing import find_comments_combined
from .comment_style import BlockComment, CommentStyle, LineComment


@dataclass(frozen=True)
class CommentStyler:
    """
    Represents a C comment with a particular comment style.

    Parameters
    ----------
    content : str
        The content of the comment without comment delimiters.
    style : CommentStyle
        The (Doxygen) style of the comment.
    """
    content: str
    style: CommentStyle

    @classmethod
    def parse_comment(cls, comment_text: str) -> Self | None:
        """
        Parses `comment_text` to extract its content and (Doxygen) style.

        Parameters
        ----------
        comment_text : str
            The comment text with delimiters (e.g. `//`).

        Returns
        -------
        Optional[Self]
            A CommandStyler object if the parsing was successful, else None.
        """
        ranges_style_pairs = list(find_comments_combined(comment_text))
        if len(ranges_style_pairs) == 1:
            ranges, style = ranges_style_pairs[0]
            text = comment_text[ranges[0].start:ranges[-1].end]
            content = extract_content(text, style)
            return cls(content, style)
        else:
            return None

    def construct_comment(self, subsequent_indentation: str = "") -> str:
        """
        Constructs a comment text from `comment_content` depending on `comment_style`.

        - The first line of the comment text will not be indented.
        - Empty and blank lines from comment_content will be retained.

        Parameters
        ----------
        subsequent_indentation : str, optional
            The indentation for the returned comment text (except the first line), by default "".

        Returns
        -------
        str
            The constructed comment.
        """
        match self.style.value:
            case LineComment(_, start_delimiter):
                return self._construct_line(f"{start_delimiter} ", subsequent_indentation)
            case BlockComment(_, start_delimiter, end_delimiter, False):
                return self._construct_block(start_delimiter, end_delimiter, " * ", subsequent_indentation)
            case BlockComment(_, start_delimiter, end_delimiter):
                return self._construct_block_inline(start_delimiter, end_delimiter, subsequent_indentation)

    def _construct_line(
            self,
            start_delimiter: str,
            subsequent_indentation: str
        ) -> str:
        lines = self.content.splitlines(keepends=True)

        lines[0] = start_delimiter + lines[0]
        for i in range(1, len(lines)):
            lines[i] = subsequent_indentation + start_delimiter + lines[i]
        return "".join(lines)

    def _construct_block(
            self,
            start_delimiter: str,
            end_delimiter: str,
            deco_prefix: str,
            subsequent_indentation: str
        ) -> str:
        lines = self.content.splitlines(keepends=True)
        middle_indented = (subsequent_indentation + deco_prefix + line for line in lines)
        return "".join(chain(
            (start_delimiter, "\n"),
            middle_indented,
            ("\n", subsequent_indentation, " ", end_delimiter)))

    def _construct_block_inline(
            self,
            start_delimiter: str,
            end_delimiter: str,
            subsequent_indentation: str
        ) -> str:
        lines = self.content.splitlines()

        lines[0] = start_delimiter + " " + lines[0] + " " + end_delimiter
        for i in range(1, len(lines)):
            lines[i] = subsequent_indentation + start_delimiter + " " + lines[i] + " " + end_delimiter
        return "\n".join(lines)
