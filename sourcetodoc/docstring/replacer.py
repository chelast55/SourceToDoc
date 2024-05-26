from typing import Iterable

from .conversion import ConversionPresent
from .extractor import BlockComment
from .converter import Replace


class Replacer:
    """
    Adds new comments to code.
    """
    def apply_conversions[T](self, code: str, conversions: Iterable[ConversionPresent[T]], replace: Replace) -> str:
        """
        Adds now comments to code given by conversions.

        Returns
        -------
        str
            Code with new comments.
        """
        match replace:
            case Replace.REPLACE_OLD_COMMENTS:
                return self._replace_old_comments(code, conversions)
            case Replace.APPEND_TO_OLD_COMMENTS:
                return self._append_to_old_comments(code, conversions)

    def _replace_old_comments[T](self, code: str, conversions: Iterable[ConversionPresent[T]]) -> str:
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

    def _append_to_old_comments[T](self, code: str, conversions: Iterable[ConversionPresent[T]]) -> str:
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
                    result += code[start:end] + "\n" + c.indentation + e.new_comment
                    start = c.comment_range.end
                case _:
                    raise NotImplementedError

        result += code[start:]
        return result
