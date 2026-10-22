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

"""Tests navigation of lists containing non-list-item children."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import helpers
from .harness import keyboard
from .helpers import BrailleLine

if TYPE_CHECKING:
    from .orca_fixtures import BrowserSession


def _assert_line(session: BrowserSession, speech: list[str], text: str) -> None:
    spoken, brailled = helpers.capture(session)
    assert spoken == speech
    assert brailled[-1] == BrailleLine(1, text, text, "\x00" * len(text))


def _mixed_list_count(session: BrowserSession) -> str:
    # Known issue: Firefox counts the two div siblings of the first child,
    # rather than the three list items. Fix counting separately.
    return helpers.expected_for_browser(session, "List with 3 items", firefox="List with 2 items")


def _description_list(session: BrowserSession) -> str:
    # Firefox includes the itemless outer list in the nesting level.
    return helpers.expected_for_browser(
        session,
        "Description list with 1 term",
        firefox="Description list with 1 term Nesting level 1",
    )


def _itemless_list_entry(session: BrowserSession) -> list[str]:
    # Known issue: Chromium counts the description list as one list item.
    return helpers.expected_for_browser(
        session,
        ["List with 1 item", _description_list(session)],
        firefox=[_description_list(session)],
    )


@pytest.mark.native_app
@pytest.mark.parametrize("layout_mode", [True, False])
def test_caret_navigation(web_mixed_lists: BrowserSession, layout_mode: bool) -> None:
    """Reads mixed and itemless lists in both directions without losing their text."""

    session = web_mixed_lists
    helpers.reset_web_state(session)
    session.orca.set("CaretNavigator", "LayoutMode", layout_mode)
    # Firefox exposes trailing whitespace after the itemless list's text.
    tail = helpers.expected_for_browser(session, "Tail", firefox="Tail ")
    description_list = _description_list(session)
    down = (
        ([_mixed_list_count(session), "foo"], "foo"),
        (["\u2022 bar"], "\u2022 bar"),
        (["\u2022 baz"], "\u2022 baz"),
        (["\u2022 bla"], "\u2022 bla"),
        (["qux"], "qux"),
        (["leaving list.", "No list items", "heading 2"], "No list items h2"),
        ([*_itemless_list_entry(session), "Term", "description term"], "Term "),
        (["Definition", "description value"], "Definition description value"),
        (["leaving list.", tail], tail),
        (["End"], "End"),
    )
    for speech, text in down:
        keyboard.tap_key(keyboard.KEYSYM_DOWN)
        _assert_line(session, speech, text)

    # Chromium announces both the description list and its outer list on exit.
    leaving = helpers.expected_for_browser(
        session, ["leaving list.", "leaving list."], firefox=["leaving list."]
    )
    up = (
        ([tail], tail),
        ([description_list, "Definition", "description value"], "Definition description value"),
        (["Term", "description term"], "Term "),
        ([*leaving, "No list items", "heading 2"], "No list items h2"),
        ([_mixed_list_count(session), "qux"], "qux"),
        (["\u2022 bla"], "\u2022 bla"),
        (["\u2022 baz"], "\u2022 baz"),
        (["\u2022 bar"], "\u2022 bar"),
        (["foo"], "foo"),
        (["leaving list.", "Start", "heading 1"], "Start h1"),
    )
    for speech, text in up:
        keyboard.tap_key(keyboard.KEYSYM_UP)
        _assert_line(session, speech, text)


@pytest.mark.native_app
def test_structural_navigation(web_mixed_lists: BrowserSession) -> None:
    """Keeps list and item navigation available despite non-item children."""

    session = web_mixed_lists
    helpers.reset_web_state(session)
    keyboard.tap_key(keyboard.KEYSYM_L)
    _assert_line(session, ["l", _mixed_list_count(session), "foo"], "foo")

    for item in ("bar", "baz", "bla"):
        keyboard.tap_key(keyboard.KEYSYM_I)
        _assert_line(session, ["i", f"\u2022 {item}"], f"\u2022 {item}")
    for item in ("baz", "bar"):
        keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_I)
        _assert_line(session, ["I", f"\u2022 {item}"], f"\u2022 {item}")

    keyboard.press_chord([keyboard.KEYSYM_SHIFT_L], keyboard.KEYSYM_L)
    _assert_line(
        session,
        [
            "L",
            "Wrapping to bottom.",
            "leaving list.",
            *_itemless_list_entry(session),
            "Term",
            "description term",
        ],
        "Term ",
    )
    keyboard.tap_key(keyboard.KEYSYM_L)
    leaving = helpers.expected_for_browser(
        session, ["leaving list.", "leaving list."], firefox=["leaving list."]
    )
    _assert_line(
        session, ["l", "Wrapping to top.", *leaving, _mixed_list_count(session), "foo"], "foo"
    )
