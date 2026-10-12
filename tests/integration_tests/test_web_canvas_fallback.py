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

"""Tests navigation through canvas fallback text and controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
@pytest.mark.parametrize("layout_mode", [True, False], ids=["layout-on", "layout-off"])
def test_line_navigation_through_canvas_fallback(
    web_canvas_fallback: BrowserSession, layout_mode: bool
) -> None:
    """Tests Down and Up across canvas fallback content and surrounding paragraphs."""

    session = web_canvas_fallback
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", layout_mode)
    before = (["Before canvas."], BrailleLine(1, "Before canvas.", "Before canvas.", "\x00" * 14))
    heading = (["Message", "heading 2"], BrailleLine(1, "Message h2", "Message h2", "\x00" * 10))
    button = (["Save", "button"], BrailleLine(1, "Save button", "Save button", "\x00" * 11))
    after = (["After canvas."], BrailleLine(1, "After canvas.", "After canvas.", "\x00" * 13))
    if layout_mode:
        paragraph = [
            (
                ["Quiet ", "river", "link", " flows."],
                BrailleLine(
                    1,
                    "Quiet river flows.",
                    "Quiet river flows.",
                    "\x00" * 6 + "\xc0" * 5 + "\x00" * 7,
                ),
            )
        ]
    else:
        paragraph = [
            (["Quiet "], BrailleLine(1, "Quiet ", "Quiet ", "\x00" * 6)),
            (["river", "link"], BrailleLine(1, "river", "river", "\xc0" * 5)),
            ([" flows."], BrailleLine(1, " flows.", " flows.", "\x00" * 7)),
        ]

    forward = [before, (["canvas", *heading[0]], heading[1]), *paragraph, button, after]
    backward = [
        (["canvas", *button[0]], button[1]),
        *reversed(paragraph),
        heading,
        before,
        (
            ["Canvas fallback", "heading 1"],
            BrailleLine(1, "Canvas fallback h1", "Canvas fallback h1", "\x00" * 18),
        ),
    ]
    for key, expected in ((keyboard.KEYSYM_DOWN, forward), (keyboard.KEYSYM_UP, backward)):
        for expected_speech, expected_braille in expected:
            keyboard.tap_key(key)
            spoken, brailled = capture(session)
            assert spoken == expected_speech
            assert brailled[-1] == expected_braille


@pytest.mark.native_app
def test_structural_navigation_through_canvas_fallback(web_canvas_fallback: BrowserSession) -> None:
    """Tests heading, link, and button navigation within canvas fallback content."""

    session = web_canvas_fallback
    reset_web_state(session)
    expected = [
        (keyboard.KEYSYM_H, [], ["h", "canvas", "Message", "heading 2"], "Message h2", "\x00" * 10),
        (keyboard.KEYSYM_K, [], ["k", "river", "link"], "river", "\xc0" * 5),
        (keyboard.KEYSYM_B, [], ["b", "Save", "button"], "Save button", "\x00" * 11),
        (keyboard.KEYSYM_K, [keyboard.KEYSYM_SHIFT_L], ["K", "river", "link"], "river", "\xc0" * 5),
        (
            keyboard.KEYSYM_H,
            [keyboard.KEYSYM_SHIFT_L],
            ["H", "Message", "heading 2"],
            "Message h2",
            "\x00" * 10,
        ),
    ]
    for key, modifiers, expected_speech, line, mask in expected:
        keyboard.press_chord(modifiers, key)
        spoken, brailled = capture(session)
        assert spoken == expected_speech
        assert brailled[-1] == BrailleLine(1, line, line, mask)


@pytest.mark.native_app
def test_tab_navigation_through_canvas_fallback(web_canvas_fallback: BrowserSession) -> None:
    """Tests Tab and Shift+Tab reach the fallback link and button."""

    session = web_canvas_fallback
    reset_web_state(session)
    expected = [
        ([], ["canvas", "river", "link"], "river", "\xc0" * 5),
        ([], ["Save", "button"], "Save button", "\x00" * 11),
        ([keyboard.KEYSYM_SHIFT_L], ["river", "link"], "river", "\xc0" * 5),
    ]
    for modifiers, expected_speech, line, mask in expected:
        keyboard.press_chord(modifiers, keyboard.KEYSYM_TAB)
        spoken, brailled = capture(session)
        assert spoken == expected_speech
        assert brailled[-1] == BrailleLine(1, line, line, mask)
