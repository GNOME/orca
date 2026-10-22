# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

"""Integration tests for braille updates during continuous terminal output."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .terminal_helpers import settle

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
@pytest.mark.parametrize("navigate", [False, True], ids=["live-updates", "review-command"])
def test_flat_review_updates(gtk3_terminal_updates: NativeAppSession, navigate: bool) -> None:
    """Limits background updates without losing the final text or the review position."""

    session = gtk3_terminal_updates
    settle(session)
    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    helpers.toggle_flat_review(session)
    keyboard.tap_key(keyboard.KEYSYM_F5)
    keyboard.tap_key(keyboard.KEYSYM_KP_UP)
    assert helpers.capture(session) == (
        ["value 000\n"],
        [helpers.BrailleLine(1, "value 000 $l", "value 000 $l", "\x00" * 12)],
    )
    if navigate:
        time.sleep(1.0)
        session.reader.reset()
        session.orca.press_orca_key(keyboard.KEYSYM_KP_HOME)

    start = time.monotonic()
    spoken, brailled = helpers.capture(session, wait_async=True, quiescence=0.4, overall=6.0)
    elapsed = time.monotonic() - start
    if not navigate:
        assert spoken == []
        # Allow scheduling slack, but reject refreshing on every output event.
        assert 2 <= len(brailled) <= int(elapsed / 0.2) + 4
        assert brailled[-1] == helpers.BrailleLine(1, "value 100 $l", "value 100 $l", "\x00" * 12)
        return

    assert spoken == ["anchor\n"]
    anchor = helpers.BrailleLine(1, "anchor $l", "anchor $l", "\x00" * 9)
    # Output already queued before the command may precede the new review position.
    first_anchor = brailled.index(anchor)
    assert all(line == anchor for line in brailled[first_anchor:])

    keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
    assert helpers.capture(session) == (
        ["value 100\n"],
        [helpers.BrailleLine(1, "value 100 $l", "value 100 $l", "\x00" * 12)],
    )
    keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
    assert helpers.capture(session) == (["anchor\n"], [anchor])
