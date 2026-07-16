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

"""Tests line navigation of a multi-column list of icon-and-text items."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


_DOWN_LINES = [
    (
        ["Wikipedia is hosted by the Wikimedia Foundation, which hosts other projects."],
        "Wikipedia is hosted by the Wikimedia Foundation, which hosts other projects.",
    ),
    (
        ["List with 6 items", "Commons logo", "image link", "Commons", "link"],
        "Commons logo image Commons ",
    ),
    (["Free media repository"], "Free media repository"),
    (["MediaWiki logo", "image link", "MediaWiki", "link"], "MediaWiki logo image MediaWiki "),
    (["Wiki software development"], "Wiki software development"),
    (["Meta-Wiki logo", "image link", "Meta-Wiki", "link"], "Meta-Wiki logo image Meta-Wiki "),
    (["Wikimedia project coordination"], "Wikimedia project coordination"),
    (["Wikibooks logo", "image link", "Wikibooks", "link"], "Wikibooks logo image Wikibooks "),
    (["Free textbooks and manuals"], "Free textbooks and manuals"),
    (["Wikidata logo", "image link", "Wikidata", "link"], "Wikidata logo image Wikidata "),
    (["Free knowledge base"], "Free knowledge base"),
    (
        ["Wikifunctions logo", "image link", "Wikifunctions", "link"],
        "Wikifunctions logo image Wikifunctions ",
    ),
    (["Catalog of computer functions"], "Catalog of computer functions"),
    (["leaving list.", "After the projects."], "After the projects."),
]

_UP_LINES = [
    (["List with 6 items", "Catalog of computer functions"], "Catalog of computer functions"),
    (
        ["Wikifunctions logo", "image link", "Wikifunctions", "link"],
        "Wikifunctions logo image Wikifunctions ",
    ),
    (["Free knowledge base"], "Free knowledge base"),
    (["Wikidata logo", "image link", "Wikidata", "link"], "Wikidata logo image Wikidata "),
    (["Free textbooks and manuals"], "Free textbooks and manuals"),
    (["Wikibooks logo", "image link", "Wikibooks", "link"], "Wikibooks logo image Wikibooks "),
    (["Wikimedia project coordination"], "Wikimedia project coordination"),
    (["Meta-Wiki logo", "image link", "Meta-Wiki", "link"], "Meta-Wiki logo image Meta-Wiki "),
    (["Wiki software development"], "Wiki software development"),
    (["MediaWiki logo", "image link", "MediaWiki", "link"], "MediaWiki logo image MediaWiki "),
    (["Free media repository"], "Free media repository"),
    (["Commons logo", "image link", "Commons", "link"], "Commons logo image Commons "),
    (
        [
            "leaving list.",
            "Wikipedia is hosted by the Wikimedia Foundation, which hosts other projects.",
        ],
        "Wikipedia is hosted by the Wikimedia Foundation, which hosts other projects.",
    ),
    (["Wikipedia's sister projects", "heading 2"], "Wikipedia's sister projects h2"),
]


def _assert_each_line(session, key, lines) -> None:
    """Arrows once per entry and asserts each landed on a single line with the whole content."""

    for expected_speech, expected_line in lines:
        keyboard.tap_key(key)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]


@pytest.mark.native_app
def test_line_down_keeps_list_rows_separate(web_sister_projects: NativeAppSession) -> None:
    """Tests that arrowing down the multi-column list keeps each row on its own line."""

    session = web_sister_projects
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    _assert_each_line(session, keyboard.KEYSYM_DOWN, _DOWN_LINES)


@pytest.mark.native_app
def test_line_up_keeps_list_rows_separate(web_sister_projects: NativeAppSession) -> None:
    """Tests that arrowing up the multi-column list keeps each row on its own line."""

    session = web_sister_projects
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)
    helpers.capture(session)
    _assert_each_line(session, keyboard.KEYSYM_UP, _UP_LINES)
