import re
from typing import Iterator, override

from sourcetodoc.docstring.common import Comment
from sourcetodoc.docstring.common import Range
from sourcetodoc.docstring.docconv import Extractor


# Matches single-line comments, e.g. "// ..."
SINGLE_COMMENT_PATTERN: str = r"//.*"

# Matches multi-line comments, e.g. "/* ... */"
MULTI_COMMENT_PATTERN: str = r"/\*(?:.|\n)*?\*/"

IDENTIFIER_PATTERN: str = r"(_|[a-zA-Z])[a-zA-Z0-9_]+"

# Matches function declarations or definitions e.g. "void main(void);" or "void main(void) { ... }"
FUNCTION_SIGNATURE_PATTERN: str = r"\b(?:\w+\s+){1,2}\w+\s*\([^)]*\)"

# Matches multi-line on function declarations or definitions
FUNCTION_COMMENT_PATTERN: str = (fr"(?P<single_comment>{SINGLE_COMMENT_PATTERN}) |"
                                fr"((?P<multi_comment>{MULTI_COMMENT_PATTERN}))"
                                fr"(?P<spacing>\s*)(?P<function_signature>{FUNCTION_SIGNATURE_PATTERN})\s*"
                                r"(?:\{[^}]*\}|;)")


class CExtractor(Extractor):

    @override
    def extract_comments(self, code: str) -> Iterator[Comment]:
        function_comment_matcher = re.compile(FUNCTION_COMMENT_PATTERN, re.VERBOSE)
        for matched in function_comment_matcher.finditer(code):
            
            function_signature: str = matched.group("function_signature")

            comment_type = self._choose(matched)

            comment: str = matched.group(comment_type)
            start: int = matched.start(comment_type)
            end: int = matched.end(comment_type)

            yield Comment(comment, Range(start, end), function_signature, "function")

    def _choose(self, matched: re.Match[str]) -> str:
        comment_type: str
        if matched.group("single_comment") is not None:
            comment_type = "single_comment"
        elif matched.group("multi_comment") is not None:
            comment_type = "multi_comment"
        else:
            raise RuntimeError
        return comment_type
