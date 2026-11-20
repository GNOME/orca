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

"""Tests choosing actions from the Actions List."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers, version_helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


@pytest.mark.native_app
@version_helpers.requires_browser_version("chromium", 151)
@version_helpers.requires_browser_version("firefox", 146)
@pytest.mark.parametrize(
    "action, result",
    [("Archive report", "Report archived."), ("Copy report", "Report copied.")],
)
def test_activate_aria_action(web_actions_list: BrowserSession, action: str, result: str) -> None:
    """Open the Actions List, choose a named action, and read the result."""

    session = web_actions_list
    helpers.reset_web_state(session)
    helpers.tab_and_swallow_presentation(session)
    keyboard.press_chord([keyboard.KEYSYM_INSERT, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_A)
    helpers.focus_dialog("Actions")

    count, first = helpers.expected_for_browser(session, (4, "click"), firefox=(3, "Press"))
    spoken, brailled = helpers.capture(session, wait_async=True)
    assert spoken[-2:] == [f"List with {count} items", first]
    assert brailled[-1].full == f"orca application Actions frame list box {first} "
    assert brailled[-1].visible == f"{first} "

    keyboard.tap_key(keyboard.KEYSYM_END)
    if action == "Archive report":
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = helpers.capture(session)
    assert spoken == [action]
    assert brailled[-1].visible == f"{action} "

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    helpers.capture(session, wait_async=True)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    spoken, brailled = helpers.capture(session)
    assert spoken == [result]
    assert brailled[-1].visible == result
