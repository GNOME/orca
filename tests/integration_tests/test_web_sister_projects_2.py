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

"""Tests a tall icon beside a name does not pull in the description on the line below it."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


# The fixture models Wikipedia's sister-projects box faithfully: inline-block cells (so the icon
# and description share the item's block) with a 62px icon over a shorter name and the description
# on the line below. The icon overlaps the description's rect, but it must not drag it onto the
# icon+name line.
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
    (["Wikimedia coordination"], "Wikimedia coordination"),
    (["Wikibooks logo", "image link", "Wikibooks", "link"], "Wikibooks logo image Wikibooks "),
    (["Free textbooks and manuals"], "Free textbooks and manuals"),
    (["Wikidata logo", "image link", "Wikidata", "link"], "Wikidata logo image Wikidata "),
    (["Free knowledge base"], "Free knowledge base"),
    (
        ["Wikifunctions logo", "image link", "Wikifunctions", "link"],
        "Wikifunctions logo image Wikifunctions ",
    ),
    (["Catalog of functions"], "Catalog of functions"),
    (["leaving list.", "After the projects."], "After the projects."),
]


@pytest.mark.native_app
def test_line_down_keeps_icon_and_name_but_not_the_description(
    web_sister_projects_2: NativeAppSession,
) -> None:
    """Tests each card reads as icon and name on one line, then the description on the next."""

    session = web_sister_projects_2
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    for expected_speech, expected_line in _DOWN_LINES:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        spoken, braille = helpers.capture(session)
        assert spoken == expected_speech
        assert [line.full for line in braille] == [expected_line]
