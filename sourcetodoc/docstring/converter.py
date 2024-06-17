from pathlib import Path
import re
from typing import Iterator, Optional

from .conversion import ConvEmpty, ConvError, ConvPresent, ConvResult, ConvUnsupported, Conversion
from .extractor import Extractor, Comment
from .replace import Replace
from .replacer import CommentReplacement, Replacer


class Converter[T]:
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

    def __init__(
            self,
            extractor: Extractor[T],
            conversion: Conversion[T],
            default_regex: str, replacer:
            Optional[Replacer] = None
        ) -> None:

        self.extractor = extractor
        self.conversion = conversion
        self.default_regex = default_regex
        if replacer is None:
            replacer = Replacer()
        self.replacer = replacer

    def convert_string(self, code: str, replace: Replace) -> str:
        # Extract comments
        print("Extracting comments", end="\r", flush=True)
        comments = self.extractor.extract_comments(code)
        comments_count = len(comments)
        print(f"{comments_count} comments were found")

        # Calculate new comments
        comment_conv_pair: list[tuple[Comment[T], ConvResult]] = []
        for i, comment in enumerate(comments):
            print(f"{i+1}/{comments_count} Processing comment", end="\r", flush=True)
            conv_result = self.conversion.calc_conversion(comment)
            comment_conv_pair.append((comment, conv_result))

        # Apply new comments
        conv_present_list = [
            (comment, conv_result)
            for comment, conv_result in comment_conv_pair if isinstance(conv_result, ConvPresent)
        ]
        if len(conv_present_list) == 0:
            result = code
        else:
            replacements = (
                CommentReplacement(
                    c.comment_range,
                    c.symbol_indentation,
                    c.comment_text,
                    conv_present.new_comment
                )
                for c, conv_present in conv_present_list
            )
            sorted_replacements = sorted(replacements, key=lambda e: e.range.start)
            result = self.replacer.replace_comments(code, sorted_replacements, replace)
        print(f"{len(conv_present_list)} comments were converted")
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
            print(f"{i+1}/{files_count} Converting file \"{file}\"")
            self.convert_file(file, replace)

    def _get_files(self, dir: Path, regex: str) -> Iterator[Path]:
        matcher = re.compile(regex)
        for (dirpath, _, filenames) in dir.walk():
            for filename in filenames:
                if matcher.fullmatch(filename) is not None:
                    file = (dirpath / filename)
                    yield file

    def print_message(self, conversion: ConvResult) -> None:
        match conversion:
            case ConvEmpty(message) if message is not None:
                print(f"Skip: {message}")
            case ConvUnsupported(message) if message is not None:
                print(f"Skip: {message}")
            case ConvEmpty() | ConvUnsupported():
                print("Skip")
            case ConvError():
                print(f"Error: {repr(conversion)}")
            case _:
                pass
