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

"""Tests the initially focused GTK4 DropDown's selected value."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .apps import gtk
from .harness import keyboard
from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

pytestmark = pytest.mark.skipif(not gtk.is_gtk4(), reason="GtkDropDown does not exist in GTK3")


@pytest.mark.native_app
@pytest.mark.skipif(
    gtk.is_gtk4(),
    reason="On hold: Orca must activate the app script before setting its initial locus of focus",
)
def test_where_am_i_reports_initial_selection(gtk_drop_down: NativeAppSession) -> None:
    """Tests starting Orca with the drop-down focused, before any focus event."""

    session = gtk_drop_down
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    assert capture(session) == (
        ["Color combo box Red", "opens popup"],
        [BrailleLine(7, "Color Red combo box", "Color Red combo box", "\x00" * 19)],
    )
