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

"""Tests line navigation across blank lines in preformatted text."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


_LINES = [
    (
        "     *  systemd - logind ' s integration with the UAPI . 1 Boot Loader",
        "    * systemd-logind's integration with the UAPI.1 Boot Loader",
    ),
    (
        "      Specification  ( which allows the systemctl reboot  -  - boot - loader - entry = ",
        "      Specification (which allows the systemctl reboot --boot-loader-entry=",
    ),
    (
        "      switch to work )  so far has supported a special directory",
        "      switch to work) so far has supported a special directory",
    ),
    (
        "       / run / boot - loader - entries /  which allowed defining boot loader entries",
        "      /run/boot-loader-entries/ which allowed defining boot loader entries",
    ),
    (
        "      outside of the ESP / XBOOTLDR partition for compatibility with legacy",
        "      outside of the ESP/XBOOTLDR partition for compatibility with legacy",
    ),
    (
        "      systems that do not natively implement UAPI . 1 .  However ,  it appears",
        "      systems that do not natively implement UAPI.1. However, it appears",
    ),
    (
        "      that  ( to our knowledge )  it is not actually being used by any project",
        "      that (to our knowledge) it is not actually being used by any project",
    ),
    (
        "       ( quite unlike UAPI . 1 itself ,  which found adoption far beyond",
        "      (quite unlike UAPI.1 itself, which found adoption far beyond",
    ),
    (
        "      systemd )  ,  and its implementation is incomplete .  With the future 262",
        "      systemd), and its implementation is incomplete. With the future 262",
    ),
    (
        "      release we intend to remove support for  / run / boot - loader - entries /  and",
        "      release we intend to remove support for /run/boot-loader-entries/ and",
    ),
    (
        "      related interfaces ,  in order to simplify our codebase .  Support for",
        "      related interfaces, in order to simplify our codebase. Support for",
    ),
    (
        "      UAPI . 1 is  –  of course  –  kept in place . ",
        "      UAPI.1 is – of course – kept in place.",
    ),
    (
        "blank",
        "",
    ),
    (
        '     *  The experimental  " systemd - sysupdated "  D - Bus API is going to be',
        '    * The experimental "systemd-sysupdated" D-Bus API is going to be',
    ),
    (
        "      removed in the next release .  The plan is that in its place",
        "      removed in the next release. The plan is that in its place",
    ),
    (
        "      clients should directly talk to systemd - sysupdate  ( i . e .  the backend",
        "      clients should directly talk to systemd-sysupdate (i.e. the backend",
    ),
    (
        '      of  " systemd - sysupdated "  )  via Varlink IPC .  The  " updatectl "  tool will',
        '      of "systemd-sysupdated") via Varlink IPC. The "updatectl" tool will',
    ),
    (
        "      be reworked along these lines . ",
        "      be reworked along these lines.",
    ),
]


def _assert_line(session: BrowserSession, index: int, *, entering: bool = False) -> None:
    spoken, brailled = helpers.capture(session)
    expected_speech, expected_braille = _LINES[index]
    assert spoken == (["code"] if entering else []) + [expected_speech]
    assert brailled[-1].full == expected_braille + " $l"


@pytest.mark.native_app
@pytest.mark.parametrize("layout", [False, True], ids=["no-layout", "layout"])
def test_line_navigation_across_blank_line(
    web_preformatted_blank_lines: BrowserSession, layout: bool
) -> None:
    """Tests both directions and reversal at a blank line in preformatted text."""

    session = web_preformatted_blank_lines
    helpers.reset_web_state(session)
    previous = session.orca.get("CaretNavigator", "LayoutMode")
    session.orca.set("CaretNavigator", "LayoutMode", layout)
    try:
        for index in range(len(_LINES)):
            keyboard.tap_key(keyboard.KEYSYM_DOWN)
            _assert_line(session, index, entering=index == 0)
            if index == 13:
                keyboard.tap_key(keyboard.KEYSYM_UP)
                _assert_line(session, 12)
                keyboard.tap_key(keyboard.KEYSYM_DOWN)
                _assert_line(session, 13)

        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        assert helpers.speech(session) == ["leaving code.", "End of release notes."]

        for index in reversed(range(len(_LINES))):
            keyboard.tap_key(keyboard.KEYSYM_UP)
            _assert_line(session, index, entering=index == len(_LINES) - 1)

        keyboard.tap_key(keyboard.KEYSYM_UP)
        assert helpers.speech(session) == ["leaving code.", "Release notes", "heading 1"]
    finally:
        session.orca.set("CaretNavigator", "LayoutMode", previous)
