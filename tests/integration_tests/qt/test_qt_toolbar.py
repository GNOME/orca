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

"""Tests keyboard navigation through toolbar controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_toolbar_navigation(qt_toolbar: NativeAppSession) -> None:
    """Reads toolbar buttons and its entry in both tab directions."""

    session = qt_toolbar
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    helpers.capture(session)
    for name in ("Open", "Save"):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        spoken, brailled = helpers.capture(session)
        assert spoken == [f"{name} button"]
        assert brailled[-1].visible == f"{name} button"
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Search text"]
    assert brailled[-1].visible == "Search  $l"
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["Save button"]
    assert brailled[-1].visible == "Save button"
