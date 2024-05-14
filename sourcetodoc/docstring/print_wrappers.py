from typing import Iterable, Iterator, Optional

from .converter import ConversionResult, Converter
from .extractor import Comment, Extractor
from .parser import Parser, Replace
from .replacer import Replacer
from .simpleparser import SimpleParser


class ExtractorPrint[T](Extractor[T]):
    def __init__(self, extractor: Extractor[T]) -> None:
        self.extractor = extractor

    def extract_comments(self, code: str) -> Iterator[Comment[T]]:
        comments = self.extractor.extract_comments(code)
        for comment in comments:
            print(f"Extracted:\n{repr(comment)}")
            yield comment


class ConverterPrint[T](Converter[T]):
    def __init__(self, converter: Converter[T]) -> None:
        self.converter = converter
    
    def calc_docstring(self, comment: Comment[T]) -> ConversionResult[T]:
        print(f"Calculating new comment from:\n{repr(comment)}")
        result = self.converter.calc_docstring(comment)
        print(f"Result:\n{repr(result)}")

        return result


class ParserPrint(Parser):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def convert_string(self, code: str, replace: Replace) -> str:
        print(f"Converting comments in code:\n{code}")
        result = self.parser.convert_string(code, replace)
        if result != code:
             print(f"Comments were converted:\n{result}")
        else:
            print("No comments were converted")
        return result


class ReplacerPrint(Replacer):
    def __init__(self, replacer: Replacer) -> None:
        self.replacer = replacer
    
    def replace_old_comments[T](self, code: str, conversions: Iterable[ConversionResult[T]]) -> str:
        return super().replace_old_comments(code, conversions)
    
    def append_to_old_comments[T](self, code: str, conversions: Iterable[ConversionResult[T]]) -> str:
        return super().append_to_old_comments(code, conversions)

    @staticmethod
    def _print[T](conversions: Iterable[ConversionResult[T]]):
        for e in conversions:
            print(repr(e))


class SimpleParserPrint[T](SimpleParser[T]):
    def __init__(self, extractor: Extractor[T], *converters: Converter[T], replacer: Optional[Replacer] = None) -> None:
        if not isinstance(extractor, ExtractorPrint):
            extractor = ExtractorPrint(extractor)
        converters = tuple(self._if_not_converter_print_map_to_converter_print(converters))
        if not isinstance(replacer, ReplacerPrint):
            if replacer is None:
                replacer = Replacer()
            replacer = ReplacerPrint(replacer)
        super().__init__(extractor, *converters, replacer=replacer)

    def _if_not_converter_print_map_to_converter_print(self, converters: Iterable[Converter[T]]) -> Iterator[ConverterPrint[T]]:
        for converter in converters:
            if not isinstance(converter, ConverterPrint):
                converter = ConverterPrint(converter)
            yield converter
