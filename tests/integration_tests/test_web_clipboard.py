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

"""Tests clipboard operations and edit history in web inputs and textareas."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import browser
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession

pytestmark = [
    helpers.skip_firefox_caret_tab(),
    pytest.mark.parametrize("field", ["input", "textarea"]),
]

_SELECTION_CLEAR = pytest.mark.skipif(
    browser.selected_browser() == "firefox",
    reason=(
        "Gecko omits text-selection-changed when an edit clears the selection, "
        "so redo selection-clear coverage is on hold"
    ),
)


def _focus_field(session: BrowserSession, field: str) -> None:
    """Reloads for fresh edit history and focuses the requested text field."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    helpers.reset_web_state(session)
    for _ in range(1 if field == "input" else 2):
        helpers.tab_and_swallow_presentation(session)
    helpers.move_to_top(session)


def _assert_text(
    session: BrowserSession,
    field: str,
    spoken: list[str],
    text: str,
    caret: int,
    selection: tuple[int, int] = (0, 0),
) -> None:
    """Checks speech and the final braille text, cursor, and selection mask."""

    actual_speech, brailled = helpers.capture(session)
    prefix = "Name " if field == "input" else "Bio "
    full = prefix + text + " $l"
    start, end = selection
    mask = "\x00" * (len(prefix) + start) + "\xc0" * (end - start)
    mask += "\x00" * (len(full) - len(mask))
    assert brailled[-1] == helpers.BrailleLine(len(prefix) + caret + 1, full, full, mask)
    assert actual_speech == spoken


@pytest.mark.native_app
def test_cut(web_form_fields: BrowserSession, field: str) -> None:
    """Tests cutting selected text and presenting its clipboard contents."""

    session = web_form_fields
    _focus_field(session, field)
    helpers.move_to_top(session)
    for _ in range(4 if field == "input" else 5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
    _assert_text(
        session,
        field,
        ["Cut selection to clipboard."],
        (" Doe" if field == "input" else " line of bio. Second "),
        0,
    )
    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    assert helpers.speech(session) == [
        "Clipboard contains: Jane" if field == "input" else "Clipboard contains: First"
    ]


@pytest.mark.native_app
@pytest.mark.parametrize("replace_selection", [False, True])
def test_paste(web_form_fields: BrowserSession, field: str, replace_selection: bool) -> None:
    """Tests pasting at the caret and over selected text."""

    session = web_form_fields
    _focus_field(session, field)
    helpers.move_to_top(session)
    for _ in range(4 if field == "input" else 5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert helpers.speech(session) == ["Copied selection to clipboard."]
    if replace_selection:
        helpers.move_to_top(session)
        for _ in range(5 if field == "input" else 6):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3 if field == "input" else 4):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(session)
    else:
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    spoken = ["Pasted contents from clipboard."]
    if replace_selection:
        spoken += helpers.expected_for_browser(session, ["Text unselected."], firefox=[])
    if field == "input":
        text = "Jane Jane" if replace_selection else "Jane DoeJane"
        caret = 9 if replace_selection else 12
    else:
        text = "First First of bio. " if replace_selection else "FirstSecond sentence "
        caret = 11 if replace_selection else 5
    _assert_text(session, field, spoken, text, caret)


@pytest.mark.native_app
@_SELECTION_CLEAR
def test_undo_redo_cut(web_form_fields: BrowserSession, field: str) -> None:
    """Tests restoring a cut selection with undo and removing it again with redo."""

    session = web_form_fields
    _focus_field(session, field)
    helpers.move_to_top(session)
    for _ in range(4 if field == "input" else 5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        field,
        ["undo", "Selection restored."],
        ("Jane Doe" if field == "input" else "First line of bio. "),
        4 if field == "input" else 5,
        (0, 4 if field == "input" else 5),
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        field,
        ["redo", "Text unselected."],
        (" Doe" if field == "input" else " line of bio. Second "),
        0,
    )


@pytest.mark.native_app
@pytest.mark.parametrize("replace_selection", [False, pytest.param(True, marks=_SELECTION_CLEAR)])
def test_undo_redo_paste(
    web_form_fields: BrowserSession, field: str, replace_selection: bool
) -> None:
    """Tests undo and redo of an insertion or replacement from the clipboard."""

    session = web_form_fields
    _focus_field(session, field)
    helpers.move_to_top(session)
    for _ in range(4 if field == "input" else 5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
    assert helpers.speech(session) == ["Copied selection to clipboard."]
    if replace_selection:
        helpers.move_to_top(session)
        for _ in range(5 if field == "input" else 6):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3 if field == "input" else 4):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(session)
    else:
        keyboard.tap_key(keyboard.KEYSYM_END)
        helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    if field == "input":
        spoken = ["undo", "Doe", "selected"] if replace_selection else ["undo"]
        text, caret = "Jane Doe", 8
        selection = (5, 8) if replace_selection else (0, 0)
    else:
        spoken = (
            helpers.expected_for_browser(
                session, ["undo", "Selection restored."], firefox=["undo", "line", "selected"]
            )
            if replace_selection
            else ["undo"]
        )
        text = "First line of bio. " if replace_selection else "Second sentence here."
        caret = 10 if replace_selection else 0
        selection = (6, 10) if replace_selection else (0, 0)
    _assert_text(session, field, spoken, text, caret, selection)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    spoken = ["redo", "Text unselected."] if replace_selection else ["redo"]
    if field == "input":
        text = "Jane Jane" if replace_selection else "Jane DoeJane"
        caret = 9 if replace_selection else 12
    else:
        text = "First First of bio. " if replace_selection else "FirstSecond sentence "
        caret = 11 if replace_selection else 5
    _assert_text(session, field, spoken, text, caret)


@pytest.mark.native_app
def test_undo_redo_delete(web_form_fields: BrowserSession, field: str) -> None:
    """Tests undo and redo of deleting a character without a selection."""

    session = web_form_fields
    _focus_field(session, field)
    keyboard.tap_key(keyboard.KEYSYM_DELETE)
    _assert_text(
        session,
        field,
        (["a"] if field == "input" else ["i"]),
        ("ane Doe" if field == "input" else "irst line of bio. Second "),
        0,
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(
        session, field, ["undo"], ("Jane Doe" if field == "input" else "First line of bio. "), 0
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        field,
        ["redo"],
        ("ane Doe" if field == "input" else "irst line of bio. Second "),
        0,
    )


@pytest.mark.native_app
@_SELECTION_CLEAR
def test_undo_redo_replacement(web_form_fields: BrowserSession, field: str) -> None:
    """Tests undo and redo of typing over selected text."""

    session = web_form_fields
    _focus_field(session, field)
    helpers.move_to_top(session)
    for _ in range(4 if field == "input" else 5):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
    helpers.capture(session)
    keyboard.tap_key(keyboard.KEYSYM_Z)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        field,
        ["undo", "Selection restored."],
        ("Jane Doe" if field == "input" else "First line of bio. "),
        4 if field == "input" else 5,
        (0, 4 if field == "input" else 5),
    )
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_Z)
    _assert_text(
        session,
        field,
        ["redo", "Text unselected."],
        ("z Doe" if field == "input" else "z line of bio. Second "),
        1,
    )


@pytest.mark.native_app
@pytest.mark.parametrize("edit", ["cut", "paste", "replacement"])
def test_undo_restores_selection(web_form_fields: BrowserSession, field: str, edit: str) -> None:
    """Tests restoring the text and selection removed by a cut, paste, or typed replacement."""

    session = web_form_fields
    _focus_field(session, field)
    if edit == "paste":
        helpers.move_to_top(session)
        for _ in range(4 if field == "input" else 5):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(session)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_C)
        assert helpers.speech(session) == ["Copied selection to clipboard."]
        helpers.move_to_top(session)
        for _ in range(5 if field == "input" else 6):
            keyboard.tap_key(keyboard.KEYSYM_RIGHT)
        for _ in range(3 if field == "input" else 4):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(session)
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_V)
    else:
        helpers.move_to_top(session)
        for _ in range(4 if field == "input" else 5):
            keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_RIGHT)
        helpers.capture(session)
        if edit == "cut":
            keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_X)
        else:
            keyboard.tap_key(keyboard.KEYSYM_Z)
    helpers.capture(session)
    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_Z)
    if edit == "paste":
        spoken = (
            ["undo", "Doe", "selected"]
            if field == "input"
            else helpers.expected_for_browser(
                session, ["undo", "Selection restored."], firefox=["undo", "line", "selected"]
            )
        )
        _assert_text(
            session,
            field,
            spoken,
            ("Jane Doe" if field == "input" else "First line of bio. "),
            8 if field == "input" else 10,
            (5, 8) if field == "input" else (6, 10),
        )
    else:
        _assert_text(
            session,
            field,
            ["undo", "Selection restored."],
            ("Jane Doe" if field == "input" else "First line of bio. "),
            4 if field == "input" else 5,
            (0, 4 if field == "input" else 5),
        )
