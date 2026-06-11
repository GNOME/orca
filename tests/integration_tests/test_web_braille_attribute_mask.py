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

"""Tests the braille attribute mask for links and text formatting, including across translation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession

# Links and text attributes use distinct indicators (dot 7 vs dot 8) so the mask shows which is
# which: "\x40" marks a link cell, "\x80" marks a cell with a brailled text attribute.
_LINK = "\x40"
_ATTR = "\x80"

_LINKS_SPEECH = ["knowledge", "link", " and ", "people", "link", " for ", "character", "link"]
_LINKS = "knowledge and people for character"
_LINKS_VISIBLE = "knowledge and people for charact"
_LINKS_MASK = _LINK * 9 + "\x00" * 5 + _LINK * 6 + "\x00" * 5 + _LINK * 9
_LINKS_CONTRACTED = 'k & p = "*'
_LINKS_CONTRACTED_MASK = _LINK + "\x00" * 3 + _LINK + "\x00" * 3 + _LINK * 2

_FORMAT_SPEECH = ["a  knowledge  and  people  here"]
_FORMAT = "a knowledge and people here"
_FORMAT_MASK = "\x00" * 2 + _ATTR * 9 + "\x00" * 5 + _ATTR * 6 + "\x00" * 5
_FORMAT_CONTRACTED = 'a k & p "h'
_FORMAT_CONTRACTED_MASK = "\x00" * 2 + _ATTR + "\x00" * 3 + _ATTR + "\x00" * 3


def _setup(session: NativeAppSession, *, table: str | None, text_attrs: bool = False) -> None:
    """Resets state and configures braille (the given table plus distinct link/text-attr dots)."""

    helpers.reset_web_state(session)
    if table is None:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", False)
    else:
        session.orca.set("BraillePresenter", "ContractedBrailleIsEnabled", True)
        session.orca.set("BraillePresenter", "ContractionTable", table)
        session.orca.set("BraillePresenter", "ComputerBrailleAtCursorIsEnabled", False)
    session.orca.set("BraillePresenter", "LinkIndicator", "dot7")
    if text_attrs:
        session.orca.set("BraillePresenter", "TextAttributesIndicator", "dot8")
        session.orca.set("TextAttributeManager", "AttributesToBraille", ["weight", "style"])
    session.reader.drain(quiescence_timeout=0.4, overall_timeout=2.0)
    session.reader.reset()


def _down(session: NativeAppSession, count: int) -> None:
    """Navigates down count lines, discarding the output of all but the last move."""

    for _ in range(count - 1):
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
        session.reader.reset()
    keyboard.tap_key(keyboard.KEYSYM_DOWN)


@pytest.mark.native_app
def test_multiple_links_uncontracted(web_attribute_mask: NativeAppSession) -> None:
    """Tests that each link in a line is underlined at its own cells (start, middle, end)."""

    session = web_attribute_mask
    _setup(session, table=None)
    _down(session, 1)
    assert helpers.capture(session) == (
        _LINKS_SPEECH,
        [helpers.BrailleLine(1, _LINKS, _LINKS_VISIBLE, _LINKS_MASK)],
    )


@pytest.mark.native_app
def test_multiple_links_contracted(web_attribute_mask: NativeAppSession) -> None:
    """Tests that the per-link underlines collapse onto each link's contracted cells."""

    session = web_attribute_mask
    _setup(session, table="en-us-g2")
    _down(session, 1)
    assert helpers.capture(session) == (
        _LINKS_SPEECH,
        [helpers.BrailleLine(1, _LINKS_CONTRACTED, _LINKS_CONTRACTED, _LINKS_CONTRACTED_MASK)],
    )


@pytest.mark.native_app
def test_text_attributes_uncontracted(web_attribute_mask: NativeAppSession) -> None:
    """Tests that bold and italic words are marked in the mask when brailling those attributes."""

    session = web_attribute_mask
    _setup(session, table=None, text_attrs=True)
    _down(session, 2)
    assert helpers.capture(session) == (
        _FORMAT_SPEECH,
        [helpers.BrailleLine(1, _FORMAT, _FORMAT, _FORMAT_MASK)],
    )


@pytest.mark.native_app
def test_text_attributes_contracted(web_attribute_mask: NativeAppSession) -> None:
    """Tests that the bold and italic marks collapse onto the contracted cells."""

    session = web_attribute_mask
    _setup(session, table="en-us-g2", text_attrs=True)
    _down(session, 2)
    assert helpers.capture(session) == (
        _FORMAT_SPEECH,
        [helpers.BrailleLine(1, _FORMAT_CONTRACTED, _FORMAT_CONTRACTED, _FORMAT_CONTRACTED_MASK)],
    )
