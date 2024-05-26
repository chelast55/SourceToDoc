from typing import Any

from ..extractor import BlockComment
from ..conversion import Conversion, Comment, ConversionEmpty, ConversionPresent, ConversionResult, ConversionUnsupported


class CCommentToDocstringConversion(Conversion[Any]):
    """
    Converts `/*...*/` and `//<whitespace>...` block comments to `/**...*/`.
    """
    def calc_conversion(self, comment: Comment[Any]) -> ConversionResult[Any]:
        match comment:
            case BlockComment() as bc if bc.comment_text.startswith("/**") and bc.comment_text.endswith("*/"):
                return ConversionEmpty(bc, "Comment already starts with /**")
            case BlockComment() as bc if bc.comment_text.startswith("/*") and bc.comment_text.endswith("*/"):
                return self._handle_slash_asterisk(bc)
            case BlockComment() as bc if self._every_line_starts_with(bc.comment_text, "// "):
                return self._handle_double_slash_space(bc)
            case _:
                return ConversionUnsupported(comment)

    def _handle_slash_asterisk(self, comment: BlockComment[Any]) -> ConversionResult[Any]:
        new_comment = comment.comment_text.replace("/*", "/**", 1)
        return ConversionPresent(comment, new_comment)

    def _handle_double_slash_space(self, comment: BlockComment[Any]) -> ConversionResult[Any]:
        result_list: list[str] = []
        lines = comment.comment_unindented().splitlines()
        
        first_line = lines[0].replace("//", "/**", 1)
        if len(lines) == 1:
            first_line = first_line + "*/"

        result_list.append(first_line)

        if len(lines) >= 2:
            for i in range(1, len(lines) - 1):
                line = lines[i].replace("//", " *")
                result_list.append(line)

            last_line = lines[len(lines) - 1] + "*/"
            result_list.append(last_line)

        new_comment = "\n".join(result_list)
        return ConversionPresent(comment, new_comment)

    def _every_line_starts_with(self, text: str, prefix: str) -> bool:
        lines = text.splitlines()
        for line in lines:
            if not line.startswith(prefix):
                return False
        return True
