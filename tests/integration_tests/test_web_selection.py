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

"""Tests presentation of selection changes in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_selecting_and_unselecting_an_option(web_selection: NativeAppSession) -> None:
    """Tests selecting and unselecting an option."""

    session = web_selection
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Toppings", "multi-select List with 2 items", "Olives", "Focus mode"]
    assert brailled[0] == BrailleLine(1, "Olives", "Olives", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["unselected"]
    assert brailled[-1] == BrailleLine(0, "unselected", "unselected", "\x00" * 10)


@pytest.mark.native_app
def test_selecting_a_tree_item(web_selection: NativeAppSession) -> None:
    """Tests selecting a tree item."""

    session = web_selection
    reset_web_state(session)

    for _ in range(2):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        capture(session)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)
