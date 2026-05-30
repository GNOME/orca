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

"""Tests presentation of a native GTK SpinButton."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _prepare(session: NativeAppSession) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    keyboard.tap_key(keyboard.KEYSYM_F12)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _collapse_to_start(session: NativeAppSession) -> None:
    """Collapses the tab-in 'all-selected' state and parks the caret before '7'."""

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _press(session: NativeAppSession, keysym: int) -> tuple[list[str], list[helpers.BrailleLine]]:
    keyboard.tap_key(keysym)
    return helpers.capture(session)


def _press_chord(
    session: NativeAppSession, modifiers: list[int], keysym: int
) -> tuple[list[str], list[helpers.BrailleLine]]:
    keyboard.press_chord(modifiers, keysym)
    return helpers.capture(session)


@pytest.mark.native_app
def test_spin_button_value_changes(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests that arrowing a spin button announces and brailles the new value."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)

    up = helpers.BrailleLine(10, "Quantity 76 $l", "Quantity 76 $l", "\x00" * 14)
    down = helpers.BrailleLine(10, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)
    assert _press(session, keyboard.KEYSYM_UP) == (["76"], [up])
    assert _press(session, keyboard.KEYSYM_DOWN) == (["75"], [down])


@pytest.mark.native_app
def test_caret_left_right(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests Left/Right caret navigation across the multi-digit value text."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)

    before_seven = helpers.BrailleLine(10, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)
    between = helpers.BrailleLine(11, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)
    after_five = helpers.BrailleLine(12, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)

    assert _press(session, keyboard.KEYSYM_LEFT) == (
        ["Text unselected.", "7"],
        [before_seven, before_seven],
    )
    assert _press(session, keyboard.KEYSYM_LEFT) == ([], [])
    assert _press(session, keyboard.KEYSYM_LEFT) == ([], [])

    assert _press(session, keyboard.KEYSYM_RIGHT) == (["5"], [between])
    assert _press(session, keyboard.KEYSYM_RIGHT) == (["blank"], [after_five])
    assert _press(session, keyboard.KEYSYM_RIGHT) == ([], [])


@pytest.mark.native_app
def test_home_and_end(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests Home/End jump within the spin button's editable text."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    _collapse_to_start(session)

    assert _press(session, keyboard.KEYSYM_END) == (
        ["blank"],
        [helpers.BrailleLine(12, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)],
    )
    assert _press(session, keyboard.KEYSYM_HOME) == (
        ["7"],
        [helpers.BrailleLine(10, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)],
    )


@pytest.mark.native_app
def test_shift_selection(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests Shift+Left/Right selecting and unselecting digits."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    _collapse_to_start(session)

    one_selected = "\x00" * 9 + "\xc0" + "\x00" * 4
    two_selected = "\x00" * 9 + "\xc0\xc0" + "\x00" * 3
    cleared = "\x00" * 14

    assert _press_chord(session, [keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT) == (
        ["7", "selected"],
        [helpers.BrailleLine(11, "Quantity 75 $l", "Quantity 75 $l", one_selected)],
    )
    assert _press_chord(session, [keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT) == (
        ["5", "selected"],
        [helpers.BrailleLine(12, "Quantity 75 $l", "Quantity 75 $l", two_selected)],
    )
    assert _press_chord(session, [keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT) == (
        ["5", "unselected"],
        [helpers.BrailleLine(11, "Quantity 75 $l", "Quantity 75 $l", one_selected)],
    )
    cleared_line = helpers.BrailleLine(10, "Quantity 75 $l", "Quantity 75 $l", cleared)
    assert _press_chord(session, [keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_LEFT) == (
        ["7", "unselected"],
        [cleared_line, cleared_line],
    )


@pytest.mark.native_app
def test_backspace(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests Backspace from the trailing caret position consuming digits."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    _collapse_to_start(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    single_digit = helpers.BrailleLine(11, "Quantity 7 $l", "Quantity 7 $l", "\x00" * 13)
    empty_value = helpers.BrailleLine(10, "Quantity  $l", "Quantity  $l", None)
    assert _press(session, keyboard.KEYSYM_BACKSPACE) == (["5"], [single_digit])
    assert _press(session, keyboard.KEYSYM_BACKSPACE) == (["7"], [empty_value])


@pytest.mark.native_app
def test_delete(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests Delete from the leading caret position consuming digits."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    _collapse_to_start(session)

    assert _press(session, keyboard.KEYSYM_DELETE) == (
        ["5"],
        [helpers.BrailleLine(10, "Quantity 5 $l", "Quantity 5 $l", "\x00" * 13)],
    )
    assert _press(session, keyboard.KEYSYM_DELETE) == (
        [""],
        [helpers.BrailleLine(10, "Quantity  $l", "Quantity  $l", None)],
    )


@pytest.mark.native_app
def test_typing(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests typing digits at the end of the value text."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    _collapse_to_start(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    after_9 = helpers.BrailleLine(13, "Quantity 759 $l", "Quantity 759 $l", "\x00" * 15)
    after_90 = helpers.BrailleLine(14, "Quantity 7590 $l", "Quantity 7590 $l", "\x00" * 16)
    assert _press(session, keyboard.KEYSYM_9) == (["9"], [after_9, after_9])
    assert _press(session, keyboard.KEYSYM_0) == (["0"], [after_90, after_90])


@pytest.mark.native_app
def test_page_up_and_down(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests PageUp/PageDown stepping the value by ten."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)

    at_85 = helpers.BrailleLine(10, "Quantity 85 $l", "Quantity 85 $l", "\x00" * 14)
    at_75 = helpers.BrailleLine(10, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 14)
    assert _press(session, keyboard.KEYSYM_PAGE_UP) == (["85"], [at_85])
    assert _press(session, keyboard.KEYSYM_PAGE_DOWN) == (["75"], [at_75])


@pytest.mark.native_app
def test_value_boundaries(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests that Up at the maximum and Down at the minimum are silent."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    # Replace the all-selected '75' by typing the new value, then commit via Tab.
    keyboard.tap_key(keyboard.KEYSYM_1)
    keyboard.tap_key(keyboard.KEYSYM_0)
    keyboard.tap_key(keyboard.KEYSYM_0)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    assert _press(session, keyboard.KEYSYM_UP) == ([], [])

    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    keyboard.tap_key(keyboard.KEYSYM_0)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    assert _press(session, keyboard.KEYSYM_DOWN) == ([], [])


@pytest.mark.native_app
def test_programmatic_change_focus_on_bump_button(
    gtk3_widget_notebook: NativeAppSession,
) -> None:
    """Tests that an off-focus programmatic value change is silent."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    for _ in range(6):
        helpers.tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    # wait_async so the drain waits through the deferred bump to confirm it stays silent,
    # rather than returning the instant Orca goes idle (before the bump fires).
    assert helpers.capture(session, wait_async=True, overall=2.0) == ([], [])


@pytest.mark.native_app
def test_readonly_spin_button(gtk3_widget_notebook: NativeAppSession) -> None:
    """Tests focus and keys on a non-editable native GTK SpinButton."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(9):
        helpers.tab_and_swallow_presentation(session)

    assert _press(session, keyboard.KEYSYM_TAB) == (
        ["Readonly spin button 25"],
        [helpers.BrailleLine(10, "Readonly 25", "Readonly 25", "\x00" * 11)],
    )

    assert _press(session, keyboard.KEYSYM_UP) == ([], [])
    assert _press(session, keyboard.KEYSYM_DOWN) == ([], [])
    assert _press(session, keyboard.KEYSYM_LEFT) == ([], [])

    assert _press(session, keyboard.KEYSYM_5) == (["5"], [])


@pytest.mark.native_app
def test_programmatic_change_focus_on_spinbutton(
    gtk3_widget_notebook: NativeAppSession,
) -> None:
    """Tests that an in-focus programmatic value change interrupts and announces."""

    session = gtk3_widget_notebook
    _prepare(session)
    for _ in range(3):
        helpers.tab_and_swallow_presentation(session)
    for _ in range(6):
        helpers.tab_and_swallow_presentation(session)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    for _ in range(6):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)

    all_selected = "\x00" * 9 + "\xc0\xc0" + "\x00" * 3
    quantity_76 = helpers.BrailleLine(10, "Quantity 76 $l", "Quantity 76 $l", "\x00" * 14)
    assert helpers.capture(session, quiescence=1.5, overall=3.5) == (
        ["76"],
        [
            helpers.BrailleLine(12, "Quantity 75 $l", "Quantity 75 $l", all_selected),
            quantity_76,
            helpers.BrailleLine(0, "Selection deleted.", "Selection deleted.", "\x00" * 18),
            quantity_76,
            quantity_76,
            quantity_76,
        ],
    )
