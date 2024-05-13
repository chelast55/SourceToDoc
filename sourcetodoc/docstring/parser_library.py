from dataclasses import dataclass
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


@dataclass(frozen=True)
class FileExtension:
    ext: str


@dataclass(frozen=True)
class ParserName:
    name: str


type Selection = Path | FileExtension | Language | ParserName


class ParserLibrary:
    """
    Contains a collection of Parser objects.

    Use the method find_parser to find a parser.
    The attributes language_map and parser_map determine its return value.

    Attributes
    ----------
    language_map : Mapping[Path | FileExtension, Language]
        A mapping to find a Language objects to find Parser objects with parser_map.
    parser_map : Mapping[Path | FileExtension | Language | ParserName, Parser]
        A mapping that contains Parser objects.
    """
    def __init__(self,
                 language_map: Mapping[Path | FileExtension, Language],
                 parser_map: Mapping[Selection, Parser]) -> None:
        """
        Constructs a ParserLibrary object.

        Parameters
        ----------
        language_map : Mapping[Path | FileExtension, Language]
        parser_map : Mapping[Path | FileExtension | Language | ParserName, Parser]
        """
        self.language_map = language_map
        self.parser_map = parser_map

    def find_parser(self, selection: Selection) -> Selection | Parser:
        """
        Returns a Parser object if one is found for the given selection.

        This method traverses (Path | FileExtension) -> (Parser | Language) -> (Parser) and
        (ParserName) -> (Parser) chains to find a parser.
        It checks for the left matching type first (e.g. Path -> Parser, then Path -> Language).

        Parameters
        ----------
        selection : Path | FileExtension | Language | ParserName
            Either a file (e.g. main.c), a file extension (e.g. ".c"), or a Language (e.g. Language.C).

        Returns
        -------
        Path | FileExtension | Language | ParserName | Parser
            A matching Parser object, a Language object, or selection
        """
        result = selection

        match result:
             # If result is Path (e.g. main.c) or FileExtension, then try to find matching Parser, then Language
            case Path() | FileExtension():
                if result in self.parser_map:
                    result = self.parser_map[result]
                elif result in self.language_map:
                    result = self.language_map[result]
            case Language() | ParserName():
                pass

        # If result is Language (e.g. Language.C) or ParserName, then try to find matching Parser
        match result:
            case Language() | ParserName():
                if result in self.parser_map:
                    result = self.parser_map[result]
            case _:
                pass

        return result

    @staticmethod
    def create_default_language_map() -> Mapping[Path | FileExtension, Language]:
        return {
            FileExtension(".c"): Language.C,
            FileExtension(".h"): Language.C,
            FileExtension(".cpp"): Language.CPP,
            FileExtension(".hh"): Language.CPP
        }

    @staticmethod
    def create_default_parser_map(client: OpenAI) -> Mapping[Selection, Parser]:
        return {
            Language.C: CParser(client),
            ParserName("c_parser"): CParser(client)
        }

    @staticmethod
    def create_default(client: OpenAI):
        return ParserLibrary(ParserLibrary.create_default_language_map(),
                             ParserLibrary.create_default_parser_map(client))

    def __iter__(self) -> Iterator[Parser]:
        return set(self.parser_map.values()).__iter__()
