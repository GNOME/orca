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

"""Tests activation and presentation of direct and inherited click actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


def _assert_line(
    session: BrowserSession, text: str, *, clickable: bool = False, cursor: int = 1
) -> None:
    """Checks the spoken line and its final braille presentation."""

    spoken, brailled = helpers.capture(session)
    assert spoken == ([text, "clickable"] if clickable else [text])
    assert brailled[-1] == helpers.BrailleLine(
        cursor, text, text, ("\xc0" if clickable else "\x00") * len(text)
    )


@pytest.mark.native_app
@pytest.mark.parametrize(
    "direction", [keyboard.KEYSYM_DOWN, keyboard.KEYSYM_UP], ids=["down", "up"]
)
def test_line_navigation_click_actions(web_click_actions: BrowserSession, direction: int) -> None:
    """Tests clickable announcements for direct actions and inherited actions in both directions."""

    session = web_click_actions
    helpers.reset_web_state(session)
    lines = [
        ("Direct review action", True),
        ("Inherited review action", False),
        ("Direct action", True),
        ("Inherited action", False),
    ]
    if direction == keyboard.KEYSYM_UP:
        helpers.move_to_bottom(session)
        lines.reverse()
    for text, clickable in lines:
        keyboard.tap_key(direction)
        _assert_line(session, text, clickable=clickable)


@pytest.mark.native_app
@pytest.mark.parametrize("flat_review", [False, True], ids=["caret", "flat-review"])
@pytest.mark.parametrize("inherited", [False, True], ids=["direct", "inherited"])
def test_activate_click_action(
    web_click_actions: BrowserSession, inherited: bool, flat_review: bool
) -> None:
    """Tests KP Divide activation of direct and inherited click handlers."""

    session = web_click_actions
    helpers.reset_web_state(session)
    target = "Inherited" if inherited else "Direct"
    if flat_review:
        target += " review"
        helpers.toggle_flat_review(session)
    try:
        steps = (2 if inherited else 1) + (0 if flat_review else 2)
        for _ in range(steps):
            key = keyboard.KEYSYM_KP_PAGE_UP if flat_review else keyboard.KEYSYM_DOWN
            keyboard.tap_key(key)
            spoken, brailled = helpers.capture(session)
        text = target + " action"
        assert spoken == ([text, "clickable"] if not inherited and not flat_review else [text])
        full = text + (" $l" if flat_review else "")
        mask = "\xc0" if not inherited and not flat_review else "\x00"
        assert brailled[-1] == helpers.BrailleLine(1, full, full, mask * len(full))
        keyboard.tap_key(keyboard.KEYSYM_KP_DIVIDE)
        helpers.capture(session)
    finally:
        if flat_review:
            helpers.toggle_flat_review(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    result = target + " activated."
    _assert_line(session, result, cursor=len(result) + 1)
