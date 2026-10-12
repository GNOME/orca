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

"""Tests explicit selection changes in a grid where selection does not follow focus."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
@pytest.mark.parametrize("table_navigation", [False, True], ids=["application", "orca-table"])
def test_select_and_unselect_grid_cells(
    web_grid_selection: BrowserSession, table_navigation: bool
) -> None:
    """Tests selecting cells independently and unselecting them after moving focus."""

    session = web_grid_selection
    reset_web_state(session)
    modifiers = [keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L] if table_navigation else []
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session)

    # Writing starts selected; moving focus around the grid must preserve selection.
    for key in (
        keyboard.KEYSYM_RIGHT,
        keyboard.KEYSYM_DOWN,
        keyboard.KEYSYM_LEFT,
        keyboard.KEYSYM_UP,
    ):
        keyboard.press_chord(modifiers, key)
        capture(session)

    for key, expected in (
        (None, "selected"),
        (keyboard.KEYSYM_RIGHT, "unselected"),
        (keyboard.KEYSYM_LEFT, "unselected"),
        (keyboard.KEYSYM_RIGHT, "selected"),
    ):
        if key is not None:
            keyboard.press_chord(modifiers, key)
            capture(session)
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        spoken, brailled = capture(session)
        assert spoken == [expected]
        assert brailled[-1] == BrailleLine(0, expected, expected, "\x00" * len(expected))
