from pathlib import Path
from typing import Optional

from .conversion import Conversion, ConvPresent, ConvResult
from .extractor import Comment, Extractor
from .replace import Replace
from .replacer import CommentReplacement, Replacer
from .util import get_files


class Converter[T]:
    """
    Extracts comments with an `Extractor` object and converts them with a `Conversion` object.

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
            default_regex: str,
            replacer: Optional[Replacer] = None
        ) -> None:

        self.extractor = extractor
        self.conversion = conversion
        self.default_regex = default_regex
        if replacer is None:
            replacer = Replacer()
        self.replacer = replacer

    def convert_string(self, code: str, replace: Replace) -> str:
        """
        Converts comments in `code`.

        Parameters
        ----------
        code : str
            The code with zero or more comments.

        replace : Replace
            Specifies how new comments are added.

        Returns
        -------
        str
            The code with replaced comments.
        """
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
        """
        Converts comments in `file`.

        The source file is updated if conversions for comments are found.

        Parameters
        ----------
        file : Path
            The source file with zero or more comments.
        replace : Replace
            Specifies how new comments are added.
        """
        code = file.read_text()
        result = self.convert_string(code, replace)
        if result != code:
            print(f"\"{file}\" was updated")
            file.write_text(result)
        else:
            print(f"\"{file}\" has not changed")

    def convert_files(self, dir: Path, replace: Replace, regex: Optional[str] = None):
        """
        Converts comments in files in `dir` recursively.

        The filenames of the files must be fully matched by `regex`.

        Parameters
        ----------
        dir : Path
            The directory.
        replace : Replace
            Specifies how new comments are added.
        regex : Optional[str], optional
            The Python RegEx to include files, by default None
        """
        if regex is None:
            regex = self.default_regex

        files = list(get_files(dir, regex))
        files_count = len(files)
        print(f"{files_count} files found by regex {regex}")
        for i, file in enumerate(files):
            print(f"{i+1}/{files_count} Converting file \"{file}\"")
            self.convert_file(file, replace)
