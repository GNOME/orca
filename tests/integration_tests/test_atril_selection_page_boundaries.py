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

from . import caret_selection_helpers as commands
from .atril_helpers import (
    FIRST_PAGE,
    SECOND_PAGE,
    assert_step,
    display_second_page,
    selected_ranges,
    selection_session,
)
from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, say_selection
from .version_helpers import requires_atril_version

if TYPE_CHECKING:
    from .orca_fixtures import AtrilSession

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
    [True, pytest.param(False, marks=requires_atril_version(1, 28, 7))],
    ids=["native", "orca"],
)
@_INDEX_BUG
def test_say_selection_includes_both_pages(atril: AtrilSession, native: bool) -> None:
    """Reports the complete selection, including the first page."""

    with selection_session(atril, native=False):
        display_second_page(atril)
    with selection_session(atril, native=native):
        if native:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
        else:
            atril.orca.select_with_caret_navigator(commands.END_OF_FILE)
        capture(atril)
        assert selected_ranges(atril) == ([(0, len(FIRST_PAGE))], [(0, len(SECOND_PAGE))])
        assert say_selection(atril) == [f"Selected text is:  {FIRST_PAGE} {SECOND_PAGE}"]


@pytest.mark.native_app
@pytest.mark.parametrize("backward", [False, True], ids=["forward", "backward"])
@_INDEX_BUG
@requires_atril_version(1, 28, 7)
def test_line_unselection_after_crossing_pages(atril: AtrilSession, backward: bool) -> None:
    """Announces the line removed when shrinking a selection across a page boundary."""

    with selection_session(atril, native=False):
        display_second_page(atril)
        move_to_top(atril)
        if backward:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
            capture(atril)
        extend = commands.PREVIOUS_LINE if backward else commands.NEXT_LINE
        shrink = commands.NEXT_LINE if backward else commands.PREVIOUS_LINE
        for _ in range(9):
            atril.orca.select_with_caret_navigator(extend)
            capture(atril)
        for _ in range(6 if backward else 3):
            atril.orca.select_with_caret_navigator(shrink)
            capture(atril)
        if backward:
            assert_step(
                atril,
                shrink,
                ["More pages!", "unselected"],
                BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\xc0" * 18),
                ([], [(12, 51)]),
                native=False,
            )
        else:
            assert_step(
                atril,
                shrink,
                ["The end.", "unselected"],
                BrailleLine(1, "The end.", "The end.", "\x00" * 8),
                ([(0, 80)], []),
                native=False,
            )


@pytest.mark.native_app
@_INDEX_BUG
@requires_atril_version(1, 28, 7)
def test_word_selection_crosses_page_boundary(atril: AtrilSession) -> None:
    """Extends a selection from the last word on page one into page two."""

    with selection_session(atril, native=False):
        display_second_page(atril)
        move_to_top(atril)
        for _ in range(5):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            capture(atril)
        for _ in range(2):
            atril.orca.select_with_caret_navigator(commands.NEXT_WORD)
            capture(atril)
        assert selected_ranges(atril) == ([(81, 89)], [])
        assert_step(
            atril,
            commands.NEXT_WORD,
            ["More", "selected"],
            BrailleLine(5, "More pages!", "More pages!", "\xc0" * 4 + "\x00" * 7),
            ([(81, 89)], [(0, 4)]),
            native=False,
        )
