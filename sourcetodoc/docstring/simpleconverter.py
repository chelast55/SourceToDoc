from typing import Optional, override

from .conversion import ConversionPresent, Conversion
from .extractor import Extractor
from .converter import Converter, Replace
from .replacer import Replacer


class SimpleConverter[T](Converter):
    """
    Extracts comments with an `Extractor` object and converts them with a `Conversion` object.

    When `convert_string` is called:
    1. The extractor extracts comments and outputs `Comment` objects.
    2. The conversion object outputs a `ConversionResult` object for every `Comment` object.
    3. The replacer (re)places the new comments and returns a string from every `ConversionResult` object
       that is a `ConversionPresent` object.

    Attributes
    ----------
    extractor: Extractor[T]
    converters: Conversion[T]
    replacer: Replacer
    """
    def __init__(self, extractor: Extractor[T], conversion: Conversion[T], replacer: Optional[Replacer] = None) -> None:
        self.extractor = extractor
        self.conversion = conversion
        if replacer is None:
            replacer = Replacer()
        self.replacer = replacer

    @override
    def convert_string(self, code: str, replace: Replace) -> str:
        comments = self.extractor.extract_comments(code)
        conversions = self.conversion.calc_conversions(comments)
        conversions_present = (e for e in conversions if isinstance(e, ConversionPresent)) # Filter by ConversionPresent
        result = self.replacer.apply_conversions(code, conversions_present, replace)
        return result
