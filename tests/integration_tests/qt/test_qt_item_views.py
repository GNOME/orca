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

"""Tests list, table, and tree navigation and selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.apps import qt
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _prepare(session: NativeAppSession, view: str = "list") -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
    keyboard.tap_key(keyboard.KEYSYM_F12)
    helpers.capture(session)
    if view == "table":
        helpers.tab_and_swallow_presentation(session)
    if view == "tree":
        for _ in range(2):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
            helpers.capture(session)


def _assert_item(session: NativeAppSession, name: str) -> None:
    spoken, brailled = helpers.capture(session)
    assert spoken == [name]
    assert brailled
    assert brailled[-1].visible == name


@pytest.mark.native_app
def test_list_navigation(qt_item_views: NativeAppSession) -> None:
    """Reads list items when arrowing and moving to the first and last items."""

    session = qt_item_views
    _prepare(session)
    for key, name in (
        (keyboard.KEYSYM_DOWN, "Olives"),
        (keyboard.KEYSYM_UP, "Cheese"),
        (keyboard.KEYSYM_END, "Onions"),
        (keyboard.KEYSYM_HOME, "Cheese"),
    ):
        keyboard.tap_key(key)
        _assert_item(session, name)


@pytest.mark.native_app
def test_list_selection(qt_item_views: NativeAppSession) -> None:
    """Announces selection and deselection of the focused item."""

    session = qt_item_views
    _prepare(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    _assert_item(session, "Olives")
    for state in ("unselected", "selected"):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_SPACE)
        spoken, brailled = helpers.capture(session)
        assert (spoken, brailled[-1:]) == (
            [state],
            [helpers.BrailleLine(0, state, state, "\x00" * len(state))],
        )


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5's AT-SPI adaptor lacks Selection on QListWidget",
    strict=True,
    raises=AssertionError,
)
def test_list_select_all(qt_item_views: NativeAppSession) -> None:
    """Announces that all four list items have been selected."""

    session = qt_item_views
    _prepare(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    assert helpers.capture(session) == (
        ["all items selected"],
        [helpers.BrailleLine(0, "all items selected", "all items selected", "\x00" * 18)],
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5's AT-SPI adaptor lacks Selection on QListWidget",
    strict=True,
    raises=AssertionError,
)
def test_present_selected_list_items(qt_item_views: NativeAppSession) -> None:
    """Reports the names of selected list items in their displayed order."""

    session = qt_item_views
    _prepare(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    spoken, _ = helpers.capture(session)
    assert spoken == ["2 of 4 items selected", "Cheese,Olives"]


@pytest.mark.native_app
def test_table_rows(qt_item_views: NativeAppSession) -> None:
    """Reads all visible columns when moving between table rows."""

    session = qt_item_views
    _prepare(session, "table")
    for key, row in (
        (keyboard.KEYSYM_DOWN, ("Grace", "Admiral", "Boston")),
        (keyboard.KEYSYM_DOWN, ("Alan", "Analyst", "Manchester")),
        (keyboard.KEYSYM_UP, ("Grace", "Admiral", "Boston")),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken[:3] == list(row)
        assert brailled
        for value in row:
            assert value in brailled[-1].full


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5's QTableWidget lacks AT-SPI Selection to identify its focused cell",
    strict=True,
    raises=AssertionError,
)
def test_table_cells(qt_item_views: NativeAppSession) -> None:
    """Reads cell values and column headers when moving horizontally."""

    session = qt_item_views
    _prepare(session, "table")
    for key, header, value in (
        (keyboard.KEYSYM_RIGHT, "Role", "Engineer"),
        (keyboard.KEYSYM_RIGHT, "Office", "London"),
        (keyboard.KEYSYM_LEFT, "Role", "Engineer"),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == [f"{header} column header {value}"]
        assert brailled[-1].visible == value


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5's QTableWidget lacks AT-SPI Selection to identify its focused cell",
    strict=True,
    raises=AssertionError,
)
def test_table_cell_reading_mode(qt_item_views: NativeAppSession) -> None:
    """Reads only the focused cell after switching to cell-reading mode."""

    session = qt_item_views
    _prepare(session, "table")
    session.orca.call("SpeechPresenter", "ToggleTableCellReadingMode", True)
    assert helpers.speech(session) == ["Speak cell"]
    try:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["2 row header Grace"]
        assert brailled[-1].visible == "Grace"
    finally:
        session.orca.call("SpeechPresenter", "ToggleTableCellReadingMode", True)
        helpers.capture(session)


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=("Qt does not identify QTreeView's focused cell in a focus or active-descendant event"),
    strict=True,
    raises=AssertionError,
)
@pytest.mark.parametrize("return_to_tree", [False, True], ids=["entry", "return"])
@pytest.mark.parametrize("item_count", [1, 2], ids=["one-item", "two-items"])
def test_tree_focus(qt_item_views: NativeAppSession, return_to_tree: bool, item_count: int) -> None:
    """Reads the focused tree item on entry and after tabbing away and back."""

    session = qt_item_views
    _prepare(session, "tree")
    if item_count == 1:
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    if return_to_tree:
        helpers.capture(session)
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        helpers.capture(session)
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert "Readme.txt" in " ".join(spoken)
    assert brailled and "Readme.txt" in brailled[-1].full


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5 lacks AT-SPI Selection to identify the selected QTreeView item on focus return",
    strict=True,
    raises=AssertionError,
)
def test_tree_focus_after_navigation(qt_item_views: NativeAppSession) -> None:
    """Reads the selected tree item when returning after arrow navigation."""

    session = qt_item_views
    _prepare(session, "tree")
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    helpers.capture(session)
    for key, name in ((keyboard.KEYSYM_DOWN, "Notes.txt"), (keyboard.KEYSYM_UP, "Readme.txt")):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == [name, "Complete"]
        assert brailled and name in brailled[-1].full
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Readme.txt"]
    assert brailled and "Readme.txt" in brailled[-1].full


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt emits no AT-SPI expanded state-change event when a QTreeWidget item expands: "
        "https://qt-project.atlassian.net/browse/QTBUG-152408"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tree_expansion(qt_item_views: NativeAppSession) -> None:
    """Announces a tree item's expansion and collapse."""

    session = qt_item_views
    _prepare(session, "tree")
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["expanded", "2 items"]
    assert brailled and "expanded" in brailled[-1].full
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["collapsed"]
    assert brailled and "collapsed" in brailled[-1].full


@pytest.mark.native_app
def test_tree_navigation(qt_item_views: NativeAppSession) -> None:
    """Reads child items and returns to their parent with Left."""

    session = qt_item_views
    _prepare(session, "tree")
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    for key, name in ((keyboard.KEYSYM_DOWN, "Report"), (keyboard.KEYSYM_DOWN, "Notes")):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert name in spoken
        assert brailled and name in brailled[-1].full
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Work expanded"]
    assert brailled and "Work" in brailled[-1].full
