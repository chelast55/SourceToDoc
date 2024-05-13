from enum import Enum, unique
from pathlib import Path
from typing import Iterator, Mapping

from openai import OpenAI

from .impl.c_parser import CParser
from .parser import Parser


@unique
class Language(Enum):
    """
    Represents a programming language.

    Example: `Language("C")` is `Language.C`.
    """
    C = "C"
    CPP = "C++"


class ParserLibrary:
    """
    Contains a collection of Parser objects.

    Use the method find_parser to find a parser.
    The attributes language_map and parser_map determine its return value.

    Attributes
    ----------
    language_map : Mapping[Path  |  str, Language]
        Intermediate mapping to find a Parser object.
    parser_map : Mapping[Path  |  str  |  Language, Parser]
        A mapping that contains Parser objects.
    """
    def __init__(self,
                 language_map: Mapping[Path | str, Language],
                 parser_map: Mapping[Path | str | Language, Parser]) -> None:
        """
        Constructs a ParserLibrary object.

        Parameters
        ----------
        language_map : Mapping[Path  |  str, Language]
        parser_map : Mapping[Path  |  str  |  Language, Parser]
        """
        self.language_map = language_map
        self.parser_map = parser_map

    def find_parser(self, selection: Path | str | Language) -> Path | str | Language | Parser:
        """
        Returns a Parser object if one is found for the given selection.

        This method traverses a (Path | str) -> (Parser | Language) -> (Parser) chain to find a parser for selection.
        It checks for the leftmost matching type first (e.g. Path -> Parser, then Path -> Language).

        Parameters
        ----------
        selection : Path | str | Language
            Either a file (e.g. main.c), a file extension (e.g. ".c"), or a Language (e.g. Language.C).

        Returns
        -------
        Path | str | Language | Parser
            A matching Parser object, a Language object, or selection
        """
        result = selection

        if isinstance(result, Path): # If result is Path (e.g. main.c), then try to find matching Parser, then Language
            if result in self.parser_map:
                result = self.parser_map[result]
            elif result in self.language_map:
                result = self.language_map[result]

        elif isinstance(result, str): # If result is str (e.g. ".c"), then try to find matching Parser, then Language
            if result in self.parser_map:
                result = self.parser_map[result]
            elif result in self.language_map:
                result = self.language_map[result]

        if isinstance(result, Language): # If result is Language (e.g. Language.C), then try to find matching Parser
            if result in self.parser_map:
                result = self.parser_map[result]

        return result

    @staticmethod
    def create_default_language_map() -> Mapping[Path | str, Language]:
        return {
            ".c": Language.C,
            ".h": Language.C,
            ".cpp": Language.CPP,
            ".hh": Language.CPP
        }

    @staticmethod
    def create_default_parser_map(client: OpenAI) -> Mapping[Path | str | Language, Parser]:
        return {
            Language.C: CParser(client),
        }

    @staticmethod
    def create_default(client: OpenAI):
        return ParserLibrary(ParserLibrary.create_default_language_map(),
                             ParserLibrary.create_default_parser_map(client))

    def __iter__(self) -> Iterator[Parser]:
        return set(self.parser_map.values()).__iter__()
