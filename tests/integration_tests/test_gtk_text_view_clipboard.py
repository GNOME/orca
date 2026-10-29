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

"""Tests clipboard operations and edit history in GTK TextViews."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .apps import gtk
from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_top, speech
from .version_helpers import gtk_version, version_at_least

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_UNDO_REDO = pytest.mark.skipif(
    not gtk.is_gtk4(), reason="GTK3 TextViews have no built-in undo/redo"
)

_GTK4_OMITS_SELECTION_CHANGED_EVENT_ON_CLEAR = gtk.is_gtk4() and version_at_least(
    gtk_version("4.0"), 4, 23, 1
)

_SELECTION_CLEAR = pytest.mark.skipif(
    gtk.is_gtk4(),
    reason=(
        "GTK4 TextView redo selection-clear coverage is on hold: "
        "https://gitlab.gnome.org/GNOME/gtk/-/work_items/8506"
    ),
)


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
    prefix = "OrcaTextView application frame "
    full = prefix + text + " $l"
    start, end = selection
    mask = "\x00" * (len(prefix) + start) + "\xc0" * (end - start)
    mask += "\x00" * (len(full) - len(mask))
    assert brailled[-1] == BrailleLine(
        cursor, full, text + " $l" if visible is None else visible, mask
    )
    assert actual_speech == spoken


@pytest.mark.native_app
def test_cut(gtk_text_view_selection: NativeAppSession) -> None:
    """Tests cutting selected text and presenting its clipboard contents."""

    session = gtk_text_view_selection
    move_to_top(session)
    for _ in range(4):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
    _assert_text(
        session,
        ["Cut selection to clipboard."],
        " one.",
        32,
        visible="OrcaTextView application frame  ",
    )
    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    assert speech(session) == ["Clipboard contains: Line"]


@pytest.mark.native_app
@pytest.mark.parametrize("replace_selection", [False, True])
def test_paste(gtk_text_view_selection: NativeAppSession, replace_selection: bool) -> None:
    """Tests pasting at the caret and over selected text."""

    session = gtk_text_view_selection
    move_to_top(session)
    for _ in range(4):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert speech(session) == ["Copied selection to clipboard."]
    if replace_selection:
        move_to_top(session)
        for _ in range(5):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        capture(session)
    else:
        keyboard.tap_key(keyboard.KEYSYM_END)
        capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    spoken = ["Pasted contents from clipboard."]
    # GTK 4.23.1 and later omit the event.
    if replace_selection and not _GTK4_OMITS_SELECTION_CHANGED_EVENT_ON_CLEAR:
        spoken.append("Text unselected.")
    text = "Line Line." if replace_selection else "Line one.Line"
    _assert_text(session, spoken, text, 10 if replace_selection else 14)


@pytest.mark.native_app
@_UNDO_REDO
@_SELECTION_CLEAR
def test_undo_redo_cut(gtk_text_view_selection: NativeAppSession) -> None:
    """Tests restoring a cut selection with undo and removing it again with redo."""

    session = gtk_text_view_selection
    move_to_top(session)
    for _ in range(4):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo", "Selection restored."], "Line one.", 1, (0, 4))
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        ["redo", "Text unselected."],
        " one.",
        32,
        visible="OrcaTextView application frame  ",
    )


@pytest.mark.native_app
@_UNDO_REDO
@pytest.mark.parametrize("replace_selection", [False, pytest.param(True, marks=_SELECTION_CLEAR)])
def test_undo_redo_paste(
    gtk_text_view_selection: NativeAppSession, replace_selection: bool
) -> None:
    """Tests undo and redo of an insertion or replacement from the clipboard."""

    session = gtk_text_view_selection
    move_to_top(session)
    for _ in range(4):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert speech(session) == ["Copied selection to clipboard."]
    if replace_selection:
        move_to_top(session)
        for _ in range(5):
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
    spoken = ["undo", "Selection restored."] if replace_selection else ["undo"]
    _assert_text(
        session,
        spoken,
        "Line one.",
        6 if replace_selection else 10,
        (5, 8) if replace_selection else (0, 0),
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    spoken = ["redo", "Text unselected."] if replace_selection else ["redo"]
    text = "Line Line." if replace_selection else "Line one.Line"
    _assert_text(session, spoken, text, 10 if replace_selection else 14)


@pytest.mark.native_app
@_UNDO_REDO
def test_undo_redo_delete(gtk_text_view_selection: NativeAppSession) -> None:
    """Tests undo and redo of deleting a character without a selection."""

    session = gtk_text_view_selection
    move_to_top(session)
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    _assert_text(session, ["i"], "ine one.", 1)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo"], "Line one.", 1)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["redo"], "ine one.", 1)


@pytest.mark.native_app
@_UNDO_REDO
@_SELECTION_CLEAR
def test_undo_redo_replacement(gtk_text_view_selection: NativeAppSession) -> None:
    """Tests undo and redo of typing over selected text."""

    session = gtk_text_view_selection
    move_to_top(session)
    for _ in range(4):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    capture(session)
    keyboard.tap_key(keyboard.KEYSYM_Z)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo"], " one.", 32, visible="OrcaTextView application frame  ")
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["undo", "Selection restored."], "Line one.", 1, (0, 4))
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        ["redo", "Text unselected."],
        " one.",
        32,
        visible="OrcaTextView application frame  ",
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(session, ["redo"], "z one.", 2)


@pytest.mark.native_app
@_UNDO_REDO
@pytest.mark.parametrize("edit", ["cut", "paste", "replacement"])
def test_undo_restores_selection(gtk_text_view_selection: NativeAppSession, edit: str) -> None:
    """Tests restoring the text and selection removed by a cut, paste, or typed replacement."""

    session = gtk_text_view_selection
    if edit == "paste":
        move_to_top(session)
        for _ in range(4):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        capture(session)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
        assert speech(session) == ["Copied selection to clipboard."]
        move_to_top(session)
        for _ in range(5):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        capture(session)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    else:
        move_to_top(session)
        for _ in range(4):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        capture(session)
        if edit == "cut":
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
        else:
            keyboard.tap_key(keyboard.KEYSYM_Z)
    capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    if edit == "replacement":
        _assert_text(session, ["undo"], " one.", 32, visible="OrcaTextView application frame  ")
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        ["undo", "Selection restored."],
        "Line one.",
        6 if edit == "paste" else 1,
        (5, 8) if edit == "paste" else (0, 4),
    )
