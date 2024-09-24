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
