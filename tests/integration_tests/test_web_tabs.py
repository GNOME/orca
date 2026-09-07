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

"""Tests presentation of ARIA tabs in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_tabs_navigation(web_tabs: NativeAppSession) -> None:
    """Tests tabs navigation."""

    session = web_tabs
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Aberdeen", "page tab", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Brindisi", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Brindisi page tab", "Brindisi page tab", "\x00" * 17)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Cusco", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Cusco page tab", "Cusco page tab", "\x00" * 14)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["Cusco", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Cusco page tab", "Cusco page tab", "\x00" * 14)

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Aberdeen", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Aberdeen page tab", "Aberdeen page tab", "\x00" * 17)

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Cusco", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Cusco page tab", "Cusco page tab", "\x00" * 14)

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["selected"]
    assert brailled[-1] == BrailleLine(0, "selected", "selected", "\x00" * 8)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Spring", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Spring page tab", "Spring page tab", "\x00" * 15)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Cusco", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Cusco page tab", "Cusco page tab", "\x00" * 14)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Aberdeen", "page tab"]
    assert brailled[-1] == BrailleLine(1, "Aberdeen page tab", "Aberdeen page tab", "\x00" * 17)

    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Brindisi", "page tab", "2 of 3"]
    assert brailled[-1] == BrailleLine(1, "Brindisi page tab", "Brindisi page tab", "\x00" * 17)

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Aberdeen", "page tab", "1 of 3"]
    assert brailled[-1] == BrailleLine(1, "Aberdeen page tab", "Aberdeen page tab", "\x00" * 17)
