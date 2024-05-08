from typing import Iterable, Iterator, override

from .converter import ConversionResult, ConversionPresent, Converter
from .extractor import Extractor
from .parser import Parser, Replace


def replace_old_comments[T](code: str, conversions: Iterable[ConversionPresent[T]]) -> str:
    result: str = ""
    start = 0
    end = len(code)

    for e in conversions:
        end = e.comment.comment_range.start
        result += code[start:end] + e.new_comment
        start = e.comment.comment_range.end

    result += code[start:]
    return result


def append_to_old_comments[T](code: str, conversions: Iterable[ConversionPresent[T]]) -> str:
    result: str = ""
    start = 0
    end = len(code)

    for e in conversions:
        end = e.comment.comment_range.end
        result += code[start:end] + "\n" + e.new_comment
        start = e.comment.comment_range.end

    result += code[start:]
    return result


class SimpleParser[T](Parser):
    def __init__(self, extractor: Extractor[T], converter: Converter[T]) -> None:
        self.extractor = extractor
        self.converter = converter

    @override
    def convert_string(self, code: str, replace: Replace) -> str:
        comments = self.extractor.extract_comments(code)
        conversions = self.converter.calc_conversions(comments)
        conversions = self._filter_conversion_present(conversions)
        match replace:
            case Replace.REPLACE_OLD_COMMENTS:
                return replace_old_comments(code, conversions)
            case Replace.APPEND_TO_OLD_COMMENTS:
                return append_to_old_comments(code, conversions)
    
    def _filter_conversion_present(self, conversions: Iterable[ConversionResult[T]]) -> Iterator[ConversionPresent[T]]:
        return (e for e in conversions if isinstance(e, ConversionPresent))
