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

"""Tests control presentation and keyboard navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.apps import qt
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _prepare(session: NativeAppSession, tabs: int = 0) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
    keyboard.tap_key(keyboard.KEYSYM_F12)
    helpers.capture(session)
    for _ in range(tabs):
        helpers.tab_and_swallow_presentation(session)


def _assert(session: NativeAppSession, spoken: list[str], braille: str, cursor: int = 1) -> None:
    actual, lines = helpers.capture(session)
    assert actual == spoken
    assert lines[-1] == helpers.BrailleLine(cursor, braille, braille, "\x00" * len(braille))


@pytest.mark.native_app
@pytest.mark.parametrize(
    "tabs, spoken, braille, cursor",
    [
        (1, ["Bold check box not checked"], "< > Bold check box", 1),
        (2, ["Enabled check box not checked"], "< > Enabled check box", 1),
        (4, ["Color Red combo box", "down"], "Color Red combo box down", 7),
        (6, ["Small selected radio button"], "&=y Small radio button", 1),
        pytest.param(
            7,
            ["Level horizontal slider 3 30 percent."],
            "Level 3 horizontal slider",
            1,
            marks=pytest.mark.xfail(
                qt.is_qt5(),
                reason="Qt5 omits the AT-SPI HORIZONTAL state on QSlider",
                strict=True,
                raises=AssertionError,
            ),
        ),
        (8, ["Bump Quantity in 1000 ms button"], "Bump Quantity in 1000 ms button", 1),
        (10, ["Include archived check box not checked"], "< > Include archived check box", 1),
        pytest.param(
            11,
            ["Widgets page tab"],
            "Widgets page tab",
            1,
            marks=pytest.mark.xfail(
                qt.is_qt5(),
                reason="Qt5's QTabBar lacks AT-SPI Selection and its tabs lack the SELECTED state",
                strict=True,
                raises=AssertionError,
            ),
        ),
    ],
)
def test_tab_navigation(
    qt_widget_notebook: NativeAppSession, tabs, spoken, braille, cursor
) -> None:
    """Announces each control reached with Tab."""

    session = qt_widget_notebook
    _prepare(session, tabs - 1)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    _assert(session, spoken, braille, cursor)


@pytest.mark.native_app
@pytest.mark.parametrize("tabs", [1, 2], ids=["toggle", "check"])
def test_button_state_changes(qt_widget_notebook: NativeAppSession, tabs: int) -> None:
    """Presents both states when a button is toggled with Space."""

    session = qt_widget_notebook
    _prepare(session, tabs)
    states = (
        [("checked", "<x> Bold check box"), ("not checked", "< > Bold check box")]
        if tabs == 1
        else [("checked", "<x> Enabled check box"), ("not checked", "< > Enabled check box")]
    )
    for spoken, braille in states:
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        _assert(session, [spoken], braille)


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt's AT-SPI adaptor omits indeterminate state-change events for QCheckBox: "
        "https://qt-project.atlassian.net/browse/QTBUG-152406"
    ),
    strict=True,
    raises=AssertionError,
)
def test_tri_state_checkbox(qt_widget_notebook: NativeAppSession) -> None:
    """Presents partially checked, checked, and unchecked states."""

    session = qt_widget_notebook
    _prepare(session, 10)
    for state, marker in (("partially checked", "<->"), ("checked", "<x>"), ("not checked", "< >")):
        keyboard.tap_key(keyboard.KEYSYM_SPACE)
        _assert(session, [state], f"{marker} Include archived check box")


@pytest.mark.native_app
def test_combo_box_collapsed(qt_widget_notebook: NativeAppSession) -> None:
    """Announces the value while arrowing a collapsed combo box."""

    session = qt_widget_notebook
    _prepare(session, 4)
    for key, value in (
        (keyboard.KEYSYM_DOWN, "Green"),
        (keyboard.KEYSYM_DOWN, "Blue"),
        (keyboard.KEYSYM_UP, "Green"),
    ):
        keyboard.tap_key(key)
        _assert(session, [value], f"Color {value} combo box down", 7)


@pytest.mark.native_app
def test_combo_box_popup(qt_widget_notebook: NativeAppSession) -> None:
    """Opens the choices, selects the next color, and closes the popup."""

    session = qt_widget_notebook
    _prepare(session, 4)
    keyboard.press_chord([keyboard.KEYSYM_ALT_L], keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Green"]
    assert brailled[-1].visible == "Green"
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    _assert(session, ["Color Green combo box", "down"], "Color Green combo box down", 7)


@pytest.mark.native_app
def test_radio_buttons(qt_widget_notebook: NativeAppSession) -> None:
    """Announces the selected radio button in both directions."""

    session = qt_widget_notebook
    _prepare(session, 6)
    for key, label in (
        (keyboard.KEYSYM_DOWN, "Medium"),
        (keyboard.KEYSYM_DOWN, "Large"),
        (keyboard.KEYSYM_UP, "Medium"),
    ):
        keyboard.tap_key(key)
        _assert(session, [f"{label} selected radio button"], f"&=y {label} radio button")


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5 omits the AT-SPI HORIZONTAL state on QSlider",
    strict=True,
    raises=AssertionError,
)
def test_slider(qt_widget_notebook: NativeAppSession) -> None:
    """Announces slider values and endpoints."""

    session = qt_widget_notebook
    _prepare(session, 7)
    for key, value in (
        (keyboard.KEYSYM_RIGHT, 4),
        (keyboard.KEYSYM_LEFT, 3),
        (keyboard.KEYSYM_END, 10),
        (keyboard.KEYSYM_HOME, 0),
    ):
        keyboard.tap_key(key)
        _assert(session, [str(value)], f"Level {value} horizontal slider")


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5 omits the AT-SPI EDITABLE state on QSpinBox",
    strict=True,
    raises=AssertionError,
)
def test_spin_button(qt_widget_notebook: NativeAppSession) -> None:
    """Announces changes to a spin button's value."""

    session = qt_widget_notebook
    _prepare(session, 3)
    for key, value in ((keyboard.KEYSYM_UP, 76), (keyboard.KEYSYM_DOWN, 75)):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == [str(value)]
        assert brailled[-1].visible == f"Quantity {value} $l"


@pytest.mark.native_app
def test_tab_bar(qt_widget_notebook: NativeAppSession) -> None:
    """Announces page tabs when moving forward and backward."""

    session = qt_widget_notebook
    _prepare(session, 11)
    for key, page in (
        (keyboard.KEYSYM_RIGHT, "Messages"),
        (keyboard.KEYSYM_RIGHT, "Labels"),
        (keyboard.KEYSYM_LEFT, "Messages"),
    ):
        keyboard.tap_key(key)
        _assert(session, [f"{page} page tab"], f"{page} page tab")


@pytest.mark.native_app
def test_description(qt_widget_notebook: NativeAppSession) -> None:
    """Presents the focused entry's description."""

    session = qt_widget_notebook
    _prepare(session, 11)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Filter text", "3 matches found"]
    assert brailled
    line = brailled[-1]
    assert line.full == line.visible == "Filter  $l 3 matches found"
    assert line.cursor_cell == 8
    assert not any(ord(cell) for cell in line.mask or "")


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5 omits the AT-SPI HORIZONTAL state on QSlider",
    strict=True,
    raises=AssertionError,
)
def test_label_for(qt_widget_notebook: NativeAppSession) -> None:
    """Uses the associated label as the slider's name."""

    session = qt_widget_notebook
    _prepare(session, 11)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    _assert(
        session,
        ["Volume horizontal slider 0 0 percent.", "Alt+V"],
        "Volume 0 horizontal slider Alt+V",
    )


@pytest.mark.native_app
def test_status_bar(qt_widget_notebook: NativeAppSession) -> None:
    """Reads the status bar on request."""

    session = qt_widget_notebook
    _prepare(session)
    session.orca.call("WhereAmIPresenter", "PresentStatusBar", True)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Ready. 3 items. status bar"]
    assert brailled[-1].visible == "Ready. 3 items. status bar"


@pytest.mark.native_app
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5 omits the AT-SPI READ_ONLY state on QSpinBox",
    strict=True,
    raises=AssertionError,
)
def test_readonly_spin_button(qt_widget_notebook: NativeAppSession) -> None:
    """Identifies a read-only spin button when it receives focus."""

    session = qt_widget_notebook
    _prepare(session, 8)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Readonly spin button 25"],
        [
            helpers.BrailleLine(
                10,
                "Readonly 25 rdonly",
                "Readonly 25 rdonly",
                "\x00" * 9 + "\xc0" * 2 + "\x00" * 7,
            )
        ],
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    reason="Qt menus sometimes close after Alt+F when an AT-SPI keyboard watcher is active",
    strict=False,
    raises=AssertionError,
)
def test_menu_navigation(qt_widget_notebook: NativeAppSession) -> None:
    """Navigates menu items and a submenu using arrow keys."""

    session = qt_widget_notebook
    _prepare(session)
    keyboard.press_chord([keyboard.KEYSYM_ALT_L], ord("f"))
    spoken, brailled = helpers.capture(session)
    assert "New" in spoken
    assert brailled and "New" in brailled[-1].full
    for key, name in (
        (keyboard.KEYSYM_DOWN, "Open"),
        (keyboard.KEYSYM_DOWN, "Recent"),
        (keyboard.KEYSYM_RIGHT, "Report"),
        (keyboard.KEYSYM_DOWN, "Summary"),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert any(name in phrase for phrase in spoken)
        assert brailled and name in brailled[-1].full
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    helpers.capture(session)
