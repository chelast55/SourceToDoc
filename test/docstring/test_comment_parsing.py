from typing import Sequence

import pytest

from sourcetodoc.docstring.comment_parsing import (find_comments,
                                                   find_comments_combined)
from sourcetodoc.docstring.comment_style import CommentStyle
from sourcetodoc.docstring.range import Range

_c_line = """\
// a
// b"""

_c_block = """\
/* a
 * b
 */"""

_c_block_inline = """\
/* a */
/* b */"""

_javadoc_block = """\
/** a
 * b
 */"""

_javadoc_block_inline = """\
/** a */
/** b */"""

_javadoc_block_member_inline = """\
/**< a */
/**< b */"""

_qt_line = """\
//! a
//! b"""

_qt_line_member = """\
//!< a
//!< b"""

_qt_block = """\
/*! a
 * b
 */"""

_qt_block_inline = """\
/*! a */
/*! b */"""

_qt_block_member_inline = """\
/*!< a */
/*!< b */"""

_triple_slash_line = """\
/// a
/// b"""

_triple_slash_line_member = """\
///< a
///< b"""

_triple_slash_line_and_c_line = """\
/// a
// b"""

_qt_block_inline_and_c_block_inline = """\
/*! a */
test
/* b */"""

_javadoc_block_and_c_block_inline = """\
/**
 * a
 */
/* b */
"""


@pytest.mark.parametrize("expected,text", [
    ([CommentStyle.C_LINE]*2, _c_line),
    ([CommentStyle.C_BLOCK], _c_block),
    ([CommentStyle.C_BLOCK_INLINE], _c_block_inline),
    ([CommentStyle.JAVADOC_BLOCK], _javadoc_block),
    ([CommentStyle.JAVADOC_BLOCK_INLINE], _javadoc_block_inline),
    ([CommentStyle.JAVADOC_BLOCK_MEMBER_INLINE], _javadoc_block_member_inline),
    ([CommentStyle.QT_LINE]*2, _qt_line),
    ([CommentStyle.QT_LINE_MEMBER]*2, _qt_line_member),
    ([CommentStyle.QT_BLOCK], _qt_block),
    ([CommentStyle.QT_BLOCK_INLINE], _qt_block_inline),
    ([CommentStyle.QT_BLOCK_MEMBER_INLINE], _qt_block_member_inline),
    ([CommentStyle.TRIPLE_SLASH_LINE]*2, _triple_slash_line),
    ([CommentStyle.TRIPLE_SLASH_LINE_MEMBER]*2, _triple_slash_line_member),
    ([CommentStyle.TRIPLE_SLASH_LINE, CommentStyle.C_LINE], _triple_slash_line_and_c_line),
    ([CommentStyle.QT_BLOCK_INLINE, CommentStyle.C_BLOCK_INLINE], _qt_block_inline_and_c_block_inline),
    ([CommentStyle.JAVADOC_BLOCK, CommentStyle.C_BLOCK_INLINE], _javadoc_block_and_c_block_inline),
])
def test_find_comments_assert_styles(expected: Sequence[CommentStyle], text: str) -> None:
    for expected_style, (_, actual_style) in zip(expected, find_comments(text)):
        assert expected_style is actual_style


@pytest.mark.parametrize("expected,text", [
    ([
        (Range(0, 4), CommentStyle.C_LINE),
        (Range(5, 9), CommentStyle.C_LINE)
    ], _c_line),
    ([
        (Range(0, 13), CommentStyle.C_BLOCK)
    ], _c_block),
    ([
        (Range(0, 7), CommentStyle.C_BLOCK_INLINE),
        (Range(8, 15), CommentStyle.C_BLOCK_INLINE)
    ], _c_block_inline),
])
def test_find_comments(expected: Sequence[tuple[Range,CommentStyle]], text: str) -> None:
    for (expected_range, expected_style), (actual_range, actual_style) in zip(expected, find_comments(text)):
        assert expected_range == actual_range
        assert expected_style is actual_style


_multi_line = """\
// a
///b

// c
/*
 * a
 */
/* a */
/* b */

/* c */
"""


def test_find_comments_composed() -> None:
    line1, line2, block1, inline1, inline2 = find_comments_combined(_multi_line)
    assert ([Range(0, 4), Range(5, 9)], CommentStyle.C_LINE) == line1
    assert ([Range(11, 15)], CommentStyle.C_LINE) == line2
    assert ([Range(16, 27)], CommentStyle.C_BLOCK) == block1
    assert ([Range(28, 35), Range(36, 43)], CommentStyle.C_BLOCK_INLINE) == inline1
    assert ([Range(45, 52)], CommentStyle.C_BLOCK_INLINE) == inline2
