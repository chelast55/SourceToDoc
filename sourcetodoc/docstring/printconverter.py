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
        print("Extracting comments ...")
        comments = list(self.extractor.extract_comments(code))
        comments_count = len(comments)
        print(f"{comments_count} comments were found")

        # Calculate new comments
        conversions: list[ConversionResult[T]] = []
        for i, comment in enumerate(comments):
            print(f"Processing {i+1} of {comments_count}")
            conversion = self.conversion.calc_conversion(comment)
            conversions.append(conversion)
            self.print_message(conversion)

        # Apply new comments
        conversions_present = [e for e in conversions if isinstance(e, ConversionPresent)]
        if len(conversions_present) > 0:
            print(f"Converting {len(conversions_present)} comments ...")
            result = self.replacer.apply_conversions(code, conversions_present, replace)
        else:
            result = code

        # Print summary
        print("Summary:")
        print(f"{len(conversions_present)} comments were converted")
        conversions_empty = [e for e in conversions if isinstance(e, ConversionEmpty)]
        print(f"{len(conversions_empty)} comments don't have to be converted")

        conversions_unsupported = [e for e in conversions if isinstance(e, ConversionUnsupported)]
        conversions_error = [e for e in conversions if isinstance(e, ConversionError)]
        print(f"{len(conversions_unsupported) + len(conversions_error)} comments can't be converted: ", end="")
        print(f"{len(conversions_unsupported)} are not supported and ", end="")
        print(f"{len(conversions_error)} raised an error")
        return result


    def print_message(self, conversion: ConversionResult[T]) -> None:
        match conversion:
            case ConversionEmpty(_, message) if message is not None:
                print(f"Skip: {message}")
            case ConversionUnsupported(_, message) if message is not None:
                print(f"Skip: {message}")
            case ConversionEmpty() | ConversionUnsupported():
                print("Skip")
            case ConversionError():
                print(f"Error: {repr(conversion)}")
            case _:
                pass
