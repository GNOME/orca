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

"""Tests that a wrapped inline list item does not cause its line to be re-read."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


# The last item of this inline "Recently featured" list wraps across two visual lines.
# Arrowing down through the box must reach the line below it without re-reading the list
# line: the second visual line advances to "Line below", it does not rebuild the first.
#
# Chromium gives us the full link as the line at offset even though the text wraps.
_DOWN_LINES = [
    (
        [
            "Recently featured: ",
            "List with 3 items",
            "The Path to Rome",
            "link",
            " ·",
            "Morris Park Aerodrome",
            "link",
            " ·",
            '"',
            "The One Where ",
            "link",
        ],
        (
            "Recently featured: The Path to Rome · Morris Park Aerodrome · "
            '"The One Where Michael Leaves'
        ),
    ),
    (["Michael Leaves", "link", '"'], 'The One Where Michael Leaves "'),
    (["leaving list.", "Line below the box."], "Line below the box."),
]


@pytest.mark.native_app
def test_line_down_past_wrapped_inline_list(web_inline_list_wrap: BrowserSession) -> None:
    """Tests that arrowing down past a wrapped inline list does not re-read the list line."""

    session = web_inline_list_wrap
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    for expected_speech, expected_line in _DOWN_LINES:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]


@pytest.mark.native_app
def test_flat_review_horizontal_links(web_inline_list_wrap: BrowserSession) -> None:
    """Tests flat review of a horizontal list of links separated by punctuation."""

    session = web_inline_list_wrap
    helpers.reset_web_state(session)
    keyboard.tap_key(keyboard.KEYSYM_2)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    tracking = session.orca.get("FlatReviewPresenter", "FocusTracking")
    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    helpers.toggle_flat_review(session)

    text = 'Home  \u00b7 News  \u00b7 " Help "'
    full = f"{text} $l"
    try:
        for command, line in (
            ("GoNextLine", text),
            ("GoNextLine", "After the links."),
            ("GoPreviousLine", text),
        ):
            session.orca.call("FlatReviewPresenter", command, True)
            spoken, brailled = helpers.capture(session)
            assert spoken == [line]
            expected = f"{line} $l"
            assert brailled[-1] == BrailleLine(1, expected, expected, "\x00" * len(expected))

        for command, word, visible, cursor in (
            ("GoStartOfLine", "H", full, 1),
            ("PresentItem", "Home", full, 1),
            ("GoNextItem", "\u00b7", ' \u00b7 News  \u00b7 " Help " $l', 2),
            ("GoNextItem", "News", 'News  \u00b7 " Help " $l', 1),
            ("GoNextItem", "\u00b7", ' \u00b7 " Help " $l', 2),
            ("GoNextItem", '"', '" Help " $l', 1),
            ("GoNextItem", "Help", 'Help " $l', 1),
            ("GoNextItem", '"', '" $l', 1),
            ("GoPreviousItem", "Help", 'Help " $l', 4),
            ("GoPreviousItem", '"', '" Help " $l', 1),
            ("GoPreviousItem", "\u00b7", ' \u00b7 " Help " $l', 2),
            ("GoPreviousItem", "News", 'News  \u00b7 " Help " $l', 4),
            ("GoPreviousItem", "\u00b7", ' \u00b7 News  \u00b7 " Help " $l', 2),
            ("GoPreviousItem", "Home", full, 4),
        ):
            session.orca.call("FlatReviewPresenter", command, True)
            spoken, brailled = helpers.capture(session)
            assert spoken == [word]
            assert brailled[-1] == BrailleLine(cursor, full, visible, "\x00" * len(full))
    finally:
        helpers.toggle_flat_review(session)
        session.orca.set("FlatReviewPresenter", "FocusTracking", tracking)


@pytest.mark.native_app
def test_flat_review_line_speech_matches_reviewed_text(
    web_inline_list_wrap: BrowserSession,
) -> None:
    """Tests that line speech uses the reviewed text rather than expanding into other objects."""

    session = web_inline_list_wrap
    helpers.reset_web_state(session)
    tracking = session.orca.get("FlatReviewPresenter", "FocusTracking")
    session.orca.set("FlatReviewPresenter", "FocusTracking", 0)
    helpers.toggle_flat_review(session)
    try:
        for command in ["GoNextLine"] * 3 + ["GoPreviousLine"] * 3:
            session.orca.call("FlatReviewPresenter", command, True)
            spoken, brailled = helpers.capture(session)
            assert brailled
            assert "".join(spoken) == brailled[-1].full.removesuffix(" $l")
    finally:
        helpers.toggle_flat_review(session)
        session.orca.set("FlatReviewPresenter", "FocusTracking", tracking)
