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

"""Tests presentation of links whose text is inside a nested inline element."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from orca.output_reader import SpeechRecord

from .harness import keyboard
from .helpers import BrailleLine, capture, move_to_bottom, move_to_top, reset_web_state, speech

if TYPE_CHECKING:
    from .orca_fixtures import WebSession

_PLAIN = "\x00"
_LINK = "\xc0"


def _line(full: str, mask: str) -> BrailleLine:
    return BrailleLine(1, full, full[:32], mask)


@pytest.mark.web
def test_line_navigation_over_nested_link_text(web_nested_link_text: WebSession) -> None:
    """Tests line navigation over nested link text."""

    session = web_nested_link_text
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Jump to the ", "glossary entry for RLS", "link", " now."],
        [
            _line(
                "Jump to the glossary entry for RLS now.",
                _PLAIN * 12 + _LINK * 22 + _PLAIN * 5,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        # KNOWN ISSUE: "link" should be presented after "localStorage"
        ["Jump to the ", "localStorage", " glossary entry now."],
        [
            _line(
                "Jump to the localStorage glossary entry now.",
                _PLAIN * 12 + _LINK * 12 + _PLAIN * 20,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        # KNOWN ISSUE: "link" should be presented after "bold term"
        ["Jump to the ", "bold term", " glossary entry now."],
        [
            _line(
                "Jump to the bold term glossary entry now.",
                _PLAIN * 12 + _LINK * 9 + _PLAIN * 20,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        # KNOWN ISSUE: link should be presented after "revoke"; not before
        ["Jump to the ", "grant/", "link", "revoke", " glossary entry now."],
        [
            _line(
                "Jump to the grant/revoke revoke glossary entry now.",
                _PLAIN * 12 + _LINK * 12 + _PLAIN + _LINK * 6 + _PLAIN * 20,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Jump to the ", "sessionStorage", "link"],
        [_line("Jump to the sessionStorage", _PLAIN * 12 + _LINK * 14)],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        # KNOWN ISSUE: link should be presented after "two"; not before
        ["Jump to the ", "one", " and ", "link", "two", " glossary entry now."],
        [
            _line(
                "Jump to the one one and two two glossary entry now.",
                _PLAIN * 12 + _LINK * 3 + _PLAIN + _LINK * 11 + _PLAIN + _LINK * 3 + _PLAIN * 20,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        # KNOWN ISSUE: "link" should be presented after "wrapped"
        ["Jump to the ", "wrapped", " glossary entry now."],
        [
            _line(
                "Jump to the wrapped glossary entry now.",
                _PLAIN * 12 + _LINK * 7 + _PLAIN * 20,
            )
        ],
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert capture(session) == (
        ["Jump to the ", "chart", "image link", " glossary entry now."],
        [
            _line(
                "Jump to the chart image glossary entry now.",
                _PLAIN * 12 + _LINK * 11 + _PLAIN * 20,
            )
        ],
    )


@pytest.mark.web
def test_tab_navigation_over_nested_link_text(web_nested_link_text: WebSession) -> None:
    """Tests tab navigation over nested link text."""

    session = web_nested_link_text
    reset_web_state(session)

    for text in (
        "glossary entry for RLS",
        "localStorage",
        "bold term",
        "grant/revoke",
        "sessionStorage",
        "one and two",
        "wrapped",
        "chart",
    ):
        keyboard.tap_key(keyboard.KEYSYM_TAB)
        assert capture(session) == (
            [text, "link"],
            [BrailleLine(1, text, text, _LINK * len(text))],
        )


@pytest.mark.web
def test_say_all_over_nested_link_text(web_nested_link_text: WebSession) -> None:
    """Tests Say All over nested link text."""

    session = web_nested_link_text
    reset_web_state(session)
    move_to_bottom(session)
    move_to_top(session)

    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert speech(session) == [
        "Nested link text",
        "Jump to the ",
        "glossary entry for RLS",
        "link",
        " now.",
        "Jump to the ",
        "localStorage",
        "link",
        " glossary entry now.",
        "Jump to the ",
        "bold term",
        "link",
        " glossary entry now.",
        "Jump to the ",
        # KNOWN ISSUE: link should be presented after "revoke"; not before
        "grant/",
        "link",
        "revoke",
        " glossary entry now.",
        "Jump to the ",
        "sessionStorage",
        "link",
        "Jump to the ",
        # KNOWN ISSUE: link should be presented once, after "two"; not twice, before each run
        "one",
        "link",
        " and ",
        "link",
        "two",
        " glossary entry now.",
        "Jump to the ",
        "wrapped",
        "link",
        " glossary entry now.",
        "Jump to the ",
        "chart",
        "image",
        "link",
        " glossary entry now.",
        "After.",
    ]


@pytest.mark.web
def test_nested_link_text_uses_the_hyperlink_voice(web_nested_link_text: WebSession) -> None:
    """Tests that nested link text uses the hyperlink voice."""

    session = web_nested_link_text
    move_to_top(session)

    for text in ("glossary entry for RLS", "localStorage", "bold term"):
        session.reader.reset()
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        record = session.reader.wait_for_speech(text, timeout=3.0)
        assert record.voice_type == "hyperlink", (
            f"{text!r}: expected the hyperlink voice, got {record.voice_type!r}"
        )

    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    record = session.reader.wait_for_speech(" glossary entry now.", timeout=3.0)
    assert record.voice_type == "default", (
        f"Text outside the link: expected the default voice, got {record.voice_type!r}"
    )


@pytest.mark.web
def test_say_all_uses_the_hyperlink_voice(web_nested_link_text: WebSession) -> None:
    """Tests that Say All uses the hyperlink voice for nested link text."""

    session = web_nested_link_text
    reset_web_state(session)
    move_to_bottom(session)
    move_to_top(session)

    session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    records = session.reader.drain(quiescence_timeout=0.3, overall_timeout=15.0)
    voices = {r.text: r.voice_type for r in records if isinstance(r, SpeechRecord)}

    for text in ("glossary entry for RLS", "localStorage", "bold term", "revoke"):
        assert voices.get(text) == "hyperlink", (
            f"{text!r}: expected the hyperlink voice, got {voices.get(text)!r}"
        )

    assert voices.get("Jump to the ") == "default"
