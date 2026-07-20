# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""Integration tests for terminal content changing in place during flat review."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle, type_text

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _navigate_to_c1_line(session: NativeAppSession) -> None:
    """Moves flat review to the c1/c2 output line and discards the output."""

    session.orca.call("FlatReviewPresenter", "GoHome", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    session.orca.call("FlatReviewPresenter", "GoNextLine", True)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_flat_review_speaks_live_update(gtk3_terminal_flatrev: NativeAppSession) -> None:
    """Tests that a terminal line changing in place is spoken when SpeaksUpdates is on."""

    session = gtk3_terminal_flatrev
    settle(session)

    type_text("bash t.sh")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    time.sleep(0.5)

    session.orca.set("FlatReviewPresenter", "SpeaksUpdates", True)
    helpers.toggle_flat_review(session)
    _navigate_to_c1_line(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["c1\n"],
        [helpers.BrailleLine(1, "c1 $l", "c1 $l", "\x00" * 5)],
    )

    assert helpers.capture(session, wait_async=True, overall=5.0) == (
        ["c2\n"],
        [
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
        ],
    )

    session.orca.set("FlatReviewPresenter", "SpeaksUpdates", False)
    helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_flat_review_silent_live_update_when_disabled(
    gtk3_terminal_flatrev: NativeAppSession,
) -> None:
    """Tests that a terminal line changing in place is not spoken when SpeaksUpdates is off."""

    session = gtk3_terminal_flatrev
    settle(session)

    type_text("bash t.sh")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    time.sleep(0.5)

    helpers.toggle_flat_review(session)
    _navigate_to_c1_line(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["c1\n"],
        [helpers.BrailleLine(1, "c1 $l", "c1 $l", "\x00" * 5)],
    )

    assert helpers.capture(session, wait_async=True, overall=5.0) == (
        [],
        [
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
            helpers.BrailleLine(1, "c2 $l", "c2 $l", "\x00" * 5),
        ],
    )

    helpers.toggle_flat_review(session)


@pytest.mark.native_app
def test_flat_review_location_survives_terminal_live_update(
    gtk3_terminal_review_update: NativeAppSession,
) -> None:
    """Tests that a terminal update does not undo a preceding flat-review command."""

    session = gtk3_terminal_review_update
    settle(session)

    type_text("bash review.sh")
    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    time.sleep(0.5)

    original_layout = session.orca.get("CommandManager", "KeyboardLayoutIsDesktop")
    assert session.orca.get("CommandManager", "LaptopModifierKeys")[0] == "Caps_Lock"
    if original_layout:
        session.orca.call("CommandManager", "ToggleKeyboardLayout", False)
    assert not session.orca.get("CommandManager", "KeyboardLayoutIsDesktop")
    session.orca.set("FlatReviewPresenter", "FocusTracking", 2)
    helpers.toggle_flat_review(session)
    try:
        session.orca.press_orca_key(keyboard.KEYSYM_U)
        spoken, brailled = helpers.capture(session)
        assert spoken == ["anchor\n"]
        assert helpers.BrailleLine(1, "anchor $l", "anchor $l", "\x00" * 9) in brailled

        helpers.capture(session, wait_async=True, overall=6.0)
        session.reader.reset()
        session.orca.call("FlatReviewPresenter", "PresentLine", True)
        assert helpers.capture(session) == (
            ["anchor\n"],
            [helpers.BrailleLine(1, "anchor $l", "anchor $l", "\x00" * 9)],
        )
    finally:
        helpers.toggle_flat_review(session)
        session.orca.set("FlatReviewPresenter", "FocusTracking", 1)
        if original_layout:
            session.orca.call("CommandManager", "ToggleKeyboardLayout", False)
