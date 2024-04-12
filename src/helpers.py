from shutil import rmtree
from pathlib import Path

SILENT_FLAG: bool = False

def delete_directory_if_exists(directory_path: Path):
    """
    Checks if a given path is a directory and deletes it and all of its contents, without asking questions.

    Parameters
    ----------
    directory_path: Path
        Path to directory to delete
    """
    if directory_path.exists():
        rmtree(directory_path)
        if not SILENT_FLAG: print(f"Delete {directory_path}")