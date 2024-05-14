from pathlib import Path
from typing import Any, Optional

from sourcetodoc.docstring.parser_library import FileExtension, Language, ParserLibrary, ParserName
from .parser import Parser, Replace

class DocstringParser:
    """
    Uses a ParserLibrary object to choose a specific Parser object to convert comments.
    """
    def __init__(self, parser_lib: ParserLibrary) -> None:
        self.parser_lib = parser_lib

    def parse_string(self, code: str, replace: Replace, selection: Language | ParserName | Parser) -> str:
        """
        Converts comments.

        Parameters
        ----------
        code : str
            The code that contains comments.
        replace : Replace
            Specifies how to replace the comments.
        selection : Language | Parser
            If a Language object is passed, it will to find a suitable Parser object.
            If a Parser object is passed, it will use it.

        Returns
        -------
        str
            The code with converted comments.

        Raises
        ------
        ValueError
            If no parser is found.
        """
        result = self._find_parser_if_not_parser(selection)

        parser = self._check_is_parser(result)
        return parser.convert_string(code, replace)

    def parse_file(self, file: Path, replace: Replace, selection: Optional[Language | ParserName | Parser] = None) -> None:
        """
        Converts comments in a file.

        The file will be updated.
        - If None is passed, it will first use the file, and then the file extension to
          find a suitable Parser object from the parser_lib attribute.
        - If a Language object is passed, it will try to find a suitable Parser object
          from the parser_lib attribute.
        - If a Parser object is passed, it will use it.

        Parameters
        ----------
        file : Path
            The file.
        replace : Replace
            Specifies how to replace the comments.
        selection : Optional[Language  |  Parser]
            Specifies how to convert the comments.

        Raises
        ------
        ValueError
            If no parser is found.
        """
        if selection is None:
            result = self._find_parser_by_file_or_else_by_file_extension(file)
        else:
            result = self._find_parser_if_not_parser(selection)

        parser = self._check_is_parser(result)
        code = file.read_text()
        result = parser.convert_string(code, replace)
        if result != code:
            file.write_text(result)

    def parse_dir(self, dir: Path, glob_pattern: str, replace: Replace) -> None:
        """
        Converts comments in all files in a directory recursively.

        The Parser object is choosen based on the file, and then the file extension.

        Parameters
        ----------
        dir : Path
            The directory.
        glob_pattern : str
            Same pattern as for Path.glob.
        replace : Replace
            Specifies how to replace the comments.
        """
        for path in dir.glob(glob_pattern):
            if path.is_dir():
                continue
            parser = self._find_parser_by_file_or_else_by_file_extension(path)
            if not isinstance(parser, Parser):
                continue
            code = path.read_text()
            result = parser.convert_string(code, replace)
            path.write_text(result)

    def is_supported(self, selection: Path | FileExtension | Language | ParserName) -> bool:
        """
        Checks if a parser exists for the given file, file extension, or language.

        Parameters
        ----------
        selection : Path | str | Language
            The file, file extension, or language.

        Returns
        -------
        bool
            Returns True if a parser exists for selection.
        """
        return isinstance(self.parser_lib.find_parser(selection), Parser)

    def _find_parser_if_not_parser(self, input: Any):
        if isinstance(input, Parser):
            return input  # Return parser if selection is a parser
        else:
            return self.parser_lib.find_parser(input) # Else find parser

    def _find_parser_by_file_or_else_by_file_extension(self, file: Path) -> Optional[Language | Parser]:
        result = self.parser_lib.find_parser(file) # Find parser by Path
        if not isinstance(result, Parser):
            result = self.parser_lib.find_parser(FileExtension(file.suffix)) # Find parser by file extension
        return result

    def _check_is_parser(self, input: Any) -> Parser:
        if not isinstance(input, Parser):
            raise ValueError
        else:
            return input
