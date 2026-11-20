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

from tests.integration_tests import helpers
from tests.integration_tests.apps import gtk
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession

_FRAME = "OrcaRedundantNames application frame "
# GTK4 exposes named content groups instead of GTK3's panels.
_DETAILS_LINE = helpers.expected_for_gtk(
    "OrcaRedundantNames application frame panel Details button",
    gtk4="OrcaRedundantNames application frame Details button",
)
_OPTIONS_LINE = helpers.expected_for_gtk(
    "OrcaRedundantNames application frame Options panel Save button",
    gtk4="OrcaRedundantNames application frame Options grouping Save button",
)
_WEATHER_LINE = "OrcaRedundantNames application frame Weather button"


def _combo_line(table: str) -> helpers.BrailleLine:
    full = f"{_FRAME}Contraction Table: {table} combo box Alt+T"
    return helpers.BrailleLine(20, full, full[len(_FRAME) : len(_FRAME) + 32], "\x00" * len(full))


@pytest.mark.native_app
def test_container_name_matching_focused_widget(gtk_redundant_names: NativeAppSession) -> None:
    """Tests that a container is not announced by name when its child has that name."""

    session = gtk_redundant_names

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert helpers.capture(session) == (
        ["Details button"],
        [helpers.BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * len(_DETAILS_LINE))],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert helpers.capture(session) == (
        helpers.expected_for_gtk(["panel", "Details button"], gtk4=["Details button"]),
        [
            helpers.BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * len(_DETAILS_LINE)),
            helpers.BrailleLine(1, _DETAILS_LINE, "Details button", "\x00" * len(_DETAILS_LINE)),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        [helpers.expected_for_gtk("Options panel", gtk4="Options grouping"), "Save button"],
        [helpers.BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * len(_OPTIONS_LINE))],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert helpers.capture(session) == (
        [helpers.expected_for_gtk("Options panel", gtk4="Options grouping"), "Save button"],
        [
            helpers.BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * len(_OPTIONS_LINE)),
            helpers.BrailleLine(1, _OPTIONS_LINE, "Save button", "\x00" * len(_OPTIONS_LINE)),
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Weather button"],
        [helpers.BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51)],
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=2)
    assert helpers.capture(session) == (
        ["Weather button"],
        [
            helpers.BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51),
            helpers.BrailleLine(1, _WEATHER_LINE, "Weather button", "\x00" * 51),
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
        helpers.tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert helpers.capture(session) == (
        ["Contraction Table: English, U.S., contracted combo box", "Alt+T"],
        [_combo_line("English, U.S., contracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["English, U.S., uncontracted"],
        [_combo_line("English, U.S., uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["English, unified, contracted"],
        [_combo_line("English, unified, contracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["English, unified, uncontracted"],
        [_combo_line("English, unified, uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["Esperanto"],
        [_combo_line("Esperanto")],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        ["English, unified, uncontracted"],
        [_combo_line("English, unified, uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
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
        helpers.tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["English, U.S., uncontracted", "2 of 5"],
        [_combo_line("English, U.S., uncontracted")],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["English, unified, contracted", "3 of 5"],
        [_combo_line("English, unified, contracted")],
    )

    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
