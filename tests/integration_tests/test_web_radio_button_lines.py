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

"""Tests line navigation through clipped radio buttons with visible labels."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import capture, move_to_bottom, move_to_top, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _radio_line(group: str, *labels: str) -> tuple[str, str]:
    """Returns the expected speech and braille for unselected choices on one line."""

    return (
        " ".join(f"{label} not selected radio button" for label in labels),
        " ".join(f"{group} & y {label} radio button" for label in labels),
    )


_DOWN_LINES = [
    ("First day panel", "First day"),
    _radio_line("First day", "Yes", "If needed", "No"),
    ("First results.", "First results."),
    ("leaving panel. Second day panel", "Second day"),
    _radio_line("Second day", "Yes", "If needed", "No"),
    ("Second results.", "Second results."),
    ("leaving panel. Vertical choices panel", "Vertical choices"),
    _radio_line("Vertical choices", "Yes"),
    _radio_line("Vertical choices", "If needed"),
    _radio_line("Vertical choices", "No"),
    ("Third results.", "Third results."),
    ("leaving panel. End.", "End."),
]

_UP_LINES = [
    ("Vertical choices Third results.", "Third results."),
    _radio_line("Vertical choices", "No"),
    _radio_line("Vertical choices", "If needed"),
    _radio_line("Vertical choices", "Yes"),
    ("Vertical choices", "Vertical choices"),
    ("Second day Second results.", "Second results."),
    _radio_line("Second day", "Yes", "If needed", "No"),
    ("Second day", "Second day"),
    ("First day First results.", "First results."),
    _radio_line("First day", "Yes", "If needed", "No"),
    ("First day", "First day"),
    ("Start.", "Start."),
]


# Without layout mode, each input and its label occupy separate lines.
_DOWN_LINES_LAYOUT_OFF = [
    ("First day panel", "First day"),
    _radio_line("First day", "Yes"),
    ("Yes", "Yes"),
    _radio_line("First day", "If needed"),
    ("If needed", "If needed"),
    _radio_line("First day", "No"),
    ("No", "No"),
    ("First results.", "First results."),
    ("leaving panel. Second day panel", "Second day"),
    _radio_line("Second day", "Yes"),
    ("Yes", "Yes"),
    _radio_line("Second day", "If needed"),
    ("If needed", "If needed"),
    _radio_line("Second day", "No"),
    ("No", "No"),
    ("Second results.", "Second results."),
    ("leaving panel. Vertical choices panel", "Vertical choices"),
    _radio_line("Vertical choices", "Yes"),
    ("Yes", "Yes"),
    _radio_line("Vertical choices", "If needed"),
    ("If needed", "If needed"),
    _radio_line("Vertical choices", "No"),
    ("No", "No"),
    ("Third results.", "Third results."),
    ("leaving panel. End.", "End."),
]

_UP_LINES_LAYOUT_OFF = [
    ("Vertical choices Third results.", "Third results."),
    ("No", "No"),
    _radio_line("Vertical choices", "No"),
    ("If needed", "If needed"),
    _radio_line("Vertical choices", "If needed"),
    ("Yes", "Yes"),
    _radio_line("Vertical choices", "Yes"),
    ("Vertical choices", "Vertical choices"),
    ("Second day Second results.", "Second results."),
    ("No", "No"),
    _radio_line("Second day", "No"),
    ("If needed", "If needed"),
    _radio_line("Second day", "If needed"),
    ("Yes", "Yes"),
    _radio_line("Second day", "Yes"),
    ("Second day", "Second day"),
    ("First day First results.", "First results."),
    ("No", "No"),
    _radio_line("First day", "No"),
    ("If needed", "If needed"),
    _radio_line("First day", "If needed"),
    ("Yes", "Yes"),
    _radio_line("First day", "Yes"),
    ("First day", "First day"),
    ("Start.", "Start."),
]


@pytest.mark.native_app
@pytest.mark.parametrize("direction", ["down", "up"])
@pytest.mark.parametrize("layout_mode", [True, False], ids=["layout-on", "layout-off"])
def test_radio_button_line_navigation(
    web_radio_button_lines: NativeAppSession,
    direction: str,
    layout_mode: bool,
) -> None:
    """Tests radio and label lines with visual grouping enabled and disabled."""

    session = web_radio_button_lines
    reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", layout_mode)
    if direction == "down":
        move_to_top(session)
        key = keyboard.KEYSYM_DOWN
        lines = _DOWN_LINES if layout_mode else _DOWN_LINES_LAYOUT_OFF
    else:
        move_to_bottom(session)
        key = keyboard.KEYSYM_UP
        lines = _UP_LINES if layout_mode else _UP_LINES_LAYOUT_OFF

    try:
        for expected_speech, expected_braille in lines:
            keyboard.tap_key(key)
            spoken, brailled = capture(session)
            assert " ".join(spoken) == expected_speech
            assert brailled[-1].full == expected_braille
    finally:
        session.orca.set("CaretNavigator", "LayoutMode", True)
