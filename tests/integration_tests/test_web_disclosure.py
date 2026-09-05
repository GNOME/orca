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

"""Tests presentation of ARIA disclosure buttons in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _reload(session: NativeAppSession) -> None:
    """Reloads the page so that each test starts with the same expanded and collapsed state."""

    keyboard.press_chord([keyboard.KEYSYM_CONTROL_L], keyboard.KEYSYM_R)
    session.reader.drain(quiescence_timeout=0.5, overall_timeout=3.0)
    session.reader.reset()
    reset_web_state(session)


@pytest.mark.native_app
def test_expanding_and_collapsing_disclosure_buttons(web_disclosure: NativeAppSession) -> None:
    """Tests expanding and collapsing disclosure buttons."""

    session = web_disclosure
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Read more", "collapsed button", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == ["expanded"]
    assert brailled[-1] == BrailleLine(
        1, "Read more expanded button", "Read more expanded button", "\x00" * 25
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["navigation", "Field guide", "List with 2 items", "Birds", "collapsed button"]
    assert brailled[-1] == BrailleLine(
        1, "Birds collapsed button", "Birds collapsed button", "\x00" * 22
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Trees", "collapsed button"]
    assert brailled[-1] == BrailleLine(
        1, "Trees collapsed button", "Trees collapsed button", "\x00" * 22
    )

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == ["expanded"]
    assert brailled[-1] == BrailleLine(
        1, "Trees expanded button", "Trees expanded button", "\x00" * 21
    )

    keyboard.tap_key(keyboard.KEYSYM_ESCAPE)
    spoken, brailled = capture(session)
    assert spoken == ["collapsed"]
    assert brailled[-1] == BrailleLine(
        1, "Trees collapsed button", "Trees collapsed button", "\x00" * 22
    )


@pytest.mark.native_app
def test_reading_disclosed_content(web_disclosure: NativeAppSession) -> None:
    """Tests reading the content a disclosure button reveals."""

    session = web_disclosure
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Read more", "collapsed button", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == ["expanded"]
    assert brailled[-1] == BrailleLine(
        1, "Read more expanded button", "Read more expanded button", "\x00" * 25
    )

    session.orca.press_orca_key(keyboard.KEYSYM_A)
    spoken, brailled = capture(session)
    assert spoken == ["Browse mode"]
    assert brailled[-1] == BrailleLine(0, "Browse mode", "Browse mode", "\x00" * 11)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["The disclosed content is a short paragraph."]
    assert brailled[-1] == BrailleLine(
        1,
        "The disclosed content is a short paragraph.",
        "The disclosed content is a short",
        "\x00" * 43,
    )


@pytest.mark.native_app
def test_structural_navigation_by_button(web_disclosure: NativeAppSession) -> None:
    """Tests structural navigation by button across the disclosure buttons."""

    session = web_disclosure
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_B)
    spoken, brailled = capture(session)
    assert spoken == ["b", "Read more", "collapsed button"]
    assert brailled[-1] == BrailleLine(
        1, "Read more collapsed button", "Read more collapsed button", "\x00" * 26
    )

    keyboard.tap_key(keyboard.KEYSYM_B)
    spoken, brailled = capture(session)
    assert spoken == [
        "b",
        "navigation",
        "Field guide",
        "List with 2 items",
        "Birds",
        "collapsed button",
    ]
    assert brailled[-1] == BrailleLine(
        1, "Birds collapsed button", "Birds collapsed button", "\x00" * 22
    )
