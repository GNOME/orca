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

"""Tests presentation of an ARIA toolbar and its controls in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_arrow_navigation_through_toolbar_controls(web_toolbar: NativeAppSession) -> None:
    """Tests arrowing through the toolbar's buttons, radio group, menu, spin button, and link."""

    session = web_toolbar
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Bold", "toggle button not pressed", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Italic", "toggle button not pressed"]
    assert brailled[-1] == BrailleLine(
        1, "& y Italic toggle button", "& y Italic toggle button", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Underline", "toggle button not pressed"]
    assert brailled[-1] == BrailleLine(
        1, "& y Underline toggle button", "& y Underline toggle button", "\x00" * 27
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Text Alignment", "panel", "Text Align Left", "selected radio button"]
    assert brailled[-1] == BrailleLine(
        1,
        "Text Alignment &=y Text Align Left radio button",
        "&=y Text Align Left radio button",
        "\x00" * 47,
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Text Align Center", "not selected radio button"]
    assert brailled[-1] == BrailleLine(
        1,
        "Text Alignment & y Text Align Center radio button",
        "& y Text Align Center radio butt",
        "\x00" * 49,
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Text Align Right", "not selected radio button"]
    assert brailled[-1] == BrailleLine(
        1,
        "Text Alignment & y Text Align Right radio button",
        "& y Text Align Right radio butto",
        "\x00" * 48,
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["leaving panel.", "Copy", "button grayed"]
    assert brailled[-1] == BrailleLine(1, "Copy button", "Copy button", "\x00" * 11)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Paste", "button grayed"]
    assert brailled[-1] == BrailleLine(1, "Paste button", "Paste button", "\x00" * 12)

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Font: Sans-serif", "collapsed button", "opens menu"]
    assert brailled[-1] == BrailleLine(
        1, "Font: Sans-serif collapsed button", "Font: Sans-serif collapsed butto", "\x00" * 33
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Font Family", "menu", "Sans-serif", "radio menu item selected"]
    assert brailled[-1] == BrailleLine(
        1, "&=y Sans-serif radio menu item", "&=y Sans-serif radio menu item", "\x00" * 30
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Serif", "radio menu item not selected"]
    assert brailled[-1] == BrailleLine(
        1, "& y Serif radio menu item", "& y Serif radio menu item", "\x00" * 25
    )

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    spoken, brailled = capture(session)
    assert spoken == ["Font: Sans-serif", "collapsed button", "opens menu"]
    assert brailled[-1] == BrailleLine(
        1, "Font: Sans-serif collapsed button", "Font: Sans-serif collapsed butto", "\x00" * 33
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Font size in points", "spin button", "14pt"]
    assert brailled[-1] == BrailleLine(
        1, "Font size in points 14pt spin button", "Font size in points 14pt spin bu", "\x00" * 36
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["15pt"]
    assert brailled[-1] == BrailleLine(
        1, "Font size in points 15pt spin button", "Font size in points 15pt spin bu", "\x00" * 36
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["14pt"]
    assert brailled[-1] == BrailleLine(
        1, "Font size in points 14pt spin button", "Font size in points 14pt spin bu", "\x00" * 36
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Night Mode", "check box not checked"]
    assert brailled[-1] == BrailleLine(
        1, "< > Night Mode check box", "< > Night Mode check box", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    spoken, brailled = capture(session)
    assert spoken == ["checked"]
    assert brailled[-1] == BrailleLine(
        1, "<x> Night Mode check box", "<x> Night Mode check box", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["Help", "link"]
    assert brailled[-1] == BrailleLine(1, "Help", "Help", "ÀÀÀÀ")

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == []
    assert brailled == []

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Bold", "toggle button not pressed"]
    assert brailled[-1] == BrailleLine(
        1, "& y Bold toggle button", "& y Bold toggle button", "\x00" * 22
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["Help", "link"]
    assert brailled[-1] == BrailleLine(1, "Help", "Help", "\xc0" * 4)

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["Night Mode", "check box checked"]
    assert brailled[-1] == BrailleLine(
        1, "<x> Night Mode check box", "<x> Night Mode check box", "\x00" * 24
    )
