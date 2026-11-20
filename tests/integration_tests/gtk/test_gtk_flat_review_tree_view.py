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

"""Tests flat review by line, word, and character over a GTK3 tree view (table)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers
from tests.integration_tests.harness import keyboard

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


@pytest.mark.native_app
def test_flat_review_by_line_word_and_character(gtk_tree_view: NativeAppSession) -> None:
    """Tests reviewing rows, cells, and characters of a table with the flat review keypad."""

    session = gtk_tree_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()
    helpers.toggle_flat_review(session)

    try:
        keyboard.tap_key(keyboard.KEYSYM_KP_UP)
        assert helpers.capture(session) == (
            ["Ada Engineer London check box not checked"],
            [
                helpers.BrailleLine(
                    1,
                    "Ada Engineer London < > check box $l",
                    "Ada Engineer London < > check bo",
                    "\x00" * 36,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert helpers.capture(session) == (
            ["Grace Admiral Boston check box checked"],
            [
                helpers.BrailleLine(
                    1,
                    "Grace Admiral Boston <x> check box $l",
                    "Grace Admiral Boston <x> check b",
                    "\x00" * 37,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_UP)
        assert helpers.capture(session) == (
            ["Alan Analyst Manchester check box not checked"],
            [
                helpers.BrailleLine(
                    1,
                    "Alan Analyst Manchester < > check box $l",
                    "Alan Analyst Manchester < > chec",
                    "\x00" * 40,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        assert helpers.capture(session) == (
            ["Grace Admiral Boston check box checked"],
            [
                helpers.BrailleLine(
                    1,
                    "Grace Admiral Boston <x> check box $l",
                    "Grace Admiral Boston <x> check b",
                    "\x00" * 37,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_HOME)
        assert helpers.capture(session) == (
            ["Ada Engineer London check box not checked"],
            [
                helpers.BrailleLine(
                    1,
                    "Ada Engineer London < > check box $l",
                    "Ada Engineer London < > check bo",
                    "\x00" * 36,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_BEGIN)
        assert helpers.capture(session) == (
            ["Ada"],
            [
                helpers.BrailleLine(
                    1,
                    "Ada Engineer London < > check box $l",
                    "Ada Engineer London < > check bo",
                    "\x00" * 36,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_RIGHT)
        assert helpers.capture(session) == (
            ["Engineer"],
            [
                helpers.BrailleLine(
                    1,
                    "Ada Engineer London < > check box $l",
                    "Engineer London < > check box $l",
                    "\x00" * 36,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_RIGHT)
        assert helpers.capture(session) == (
            ["London"],
            [
                helpers.BrailleLine(
                    1,
                    "Ada Engineer London < > check box $l",
                    "London < > check box $l",
                    "\x00" * 36,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_DOWN)
        assert helpers.capture(session) == (
            ["L"],
            [
                helpers.BrailleLine(
                    1,
                    "Ada Engineer London < > check box $l",
                    "London < > check box $l",
                    "\x00" * 36,
                )
            ],
        )

        keyboard.tap_key(keyboard.KEYSYM_KP_PAGE_DOWN)
        assert helpers.capture(session) == (
            ["o"],
            [
                helpers.BrailleLine(
                    2,
                    "Ada Engineer London < > check box $l",
                    "London < > check box $l",
                    "\x00" * 36,
                )
            ],
        )
    finally:
        helpers.toggle_flat_review(session)
