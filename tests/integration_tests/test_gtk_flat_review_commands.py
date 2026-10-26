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

"""Integration tests for flat review present/spell/phonetic/restrict/clipboard commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, expected_for_gtk, speech, toggle_flat_review

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

# While reviewing the first line, the braille shows that line regardless of whether
# speech is presenting the word, the line, or a single character.
_LINE = BrailleLine(1, "Line one. $l", "Line one. $l", "\x00" * 12)


def _command(session: NativeAppSession, name: str) -> tuple[list[str], list[BrailleLine]]:
    session.orca.call("FlatReviewPresenter", name, True)
    return capture(session)


def _clipboard_contents(session: NativeAppSession) -> list[str]:
    session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
    return speech(session)


@pytest.mark.native_app
def test_present_spell_phonetic(gtk_text_view: NativeAppSession) -> None:
    """Tests presenting, spelling, and phonetically spelling the review word/line/char."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        keyboard.tap_key(keyboard.KEYSYM_KP_BEGIN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        assert _command(session, "PresentItem") == (["Line "], [_LINE])
        assert _command(session, "SpellItem") == (["L", "i", "n", "e", " "], [_LINE])
        assert _command(session, "PhoneticItem") == (
            ["lima", "india", "november", "echo", " "],
            [_LINE],
        )

        assert _command(session, "PresentLine") == (
            expected_for_gtk(["Line one.\n"], gtk4=["Line one."]),
            [_LINE],
        )
        assert _command(session, "SpellLine") == (
            expected_for_gtk(
                ["L", "i", "n", "e", " ", "o", "n", "e", ".", "\n"],
                gtk4=["L", "i", "n", "e", " ", "o", "n", "e", "."],
            ),
            [_LINE],
        )
        assert _command(session, "PhoneticLine") == (
            expected_for_gtk(
                ["lima", "india", "november", "echo", " ", "oscar", "november", "echo", ".", "\n"],
                gtk4=["lima", "india", "november", "echo", " ", "oscar", "november", "echo", "."],
            ),
            [_LINE],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        assert _command(session, "PresentCharacter") == (["L"], [_LINE])
        assert _command(session, "SpellCharacter") == (["lima"], [_LINE])
        assert _command(session, "UnicodeCurrentCharacter") == (["Unicode 004c"], [_LINE])
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_review_word_by_word(gtk_text_view: NativeAppSession) -> None:
    """Tests reviewing a line one word at a time."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        keyboard.tap_key(keyboard.KEYSYM_KP_BEGIN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        assert _command(session, "PresentItem") == (["Line "], [_LINE])
        assert _command(session, "GoNextItem") == (
            expected_for_gtk(["one.\n"], gtk4=["one."]),
            [BrailleLine(6, "Line one. $l", "Line one. $l", "\x00" * 12)],
        )
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_toggle_restrict(gtk_text_view: NativeAppSession) -> None:
    """Tests toggling flat review restriction to the current object and back."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    try:
        assert _command(session, "ToggleRestrict") == (
            ["Flat review restricted to the current object"],
            [
                BrailleLine(
                    0,
                    "Flat review restricted to the current object",
                    "Flat review restricted to the cu",
                    "\x00" * 44,
                )
            ],
        )
        assert _command(session, "ToggleRestrict") == (
            ["Flat review unrestricted"],
            [BrailleLine(0, "Flat review unrestricted", "Flat review unrestricted", "\x00" * 24)],
        )
    finally:
        toggle_flat_review(session)


@pytest.mark.native_app
def test_copy_and_append(gtk_text_view: NativeAppSession) -> None:
    """Tests copying and appending reviewed text to the clipboard."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    toggle_flat_review(session)

    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()

        (copy_key, copy_mods), (append_key, append_mods) = session.orca.available_keybindings(2)
        with (
            session.orca.bound_command("flatReviewCopyHandler", copy_key, copy_mods),
            session.orca.bound_command("flatReviewAppendHandler", append_key, append_mods),
        ):
            assert _command(session, "PresentLine")[0] == expected_for_gtk(
                ["Line one.\n"], gtk4=["Line one."]
            )
            session.orca.press_bound_key(copy_key)
            assert capture(session) == (
                ["Copied contents to clipboard."],
                [
                    BrailleLine(
                        0,
                        "Copied contents to clipboard.",
                        "Copied contents to clipboard.",
                        "\x00" * 29,
                    )
                ],
            )
            assert _clipboard_contents(session) == ["Clipboard contains: Line one."]

            second_line = "Line two has additional words to make it long enough that "
            assert _command(session, "GoNextLine")[0] == [second_line]
            session.orca.press_bound_key(append_key)
            assert capture(session) == (
                ["Appended contents to clipboard."],
                [
                    BrailleLine(
                        0,
                        "Appended contents to clipboard.",
                        "Appended contents to clipboard.",
                        "\x00" * 31,
                    )
                ],
            )
            session.orca.call("ClipboardPresenter", "PresentClipboardContents", True)
            spoken, brailled = capture(session)
            assert spoken == [f"Clipboard contains: Line one.\n{second_line}"]
            assert brailled[-1] == BrailleLine(
                0,
                f"Clipboard contains: Line one. {second_line}",
                "Clipboard contains: Line one. Li",
                "\x00" * 88,
            )

            assert _command(session, "GoNextItem")[0] == ["two "]
            session.orca.press_bound_key(copy_key)
            assert speech(session) == ["Copied contents to clipboard."]
            assert _clipboard_contents(session) == ["Clipboard contains: two "]
    finally:
        toggle_flat_review(session)
