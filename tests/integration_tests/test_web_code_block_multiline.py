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

"""Line navigation to the last line of a multi-line code block with no blank line."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from orca.output_reader import BrailleRecord, SpeechRecord

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


@pytest.mark.native_app
def test_line_navigation_to_the_last_line(web_code_block_multiline: BrowserSession) -> None:
    """Tests line navigation to the last line."""

    session = web_code_block_multiline
    helpers.reset_web_state(session)

    for _step in range(3):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        helpers.speech(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == [
        "Build with voice and video 4 . characters : no",
    ]

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.speech(session) == ["leaving code.", "End of report."]


@pytest.mark.native_app
@pytest.mark.parametrize("kind", ["unnamed", "named", "standalone"])
def test_code_block_entry_announcements(
    web_code_block_multiline: BrowserSession, kind: str
) -> None:
    """Announces each boundary once in either direction, preserving the block's label."""

    session = web_code_block_multiline
    helpers.reset_web_state(session)
    if kind != "unnamed":
        for _step in range(5 if kind == "named" else 8):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.speech(session)
        lines = ["first line", "last line"]
        spoken_lines = lines
        if kind == "named":
            before, after = "End of report.", "After example."
            label = ["Example"]
        else:
            before, after = "After example.", "After standalone."
            # Chromium treats a standalone pre as text and suppresses its name.
            label = helpers.expected_for_browser(session, [], firefox=["Standalone"])
    else:
        lines = [
            "Build with GStreamer support.. : yes",
            "Build for GStreamer version... : 1.0",
            "Build with D-Bus support...... : yes",
            "Build with voice and video.... : no",
        ]
        spoken_lines = [
            "Build with GStreamer support.. : yes",
            "Build for GStreamer version... : 1.0",
            "Build with D-Bus support 6 . characters : yes",
            "Build with voice and video 4 . characters : no",
        ]
        before, after = "The build reports:", "End of report."
        label = []

    braille_label = " ".join(label) + " " if kind == "standalone" and label else ""
    for key, indices in (
        (keyboard.KEYSYM_DOWN, range(len(lines))),
        (keyboard.KEYSYM_UP, range(len(lines) - 1, -1, -1)),
    ):
        for index in indices:
            keyboard.tap_key(key)
            spoken, brailled = helpers.capture(session)
            expected = []
            if index == indices.start:
                expected += [*label, "code"]
            expected += [spoken_lines[index]]
            assert spoken == expected
            full = braille_label + lines[index] + " $l"
            assert brailled[-1] == helpers.BrailleLine(
                len(braille_label) + 1, full, full[:32], "\x00" * len(full)
            )

        keyboard.tap_key(key)
        spoken, brailled = helpers.capture(session)
        text = after if key == keyboard.KEYSYM_DOWN else before
        assert spoken == ["leaving code.", text]
        assert brailled[-1] == helpers.BrailleLine(1, text, text, "\x00" * len(text))


@pytest.mark.native_app
@pytest.mark.parametrize(
    "punctuation,indentation",
    [("some", False), ("some", True), ("most", False), ("none", False), ("all", False)],
)
def test_code_punctuation(
    web_code_block_multiline: BrowserSession, punctuation: str, indentation: bool
) -> None:
    """Code requests all punctuation without changing indentation or subsequent prose."""

    session = web_code_block_multiline
    helpers.reset_web_state(session)
    session.orca.set("SpeechManager", "PunctuationLevel", punctuation)
    session.orca.set("SpeechPresenter", "SpeakIndentation", indentation)
    try:
        for _ in range(11):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            helpers.speech(session)

        lines = ["if (ready) {", "    return 0;", "}"]
        override = "all" if punctuation in ("some", "most") else ""
        for key, indices in (
            (keyboard.KEYSYM_DOWN, range(3)),
            (keyboard.KEYSYM_UP, range(2, -1, -1)),
        ):
            for index in indices:
                keyboard.tap_key(key)
                records = session.reader.drain()
                spoken = [r for r in records if isinstance(r, SpeechRecord)]
                content = [r for r in spoken if r.voice_type != "system"]
                assert [(r.text, r.punctuation) for r in content] == [(lines[index], override)]
                assert all(r.punctuation == "" for r in spoken if r.voice_type == "system")
                if indentation and index == 1:
                    assert "4 spaces" in [r.text.strip() for r in spoken]
                brailled = [r for r in records if isinstance(r, BrailleRecord)]
                assert brailled[-1].full == lines[index] + " $l"

            keyboard.tap_key(key)
            records = session.reader.drain()
            spoken = [r for r in records if isinstance(r, SpeechRecord)]
            after = "After punctuation." if key == keyboard.KEYSYM_DOWN else "After standalone."
            assert after in [r.text for r in spoken]
            assert all(r.punctuation == "" for r in spoken)
        assert session.orca.get("SpeechManager", "PunctuationLevel") == punctuation
    finally:
        session.orca.set("SpeechManager", "PunctuationLevel", "some")
        session.orca.set("SpeechPresenter", "SpeakIndentation", False)


@pytest.mark.native_app
def test_say_all_code_punctuation(web_code_block_multiline: BrowserSession) -> None:
    """Say All carries the override for code and leaves following prose unchanged."""

    session = web_code_block_multiline
    helpers.reset_web_state(session)
    session.orca.set("SayAllPresenter", "Style", "line")
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    records = session.reader.drain()
    spoken = [r for r in records if isinstance(r, SpeechRecord)]
    for line in ("if (ready) {", "    return 0;", "}"):
        matching = [r for r in spoken if r.text.rstrip("\n") == line]
        assert matching, (line, spoken)
        assert all(r.punctuation == "all" for r in matching)
    assert [(r.text, r.punctuation) for r in spoken if r.text == "After punctuation."] == [
        ("After punctuation.", "")
    ]
