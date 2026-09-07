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

from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_selecting_and_unselecting_a_list_item(gtk3_multi_select_list: NativeAppSession) -> None:
    """Tests selecting and unselecting a list item."""

    session = gtk3_multi_select_list

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
