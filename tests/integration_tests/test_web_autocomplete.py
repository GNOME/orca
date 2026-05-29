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

"""Tests an ARIA autocomplete combobox's listbox navigation and the alert it raises on submit."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_combobox_listbox_navigation(web_autocomplete: NativeAppSession) -> None:
    """Tests opening the listbox and moving selection through the option list."""

    session = web_autocomplete
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Fruit", "editable combo box", "opens listbox", "Focus mode"]

    # Down opens the popup and lands on the first option; further arrows move selection.
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Apricot"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Apple"]
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert speech(session) == ["Avocado"]
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert speech(session) == ["Apple"]

    # Close the popup so the combobox is pristine for the next test (session-scoped app).
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_alert_region_announced(web_autocomplete: NativeAppSession) -> None:
    """Tests that populating a role=alert region after activating Submit is announced."""

    session = web_autocomplete
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Fruit", "editable combo box", "opens listbox", "Focus mode"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert speech(session) == ["Submit", "button", "Browse mode"]

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert speech(session) == ["Form could not be submitted"]
