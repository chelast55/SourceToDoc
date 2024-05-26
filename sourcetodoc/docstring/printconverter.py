from pathlib import Path
import re
from typing import Iterator, Optional, override

from .conversion import ConversionEmpty, ConversionError, ConversionPresent, ConversionResult, ConversionUnsupported, Conversion
from .extractor import Extractor
from .converter import Converter, Replace
from .replacer import Replacer


class PrintConverter[T](Converter):
    """
    Extracts comments with an `Extractor` object and converts them with a `Conversion` object.

    When `convert_string` is called:
    - The extractor extracts comments and outputs `Comment` objects.
    - The conversion object outputs a `ConversionResult` object for every `Comment` object.
    - The replacer (re)places the new comments and returns a string from every `ConversionResult` object
       that is a `ConversionPresent` object.

    Attributes
    ----------
    extractor: Extractor[T]
    converters: Conversion[T]
    default_pattern: str
    replacer: Replacer
    """

    def __init__(self, extractor: Extractor[T], conversion: Conversion[T], default_regex: str, replacer: Optional[Replacer] = None) -> None:
        self.extractor = extractor
        self.conversion = conversion
        self.default_regex = default_regex
        if replacer is None:
            replacer = Replacer()
        self.replacer = replacer

    @override
    def convert_string(self, code: str, replace: Replace) -> str:
        # Extract comments
        print("Extracting comments")
        comments = list(self.extractor.extract_comments(code))
        comments_count = len(comments)
        print(f"{comments_count} comments were found")

        # Calculate new comments
        conversions: list[ConversionResult[T]] = []
        for i, comment in enumerate(comments):
            print(f"Processing comment {i+1}/{comments_count}")
            conversion = self.conversion.calc_conversion(comment)
            conversions.append(conversion)
            self.print_message(conversion)

        # Apply new comments
        conversions_present = [e for e in conversions if isinstance(e, ConversionPresent)]
        if len(conversions_present) > 0:
            print(f"Converting {len(conversions_present)} comments")
            result = self.replacer.apply_conversions(code, conversions_present, replace)
        else:
            result = code

        # Print summary
        print(f"{len(conversions_present)} comments were converted")
        conversions_empty = [e for e in conversions if isinstance(e, ConversionEmpty)]
        print(f"{len(conversions_empty)} comments don't have to be converted")

        conversions_unsupported = [e for e in conversions if isinstance(e, ConversionUnsupported)]
        conversions_error = [e for e in conversions if isinstance(e, ConversionError)]
        print(f"{len(conversions_unsupported) + len(conversions_error)} comments can't be converted: ", end="")
        print(f"{len(conversions_unsupported)} are not supported and ", end="")
        print(f"{len(conversions_error)} raised an error")
        return result

    def convert_file(self, file: Path, replace: Replace):
        code = file.read_text()
        result = self.convert_string(code, replace)
        file.write_text(result)

    def convert_files(self, dir: Path, replace: Replace, regex: Optional[str] = None):
        if regex is None:
            regex = self.default_regex

        files = list(self._get_files(dir, regex))
        files_count = len(files)
        print(f"{files_count} files found by regex {regex}")
        for i, file in enumerate(files):
            print(f"Converting file \"{file}\" {i}/{files_count}")
            self.convert_file(file, replace)

    def _get_files(self, dir: Path, regex: str) -> Iterator[Path]:
        matcher = re.compile(regex)
        for (dirpath, _, filenames) in dir.walk():
            for filename in filenames:
                if matcher.fullmatch(filename) is not None:
                    file = (dirpath / filename)
                    yield file

    def print_message(self, conversion: ConversionResult[T]) -> None:
        match conversion:
            case ConversionEmpty(_, message) if message is not None:
                print(f"Skip: {message}")
            case ConversionUnsupported(_, message) if message is not None:
                print(f"Skip: {message}")
            case ConversionEmpty() | ConversionUnsupported():
                print("Skip")
            case ConversionError():
                print(f"Error: {repr(conversion)}")
            case _:
                pass
