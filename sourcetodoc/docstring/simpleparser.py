from itertools import chain
from typing import Iterable, Iterator, Optional, override

from .converter import ConversionResult, ConversionUnsupported, Converter
from .extractor import Comment, Extractor
from .parser import Parser, Replace
from .replacer import Replacer


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
    def __init__(self, extractor: Extractor[T], *converters: Converter[T], replacer: Optional[Replacer] = None) -> None:
        self.extractor = extractor
        self.converters = converters
        if replacer is None:
            replacer = Replacer()
        self.replacer = replacer

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

        match replace:
            case Replace.REPLACE_OLD_COMMENTS:
                return self.replacer.replace_old_comments(code, conversions)
            case Replace.APPEND_TO_OLD_COMMENTS:
                return self.replacer.append_to_old_comments(code, conversions)

    def _convert_unsupported_to_comments(self, conversions: Iterable[ConversionResult[T]]) -> tuple[Iterator[Comment[T]], Iterator[ConversionResult[T]]]:
        return ((e.comment for e in conversions if isinstance(e, ConversionUnsupported)),
                (e for e in conversions if not isinstance(e, ConversionUnsupported)))

    def _empty_iter(self) -> Iterable[ConversionResult[T]]:
        yield from ()
