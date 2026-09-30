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

"""Tests browse/focus mode switching: the manual toggle and automatic switching."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


def _toggle_mode(session: BrowserSession) -> list[str]:
    session.orca.press_orca_key(keyboard.KEYSYM_A)
    return speech(session)


def _next(session: BrowserSession, keysym: int) -> list[str]:
    keyboard.tap_key(keysym)
    return speech(session)


@pytest.mark.native_app
def test_manual_toggle_between_browse_and_focus_mode(
    web_structural_navigation: BrowserSession,
) -> None:
    """Tests that Orca+A toggles between focus mode and browse mode."""

    session = web_structural_navigation
    reset_web_state(session)

    assert _toggle_mode(session) == ["Focus mode"]
    assert _toggle_mode(session) == ["Browse mode"]
    assert _toggle_mode(session) == ["Focus mode"]
    assert _toggle_mode(session) == ["Browse mode"]


@pytest.mark.native_app
def test_native_navigation_switches_mode_automatically(
    web_structural_navigation: BrowserSession,
) -> None:
    """Tests that tabbing to a combo box enters focus mode and tabbing on leaves it."""

    session = web_structural_navigation
    reset_web_state(session)

    assert _next(session, keyboard.KEYSYM_TAB) == ["Save", "button"]
    assert _next(session, keyboard.KEYSYM_TAB) == ["Agree", "check box not checked"]
    assert _next(session, keyboard.KEYSYM_TAB) == [
        "Fruit",
        "combo box",
        "Apple",
        "opens menu",
        "Focus mode",
    ]
    assert _next(session, keyboard.KEYSYM_TAB) == ["City", "entry"]
    assert _next(session, keyboard.KEYSYM_TAB) == [
        "Option A",
        "not selected radio button",
        "Browse mode",
    ]


@pytest.mark.native_app
def test_structural_navigation_stays_in_browse_mode(
    web_structural_navigation: BrowserSession,
) -> None:
    """Tests that quick-navigating to an entry does not auto-switch to focus mode."""

    session = web_structural_navigation
    reset_web_state(session)

    assert _next(session, keyboard.KEYSYM_E) == ["e", "City", "entry"]
    assert _toggle_mode(session) == ["Focus mode"]


@pytest.mark.native_app
@pytest.mark.parametrize("click_count", [1, 2], ids=["basic", "detailed"])
@pytest.mark.parametrize("key", [keyboard.KEYSYM_C, keyboard.KEYSYM_E], ids=["combo", "entry"])
def test_where_am_i_preserves_browse_mode(
    web_structural_navigation: BrowserSession, key: int, click_count: int
) -> None:
    """Tests that querying a control does not switch from browse mode to focus mode."""

    session = web_structural_navigation
    reset_web_state(session)
    _next(session, key)
    assert not session.orca.get("DocumentPresenter", "InFocusMode")

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER, click_count=click_count)
    spoken = speech(session)
    assert not session.orca.get("DocumentPresenter", "InFocusMode")
    assert "Focus mode" not in spoken
