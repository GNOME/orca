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

"""Tests clipboard presentation and flat review copying with a GTK application."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import capture, speech, toggle_flat_review

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _discard_output(session: NativeAppSession) -> None:
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_copy_and_paste(gtk3_two_entries: NativeAppSession) -> None:
    """Tests copying, presenting the clipboard, and pasting into another entry."""

    session = gtk3_two_entries
    _discard_output(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    _discard_output(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert speech(session) == ["Copied selection to clipboard."]

    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    assert speech(session) == ["Clipboard contains: Apple pie recipe"]

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_A)
    _discard_output(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    spoken, brailled = capture(session)
    assert spoken == ["Pasted contents from clipboard.", "Text unselected."]
    assert brailled[-1].full == "OrcaTwoEntries application frame Apple pie recipe $l"


@pytest.mark.native_app
def test_flat_review_copy_and_append(gtk3_two_entries: NativeAppSession) -> None:
    """Tests copying and appending reviewed text to the clipboard."""

    session = gtk3_two_entries
    _discard_output(session)
    toggle_flat_review(session)
    session.orca.call("FlatReviewPresenter", "PresentLine", True)
    assert speech(session) == ["Apple pie recipe"]

    session.orca.call("FlatReviewPresenter", "CopyToClipboard", True)
    assert speech(session) == ["Copied contents to clipboard."]
    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    assert speech(session) == ["Clipboard contains: Apple pie recipe"]

    session.orca.call("FlatReviewPresenter", "GoNextLine", True)
    assert speech(session) == ["Banana bread recipe"]
    session.orca.call("FlatReviewPresenter", "AppendToClipboard", True)
    assert speech(session) == ["Appended contents to clipboard."]
    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    assert speech(session) == ["Clipboard contains: Apple pie recipe\nBanana bread recipe"]
