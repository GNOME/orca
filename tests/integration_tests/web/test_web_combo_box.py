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

"""Tests combo box speech and braille presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.apps import browser
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


def _focus_entry(session: BrowserSession) -> None:
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    helpers.capture(session, quiescence=0.5)
    helpers.reset_web_state(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    helpers.capture(session)


@pytest.mark.native_app
def test_unfocused_selection_change(web_combo_box: BrowserSession) -> None:
    """Keeps Fruit's change silent while the City entry has focus."""

    session = web_combo_box
    _focus_entry(session)
    keyboard.tap_key(keyboard.KEYSYM_F8)
    assert helpers.capture(session) == ([], [])
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Fruit", "combo box", "Banana", "opens listbox"]
    text = "Fruit Banana combo box"
    assert brailled[-1] == helpers.BrailleLine(7, text, text, "\x00" * len(text))


# TODO: Link the Firefox bug for missing text-selection-changed when End clears selection.
@pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Gecko omits the selection-clear event, causing an extra 'Selection deleted.'",
    strict=True,
    raises=AssertionError,
)
@pytest.mark.native_app
def test_selection_change_while_editing(web_combo_box: BrowserSession) -> None:
    """Presents the selected item's text when it replaces the focused City entry."""

    session = web_combo_box
    _focus_entry(session)
    for value in ("Paris", "Rome"):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F8)
        spoken, brailled = helpers.capture(session)
        assert spoken == [value]
        text = f"City {value} $l"
        assert brailled[-1] == helpers.BrailleLine(len(value) + 6, text, text, "\x00" * len(text))
