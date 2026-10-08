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

"""Tests line navigation through colored blocks with and without click handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession

_COLORS = ["Red", "Green", "Blue"]
_LAYOUTS = [
    ("Clickable blocks", [_COLORS], True),
    ("Plain blocks", [_COLORS], False),
    ("Stacked clickable blocks", [[color] for color in _COLORS], True),
    ("Stacked plain blocks", [[color] for color in _COLORS], False),
    ("Wrapped clickable blocks", [_COLORS[:2], _COLORS[2:]], True),
    ("Wrapped plain blocks", [_COLORS[:2], _COLORS[2:]], False),
    ("Nested clickable labels", [_COLORS], False),
    ("Nested plain labels", [_COLORS], False),
    (
        "Multiline clickable labels",
        [[text] for color in _COLORS for text in (color, "Tone")],
        False,
    ),
    ("Multiline plain labels", [[text] for color in _COLORS for text in (color, "Tone")], False),
]


@pytest.mark.native_app
@pytest.mark.parametrize(
    "direction", [keyboard.KEYSYM_DOWN, keyboard.KEYSYM_UP], ids=["down", "up"]
)
@pytest.mark.parametrize("layout", range(len(_LAYOUTS)), ids=[case[0] for case in _LAYOUTS])
def test_line_navigation_groups_blocks(
    web_colored_blocks: BrowserSession, layout: int, direction: int
) -> None:
    """Tests visual lines and their boundaries in both navigation directions."""

    session = web_colored_blocks
    helpers.reset_web_state(session)
    heading, lines, clickable = _LAYOUTS[layout]
    reverse = direction == keyboard.KEYSYM_UP
    for _ in range(layout + 1 + int(reverse)):
        keyboard.tap_key(keyboard.KEYSYM_H)
        helpers.capture(session)
    if reverse:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.speech(session) == ["After blocks."]

    for line in reversed(lines) if reverse else lines:
        keyboard.tap_key(direction)
        spoken, brailled = helpers.capture(session)
        expected = [part for color in line for part in (color, "clickable")] if clickable else line
        assert spoken == expected
        assert brailled[-1].full == " ".join(line)

    keyboard.tap_key(direction)
    expected = [heading, "heading 2"] if reverse else ["After blocks."]
    assert helpers.speech(session) == expected
