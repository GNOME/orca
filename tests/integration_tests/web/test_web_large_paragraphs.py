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

"""Tests paragraph navigation across the full-filtering cutoff."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest
from Xlib import X, display  # type: ignore[import-untyped]

from tests.integration_tests.harness import keyboard
from tests.integration_tests.helpers import BrailleLine, capture, move_to_top

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import BrowserSession


def _next(session: BrowserSession, keysym: int) -> tuple[list[str], list[BrailleLine]]:
    keyboard.tap_key(keysym)
    return capture(session, overall=10)


def _previous(session: BrowserSession, keysym: int) -> tuple[list[str], list[BrailleLine]]:
    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keysym)
    return capture(session, overall=10)


def _focus_paragraph_dialog() -> None:
    """Focuses our dialog on Xvfb, which has no window manager."""

    connection = display.Display()
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            for window in connection.screen().root.query_tree().children:
                if not (window.get_wm_name() or "").startswith("Paragraphs: "):
                    continue
                if window.get_attributes().map_state != X.IsViewable:
                    continue
                window.configure(stack_mode=X.Above)
                window.set_input_focus(X.RevertToParent, X.CurrentTime)
                connection.sync()
                return
            time.sleep(0.05)
        raise RuntimeError("Paragraph dialog did not appear")
    finally:
        connection.close()


def _row_braille(text: str) -> BrailleLine:
    full = f" Paragraph column header {text}"
    return BrailleLine(1, full, text[:32], "\x00" * len(full))


@pytest.mark.native_app
def test_paragraph_filter_cutoff(web_large_paragraphs: BrowserSession) -> None:
    """Tests navigation and dialog rows across the 2500-candidate cutoff."""

    session = web_large_paragraphs
    # Key echo can be interrupted while the full paragraph filter runs.
    session.orca.set("TypingEchoPresenter", "KeyEchoEnabled", False)
    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_P) == (
        ["main content", "First valid paragraph."],
        [BrailleLine(1, "First valid paragraph.", "First valid paragraph.", "\x00" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["After short paragraphs."],
        [BrailleLine(1, "After short paragraphs.", "After short paragraphs.", "\x00" * 23)],
    )

    assert _previous(session, keyboard.KEYSYM_P) == (
        ["First valid paragraph."],
        [BrailleLine(1, "First valid paragraph.", "First valid paragraph.", "\x00" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in short paragraph", "link"],
        [BrailleLine(1, "Link in short paragraph", "Link in short paragraph", "\xc0" * 23)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["After short paragraphs."],
        [BrailleLine(1, "After short paragraphs.", "After short paragraphs.", "\x00" * 23)],
    )

    assert _previous(session, keyboard.KEYSYM_B) == (
        ["leaving main content.", "Add one paragraph", "button"],
        [BrailleLine(1, "Add one paragraph button", "Add one paragraph button", "\x00" * 24)],
    )

    assert _next(session, keyboard.KEYSYM_RETURN) == ([], [])

    move_to_top(session)

    assert _next(session, keyboard.KEYSYM_P) == (
        ["main content", "First valid paragraph."],
        [BrailleLine(1, "First valid paragraph.", "First valid paragraph.", "\x00" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["x"],
        [BrailleLine(1, "x", "x", "\x00")],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["xy"],
        [BrailleLine(1, "xy", "xy", "\x00" * 2)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in short paragraph", "link"],
        [BrailleLine(1, "Link in short paragraph", "Link in short paragraph", "\xc0" * 23)],
    )

    assert _previous(session, keyboard.KEYSYM_P) == (
        ["xy"],
        [BrailleLine(1, "xy", "xy", "\x00" * 2)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in short paragraph", "link"],
        [BrailleLine(1, "Link in short paragraph", "Link in short paragraph", "\xc0" * 23)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["After short paragraphs."],
        [BrailleLine(1, "After short paragraphs.", "After short paragraphs.", "\x00" * 23)],
    )

    assert _next(session, keyboard.KEYSYM_U) == (
        ["Link in long paragraph", "link"],
        [BrailleLine(1, "Link in long paragraph", "Link in long paragraph", "\xc0" * 22)],
    )

    assert _next(session, keyboard.KEYSYM_P) == (
        ["Following accepted paragraph."],
        [
            BrailleLine(
                1, "Following accepted paragraph.", "Following accepted paragraph.", "\x00" * 29
            )
        ],
    )

    for _ in range(5):
        _next(session, keyboard.KEYSYM_P)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", True)
    keyboard.press_chord([keyboard.KEYSYM_ALT_L, keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_P)
    assert capture(session, quiescence=0.1, wait_async=True) == (
        ["Loading.  Please wait."],
        [BrailleLine(0, "Loading.  Please wait.", "Loading.  Please wait.", "\x00" * 22)],
    )
    _focus_paragraph_dialog()

    assert capture(session, wait_async=True) == (
        [
            "Paragraphs: 2500 items found dialog",
            "table with 2500 rows 1 column",
            "Visible heading text.",
            "11 of 2500",
        ],
        [
            BrailleLine(
                1,
                "orca application Paragraphs: 2500 items found dialog",
                "Paragraphs: 2500 items found dia",
                "\x00" * 52,
            ),
            _row_braille("Visible heading text."),
        ],
    )

    rows = [
        "First valid paragraph.",
        "x",
        "xy",
        "Link in short paragraph",
        "After short paragraphs.",
        "With Link in long paragraph and surrounding text.",
        "Following accepted paragraph.",
        "Long paragraph preview. " * 8 + "Long par...",
        "Text after leading spaces.",
        "Visible paragraph text.",
    ]
    for position, text in enumerate(rows, 1):
        key = keyboard.KEYSYM_HOME if position == 1 else keyboard.KEYSYM_DOWN
        assert _next(session, key) == (
            [text, f"{position} of 2500"],
            [_row_braille(text)],
        )

    assert _next(session, keyboard.KEYSYM_DOWN) == (
        ["Visible heading text.", "11 of 2500", "selected"],
        [
            _row_braille("Visible heading text."),
            BrailleLine(0, "selected", "selected", "\x00" * 8),
        ],
    )

    assert _next(session, keyboard.KEYSYM_UP) == (
        ["Visible paragraph text.", "10 of 2500", "selected"],
        [
            _row_braille("Visible heading text."),
            _row_braille("Visible paragraph text."),
            BrailleLine(0, "selected", "selected", "\x00" * 8),
        ],
    )

    assert _next(session, keyboard.KEYSYM_UP) == (
        ["Text after leading spaces.", "9 of 2500", "selected"],
        [
            _row_braille("Visible paragraph text."),
            _row_braille("Text after leading spaces."),
            BrailleLine(0, "selected", "selected", "\x00" * 8),
        ],
    )

    _next(session, keyboard.KEYSYM_ESCAPE)
    session.orca.set("SpeechPresenter", "SpeakPositionInSet", False)
