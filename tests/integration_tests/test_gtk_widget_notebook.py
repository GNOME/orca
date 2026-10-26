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

"""Tests GTK widget roles, notebook navigation, and static-text techniques.

One session-scoped notebook app covers it all: an F12 reset restores widget state and
focus between tests, and braille ancestors are disabled so the widget lines do not
carry the notebook scaffolding.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import gtk
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _prepare(session: NativeAppSession) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
    keyboard.tap_key(keyboard.KEYSYM_F12)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _tab_to(session: NativeAppSession, count: int) -> None:
    for _ in range(count):
        helpers.tab_and_swallow_presentation(session)


def _press(session: NativeAppSession, keysym: int) -> tuple[list[str], list[helpers.BrailleLine]]:
    keyboard.tap_key(keysym)
    return helpers.capture(session)


@pytest.mark.native_app
@pytest.mark.parametrize(
    "count, expected",
    [
        pytest.param(
            1,
            (
                ["Bold toggle button not pressed"],
                [
                    helpers.BrailleLine(
                        1, "& y Bold toggle button", "& y Bold toggle button", "\x00" * 22
                    )
                ],
            ),
            id="toggle",
        ),
        pytest.param(
            2,
            (
                ["Enabled check box not checked"],
                [
                    helpers.BrailleLine(
                        1, "< > Enabled check box", "< > Enabled check box", "\x00" * 21
                    )
                ],
            ),
            id="check",
        ),
        pytest.param(
            3,
            (
                ["Quantity spin button", "75"],
                [
                    helpers.BrailleLine(
                        12, "Quantity 75 $l", "Quantity 75 $l", "\x00" * 9 + "\xc0\xc0" + "\x00" * 3
                    )
                ],
            ),
            id="spin",
        ),
        pytest.param(
            4,
            (
                ["Color combo box Red"],
                [helpers.BrailleLine(7, "Color Red combo box", "Color Red combo box", "\x00" * 19)],
            ),
            id="color",
            marks=pytest.mark.skipif(
                gtk.is_gtk4(), reason="DropDown coverage is on hold pending production fixes"
            ),
        ),
        pytest.param(
            5,
            helpers.expected_for_gtk(
                (
                    ["City text", "Madrid", "selected"],
                    [
                        helpers.BrailleLine(
                            12,
                            "City Madrid $l",
                            "City Madrid $l",
                            "\x00" * 5 + "\xc0" * 6 + "\x00" * 3,
                        )
                    ],
                ),
                gtk4=(
                    ["City text", "Madrid", "selected", "opens popup"],
                    [
                        helpers.BrailleLine(
                            12,
                            "City Madrid $l",
                            "City Madrid $l",
                            "\x00" * 5 + "\xc0" * 6 + "\x00" * 3,
                        )
                    ],
                ),
            ),
            id="entry",
        ),
        pytest.param(
            6,
            helpers.expected_for_gtk(
                (
                    ["Website button"],
                    [helpers.BrailleLine(1, "Website button", "Website button", "\x00" * 14)],
                ),
                gtk4=(["Website link"], [helpers.BrailleLine(1, "Website", "Website", "\xc0" * 7)]),
            ),
            id="link",
        ),
        pytest.param(
            7,
            helpers.expected_for_gtk(
                (
                    ["Small selected radio button"],
                    [
                        helpers.BrailleLine(
                            1, "&=y Small radio button", "&=y Small radio button", "\x00" * 22
                        )
                    ],
                ),
                gtk4=(
                    ["Widgets Page 1", "Small selected radio button"],
                    [
                        helpers.BrailleLine(
                            1,
                            "Widgets Page 1 &=y Small radio button",
                            "&=y Small radio button",
                            "\x00" * 37,
                        )
                    ],
                ),
            ),
            id="radio",
        ),
        pytest.param(
            8,
            (
                ["Level horizontal slider 3 30 percent."],
                [
                    helpers.BrailleLine(
                        1, "Level 3 horizontal slider", "Level 3 horizontal slider", "\x00" * 25
                    )
                ],
            ),
            id="scale",
        ),
        pytest.param(
            9,
            (
                ["Bump Quantity in 1000 ms button"],
                [
                    helpers.BrailleLine(
                        1,
                        "Bump Quantity in 1000 ms button",
                        "Bump Quantity in 1000 ms button",
                        "\x00" * 31,
                    )
                ],
            ),
            id="button",
        ),
        pytest.param(
            10,
            helpers.expected_for_gtk(
                (
                    ["Readonly spin button 25"],
                    [helpers.BrailleLine(10, "Readonly 25", "Readonly 25", "\x00" * 11)],
                ),
                gtk4=(
                    ["Readonly spin button", "25"],
                    [helpers.BrailleLine(10, "Readonly 25 $l", "Readonly 25 $l", "\x00" * 14)],
                ),
            ),
            id="readonly",
        ),
        pytest.param(
            11,
            (
                ["Widgets page tab"],
                [helpers.BrailleLine(1, "Widgets page tab", "Widgets page tab", "\x00" * 16)],
            ),
            id="page-tab",
            marks=pytest.mark.xfail(
                gtk.is_gtk4(),
                reason="GTK4 notebook focus reports the grouping instead of the active page tab",
                strict=True,
                raises=AssertionError,
            ),
        ),
        pytest.param(
            12,
            helpers.expected_for_gtk(
                (
                    ["Save button"],
                    [helpers.BrailleLine(1, "Save button", "Save button", "\x00" * 11)],
                ),
                gtk4=(
                    ["Widgets Page 1 panel", "Save button"],
                    [helpers.BrailleLine(1, "Save button", "Save button", "\x00" * 11)],
                ),
            ),
            id="wrap",
        ),
    ],
)
def test_tab_navigation_announces_each_widget_role(
    gtk_widget_notebook: NativeAppSession,
    count: int,
    expected: tuple[list[str], list[helpers.BrailleLine]],
) -> None:
    """Tests each Tab destination independently, including wrapping at the end."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, count - 1)
    assert _press(session, keyboard.KEYSYM_TAB) == expected


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="GTK4 popover menu does not restore keyboard focus after Escape",
)
def test_menu_bar_navigation(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests opening the menu bar and arrowing through its items, then closing it."""

    session = gtk_widget_notebook
    _prepare(session)

    assert _press(session, keyboard.KEYSYM_F10) == (
        ["File menu", "Alt+F"],
        [helpers.BrailleLine(1, "File menu Alt+F", "File menu Alt+F", "\x00" * 15)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["New", "N"],
        [helpers.BrailleLine(1, "New N", "New N", "\x00" * 5)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Open", "O"],
        [helpers.BrailleLine(1, "Open O", "Open O", "\x00" * 6)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Recent menu", "R"],
        [helpers.BrailleLine(1, "Recent menu R", "Recent menu R", "\x00" * 13)],
    )
    assert _press(session, keyboard.KEYSYM_RIGHT) == (
        ["Report", "R"],
        [helpers.BrailleLine(1, "Report R", "Report R", "\x00" * 8)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Summary", "S"],
        [helpers.BrailleLine(1, "Summary S", "Summary S", "\x00" * 9)],
    )
    assert _press(session, keyboard.KEYSYM_LEFT) == (
        ["Recent menu", "R"],
        [helpers.BrailleLine(1, "Recent menu R", "Recent menu R", "\x00" * 13)],
    )
    assert _press(session, keyboard.KEYSYM_ESCAPE) == (
        ["Widgets page tab", "Save button"],
        [helpers.BrailleLine(1, "Save button", "Save button", "\x00" * 11)],
    )


@pytest.mark.native_app
def test_toggle_button_state_changes(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that pressing Space on a toggle button announces the pressed state."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, 1)

    assert _press(session, keyboard.KEYSYM_SPACE) == (
        ["pressed"],
        [helpers.BrailleLine(1, "&=y Bold toggle button", "&=y Bold toggle button", "\x00" * 22)],
    )
    assert _press(session, keyboard.KEYSYM_SPACE) == (
        ["not pressed"],
        [helpers.BrailleLine(1, "& y Bold toggle button", "& y Bold toggle button", "\x00" * 22)],
    )


@pytest.mark.native_app
def test_check_button_state_changes(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that pressing Space on a check box announces the checked state."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, 2)

    assert _press(session, keyboard.KEYSYM_SPACE) == (
        ["checked"],
        [helpers.BrailleLine(1, "<x> Enabled check box", "<x> Enabled check box", "\x00" * 21)],
    )
    assert _press(session, keyboard.KEYSYM_SPACE) == (
        ["not checked"],
        [helpers.BrailleLine(1, "< > Enabled check box", "< > Enabled check box", "\x00" * 21)],
    )


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="GTK4 ComboBox accessibility: https://gitlab.gnome.org/GNOME/gtk/-/work_items/4978",
)
def test_combo_box_open_navigate_select(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests opening a combo box, arrowing to a new item, and selecting it."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, 4)

    keyboard.press_chord([keyboard.KEYSYM_ALT_L], keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Red"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Green"]
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    assert helpers.speech(session) == ["Color combo box Green"]


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="GTK4 ComboBox accessibility: https://gitlab.gnome.org/GNOME/gtk/-/work_items/4978",
)
def test_combo_box_arrow_navigation_while_collapsed(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests combo box arrow navigation while collapsed."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, 4)

    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Green"],
        [helpers.BrailleLine(7, "Color Green combo box", "Color Green combo box", "\x00" * 21)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Blue"],
        [helpers.BrailleLine(7, "Color Blue combo box", "Color Blue combo box", "\x00" * 20)],
    )
    assert _press(session, keyboard.KEYSYM_UP) == (
        ["Green"],
        [helpers.BrailleLine(7, "Color Green combo box", "Color Green combo box", "\x00" * 21)],
    )
    assert _press(session, keyboard.KEYSYM_TAB) == (
        ["City text", "Madrid", "selected"],
        [
            helpers.BrailleLine(
                12, "City Madrid $l", "City Madrid $l", "\x00" * 5 + "\xc0" * 6 + "\x00" * 3
            )
        ],
    )


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="GTK4 ComboBox accessibility: https://gitlab.gnome.org/GNOME/gtk/-/work_items/4978",
)
def test_position_in_set_when_arrowing_a_combo_box(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests position in set when arrowing a combo box."""

    session = gtk_widget_notebook
    _prepare(session)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    _tab_to(session, 4)

    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Green", "2 of 3"],
        [helpers.BrailleLine(7, "Color Green combo box", "Color Green combo box", "\x00" * 21)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["Blue", "3 of 3"],
        [helpers.BrailleLine(7, "Color Blue combo box", "Color Blue combo box", "\x00" * 20)],
    )


@pytest.mark.native_app
def test_position_in_set_when_arrowing_radio_buttons(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests position in set when arrowing radio buttons."""

    session = gtk_widget_notebook
    _prepare(session)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    _tab_to(session, 7)

    assert _press(session, keyboard.KEYSYM_DOWN) == helpers.expected_for_gtk(
        (
            ["Medium selected radio button", "2 of 3"],
            [
                helpers.BrailleLine(
                    1, "&=y Medium radio button", "&=y Medium radio button", "\x00" * 23
                )
            ],
        ),
        gtk4=(
            ["Widgets Page 1", "Medium selected radio button", "2 of 3"],
            [
                helpers.BrailleLine(
                    1,
                    "Widgets Page 1 &=y Medium radio button",
                    "&=y Medium radio button",
                    "\x00" * 38,
                )
            ],
        ),
    )
    assert _press(session, keyboard.KEYSYM_UP) == helpers.expected_for_gtk(
        (
            ["Small selected radio button", "1 of 3"],
            [
                helpers.BrailleLine(
                    1, "&=y Small radio button", "&=y Small radio button", "\x00" * 22
                )
            ],
        ),
        gtk4=(
            ["Widgets Page 1", "Small selected radio button", "1 of 3"],
            [
                helpers.BrailleLine(
                    1,
                    "Widgets Page 1 &=y Small radio button",
                    "&=y Small radio button",
                    "\x00" * 37,
                )
            ],
        ),
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.is_gtk4(),
    reason="GTK4 notebook tab navigation omits position in set and braille",
    strict=True,
    raises=AssertionError,
)
def test_position_in_set_when_arrowing_page_tabs(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests position in set when arrowing page tabs."""

    session = gtk_widget_notebook
    _prepare(session)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _press(session, keyboard.KEYSYM_RIGHT) == (
        ["Messages page tab", "2 of 5"],
        [helpers.BrailleLine(1, "Messages page tab", "Messages page tab", "\x00" * 17)],
    )
    assert _press(session, keyboard.KEYSYM_RIGHT) == (
        ["Labels page tab", "3 of 5"],
        [helpers.BrailleLine(1, "Labels page tab", "Labels page tab", "\x00" * 15)],
    )


@pytest.mark.native_app
def test_position_in_set_when_arrowing_a_list(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests position in set when arrowing a list."""

    session = gtk_widget_notebook
    _prepare(session)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _press(session, keyboard.KEYSYM_TAB) == (
        helpers.expected_for_gtk(
            ["List with 3 items", "report.pdf", "shared", "1 of 3"],
            gtk4=["Files Page 4", "List with 3 items", "report.pdf", "shared", "1 of 3"],
        ),
        [helpers.BrailleLine(1, "report.pdf shared ", "report.pdf shared ", "\x00" * 18)],
    )
    assert _press(session, keyboard.KEYSYM_DOWN) == (
        ["notes.txt", "private", "2 of 3"],
        [helpers.BrailleLine(1, "notes.txt private ", "notes.txt private ", "\x00" * 18)],
    )
    assert _press(session, keyboard.KEYSYM_UP) == (
        ["report.pdf", "shared", "1 of 3"],
        [helpers.BrailleLine(1, "report.pdf shared ", "report.pdf shared ", "\x00" * 18)],
    )


@pytest.mark.native_app
def test_radio_button_selection_change(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that arrowing within a radio group announces the newly selected button."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, 7)

    assert _press(session, keyboard.KEYSYM_DOWN) == helpers.expected_for_gtk(
        (
            ["Medium selected radio button"],
            [
                helpers.BrailleLine(
                    1, "&=y Medium radio button", "&=y Medium radio button", "\x00" * 23
                )
            ],
        ),
        gtk4=(
            ["Widgets Page 1", "Medium selected radio button"],
            [
                helpers.BrailleLine(
                    1,
                    "Widgets Page 1 &=y Medium radio button",
                    "&=y Medium radio button",
                    "\x00" * 38,
                )
            ],
        ),
    )
    assert _press(session, keyboard.KEYSYM_UP) == helpers.expected_for_gtk(
        (
            ["Small selected radio button"],
            [
                helpers.BrailleLine(
                    1, "&=y Small radio button", "&=y Small radio button", "\x00" * 22
                )
            ],
        ),
        gtk4=(
            ["Widgets Page 1", "Small selected radio button"],
            [
                helpers.BrailleLine(
                    1,
                    "Widgets Page 1 &=y Small radio button",
                    "&=y Small radio button",
                    "\x00" * 37,
                )
            ],
        ),
    )


@pytest.mark.native_app
def test_scale_value_changes(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that arrowing a horizontal slider announces the new value."""

    session = gtk_widget_notebook
    _prepare(session)
    _tab_to(session, 8)

    assert _press(session, keyboard.KEYSYM_RIGHT) == (
        ["4"],
        [
            helpers.BrailleLine(
                1, "Level 4 horizontal slider", "Level 4 horizontal slider", "\x00" * 25
            )
        ],
    )
    assert _press(session, keyboard.KEYSYM_LEFT) == (
        ["3"],
        [
            helpers.BrailleLine(
                1, "Level 3 horizontal slider", "Level 3 horizontal slider", "\x00" * 25
            )
        ],
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.is_gtk4(),
    reason="GTK4 notebook focus reports the grouping instead of the active page tab",
    strict=True,
    raises=AssertionError,
)
def test_tab_bar_arrow_navigation(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that arrowing on the tab bar moves between page tabs."""

    session = gtk_widget_notebook
    _prepare(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["Widgets page tab"],
        [helpers.BrailleLine(1, "Widgets page tab", "Widgets page tab", "\x00" * 16)],
    )
    assert _press(session, keyboard.KEYSYM_RIGHT) == (
        ["Messages page tab"],
        [helpers.BrailleLine(1, "Messages page tab", "Messages page tab", "\x00" * 17)],
    )
    assert _press(session, keyboard.KEYSYM_RIGHT) == (
        ["Labels page tab"],
        [helpers.BrailleLine(1, "Labels page tab", "Labels page tab", "\x00" * 15)],
    )
    assert _press(session, keyboard.KEYSYM_LEFT) == (
        ["Messages page tab"],
        [helpers.BrailleLine(1, "Messages page tab", "Messages page tab", "\x00" * 17)],
    )


@pytest.mark.native_app
def test_description_technique_presents_static_text(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests that an accessible description is presented for a widget and for an ancestor."""

    session = gtk_widget_notebook
    _prepare(session)

    if gtk.is_gtk4():
        # GTK4's page-switch shortcut leaves focus on the notebook, not the entry.
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    else:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.speech(session) == helpers.expected_for_gtk(
        ["Messages page tab", "Filter text", "3 matches found"],
        gtk4=["Messages Page 2 panel", "Filter text", "3 matches found", "opens popup"],
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.speech(session) == helpers.expected_for_gtk(
        ["Options Review before saving panel", "Agree check box not checked"],
        gtk4=["Review before saving grouping", "Options grouping", "Agree check box not checked"],
    )


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.is_gtk4(),
    reason="GTK4 notebook page context includes an unrelated static label",
    strict=True,
    raises=AssertionError,
)
def test_label_for_names_the_widget(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that a label with a label-for relationship names its widget, not static text."""

    session = gtk_widget_notebook
    _prepare(session)

    if gtk.is_gtk4():
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
        keyboard.tap_key(keyboard.KEYSYM_TAB)
    else:
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_PAGE_DOWN)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_PAGE_DOWN)
    assert helpers.speech(session) == helpers.expected_for_gtk(
        ["Labels page tab", "Volume horizontal slider 0 0 percent."],
        gtk4=["Labels Page 3 panel", "Volume horizontal slider 0 0 percent."],
    )


@pytest.mark.native_app
def test_focusable_list_item_presents_descendants(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests that a focusable list item presents its labels, applying the redundancy filter."""

    session = gtk_widget_notebook
    _prepare(session)

    # Reach the Files page via the tab bar: a focused slider eats Control+Page Down.
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    for _ in range(3):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.speech(session) == helpers.expected_for_gtk(
        ["List with 3 items", "report.pdf", "shared"],
        gtk4=["Files Page 4", "List with 3 items", "report.pdf", "shared"],
    )
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["notes.txt", "private"]

    # The "Budget" row is named "Budget" and also holds a "Budget" label; the redundant
    # label is filtered, so "Budget" is heard once.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["Budget", "2 MB"]


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.is_gtk4(),
    reason="GTK4 list presentation reports 3 items instead of 1 available item",
    strict=True,
    raises=AssertionError,
)
def test_list_count_distinguishes_available_items(
    gtk_widget_notebook: NativeAppSession,
) -> None:
    """Tests that a list count reflects the rows the user can reach with Tab."""

    session = gtk_widget_notebook
    _prepare(session)

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    for _ in range(4):
        keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.speech(session) == ["List with 1 available item", "Available"]
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.speech(session) == ["After list button"]


@pytest.mark.native_app
def test_status_bar_presents_its_contents(gtk_widget_notebook: NativeAppSession) -> None:
    """Tests that presenting the status bar speaks its contents."""

    session = gtk_widget_notebook
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    session.orca.call("WhereAmIPresenter", "PresentStatusBar", True)
    assert helpers.speech(session) == helpers.expected_for_gtk(
        ["Ready. 3 items. status bar"], gtk4=["status bar", "Ready. 3 items."]
    )
