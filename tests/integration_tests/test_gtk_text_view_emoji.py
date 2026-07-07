# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Tests Orca's presentation of emoji during caret navigation in a native GtkTextView.

The fixture has five lines:
  Start.
  Flags \U0001f1fa\U0001f1f8 and \U0001f1ee\U0001f1f9 here.   (two flags, space-separated)
  Joined \U0001f1fa\U0001f1f8\U0001f1ee\U0001f1f9 flags.       (two flags back-to-back)
  Family \U0001f468‍\U0001f469‍\U0001f467‍\U0001f466 here.  (ZWJ family)
  End.

Line navigation (Down), word navigation (Ctrl+Right), and character navigation
(Right/Left) all produce whole emoji in their announcements. The generic
default.say_character path uses ensure_whole_characters, so each flag pair and
the ZWJ family sequence land at a single caret stop and are announced intact.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_US_FLAG = "\U0001f1fa\U0001f1f8"
_IT_FLAG = "\U0001f1ee\U0001f1f9"
_FAMILY = "\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466"

_FLAGS_LINE = f"Flags {_US_FLAG} and {_IT_FLAG} here."
_JOINED_LINE = f"Joined {_US_FLAG}{_IT_FLAG} flags."
_FAMILY_LINE = f"Family {_FAMILY} here."


@pytest.mark.native_app
def test_down_arrow_announces_whole_emoji_lines(gtk3_text_view_emoji: NativeAppSession) -> None:
    """Down-arrow presents each line with whole emoji intact."""

    session = gtk3_text_view_emoji
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [f"{_FLAGS_LINE}\n"],
        [BrailleLine(1, f"{_FLAGS_LINE} $l", f"{_FLAGS_LINE} $l", "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [f"{_JOINED_LINE}\n"],
        [BrailleLine(1, f"{_JOINED_LINE} $l", f"{_JOINED_LINE} $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [f"{_FAMILY_LINE}\n"],
        [BrailleLine(1, f"{_FAMILY_LINE} $l", f"{_FAMILY_LINE} $l", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["End."],
        [BrailleLine(1, "End. $l", "End. $l", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_word_nav_announces_whole_emoji(gtk3_text_view_emoji: NativeAppSession) -> None:
    """Ctrl+Right word navigation produces whole emoji as part of each word unit."""

    session = gtk3_text_view_emoji
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    _flags_braille = f"{_FLAGS_LINE} $l"
    _joined_braille = f"{_JOINED_LINE} $l"
    _family_braille = f"{_FAMILY_LINE} $l"

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["Flags"],
        [BrailleLine(6, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [f"{_US_FLAG} and"],
        [BrailleLine(13, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [f"{_IT_FLAG} here"],
        [BrailleLine(21, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [".\nJoined"],
        [BrailleLine(7, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [f"{_US_FLAG}{_IT_FLAG} flags"],
        [BrailleLine(18, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [".\nFamily"],
        [BrailleLine(7, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [f"{_FAMILY} here"],
        [BrailleLine(20, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [".\nEnd"],
        [BrailleLine(4, "End. $l", "End. $l", "\x00" * 7)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["."],
        [BrailleLine(5, "End. $l", "End. $l", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_char_nav_right_announces_whole_emoji(gtk3_text_view_emoji: NativeAppSession) -> None:
    """Right-arrow character navigation presents each flag and ZWJ family as a single stop."""

    session = gtk3_text_view_emoji

    _flags_braille = f"{_FLAGS_LINE} $l"
    _joined_braille = f"{_JOINED_LINE} $l"
    _family_braille = f"{_FAMILY_LINE} $l"

    move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["l"],
        [BrailleLine(2, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(3, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["g"],
        [BrailleLine(4, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["s"],
        [BrailleLine(5, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(6, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_US_FLAG],
        [BrailleLine(7, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(9, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(10, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["n"],
        [BrailleLine(11, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["d"],
        [BrailleLine(12, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(13, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_IT_FLAG],
        [BrailleLine(14, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(16, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["h"],
        [BrailleLine(17, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(18, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["r"],
        [BrailleLine(19, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(20, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["."],
        [BrailleLine(21, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["blank"],
        [BrailleLine(22, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["o"],
        [BrailleLine(2, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["i"],
        [BrailleLine(3, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["n"],
        [BrailleLine(4, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(5, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["d"],
        [BrailleLine(6, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(7, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_US_FLAG],
        [BrailleLine(8, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_IT_FLAG],
        [BrailleLine(10, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(12, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["f"],
        [BrailleLine(13, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["l"],
        [BrailleLine(14, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(15, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["g"],
        [BrailleLine(16, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["s"],
        [BrailleLine(17, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["."],
        [BrailleLine(18, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["blank"],
        [BrailleLine(19, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(2, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["m"],
        [BrailleLine(3, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["i"],
        [BrailleLine(4, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["l"],
        [BrailleLine(5, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["y"],
        [BrailleLine(6, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(7, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [_FAMILY],
        [BrailleLine(8, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        [" "],
        [BrailleLine(15, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["h"],
        [BrailleLine(16, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(17, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["r"],
        [BrailleLine(18, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(19, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["."],
        [BrailleLine(20, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["blank"],
        [BrailleLine(21, _family_braille, _family_braille, "\x00" * 23)],
    )


@pytest.mark.native_app
def test_char_nav_left_announces_whole_emoji(gtk3_text_view_emoji: NativeAppSession) -> None:
    """Left-arrow character navigation presents each flag and ZWJ family as a single stop."""

    session = gtk3_text_view_emoji

    _flags_braille = f"{_FLAGS_LINE} $l"
    _joined_braille = f"{_JOINED_LINE} $l"
    _family_braille = f"{_FAMILY_LINE} $l"

    move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["."],
        [BrailleLine(21, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(20, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["r"],
        [BrailleLine(19, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(18, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["h"],
        [BrailleLine(17, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(16, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_IT_FLAG],
        [BrailleLine(14, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(13, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["d"],
        [BrailleLine(12, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["n"],
        [BrailleLine(11, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(10, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(9, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_US_FLAG],
        [BrailleLine(7, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(6, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["s"],
        [BrailleLine(5, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["g"],
        [BrailleLine(4, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(3, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["l"],
        [BrailleLine(2, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["F"],
        [BrailleLine(1, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["."],
        [BrailleLine(18, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["s"],
        [BrailleLine(17, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["g"],
        [BrailleLine(16, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(15, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["l"],
        [BrailleLine(14, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["f"],
        [BrailleLine(13, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(12, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_IT_FLAG],
        [BrailleLine(10, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_US_FLAG],
        [BrailleLine(8, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(7, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["d"],
        [BrailleLine(6, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(5, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["n"],
        [BrailleLine(4, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["i"],
        [BrailleLine(3, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["o"],
        [BrailleLine(2, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["J"],
        [BrailleLine(1, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["."],
        [BrailleLine(20, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(19, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["r"],
        [BrailleLine(18, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["e"],
        [BrailleLine(17, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["h"],
        [BrailleLine(16, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(15, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [_FAMILY],
        [BrailleLine(8, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        [" "],
        [BrailleLine(7, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["y"],
        [BrailleLine(6, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["l"],
        [BrailleLine(5, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["i"],
        [BrailleLine(4, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["m"],
        [BrailleLine(3, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["a"],
        [BrailleLine(2, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert capture(session) == (
        ["F"],
        [BrailleLine(1, _family_braille, _family_braille, "\x00" * 23)],
    )
