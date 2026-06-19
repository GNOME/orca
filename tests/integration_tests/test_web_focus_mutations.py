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

"""Tests for controls that recreate or relabel themselves in response to focus and activation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_focus_replaces_element(web_focus_mutations: NativeAppSession) -> None:
    """Tests that focusing a self-replacing button announces the recreated element."""

    session = web_focus_mutations
    reset_web_state(session)

    # The button's onfocus destroys the original DOM node and focuses a new one.
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session, wait_async=True) == (
        ["Replacement button", "button"],
        [
            BrailleLine(1, "Replacement button button", "Replacement button button", "\x00" * 25),
        ],
    )


@pytest.mark.native_app
def test_similar_relabel_is_suppressed(web_focus_mutations: NativeAppSession) -> None:
    """Tests that relabeling the focused button to a near-identical name is not announced."""

    session = web_focus_mutations
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session, wait_async=True)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Save", "button"],
        [BrailleLine(1, "Save button", "Save button", "\x00" * 11)],
    )

    # "Save" -> "Saved" exceeds the name-similarity threshold, so Orca suppresses it.
    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert capture(session, wait_async=True) == ([], [])


@pytest.mark.native_app
def test_distinct_relabel_is_announced(web_focus_mutations: NativeAppSession) -> None:
    """Tests that relabeling the focused button to a distinct name re-announces it."""

    session = web_focus_mutations
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session, wait_async=True)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    capture(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert capture(session) == (
        ["Refresh", "button"],
        [BrailleLine(1, "Refresh button", "Refresh button", "\x00" * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_SPACE)
    assert capture(session, wait_async=True) == (
        ["Loading complete"],
        [BrailleLine(1, "Loading complete button", "Loading complete button", "\x00" * 23)],
    )
