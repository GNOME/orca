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

"""Integration tests for speech presenter toggle commands and their announcements."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.integration_tests import helpers

if TYPE_CHECKING:
    from tests.integration_tests.orca_fixtures import NativeAppSession


def _command(session: NativeAppSession, name: str) -> tuple[list[str], list[helpers.BrailleLine]]:
    session.orca.call("SpeechPresenter", name, True)
    return helpers.capture(session)


@pytest.mark.native_app
def test_toggle_verbosity(gtk_text_view: NativeAppSession) -> None:
    """Tests that toggling speech verbosity announces the new level and restores it."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ToggleVerbosity") == (
        ["Verbosity level: brief"],
        [helpers.BrailleLine(0, "Verbosity level: brief", "Verbosity level: brief", "\x00" * 22)],
    )
    assert _command(session, "ToggleVerbosity") == (
        ["Verbosity level: verbose"],
        [
            helpers.BrailleLine(
                0, "Verbosity level: verbose", "Verbosity level: verbose", "\x00" * 24
            )
        ],
    )


@pytest.mark.native_app
def test_change_number_style(gtk_text_view: NativeAppSession) -> None:
    """Tests that changing the number reading style announces digits vs words."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ChangeNumberStyle") == (
        ["Speak numbers as digits."],
        [
            helpers.BrailleLine(
                0, "Speak numbers as digits.", "Speak numbers as digits.", "\x00" * 24
            )
        ],
    )
    assert _command(session, "ChangeNumberStyle") == (
        ["Speak numbers as words."],
        [helpers.BrailleLine(0, "Speak numbers as words.", "Speak numbers as words.", "\x00" * 23)],
    )


@pytest.mark.native_app
def test_toggle_spoken_indentation(gtk_text_view: NativeAppSession) -> None:
    """Tests that toggling spoken indentation announces enabled then disabled."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ToggleIndentation") == (
        ["Spoken indentation enabled."],
        [
            helpers.BrailleLine(
                0, "Spoken indentation enabled.", "Spoken indentation enabled.", "\x00" * 27
            )
        ],
    )
    assert _command(session, "ToggleIndentation") == (
        ["Spoken indentation disabled."],
        [
            helpers.BrailleLine(
                0, "Spoken indentation disabled.", "Spoken indentation disabled.", "\x00" * 28
            )
        ],
    )


@pytest.mark.native_app
def test_cycle_text_attribute_change_mode(gtk_text_view: NativeAppSession) -> None:
    """Tests cycling the text-attribute-change mode through its three states."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "CycleTextAttributeChangeMode") == (
        ["Text attributes: editable text."],
        [
            helpers.BrailleLine(
                0,
                "Text attributes: editable text.",
                "Text attributes: editable text.",
                "\x00" * 31,
            )
        ],
    )
    assert _command(session, "CycleTextAttributeChangeMode") == (
        ["Text attributes: on."],
        [helpers.BrailleLine(0, "Text attributes: on.", "Text attributes: on.", "\x00" * 20)],
    )
    assert _command(session, "CycleTextAttributeChangeMode") == (
        ["Text attributes: off."],
        [helpers.BrailleLine(0, "Text attributes: off.", "Text attributes: off.", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_toggle_table_cell_read_mode_outside_table(gtk_text_view: NativeAppSession) -> None:
    """Tests that the table cell read mode command reports when not in a table."""

    session = gtk_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ToggleTableCellReadingMode") == (
        ["Not in a table."],
        [helpers.BrailleLine(0, "Not in a table.", "Not in a table.", "\x00" * 15)],
    )
