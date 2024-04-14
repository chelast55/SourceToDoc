from typing import Iterable
from sourcetodoc.docstring.common import Comment, Conversion, Range
from sourcetodoc.docstring.converter import Converter
from sourcetodoc.docstring.extractor import Extractor
from sourcetodoc.docstring.filter import Filter


def replace(text: str, replacement: str, replace_between: Range) -> str:
    return text[:replace_between.start] + replacement + text[:replace_between.end]


def replace_comments(code: str, conversions: Iterable[Conversion]) -> str:
    result: str = code
    for conversion in conversions:
        if conversion.new_docstring is not None:
            result = replace(result, conversion.new_docstring, conversion.comment.range)
    return result


class DocstringConverter:
    def __init__(self, extractor: Extractor, filter: Filter, converter: Converter) -> None:
        self.extractor = extractor
        self.filter = filter
        self.converter = converter

    def convert_comments(self, code: str) -> str:
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
        extracted_comments: Iterable[Comment] = self.extractor.extract_comments(code)
        filtered_comments: Iterable[Comment] = self.filter.filter_comments(extracted_comments)
        conversions: Iterable[Conversion] = self.converter.calc_conversions(filtered_comments)
        return replace_comments(code, conversions)
