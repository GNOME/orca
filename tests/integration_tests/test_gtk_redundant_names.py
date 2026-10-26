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

"""Tests presentation of names Orca may treat as redundant."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .apps import gtk
from .harness import keyboard
from .helpers import BrailleLine, capture, expected_for_gtk, tab_and_swallow_presentation

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_FRAME = "OrcaRedundantNames application frame "
# GTK4 exposes named content groups instead of GTK3's panels.
_DETAILS_LINE = expected_for_gtk(
    "OrcaRedundantNames application frame panel Details button",
    gtk4="OrcaRedundantNames application frame Details button",
)
_OPTIONS_LINE = expected_for_gtk(
    "OrcaRedundantNames application frame Options panel Save button",
    gtk4="OrcaRedundantNames application frame Options grouping Save button",
)
_WEATHER_LINE = "OrcaRedundantNames application frame Weather button"


def _combo_line(table: str) -> BrailleLine:
    full = f"{_FRAME}Contraction Table: {table} combo box Alt+T"
    return BrailleLine(20, full, full[len(_FRAME) : len(_FRAME) + 32], "\x00" * len(full))


@pytest.mark.native_app
def test_container_name_matching_focused_widget(gtk_redundant_names: NativeAppSession) -> None:
    """Tests that a container is not announced by name when its child has that name."""

    session = gtk_redundant_names

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Details button"],
        [BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * len(_DETAILS_LINE))],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        expected_for_gtk(["panel", "Details button"], gtk4=["Details button"]),
        [
            BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * len(_DETAILS_LINE)),
            BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * len(_DETAILS_LINE)),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        [expected_for_gtk("Options panel", gtk4="Options grouping"), "Save button"],
        [BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * len(_OPTIONS_LINE))],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        [expected_for_gtk("Options panel", gtk4="Options grouping"), "Save button"],
        [
            BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * len(_OPTIONS_LINE)),
            BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * len(_OPTIONS_LINE)),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Weather button"],
        [BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert capture(session) == (
        ["Weather button"],
        [
            BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51),
            BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51),
        ],
    )


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="GTK4 ComboBox accessibility: https://gitlab.gnome.org/GNOME/gtk/-/work_items/4978",
)
def test_arrowing_a_combo_box_with_similar_item_names(
    gtk_redundant_names: NativeAppSession,
) -> None:
    """Tests arrowing a combo box with similar item names."""

    session = gtk_redundant_names
    for _ in range(3):
        tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Contraction Table: English, U.S., contracted combo box", "Alt+T"],
        [_combo_line("English, U.S., contracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["English, U.S., uncontracted"],
        [_combo_line("English, U.S., uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["English, unified, contracted"],
        [_combo_line("English, unified, contracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["English, unified, uncontracted"],
        [_combo_line("English, unified, uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Esperanto"],
        [_combo_line("Esperanto")],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["English, unified, uncontracted"],
        [_combo_line("English, unified, uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert capture(session) == (
        ["English, unified, contracted"],
        [_combo_line("English, unified, contracted")],
    )


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="GTK4 ComboBox accessibility: https://gitlab.gnome.org/GNOME/gtk/-/work_items/4978",
)
def test_position_in_set_when_arrowing_a_combo_box(
    gtk_redundant_names: NativeAppSession,
) -> None:
    """Tests position in set when arrowing a combo box."""

    session = gtk_redundant_names
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    for _ in range(3):
        tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["English, U.S., uncontracted", "2 of 5"],
        [_combo_line("English, U.S., uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["English, unified, contracted", "3 of 5"],
        [_combo_line("English, unified, contracted")],
    )

    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
