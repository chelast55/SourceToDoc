import re
from dataclasses import dataclass
from enum import Enum, auto
from textwrap import dedent, indent
from typing import ClassVar, Iterator, Optional, Self


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

    C_LINE = auto()
    """
    ```
    // text
    // ...
    ```
    """

    C_BLOCK_INLINE = auto()
    """
    ```
    /* text */
    ```
    """

    C_BLOCK = auto()
    """
    ```
    /*
     * text
     * ...
     */
    ```
    """

    JAVADOC_BLOCK = auto()
    """
    ```
    /**
     * text
     * ...
     */
    ```
    """

    JAVADOC_BLOCK_INLINE = auto()
    """
    ```
    /** text */
    ```
    """

    JAVADOC_BLOCK_MEMBER_INLINE = auto()
    """
    ```
    /**< text */
    ```
    """

    QT_BLOCK = auto()
    """
    ```
    /*!
     * text
     * ...
     */
    ```
    """

    QT_BLOCK_INLINE = auto()
    """
    ```
    /*! text */
    ```
    """

    QT_BLOCK_MEMBER_INLINE = auto()
    """
    ```
    /*!< text */
    ```
    """

    TRIPLE_SLASH_LINE = auto()
    """
    ```
    /// text
    /// ...
    ```
    """

    TRIPLE_SLASH_LINE_MEMBER = auto()
    """
    ```
    ///< text
    ///< ...
    ```
    """

    QT_LINE = auto()
    """
    ```
    //! text
    //! ...
    ```
    """
    QT_LINE_MEMBER = auto()
    """
    ```
    //!< text
    //!< ...
    ```
    """


@dataclass(frozen=True)
class CommentStyler:
    """
    Represents a comment.

    Attributes
    ----------
    comment_content : str
        The content of the comment without comment delimiters.
    comment_style : CommentStyle
        The style of the comment.
    """
    comment_content: str
    comment_style: CommentStyle

    _C_LINE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"//.*(?:\n[ \t]*//.*)*")
    _C_BLOCK_INLINE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"/\*[.]*?\*/(?:\n/\*[.]*?\*/)*")
    _C_BLOCK_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"/\*[.\n]*?\*/")

    _LAST_LINE_SPACES_OR_TABS_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\n[ \t]*$")

    @classmethod
    def parse_comment(cls, text: str) -> Optional[Self]:
        """
        Creates a new instance from a comment text.

        Parameters
        ----------
        input : str
            The comment text.

        Returns
        -------
        Optional[Self]
            A new CommentRepr instance if a CommentStyle is found for input, else None.
        """
        text_stripped = text.strip()
        if cls._C_LINE_PATTERN.fullmatch(text_stripped) is not None:
            content = cls._extract_content_from_line_comment(text_stripped, "//")

            style = CommentStyle.C_LINE
            if text_stripped.startswith("///<"):
                style = CommentStyle.TRIPLE_SLASH_LINE_MEMBER
            elif text_stripped.startswith("///"):
                style = CommentStyle.TRIPLE_SLASH_LINE
            elif text_stripped.startswith("//!<"):
                style = CommentStyle.QT_BLOCK_MEMBER_INLINE
            elif text_stripped.startswith("//!"):
                style = CommentStyle.QT_BLOCK

        elif cls._C_BLOCK_INLINE_PATTERN.fullmatch(text_stripped) is not None:
            content = cls._extract_content_from_block_comment(text_stripped, "/*", "*/")

            style = CommentStyle.C_BLOCK_INLINE
            if text_stripped.startswith("/**<"):
                style = CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE
            elif text_stripped.startswith("/**"):
                style = CommentStyle.JAVADOC_BLOCK_INLINE
            elif text_stripped.startswith("/*!<"):
                style = CommentStyle.QT_BLOCK_MEMBER_INLINE
            elif text_stripped.startswith("/*!"):
                style = CommentStyle.QT_BLOCK_INLINE

        elif cls._C_BLOCK_PATTERN.fullmatch(text_stripped) is not None:
            content = cls._extract_content_from_block_comment(text_stripped, "/*", "*/", "*")

            style = CommentStyle.C_BLOCK
            if text_stripped.startswith("/**"):
                style = CommentStyle.JAVADOC_BLOCK
            elif text_stripped.startswith("/*!"):
                style = CommentStyle.QT_BLOCK

        else:
            return None

        content_stripped = content.strip()
        return cls(content_stripped, style)

    def construct_comment(self, indentation: str = "") -> str:
        """
        Constructs a comment text from comment_content depending on comment_style.

        - The first line of the comment text will not be indented.
        - Empty and blank lines from comment_content will be retained.

        Parameters
        ----------
        indentation : str, optional
            The indentation for the returned comment text (except the first line), by default "".

        Returns
        -------
        str
            The comment text.
        """
        match self.comment_style:
            case CommentStyle.C_LINE:
                return self._construct_line("// ", indentation)
            case CommentStyle.C_BLOCK:
                return self._construct_block("/*", " */", " * ", indentation)
            case CommentStyle.C_BLOCK_INLINE:
                return self._construct_block_inline("/* ", " */")
            case CommentStyle.JAVADOC_BLOCK:
                return self._construct_block("/**", " */", " * ", indentation)
            case CommentStyle.JAVADOC_BLOCK_INLINE:
                return self._construct_block_inline("/** ", " */")
            case CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE:
                return self._construct_block_inline("/**< ", " */")
            case CommentStyle.QT_BLOCK:
                return self._construct_block("/*!", " */", " * ", indentation)
            case CommentStyle.QT_BLOCK_INLINE:
                return self._construct_block_inline("/*! ", " */")
            case CommentStyle.QT_BLOCK_MEMBER_INLINE:
                return self._construct_block_inline("/*!< ", " */")
            case CommentStyle.TRIPLE_SLASH_LINE:
                return self._construct_line("/// ", indentation)
            case CommentStyle.TRIPLE_SLASH_LINE_MEMBER:
                return self._construct_line("///< ", indentation)
            case CommentStyle.QT_LINE:
                return self._construct_line("//! ", indentation)
            case CommentStyle.QT_LINE_MEMBER:
                return self._construct_line("//!< ", indentation)

    @classmethod
    def _extract_content_from_line_comment(cls, text_stripped: str, prefix: str) -> str:
        text = "".join(cls._remove_and_check_prefix_in_every_line(text_stripped, prefix))
        return dedent(text)
    
    @classmethod
    def _remove_and_check_prefix_in_every_line(cls, text_stripped: str, prefix: str) -> Iterator[str]:
        for line in text_stripped.splitlines(keepends=True):
            line_left_stripped = line.lstrip()
            if not line_left_stripped.startswith(prefix):
                raise ValueError(f"Not all lines of {text_stripped} start with {prefix}")
            yield line_left_stripped.removeprefix(prefix)

    @classmethod
    def _extract_content_from_block_comment(cls, text_stripped: str, first: str, last: str, line_prefix: str = "") -> str:
        # Remove prefix, e.g. "/*..." or "/*\n..." to "..."
        tmp = (text_stripped
               .removeprefix(first)
               .removeprefix("\n"))
    
        # Remove suffix, e.g. "...*/" or "...\n␣␣␣*/" to "..."
        tmp = cls._LAST_LINE_SPACES_OR_TABS_PATTERN.sub("", tmp.removesuffix(last))

        # For every line: From the left remove whitespaces, then remove line_prefix (e.g. "*")
        content = "".join(line.lstrip().removeprefix(line_prefix) for line in tmp.splitlines(keepends=True))
        return dedent(content)

    def _construct_line(self, line_prefix: str, indentation: str) -> str:
        lines = self.comment_content.splitlines(keepends=True)
        first_line_not_indented = line_prefix + lines[0]
        other_lines_indented = "".join(indentation + line_prefix + line for line in lines[1:])
        return first_line_not_indented + other_lines_indented

    def _construct_block(self, prefix: str, suffix: str, line_prefix: str, indentation: str) -> str:
        top_not_indented = prefix
        middle_indented = indent(self.comment_content, indentation + line_prefix, lambda _: True)
        end_indented =  f"{indentation}{suffix}"
        return f"{top_not_indented}\n{middle_indented}\n{end_indented}"
    
    def _construct_block_inline(self, prefix: str, suffix: str) -> str:
        return "".join(suffix + line + prefix for line in self.comment_content)
