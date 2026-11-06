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

"""Tests navigation, selection, and review in Nautilus's icon and list views."""

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

    label = name + (". File" if name.endswith(".txt") else ". Folder")
    if session.view == "icon":
        full = label
    else:
        label += " table row"
        full = (
            f"org.gnome.Nautilus application {folder} frame {folder} panel "
            "Content View tree table list " + label
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
    expected = [name + (". File" if name.endswith(".txt") else ". Folder")]
    if unselected and session.view == "icon":
        expected.append("not selected")
    assert spoken == expected
    assert brailled[-1] == _item_braille(session, name, folder)


def _assert_message(session: FileManagerSession, message: str) -> None:
    spoken, brailled = capture(session)
    assert spoken == [message]
    assert brailled[-1] == BrailleLine(0, message, message, "\x00" * len(message))


@pytest.mark.native_app
@pytest.mark.parametrize("control", [False, True])
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_arrow_navigation(nautilus: FileManagerSession, control: bool) -> None:
    """Checks file announcements after arrow and Ctrl+arrow keys."""

    session = nautilus
    start_at_first_file(session)
    modifiers = [keyboard.KEYSYM_CONTROL_L] if control else []
    if session.view == "icon":
        moves = [
            (keyboard.KEYSYM_RIGHT, "02 Nested"),
            (keyboard.KEYSYM_DOWN, "delta.txt"),
            (keyboard.KEYSYM_LEFT, "charlie.txt"),
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
@pytest.mark.parametrize("nautilus", ["icon"], indirect=True)
def test_icon_row_boundary(nautilus: FileManagerSession) -> None:
    """Checks Right into the next icon row and Left back into the previous row."""

    session = nautilus
    start_at_first_file(session)
    names = ["02 Nested", "03 Scrolling", "alpha.txt", "bravo.txt"]
    names.append("charlie.txt")
    for name in names:
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        _assert_item(session, name)
    for name in reversed(["01 Empty", *names[:-1]]):
        keyboard.tap_key(keyboard.KEYSYM_LEFT)
        _assert_item(session, name)


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon"], indirect=True)
def test_home_end_and_boundaries(nautilus: FileManagerSession) -> None:
    """Checks Home and End navigation, and pressing Up on the first item."""

    session = nautilus
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
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_control_space_selection(nautilus: FileManagerSession) -> None:
    """Adds a second selection, returns to the first, and removes both selections."""

    session = nautilus
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
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
    _assert_item(session, "02 Nested")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
    _assert_message(session, "unselected")


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_range_selection(nautilus: FileManagerSession) -> None:
    """Checks file announcements as Shift+arrows extend and shrink a selection."""

    session = nautilus
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
@pytest.mark.parametrize(
    "nautilus",
    [
        "icon",
        pytest.param(
            "list",
            marks=pytest.mark.xfail(
                strict=False,
                raises=AssertionError,
                reason="Intermittent missing name: https://gitlab.gnome.org/GNOME/gtk/-/work_items/8530",
            ),
        ),
    ],
    indirect=True,
)
def test_selection_reporting(nautilus: FileManagerSession) -> None:
    """Reports selected files in folder order as the selection shrinks and grows."""

    session = nautilus
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    backward = keyboard.KEYSYM_LEFT if session.view == "icon" else keyboard.KEYSYM_UP
    for _ in range(2):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
        capture(session)
    names = ["01 Empty. Folder", "02 Nested. Folder", "03 Scrolling. Folder"]
    for key, count in ((None, 3), (backward, 2), (forward, 3)):
        if key is not None:
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], key)
            capture(session)
        session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
        spoken, brailled = capture(session)
        message = f"{count} of 14 items selected"
        assert spoken == [message, ",".join(names[:count])]
        assert brailled and brailled[-1] == BrailleLine(0, message, message, "\x00" * len(message))


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon"], indirect=True)
def test_braille_panning(nautilus: FileManagerSession) -> None:
    """Checks braille while panning a long filename forward and back."""

    session = nautilus
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
                "navigation.txt. File"
                if session.view == "icon"
                else "navigation.txt. File table row",
            ),
            (left, 0, "braille panning and file navigat"),
            (left, 1, "long filename for testing braill"),
        ):
            session.orca.press_bound_key(key)
            spoken, brailled = capture(session)
            assert spoken == []
            assert brailled[-1] == BrailleLine(cursor, original.full, visible, original.mask)


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_where_am_i(nautilus: FileManagerSession) -> None:
    """Checks Where Am I after selecting three items."""

    session = nautilus
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for _ in range(2):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
        capture(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == ["03 Scrolling. Folder"]
    assert brailled[-1] == _item_braille(session, "03 Scrolling")


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_flat_review(nautilus: FileManagerSession) -> None:
    """Reviews the focused file's screen line and moves forward and back."""

    session = nautilus
    start_at_first_file(session)
    toggle_flat_review(session)
    first = (
        "01 Empty. Folder 02 Nested. Folder 03 Scrolling. Folder alpha.txt. File bravo.txt. File"
        if session.view == "icon"
        else "table row 01 Empty Star"
    )
    full = first + " $l"
    expectations = [
        (keyboard.KEYSYM_KP_UP, first, full, 1),
        (
            keyboard.KEYSYM_KP_RIGHT,
            "Empty." if session.view == "icon" else "row",
            full,
            4 if session.view == "icon" else 7,
        ),
        (keyboard.KEYSYM_KP_LEFT, "01" if session.view == "icon" else "table", full, 1),
    ]
    for key, spoken_expected, full, cursor in expectations:
        keyboard.tap_key(key)
        spoken, brailled = capture(session)
        assert "".join(spoken).strip() == spoken_expected
        assert brailled[-1] == BrailleLine(cursor, full, full[:32], "\x00" * len(full))


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_space_behavior(nautilus: FileManagerSession) -> None:
    """Checks that repeated Space presses produce no speech or changed braille."""

    session = nautilus
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    for unselected in (False, True):
        name = "01 Empty"
        if unselected:
            name = "02 Nested"
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
            _assert_item(session, name, unselected=True)
        for _ in range(2):
            keyboard.tap_key(keyboard.KEYSYM_SPACE)
            spoken, brailled = capture(session)
            assert spoken == []
            assert all(line == _item_braille(session, name) for line in brailled)


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
@pytest.mark.parametrize("parent", ["02 Nested", "Sibling"], ids=["two-items", "one-item"])
def test_return_to_parent(nautilus: FileManagerSession, parent: str) -> None:
    """Checks the Child folder announcement after returning with Alt+Up."""

    session = nautilus
    start_at_first_file(session)
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    keyboard.tap_key(forward)
    _assert_item(session, "02 Nested")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session, quiescence=0.5)
    if parent == "Sibling":
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(session)
        keyboard.tap_key(keyboard.KEYSYM_RETURN)
        capture(session, quiescence=0.5)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    capture(session, quiescence=0.5)
    keyboard.press_chord([keyboard.KEYSYM_ALT_L], keyboard.KEYSYM_UP)
    _assert_item(session, "Child", folder=parent)


@pytest.mark.native_app
@pytest.mark.parametrize(
    "nautilus",
    [
        "icon",
        # TODO: Investigate the missing Select All announcement in list view.
        pytest.param(
            "list",
            marks=pytest.mark.xfail(
                reason="Select All is not announced in Nautilus list view",
                raises=AssertionError,
                strict=True,
            ),
        ),
    ],
    indirect=True,
)
def test_select_all(nautilus: FileManagerSession) -> None:
    """Selects all files, toggles one selection, and resumes navigation."""

    session = nautilus
    start_at_first_file(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    _assert_message(session, "all items selected")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    spoken, brailled = capture(session)
    assert spoken == []
    if session.view == "icon":
        assert brailled[-1] == _item_braille(session, "01 Empty")
    else:
        assert brailled == []
    forward = keyboard.KEYSYM_RIGHT if session.view == "icon" else keyboard.KEYSYM_DOWN
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], forward)
    _assert_item(session, "02 Nested")
    for message in ("unselected", "selected"):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
        _assert_message(session, message)
    keyboard.tap_key(keyboard.KEYSYM_HOME)
    _assert_item(session, "01 Empty")
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], forward)
    _assert_item(session, "02 Nested")


@pytest.mark.native_app
@pytest.mark.parametrize("nautilus", ["icon", "list"], indirect=True)
def test_range_to_all_files(nautilus: FileManagerSession) -> None:
    """Selects every file with Shift+End, then shrinks the selection with Shift+Home."""

    session = nautilus
    start_at_first_file(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    _assert_item(session, LONG_NAME)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    _assert_item(session, "01 Empty")
