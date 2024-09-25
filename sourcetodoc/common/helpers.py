"""
Collection of general utility/helper functions.
"""

from shutil import rmtree
from pathlib import Path
from typing import Iterable, Iterator

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


def index_from_coordinates(text: str, line_column_pairs: Iterable[tuple[int,int]]) -> Iterator[int]:
    """
    Returns the indices of the corresponding lines and columns of the given text.

    Parameters
    ----------
    text: str
        The text.
    line_column_pairs: Iterable[tuple[int,int]]
        2-tuples (line,column) in ascending order.

    Yields
    ------
    Iterator[int]
        The i-index of the i-line-column pair.

    Raises
    ------
    ValueError
        If no index was found for a line-column pair.
    """
    current_line: int = 1
    current_column: int = 1
    i: int = 0

    for line, column in line_column_pairs:
        while True:
            if line == current_line and column == current_column:
                yield i
                break
            elif line < current_line or (line == current_line and column < current_column):
                raise ValueError(f"No index was found for Line: {line} and Column: {column}")
            if text[i] == "\n":
                current_line = current_line + 1
                current_column = 1
            else:
                current_column = current_column + 1
            i = i + 1
