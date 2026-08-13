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

"""Tests caret navigation and selection in single-line entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_ORCA_CONTROLS = "The screen reader is controlling the caret."
_APP_CONTROLS = "The application is controlling the caret."
_FIRST = "OrcaTwoEntries application frame Apple pie recipe $l"
_FIRST_VISIBLE = "Apple pie recipe $l"
_SECOND = "OrcaTwoEntries application frame Banana bread recipe $l"
_SECOND_VISIBLE = "Banana bread recipe $l"


@pytest.mark.native_app
def test_caret_navigation_in_an_entry(gtk3_two_entries: NativeAppSession) -> None:
    """Tests caret navigation in an entry."""

    session = gtk3_two_entries
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["A"]
    assert brailled[-1] == BrailleLine(1, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["p"]
    assert brailled[-1] == BrailleLine(2, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Apple"]
    assert brailled[-1] == BrailleLine(6, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["blank"]
    assert brailled[-1] == BrailleLine(17, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Banana bread recipe", "text"]
    assert brailled[-1] == BrailleLine(1, _SECOND, _SECOND_VISIBLE, "\x00" * 55)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["Apple pie recipe", "text"]
    assert brailled[-1] == BrailleLine(1, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Apple pie recipe"]
    assert brailled[-1] == BrailleLine(17, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Apple pie recipe"]
    assert brailled[-1] == BrailleLine(1, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_selection_in_an_entry(gtk3_two_entries: NativeAppSession) -> None:
    """Tests selection in an entry."""

    session = gtk3_two_entries
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    assert capture(session) == (
        ["A", "selected"],
        [BrailleLine(2, _FIRST, _FIRST_VISIBLE, "\x00" * 33 + "\xc0" + "\x00" * 18)],
    )

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    assert capture(session) == (
        ["pple", "selected"],
        [BrailleLine(6, _FIRST, _FIRST_VISIBLE, "\x00" * 33 + "\xc0" * 5 + "\x00" * 14)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert capture(session) == (
        [" pie recipe", "selected"],
        [BrailleLine(17, _FIRST, _FIRST_VISIBLE, "\x00" * 33 + "\xc0" * 16 + "\x00" * 3)],
    )

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Apple pie recipe", "unselected"]
    assert brailled[-1] == BrailleLine(1, _FIRST, _FIRST_VISIBLE, "\x00" * 52)

    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert capture(session) == (["No selected text."], [])
