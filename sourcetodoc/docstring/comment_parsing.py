from enum import Enum, auto
from typing import Iterable, Iterator, Sequence, SupportsIndex

from .comment_style import (BLOCK_INLINE_STYLES, BLOCK_STYLES, LINE_STYLES,
                            CommentStyle)
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


def find_comments(code: str) -> Iterator[tuple[Range, CommentStyle]]:
    """
    Returns the range and style of C comments in `code` in ascending order.

    Parameters
    ----------
    code: str
        The code.

    Yields
    ------
    Iterator[tuple[Range, CommentStyle]]
    """
    state: _State = _State.START
    start: int = 0
    for i in range(len(code)):
        x = code[i]
        match state:
            case _State.START:
                match x:
                    case "/": # /
                        start = i
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
                        yield Range(start, i), _get_style_by_start_delimiter(code, LINE_STYLES, start)
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
                        yield Range(start,i+1), _get_style_by_start_delimiter(code, BLOCK_INLINE_STYLES, start)
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
                        yield Range(start,i+1), _get_style_by_start_delimiter(code, BLOCK_STYLES, start)
                        state = _State.START
                    case str(): # /*...\n...*...
                        pass

    # Handle last line or block comment that has not ended by \n or */ respectively
    match state:
        case _State.LINE:
            yield Range(start, len(code)), _get_style_by_start_delimiter(code, LINE_STYLES, start)
        case _State.BLOCK_INLINE | _State.BLOCK_INLINE_ASTERISK:
            yield Range(start, len(code)), _get_style_by_start_delimiter(code, BLOCK_INLINE_STYLES, start)
        case _State.BLOCK | _State.BLOCK_ASTERISK:
            yield Range(start, len(code)), _get_style_by_start_delimiter(code, BLOCK_STYLES, start)
        case _:
            pass


def find_comments_combined(code: str) -> Iterator[tuple[Sequence[Range], CommentStyle]]:
    """
    Returns the range and style of C comments in `code` in ascending order.

    Comments are combined if:

    - between them are only whitespaces and at most 2 newline characters (\n) and
    - the comments are either both line style or block inline style
    - Then the least specific style is chosen

    Parameters
    ----------
    code: str
        The code.

    Yields
    ------
    Iterator[tuple[Sequence[Range], CommentStyle]]
    """
    ranges: list[Range] = []
    styles: set[CommentStyle] = set()
    last_style_type: Sequence[CommentStyle] | None = None
    for range, style in find_comments(code):
        if last_style_type is None: # Init: There is no previous comment to combine
            ranges.append(range)
            styles.add(style)
            last_style_type = _get_style_type(style)
        # Current comment must not have a block style and previous and current comment both must be either line or block inline style
        elif style in BLOCK_STYLES or not style in last_style_type:
            yield ranges, _get_least_specific_style(styles, last_style_type)
            ranges = [range]
            styles = {style}
            last_style_type = _get_style_type(style)
        else:
            # Between previous and current comment are only whitespaces and at most 2 newline characters
            if ranges and (not (between := code[ranges[-1].end:range.start]) or not between.isspace() or between.count("\n") > 1):
                yield ranges, _get_least_specific_style(styles, last_style_type)
                ranges = [range]
                styles = {style}
                last_style_type = _get_style_type(style)
            else:
                ranges.append(range)
                styles.add(style)
    
    if last_style_type is not None:
        yield ranges, _get_least_specific_style(styles, last_style_type)


def _get_style_type(style: CommentStyle) -> Sequence[CommentStyle]:
    for candidate in (LINE_STYLES, BLOCK_STYLES, BLOCK_INLINE_STYLES):
        if style in candidate:
            return candidate
    raise RuntimeError


def _get_least_specific_style(styles: set[CommentStyle], most_specific_first: Sequence[CommentStyle]) -> CommentStyle:
    for e in reversed(most_specific_first):
        for style in styles:
            if style is e:
                return style
    raise ValueError
