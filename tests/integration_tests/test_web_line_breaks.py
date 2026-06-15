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

"""Line navigation through paragraphs whose lines are split by br rather than collapsed."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _assert_lines_two_through_five(session: NativeAppSession) -> None:
    """Arrows Down through the remaining four lines, checking Orca speaks each separately."""

    # A line that ends in a br carries the trailing newline in its content.
    for expected in ["Two", "three four\n", "five", "This is a test of orca."]:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == [expected]


@pytest.mark.native_app
def test_browse_mode_line_navigation(web_line_breaks: NativeAppSession) -> None:
    """Tests that Orca speaks each br-delimited line separately during caret navigation."""

    session = web_line_breaks
    helpers.reset_web_state(session)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    assert helpers.speech(session) == ["One\n"]
    _assert_lines_two_through_five(session)


@pytest.mark.native_app
def test_focus_mode_line_navigation(web_line_breaks: NativeAppSession) -> None:
    """Tests that Orca speaks each br-delimited line when focus mode is forced on a document."""

    session = web_line_breaks
    helpers.reset_web_state(session)

    keyboard.press_chord([keyboard.KEYSYM_INSERT], keyboard.KEYSYM_A)
    assert helpers.speech(session) == ["Focus mode"]
    _assert_lines_two_through_five(session)


@pytest.mark.native_app
def test_app_controlled_line_navigation(web_line_breaks: NativeAppSession) -> None:
    """Tests that Orca speaks each br-delimited line when the application controls the caret."""

    session = web_line_breaks
    helpers.reset_web_state(session)

    keyboard.press_chord([keyboard.KEYSYM_INSERT], keyboard.KEYSYM_F12)
    assert helpers.speech(session) == ["The application is controlling the caret."]
    _assert_lines_two_through_five(session)
