# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, Inc.;
# either version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA 02110-1301 USA.

"""Tests Orca-controlled caret navigation through blank lines in a text view."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_ORCA_CONTROLS = "The screen reader is controlling the caret."
_APP_CONTROLS = "The application is controlling the caret."
_BLANK_LINE = BrailleLine(1, " $l", " $l", "\x00" * 3)
_FIRST_LINE = BrailleLine(
    1,
    "OrcaTextView application frame First sentence. $l",
    "First sentence. $l",
    "\x00" * 49,
)
_SECOND_LINE = BrailleLine(1, "Second sentence. $l", "Second sentence. $l", "\x00" * 19)


@pytest.mark.native_app
def test_caret_navigation_through_blank_line(
    gtk3_text_view_blank_line: NativeAppSession,
) -> None:
    """Tests Orca-controlled line navigation through an interior blank line."""

    session = gtk3_text_view_blank_line
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["blank"]
    assert brailled[-1] == _BLANK_LINE

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Second sentence.\n"]
    assert brailled[-1] == _SECOND_LINE

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["blank"]
    assert brailled[-1] == _BLANK_LINE

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["First sentence.\n"]
    assert brailled[-1] == _FIRST_LINE

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]


@pytest.mark.native_app
def test_caret_navigation_at_trailing_blank_line(
    gtk3_text_view_blank_line: NativeAppSession,
) -> None:
    """Tests Orca-controlled navigation to and from a trailing blank line."""

    session = gtk3_text_view_blank_line
    move_to_top(session)
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_ORCA_CONTROLS]

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["blank"]
    assert brailled[-1] == _BLANK_LINE

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["Second sentence.\n"]
    assert brailled[-1] == _SECOND_LINE

    # Moving onto the trailing blank line is silent. Moving back up verifies that the
    # caret reached it; otherwise Up would land on the interior blank line.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["Second sentence.\n"]
    assert brailled[-1] == _SECOND_LINE

    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert capture(session)[0] == [_APP_CONTROLS]
