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

"""Tests selection in web editables containing embedded objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import expected_for_browser, reset_web_state, say_selection, speech

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_selected_text_separates_embedded_control(
    web_editable_embedded_selection: BrowserSession,
) -> None:
    """Tests that selected text separates an embedded control from its adjacent label."""

    session = web_editable_embedded_selection
    reset_web_state(session)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Editor", "entry", "Focus mode"]
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    speech(session)

    # Firefox exposes no text for the combo box or its option; Chromium exposes "Apple".
    expected = expected_for_browser(
        session,
        "Selected text is:  First link Fruit Apple Second paragraph.",
        firefox="Selected text is:  First link Fruit Second paragraph.",
    )
    assert say_selection(session) == [expected]
