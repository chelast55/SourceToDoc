from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import Iterator, Mapping, Optional, overload

from openai import OpenAI

from .impl.c_converter import CConverter
from .impl.c_extractor import CExtractor
from .parser import Parser
from .simpleparser import SimpleParser


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

    @overload
    def find_parser(self, selection: Path | FileExtension) -> Optional[Language | Parser]: ...

    @overload
    def find_parser(self, selection: Language | ParserName) -> Optional[Parser]: ...

    def find_parser(self, selection: Selection) -> Optional[Language | Parser]:
        """
        Returns a Parser or Language object if one is found for the given selection.

        This method traverses (Path | FileExtension) -> (Parser | Language) -> (Parser) and
        (ParserName) -> (Parser) chains to find a parser.
        It checks for the left matching type first (e.g. Path -> Parser, then Path -> Language).

        Parameters
        ----------
        selection : Path | FileExtension | Language | ParserName
            Either a file (e.g. Path("main.c")), a file extension (e.g. FileExtension(".c")),
            a language (e.g. Language("C")), or a the name of a parser (e.g. ParserName("c_parser")).

        Returns
        -------
        Language | Parser | None
            A matching Parser object, a Language object, or None.
        """
        result = None
        match selection:
             # If selection is Path (e.g. main.c) or FileExtension (e.g. FileExtension(".c")),
             # try to find matching Parser, then try to find matching Language of no Parser was found
            case Path() | FileExtension():
                if selection in self.parser_map:
                    result = self.parser_map[selection]
                elif selection in self.language_map:
                    result = self.language_map[selection]
            case Language() | ParserName():
                result = selection

        # If result is Language (e.g. Language.C) or ParserName (e.g. ParserName("c_parser")),
        # try to find matching Parser
        match result:
            case Language() | ParserName():
                if result in self.parser_map:
                    result = self.parser_map[result]
                else:
                    result = None
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
        c_parser = SimpleParser(CExtractor(), CConverter(client))
        return {
            Language.C: c_parser,
            ParserName("c_parser"): c_parser
        }

    @staticmethod
    def create_default(client: OpenAI):
        return ParserLibrary(ParserLibrary.create_default_language_map(),
                             ParserLibrary.create_default_parser_map(client))

    def __iter__(self) -> Iterator[Parser]:
        return set(self.parser_map.values()).__iter__()
