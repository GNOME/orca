# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Command definitions for braille presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import braille, cmdnames
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .braille_presenter import BraillePresenter


def get_commands(owner: BraillePresenter) -> list[Command]:
    """Returns commands for braille presentation."""

    return [
        KeyboardCommand(
            "toggle_braille_monitor",
            owner.toggle_monitor,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_BRAILLE_MONITOR,
        ),
    ]


def get_brltty_command_names() -> dict[int, str]:
    """Returns BrlTTY command names for presentation in the UI."""

    command_names: dict[int, str] = {}

    def add_command(command_id: int | None, label: str) -> None:
        if command_id is not None:
            command_names[command_id] = label

    add_command(braille.BRLAPI_KEY_CMD_HWINLT, cmdnames.BRAILLE_LINE_LEFT)
    add_command(braille.BRLAPI_KEY_CMD_FWINLT, cmdnames.BRAILLE_LINE_LEFT)
    add_command(braille.BRLAPI_KEY_CMD_FWINLTSKIP, cmdnames.BRAILLE_LINE_LEFT)
    add_command(braille.BRLAPI_KEY_CMD_HWINRT, cmdnames.BRAILLE_LINE_RIGHT)
    add_command(braille.BRLAPI_KEY_CMD_FWINRT, cmdnames.BRAILLE_LINE_RIGHT)
    add_command(braille.BRLAPI_KEY_CMD_FWINRTSKIP, cmdnames.BRAILLE_LINE_RIGHT)
    add_command(braille.BRLAPI_KEY_CMD_LNUP, cmdnames.BRAILLE_LINE_UP)
    add_command(braille.BRLAPI_KEY_CMD_LNDN, cmdnames.BRAILLE_LINE_DOWN)
    add_command(braille.BRLAPI_KEY_CMD_FREEZE, cmdnames.BRAILLE_FREEZE)
    add_command(braille.BRLAPI_KEY_CMD_TOP_LEFT, cmdnames.BRAILLE_TOP_LEFT)
    add_command(braille.BRLAPI_KEY_CMD_BOT_LEFT, cmdnames.BRAILLE_BOTTOM_LEFT)
    add_command(braille.BRLAPI_KEY_CMD_HOME, cmdnames.BRAILLE_HOME)
    add_command(braille.BRLAPI_KEY_CMD_SIXDOTS, cmdnames.BRAILLE_SIX_DOTS)
    add_command(braille.BRLAPI_KEY_CMD_ROUTE, cmdnames.BRAILLE_ROUTE_CURSOR)
    add_command(braille.BRLAPI_KEY_CMD_CUTBEGIN, cmdnames.BRAILLE_CUT_BEGIN)
    add_command(braille.BRLAPI_KEY_CMD_CUTLINE, cmdnames.BRAILLE_CUT_LINE)

    return command_names
