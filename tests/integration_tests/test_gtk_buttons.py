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

"""Shared GTK3/GTK4 coverage for button focus, activation, and state presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import gtk
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _prepare(session: NativeAppSession, tabs: int = 0) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    keyboard.tap_key(keyboard.KEYSYM_F12)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    for _ in range(tabs):
        helpers.tab_and_swallow_presentation(session)


def _assert_presentation(session: NativeAppSession, speech: str, braille: str) -> None:
    spoken, brailled = helpers.capture(session)
    assert spoken == [speech]
    assert brailled[-1] == helpers.BrailleLine(1, braille, braille, "\x00" * len(braille))


def _switch_presentation(active: bool) -> tuple[str, str, str]:
    # GTK3 exposes Gtk.Switch as a toggle button; GTK4 exposes the switch role.
    indicator = "&=y" if active else "& y"
    if gtk.selected_toolkit() == "gtk3":
        state = "pressed" if active else "not pressed"
        return f"Wi-Fi toggle button {state}", f"{indicator} Wi-Fi toggle button", state
    state = "on" if active else "off"
    return f"Wi-Fi {state} switch", f"{indicator} Wi-Fi switch", state


@pytest.mark.native_app
@pytest.mark.parametrize("reverse", (False, True), ids=("forward", "backward"))
def test_tab_navigation(gtk_buttons: NativeAppSession, reverse: bool) -> None:
    """Tests roles, initial states, wrapping, and skipping the disabled button."""

    session = gtk_buttons
    _prepare(session)
    controls = [
        ("Save button", "Save button"),
        ("Bold toggle button not pressed", "& y Bold toggle button"),
        ("Enabled check box not checked", "< > Enabled check box"),
        _switch_presentation(False)[:2],
        ("Done button", "Done button"),
    ]
    order = (4, 3, 2, 1, 0) if reverse else (1, 2, 3, 4, 0)
    for index in order:
        if reverse:
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
        else:
            keyboard.tap_key(keyboard.KEYSYM_TAB)
        _assert_presentation(session, *controls[index])


@pytest.mark.native_app
@pytest.mark.parametrize(
    "key", (keyboard.KEYSYM_SPACE, keyboard.KEYSYM_RETURN), ids=("space", "enter")
)
def test_push_button_activation(gtk_buttons: NativeAppSession, key: int) -> None:
    """Tests that activation updates the name presented by Where Am I and on refocus."""

    session = gtk_buttons
    _prepare(session)
    session.orca.call("WhereAmIPresenter", "WhereAmIBasic", True)
    _assert_presentation(session, "Save button", "Save button")

    keyboard.tap_key(key)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("WhereAmIPresenter", "WhereAmIBasic", True)
    _assert_presentation(session, "Saved button", "Saved button")

    helpers.tab_and_swallow_presentation(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    _assert_presentation(session, "Saved button", "Saved button")
    # Leave focus away from the renamed button so the next test's reset moves focus.
    # Changes without refocusing are covered in test_gtk_button_name_change.py.
    helpers.tab_and_swallow_presentation(session)


@pytest.mark.native_app
@pytest.mark.parametrize("tabs", (1, 2, 3), ids=("toggle", "check", "switch"))
def test_button_state_changes(gtk_buttons: NativeAppSession, tabs: int) -> None:
    """Tests both state transitions, Where Am I, and the active state after refocusing."""

    session = gtk_buttons
    _prepare(session, tabs)
    if tabs == 1:
        inactive = ("Bold toggle button not pressed", "& y Bold toggle button", "not pressed")
        active = ("Bold toggle button pressed", "&=y Bold toggle button", "pressed")
    elif tabs == 2:
        inactive = ("Enabled check box not checked", "< > Enabled check box", "not checked")
        active = ("Enabled check box checked", "<x> Enabled check box", "checked")
    else:
        inactive = _switch_presentation(False)
        active = _switch_presentation(True)

    session.orca.call("WhereAmIPresenter", "WhereAmIBasic", True)
    _assert_presentation(session, *inactive[:2])

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    _assert_presentation(session, active[2], active[1])
    session.orca.call("WhereAmIPresenter", "WhereAmIBasic", True)
    _assert_presentation(session, *active[:2])

    helpers.tab_and_swallow_presentation(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    _assert_presentation(session, *active[:2])

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    _assert_presentation(session, inactive[2], inactive[1])
    session.orca.call("WhereAmIPresenter", "WhereAmIBasic", True)
    _assert_presentation(session, *inactive[:2])
