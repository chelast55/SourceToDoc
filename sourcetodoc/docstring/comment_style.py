from itertools import chain
import re
from dataclasses import dataclass
from enum import Enum
from textwrap import dedent
from typing import ClassVar, Iterable, Iterator, Optional, Self


@dataclass(frozen=True)
class _LineComment:
    start_delimiter: str


@dataclass(frozen=True)
class _BlockComment:
    start_delimiter: str
    end_delimiter: str
    is_inline: bool = False


class CommentStyle(Enum):
    """
    Specifies the style of the comment.

    Conventions:

    `_LINE`:
        Comment has a start delimiter that ends at the end of line that can span over multiple lines.

    `_BLOCK`:
        Comment has a start delimiter and an end delimiter that can span over multiple lines).

    `_BLOCK_INLINE`:
        Comment has a start delimiter and an end delimiter in the same line.
    
    `_MEMBER`:
        Typically for comments after member variables.
    """

    C_LINE = _LineComment("//")
    """
    ```
    // text
    // ...
    ```
    """

    C_BLOCK_INLINE = _BlockComment("/*", "*/", True)
    """
    ```
    /* text */
    /* ... */
    ```
    """

    C_BLOCK = _BlockComment("/*", "*/")
    """
    ```
    /*
     * text
     * ...
     */
    ```
    """

    JAVADOC_BLOCK = _BlockComment("/**", "*/")
    """
    ```
    /**
     * text
     * ...
     */
    ```
    """

    JAVADOC_BLOCK_INLINE = _BlockComment("/**", "*/", True)
    """
    ```
    /** text */
    /** ... */
    ```
    """

    JAVADOC_BLOCK_MEMBER_INLINE = _BlockComment("/**<", "*/", True)
    """
    ```
    /**< text */
    /**< ... */
    ```
    """

    QT_BLOCK = _BlockComment("/*!", "*/")
    """
    ```
    /*!
     * text
     * ...
     */
    ```
    """

    QT_BLOCK_INLINE = _BlockComment("/*!", "*/", True)
    """
    ```
    /*! text */
    /*! ... */
    ```
    """

    QT_BLOCK_MEMBER_INLINE = _BlockComment("/*!<", "*/", True)
    """
    ```
    /*!< text */
    /*!< ... */
    ```
    """

    TRIPLE_SLASH_LINE = _LineComment("///")
    """
    ```
    /// text
    /// ...
    ```
    """

    TRIPLE_SLASH_LINE_MEMBER = _LineComment("///<")
    """
    ```
    ///< text
    ///< ...
    ```
    """

    QT_LINE = _LineComment("//!")
    """
    ```
    //! text
    //! ...
    ```
    """
    QT_LINE_MEMBER = _LineComment("//!<")
    """
    ```
    //!< text
    //!< ...
    ```
    """

    def is_doxygen_style(self) -> bool:
        return self in {
            CommentStyle.JAVADOC_BLOCK,
            CommentStyle.JAVADOC_BLOCK_INLINE,
            CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE,
            CommentStyle.QT_BLOCK,
            CommentStyle.QT_BLOCK_INLINE,
            CommentStyle.QT_BLOCK_MEMBER_INLINE,
            CommentStyle.TRIPLE_SLASH_LINE,
            CommentStyle.TRIPLE_SLASH_LINE_MEMBER,
            CommentStyle.QT_LINE,
            CommentStyle.QT_LINE_MEMBER,
        }

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

    _C_LINE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"//.*(?:\n(?: |\t)*//.*)*"
    )
    _C_BLOCK_INLINE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"/\*.*?\*/(?:(?: |\t)*\n(?: |\t)*/\*.*?\*/)*"
    )
    _C_BLOCK_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"/\*(?:.|\n)*?\*/"
    )

    @classmethod
    def parse_comment(cls, comment_text: str) -> Optional[Self]:
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
        text_stripped = comment_text.strip()
        if cls._C_LINE_PATTERN.fullmatch(text_stripped) is not None:
            style = cls._get_style_by_delimiter(text_stripped, (
                CommentStyle.TRIPLE_SLASH_LINE_MEMBER,
                CommentStyle.TRIPLE_SLASH_LINE,
                CommentStyle.QT_LINE_MEMBER,
                CommentStyle.QT_LINE,
                CommentStyle.C_LINE,
            ))
            start_delimiter = style.value.start_delimiter
            content = cls._extract_content_from_line_comment(
                text_stripped, start_delimiter
            )

        elif cls._C_BLOCK_INLINE_PATTERN.fullmatch(text_stripped) is not None:
            content, style = cls._extract_content_from_block_inline_comment(
                text_stripped
            )

        elif cls._C_BLOCK_PATTERN.fullmatch(text_stripped) is not None:
            style = cls._get_style_by_delimiter(text_stripped, (
                CommentStyle.JAVADOC_BLOCK,
                CommentStyle.QT_BLOCK,
                CommentStyle.C_BLOCK,
            ))
            start_delimiter = style.value.start_delimiter
            end_delimiter = style.value.end_delimiter # type: ignore
            content = cls._extract_content_from_block_comment(
                text_stripped, start_delimiter, end_delimiter, "*" # type: ignore
            )

        else:
            return None

        content_stripped = content.strip()
        return cls(content_stripped, style)

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
            case _LineComment(start_delimiter):
                return self._construct_line(f"{start_delimiter} ", subsequent_indentation)
            case _BlockComment(start_delimiter, end_delimiter, False):
                return self._construct_block(start_delimiter, end_delimiter, " * ", subsequent_indentation)
            case _BlockComment(start_delimiter, end_delimiter):
                return self._construct_block_inline(start_delimiter, end_delimiter, subsequent_indentation)
    
    @classmethod
    def _get_style_by_delimiter(
        cls,
        text_stripped: str,
        candidates: Iterable[CommentStyle]
    ) -> CommentStyle:
        """
        Gets the style by checking the prefix (and suffix) of `candidates` on `text_stripped`.
        """
        for candidate in candidates:
            c = candidate.value
            if text_stripped.startswith(c.start_delimiter):
                if isinstance(c, _BlockComment) and not text_stripped.endswith(c.end_delimiter):
                    continue
                return candidate
        raise RuntimeError

    @classmethod
    def _extract_content_from_line_comment(cls, text_stripped: str, prefix: str) -> str:
        text = "".join(cls._remove_and_check_prefix_in_every_line(text_stripped, prefix))
        return dedent(text)

    @classmethod
    def _remove_and_check_prefix_in_every_line(
        cls,
        text_stripped: str,
        prefix: str
    ) -> Iterator[str]:
        for line in text_stripped.splitlines(keepends=True):
            line_left_stripped = line.lstrip()
            if not line_left_stripped.startswith(prefix):
                raise ValueError(f"Not all lines of {text_stripped} start with {prefix}")
            yield line_left_stripped.removeprefix(prefix)
    
    @classmethod
    def _extract_content_from_block_inline_comment(
        cls,
        text: str,
    ) -> tuple[str, CommentStyle]:
        found_styles: set[CommentStyle] = set()
        lines = text.splitlines()
        for i in range(len(lines)):
            lines[i], style = cls._get_from_inline_line(lines[i].strip())
            found_styles.add(style)

        content = dedent("\n".join(lines))
        if len(found_styles) == 1:
            return content, found_styles.pop()
        else:
            return content, CommentStyle.C_BLOCK_INLINE
    
    @classmethod
    def _get_from_inline_line(cls, line_stripped: str) -> tuple[str, CommentStyle]:
        style = cls._get_style_by_delimiter(line_stripped, (
            CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE,
            CommentStyle.JAVADOC_BLOCK_INLINE,
            CommentStyle.QT_BLOCK_MEMBER_INLINE,
            CommentStyle.QT_BLOCK_INLINE,
            CommentStyle.C_BLOCK_INLINE,
        ))

        return (line_stripped
            .removeprefix(style.value.start_delimiter)
            .removesuffix(style.value.end_delimiter) # type: ignore
            .rstrip()), style

    @classmethod
    def _extract_content_from_block_comment(
        cls,
        text_stripped: str,
        start_delimiter: str,
        end_delimiter: str,
        deco_prefix: str = ""
    ) -> str:
        lines = text_stripped.splitlines(keepends=True)

        start_index = 0
        end_index = len(lines)

        # Exclude start_delimiter, e.g. "/*..." or "/*\n..." to "..."
        lines[0] = lines[0].removeprefix(start_delimiter)
        if lines[0].isspace():
            start_index = 1

        # Exclude end_delimiter, e.g. "...*/" or "...\n␣␣␣*/" to "..."
        lines[-1] = lines[-1].removesuffix(end_delimiter)
        if lines[-1].isspace() and end_index >= 2:
            end_index = end_index - 1
            lines[-2] = lines[-2].removesuffix("\n")

        # For every line except first line: From the left remove whitespaces,
        # then remove the prefix (e.g. "*")
        for i in range(1, end_index):
            lines[i] = lines[i].lstrip().removeprefix(deco_prefix)
        
        content = "".join(lines[start_index:end_index])
        return dedent(content)

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
