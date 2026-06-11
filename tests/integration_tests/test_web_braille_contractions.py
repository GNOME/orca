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

"""Tests that the link underline tracks the link's cells when the line is translated to braille."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

_PLAIN_SPEECH = ["knowledge good people child about character educated everywhere indeed."]
_LINK_SPEECH = ["A little ", "knowledge", "link", " about good people and a character."]

_PLAIN_COMPUTER = "knowledge good people child about character educated everywhere indeed."
_LINK_COMPUTER = "A little knowledge about good people and a character."
_LINK_COMPUTER_MASK = "\x00" * 9 + "\xc0" * 9 + "\x00" * (len(_LINK_COMPUTER) - 18)

_PLAIN_LITERARY = "knowledge good people child about character educated everywhere indeed4"
_LINK_LITERARY = ";,a little knowledge about good people and ;a character4"
_LINK_LITERARY_MASK = "\x00" * 11 + "\xc0" * 9 + "\x00" * (len(_LINK_LITERARY) - 20)

_PLAIN_CONTRACTED = 'k gd p * ab "* $ucat$ "ey": 9de$4'
_LINK_CONTRACTED = ',a ll k ab gd p &a "*4'
_LINK_CONTRACTED_MASK = "\x00" * 6 + "\xc0" + "\x00" * (len(_LINK_CONTRACTED) - 7)


def _configure(session: NativeAppSession, *, table: str | None) -> None:
    """Resets state and configures braille for the given table (None for computer braille)."""

    helpers.reset_web_state(session)
    if table is None:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", False)
    else:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
        session.orca.set("BraillePresenter", "ContractionTable", table)
        session.orca.set("BraillePresenter", "ComputerBrailleAtCursorIsEnabled", False)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


def _move_to_link_line(session: NativeAppSession) -> None:
    """Moves onto the link paragraph and discards the captured navigation output."""

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()


@pytest.mark.native_app
def test_uncontracted_link_and_plain_lines(web_contracted_braille: NativeAppSession) -> None:
    """Tests that the link underline covers the link's nine cells in uncontracted braille."""

    session = web_contracted_braille
    _configure(session, table=None)
    _move_to_link_line(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        _PLAIN_SPEECH,
        [
            helpers.BrailleLine(
                1,
                _PLAIN_COMPUTER,
                "knowledge good people child abou",
                "\x00" * len(_PLAIN_COMPUTER),
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        _LINK_SPEECH,
        [
            helpers.BrailleLine(
                1, _LINK_COMPUTER, "A little knowledge about good pe", _LINK_COMPUTER_MASK
            )
        ],
    )


@pytest.mark.native_app
def test_literary_braille_remaps_link_underline(web_contracted_braille: NativeAppSession) -> None:
    """Tests that the link underline still covers the link when the braille line is longer."""

    session = web_contracted_braille
    _configure(session, table="en-us-g1")
    _move_to_link_line(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        _PLAIN_SPEECH,
        [
            helpers.BrailleLine(
                1,
                _PLAIN_LITERARY,
                "knowledge good people child abou",
                "\x00" * len(_PLAIN_LITERARY),
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        _LINK_SPEECH,
        [
            helpers.BrailleLine(
                1, _LINK_LITERARY, ";,a little knowledge about good ", _LINK_LITERARY_MASK
            )
        ],
    )


@pytest.mark.native_app
def test_contracted_braille_collapses_link_underline(
    web_contracted_braille: NativeAppSession,
) -> None:
    """Tests that the link underline collapses onto the link's cell in contracted braille."""

    session = web_contracted_braille
    _configure(session, table="en-us-g2")
    _move_to_link_line(session)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    assert helpers.capture(session) == (
        _PLAIN_SPEECH,
        [
            helpers.BrailleLine(
                1,
                _PLAIN_CONTRACTED,
                'k gd p * ab "* $ucat$ "ey": 9de$',
                "\x00" * len(_PLAIN_CONTRACTED),
            )
        ],
    )
    keyboard.tap_key(keyboard.KEYSYM_UP)
    assert helpers.capture(session) == (
        _LINK_SPEECH,
        [helpers.BrailleLine(1, _LINK_CONTRACTED, _LINK_CONTRACTED, _LINK_CONTRACTED_MASK)],
    )
