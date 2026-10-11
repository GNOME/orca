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

"""Tests word boundaries in a text view when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.parametrize("backward", [False, True], ids=["forward", "backward"])
@pytest.mark.parametrize(
    "line, words",
    [
        pytest.param(0, ("Start ", "doesn'", "t ", "end"), id="doesnt"),
        pytest.param(1, ("Start ", "don'", "t ", "end"), id="dont"),
        pytest.param(2, ("Start ", "doesn’", "t ", "end"), id="curly-doesnt"),
        pytest.param(3, ("Start ", "don’", "t ", "end"), id="curly-dont"),
        pytest.param(4, ("a.", "b ", "end"), id="internal-period"),
        pytest.param(5, ("Start ", "word. ", "end"), id="trailing-period"),
        pytest.param(6, ("Start '", "word' ", "end"), id="quotes"),
        pytest.param(7, ("Start `", "word` ", "end"), id="backticks"),
        pytest.param(8, ("Start ", "doesn'", "t, ", "end"), id="doesnt-comma"),
        pytest.param(9, ("Start ", "don'", "t, ", "end"), id="dont-comma"),
        pytest.param(10, ("Start ", "doesn’", "t, ", "end"), id="curly-doesnt-comma"),
        pytest.param(11, ("Start ", "don’", "t, ", "end"), id="curly-dont-comma"),
        pytest.param(12, ("Start ", "ctrl+", "alt+", "f ", "end"), id="keystroke"),
        pytest.param(13, ("Start ", "c++ ", "end"), id="double-plus"),
        pytest.param(14, ("Start ", "yay!? ", "end"), id="exclamation-question"),
        pytest.param(15, ("doesn'", "t"), id="document-end"),
    ],
)
def test_word_navigation_preserves_adjacent_ranges(
    gtk3_text_view_word_boundaries: NativeAppSession,
    line: int,
    words: tuple[str, ...],
    backward: bool,
) -> None:
    """Tests speech and caret positions for every word range in both directions."""

    session = gtk3_text_view_word_boundaries
    text = "".join(words)
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert speech(session) == ["The screen reader is controlling the caret."]
    try:
        for _ in range(line):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            capture(session)
        if backward:
            keyboard.tap_key(keyboard.KEYSYM_END)
            capture(session)

        ranges = []
        offset = 0
        for word in words:
            ranges.append((word, offset, offset + len(word.rstrip())))
            offset += len(word)

        key = keyboard.KEYSYM_LEFT if backward else keyboard.KEYSYM_RIGHT
        for word, start, end in reversed(ranges) if backward else ranges:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], key)
            spoken, brailled = capture(session)
            assert spoken == [word.rstrip()]
            assert brailled[-1].visible == f"{text} $l"
            assert brailled[-1].cursor_cell == (start if backward else end) + 1
    finally:
        session.orca.press_orca_key(keyboard.KEYSYM_F12)
        speech(session)
