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

"""Tests clipboard presentation with a GTK application."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .apps import gtk
from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _discard_output(session: NativeAppSession) -> None:
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_copy_and_paste(gtk_two_entries: NativeAppSession) -> None:
    """Tests copying, presenting the clipboard, and pasting into another entry."""

    session = gtk_two_entries
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


_UNDO_REDO = pytest.mark.skipif(not gtk.is_gtk4(), reason="GTK3 entries have no built-in undo/redo")


def _assert_text(
    session: NativeAppSession,
    spoken: list[str],
    text: str,
    cursor: int,
    selection: tuple[int, int] = (0, 0),
    visible: str | None = None,
) -> None:
    """Checks speech and the final braille text, cursor, and selection mask."""

    actual_speech, brailled = capture(session)
    prefix = "OrcaTwoEntries application frame "
    full = prefix + text + " $l"
    start, end = selection
    mask = "\x00" * (len(prefix) + start) + "\xc0" * (end - start)
    mask += "\x00" * (len(full) - len(mask))
    assert brailled[-1] == BrailleLine(
        cursor, full, text + " $l" if visible is None else visible, mask
    )
    assert actual_speech == spoken


@pytest.mark.native_app
def test_cut(gtk_two_entries: NativeAppSession) -> None:
    """Tests cutting selected text and presenting its clipboard contents."""

    session = gtk_two_entries
    move_to_top(session)
    for _ in range(5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
    _assert_text(
        session,
        ["Cut selection to clipboard."],
        " pie recipe",
        7,
        visible="frame  pie recipe $l",
    )
    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    assert speech(session) == ["Clipboard contains: Apple"]


@pytest.mark.native_app
@pytest.mark.parametrize("replace_selection", [False, True])
def test_paste(gtk_two_entries: NativeAppSession, replace_selection: bool) -> None:
    """Tests pasting at the caret and over selected text."""

    session = gtk_two_entries
    move_to_top(session)
    for _ in range(5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert speech(session) == ["Copied selection to clipboard."]
    if replace_selection:
        move_to_top(session)
        for _ in range(6):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        capture(session)
    else:
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    spoken = ["Pasted contents from clipboard."]
    if replace_selection:
        spoken.append("Text unselected.")
    text = "Apple Apple recipe" if replace_selection else "Apple pie recipeApple"
    _assert_text(session, spoken, text, 12 if replace_selection else 22)


@pytest.mark.native_app
@_UNDO_REDO
def test_undo_redo_cut(gtk_two_entries: NativeAppSession) -> None:
    """Tests restoring a cut selection with undo and removing it again with redo."""

    session = gtk_two_entries
    move_to_top(session)
    for _ in range(5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo", "Selection restored."], "Apple pie recipe", 6, (0, 5))
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        ["redo", "Text unselected."],
        " pie recipe",
        7,
        visible="frame  pie recipe $l",
    )


@pytest.mark.native_app
@_UNDO_REDO
@pytest.mark.parametrize("replace_selection", [False, True])
def test_undo_redo_paste(gtk_two_entries: NativeAppSession, replace_selection: bool) -> None:
    """Tests undo and redo of an insertion or replacement from the clipboard."""

    session = gtk_two_entries
    move_to_top(session)
    for _ in range(5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert speech(session) == ["Copied selection to clipboard."]
    if replace_selection:
        move_to_top(session)
        for _ in range(6):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        capture(session)
    else:
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    if replace_selection:
        # GtkEntry records paste's deletion and insertion as separate undo actions.
        _assert_text(session, ["undo"], "Apple  recipe", 7)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
        _assert_text(session, ["undo", "Selection restored."], "Apple pie recipe", 10, (6, 9))
    else:
        _assert_text(session, ["undo"], "Apple pie recipe", 17)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    if replace_selection:
        _assert_text(session, ["redo", "Text unselected."], "Apple  recipe", 7)
        keyboard.press_chord(
            [keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z
        )
    text = "Apple Apple recipe" if replace_selection else "Apple pie recipeApple"
    _assert_text(session, ["redo"], text, 12 if replace_selection else 22)


@pytest.mark.native_app
@_UNDO_REDO
def test_undo_redo_delete(gtk_two_entries: NativeAppSession) -> None:
    """Tests undo and redo of deleting a character without a selection."""

    session = gtk_two_entries
    move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    _assert_text(session, ["p"], "pple pie recipe", 1)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo"], "Apple pie recipe", 1)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["redo"], "pple pie recipe", 1)


@pytest.mark.native_app
@_UNDO_REDO
def test_undo_redo_replacement(gtk_two_entries: NativeAppSession) -> None:
    """Tests undo and redo of typing over selected text."""

    session = gtk_two_entries
    move_to_top(session)
    for _ in range(5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_Z)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo", "Selection restored."], "Apple pie recipe", 6, (0, 5))
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["redo", "Text unselected."], "z pie recipe", 2)
