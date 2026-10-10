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

"""Tests line navigation when objects are temporarily hidden with aria-hidden."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


_LINES = [
    (
        ["1. Introduction", "heading 1"],
        BrailleLine(1, "1. Introduction h1", "1. Introduction h1", "\x00" * 18),
    ),
    (
        [
            "In his book Topics in Analytic Number Theory\xa0",
            "Reference\xa013",
            "link",
            ", Hans Rademacher ",
        ],
        BrailleLine(
            1,
            "In his book Topics in Analytic Number Theory\xa0Reference\xa0 13, Hans Rademacher ",
            "In his book Topics in Analytic N",
            "\x00" * 45 + "\xc0" * 13 + "\x00" * 18,
        ),
    ),
    (
        ["gave a partial fraction decomposition of the partition generating function "],
        BrailleLine(
            1,
            "gave a partial fraction decomposition of the partition generating function ",
            "gave a partial fraction decompos",
            "\x00" * 75,
        ),
    ),
    (
        [
            (
                "product Underscript j greater than or equals 1 Endscripts "
                "left parenthesis 1 minus x Superscript j Baseline "
                "right parenthesis Superscript negative 1"
            ),
            "tree",
            ".",
            " He conjectured that the decomposition of the generating ",
        ],
        BrailleLine(
            1,
            "⠐⠩⠚⠀⠨⠂⠱⠀⠼⠂⠻⠷⠂⠤⠭⠘⠚⠐⠾⠘⠤⠂ tree. He conjectured that the decomposition of the generating ",
            "⠐⠩⠚⠀⠨⠂⠱⠀⠼⠂⠻⠷⠂⠤⠭⠘⠚⠐⠾⠘⠤⠂ tree. He ",
            "\x00" * 85,
        ),
    ),
    (
        [
            "function of partitions into at most\xa0",
            "upper N",
            "image",
            " parts (equivalently, into parts from ",
        ],
        BrailleLine(
            1,
            "function of partitions into at most\xa0⠠⠝ image parts (equivalently, into parts from ",
            "function of partitions into at m",
            "\x00" * 82,
        ),
    ),
    (
        ["StartSet 1 comma ellipsis comma upper N EndSet", "tree", "),"],
        BrailleLine(1, "⠨⠷⠂⠠⠀⠄⠄⠄⠠⠀⠠⠝⠨⠾ tree),", "⠨⠷⠂⠠⠀⠄⠄⠄⠠⠀⠠⠝⠨⠾ tree),", "\x00" * 21),
    ),
    (
        ["End of introduction", "heading 2"],
        BrailleLine(1, "End of introduction h2", "End of introduction h2", "\x00" * 22),
    ),
]


@pytest.mark.native_app
def test_line_navigation_with_temporary_aria_hidden(
    web_temporary_aria_hidden: BrowserSession,
) -> None:
    """Tests temporarily hidden objects and surrounding text are read in both directions."""

    session = web_temporary_aria_hidden
    helpers.reset_web_state(session)

    for key, lines in (
        (keyboard.KEYSYM_DOWN, _LINES[1:]),
        (keyboard.KEYSYM_UP, reversed(_LINES[:-1])),
    ):
        for expected_speech, expected_braille in lines:
            keyboard.tap_key(key)
            spoken, brailled = helpers.capture(session, wait_async=True)
            assert spoken == expected_speech
            assert brailled[-1] == expected_braille
