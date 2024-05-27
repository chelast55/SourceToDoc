from enum import Enum, auto
from typing import Protocol, runtime_checkable


class Replace(Enum):
    """
    Specifies how the comments should be replaced.
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


@runtime_checkable
class Converter(Protocol):
    """
    Converts comments.
    """
    def convert_string(self, code: str, replace: Replace) -> str:
        """
        Converts comments.

        Parameters
        ----------
        code : str
            The code that contains comments.
        replace : Replace
            Specifies how the comments should be replaced.

        Returns
        -------
        str
            The code with converted comments.
        """
        ...
