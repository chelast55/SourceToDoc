import re
from typing import Iterator, Optional, override

from ..extractor import Extractor, Comment, Range


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

    def __init__(self) -> None:
        self.function_comment_matcher = re.compile(FUNCTION_COMMENT_PATTERN, re.VERBOSE)

    @override
    def extract_comments(self, code: str) -> Iterator[Comment]:
        last_range: Optional[Range] = None # Keep track of the position of previous match
        for matched in self.function_comment_matcher.finditer(code):
            function_signature: str = matched.group("function_signature")

            comment_type = CExtractor._matched_group(matched) # Retrieve "//..." or "/*...*/" comments

            comment: str = matched.group(comment_type)
            range: Range = Range(matched.start(comment_type), matched.end(comment_type))

            if (last_range is None or range.start > last_range.end): # Assure that matches will not overlap (e.g. "/* /**/" will match "/* /**/" and "/**/")
                yield Comment(comment, range, function_signature, "function")
            last_range = range

    @staticmethod
    def _matched_group(matched: re.Match[str]) -> str:
        comment_type: str
        if matched.group("single_comment") is not None:
            comment_type = "single_comment"
        elif matched.group("multi_comment") is not None:
            comment_type = "multi_comment"
        else:
            raise RuntimeError # Should never happen
        return comment_type
