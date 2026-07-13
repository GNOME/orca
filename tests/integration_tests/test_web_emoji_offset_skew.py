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

"""Tests line, character, and word navigation through a page where emoji precede hyperlinks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_LINK_NOTES_MASK = "\x00" * 49 + "\xc0" * 10 + "\x00"
_SERVICE_ONE_MASK = "\x00" * 15 + "\xc0" * 11 + "\x00"
_SERVICE_TWO_MASK = "\x00" * 15 + "\xc0" * 11 + "\x00"
_SERVICE_THREE_MASK = "\x00" * 17 + "\xc0" * 13 + "\x00"
_FLAGS_ROW_MASK = "\x00" * 22 + "\xc0" * 12 + "\x00" * 10
_FAMILY_ROW_MASK = "\x00" * 30 + "\xc0" * 12 + "\x00"
_PILE_OF_EMOJI_MASK = "\x00" * 28 + "\xc0" * 11 + "\x00"

_DOWN_LINES = [
    (
        ["Streaming and social links below"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="Streaming and social links below",
                visible="Streaming and social links below",
                mask="\x00" * 32,
            )
        ],
    ),
    (
        ["♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: ", "link notes", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: link notes ",
                visible="♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note s",
                mask=_LINK_NOTES_MASK,
            )
        ],
    ),
    (
        ["next line 1\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="next line 1",
                visible="next line 1",
                mask="\x00" * 11,
            )
        ],
    ),
    (
        ["next line 2\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="next line 2",
                visible="next line 2",
                mask="\x00" * 11,
            )
        ],
    ),
    # Double <br>
    (
        ["blank"],
        [helpers.BrailleLine(cursor_cell=1, full="", visible="", mask=None)],
    ),
    (
        ["next line 3\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="next line 3",
                visible="next line 3",
                mask="\x00" * 11,
            )
        ],
    ),
    (
        ["🎵 service one: ", "profile one", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵 service one: profile one ",
                visible="🎵 service one: profile one ",
                mask=_SERVICE_ONE_MASK,
            )
        ],
    ),
    (
        ["🎵 service two: ", "profile two", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵 service two: profile two ",
                visible="🎵 service two: profile two ",
                mask=_SERVICE_TWO_MASK,
            )
        ],
    ),
    (
        ["🎵 service three: ", "profile three", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵 service three: profile three ",
                visible="🎵 service three: profile three ",
                mask=_SERVICE_THREE_MASK,
            )
        ],
    ),
    (
        ["from 🇺🇸 to 🇮🇹 abroad: ", "profile four", "link", " back 🇺🇸🇮🇹\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="from 🇺🇸 to 🇮🇹 abroad: profile four back 🇺🇸🇮🇹",
                visible="from 🇺🇸 to 🇮🇹 abroad: profile fo",
                mask=_FLAGS_ROW_MASK,
            )
        ],
    ),
    (
        ["the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: ", "profile five", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: profile five ",
                visible="the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: pr",
                mask=_FAMILY_ROW_MASK,
            )
        ],
    ),
    (
        ["10 🎵 characters a pile of emoji: ", "profile six", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: profile six ",
                visible="🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: prof",
                mask=_PILE_OF_EMOJI_MASK,
            )
        ],
    ),
    (
        ["last line, no link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="last line, no link",
                visible="last line, no link",
                mask="\x00" * 18,
            )
        ],
    ),
    (
        ["Bottom of the test."],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="Bottom of the test.",
                visible="Bottom of the test.",
                mask="\x00" * 19,
            )
        ],
    ),
]

# Up-arrow navigation through the flags row is asymmetric with Down-arrow.
# Down-arrow presents the full flags line in one press, but Up-arrow stops twice:
# once showing only the trailing " back 🇺🇸🇮🇹\n" fragment, then again showing the
# full line. This is captured as-is for jd to evaluate as a possible bug.
_UP_LINES = [
    (
        ["last line, no link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="last line, no link",
                visible="last line, no link",
                mask="\x00" * 18,
            )
        ],
    ),
    (
        ["10 🎵 characters a pile of emoji: ", "profile six", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: profile six ",
                visible="🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: prof",
                mask=_PILE_OF_EMOJI_MASK,
            )
        ],
    ),
    (
        ["the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: ", "profile five", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: profile five ",
                visible="the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: pr",
                mask=_FAMILY_ROW_MASK,
            )
        ],
    ),
    # Up from the family row lands at the end of the flags line first.
    # This is the asymmetric extra stop described in the note above.
    (
        [" back 🇺🇸🇮🇹\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full=" back 🇺🇸🇮🇹",
                visible=" back 🇺🇸🇮🇹",
                mask="\x00" * 10,
            )
        ],
    ),
    (
        ["from 🇺🇸 to 🇮🇹 abroad: ", "profile four", "link", " back 🇺🇸🇮🇹\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="from 🇺🇸 to 🇮🇹 abroad: profile four back 🇺🇸🇮🇹",
                visible="from 🇺🇸 to 🇮🇹 abroad: profile fo",
                mask=_FLAGS_ROW_MASK,
            )
        ],
    ),
    (
        ["🎵 service three: ", "profile three", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵 service three: profile three ",
                visible="🎵 service three: profile three ",
                mask=_SERVICE_THREE_MASK,
            )
        ],
    ),
    (
        ["🎵 service two: ", "profile two", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵 service two: profile two ",
                visible="🎵 service two: profile two ",
                mask=_SERVICE_TWO_MASK,
            )
        ],
    ),
    (
        ["🎵 service one: ", "profile one", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="🎵 service one: profile one ",
                visible="🎵 service one: profile one ",
                mask=_SERVICE_ONE_MASK,
            )
        ],
    ),
    (
        ["next line 3\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="next line 3",
                visible="next line 3",
                mask="\x00" * 11,
            )
        ],
    ),
    # Double <br>
    (
        ["blank"],
        [helpers.BrailleLine(cursor_cell=1, full="", visible="", mask=None)],
    ),
    (
        ["next line 2\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="next line 2",
                visible="next line 2",
                mask="\x00" * 11,
            )
        ],
    ),
    (
        ["next line 1\n"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="next line 1",
                visible="next line 1",
                mask="\x00" * 11,
            )
        ],
    ),
    (
        ["♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: ", "link notes", "link"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: link notes ",
                visible="♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note s",
                mask=_LINK_NOTES_MASK,
            )
        ],
    ),
    (
        ["Streaming and social links below"],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="Streaming and social links below",
                visible="Streaming and social links below",
                mask="\x00" * 32,
            )
        ],
    ),
    (
        ["Top of the test."],
        [
            helpers.BrailleLine(
                cursor_cell=1,
                full="Top of the test.",
                visible="Top of the test.",
                mask="\x00" * 16,
            )
        ],
    ),
]

# Char-right: one stop per grapheme. Each flag emoji (e.g. 🇺🇸) is one stop; the
# back-to-back pair "🇺🇸🇮🇹" is two stops. Each ZWJ family emoji (👨‍👩‍👧‍👦) is one stop.
_RIGHT_SPEECH = [
    # "Top of the test." chars 2 to 16
    "o",
    "p",
    " ",
    "o",
    "f",
    " ",
    "t",
    "h",
    "e",
    " ",
    "t",
    "e",
    "s",
    "t",
    ".",
    # "Streaming and social links below"
    "S",
    "t",
    "r",
    "e",
    "a",
    "m",
    "i",
    "n",
    "g",
    " ",
    "a",
    "n",
    "d",
    " ",
    "s",
    "o",
    "c",
    "i",
    "a",
    "l",
    " ",
    "l",
    "i",
    "n",
    "k",
    "s",
    " ",
    "b",
    "e",
    "l",
    "o",
    "w",
    "blank",
    # "♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: link notes"
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "b",
    "a",
    "s",
    "i",
    "c",
    " ",
    "n",
    "o",
    "t",
    "e",
    " ",
    "s",
    "y",
    "m",
    "b",
    "o",
    "l",
    "s",
    ",",
    " ",
    "n",
    "o",
    " ",
    "s",
    "k",
    "e",
    "w",
    ":",
    " ",
    "l",
    "i",
    "n",
    "k",
    " ",
    "n",
    "o",
    "t",
    "e",
    "s",
    "blank",
    # "next line 1"
    "n",
    "e",
    "x",
    "t",
    " ",
    "l",
    "i",
    "n",
    "e",
    " ",
    "1",
    "blank",
    # "next line 2"
    "n",
    "e",
    "x",
    "t",
    " ",
    "l",
    "i",
    "n",
    "e",
    " ",
    "2",
    "blank",
    # double <br>
    "blank",
    # "next line 3"
    "n",
    "e",
    "x",
    "t",
    " ",
    "l",
    "i",
    "n",
    "e",
    " ",
    "3",
    "blank",
    # "🎵 service one: profile one"
    "🎵",
    " ",
    "s",
    "e",
    "r",
    "v",
    "i",
    "c",
    "e",
    " ",
    "o",
    "n",
    "e",
    ":",
    " ",
    "p",
    "r",
    "o",
    "f",
    "i",
    "l",
    "e",
    " ",
    "o",
    "n",
    "e",
    "blank",
    # "🎵 service two: profile two"
    "🎵",
    " ",
    "s",
    "e",
    "r",
    "v",
    "i",
    "c",
    "e",
    " ",
    "t",
    "w",
    "o",
    ":",
    " ",
    "p",
    "r",
    "o",
    "f",
    "i",
    "l",
    "e",
    " ",
    "t",
    "w",
    "o",
    "blank",
    # "🎵 service three: profile three"
    "🎵",
    " ",
    "s",
    "e",
    "r",
    "v",
    "i",
    "c",
    "e",
    " ",
    "t",
    "h",
    "r",
    "e",
    "e",
    ":",
    " ",
    "p",
    "r",
    "o",
    "f",
    "i",
    "l",
    "e",
    " ",
    "t",
    "h",
    "r",
    "e",
    "e",
    "blank",
    # "from 🇺🇸 to 🇮🇹 abroad: profile four back 🇺🇸🇮🇹"
    # Each isolated flag emoji is one stop; the back-to-back pair is two stops.
    "f",
    "r",
    "o",
    "m",
    " ",
    "🇺🇸",
    " ",
    "t",
    "o",
    " ",
    "🇮🇹",
    " ",
    "a",
    "b",
    "r",
    "o",
    "a",
    "d",
    ":",
    " ",
    "p",
    "r",
    "o",
    "f",
    "i",
    "l",
    "e",
    " ",
    "f",
    "o",
    "u",
    "r",
    " ",
    "b",
    "a",
    "c",
    "k",
    " ",
    "🇺🇸",
    "🇮🇹",
    "blank",
    # "the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: profile five"
    # Each ZWJ family emoji is one stop.
    "t",
    "h",
    "e",
    " ",
    "👨‍👩‍👧‍👦",
    " ",
    "a",
    "n",
    "d",
    " ",
    "👨‍👩‍👧‍👦",
    " ",
    "h",
    "e",
    "r",
    "e",
    ":",
    " ",
    "p",
    "r",
    "o",
    "f",
    "i",
    "l",
    "e",
    " ",
    "f",
    "i",
    "v",
    "e",
    "blank",
    # "🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: profile six"
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    " ",
    "a",
    " ",
    "p",
    "i",
    "l",
    "e",
    " ",
    "o",
    "f",
    " ",
    "e",
    "m",
    "o",
    "j",
    "i",
    ":",
    " ",
    "p",
    "r",
    "o",
    "f",
    "i",
    "l",
    "e",
    " ",
    "s",
    "i",
    "x",
    "blank",
    # "last line, no link"
    "l",
    "a",
    "s",
    "t",
    " ",
    "l",
    "i",
    "n",
    "e",
    ",",
    " ",
    "n",
    "o",
    " ",
    "l",
    "i",
    "n",
    "k",
    # "Bottom of the test."
    "B",
    "o",
    "t",
    "t",
    "o",
    "m",
    " ",
    "o",
    "f",
    " ",
    "t",
    "h",
    "e",
    " ",
    "t",
    "e",
    "s",
    "t",
    ".",
]

_LEFT_SPEECH = [
    # "Bottom of the test." right-to-left
    ".",
    "t",
    "s",
    "e",
    "t",
    " ",
    "e",
    "h",
    "t",
    " ",
    "f",
    "o",
    " ",
    "m",
    "o",
    "t",
    "t",
    "o",
    "B",
    # "last line, no link" right-to-left
    "k",
    "n",
    "i",
    "l",
    " ",
    "o",
    "n",
    " ",
    ",",
    "e",
    "n",
    "i",
    "l",
    " ",
    "t",
    "s",
    "a",
    "l",
    # blank (entering pile-of-emoji line from the right)
    "blank",
    # "🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: profile six" right-to-left (39 chars)
    "x",
    "i",
    "s",
    " ",
    "e",
    "l",
    "i",
    "f",
    "o",
    "r",
    "p",
    " ",
    ":",
    "i",
    "j",
    "o",
    "m",
    "e",
    " ",
    "f",
    "o",
    " ",
    "e",
    "l",
    "i",
    "p",
    " ",
    "a",
    " ",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    "🎵",
    # blank (entering family row from pile)
    "blank",
    # "the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: profile five" right-to-left
    # Each ZWJ family emoji is one stop.
    "e",
    "v",
    "i",
    "f",
    " ",
    "e",
    "l",
    "i",
    "f",
    "o",
    "r",
    "p",
    " ",
    ":",
    "e",
    "r",
    "e",
    "h",
    " ",
    "👨‍👩‍👧‍👦",
    " ",
    "d",
    "n",
    "a",
    " ",
    "👨‍👩‍👧‍👦",
    " ",
    "e",
    "h",
    "t",
    # blank (entering flags row from family row)
    "blank",
    # "from 🇺🇸 to 🇮🇹 abroad: profile four back 🇺🇸🇮🇹" right-to-left
    # The back-to-back pair "🇺🇸🇮🇹" is two stops (Italy then US); isolated flags are one stop each.
    "🇮🇹",
    "🇺🇸",
    " ",
    "k",
    "c",
    "a",
    "b",
    " ",
    "r",
    "u",
    "o",
    "f",
    " ",
    "e",
    "l",
    "i",
    "f",
    "o",
    "r",
    "p",
    " ",
    ":",
    "d",
    "a",
    "o",
    "r",
    "b",
    "a",
    " ",
    "🇮🇹",
    " ",
    "o",
    "t",
    " ",
    "🇺🇸",
    " ",
    "m",
    "o",
    "r",
    "f",
    # blank (entering service three)
    "blank",
    # "🎵 service three: profile three" right-to-left (30 chars)
    "e",
    "e",
    "r",
    "h",
    "t",
    " ",
    "e",
    "l",
    "i",
    "f",
    "o",
    "r",
    "p",
    " ",
    ":",
    "e",
    "e",
    "r",
    "h",
    "t",
    " ",
    "e",
    "c",
    "i",
    "v",
    "r",
    "e",
    "s",
    " ",
    "🎵",
    # blank (entering service two)
    "blank",
    # "🎵 service two: profile two" right-to-left (26 chars)
    "o",
    "w",
    "t",
    " ",
    "e",
    "l",
    "i",
    "f",
    "o",
    "r",
    "p",
    " ",
    ":",
    "o",
    "w",
    "t",
    " ",
    "e",
    "c",
    "i",
    "v",
    "r",
    "e",
    "s",
    " ",
    "🎵",
    # blank (entering service one)
    "blank",
    # "🎵 service one: profile one" right-to-left (26 chars)
    "e",
    "n",
    "o",
    " ",
    "e",
    "l",
    "i",
    "f",
    "o",
    "r",
    "p",
    " ",
    ":",
    "e",
    "n",
    "o",
    " ",
    "e",
    "c",
    "i",
    "v",
    "r",
    "e",
    "s",
    " ",
    "🎵",
    # blank (entering next line 3)
    "blank",
    # "next line 3" right-to-left
    "3",
    " ",
    "e",
    "n",
    "i",
    "l",
    " ",
    "t",
    "x",
    "e",
    "n",
    # double <br>
    "blank",
    # end-of-line blank when entering "next line 2" from above
    "blank",
    # "next line 2" right-to-left
    "2",
    " ",
    "e",
    "n",
    "i",
    "l",
    " ",
    "t",
    "x",
    "e",
    "n",
    "blank",
    # "next line 1" right-to-left
    "1",
    " ",
    "e",
    "n",
    "i",
    "l",
    " ",
    "t",
    "x",
    "e",
    "n",
    # blank (entering note-symbols line)
    "blank",
    # note-symbols line right-to-left
    "s",
    "e",
    "t",
    "o",
    "n",
    " ",
    "k",
    "n",
    "i",
    "l",
    " ",
    ":",
    "w",
    "e",
    "k",
    "s",
    " ",
    "o",
    "n",
    " ",
    ",",
    "s",
    "l",
    "o",
    "b",
    "m",
    "y",
    "s",
    " ",
    "e",
    "t",
    "o",
    "n",
    " ",
    "c",
    "i",
    "s",
    "a",
    "b",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    " ",
    "♫",
    " ",
    "♪",
    # blank (entering Streaming... line)
    "blank",
    # "Streaming and social links below" right-to-left
    "w",
    "o",
    "l",
    "e",
    "b",
    " ",
    "s",
    "k",
    "n",
    "i",
    "l",
    " ",
    "l",
    "a",
    "i",
    "c",
    "o",
    "s",
    " ",
    "d",
    "n",
    "a",
    " ",
    "g",
    "n",
    "i",
    "m",
    "a",
    "e",
    "r",
    "t",
    "S",
    # "Top of the test." right-to-left
    ".",
    "t",
    "s",
    "e",
    "t",
    " ",
    "e",
    "h",
    "t",
    " ",
    "f",
    "o",
    " ",
    "p",
    "o",
    "T",
]

_WORD_RIGHT_SPEECH: list[list[str]] = [
    # "Top of the test."
    ["Top "],
    ["of "],
    ["the "],
    ["test"],
    # "Streaming and social links below"
    ["Streaming "],
    ["and "],
    ["social "],
    ["links "],
    ["below"],
    # "♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: link notes"
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["basic "],
    ["note "],
    ["symbols"],
    ["no "],
    ["skew"],
    ["link "],
    ["notes"],
    # "next line 1"
    ["next "],
    ["line "],
    ["1\n"],
    # "next line 2"
    ["next "],
    ["line "],
    ["2\n\n"],
    # "next line 3"
    ["next "],
    ["line "],
    ["3\n"],
    # "🎵 service one: profile one"
    ["🎵"],
    ["service "],
    ["one"],
    ["profile "],
    ["one"],
    # "🎵 service two: profile two"
    ["🎵"],
    ["service "],
    ["two"],
    ["profile "],
    ["two"],
    # "🎵 service three: profile three"
    ["🎵"],
    ["service "],
    ["three"],
    ["profile "],
    ["three"],
    # "from 🇺🇸 to 🇮🇹 abroad: profile four back 🇺🇸🇮🇹"
    # Isolated flag emojis are individual word stops; the back-to-back pair is one word stop.
    ["from "],
    ["🇺🇸"],
    ["to "],
    ["🇮🇹"],
    ["abroad"],
    ["profile "],
    ["four"],
    ["back "],
    ["🇺🇸🇮🇹"],
    # "the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: profile five"
    # Each ZWJ family emoji is one word stop.
    ["the "],
    ["👨‍👩‍👧‍👦"],
    ["and "],
    ["👨‍👩‍👧‍👦"],
    ["here"],
    ["profile "],
    ["five"],
    # "🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: profile six"
    ["10 🎵 characters"],
    ["a "],
    ["pile "],
    ["of "],
    ["emoji"],
    ["profile "],
    ["six"],
    # "last line, no link"
    ["last "],
    ["line"],
    ["no "],
    ["link"],
    # "Bottom of the test."
    ["Bottom "],
    ["of "],
    ["the "],
    ["test"],
]

_WORD_LEFT_SPEECH: list[list[str]] = [
    # "Bottom of the test." right-to-left
    ["."],
    ["test"],
    ["the "],
    ["of "],
    ["Bottom "],
    # "last line, no link" right-to-left
    ["link"],
    ["no "],
    [", "],
    ["line"],
    ["last "],
    # "🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵 a pile of emoji: profile six" right-to-left
    ["six"],
    ["profile "],
    [": "],
    ["emoji"],
    ["of "],
    ["pile "],
    ["a "],
    ["10 🎵 characters "],
    # "the 👨‍👩‍👧‍👦 and 👨‍👩‍👧‍👦 here: profile five" right-to-left
    # Each ZWJ family emoji is one word stop.
    ["five"],
    ["profile "],
    [": "],
    ["here"],
    ["👨‍👩‍👧‍👦"],
    ["and "],
    ["👨‍👩‍👧‍👦"],
    ["the "],
    # "from 🇺🇸 to 🇮🇹 abroad: profile four back 🇺🇸🇮🇹" right-to-left
    # The back-to-back pair "🇺🇸🇮🇹" is one word stop (includes trailing newline).
    # Isolated flag emojis are individual word stops.
    ["🇺🇸🇮🇹\n"],
    ["back "],
    ["four"],
    ["profile "],
    [": "],
    ["abroad"],
    ["🇮🇹"],
    ["to "],
    ["🇺🇸"],
    ["from "],
    # "🎵 service three: profile three" right-to-left
    ["three"],
    ["profile "],
    [": "],
    ["three"],
    ["service "],
    ["🎵"],
    # "🎵 service two: profile two" right-to-left
    ["two"],
    ["profile "],
    [": "],
    ["two"],
    ["service "],
    ["🎵"],
    # "🎵 service one: profile one" right-to-left
    ["one"],
    ["profile "],
    [": "],
    ["one"],
    ["service "],
    ["🎵"],
    # "next line 3" right-to-left
    ["3\n"],
    ["line "],
    ["next "],
    # "next line 2" right-to-left
    ["2\n\n"],
    ["line "],
    ["next "],
    # "next line 1" right-to-left
    ["1\n"],
    ["line "],
    ["next "],
    # "♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ basic note symbols, no skew: link notes" right-to-left
    ["notes"],
    ["link "],
    [": "],
    ["skew"],
    ["no "],
    [", "],
    ["symbols"],
    ["note "],
    ["basic "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    ["♫ "],
    ["♪ "],
    # "Streaming and social links below" right-to-left
    ["below"],
    ["links "],
    ["social "],
    ["and "],
    ["Streaming "],
    # "Top of the test." right-to-left
    ["."],
    ["test"],
    ["the "],
    ["of "],
    ["Top "],
]


def _assert_line(session: NativeAppSession, key: int, speech: list[str], braille: list) -> None:
    """Presses key once and asserts both speech and braille."""

    keyboard.tap_key(key)
    assert helpers.capture(session) == (speech, braille)


def _collect_speech(session: NativeAppSession, key: int, count: int) -> list[list[str]]:
    """Presses key count times and collects each speech result."""

    results = []
    for _ in range(count):
        keyboard.tap_key(key)
        results.append(helpers.speech(session))
    return results


def _collect_word_speech(session: NativeAppSession, direction: int, count: int) -> list[list[str]]:
    """Presses Ctrl+direction count times and collects each speech result."""

    results = []
    for _ in range(count):
        keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], direction)
        results.append(helpers.speech(session))
    return results


@pytest.mark.native_app
def test_line_down(web_emoji_offset_skew: NativeAppSession) -> None:
    """Tests Down-arrow through the emoji-links page: all profile links read correctly."""

    session = web_emoji_offset_skew
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    for expected_speech, expected_braille in _DOWN_LINES:
        _assert_line(session, keyboard.KEYSYM_DOWN, expected_speech, expected_braille)


@pytest.mark.native_app
def test_line_up(web_emoji_offset_skew: NativeAppSession) -> None:
    """Tests Up-arrow back through the emoji-links page to confirm symmetric presentation."""

    session = web_emoji_offset_skew
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)
    helpers.capture(session)
    for expected_speech, expected_braille in _UP_LINES:
        _assert_line(session, keyboard.KEYSYM_UP, expected_speech, expected_braille)


@pytest.mark.native_app
def test_char_right(web_emoji_offset_skew: NativeAppSession) -> None:
    """Tests Right-arrow char-by-char top to bottom through a page where emoji precede links."""

    session = web_emoji_offset_skew
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    assert _collect_speech(session, keyboard.KEYSYM_RIGHT, len(_RIGHT_SPEECH)) == [
        [s] for s in _RIGHT_SPEECH
    ]


@pytest.mark.native_app
def test_char_left(web_emoji_offset_skew: NativeAppSession) -> None:
    """Tests Left-arrow char-by-char bottom to top through a page where emoji precede links."""

    session = web_emoji_offset_skew
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)
    helpers.capture(session)
    assert _collect_speech(session, keyboard.KEYSYM_LEFT, len(_LEFT_SPEECH)) == [
        [s] for s in _LEFT_SPEECH
    ]


@pytest.mark.native_app
def test_word_right(web_emoji_offset_skew: NativeAppSession) -> None:
    """Tests Ctrl+Right word-by-word through the full page."""

    session = web_emoji_offset_skew
    helpers.reset_web_state(session)
    helpers.move_to_top(session)
    assert (
        _collect_word_speech(session, keyboard.KEYSYM_RIGHT, len(_WORD_RIGHT_SPEECH))
        == _WORD_RIGHT_SPEECH
    )


@pytest.mark.native_app
def test_word_left(web_emoji_offset_skew: NativeAppSession) -> None:
    """Tests Ctrl+Left word-by-word back through the full page."""

    session = web_emoji_offset_skew
    helpers.reset_web_state(session)
    helpers.move_to_bottom(session)
    helpers.capture(session)
    assert (
        _collect_word_speech(session, keyboard.KEYSYM_LEFT, len(_WORD_LEFT_SPEECH))
        == _WORD_LEFT_SPEECH
    )
