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

"""Tests speech and braille for wrapped text."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.apps import browser
from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


_GECKO_TEXT_BOUNDS = pytest.mark.xfail(
    browser.selected_browser() == "firefox",
    reason="Gecko reports incorrect text bounds: "
    "https://bugzilla.mozilla.org/show_bug.cgi?id=2090138",
    strict=True,
    raises=AssertionError,
)


@_GECKO_TEXT_BOUNDS
@pytest.mark.native_app
@pytest.mark.parametrize("layout_mode", [True, False])
def test_say_all_after_find(web_say_all_wrapped_text: BrowserSession, layout_mode: bool) -> None:
    """Reads from a search match without repeating wrapped lines."""

    session = web_say_all_wrapped_text
    helpers.reset_web_state(session)
    session.orca.set("SayAllPresenter", "Style", "line")
    session.orca.set("CaretNavigator", "LayoutMode", layout_mode)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_F)
    for char in "musetto watches":
        keyboard.tap_key(ord(char))
    helpers.capture(session, wait_async=True)
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    helpers.capture(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    spoken, brailled = helpers.capture(session, wait_async=True)
    assert " ".join(" ".join(spoken).split()) == (
        "Musetto watches the garden from his favorite window. "
        "He tells us when a sparrow visits the fence. "
        "After lunch he inspects every cupboard for toys. "
        "In the evening he curls up beside his friend. Time for a nap."
    )
    assert brailled[-1] == BrailleLine(1, "Time for a nap.", "Time for a nap.", "\x00" * 15)


@pytest.mark.native_app
@pytest.mark.parametrize("layout_mode", [pytest.param(True, marks=_GECKO_TEXT_BOUNDS), False])
@pytest.mark.parametrize("reverse", [False, True])
def test_line_navigation(
    web_say_all_wrapped_text: BrowserSession, layout_mode: bool, reverse: bool
) -> None:
    """Reads each wrapped line once when navigating down or up."""

    session = web_say_all_wrapped_text
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", layout_mode)
    lines = [
        "Siamese cats always have something to say.",
        "Musetto watches the garden from his favorite",
        "window. He tells us when a sparrow visits the",
        "fence. After lunch he inspects every cupboard",
        "for toys. In the evening he curls up beside his",
        "friend.",
        "Time for a nap.",
    ]
    if reverse:
        helpers.move_to_bottom(session)
    expected = list(reversed(lines[:-1])) if reverse else lines[1:]
    speech = []
    braille = []
    for _ in expected:
        keyboard.tap_key(keyboard.KEYSYM_UP if reverse else keyboard.KEYSYM_DOWN)
        spoken, brailled = helpers.capture(session)
        speech.append(" ".join(" ".join(spoken).split()))
        braille.append(brailled[-1].full.strip() if brailled else "")
    assert speech == expected
    assert braille == expected
