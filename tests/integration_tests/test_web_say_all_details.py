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

"""Tests Say All through native details which can expand on focus."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
@pytest.mark.parametrize("expand_on_focus", [False, True])
def test_say_all_continues_past_details(
    web_say_all_details: BrowserSession, expand_on_focus: bool
) -> None:
    """Reading a summary must not expand its details or interrupt Say All."""

    session = web_say_all_details
    session.orca.set("DocumentPresenter", "SayAllOnLoad", False)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    helpers.reset_web_state(session)

    if not expand_on_focus:
        keyboard.tap_key(keyboard.KEYSYM_X)
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        assert helpers.speech(session) == ["not checked"]

    keyboard.tap_key(keyboard.KEYSYM_H)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Before details."]

    # Start via D-Bus so the recent-keyboard check cannot mask the interruption.
    session.orca.call("SayAllPresenter", "SayAll", True)
    spoken, brailled = helpers.capture(session, wait_async=True)
    role = helpers.expected_for_browser(
        session, "toggle button collapsed", firefox="collapsed button"
    )
    assert " ".join(spoken) == f"Before details. More options {role} After details."
    assert brailled[-1] == BrailleLine(1, "After details.", "After details.", "\x00" * 14)
