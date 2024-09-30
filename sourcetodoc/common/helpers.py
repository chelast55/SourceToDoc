"""
Collection of general utility/helper functions.
"""

from shutil import rmtree
from pathlib import Path

SILENT_FLAG: bool = False


def delete_directory_if_exists(directory_path: Path) -> None:
    """
    Checks if a given path is a directory and deletes it and all of its contents, without asking questions.

    Parameters
    ----------
    directory_path: Path
        Path to directory to delete
    """
    if directory_path.is_dir():
        rmtree(directory_path)
        if not SILENT_FLAG: print(f"Delete {directory_path}")


def delete_directory_contents(directory_path: Path) -> None:
    """
    Checks if a given path is a directory and deletes it and all of its contents except the directory itself, without asking questions.

    Parameters
    ----------
    directory_path: Path
        The directory.
    """
    if directory_path.is_dir():
        for item in directory_path.iterdir():
            if item.is_dir():
                rmtree(item)
            else:
                item.unlink()


class IndexFinder:
    """Finds indices of lines and columns."""

    def __init__(self, text: str) -> None:
        """
        Indexes the text.

        Parameters
        ----------
        text: str
            The text.
        """
        # line_end_indices[i] means "last index of line i"
        line_end_indices: list[int] = [-1] # dummy for case input line == 1
        last_index = len(text) - 1
        c: str = ""
        for i in range(last_index): # exclude last character
            c = text[i]
            if c == "\n": 
                line_end_indices.append(i)
        line_end_indices.append(last_index)

        self._line_end_indices = line_end_indices

    def find_index(self, line: int, column: int) -> int | None:
        """
        Returns the index of a line and column pair.

        Parameters
        ----------
        line: int
            The line.
        column: int
            The column.

        Returns
        -------
        int | None
            The index, if found, else None.

        Raises
        ------
        ValueError
            if `line` or `column` are smaller than 1.
        """
        if line < 1:
            raise ValueError(f"{line = } must be greater than zero")
        if column < 1:
            raise ValueError(f"{column = } must be greater than zero")

        if line > len(self._line_end_indices) - 1:
            return None

        line_end_index = self._line_end_indices[line]
        prev_line_end_index = self._line_end_indices[line-1]
        line_length = line_end_index - prev_line_end_index
        if column > line_length:
            return None
        else:
            return prev_line_end_index + column
