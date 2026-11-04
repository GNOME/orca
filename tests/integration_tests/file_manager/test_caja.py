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

"""Tests navigation, selection, and review in Caja's icon and list views."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests.file_manager_helpers import LONG_NAME, start_at_first_file
from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine, bound_pan_keys, capture, toggle_flat_review

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import FileManagerSession


def _item_braille(
    session: FileManagerSession, name: str, folder: str = "Test Files"
) -> BrailleLine:
    """Builds the expected braille for a file or folder."""

    is_folder = not name.endswith(".txt")
    if session.view == "icon":
        label = name + (" Folder" if is_folder else " Plain text document")
        full = (
            f"caja application {folder} frame vertical splitter vertical splitter "
            "page tab list page tab Icon View layered pane " + label
        )
    else:
        label = name + (" collapsed" if is_folder else "") + " TREE LEVEL 1"
        full = " Name column header " + label
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
    is_folder = not name.endswith(".txt")
    if session.view == "icon":
        expected = [name + (" Folder" if is_folder else " Plain text document")]
    else:
        expected = [name + (" collapsed" if is_folder else "")]
        if unselected:
            expected.append("not selected")
    assert spoken == expected
    assert brailled[-1] == _item_braille(session, name, folder)


def _assert_return(session: FileManagerSession, name: str) -> None:
    spoken, brailled = capture(session, quiescence=0.5)
    if session.view == "icon":
        assert spoken == ["page tab", "Icon View", name + " Folder"]
        assert brailled[-1] == _item_braille(session, name)
    else:
        assert spoken == ["Test Files"]
        assert brailled[-1] == BrailleLine(0, "Test Files", "Test Files", "\x00" * 10)


def _assert_message(session: FileManagerSession, message: str) -> None:
    spoken, brailled = capture(session)
    assert spoken == [message]
    assert brailled[-1] == BrailleLine(0, message, message, "\x00" * len(message))


@pytest.mark.native_app
@pytest.mark.parametrize("control", [False, True])
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_arrow_navigation(caja: FileManagerSession, control: bool) -> None:
    """Checks file announcements after arrow and Ctrl+arrow keys."""

    session = caja
    start_at_first_file(session)
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
@pytest.mark.parametrize("caja", ["icon"], indirect=True)
def test_icon_row_boundary(caja: FileManagerSession) -> None:
    """Checks Right into the next icon row and Left back into the previous row."""

    session = caja
    start_at_first_file(session)
    names = ["02 Nested", "03 Scrolling", "alpha.txt", "bravo.txt"]
    names.append("charlie.txt")
    names.append("delta.txt")
    for name in names:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        _assert_item(session, name)
    for name in reversed(["01 Empty", *names[:-1]]):
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        _assert_item(session, name)


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_home_end_and_boundaries(caja: FileManagerSession) -> None:
    """Checks Home and End navigation, and pressing Up on the first item."""

    session = caja
    start_at_first_file(session)
    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == []
    assert all(line == _item_braille(session, "01 Empty") for line in brailled)
    keyboard.tap_key(keyboard.KEYSYM_END)
    _assert_item(session, LONG_NAME)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    _assert_item(session, "01 Empty")


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_control_space_selection(caja: FileManagerSession) -> None:
    """Adds a second selection, returns to the first, and removes the original selection."""

    session = caja
    start_at_first_file(session)
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


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_range_selection(caja: FileManagerSession) -> None:
    """Checks file announcements as Shift+arrows extend and shrink a selection."""

    session = caja
    start_at_first_file(session)
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
@pytest.mark.parametrize("caja", ["icon"], indirect=True)
def test_selection_reporting(caja: FileManagerSession) -> None:
    """Reports both the selected count and the selected filenames."""

    session = caja
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for _ in range(2):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
        capture(session)
    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    spoken, brailled = capture(session)
    message = "3 of 14 items selected"
    assert spoken and spoken[0] == message
    assert brailled and brailled[-1] == BrailleLine(0, message, message, "\x00" * len(message))
    assert sorted(spoken[1].split(",")) == ["01 Empty", "02 Nested", "03 Scrolling"]


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_scrolling_and_return(caja: FileManagerSession) -> None:
    """Checks offscreen files, reverse movement, and returning to their parent folder."""

    session = caja
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for name in ("02 Nested", "03 Scrolling"):
        keyboard.tap_key(forward)
        _assert_item(session, name)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session, quiescence=0.5)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    _assert_item(session, "item 60.txt", folder="03 Scrolling")
    stride = 6 if session.view == "icon" else 1
    indices = list(range(60 - stride, max(0, 60 - 31 * stride), -stride))
    for key, numbers in (
        (keyboard.KEYSYM_UP, indices),
        (keyboard.KEYSYM_DOWN, list(reversed([60, *indices[:-1]]))),
    ):
        for index in numbers:
            name = f"item {index:02}.txt"
            keyboard.tap_key(key)
            _assert_item(session, name, folder="03 Scrolling")
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    _assert_item(session, "item 01.txt", folder="03 Scrolling")
    keyboard.press_chord([keyboard.KEYSYM_ALT_L], keyboard.KEYSYM_LEFT)
    _assert_return(session, "03 Scrolling")


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_braille_panning(caja: FileManagerSession) -> None:
    """Checks braille while panning a long filename forward and back."""

    session = caja
    start_at_first_file(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    _assert_item(session, LONG_NAME)
    original = _item_braille(session, LONG_NAME)
    with bound_pan_keys(session) as (left, right):
        for key, cursor, visible in (
            (right, 0, "braille panning and file navigat"),
            (
                right,
                0,
                "navigation.txt Plain text docume"
                if session.view == "icon"
                else "navigation.txt TREE LEVEL 1",
            ),
            (left, 0, "braille panning and file navigat"),
            (left, 1, "long filename for testing braill"),
        ):
            session.orca.press_bound_key(key)
            spoken, brailled = capture(session)
            assert spoken == []
            assert brailled[-1] == BrailleLine(cursor, original.full, visible, original.mask)


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_where_am_i(caja: FileManagerSession) -> None:
    """Checks Where Am I after selecting three items."""

    session = caja
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for _ in range(2):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
        capture(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    if session.view == "icon":
        assert spoken[:3] == [
            "Icon panel.",
            "03 Scrolling Folder",
            "3 of 14 items selected on 3 of 14",
        ]
        assert sorted(spoken[3:]) == ["01 Empty", "02 Nested", "03 Scrolling"]
    else:
        assert spoken == [
            "Name 03 Scrolling collapsed",
            "tree level 1",
            "column 1 of 1 row 3 of 14",
        ]
    assert brailled[-1] == _item_braille(session, "03 Scrolling")


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_flat_review(caja: FileManagerSession) -> None:
    """Reviews the focused file's screen line and moves forward and back."""

    session = caja
    start_at_first_file(session)
    toggle_flat_review(session)
    first = (
        "01 Empty 02 Nested 03 Scrolling alpha.txt bravo.txt charlie.txt"
        if session.view == "icon"
        else "01 Empty"
    )
    second = (
        "delta.txt echo.txt file with spaces.txt golf.txt hotel.txt india.txt"
        if session.view == "icon"
        else "02 Nested"
    )
    expectations = [
        (keyboard.KEYSYM_KP_UP, first, first + " $l", 1),
        (keyboard.KEYSYM_KP_PAGE_UP, second, second + " $l", 1),
        (keyboard.KEYSYM_KP_HOME, first, first + " $l", 1),
    ]
    for key, spoken_expected, full, cursor in expectations:
        keyboard.tap_key(key)
        spoken, brailled = capture(session)
        assert spoken == [spoken_expected]
        assert brailled[-1] == BrailleLine(cursor, full, full[:32], "\x00" * len(full))


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon", "list"], indirect=True)
def test_space_behavior(caja: FileManagerSession) -> None:
    """Checks Space opening the selected folder, including when another item has focus."""

    session = caja
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for unselected in (False, True):
        start_at_first_file(session)
        if unselected:
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
            _assert_item(session, "02 Nested", unselected=True)
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        _assert_message(session, "01 Empty")
        keyboard.press_chord([keyboard.KEYSYM_ALT_L], keyboard.KEYSYM_LEFT)
        capture(session, quiescence=0.5)


@pytest.mark.native_app
@pytest.mark.parametrize("caja", ["icon"], indirect=True)
def test_return_to_parent(caja: FileManagerSession) -> None:
    """Checks the Child folder announcement after returning with Alt+Up."""

    session = caja
    start_at_first_file(session)
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
    spoken, brailled = capture(session)
    assert spoken == ["page tab", "Icon View", "Child Folder"]
    assert brailled[-1] == _item_braille(session, "Child", "02 Nested")
