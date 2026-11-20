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

"""Tests native browser context-menu presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_context_menu(web_context_menu: BrowserSession) -> None:
    """Opens, navigates, and closes the context menu without repeated announcements."""

    session = web_context_menu
    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("BraillePresenter", "PresentMnemonics", False)
    session.orca.set("SpeechPresenter", "SpeakWidgetMnemonic", False)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, _brailled = helpers.capture(session)
    assert spoken == ["Tools", "collapsed button", "opens menu", "Focus mode"]

    for _ in range(3):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F10)
        spoken, brailled = helpers.capture(session, quiescence=0.3)
        assert spoken == helpers.expected_for_browser(
            session, ["menu", "opens menu"], firefox=["menu"]
        )
        assert brailled[-1] == helpers.BrailleLine(1, "menu", "menu", "\x00" * 4)

        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = helpers.capture(session)
        assert spoken == helpers.expected_for_browser(
            session, ["Back Alt+Left Arrow grayed"], firefox=["Reload"]
        )
        text = helpers.expected_for_browser(session, "Back Alt+Left Arrow", firefox="Reload")
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))

        keyboard.tap_key(keyboard.KEYSYM_UP)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["Inspect"]
        text = "Inspect"
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))

        keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["Tools", "collapsed button", "opens menu", "Focus mode"]
        assert brailled[-1] == helpers.BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)
