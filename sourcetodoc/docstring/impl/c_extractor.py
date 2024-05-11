import re
from enum import Enum, auto
from typing import Iterator, Optional, override

from ..extractor import BlockComment, Comment, Extractor, Range

# Matches single-line comments (also over multiple lines), e.g. "// ..."
SINGLE_COMMENT_PATTERN: str = r"(?://.*\n)*//.*"

# Matches multi-line comments, e.g. "/* ... */"
MULTI_COMMENT_PATTERN: str = r"(/\*(?:.|\n)*?\*/)|(?://.*\n)*//.*"

IDENTIFIER_PATTERN: str = r"(_|[a-zA-Z])[a-zA-Z0-9_]+"

# Matches function declarations or definitions e.g. "void main(void);" or "void main(void) { ... }"
FUNCTION_SIGNATURE_PATTERN: str = r"\b(?:\w+\s+){1,2}\w+\s*\([^)]*\)"

# Matches multi-line on function declarations or definitions
FUNCTION_COMMENT_PATTERN: str = (fr"^(?P<indentation>[ \t]*)"
                                fr"((?P<single_comment>{SINGLE_COMMENT_PATTERN}) |"
                                fr"(?P<multi_comment>{MULTI_COMMENT_PATTERN}))"
                                fr"(?P<spacing>\s*)(?P<function_signature>{FUNCTION_SIGNATURE_PATTERN})\s*"
                                r"(?:\{[^}]*\}|;)")


class CType(Enum):
    FUNCTION_MULTI_COMMENT = auto()


class CExtractor(Extractor[CType]):

    def __init__(self) -> None:
        self.function_comment_matcher = re.compile(FUNCTION_COMMENT_PATTERN, re.VERBOSE)

    @override
    def extract_comments(self, code: str) -> Iterator[Comment[CType]]:
        last_range: Optional[Range] = None # Keep track of range of previous match
        for matched in self.function_comment_matcher.finditer(code):
            # Retrieve "//..." or "/*...*/" comments
            comment_type = CExtractor._matched_group(matched)

            comment_text = matched.group(comment_type)
            comment_range = Range(matched.start(comment_type), matched.end(comment_type))
            function_signature = matched.group("function_signature")
            initial_comment_indentation = matched.group("indentation")
            comment_symbol_spacing = matched.group("spacing")
            
            if (last_range is None or comment_range.start > last_range.end): # Assure that matches will not overlap (e.g. "/* /**/" will match "/* /**/" and "/**/")
                yield BlockComment(comment_text, comment_range, function_signature, CType.FUNCTION_MULTI_COMMENT, initial_comment_indentation, comment_symbol_spacing)
            last_range = comment_range

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
