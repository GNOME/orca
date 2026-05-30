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

from .helpers import BrailleLine, capture

if TYPE_CHECKING:
    from .orca_fixtures import NativeAppSession


def _command(session: NativeAppSession, name: str) -> tuple[list[str], list[BrailleLine]]:
    session.orca.call("SpeechPresenter", name, True)
    return capture(session)


@pytest.mark.native_app
def test_toggle_verbosity(gtk3_text_view: NativeAppSession) -> None:
    """Tests that toggling speech verbosity announces the new level and restores it."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ToggleVerbosity") == (
        ["Verbosity level: brief"],
        [BrailleLine(0, "Verbosity level: brief", "Verbosity level: brief", "\x00" * 22)],
    )
    assert _command(session, "ToggleVerbosity") == (
        ["Verbosity level: verbose"],
        [BrailleLine(0, "Verbosity level: verbose", "Verbosity level: verbose", "\x00" * 24)],
    )


@pytest.mark.native_app
def test_change_number_style(gtk3_text_view: NativeAppSession) -> None:
    """Tests that changing the number reading style announces digits vs words."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ChangeNumberStyle") == (
        ["Speak numbers as digits."],
        [BrailleLine(0, "Speak numbers as digits.", "Speak numbers as digits.", "\x00" * 24)],
    )
    assert _command(session, "ChangeNumberStyle") == (
        ["Speak numbers as words."],
        [BrailleLine(0, "Speak numbers as words.", "Speak numbers as words.", "\x00" * 23)],
    )


@pytest.mark.native_app
def test_toggle_spoken_indentation(gtk3_text_view: NativeAppSession) -> None:
    """Tests that toggling spoken indentation announces enabled then disabled."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ToggleIndentation") == (
        ["Spoken indentation enabled."],
        [BrailleLine(0, "Spoken indentation enabled.", "Spoken indentation enabled.", "\x00" * 27)],
    )
    assert _command(session, "ToggleIndentation") == (
        ["Spoken indentation disabled."],
        [
            BrailleLine(
                0, "Spoken indentation disabled.", "Spoken indentation disabled.", "\x00" * 28
            )
        ],
    )


@pytest.mark.native_app
def test_cycle_text_attribute_change_mode(gtk3_text_view: NativeAppSession) -> None:
    """Tests cycling the text-attribute-change mode through its three states."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "CycleTextAttributeChangeMode") == (
        ["Text attributes: editable text."],
        [
            BrailleLine(
                0,
                "Text attributes: editable text.",
                "Text attributes: editable text.",
                "\x00" * 31,
            )
        ],
    )
    assert _command(session, "CycleTextAttributeChangeMode") == (
        ["Text attributes: on."],
        [BrailleLine(0, "Text attributes: on.", "Text attributes: on.", "\x00" * 20)],
    )
    assert _command(session, "CycleTextAttributeChangeMode") == (
        ["Text attributes: off."],
        [BrailleLine(0, "Text attributes: off.", "Text attributes: off.", "\x00" * 21)],
    )


@pytest.mark.native_app
def test_toggle_table_cell_read_mode_outside_table(gtk3_text_view: NativeAppSession) -> None:
    """Tests that the table cell read mode command reports when not in a table."""

    session = gtk3_text_view
    session.reader.drain(quiescence_timeout=0.3, overall_timeout=2.0)
    session.reader.reset()

    assert _command(session, "ToggleTableCellReadingMode") == (
        ["Not in a table."],
        [BrailleLine(0, "Not in a table.", "Not in a table.", "\x00" * 15)],
    )
