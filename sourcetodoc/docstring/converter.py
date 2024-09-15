from pathlib import Path
from re import Pattern
from typing import Any

from .conversion import Conversion, ConvPresent, ConvResult
from .extractor import Comment, Extractor
from .extractors.c_libclang_extractor import CLibclangExtractor
from .extractors.c_type import CType
from .extractors.cxx_libclang_extractor import CXXLibclangExtractor
from .extractors.cxx_type import CXXType
from .replace import Replace
from .replacer import CommentReplacement, Replacer


class Converter:

    c_extractor = CLibclangExtractor()
    cxx_extractor = CXXLibclangExtractor()

    def __init__(
            self,
            c_pattern: Pattern[str],
            cxx_pattern: Pattern[str],
            conversion: Conversion[CType | CXXType],
            replace: Replace
        ) -> None:
        self.c_pattern = c_pattern
        self.cxx_pattern = cxx_pattern
        self.conversion = conversion
        self.replace = replace

    def convert_file(self, file: Path) -> None:
        """
        Converts comments in `file`.

        The source file is updated if conversions for comments are found.

        Parameters
        ----------
        file : Path
            The source file with zero or more comments.
        """
        c_matched = self.c_pattern.fullmatch(file.stem) is not None
        cxx_matched = self.cxx_pattern.fullmatch(file.stem) is not None
        if c_matched and cxx_matched:
            raise ValueError
        elif c_matched:
            print(f"\"{file}\" was identified as a C source file")
            self._convert_file(file, self.__class__.c_extractor)
        elif cxx_matched:
            print(f"\"{file}\" was identified as a C++ source file")
            self._convert_file(file, self.__class__.cxx_extractor)
        else:
            print(f"\"{file}\": Filename does not match C (specified by --c_regex) or C++ (specified by --cxx_regex) Python RegEx")


    def convert_files(self, dir: Path) -> None:
        """
        Converts comments in files in `dir` recursively.

        Parameters
        ----------
        dir : Path
            The directory.
        """
        # Collect source files
        c_files: list[Path] = []
        cxx_files: list[Path] = []
        for (dirpath, _, filenames) in dir.walk():
            for filename in filenames:
                file = (dirpath / filename)
                if self.c_pattern.fullmatch(filename) is not None:
                    c_files.append(file)
                elif self.cxx_pattern.fullmatch(filename) is not None:
                    cxx_files.append(file)
        
        c_files_count = len(c_files)
        cxx_files_count = len(cxx_files)

        # Convert source files
        print(f"{c_files_count} C source files found")
        for i, file in enumerate(c_files):
            print(f"{i+1}/{c_files_count} Converting file \"{file}\"")
            self._convert_file(file, self.c_extractor)

        print(f"{cxx_files_count} C++ source files found")
        for i, file in enumerate(cxx_files):
            print(f"{i+1}/{cxx_files_count} Converting file \"{file}\"")
            self._convert_file(file, self.cxx_extractor)

    def _convert_file(self, file: Path, extractor: Extractor[CType] | Extractor[CXXType]) -> None:
        code: str = ""
        try:  # try reading file as utf-8
            code = file.read_text()
        except UnicodeDecodeError as ue:
            print(ue)
            print(f"{str(file)} could not be decoded as utf-8. Re-attempting decode as ISO-8859-1 (latin-1):")
            try:  # try reading file as latin-1
                code = file.read_text(encoding="ISO-8859-1")
            except UnicodeDecodeError as le:
                print(le)

        result: str = self._convert_string(code, extractor)
        if result != code:
            print(f"\"{file}\" was updated")
            file.write_text(result)
            return

        print(f"\"{file}\" has not changed")

    def _convert_string(
            self,
            code: str,
            extractor: Extractor[CType] | Extractor[CXXType],
        ) -> str:
        """
        Converts comments in `code`.

        Parameters
        ----------
        code : str
            The code with zero or more comments.
        extractor: Extractor[CType] | Extractor[CXXType]
            The extractor to use to extract comments from `code`.

        Returns
        -------
        str
            The code with replaced comments.
        """
        # Extract comments
        print("Extracting comments", end="\r", flush=True)
        comments = extractor.extract_comments(code)
        comments_count = len(comments)
        print(f"{comments_count} comments were found")
        # Calculate new comments
        comment_conv_pair: list[tuple[Comment[Any], ConvResult]] = []
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
            result = Replacer.replace_comments(code, sorted_replacements, self.replace)
        print(f"{len(conv_present_list)} comments were converted")
        return result
