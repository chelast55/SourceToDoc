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
            case Replace.APPEND_TO_OLD_COMMENTS_INLINE:
                return self._append_to_old_comments_inline(code, conversions)

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
        Places new comments under old comments.
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
                    continue

        result += code[start:]
        return result

    def _append_to_old_comments_inline[T](self, code: str, conversions: Iterable[ConversionPresent[T]]) -> str:
        """
        Places new comments under old comments.
        """
        result: str = ""
        start = 0
        end = len(code)

        for e in conversions:
            match e.comment:
                case BlockComment() as c:
                    old_comment = code[c.comment_range.start:c.comment_range.end]
                    if old_comment.startswith("/*") and old_comment.endswith("*/") and e.new_comment.startswith("/*") and e.new_comment.endswith("*/"):
                        end = c.comment_range.start
                        result += (code[start:end]
                                   + "/**" + old_comment.removesuffix("/").removeprefix("/*").removeprefix("/**") +
                                   "\n" + c.indentation + " * NEW_COMMENT" +
                                   "\n" + c.indentation + " *" +
                                   e.new_comment.removeprefix("/**").removeprefix("/*"))
                        start = c.comment_range.end
                    else:
                        end = c.comment_range.end
                        result += code[start:end] + "\n" + c.indentation + e.new_comment
                        start = c.comment_range.end
                case _:
                    continue

        result += code[start:]
        return result
