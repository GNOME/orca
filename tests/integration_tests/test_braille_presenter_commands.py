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

"""Integration tests for braille word wrap and the braille monitor toggle."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

# The second line of the text view is longer than the 32-cell display, so the visible
# window is a slice of this full line.
_FULL = "Line two has additional words to make it long enough that  $l"
_SPOKEN = "Line two has additional words to make it long enough that "


@pytest.mark.native_app
def test_word_wrap_ends_visible_window_at_word_boundary(gtk3_text_view: NativeAppSession) -> None:
    """Tests that braille word wrap ends the visible window at a word boundary."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    # Default: the window is a hard slice at the display edge, mid layout.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        [_SPOKEN],
        [BrailleLine(1, _FULL, "Line two has additional words to", "\x00" * 61)],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("BraillePresenter", "WordWrapIsEnabled", True)
    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert capture(session) == (
            [_SPOKEN],
            [BrailleLine(1, _FULL, "Line two has additional words ", "\x00" * 61)],
        )
    finally:
        session.orca.set("BraillePresenter", "WordWrapIsEnabled", False)


@pytest.mark.native_app
def test_toggle_braille_monitor(gtk3_text_view: NativeAppSession) -> None:
    """Tests that toggling the braille monitor announces it enabled then disabled."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.call("BraillePresenter", "ToggleMonitor", True)
    assert capture(session) == (
        ["On-screen braille enabled."],
        [BrailleLine(0, "On-screen braille enabled.", "On-screen braille enabled.", "\x00" * 26)],
    )
    session.orca.call("BraillePresenter", "ToggleMonitor", True)
    assert capture(session) == (
        ["On-screen braille disabled."],
        [BrailleLine(0, "On-screen braille disabled.", "On-screen braille disabled.", "\x00" * 27)],
    )


@pytest.mark.native_app
def test_word_wrap_ends_table_row_window_at_word_boundary(gtk3_tree_view: NativeAppSession) -> None:
    """Tests that word wrap ends a table row's visible window on a word boundary."""

    session = gtk3_tree_view
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.set("BraillePresenter", "WordWrapIsEnabled", True)
    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        # The window ends after the whole word "check" rather than cutting "box" to "b".
        assert capture(session) == (
            ["Grace", "Admiral", "Boston", "Done check box checked"],
            [
                BrailleLine(
                    1,
                    " Name column header Grace Admiral Boston <x> check boxDone",
                    "Grace Admiral Boston <x> check ",
                    "\x00" * 58,
                )
            ],
        )
    finally:
        session.orca.set("BraillePresenter", "WordWrapIsEnabled", False)
