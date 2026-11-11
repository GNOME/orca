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

"""Tests caret navigation after opening another document window."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine, capture, expected_for_gtk

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _assert_line(session: NativeAppSession, title: str, line: str) -> None:
    """Checks the current line's speech and braille."""

    spoken, brailled = capture(session)
    full = f"OrcaNoteReader application {title} frame {line} rdonly"
    assert spoken == expected_for_gtk([line + "\n"], gtk4=[line])
    assert brailled[-1] == BrailleLine(1, full, f"{line} rdonly"[:32], "\x00" * len(full))


@pytest.mark.native_app
@pytest.mark.parametrize("close_at_end", [False, True], ids=["middle", "end"])
def test_navigation_in_second_document(
    gtk_note_reader: NativeAppSession, close_at_end: bool
) -> None:
    """Reads the new document after closing the previous one."""

    session = gtk_note_reader
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    _assert_line(session, "Garden note", "Please water the roses.")
    keyboard.tap_key(keyboard.KEYSYM_UP)
    _assert_line(session, "Garden note", "The garden gate is open.")
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    _assert_line(session, "Garden note", "Please water the roses.")
    if close_at_end:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
        spoken, brailled = capture(session)
        assert spoken == ["The hose is beside the shed."]
        assert brailled[-1].full == (
            "OrcaNoteReader application Garden note frame The hose is beside the shed. rdonly"
        )

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session)

    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        _assert_line(session, "Kitchen note", "Please wash the apples.")
        keyboard.tap_key(keyboard.KEYSYM_UP)
        _assert_line(session, "Kitchen note", "The bread is on the table.")
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        _assert_line(session, "Kitchen note", "Please wash the apples.")
    finally:
        keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
        capture(session)
