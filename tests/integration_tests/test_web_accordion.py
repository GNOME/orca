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

"""Tests presentation of an ARIA accordion in web content."""

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
def test_arrow_navigation_between_accordion_headers(web_accordion: NativeAppSession) -> None:
    """Tests arrowing between accordion headers and expanding and collapsing panels."""

    session = web_accordion
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Contact details", "expanded button heading 3", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Delivery address", "collapsed button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Delivery address collapsed button", "Delivery address collapsed butto", "\x00" * 33
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["Payment", "collapsed button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Payment collapsed button", "Payment collapsed button", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_HOME)
    spoken, brailled = capture(session)
    assert spoken == ["Contact details", "expanded button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Contact details expanded button", "Contact details expanded button", "\x00" * 31
    )

    keyboard.tap_key(keyboard.KEYSYM_END)
    spoken, brailled = capture(session)
    assert spoken == ["Payment", "collapsed button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Payment collapsed button", "Payment collapsed button", "\x00" * 24
    )

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == ["expanded"]
    assert brailled[-1] == BrailleLine(
        1, "Payment expanded button", "Payment expanded button", "\x00" * 23
    )

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Payment", "region", "Street:", "entry"]
    assert brailled[-1] == BrailleLine(9, "Street:  $l", "Street:  $l", None)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["leaving region.", "Contact details", "expanded button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Contact details expanded button", "Contact details expanded button", "\x00" * 31
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["leaving region.", "Delivery address", "collapsed button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Delivery address collapsed button", "Delivery address collapsed butto", "\x00" * 33
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["Contact details", "expanded button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Contact details expanded button", "Contact details expanded button", "\x00" * 31
    )

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == ["collapsed"]
    assert brailled[-1] == BrailleLine(
        1, "Contact details collapsed button", "Contact details collapsed button", "\x00" * 32
    )

    keyboard.tap_key(keyboard.KEYSYM_RETURN)
    spoken, brailled = capture(session)
    assert spoken == ["expanded"]
    assert brailled[-1] == BrailleLine(
        1, "Contact details expanded button", "Contact details expanded button", "\x00" * 31
    )


@pytest.mark.native_app
def test_structural_navigation_by_heading(web_accordion: NativeAppSession) -> None:
    """Tests structural navigation by heading across the accordion headers."""

    session = web_accordion
    _reload(session)

    keyboard.tap_key(keyboard.KEYSYM_H)
    spoken, brailled = capture(session)
    assert spoken == ["h", "Contact details", "expanded button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Contact details expanded button", "Contact details expanded button", "\x00" * 31
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    spoken, brailled = capture(session)
    assert spoken == ["h", "Delivery address", "collapsed button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Delivery address collapsed button", "Delivery address collapsed butto", "\x00" * 33
    )

    keyboard.tap_key(keyboard.KEYSYM_H)
    spoken, brailled = capture(session)
    assert spoken == ["h", "Payment", "collapsed button heading 3"]
    assert brailled[-1] == BrailleLine(
        1, "Payment collapsed button", "Payment collapsed button", "\x00" * 24
    )
