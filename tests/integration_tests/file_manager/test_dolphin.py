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

"""Tests navigation, selection, and review in Dolphin's icon and Details views."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests.file_manager_helpers import LONG_NAME
from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine, bound_pan_keys, capture

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import FileManagerSession


def _item_braille(
    session: FileManagerSession, name: str, folder: str = "Test Files"
) -> BrailleLine:
    """Builds the expected braille for a file or folder."""

    label = name
    if session.view == "list" and name in ("02 Nested", "03 Scrolling"):
        label += " collapsed"
    full = (
        f"dolphin application {folder} \u2014 Dolphin frame Location View layered pane "
        f"split pane {folder} list {label}"
    )
    return BrailleLine(1, full, label[:32], "\x00" * len(full))


def _assert_item(
    session: FileManagerSession,
    name: str,
    *,
    unselected: bool = False,
    folder: str = "Test Files",
) -> None:
    """Checks the file or folder announcement in speech and braille."""

    spoken, brailled = capture(session)
    expected = [name]
    if unselected:
        expected.append("not selected")
    if session.view == "list" and name in ("02 Nested", "03 Scrolling"):
        expected.append("collapsed")
    expected.append(", Plain text document" if name.endswith(".txt") else ", Folder")
    assert spoken == expected
    assert brailled[-1] == _item_braille(session, name, folder)


def _assert_message(session: FileManagerSession, message: str) -> None:
    spoken, brailled = capture(session)
    assert spoken == [message]
    assert brailled[-1] == BrailleLine(0, message, message, "\x00" * len(message))


def _start_at_first_file(session: FileManagerSession) -> None:
    """Navigates to the first file and checks its presentation."""

    keyboard.tap_key(keyboard.KEYSYM_END)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    _assert_item(session, "01 Empty")


@pytest.mark.native_app
@pytest.mark.parametrize("control", [False, True])
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_arrow_navigation(dolphin: FileManagerSession, control: bool) -> None:
    """Checks file announcements after arrow and Ctrl+arrow keys."""

    session = dolphin
    _start_at_first_file(session)
    modifiers = [keyboard.KEYSYM_CONTROL_L] if control else []
    if session.view == "icon":
        moves = [
            (keyboard.KEYSYM_RIGHT, "02 Nested"),
            (keyboard.KEYSYM_DOWN, "echo.txt"),
            (keyboard.KEYSYM_LEFT, "delta.txt"),
            (keyboard.KEYSYM_UP, "01 Empty"),
        ]
    else:
        moves = [
            (keyboard.KEYSYM_DOWN, "02 Nested"),
            (keyboard.KEYSYM_DOWN, "03 Scrolling"),
            (keyboard.KEYSYM_UP, "02 Nested"),
            (keyboard.KEYSYM_UP, "01 Empty"),
        ]
    for key, name in moves:
        keyboard.press_chord(modifiers, key)
        _assert_item(session, name, unselected=control and name != "01 Empty")


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon"], indirect=True)
def test_icon_row_boundary(dolphin: FileManagerSession) -> None:
    """Checks Right into the next icon row and Left back into the previous row."""

    session = dolphin
    _start_at_first_file(session)
    names = ["02 Nested", "03 Scrolling", "alpha.txt", "bravo.txt", "charlie.txt", "delta.txt"]
    for name in names:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        _assert_item(session, name)
    for name in reversed(["01 Empty", *names[:-1]]):
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        _assert_item(session, name)


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_home_end_and_boundaries(dolphin: FileManagerSession) -> None:
    """Checks Home and End navigation, and pressing Up on the first item."""

    session = dolphin
    _start_at_first_file(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == []
    assert all(line == _item_braille(session, "01 Empty") for line in brailled)
    keyboard.tap_key(keyboard.KEYSYM_END)
    _assert_item(session, LONG_NAME)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    _assert_item(session, "01 Empty")


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_control_space_selection(dolphin: FileManagerSession) -> None:
    """Adds a second selection, returns to the first, and removes both selections."""

    session = dolphin
    _start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    backward = keyboard.KEYSYM_LEFT if session.view == "icon" else keyboard.KEYSYM_UP
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
    _assert_item(session, "02 Nested", unselected=True)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
    _assert_message(session, "selected")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], backward)
    _assert_item(session, "01 Empty")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
    _assert_message(session, "unselected")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
    _assert_item(session, "02 Nested")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
    _assert_message(session, "unselected")


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_range_selection(dolphin: FileManagerSession) -> None:
    """Checks file announcements as Shift+arrows extend and shrink a selection."""

    session = dolphin
    _start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    backward = keyboard.KEYSYM_LEFT if session.view == "icon" else keyboard.KEYSYM_UP
    names = ["01 Empty", "02 Nested", "03 Scrolling"]
    for index in (1, 2):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
        _assert_item(session, names[index])
    for index in (1, 0):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], backward)
        _assert_item(session, names[index])


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_braille_panning(dolphin: FileManagerSession) -> None:
    """Checks speech and braille when panning a long filename forward and back."""

    session = dolphin
    _start_at_first_file(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    _assert_item(session, LONG_NAME)
    original = _item_braille(session, LONG_NAME)
    with bound_pan_keys(session) as (left, right):
        for key, cursor, visible in (
            (right, 0, "braille panning and file navigat"),
            (right, 0, "navigation.txt"),
            (left, 0, "braille panning and file navigat"),
            (left, 1, "long filename for testing braill"),
        ):
            session.orca.press_bound_key(key)
            spoken, brailled = capture(session)
            assert spoken == []
            assert brailled[-1] == BrailleLine(cursor, original.full, visible, original.mask)


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_where_am_i(dolphin: FileManagerSession) -> None:
    """Checks Where Am I after selecting three items."""

    session = dolphin
    _start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for _ in range(2):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
        capture(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    expected = ["03 Scrolling list item"]
    if session.view == "list":
        expected.append("collapsed")
    expected.append(", Folder")
    assert spoken == expected
    assert brailled[-1] == _item_braille(session, "03 Scrolling")


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_space_behavior(dolphin: FileManagerSession) -> None:
    """Checks Space announcing selection mode enabled and then disabled."""

    session = dolphin
    _start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for unselected in (False, True):
        if unselected:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
            _assert_item(session, "02 Nested", unselected=True)
        for message in ("Selection mode enabled", "Selection mode disabled"):
            keyboard.tap_key(keyboard.KEYSYM_SPACE)
            _assert_message(session, message)


@pytest.mark.native_app
@pytest.mark.parametrize("dolphin", ["icon", "list"], indirect=True)
def test_return_to_parent(dolphin: FileManagerSession) -> None:
    """Checks the Child folder announcement after returning with Alt+Up."""

    session = dolphin
    _start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    keyboard.tap_key(forward)
    _assert_item(session, "02 Nested")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session, quiescence=0.5)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session, quiescence=0.5)
    keyboard.press_chord([keyboard.KEYSYM_ALT_L], keyboard.KEYSYM_UP)
    spoken, brailled = capture(session, quiescence=0.5)
    assert spoken == ["02 Nested \u2014 Dolphin", "Child", ", Folder"]
    assert brailled[-1] == _item_braille(session, "Child", "02 Nested")
