from typing import Iterable, override
from sourcetodoc.docstring.converter import Conversion, ConversionSuccess, Converter
from sourcetodoc.docstring.extractor import Extractor, Range
from sourcetodoc.docstring.parser import Parser


def replace_substring(text: str, replacement: str, between: Range) -> str:
    return text[:between.start] + replacement + text[between.end:]


def replace_substrings(code: str, conversions: Iterable[Conversion]) -> str:
    result: str = code
    for conversion in conversions:
        if conversion is ConversionSuccess:
            result = replace_substring(result, conversion.new_docstring, conversion.comment.range)
    return result


class SimpleParser(Parser):
    def __init__(self, extractor: Extractor, converter: Converter) -> None:
        self.extractor = extractor
        self.converter = converter

    @override
    def convert_string(self, code: str) -> str:
        comments = self.extractor.extract_comments(code)
        conversions = self.converter.calc_conversions(comments)
        return replace_substrings(code, conversions)
