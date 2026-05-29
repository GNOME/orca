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

"""Tests the GTK TextView braille selection underline (uncontracted, contracted, panning)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_LINE_COMPUTER = "Line two has additional words to make it long enough that  $l"
_LINE_CONTRACTED = ",l9e two has a4i;nal ~ws 6make x l;g 5 t  $l"


def _mask(full: str, selected_cells: int) -> str:
    """Returns a full-line mask with the selector indicator on the first selected_cells cells."""

    return "\xc0" * selected_cells + "\x00" * (len(full) - selected_cells)


def _setup_on_line_two(
    session: NativeAppSession, *, table: str | None, word_wrap: bool = False
) -> None:
    """Configures braille for the given table and moves onto the wide second line."""

    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("BraillePresenter", "WordWrapIsEnabled", word_wrap)
    if table is None:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", False)
    else:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
        session.orca.set("BraillePresenter", "ContractionTable", table)
        session.orca.set("BraillePresenter", "ComputerBrailleAtCursorIsEnabled", False)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.4, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _select_word(session: NativeAppSession) -> tuple[list[str], list[helpers.BrailleLine]]:
    """Extends the selection by one word and returns the capture."""

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    return helpers.capture(session)


@pytest.mark.native_app
def test_selection_mask_uncontracted(gtk3_text_view: NativeAppSession) -> None:
    """Tests that the selection underline spans the verbatim cells of each selected word."""

    session = gtk3_text_view
    _setup_on_line_two(session, table=None)
    line = _LINE_COMPUTER
    assert _select_word(session) == (
        ["Line", "selected"],
        [helpers.BrailleLine(5, line, "Line two has additional words to", _mask(line, 4))],
    )
    assert _select_word(session) == (
        [" two", "selected"],
        [helpers.BrailleLine(9, line, "Line two has additional words to", _mask(line, 8))],
    )
    assert _select_word(session) == (
        [" has", "selected"],
        [helpers.BrailleLine(13, line, "Line two has additional words to", _mask(line, 12))],
    )
    assert _select_word(session) == (
        [" additional", "selected"],
        [helpers.BrailleLine(24, line, "Line two has additional words to", _mask(line, 23))],
    )


@pytest.mark.native_app
def test_selection_mask_contracted(gtk3_text_view: NativeAppSession) -> None:
    """Tests that the selection underline tracks the contracted cells."""

    session = gtk3_text_view
    _setup_on_line_two(session, table="en-us-g2")
    line = _LINE_CONTRACTED
    assert _select_word(session) == (
        ["Line", "selected"],
        [helpers.BrailleLine(5, line, ",l9e two has a4i;nal ~ws 6make x", _mask(line, 4))],
    )
    assert _select_word(session) == (
        [" two", "selected"],
        [helpers.BrailleLine(9, line, ",l9e two has a4i;nal ~ws 6make x", _mask(line, 8))],
    )
    assert _select_word(session) == (
        [" has", "selected"],
        [helpers.BrailleLine(13, line, ",l9e two has a4i;nal ~ws 6make x", _mask(line, 12))],
    )
    assert _select_word(session) == (
        [" additional", "selected"],
        [helpers.BrailleLine(21, line, ",l9e two has a4i;nal ~ws 6make x", _mask(line, 20))],
    )


@pytest.mark.native_app
def test_pan_contracted_selection_word_wrap_off(gtk3_text_view: NativeAppSession) -> None:
    """Tests panning a selected wide line: word-wrap off cuts the window at a fixed 32 cells."""

    session = gtk3_text_view
    _setup_on_line_two(session, table="en-us-g2", word_wrap=False)
    line = _LINE_CONTRACTED
    mask = _mask(line, 40)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert helpers.capture(session) == (
        ["Line two has additional words to make it long enough that", "selected"],
        [helpers.BrailleLine(32, line, "has a4i;nal ~ws 6make x l;g 5 t ", mask)],
    )
    with helpers.bound_pan_keys(session) as (_left_key, right_key):
        session.orca.press_bound_key(right_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(1, line, "  $l", mask)],
        )


@pytest.mark.native_app
def test_pan_contracted_selection_word_wrap_on(gtk3_text_view: NativeAppSession) -> None:
    """Tests panning a selected wide line: word-wrap on breaks the window at word boundaries."""

    session = gtk3_text_view
    _setup_on_line_two(session, table="en-us-g2", word_wrap=True)
    line = _LINE_CONTRACTED
    # Same selection mask as word-wrap off; only the visible window differs (word-aligned, not cut).
    mask = _mask(line, 40)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    assert helpers.capture(session) == (
        ["Line two has additional words to make it long enough that", "selected"],
        [helpers.BrailleLine(10, line, "x l;g 5 t  $l", mask)],
    )
    with helpers.bound_pan_keys(session) as (left_key, _right_key):
        session.orca.press_bound_key(left_key)
        assert helpers.capture(session) == (
            [],
            [helpers.BrailleLine(0, line, ",l9e two has a4i;nal ~ws 6make ", mask)],
        )
