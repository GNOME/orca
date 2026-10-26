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

"""Tests button name changes while focus remains on the button."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import gtk
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.xfail(
    gtk.selected_toolkit() == "gtk4",
    reason=(
        "GTK4 emits the name-change event for the child label but not the button: "
        "https://gitlab.gnome.org/GNOME/gtk/-/work_items/8504"
    ),
    strict=True,
    raises=AssertionError,
)
def test_button_name_change_without_refocusing(gtk_buttons: NativeAppSession) -> None:
    """Tests that Where Am I uses a changed button name without needing a focus change."""

    session = gtk_buttons
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    # Refocus the renamed button so its current name is cached before the next change.
    helpers.tab_and_swallow_presentation(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Saved button"]
    assert brailled[-1] == helpers.BrailleLine(1, "Saved button", "Saved button", "\x00" * 12)

    # F12 changes Saved back to Save while focus stays on the same button.
    keyboard.tap_key(keyboard.KEYSYM_F12)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("WhereAmIPresenter", "WhereAmIBasic", True)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Save button"]
    assert brailled[-1] == helpers.BrailleLine(1, "Save button", "Save button", "\x00" * 11)
