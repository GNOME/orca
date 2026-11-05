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

"""Tests combo box speech and braille presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _focus_entry(session: NativeAppSession) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
    helpers.tab_and_swallow_presentation(session)
    helpers.tab_and_swallow_presentation(session)
    keyboard.tap_key(keyboard.KEYSYM_END)
    helpers.capture(session)


@pytest.mark.native_app
def test_unfocused_selection_change(gtk_combo_box: NativeAppSession) -> None:
    """Keeps Color's selection change silent while the City entry has focus."""

    session = gtk_combo_box
    _focus_entry(session)
    keyboard.tap_key(keyboard.KEYSYM_F5)
    assert helpers.capture(session) == ([], [])
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Color combo box Green"]
    assert brailled[-1] == helpers.BrailleLine(
        7, "Color Green combo box", "Color Green combo box", "\x00" * 21
    )


@pytest.mark.native_app
def test_selection_change_while_editing(gtk_combo_box: NativeAppSession) -> None:
    """Presents the selected item's text when it replaces the focused City entry."""

    session = gtk_combo_box
    _focus_entry(session)
    for value in ("Paris", "Rome"):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_F5)
        spoken, brailled = helpers.capture(session)
        assert spoken == [value]
        text = f"{value} $l"
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))
