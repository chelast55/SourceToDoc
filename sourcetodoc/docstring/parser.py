from enum import Enum, auto
from typing import Protocol, runtime_checkable


class Replace(Enum):
    """
    The strategy how the comments should be replaced.
    """
    REPLACE_OLD_COMMENTS = auto()
    APPEND_TO_OLD_COMMENTS = auto()


@runtime_checkable
class Parser(Protocol):
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
