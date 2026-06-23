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

from . import braille, cmdnames, debug
from .command import BrailleCommand, Command, KeyboardCommand

if TYPE_CHECKING:
    from collections.abc import Callable

    from .braille_presenter import BraillePresenter

    CommandCallback = Callable[..., bool]


def get_commands(owner: BraillePresenter) -> list[Command]:
    """Returns commands for braille presentation."""

    commands: list[Command] = [
        KeyboardCommand(
            "panBrailleLeftHandler",
            owner.pan_braille_left,
            owner.GROUP_LABEL,
            cmdnames.PAN_BRAILLE_LEFT,
        ),
        KeyboardCommand(
            "panBrailleRightHandler",
            owner.pan_braille_right,
            owner.GROUP_LABEL,
            cmdnames.PAN_BRAILLE_RIGHT,
        ),
        KeyboardCommand(
            "contractedBrailleHandler",
            owner.toggle_contracted_braille,
            owner.GROUP_LABEL,
            cmdnames.SET_CONTRACTED_BRAILLE,
        ),
        KeyboardCommand(
            "toggle_braille_monitor",
            owner.toggle_monitor,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_BRAILLE_MONITOR,
        ),
    ]

    _append_braille_command(
        commands,
        "panBrailleLeftHandler",
        owner.pan_braille_left,
        owner.GROUP_LABEL,
        cmdnames.PAN_BRAILLE_LEFT,
        (
            braille.BRLAPI_KEY_CMD_HWINLT,
            braille.BRLAPI_KEY_CMD_FWINLT,
            braille.BRLAPI_KEY_CMD_FWINLTSKIP,
        ),
        executes_in_learn_mode=True,
    )
    _append_braille_command(
        commands,
        "panBrailleRightHandler",
        owner.pan_braille_right,
        owner.GROUP_LABEL,
        cmdnames.PAN_BRAILLE_RIGHT,
        (
            braille.BRLAPI_KEY_CMD_HWINRT,
            braille.BRLAPI_KEY_CMD_FWINRT,
            braille.BRLAPI_KEY_CMD_FWINRTSKIP,
        ),
        executes_in_learn_mode=True,
    )
    _append_braille_command(
        commands,
        "contractedBrailleHandler",
        owner.toggle_contracted_braille,
        owner.GROUP_LABEL,
        cmdnames.SET_CONTRACTED_BRAILLE,
        (braille.BRLAPI_KEY_CMD_SIXDOTS,),
        executes_in_learn_mode=True,
    )
    _append_braille_command(
        commands,
        "goBrailleHomeHandler",
        owner.go_home,
        owner.GROUP_LABEL,
        cmdnames.GO_BRAILLE_HOME,
        (braille.BRLAPI_KEY_CMD_HOME,),
    )
    _append_braille_command(
        commands,
        "processRoutingKeyHandler",
        owner.process_routing_key,
        owner.GROUP_LABEL,
        cmdnames.PROCESS_ROUTING_KEY,
        (braille.BRLAPI_KEY_CMD_ROUTE,),
    )
    _append_braille_command(
        commands,
        "processBrailleCutBeginHandler",
        owner.process_braille_cut_begin,
        owner.GROUP_LABEL,
        cmdnames.PROCESS_BRAILLE_CUT_BEGIN,
        (braille.BRLAPI_KEY_CMD_CUTBEGIN,),
    )
    _append_braille_command(
        commands,
        "processBrailleCutLineHandler",
        owner.process_braille_cut_line,
        owner.GROUP_LABEL,
        cmdnames.PROCESS_BRAILLE_CUT_LINE,
        (braille.BRLAPI_KEY_CMD_CUTLINE,),
    )

    return commands


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _append_braille_command(
    commands: list[Command],
    name: str,
    function: CommandCallback,
    group: str,
    description: str,
    bindings: tuple[int | None, ...],
    executes_in_learn_mode: bool = False,
) -> None:
    """Appends a braille command when at least one binding is available."""

    available_bindings = tuple(binding for binding in bindings if binding is not None)
    if not available_bindings:
        msg = f"BRAILLE PRESENTER: Braille bindings unavailable for {name}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return

    commands.append(
        BrailleCommand(
            name,
            function,
            group,
            description,
            braille_bindings=available_bindings,
            executes_in_learn_mode=executes_in_learn_mode,
        )
    )


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
