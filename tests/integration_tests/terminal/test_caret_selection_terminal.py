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

"""Tests text selection in a terminal when Orca controls the caret."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import caret_selection_helpers, helpers, terminal_helpers
from tests.integration_tests.apps import terminal
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession

pytestmark = [
    pytest.mark.xfail(
        terminal.selected_toolkit() == "konsole",
        reason=(
            "Konsole's TerminalDisplayAccessible::selection() and addSelection() use cell offsets "
            "inconsistent with inherited textAtOffset()"
            " (https://bugs.kde.org/show_bug.cgi?id=528946); text() includes the end offset"
            " (https://bugs.kde.org/show_bug.cgi?id=528942)"
        ),
        raises=AssertionError,
        strict=True,
    ),
    pytest.mark.skipif(
        terminal.selected_toolkit() == "gtk4",
        reason="GTK4 VTE cannot set text selections: "
        "https://gitlab.gnome.org/GNOME/vte/-/work_items/2973",
    ),
]

_ORCA_CONTROLS = "The screen reader is controlling the caret."
_APP_CONTROLS = "The application is controlling the caret."

# After selection collapses, VTE reports the terminal cursor on the pager status line.
_STATUS_LINE = helpers.BrailleLine(8, "doc.txt", "doc.txt", "\x00" * 7)


def _move_to_the_second_line(session: NativeAppSession) -> None:
    """Puts the caret at the start of the second line of the document."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.1, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["line 02\n"],
        [helpers.BrailleLine(1, "line 02", "line 02", "\x00" * 7)],
    )


@pytest.mark.native_app
def test_selection_by_character(terminal_pager: NativeAppSession) -> None:
    """Tests selection by character."""

    session = terminal_pager
    terminal_helpers.settle(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.capture(session)[0] == [_ORCA_CONTROLS]

    _move_to_the_second_line(session)

    assert caret_selection_helpers.select(session, caret_selection_helpers.NEXT_CHARACTER) == (
        ["l", "selected"],
        helpers.BrailleLine(2, "line 02", "line 02", "\xc0" + "\x00" * 6),
    )
    assert caret_selection_helpers.select(session, caret_selection_helpers.NEXT_CHARACTER) == (
        ["i", "selected"],
        helpers.BrailleLine(3, "line 02", "line 02", "\xc0" * 2 + "\x00" * 5),
    )
    assert helpers.say_selection(session) == ["Selected text is:  li"]

    assert caret_selection_helpers.select(session, caret_selection_helpers.PREVIOUS_CHARACTER) == (
        ["i", "unselected"],
        helpers.BrailleLine(2, "line 02", "line 02", "\xc0" + "\x00" * 6),
    )
    assert helpers.say_selection(session) == ["Selected text is:  l"]

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_selection_by_word_and_line(terminal_pager: NativeAppSession) -> None:
    """Tests selection by word and by line."""

    session = terminal_pager
    terminal_helpers.settle(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.capture(session)[0] == [_ORCA_CONTROLS]

    _move_to_the_second_line(session)

    assert caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD) == (
        ["line", "selected"],
        helpers.BrailleLine(5, "line 02", "line 02", "\xc0" * 4 + "\x00" * 3),
    )
    assert caret_selection_helpers.select(session, caret_selection_helpers.END_OF_LINE) == (
        [" 02", "selected"],
        helpers.BrailleLine(8, "line 02", "line 02", "\xc0" * 7),
    )
    assert helpers.say_selection(session) == ["Selected text is:  line 02"]

    assert caret_selection_helpers.select(session, caret_selection_helpers.NEXT_LINE) == (
        ["\n", "selected"],
        helpers.BrailleLine(1, "line 03", "line 03", "\x00" * 7),
    )
    assert helpers.say_selection(session) == ["Selected text is:  line 02\n"]

    assert caret_selection_helpers.select(session, caret_selection_helpers.PREVIOUS_LINE) == (
        ["line 02\n", "unselected"],
        _STATUS_LINE,
    )
    assert helpers.say_selection(session) == ["No selected text."]

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_selection_removed_by_caret_navigation(terminal_pager: NativeAppSession) -> None:
    """Tests removing a selection with the caret navigation commands."""

    session = terminal_pager
    terminal_helpers.settle(session)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert helpers.speech(session) == ["line 01\n"]

    assert caret_selection_helpers.select(session, caret_selection_helpers.NEXT_WORD) == (
        ["line", "selected"],
        helpers.BrailleLine(5, "line 01", "line 01", "\xc0" * 4 + "\x00" * 3),
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Text unselected.", "line 02\n"]
    assert helpers.say_selection(session) == ["No selected text."]

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.capture(session)[0] == [_APP_CONTROLS]
