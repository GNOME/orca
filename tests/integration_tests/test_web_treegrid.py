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

"""Tests presentation of an ARIA treegrid in web content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import keyboard
from .helpers import BrailleLine, capture, reset_web_state

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_treegrid_navigation(web_treegrid: NativeAppSession) -> None:
    """Tests treegrid navigation."""

    session = web_treegrid
    reset_web_state(session)

    keyboard.tap_key(keyboard.KEYSYM_TAB)
    spoken, brailled = capture(session)
    assert spoken == ["Roof repair quote Two tiles are cracked", "expanded", "Focus mode"]
    assert brailled[-1] == BrailleLine(0, "Focus mode", "Focus mode", "\x00" * 10)

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["re: Roof repair quote The scaffolding is booked"]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote The scaffolding is booked table row",
        "re: Roof repair quote The scaffo",
        "\x00" * 57,
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["re: Roof repair quote Can we start on Monday", "collapsed"]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote Can we start on Monday table row collapsed",
        "re: Roof repair quote Can we sta",
        "\x00" * 64,
    )

    keyboard.tap_key(keyboard.KEYSYM_RIGHT)
    spoken, brailled = capture(session)
    assert spoken == ["expanded"]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote Can we start on Monday table row expanded",
        "re: Roof repair quote Can we sta",
        "\x00" * 63,
    )

    keyboard.tap_key(keyboard.KEYSYM_DOWN)
    spoken, brailled = capture(session)
    assert spoken == ["re: Roof repair quote Monday suits us"]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote Monday suits us table row",
        "re: Roof repair quote Monday sui",
        "\x00" * 47,
    )

    keyboard.tap_key(keyboard.KEYSYM_KP_ENTER)
    spoken, brailled = capture(session)
    assert spoken == [
        "re: Roof repair quote Monday suits us",
        "Subject re: Roof repair quote",
        "row 5 column 1",
        "column 1 of 2 row 5 of 5",
        "Summary Monday suits us",
        "row 5 column 2",
        "column 2 of 2 row 5 of 5",
    ]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote Monday suits us table row Subject column header re: Roof "
        "repair quote Summary column header Monday suits us",
        "re: Roof repair quote Monday sui",
        "\x00" * 129,
    )

    keyboard.tap_key(keyboard.KEYSYM_UP)
    spoken, brailled = capture(session)
    assert spoken == ["re: Roof repair quote Can we start on Monday", "expanded"]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote Can we start on Monday table row expanded",
        "re: Roof repair quote Can we sta",
        "\x00" * 63,
    )

    keyboard.tap_key(keyboard.KEYSYM_LEFT)
    spoken, brailled = capture(session)
    assert spoken == ["collapsed"]
    assert brailled[-1] == BrailleLine(
        1,
        "re: Roof repair quote Can we start on Monday table row collapsed",
        "re: Roof repair quote Can we sta",
        "\x00" * 64,
    )
