from typing import override

from .simpleconverter import SimpleConverter

from .conversion import ConversionEmpty, ConversionError, ConversionPresent, ConversionResult, ConversionUnsupported, Conversion
from .extractor import Extractor
from .converter import Replace
from .replacer import Replacer


class PrintConverter[T](SimpleConverter[T]):
    """
    Same as SimpleConverter, but also prints to stdout.
    """
    def __init__(self, extractor: Extractor[T], conversion: Conversion[T], replacer: Replacer | None = None) -> None:
        super().__init__(extractor, conversion, replacer)

    @override
    def convert_string(self, code: str, replace: Replace) -> str:
        # Extract comments
        comments = list(self.extractor.extract_comments(code))
        comments_count = len(comments)
        print(f"{comments_count} comments were found")

        # Calculate new comments
        conversions: list[ConversionResult[T]] = []
        for i, comment in enumerate(comments):
            print(f"Processing comment {i}")
            conversion = self.conversion.calc_conversion(comment)
            conversions.append(conversion)
            self.if_error_print_message(conversion)

        # Apply new comments
        conversions_present = [e for e in conversions if isinstance(e, ConversionPresent)]
        print(f"Converting {len(conversions_present)} of {comments_count} comments ...")
        result = self.replacer.apply_conversions(code, conversions_present, replace)

        conversions_empty = [e for e in conversions if isinstance(e, ConversionEmpty)]
        print(f"{len(conversions_empty)} of {comments_count} comments don't have to be converted")

        conversions_unsupported = [e for e in conversions if isinstance(e, ConversionUnsupported)]
        conversions_error = [e for e in conversions if isinstance(e, ConversionError)]
        print(f"{len(conversions_unsupported) + len(conversions_error)} of {comments_count} comments can't be converted:")
        print(f"{len(conversions_unsupported)} comments are not supported")
        print(f"{len(conversions_error)} comments raised an error")
        return result

    def if_error_print_message(self, conversion: ConversionResult[T]) -> None:
        if isinstance(conversion, ConversionError):
            print(f"An error occured when trying to convert: {repr(conversion.comment)}\nError message: {conversion.message}")
