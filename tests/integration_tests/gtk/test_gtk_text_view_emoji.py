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

from tests.integration_tests import helpers, version_helpers
from tests.integration_tests.apps import gtk
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession

_US_FLAG = "\U0001f1fa\U0001f1f8"
_IT_FLAG = "\U0001f1ee\U0001f1f9"
_FAMILY = "\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466"

_FLAGS_LINE = f"Flags {_US_FLAG} and {_IT_FLAG} here."
_JOINED_LINE = f"Joined {_US_FLAG}{_IT_FLAG} flags."
_FAMILY_LINE = f"Family {_FAMILY} here."


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_down_arrow_announces_whole_emoji_lines(gtk_text_view_emoji: NativeAppSession) -> None:
    """Down-arrow presents each line with whole emoji intact."""

    session = gtk_text_view_emoji
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk([f"{_FLAGS_LINE}\n"], gtk4=[_FLAGS_LINE]),
        [helpers.BrailleLine(1, f"{_FLAGS_LINE} $l", f"{_FLAGS_LINE} $l", "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk([f"{_JOINED_LINE}\n"], gtk4=[_JOINED_LINE]),
        [helpers.BrailleLine(1, f"{_JOINED_LINE} $l", f"{_JOINED_LINE} $l", "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk(
            [f"{_FAMILY_LINE}\n"],
            gtk4=[_FAMILY_LINE],
        ),
        [helpers.BrailleLine(1, f"{_FAMILY_LINE} $l", f"{_FAMILY_LINE} $l", "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["End."],
        [helpers.BrailleLine(1, "End. $l", "End. $l", "\x00" * 7)],
    )


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_word_nav_announces_whole_emoji(gtk_text_view_emoji: NativeAppSession) -> None:
    """Ctrl+Right word navigation produces whole emoji as part of each word unit."""

    session = gtk_text_view_emoji
    helpers.move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    _flags_braille = f"{_FLAGS_LINE} $l"
    _joined_braille = f"{_JOINED_LINE} $l"
    _family_braille = f"{_FAMILY_LINE} $l"

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["Flags"],
        [helpers.BrailleLine(6, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [f"{_US_FLAG} and"],
        [helpers.BrailleLine(13, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [f"{_IT_FLAG} here"],
        [helpers.BrailleLine(21, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [".\nJoined"],
        [helpers.BrailleLine(7, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [f"{_US_FLAG}{_IT_FLAG} flags"],
        [helpers.BrailleLine(18, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [".\nFamily"],
        [helpers.BrailleLine(7, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [f"{_FAMILY} here"],
        [helpers.BrailleLine(20, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [".\nEnd"],
        [helpers.BrailleLine(4, "End. $l", "End. $l", "\x00" * 7)],
    )

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(5, "End. $l", "End. $l", "\x00" * 7)],
    )


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_char_nav_right_announces_whole_emoji(gtk_text_view_emoji: NativeAppSession) -> None:
    """Right-arrow character navigation presents each flag and ZWJ family as a single stop."""

    session = gtk_text_view_emoji

    _flags_braille = f"{_FLAGS_LINE} $l"
    _joined_braille = f"{_JOINED_LINE} $l"
    _family_braille = f"{_FAMILY_LINE} $l"

    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["l"],
        [helpers.BrailleLine(2, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(3, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["g"],
        [helpers.BrailleLine(4, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["s"],
        [helpers.BrailleLine(5, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(6, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [_US_FLAG],
        [helpers.BrailleLine(7, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(9, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(10, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["n"],
        [helpers.BrailleLine(11, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["d"],
        [helpers.BrailleLine(12, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(13, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [_IT_FLAG],
        [helpers.BrailleLine(14, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(16, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["h"],
        [helpers.BrailleLine(17, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(18, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["r"],
        [helpers.BrailleLine(19, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(20, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(21, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["blank"],
        [helpers.BrailleLine(22, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    helpers.move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["o"],
        [helpers.BrailleLine(2, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["i"],
        [helpers.BrailleLine(3, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["n"],
        [helpers.BrailleLine(4, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(5, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["d"],
        [helpers.BrailleLine(6, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(7, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [_US_FLAG],
        [helpers.BrailleLine(8, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [_IT_FLAG],
        [helpers.BrailleLine(10, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(12, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["f"],
        [helpers.BrailleLine(13, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["l"],
        [helpers.BrailleLine(14, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(15, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["g"],
        [helpers.BrailleLine(16, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["s"],
        [helpers.BrailleLine(17, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(18, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["blank"],
        [helpers.BrailleLine(19, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    helpers.move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(2, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["m"],
        [helpers.BrailleLine(3, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["i"],
        [helpers.BrailleLine(4, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["l"],
        [helpers.BrailleLine(5, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["y"],
        [helpers.BrailleLine(6, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(7, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [_FAMILY],
        [helpers.BrailleLine(8, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(15, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["h"],
        [helpers.BrailleLine(16, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(17, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["r"],
        [helpers.BrailleLine(18, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(19, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(20, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    assert helpers.capture(session) == (
        ["blank"],
        [helpers.BrailleLine(21, _family_braille, _family_braille, "\x00" * 23)],
    )


@pytest.mark.native_app
@version_helpers.requires_gtk_version("4.0", 4, 24, when=gtk.is_gtk4())
def test_char_nav_left_announces_whole_emoji(gtk_text_view_emoji: NativeAppSession) -> None:
    """Left-arrow character navigation presents each flag and ZWJ family as a single stop."""

    session = gtk_text_view_emoji

    _flags_braille = f"{_FLAGS_LINE} $l"
    _joined_braille = f"{_JOINED_LINE} $l"
    _family_braille = f"{_FAMILY_LINE} $l"

    helpers.move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(21, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(20, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["r"],
        [helpers.BrailleLine(19, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(18, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["h"],
        [helpers.BrailleLine(17, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(16, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [_IT_FLAG],
        [helpers.BrailleLine(14, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(13, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["d"],
        [helpers.BrailleLine(12, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["n"],
        [helpers.BrailleLine(11, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(10, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(9, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [_US_FLAG],
        [helpers.BrailleLine(7, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(6, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["s"],
        [helpers.BrailleLine(5, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["g"],
        [helpers.BrailleLine(4, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(3, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["l"],
        [helpers.BrailleLine(2, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["F"],
        [helpers.BrailleLine(1, _flags_braille, _flags_braille, "\x00" * 24)],
    )

    helpers.move_to_top(session)
    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(18, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["s"],
        [helpers.BrailleLine(17, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["g"],
        [helpers.BrailleLine(16, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(15, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["l"],
        [helpers.BrailleLine(14, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["f"],
        [helpers.BrailleLine(13, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(12, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [_IT_FLAG],
        [helpers.BrailleLine(10, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [_US_FLAG],
        [helpers.BrailleLine(8, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(7, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["d"],
        [helpers.BrailleLine(6, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(5, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["n"],
        [helpers.BrailleLine(4, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["i"],
        [helpers.BrailleLine(3, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["o"],
        [helpers.BrailleLine(2, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["J"],
        [helpers.BrailleLine(1, _joined_braille, _joined_braille, "\x00" * 21)],
    )

    helpers.move_to_top(session)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["."],
        [helpers.BrailleLine(20, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(19, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["r"],
        [helpers.BrailleLine(18, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["e"],
        [helpers.BrailleLine(17, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["h"],
        [helpers.BrailleLine(16, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(15, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [_FAMILY],
        [helpers.BrailleLine(8, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        [" "],
        [helpers.BrailleLine(7, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["y"],
        [helpers.BrailleLine(6, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["l"],
        [helpers.BrailleLine(5, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["i"],
        [helpers.BrailleLine(4, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["m"],
        [helpers.BrailleLine(3, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["a"],
        [helpers.BrailleLine(2, _family_braille, _family_braille, "\x00" * 23)],
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    assert helpers.capture(session) == (
        ["F"],
        [helpers.BrailleLine(1, _family_braille, _family_braille, "\x00" * 23)],
    )
