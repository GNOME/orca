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

"""Tests presentation of an ARIA menubar with menus and submenus in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_arrow_navigation_through_the_menubar(web_menubar: NativeAppSession) -> None:
    """Tests arrow navigation through the menubar, its menus, and a submenu."""

    session = web_menubar
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["leaving banner.", "Home", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Catalog", "collapsed", "opens menu"]
    assert brailled[-1] == BrailleLine(1, "Catalog collapsed", "Catalog collapsed", "\x00" * 17)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["expanded", "Books"]
    assert brailled[-1] == BrailleLine(1, "Books", "Books", "\x00" * 5)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Maps"]
    assert brailled[-1] == BrailleLine(1, "Maps", "Maps", "\x00" * 4)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Archives", "collapsed", "opens menu"]
    assert brailled[-1] == BrailleLine(1, "Archives collapsed", "Archives collapsed", "\x00" * 18)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["expanded", "Letters"]
    assert brailled[-1] == BrailleLine(1, "Letters", "Letters", "\x00" * 7)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Photographs"]
    assert brailled[-1] == BrailleLine(1, "Photographs", "Photographs", "\x00" * 11)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Photographs"]
    assert brailled[-1] == BrailleLine(1, "Photographs", "Photographs", "\x00" * 11)

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    spoken, brailled = capture(session)
    assert spoken == ["Archives", "collapsed", "opens menu"]
    assert brailled[-1] == BrailleLine(1, "Archives collapsed", "Archives collapsed", "\x00" * 18)

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    spoken, brailled = capture(session)
    assert spoken == ["Catalog", "collapsed", "opens menu"]
    assert brailled[-1] == BrailleLine(1, "Catalog collapsed", "Catalog collapsed", "\x00" * 17)

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["Home"]
    assert brailled[-1] == BrailleLine(1, "Home", "Home", "\x00" * 4)

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == []
    assert brailled == []

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Contact"]
    assert brailled[-1] == BrailleLine(1, "Contact", "Contact", "\x00" * 7)
