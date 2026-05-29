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

"""Tests the web braille selection underline (editable, non-editable, uncontracted, contracted)."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .orca_fixtures import NativeAppSession

_FULL_COMPUTER = "knowledge good people child about character educated everywhere indeed. $l"
_VISIBLE_COMPUTER = "knowledge good people child abou"
_FULL_CONTRACTED = 'k gd p * ab "* $ucat$ "ey": 9de$4 $l'
_VISIBLE_CONTRACTED = 'k gd p * ab "* $ucat$ "ey": 9de$'

_HEADING_CONTRACTED = ",3trac;ns ;h#a"


def _selection_mask(full: str, selected_cells: int) -> str:
    """Returns a full-line mask with the selector indicator on the first selected_cells cells."""

    return "\xc0" * selected_cells + "\x00" * (len(full) - selected_cells)


def _mask_cells(full: str, start: int, end: int) -> str:
    """Returns a full-line mask with the selector indicator on cells [start, end)."""

    return "\x00" * start + "\xc0" * (end - start) + "\x00" * (len(full) - end)


def _assert_selection(
    session: NativeAppSession, *, speech: list[str], line: helpers.BrailleLine
) -> None:
    """Asserts the speech and the settled (last) braille frame after a selection change."""

    spoken, brailled = helpers.capture(session)
    assert (spoken, brailled[-1]) == (speech, line)


def _configure_and_focus_editable(session: NativeAppSession, *, table: str | None) -> None:
    """Resets state, configures braille, and tabs into the editable div (caret at its start)."""

    helpers.reset_web_state(session)
    if table is None:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", False)
    else:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
        session.orca.set("BraillePresenter", "ContractionTable", table)
        session.orca.set("BraillePresenter", "ComputerBrailleAtCursorIsEnabled", False)
    session.reader.drain(quiescence_timeout=0.4, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_TAB)  # focus the link
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_TAB)  # focus the contenteditable div
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    # Collapse to the field start; a prior test can leave a selection that Tab refocus restores.
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _configure_noneditable_contracted(session: NativeAppSession) -> None:
    """Resets state and configures contracted braille without focusing the editable field."""

    helpers.reset_web_state(session)
    session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
    session.orca.set("BraillePresenter", "ContractionTable", "en-us-g2")
    session.orca.set("BraillePresenter", "ComputerBrailleAtCursorIsEnabled", False)
    session.reader.drain(quiescence_timeout=0.4, overall_timeout=2.0)
    session.reader.reset()


@contextlib.contextmanager
def _sticky_focus_mode(session: NativeAppSession) -> Iterator[None]:
    """Turns on sticky focus mode so Shift+arrow selection reaches the browser and stays in sync."""

    ((key, mods),) = session.orca.available_keybindings(1)
    session.orca.bind_command("enable_sticky_focus_mode", key, mods)
    session.orca.refresh_keybindings()
    session.orca.press_bound_key(key)
    session.reader.drain(quiescence_timeout=0.4, overall_timeout=2.0)
    session.reader.reset()
    try:
        yield
    finally:
        session.orca.unbind_command("enable_sticky_focus_mode")
        session.orca.refresh_keybindings()


@pytest.mark.native_app
def test_editable_selection_uncontracted(web_contracted_braille: NativeAppSession) -> None:
    """Tests that the selection underline spans the verbatim cells of each selected word."""

    session = web_contracted_braille
    _configure_and_focus_editable(session, table=None)
    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    _assert_selection(
        session,
        speech=["knowledge", "selected"],
        line=helpers.BrailleLine(
            10, _FULL_COMPUTER, _VISIBLE_COMPUTER, _selection_mask(_FULL_COMPUTER, 9)
        ),
    )
    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    _assert_selection(
        session,
        speech=[" good", "selected"],
        line=helpers.BrailleLine(
            15, _FULL_COMPUTER, _VISIBLE_COMPUTER, _selection_mask(_FULL_COMPUTER, 14)
        ),
    )


@pytest.mark.native_app
def test_editable_selection_contracted(web_contracted_braille: NativeAppSession) -> None:
    """Tests that the selection underline collapses to the contracted cells."""

    session = web_contracted_braille
    _configure_and_focus_editable(session, table="en-us-g2")
    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    _assert_selection(
        session,
        speech=["knowledge", "selected"],
        line=helpers.BrailleLine(
            2, _FULL_CONTRACTED, _VISIBLE_CONTRACTED, _selection_mask(_FULL_CONTRACTED, 1)
        ),
    )
    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    _assert_selection(
        session,
        speech=[" good", "selected"],
        line=helpers.BrailleLine(
            5, _FULL_CONTRACTED, _VISIBLE_CONTRACTED, _selection_mask(_FULL_CONTRACTED, 4)
        ),
    )


@pytest.mark.native_app
def test_editable_selection_midstring_extend_and_unselect(
    web_contracted_braille: NativeAppSession,
) -> None:
    """Tests a selection that starts mid-line, extends to the end, then is collapsed."""

    session = web_contracted_braille
    _configure_and_focus_editable(session, table="en-us-g2")
    # Move the caret past "knowledge good" so the selection starts in the middle of the line.
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.press_chord(
        [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
    )
    _assert_selection(
        session,
        speech=[" people", "selected"],
        line=helpers.BrailleLine(
            7, _FULL_CONTRACTED, _VISIBLE_CONTRACTED, _mask_cells(_FULL_CONTRACTED, 4, 6)
        ),
    )
    # Extend to the end of the line; the underline runs to the last text cell, not the EOL.
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    _assert_selection(
        session,
        speech=[" child about character educated everywhere indeed.", "selected"],
        line=helpers.BrailleLine(
            32,
            _FULL_CONTRACTED,
            'gd p * ab "* $ucat$ "ey": 9de$4 ',
            _mask_cells(_FULL_CONTRACTED, 4, 33),
        ),
    )
    # Collapsing the selection clears the whole mask and announces the change.
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    _assert_selection(
        session,
        speech=["Text unselected."],
        line=helpers.BrailleLine(
            32, _FULL_CONTRACTED, 'gd p * ab "* $ucat$ "ey": 9de$4 ', "\x00" * len(_FULL_CONTRACTED)
        ),
    )


@pytest.mark.native_app
def test_noneditable_selection_contracted(web_contracted_braille: NativeAppSession) -> None:
    """Tests that selecting non-editable page text underlines the contracted cells."""

    session = web_contracted_braille
    _configure_noneditable_contracted(session)
    with _sticky_focus_mode(session):
        keyboard.press_chord(
            [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT
        )
        _assert_selection(
            session,
            speech=["Contractions", "selected"],
            line=helpers.BrailleLine(
                10,
                _HEADING_CONTRACTED,
                _HEADING_CONTRACTED,
                _selection_mask(_HEADING_CONTRACTED, 9),
            ),
        )
