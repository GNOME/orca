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

"""Tests Say All after focus moves between terminals."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.parametrize("remove_previous", [False, True], ids=["retained", "removed"])
def test_say_all_after_terminal_focus_change(
    gtk3_terminal_focus: NativeAppSession,
    remove_previous: bool,
) -> None:
    """Tests that Say All uses the newly focused terminal's caret offset."""

    session = gtk3_terminal_focus
    settle(session)
    session.orca.set("SayAllPresenter", "Style", "line")
    session.orca.press_orca_key(keyboard.KEYSYM_F12)
    assert helpers.speech(session) == ["The screen reader is controlling the caret."]
    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == ["Last line.\n"]
        keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
        assert helpers.speech(session, quiescence=0.5, overall=10.0) == ["Last line.\n"]

        keyboard.tap_key(keyboard.KEYSYM_F7 if remove_previous else keyboard.KEYSYM_F6)
        settle(session)
        keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
        assert helpers.speech(session, quiescence=0.5, overall=10.0) == [
            "Second terminal.\n",
            "Final line.\n",
        ]
    finally:
        session.orca.press_orca_key(keyboard.KEYSYM_F12)
        settle(session)
