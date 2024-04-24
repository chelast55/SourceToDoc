from pathlib import Path
from typing import Optional, Protocol


class Parser(Protocol):

    def convert_string(self, code: str) -> str:
        """
        Converts comments to docstrings.

        Parameters
        ----------
        code : str
            The code that contains comments.

        Returns
        -------
        str
            The code with converted comments.
        """
        ...

    def convert_file(self, code_file: Path, target: Optional[Path] = None) -> None:
        """
        Converts comments to docstrings.

        Parameters
        ----------
        code_file : Path
            The file that contains code.
        target : Optional[Path], optional
            The target file, by default None.

        Raises
        ------
        ValueError
            If code_file is not a file.
        """
        if not code_file.is_file():
            raise ValueError

        if target is None:
            target = code_file
        code = code_file.read_text()
        converted_code = self.convert_string(code)
        target.write_text(converted_code)
