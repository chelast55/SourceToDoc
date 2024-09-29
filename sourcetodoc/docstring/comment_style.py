from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class LineComment:
    name: str
    start_delimiter: str


@dataclass(frozen=True)
class BlockComment:
    name: str
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

    C_LINE = LineComment("c_line", "//")
    """
    ```
    // text
    // ...
    ```
    """

    C_BLOCK = BlockComment("c_block", "/*", "*/")
    """
    ```
    /*
     * text
     * ...
     */
    ```
    """

    C_BLOCK_INLINE = BlockComment("c_block_inline", "/*", "*/", True)
    """
    ```
    /* text */
    /* ... */
    ```
    """

    JAVADOC_BLOCK = BlockComment("javadoc_block", "/**", "*/")
    """
    ```
    /**
     * text
     * ...
     */
    ```
    """

    JAVADOC_BLOCK_INLINE = BlockComment("javadoc_block_inline", "/**", "*/", True)
    """
    ```
    /** text */
    /** ... */
    ```
    """

    JAVADOC_BLOCK_MEMBER_INLINE = BlockComment("javadoc_block_member_inline", "/**<", "*/", True)
    """
    ```
    /**< text */
    /**< ... */
    ```
    """

    QT_LINE = LineComment("qt_line", "//!")
    """
    ```
    //! text
    //! ...
    ```
    """

    QT_LINE_MEMBER = LineComment("qt_line_member", "//!<")
    """
    ```
    //!< text
    //!< ...
    ```
    """

    QT_BLOCK = BlockComment("qt_block", "/*!", "*/")
    """
    ```
    /*!
     * text
     * ...
     */
    ```
    """

    QT_BLOCK_INLINE = BlockComment("qt_block_inline", "/*!", "*/", True)
    """
    ```
    /*! text */
    /*! ... */
    ```
    """

    QT_BLOCK_MEMBER_INLINE = BlockComment("qt_block_member_inline", "/*!<", "*/", True)
    """
    ```
    /*!< text */
    /*!< ... */
    ```
    """

    TRIPLE_SLASH_LINE = LineComment("triple_slash_line", "///")
    """
    ```
    /// text
    /// ...
    ```
    """

    TRIPLE_SLASH_LINE_MEMBER = LineComment("triple_slash_line_member", "///<")
    """
    ```
    ///< text
    ///< ...
    ```
    """


    def is_doxygen_style(self) -> bool:
        return self in {
            CommentStyle.JAVADOC_BLOCK,
            CommentStyle.JAVADOC_BLOCK_INLINE,
            CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE,
            CommentStyle.QT_LINE,
            CommentStyle.QT_LINE_MEMBER,
            CommentStyle.QT_BLOCK,
            CommentStyle.QT_BLOCK_INLINE,
            CommentStyle.QT_BLOCK_MEMBER_INLINE,
            CommentStyle.TRIPLE_SLASH_LINE,
            CommentStyle.TRIPLE_SLASH_LINE_MEMBER,
        }


# The order is important, because TRIPLE_SLASH_LINE and TRIPLE_SLASH_LINE_MEMBER have a common prefix
LINE_STYLES: tuple[CommentStyle,...] = (
    CommentStyle.TRIPLE_SLASH_LINE_MEMBER,
    CommentStyle.TRIPLE_SLASH_LINE,
    CommentStyle.QT_LINE_MEMBER,
    CommentStyle.QT_LINE,
    CommentStyle.C_LINE
)

# The order is important
BLOCK_INLINE_STYLES: tuple[CommentStyle,...] = (
    CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE,
    CommentStyle.JAVADOC_BLOCK_INLINE,
    CommentStyle.QT_BLOCK_MEMBER_INLINE,
    CommentStyle.QT_BLOCK_INLINE,
    CommentStyle.C_BLOCK_INLINE
)


BLOCK_STYLES: tuple[CommentStyle,...] = (
    CommentStyle.JAVADOC_BLOCK,
    CommentStyle.QT_BLOCK,
    CommentStyle.C_BLOCK
)
