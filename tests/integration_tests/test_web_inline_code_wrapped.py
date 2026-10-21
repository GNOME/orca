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

"""Tests inline code boundaries across a line break."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .apps import browser
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


# Chromium's native LINE ranges return the whole "first\nlast" at both offsets
# 0 and 6. This duplicates speech and braille even with inline announcements off.
_CHROMIUM_LINE_RANGE = pytest.mark.xfail(
    browser.selected_browser() == "chromium",
    reason="Chromium's native LINE range ignores the line break inside code",
    raises=AssertionError,
    strict=True,
)


def _speech(utterances: list[str], enabled: bool) -> list[str]:
    return [item for item in utterances if enabled or item not in ("code", "code end")]


@_CHROMIUM_LINE_RANGE
@pytest.mark.native_app
@pytest.mark.parametrize("enabled", [False, True])
def test_wrapped_inline_code_navigation(
    web_inline_code_wrapped: BrowserSession, enabled: bool
) -> None:
    """Line navigation announces boundaries once and preserves braille in both directions."""

    session = web_inline_code_wrapped
    helpers.reset_web_state(session)
    session.orca.set("SpeechPresenter", "AnnounceInlineCode", enabled)
    lines = [
        (["Before snippets."], "Before snippets."),
        (["Wrapped ", "code", "first"], "Wrapped first"),
        (["last", "code end", " ends."], "last ends."),
        (["After snippets."], "After snippets."),
    ]
    for key, indices in (
        (keyboard.KEYSYM_DOWN, range(1, 4)),
        (keyboard.KEYSYM_UP, range(2, -1, -1)),
    ):
        for index in indices:
            spoken, text = lines[index]
            keyboard.tap_key(key)
            assert helpers.capture(session) == (
                _speech(spoken, enabled),
                [BrailleLine(1, text, text, "\x00" * len(text))],
            )


@pytest.mark.native_app
@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("style", [pytest.param("line", marks=_CHROMIUM_LINE_RANGE), "sentence"])
def test_wrapped_inline_code_say_all(
    web_inline_code_wrapped: BrowserSession, enabled: bool, style: str
) -> None:
    """Both Say All styles announce one pair of boundaries for a wrapped snippet."""

    session = web_inline_code_wrapped
    helpers.reset_web_state(session)
    session.orca.set("SayAllPresenter", "AnnounceInlineCode", enabled)
    session.orca.set("SayAllPresenter", "Style", style)
    code = ["first", "last"]
    if style == "sentence":
        code = helpers.expected_for_browser(session, code, firefox=["first\nlast"])
    keyboard.tap_key(keyboard.KEYSYM_KP_ADD)
    assert helpers.speech(session) == _speech(
        [
            "Before snippets.",
            "Wrapped ",
            "code",
            *code,
            "code end",
            " ends.",
            "After snippets.",
        ],
        enabled,
    )
