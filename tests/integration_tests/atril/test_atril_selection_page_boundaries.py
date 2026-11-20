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

"""Regressions blocked by Atril pages reporting an index in parent of -1."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import atril_helpers, helpers, version_helpers
from tests.integration_tests import caret_selection_helpers as commands
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import AtrilSession

# Confirmed directly through AT-SPI on Atril 1.28.7, without Orca.
# Both pages are present in their parent but return -1 for get_index_in_parent().
_INDEX_BUG = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril pages return index-in-parent -1, breaking cross-page selection: "
        "https://github.com/mate-desktop/atril/issues/732"
    ),
)


@pytest.mark.native_app
@pytest.mark.parametrize(
    "native",
    [True, pytest.param(False, marks=version_helpers.requires_atril_version(1, 28, 7))],
    ids=["native", "orca"],
)
@_INDEX_BUG
def test_say_selection_includes_both_pages(atril: AtrilSession, native: bool) -> None:
    """Reports the complete selection, including the first page."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
    with atril_helpers.selection_session(atril, native=native):
        if native:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
        else:
            atril.orca.select_with_caret_navigator(commands.END_OF_FILE)
        helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == (
            [(0, len(atril_helpers.FIRST_PAGE))],
            [(0, len(atril_helpers.SECOND_PAGE))],
        )
        assert helpers.say_selection(atril) == [
            f"Selected text is:  {atril_helpers.FIRST_PAGE} {atril_helpers.SECOND_PAGE}"
        ]


@pytest.mark.native_app
@pytest.mark.parametrize("backward", [False, True], ids=["forward", "backward"])
@_INDEX_BUG
@version_helpers.requires_atril_version(1, 28, 7)
def test_line_unselection_after_crossing_pages(atril: AtrilSession, backward: bool) -> None:
    """Announces the line removed when shrinking a selection across a page boundary."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        if backward:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
            helpers.capture(atril)
        extend = commands.PREVIOUS_LINE if backward else commands.NEXT_LINE
        shrink = commands.NEXT_LINE if backward else commands.PREVIOUS_LINE
        for _ in range(9):
            atril.orca.select_with_caret_navigator(extend)
            helpers.capture(atril)
        for _ in range(6 if backward else 3):
            atril.orca.select_with_caret_navigator(shrink)
            helpers.capture(atril)
        if backward:
            atril_helpers.assert_step(
                atril,
                shrink,
                ["More pages!", "unselected"],
                helpers.BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
                ([], [(12, 51)]),
                native=False,
            )
        else:
            atril_helpers.assert_step(
                atril,
                shrink,
                ["The end.", "unselected"],
                helpers.BrailleLine(1, "The end.", "The end.", "\x00" * 8),
                ([(0, 80)], []),
                native=False,
            )


@pytest.mark.native_app
@_INDEX_BUG
@version_helpers.requires_atril_version(1, 28, 7)
def test_word_selection_crosses_page_boundary(atril: AtrilSession) -> None:
    """Extends a selection from the last word on page one into page two."""

    with atril_helpers.selection_session(atril, native=False):
        atril_helpers.display_second_page(atril)
        helpers.move_to_top(atril)
        for _ in range(5):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.capture(atril)
        for _ in range(2):
            atril.orca.select_with_caret_navigator(commands.NEXT_WORD)
            helpers.capture(atril)
        assert atril_helpers.selected_ranges(atril) == ([(81, 89)], [])
        atril_helpers.assert_step(
            atril,
            commands.NEXT_WORD,
            ["More", "selected"],
            helpers.BrailleLine(5, "More pages!", "More pages!", "\xc0" * 4 + "\x00" * 7),
            ([(81, 89)], [(0, 4)]),
            native=False,
        )
