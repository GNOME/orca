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

"""Tests presentation of ARIA menu buttons and their menus in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_opening_and_closing_menu_button_menus(web_menu_button: NativeAppSession) -> None:
    """Tests opening a menu button's menu, arrowing through it, and closing it."""

    session = web_menu_button
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Tools", "collapsed button", "opens menu", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Tools", "menu", "Rename"]
    assert brailled[-1] == BrailleLine(1, "Rename", "Rename", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Duplicate"]
    assert brailled[-1] == BrailleLine(1, "Duplicate", "Duplicate", "\x00" * 9)

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Delete"]
    assert brailled[-1] == BrailleLine(1, "Delete", "Delete", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Delete"]
    assert brailled[-1] == BrailleLine(1, "Delete", "Delete", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    spoken, brailled = capture(session)
    assert spoken == ["Tools", "collapsed button", "opens menu"]
    assert brailled[-1] == BrailleLine(
        1, "Tools collapsed button", "Tools collapsed button", "\x00" * 22
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Sort by", "collapsed button", "opens menu"]
    assert brailled[-1] == BrailleLine(
        1, "Sort by collapsed button", "Sort by collapsed button", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Sort by", "menu", "Name"]
    assert brailled[-1] == BrailleLine(1, "Name", "Name", "\x00" * 4)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Size"]
    assert brailled[-1] == BrailleLine(1, "Size", "Size", "\x00" * 4)

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    spoken, brailled = capture(session)
    assert spoken == ["Sort by", "collapsed button", "opens menu"]
    assert brailled[-1] == BrailleLine(
        1, "Sort by collapsed button", "Sort by collapsed button", "\x00" * 24
    )
