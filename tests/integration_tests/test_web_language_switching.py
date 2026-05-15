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

"""Tests that automatic language switching picks the right synthesizer voice per item."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_ITEMS: tuple[tuple[str, str], ...] = (
    ("English", "en"),
    ("Español", "es"),
    ("Français", "fr"),
    ("Deutsch", "de"),
    ("Italiano", "it"),
    ("Português", "pt"),
    ("Nederlands", "nl"),
    ("Svenska", "sv"),
)


@pytest.mark.native_app
def test_arrowing_switches_voice_language_per_item(web_languages: NativeAppSession) -> None:
    """Each list item is spoken with a voice whose language matches its lang attribute."""

    session = web_languages
    session.orca.set("SpeechManager", "AutoLanguageSwitching", True)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)

    for item_text, expected_language in _ITEMS:
        session.reader.reset()
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        record = session.reader.wait_for_speech(item_text, timeout=3.0)
        assert record.language == expected_language, (
            f"Item {item_text!r}: expected language {expected_language!r}, got {record.language!r}"
        )


@pytest.mark.native_app
def test_arrowing_does_not_switch_voice_when_disabled(web_languages: NativeAppSession) -> None:
    """With auto-language-switching off, every item is spoken with the same voice language."""

    session = web_languages
    session.orca.set("SpeechManager", "AutoLanguageSwitching", False)

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_HOME)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)

    seen: list[tuple[str, str]] = []
    for item_text, _ in _ITEMS:
        session.reader.reset()
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        record = session.reader.wait_for_speech(item_text, timeout=3.0)
        seen.append((item_text, record.language))

    languages = {language for _, language in seen}
    assert len(languages) == 1, f"Expected one voice language across items, saw: {seen}"
