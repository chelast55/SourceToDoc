from typing import Iterable

from .converter import ConversionPresent, ConversionResult
from .extractor import BlockComment


class Replacer:
    """
    Adds new comments to code.
    """

    def replace_old_comments[T](self, code: str, conversions: Iterable[ConversionResult[T]]) -> str:
        """
        Replaces old comments with new comments.
        """
        result: str = ""
        start = 0
        end = len(code)

        for e in conversions:
            if not isinstance(e, ConversionPresent):
                continue
            end = e.comment.comment_range.start
            result += code[start:end] + e.new_comment
            start = e.comment.comment_range.end

        result += code[start:]
        return result


    def append_to_old_comments[T](self, code: str, conversions: Iterable[ConversionResult[T]]) -> str:
        """
        Places new comments from conversions under old comments.
        """
        result: str = ""
        start = 0
        end = len(code)

        for e in conversions:
            if not isinstance(e, ConversionPresent):
                continue

            match e.comment:
                case BlockComment() as c:
                    end = c.comment_range.end
                    result += code[start:end] + "\n" + c.initial_comment_indentation + e.new_comment
                    start = c.comment_range.end
                case _:
                    raise NotImplementedError

        result += code[start:]
        return result
