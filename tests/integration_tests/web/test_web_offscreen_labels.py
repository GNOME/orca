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

"""Tests presentation of form fields whose labels are hidden in various ways."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


def _say_all(session: BrowserSession, style: str) -> list[str]:
    """Warms the line caches, sets the Say All style, and returns the Say All speech."""

    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)
    helpers.move_to_top(session)
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    session.orca.set("SayAllPresenter", "Style", style)
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    return helpers.speech(session)


@pytest.mark.native_app
def test_line_navigation_over_offscreen_labels(web_offscreen_labels: BrowserSession) -> None:
    """Tests line navigation past fields with off-screen and clip-hidden labels."""

    session = web_offscreen_labels
    helpers.move_to_top(session)

    for name in (
        "Label one neg X",
        "Label two neg Y",
        "Label three div",
        "Label four span",
        "Label five clip",
    ):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.capture(session) == (
            [name, "entry"],
            [helpers.BrailleLine(17, f"{name}  $l", f"{name}  $l", None)],
        )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        ["End."],
        [helpers.BrailleLine(1, "End.", "End.", "\x00" * 4)],
    )


@pytest.mark.native_app
def test_say_all_by_sentence_omits_offscreen_labels(
    web_offscreen_labels: BrowserSession,
) -> None:
    """Tests that Say All by sentence does not read the off-screen labels as content."""

    # The fields are empty and their labels are hidden, so Say All reads neither.
    assert _say_all(web_offscreen_labels, "sentence") == ["Start.", "End."]


@pytest.mark.native_app
def test_say_all_by_line_omits_offscreen_labels(web_offscreen_labels: BrowserSession) -> None:
    """Tests that Say All by line does not read the off-screen labels as content."""

    assert _say_all(web_offscreen_labels, "line") == ["Start.", "End."]
