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

"""Tests caret movement, selection, and reading in a text editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _prepare(session: NativeAppSession) -> None:
    session.orca.set("BraillePresenter", "DisplayAncestors", False)
    helpers.move_to_top(session)


def _assert(session: NativeAppSession, spoken, text, cursor=1, selected=0) -> None:
    actual, brailled = helpers.capture(session)
    assert actual == spoken
    assert brailled
    full = text + " $l"
    assert brailled[-1] == helpers.BrailleLine(
        cursor, full, full, "\xc0" * selected + "\x00" * (len(full) - selected)
    )


@pytest.mark.native_app
@pytest.mark.parametrize("orca_controls", [False, True], ids=["native", "orca-controlled"])
def test_character_and_line_navigation(qt_text_view_short: NativeAppSession, orca_controls) -> None:
    """Reads characters and crosses a blank line in both directions."""

    session = qt_text_view_short
    _prepare(session)
    if orca_controls:
        session.orca.press_orca_key(keyboard.KEYSYM_F12)
        assert helpers.speech(session) == ["The screen reader is controlling the caret."]
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    _assert(session, ["i"], "First sentence.", 2)
    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    _assert(session, ["F"], "First sentence.")
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    _assert(session, ["blank"], "")
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    _assert(session, ["Second sentence."], "Second sentence.")
    keyboard.tap_key(keyboard.KEYSYM_UP)
    _assert(session, ["blank"], "")
    keyboard.tap_key(keyboard.KEYSYM_UP)
    _assert(session, ["First sentence."], "First sentence.")


@pytest.mark.native_app
@pytest.mark.parametrize("orca_controls", [False, True], ids=["native", "orca-controlled"])
def test_document_endpoints(qt_text_view_short: NativeAppSession, orca_controls) -> None:
    """Moves to the document end and back to its start."""

    session = qt_text_view_short
    _prepare(session)
    if orca_controls:
        session.orca.press_orca_key(keyboard.KEYSYM_F12)
        helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_END)
    _assert(session, ["blank"], "")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    _assert(session, ["First sentence."], "First sentence.")


@pytest.mark.native_app
def test_selection(qt_text_view_short: NativeAppSession) -> None:
    """Extends and shrinks a selection, then reports the remaining selected text."""

    session = qt_text_view_short
    _prepare(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    _assert(session, ["F", "selected"], "First sentence.", 2, 1)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_END)
    _assert(session, ["irst sentence.", "selected"], "First sentence.", 16, 15)
    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (["Selected text is:  First sentence."], [])
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_HOME)
    _assert(session, ["First sentence.", "unselected"], "First sentence.")
    session.orca.press_orca_key(keyboard.KEYSYM_UP, extra_modifiers=[keyboard.KEYSYM_SHIFT_L])
    assert helpers.capture(session) == (["No selected text."], [])


@pytest.mark.native_app
@pytest.mark.xfail(
    reason=(
        "Orca omits position feedback when native navigation clears a selection "
        "without moving the caret"
    ),
    strict=True,
    raises=AssertionError,
)
def test_selection_collapse(qt_text_view_short: NativeAppSession) -> None:
    """Reports the character reached when an arrow collapses selected text."""

    session = qt_text_view_short
    _prepare(session)
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    _assert(session, ["Text unselected.", "i"], "First sentence.", 2)


@pytest.mark.native_app
@pytest.mark.parametrize("style", ["line", "sentence"])
def test_say_all(qt_text_view_short: NativeAppSession, style: str) -> None:
    """Reads the document once, including text after the blank line."""

    session = qt_text_view_short
    _prepare(session)
    session.orca.set("SayAllPresenter", "Style", style)
    session.orca.set("SayAllPresenter", "OnlySpeakDisplayedText", True)
    session.orca.call("SayAllPresenter", "SayAll", True)
    assert helpers.speech(session, quiescence=0.4, overall=10.0) == [
        "First sentence.",
        "Second sentence.",
    ]


@pytest.mark.native_app
@pytest.mark.xfail(
    reason="Qt's GetStringAtOffset(LINE) omits newlines, leaving blank lines with empty ranges",
    strict=True,
    raises=AssertionError,
)
def test_flat_review(qt_text_view_short: NativeAppSession) -> None:
    """Reviews lines, words, and characters without moving the caret."""

    session = qt_text_view_short
    _prepare(session)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    _assert(session, ["First sentence."], "First sentence.")
    keyboard.tap_key(keyboard.KEYSYM_KP_RIGHT)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["sentence."]
    assert brailled[-1].full == "First sentence. $l"
    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_DOWN)
    spoken, brailled = helpers.capture(session)
    assert spoken == ["e"]
    assert brailled[-1].full == "First sentence. $l"
