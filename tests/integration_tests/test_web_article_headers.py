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

"""Tests announcements for named and unnamed article headers and footers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


_CONTENTS = [
    ("Before articles.", False),
    ("First article", True),
    ("First summary.", False),
    ("First details.", True),
    ("Named article", True),
    ("Named summary.", False),
    ("Named details.", True),
    ("After articles.", False),
]
_DOWN = [
    (1, ["article", "header"]),
    (2, []),
    (3, ["footer"]),
    (4, ["leaving article.", "article", "header"]),
    (5, []),
    (6, ["footer"]),
    (7, ["leaving article."]),
]
_UP = [
    (6, ["article", "footer"]),
    (5, []),
    (4, ["header"]),
    (3, ["leaving article.", "article", "footer"]),
    (2, []),
    (1, ["header"]),
    (0, ["leaving article."]),
]
_TAB = [
    (1, ["article", "header"]),
    (3, ["footer"]),
    (4, ["leaving article.", "article", "header"]),
    (6, ["footer"]),
]
_SHIFT_TAB = [
    (4, ["header"]),
    (3, ["leaving article.", "article", "footer"]),
    (1, ["header"]),
]


def _set_announcements(session: BrowserSession, enabled: bool, *, say_all: bool = False) -> None:
    helpers.reset_web_state(session)
    presenter = "SayAllPresenter" if say_all else "SpeechPresenter"
    other = "SpeechPresenter" if say_all else "SayAllPresenter"
    session.orca.set(presenter, "AnnounceHeaderAndFooter", enabled)
    session.orca.set(other, "AnnounceHeaderAndFooter", not enabled)
    # Neither the other presentation mode nor the Panels setting controls these roles.
    session.orca.set(presenter, "AnnounceGrouping", not enabled)
    session.orca.set(other, "AnnounceGrouping", enabled)


def _expected_speech(session: BrowserSession, utterances: list[str], enabled: bool) -> list[str]:
    # Firefox exposes these article children as sections, including when named.
    if not enabled or helpers.expected_for_browser(session, False, firefox=True):
        return [item for item in utterances if item not in ("header", "footer")]
    return utterances


def _line_speech(index: int, context: list[str]) -> list[str]:
    text, is_link = _CONTENTS[index]
    return context + [text] + (["link"] if is_link else [])


@pytest.mark.native_app
@pytest.mark.parametrize("enabled", [True, False])
@pytest.mark.parametrize(
    "navigation", ["line", pytest.param("tab", marks=helpers.skip_firefox_caret_tab())]
)
def test_navigate_headers_and_footers(
    web_article_headers: BrowserSession, enabled: bool, navigation: str
) -> None:
    """Tests both directions through named and unnamed containers with the setting on and off."""

    session = web_article_headers
    _set_announcements(session, enabled)
    if navigation == "line":
        directions = [
            (keyboard.KEYSYM_DOWN, [], _DOWN),
            (keyboard.KEYSYM_UP, [], _UP),
        ]
    else:
        directions = [
            (keyboard.KEYSYM_TAB, [], _TAB),
            (keyboard.KEYSYM_TAB, [keyboard.KEYSYM_SHIFT_L], _SHIFT_TAB),
        ]
    for key, modifiers, expected_lines in directions:
        for index, context in expected_lines:
            keyboard.press_chord(modifiers, key)
            text, is_link = _CONTENTS[index]
            mask = ("\xc0" if is_link else "\x00") * len(text)
            assert helpers.capture(session) == (
                _expected_speech(session, _line_speech(index, context), enabled),
                [BrailleLine(1, text, text, mask)],
            )


@pytest.mark.native_app
@pytest.mark.parametrize("enabled", [True, False])
@pytest.mark.parametrize("style", ["line", "sentence"])
def test_say_all_headers_and_footers(
    web_article_headers: BrowserSession, enabled: bool, style: str
) -> None:
    """Tests Say All's independent setting for named and unnamed containers."""

    session = web_article_headers
    _set_announcements(session, enabled, say_all=True)
    session.orca.set("SayAllPresenter", "Style", style)
    if style == "line":
        expected = ["Before articles."]
        for index, context in _DOWN:
            expected.extend(_line_speech(index, context))
    else:
        # Sentence grouping joins each footer link to the following content. Ancestor
        # announcements within a sentence are suppressed; line mode covers every entry.
        expected = [
            "Before articles.",
            "article",
            "header",
            "First article",
            "link",
            "First summary.",
            "footer",
            "First details.",
            "link",
            "Named article",
            "link",
            "Named summary.",
            "footer",
            "Named details.",
            "link",
            "After articles.",
        ]
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == _expected_speech(session, expected, enabled)
