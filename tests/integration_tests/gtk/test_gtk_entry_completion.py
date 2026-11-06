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

"""Tests entry-completion speech and braille presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _open_completion(session: NativeAppSession) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["City text", "Alt+C"]
    assert brailled[-1] == helpers.BrailleLine(6, "City  $l Alt+C", "City  $l Alt+C", None)
    for char in "lo":
        keyboard.tap_key(ord(char))
    helpers.capture(session, quiescence=0.5)


@pytest.mark.native_app
# TODO: Investigate missing feedback when navigating GTK3 completion suggestions.
@pytest.mark.xfail(
    reason="GTK3 entry-completion suggestions are not presented",
    raises=AssertionError,
    strict=True,
)
def test_popup_navigation(gtk_entry_completion: NativeAppSession) -> None:
    """Navigates suggestions forward and backward, including clearing the selection."""

    session = gtk_entry_completion
    _open_completion(session)
    for key, name in (
        (keyboard.KEYSYM_DOWN, "London"),
        (keyboard.KEYSYM_DOWN, "Los Angeles"),
        (keyboard.KEYSYM_UP, "London"),
        (keyboard.KEYSYM_UP, None),
        (keyboard.KEYSYM_DOWN, "London"),
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        if name is not None:
            assert spoken == [name]
            assert brailled and name in brailled[-1].full
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    assert helpers.capture(session) == ([], [])


@pytest.mark.native_app
@pytest.mark.parametrize("accept", [False, True], ids=["cancel", "accept"])
def test_close_completion(gtk_entry_completion: NativeAppSession, accept: bool) -> None:
    """Accepts or cancels a suggestion, then continues typing in the entry."""

    session = gtk_entry_completion
    _open_completion(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN if accept else keyboard.KEYSYM_ESCAPE)
    spoken, brailled = helpers.capture(session)
    assert spoken == []
    value = "London" if accept else "lo"
    text = f"City {value} $l Alt+C"
    if accept:
        assert brailled[-1] == helpers.BrailleLine(len(value) + 6, text, text, "\x00" * len(text))
    else:
        assert brailled == []
    keyboard.tap_key(keyboard.KEYSYM_END)
    helpers.capture(session)
    keyboard.tap_key(ord("x"))
    spoken, brailled = helpers.capture(session)
    text = f"City {value}x $l Alt+C"
    assert spoken == ["x"]
    assert brailled[-1] == helpers.BrailleLine(len(value) + 7, text, text, "\x00" * len(text))
    keyboard.tap_key(keyboard.KEYSYM_TAB)
    assert helpers.capture(session) == (
        ["After button"],
        [helpers.BrailleLine(1, "After button", "After button", "\x00" * 12)],
    )
