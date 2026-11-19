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

"""Tests presentation of selection changes in a GTK list."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine, capture

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.parametrize("tabs", [1, 2], ids=["selection-first", "active-descendant-first"])
def test_space_selects_active_item_once(gtk_multi_select_list: NativeAppSession, tabs: int) -> None:
    """Reads the item once when Space selects it and makes it active."""

    session = gtk_multi_select_list
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    for _ in range(tabs):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        capture(session)
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session, quiescence=1.2, overall=5.0, wait_async=True)
    assert spoken == ["Read report"]
    assert brailled[-1] == BrailleLine(1, "Read report", "Read report", "\x00" * 11)


@pytest.mark.native_app
def test_selecting_and_unselecting_a_list_item(gtk_multi_select_list: NativeAppSession) -> None:
    """Tests selecting and unselecting a list item."""

    session = gtk_multi_select_list

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Olives"]
    assert brailled[-1] == BrailleLine(1, " Topping column header Olives", "Olives", "\x00" * 29)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["unselected"]
    assert brailled[-1] == BrailleLine(0, "unselected", "unselected", "\x00" * 10)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)
