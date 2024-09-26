from pathlib import Path
from re import Pattern, compile
from typing import Any, ClassVar

from .conversion import ConvEmpty, ConvError, ConvUnsupported, Conversion, ConvPresent, ConvResult
from .extractor import Comment, Extractor
from .extractors.c_libclang_extractor import CLibclangExtractor
from .extractors.c_type import CType
from .extractors.cxx_libclang_extractor import CXXLibclangExtractor
from .extractors.cxx_type import CXXType
from .replace import Replace
from .replacer import CommentReplacement, Replacer


class Converter:
    """
    The Converter converts comments in source code.
    """

    _DEFAULT_C_PATTERN: ClassVar[Pattern[str]] = compile(r".*\.[ch]")
    _DEFAULT_CXX_PATTERN: ClassVar[Pattern[str]] = compile(r".*\.(c(pp|xx|c)|h(pp|xx|h)?)")

    _DEFAULT_C_EXTRACTOR: ClassVar[Extractor[CType]] = CLibclangExtractor()
    _DEFAULT_CXX_EXTRACTOR: ClassVar[Extractor[CXXType]] = CXXLibclangExtractor()

    def __init__(
            self,
            conversion: Conversion[CType | CXXType],
            replace: Replace,
            c_pattern: Pattern[str] | None = None,
            cxx_pattern: Pattern[str] | None = None,
            c_extractor: Extractor[CType] | None = None,
            cxx_extractor: Extractor[CXXType] | None = None
        ) -> None:
        """
        Creates a new `Converter` object.

        Parameters
        ----------
        conversion: Conversion[CType | CXXType]
            The `Conversion` object to use to convert comments.
        replace: Replace
            Specifies how new comments are added.
        c_pattern: Pattern[str] | None, optional
            Used to determine C source files, by default `r".*\\.[ch]"`
        cxx_pattern: Pattern[str] | None, optional
            Used to determine C++ source files, by default `r".*\\.(c(pp|xx|c)|h(pp|xx|h)?)"`
        """
        self.conversion = conversion
        self.replace = replace
        self.c_pattern = c_pattern if c_pattern is not None else self.__class__._DEFAULT_C_PATTERN
        self.cxx_pattern = cxx_pattern if cxx_pattern is not None else self.__class__._DEFAULT_CXX_PATTERN
        self.c_extractor = c_extractor if c_extractor is not None else self.__class__._DEFAULT_C_EXTRACTOR
        self.cxx_extractor = cxx_extractor if cxx_extractor is not None else self.__class__._DEFAULT_CXX_EXTRACTOR

    def convert_file(self, file: Path) -> None:
        """
        Converts comments in `file`.

        The source file is updated if conversions for comments are found.

        Parameters
        ----------
        file : Path
            The source file with zero or more comments.
        """
        match (self.c_pattern.fullmatch(file.name) is not None,
               self.cxx_pattern.fullmatch(file.name) is not None):
            case True, _:
                print(f"\"{file}\" was identified as a C source file")
                self._convert_file(file, self.c_extractor)
            case False, True:
                print(f"\"{file}\" was identified as a C++ source file")
                self._convert_file(file, self.cxx_extractor)
            case False, False:
                print(f"Skip \"{file}\": Filename does not match C ({self.c_pattern} specified by --c_regex) \n"
                      f"or C++ ({self.cxx_pattern} specified by --cxx_regex) Python RegEx")

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
        for i, file in enumerate(c_files, start=1):
            print(f"{i}/{c_files_count} Converting file \"{file}\"")
            self._convert_file(file, self.c_extractor)

        print(f"{cxx_files_count} C++ source files found")
        for i, file in enumerate(cxx_files, start=1):
            print(f"{i}/{cxx_files_count} Converting file \"{file}\"")
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

        result: str | None = None
        try:
            result = self._convert_string(code, extractor)
        except Exception:
            if extractor == self.c_extractor:
                print(f"An error occured when parsing \"{file}\" as a C file. Trying to parse it as a C++ file...")
                try:
                    result = self._convert_string(code, self.cxx_extractor)
                except Exception as e:
                    print(f"An error occured when parsing \"{file}\" as a C++ file: {e}. Skipping the file...")

        if result is not None and result != code:
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
        for i, comment in enumerate(comments, start=1):
            print(f"{i}/{comments_count} Processing comment", end="\r", flush=True)
            conv_result = self.conversion.calc_conversion(comment)
            self.__class__._print_if_not_present(conv_result)
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

    @staticmethod
    def _print_if_not_present(conv_result: ConvResult) -> None:
        match conv_result:
            case ConvEmpty(None) :
                print("Skip: No conversion was found")
            case ConvUnsupported(None):
                print(f"Skip: The comment is not supported")
            case ConvError(None):
                print("Skip: An error occured")
            case ConvEmpty(message):
                print(f"Skip: No conversion was found: {message}")
            case ConvUnsupported(message):
                print(f"Skip: The comment is not supported: {message}")
            case ConvError(message):
                print(f"Skip: An error occured: {message}")
            case ConvPresent():
                pass
