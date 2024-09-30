from enum import Enum, auto
from typing import Iterable, Iterator, Sequence, SupportsIndex

from .comment_style import (BLOCK_INLINE_STYLES, BLOCK_STYLES, LINE_STYLES,
                            BlockComment, CommentStyle, LineComment)
from .range import Range


def _get_style_by_start_delimiter(comment: str, candidates: Iterable[CommentStyle], start: SupportsIndex) -> CommentStyle:
    for style in candidates:
        if comment.startswith(style.value.start_delimiter, start):
            return style
    raise RuntimeError


class _State(Enum):
    START = auto()
    SLASH = auto()
    LINE = auto()
    BLOCK_INLINE = auto()
    BLOCK_INLINE_ASTERISK = auto()
    BLOCK = auto()
    BLOCK_ASTERISK = auto()


def find_comments(
        code: str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None
    ) -> Iterator[tuple[Range, CommentStyle]]:
    """
    Returns the range and style of single C comment pieces in `code` in ascending order.

    Example:
    ```
    // a
    // b
    ````
    are two comment pieces.

    Parameters
    ----------
    code: str
        The code.
    start: SupportsIndex | None, optional
        The start index to search, by default `0`.
    end: SupportsIndex | None, optional
        The end index to search, by default `len(code`)

    Yields
    ------
    Iterator[tuple[Range, CommentStyle]]
    """
    if start is None:
        start = 0
    if end is None:
        end = len(code)

    state: _State = _State.START
    comment_start: int = 0
    for i in range(start, end):
        x = code[i]
        match state:
            case _State.START:
                match x:
                    case "/": # /
                        comment_start = i
                        state = _State.SLASH
                    case str(): # ...
                        pass
            case _State.SLASH: # /
                match x:
                    case "/": # //
                        state = _State.LINE
                    case "*": # /*
                        state = _State.BLOCK_INLINE
                    case str():
                        pass
            case _State.LINE: # //...
                match x:
                    case "\n": # //...\n
                        state = _State.START
                        yield Range(comment_start, i), _get_style_by_start_delimiter(code, LINE_STYLES, comment_start)
                    case str(): # //...
                        pass
            case _State.BLOCK_INLINE: # /*...
                match x:
                    case "*": # /*...*
                        state = _State.BLOCK_INLINE_ASTERISK
                    case "\n":
                        state = _State.BLOCK
                    case str(): # /*...
                        pass
            case _State.BLOCK_INLINE_ASTERISK: # /*...*
                match x:
                    case "/": # /*...*/
                        yield Range(comment_start,i+1), _get_style_by_start_delimiter(code, BLOCK_INLINE_STYLES, comment_start)
                        state = _State.START
                    case "\n": # /*...*\n
                        state = _State.BLOCK
                    case str():  # /*...*...
                        state = _State.BLOCK_INLINE
            case _State.BLOCK: # /*...\n...
                match x:
                    case "*": # /*...\n...*
                        state = _State.BLOCK_ASTERISK
                    case str(): # /*...\n...
                        pass
            case _State.BLOCK_ASTERISK:
                match x:
                    case "/": # /*...\n...*/
                        yield Range(comment_start,i+1), _get_style_by_start_delimiter(code, BLOCK_STYLES, comment_start)
                        state = _State.START
                    case str(): # /*...\n...*...
                        pass

    # Handle last line or block comment that has not ended by \n or */ respectively
    match state:
        case _State.LINE:
            yield Range(comment_start, end.__index__()), _get_style_by_start_delimiter(code, LINE_STYLES, comment_start)
        case _State.BLOCK_INLINE | _State.BLOCK_INLINE_ASTERISK:
            yield Range(comment_start, end.__index__()), _get_style_by_start_delimiter(code, BLOCK_INLINE_STYLES, comment_start)
        case _State.BLOCK | _State.BLOCK_ASTERISK:
            yield Range(comment_start, end.__index__()), _get_style_by_start_delimiter(code, BLOCK_STYLES, comment_start)
        case _:
            pass


def find_comments_connected_with_ranges(
        code: str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None
    ) -> Iterator[tuple[Sequence[Range], CommentStyle]]:
    """
    Returns the range and style of C comments in `code` in ascending order.

    Comments are combined if:

    - between them are only whitespaces and at most 2 newline characters (\n) and
    - the comments are either both line style or block inline style
    - Then the least specific style is chosen

    The ranges determine the ranges of individual comment pieces.

    Parameters
    ----------
    code: str
        The code.
    start: SupportsIndex | None, optional
        The start index to search, by default `0`.
    end: SupportsIndex | None, optional
        The end index to search, by default `len(code`).

    Yields
    ------
    Iterator[tuple[Sequence[Range], CommentStyle]]
    """
    ranges: list[Range] = []
    last_style: CommentStyle | None = None
    for range, style in find_comments(code, start, end):
        if last_style is None: # Init: There is no previous comment to combine
            ranges.append(range)
            last_style = style
        # Current comment must not have a block style and previous and current comment both must be either line or block inline style
        elif style in BLOCK_STYLES or not _has_same_style_type(style, last_style):
            yield ranges, last_style
            ranges = [range]
            last_style = style
        else:
            # Between previous and current comment are only whitespaces and at most 2 newline characters
            if ranges and (not (between := code[ranges[-1].end:range.start]) or not between.isspace() or between.count("\n") > 1):
                yield ranges, last_style
                ranges = [range]
                last_style = style
            else:
                ranges.append(range)
                last_style = _use_less_specific_style(last_style, style)
    
    if last_style is not None:
        yield ranges, last_style


def _has_same_style_type(current_style: CommentStyle, other_style: CommentStyle) -> bool:
    current_type = current_style.value
    other_type = other_style.value
    if type(current_type) == BlockComment and type(other_type) == BlockComment:
        return current_type.is_inline == other_type.is_inline
    return type(current_type) == type(other_type)


def _use_less_specific_style(current_style: CommentStyle, other_style: CommentStyle) -> CommentStyle:
    if current_style.value.start_delimiter.startswith(other_style.value.start_delimiter):
        return other_style
    elif other_style.value.start_delimiter.startswith(current_style.value.start_delimiter):
        return current_style
    else:
        match current_style.value:
            case LineComment():
                return CommentStyle.C_LINE
            case BlockComment() as b if b.is_inline:
                return CommentStyle.C_BLOCK_INLINE
            case _:
                raise RuntimeError


def find_comments_connected(
        code: str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None
    ) -> Iterator[tuple[Range, CommentStyle]]:
    """
    Returns the range and style of C comments in `code` in ascending order.

    Like `find_comments_combined_with_ranges`, but the ranges are combined into one.

    Parameters
    ----------
    code: str
        The code.
    start: SupportsIndex | None, optional
        The start index to search, by default `0`.
    end: SupportsIndex | None, optional
        The end index to search, by default `len(code`).

    Yields
    ------
    Iterator[tuple[Range, CommentStyle]]
    """
    return ((Range(ranges[0].start, ranges[-1].end), style) for ranges, style in find_comments_connected_with_ranges(code, start, end))
