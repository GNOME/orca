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
from tests.integration_tests.apps import qt
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
@pytest.mark.xfail(
    qt.is_qt5(),
    reason="Qt5 exposes QCompleter's popup without an accessible parent",
    strict=True,
    raises=AssertionError,
)
def test_popup_navigation(qt_entry_completion: NativeAppSession) -> None:
    """Navigates suggestions forward and backward."""

    session = qt_entry_completion
    _open_completion(session)
    for index, (key, name) in enumerate(
        (
            (keyboard.KEYSYM_DOWN, "London"),
            (keyboard.KEYSYM_DOWN, "Los Angeles"),
            (keyboard.KEYSYM_UP, "London"),
        )
    ):
        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        assert spoken == (["OrcaEntryCompletion List with 3 items", name] if index == 0 else [name])
        assert brailled and name in brailled[-1].full
    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    helpers.capture(session)


@pytest.mark.native_app
@pytest.mark.parametrize("accept", [False, True], ids=["cancel", "accept"])
@pytest.mark.xfail(
    reason="Qt does not emit an AT-SPI focus event for the entry when QCompleter's popup closes",
    strict=True,
    raises=AssertionError,
)
def test_close_completion(qt_entry_completion: NativeAppSession, accept: bool) -> None:
    """Accepts or cancels a suggestion, then continues typing in the entry."""

    session = qt_entry_completion
    _open_completion(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RETURN if accept else keyboard.KEYSYM_ESCAPE)
    spoken, brailled = helpers.capture(session)
    value = "London"
    assert spoken == ["City text", value, "Alt+C"]
    text = f"City {value} $l Alt+C"
    assert brailled[-1] == helpers.BrailleLine(len(value) + 6, text, text, "\x00" * len(text))
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


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Qt's QListView::currentChanged() omits the AT-SPI focus notification "
        "when the current completion item is cleared"
    ),
    strict=True,
    raises=AssertionError,
)
def test_reselect_first_completion(qt_entry_completion: NativeAppSession) -> None:
    """Reads the first suggestion after moving above it and back down."""

    session = qt_entry_completion
    _open_completion(session)
    for key in (keyboard.KEYSYM_DOWN, keyboard.KEYSYM_UP):
        keyboard.tap_key(key)
        helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["London"]
    assert brailled and brailled[-1].visible == "London"
