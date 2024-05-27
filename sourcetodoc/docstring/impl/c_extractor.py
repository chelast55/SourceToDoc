import re
from enum import Enum, auto
from typing import Iterator, Optional, override

from ..extractor import BlockComment, Comment, Extractor, Range

IDENTIFIER_REGEX: str = r"(_|[a-zA-Z])[a-zA-Z0-9_]+"

# Matches function declarations or definitions e.g. "void main(void);" or "void main(void) { ... }"
FUNCTION_SIGNATURE_REGEX: str = r"\b(?:\w+\s+){1,2}\w+\s*\([^)]*\)"

# Matches block comments with equal indentations
BLOCK_COMMENT_REGEX: str = (r"^(?P<indentation>(?:[ ]{2}|\t)*)"             # Match the initial indentation
                                r"(?P<comment>(?://.*\n\1)*//.*               |" # Match "// ..." , or
                                r"            /\*(?:(?:.*\n\1[ ]\*)*?|.*?\*)/ )" # match "/* ... */"
                                r"\n\1"
                                r"(" # Match function declaration or definition
                                fr"(?P<function>{FUNCTION_SIGNATURE_REGEX})" r"\s*(\{[^}]*\}|;)"
                                r"|" # match struct
                                fr"(?P<struct>struct\s+{IDENTIFIER_REGEX})" r"\s*?\{"
                                r"|" # match enum
                                fr"(?P<enum>enum\s+{IDENTIFIER_REGEX})" r"\s*?\{"
                                r"|" # match member variable
                                fr"(?P<variable>{IDENTIFIER_REGEX}\s+{IDENTIFIER_REGEX})" r"\s*?;"
                                r")")


class CType(Enum):
    FUNCTION = auto()
    STRUCT = auto()
    ENUM = auto()
    VARIABLE = auto()


class CExtractor(Extractor[CType]):
    """
    Extracts comments from C source code.

    Extracts comments of the form:
    ```
    /*
     *
     */
    symbol
    ```

    where `symbol` has one of the following forms:
    - `function declaration {...} | ;`
    - `identifier identifier;` e.g. a member in a struct
    - `struct identifier {`
    - `enum identifier {`

    where `identifier` matches `(_|[a-zA-Z])[a-zA-Z0-9_]+`.
    """

    def __init__(self) -> None:
        self.comment_pattern = re.compile(BLOCK_COMMENT_REGEX, re.VERBOSE | re.MULTILINE)

    @override
    def extract_comments(self, code: str) -> Iterator[Comment[CType]]:
        last_range: Optional[Range] = None # Keep track of range of previous match
        for matched in self.comment_pattern.finditer(code):
            initial_comment_indentation = matched.group("indentation")
            comment_text = matched.group("comment")
            comment_range = Range(matched.start("comment"), matched.end("comment"))
            symbol_text, symbol_type = CExtractor._get_matched_symbol_group(matched)
            
            if (last_range is None or comment_range.start > last_range.end): # Assure that matches will not overlap (e.g. otherwise "/* /**/" can match "/* /**/" and "/**/")
                yield BlockComment(comment_text, comment_range, symbol_text, symbol_type, initial_comment_indentation)
            last_range = comment_range

    @staticmethod
    def _get_matched_symbol_group(matched: re.Match[str]) -> tuple[str, CType]:
        groupdict = matched.groupdict()
        if "function" in groupdict and groupdict["function"] is not None:
            symbol_text = groupdict["function"]
            symbol_type = CType.FUNCTION
        elif "struct" in groupdict and groupdict["struct"] is not None:
            symbol_text = groupdict["struct"]
            symbol_type = CType.STRUCT
        elif "enum" in groupdict and groupdict["enum"] is not None:
            symbol_text = groupdict["enum"]
            symbol_type = CType.ENUM
        else:
            raise RuntimeError
        return symbol_text, symbol_type
