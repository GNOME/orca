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

"""Tests caret navigation around and into compound widgets in browse modes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
@pytest.mark.parametrize("sticky", [False, True], ids=["browse", "sticky-browse"])
def test_caret_navigation_through_widgets(
    web_widget_boundaries: BrowserSession, sticky: bool
) -> None:
    """Tests both directions, descending into widgets only in sticky browse mode."""

    session = web_widget_boundaries
    helpers.reset_web_state(session)
    if sticky:
        session.orca.call("DocumentPresenter", "EnableStickyBrowseMode", True)
        helpers.speech(session)

    lines = [
        "Widget boundaries",
        "Before colors.",
        *(["Red", "Green", "Blue"] if sticky else ["Colors Red"]),
        "After colors.",
        "Before animals.",
        *(["Cat", "Dog", "Bird"] if sticky else ["Animals Cat"]),
        "After animals.",
        "Before food.",
        *(["Fruits", "Apple", "Banana"] if sticky else ["Food"]),
        "After food.",
        "Before cities.",
        *(["Oslo", "Lima", "Rome"] if sticky else ["Cities Oslo"]),
        "After cities.",
        "End of page.",
    ]
    for key, expected_lines in (
        (keyboard.KEYSYM_DOWN, lines[1:]),
        (keyboard.KEYSYM_UP, list(reversed(lines[:-1]))),
    ):
        for expected in expected_lines:
            keyboard.tap_key(key)
            spoken = helpers.speech(session)
            assert expected in " ".join(spoken), (expected, spoken)
            assert not session.orca.get("DocumentPresenter", "InFocusMode")
            assert session.orca.get("DocumentPresenter", "BrowseModeIsSticky") == sticky
