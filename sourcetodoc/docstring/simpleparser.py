from itertools import chain
from typing import Iterable, Iterator, Optional, override

from .converter import ConversionResult, ConversionPresent, ConversionUnsupported, Converter
from .extractor import Comment, BlockComment, Extractor
from .parser import Parser, Replace


def replace_old_comments[T](code: str, conversions: Iterable[ConversionPresent[T]]) -> str:
    """
    Replaces old comments with new comments.
    """
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
    """
    Places new comments from conversions under old comments.
    """
    result: str = ""
    start = 0
    end = len(code)

    for e in conversions:
        match e.comment:
            case BlockComment() as c:
                end = c.comment_range.end
                result += code[start:end] + "\n" + c.initial_comment_indentation + e.new_comment
                start = c.comment_range.end
            case _:
                raise NotImplementedError

    result += code[start:]
    return result


class SimpleParser[T](Parser):
    """
    Extracts comments with an `Extractor` object and converts them with `Converter` objects.

    When `convert_string` is called:
    1. This parser uses an extractor that outputs `Comment` objects.
    2. The first converter outputs a `ConversionResult` object from every `Comment` object.
    3. If a `ConversionResult` object is a `ConversionUnsupported` object,
      it will be converted to a `Comment` object for the second converter.
    4. The second converter outputs a `ConversionResult` object from every `Comment` object.
    5. Repeat 3., but for the third converter, and so on.

    - The comments in the code will be converted for every `ConversionPresent` object.
    - Use last_conversions to get all the `ConversionResult` objects from the last `convert_string` call.

    Attributes
    ----------
    extractor: Extractor[T]
    converters: tuple[Converter[T]]
    last_conversions: Optional[Iterable[ConversionResult[T]]] = None
    """
    def __init__(self, extractor: Extractor[T], *converters: Converter[T]) -> None:
        self.extractor = extractor
        self.converters = converters
        self.last_conversions: Optional[Iterable[ConversionResult[T]]] = None

    @override
    def convert_string(self, code: str, replace: Replace) -> str:
        comments = self.extractor.extract_comments(code)

        conversions = self._empty_iter()
        for converter in self.converters:
            new_conversions = converter.calc_conversions(comments)
            conversions = chain(conversions, new_conversions)
            comments, conversions = self._convert_unsupported_to_comments(conversions)

        self.last_conversions = conversions
        conversions = self._filter_conversion_present(conversions)
        match replace:
            case Replace.REPLACE_OLD_COMMENTS:
                return replace_old_comments(code, conversions)
            case Replace.APPEND_TO_OLD_COMMENTS:
                return append_to_old_comments(code, conversions)
    
    def _filter_conversion_present(self, conversions: Iterable[ConversionResult[T]]) -> Iterator[ConversionPresent[T]]:
        return (e for e in conversions if isinstance(e, ConversionPresent))

    def _convert_unsupported_to_comments(self, conversions: Iterable[ConversionResult[T]]) -> tuple[Iterator[Comment[T]], Iterator[ConversionResult[T]]]:
        return ((e.comment for e in conversions if isinstance(e, ConversionUnsupported)),
                (e for e in conversions if not isinstance(e, ConversionUnsupported)))

    def _empty_iter(self) -> Iterable[ConversionResult[T]]:
        yield from ()
