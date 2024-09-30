from textwrap import dedent
from typing import Iterator

from .comment_style import (BLOCK_INLINE_STYLES, BLOCK_STYLES, LINE_STYLES,
                            BlockComment, CommentStyle)


def extract_content(comment: str, style: CommentStyle) -> str:
    if style in LINE_STYLES:
        content = _extract_content_from_line_comment(comment, style.value.start_delimiter)
    elif style in BLOCK_INLINE_STYLES:
        if not isinstance(style.value, BlockComment):
            raise RuntimeError
        content = _extract_content_from_block_inline_comment(comment, style.value.start_delimiter, style.value.end_delimiter) # type: ignore
    elif style in BLOCK_STYLES:
        if not isinstance(style.value, BlockComment):
            raise RuntimeError
        content = _extract_content_from_block_comment(comment, style.value.start_delimiter, style.value.end_delimiter, "*")
    else:
        raise RuntimeError(f"{style = } is not handled")
    return content


def _extract_content_from_line_comment(text_stripped: str, prefix: str) -> str:
    text = "".join(_remove_and_check_prefix_in_every_line(text_stripped, prefix))
    return dedent(text)


def _remove_and_check_prefix_in_every_line(text_stripped: str, prefix: str) -> Iterator[str]:
    for line in text_stripped.splitlines(keepends=True):
        line_left_stripped = line.lstrip()
        if not line_left_stripped.startswith(prefix):
            raise ValueError(f"Not all lines of {text_stripped} start with {prefix}")
        yield line_left_stripped.removeprefix(prefix)


def _extract_content_from_block_inline_comment(text: str, start_delimiter: str, end_delimiter: str) -> str:
    lines = text.splitlines()
    for i in range(len(lines)):
        lines[i] = lines[i].strip().removeprefix(start_delimiter).removesuffix(end_delimiter).rstrip()
    content = dedent("\n".join(lines))
    return content

def _extract_content_from_block_comment(
    text_stripped: str,
    start_delimiter: str,
    end_delimiter: str,
    deco_prefix: str = ""
) -> str:
    lines = text_stripped.splitlines(keepends=True)

    start_index = 0
    end_index = len(lines)

    # Exclude start_delimiter, e.g. "/*..." or "/*\n..." to "..."
    lines[0] = lines[0].removeprefix(start_delimiter)
    if lines[0].isspace():
        start_index = 1

    # Exclude end_delimiter, e.g. "...*/" or "...\n␣␣␣*/" to "..."
    lines[-1] = lines[-1].removesuffix(end_delimiter)
    if lines[-1].isspace() and end_index >= 2:
        end_index = end_index - 1
        lines[-2] = lines[-2].removesuffix("\n")

    # For every line except first line: From the left remove whitespaces,
    # then remove the prefix (e.g. "*")
    for i in range(1, end_index):
        lines[i] = lines[i].lstrip().removeprefix(deco_prefix)

    content = "".join(lines[start_index:end_index])
    return dedent(content)
