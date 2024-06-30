from enum import Enum, auto


class Replace(Enum):
    """
    Specifies how new comments are added.
    """

    REPLACE_OLD_COMMENTS = auto()
    """
    Old comments will be replaced.

    Example:

    Old comment:
    ```
    /*
     * Old comment
     */
    ```
    New comment:
    ```
    /**
     * New comment
     */
    ```

    Result:
    ```
    /**
     * New comment
     */
    ```
    """
    APPEND_TO_OLD_COMMENTS = auto()
    """
    New comments will be placed under old comments.

    Example:

    Old comment:
    ```
    /*
     * Old comment
     */
    ```
    New comment:
    ```
    /**
     * New comment
     */
    ```

    Result:
    ```
    /**
     * Old comment
     */
    /**
     * New comment
     */
    ```
    """
    APPEND_TO_OLD_COMMENTS_INLINE = auto()
    """
    Same as APPEND_TO_OLD_COMMENTS, but in case that both old and new comments are `/*...*/`,
    they will be in the same comment block the text NEW_COMMENT is added above the new comment.

    Example:

    Old comment:
    ```
    /*
     * Old comment
     */
    ```
    New comment:
    ```
    /*
     * New comment
     */
    ```

    Result:
    ```
    /**
     * Old comment
     *
     * NEW_COMMENT
     * New comment
     */
    ```

    Note: `/**` will always be added at the start.
    """
