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

"""Tests presentation of grouped and multi-select ARIA listboxes in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_listbox_navigation(web_listbox: NativeAppSession) -> None:
    """Tests listbox navigation."""

    session = web_listbox
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "Transuranium elements",
        "List with 5 items",
        "Actinides",
        "Neptunium",
        "Focus mode",
    ]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Plutonium"]
    assert brailled[-1] == BrailleLine(1, "Plutonium", "Plutonium", "\x00" * 9)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Americium"]
    assert brailled[-1] == BrailleLine(1, "Americium", "Americium", "\x00" * 9)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["leaving panel.", "Transactinides", "Rutherfordium"]
    assert brailled[-1] == BrailleLine(1, "Rutherfordium", "Rutherfordium", "\x00" * 13)

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["leaving panel.", "Actinides", "Neptunium"]
    assert brailled[-1] == BrailleLine(1, "Neptunium", "Neptunium", "\x00" * 9)

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["leaving panel.", "Transactinides", "Dubnium"]
    assert brailled[-1] == BrailleLine(1, "Dubnium", "Dubnium", "\x00" * 7)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Dubnium", "list item"]
    assert brailled[-1] == BrailleLine(1, "Dubnium", "Dubnium", "\x00" * 7)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == [
        "leaving panel.",
        "Nearby amenities",
        "multi-select List with 3 items",
        "A park",
        "not selected",
    ]
    assert brailled[-1] == BrailleLine(1, "A park", "A park", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["A school", "not selected"]
    assert brailled[-1] == BrailleLine(1, "A school", "A school", "\x00" * 8)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Shops", "not selected"]
    assert brailled[-1] == BrailleLine(1, "Shops", "Shops", "\x00" * 5)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)

    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["A park", "not selected", "1 of 3"]
    assert brailled[-1] == BrailleLine(1, "A park", "A park", "\x00" * 6)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["A school", "2 of 3"]
    assert brailled[-1] == BrailleLine(1, "A school", "A school", "\x00" * 8)
