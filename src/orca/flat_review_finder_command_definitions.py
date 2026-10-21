# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2022 Igalia, S.L.
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

"""Command definitions for flat-review find."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand
from .help_metadata import CommandDoc, CommandGroupDoc

if TYPE_CHECKING:
    from .flat_review_finder import FlatReviewFinder


def get_documentation() -> CommandGroupDoc:
    """Returns documentation metadata for find commands."""

    return CommandGroupDoc(
        commands=(
            CommandDoc(
                "findHandler",
                details=(
                    "Opens a dialog where you can enter text to search for, start from the "
                    "current location or the top of the window, match case, match whole words, "
                    "search backward, and wrap around. Search text is interpreted as a regular "
                    "expression; characters such as a period or an asterisk have special "
                    "meanings. Use a backslash before a special character to match it "
                    "literally."
                ),
            ),
            CommandDoc(
                "findNextHandler",
                details=(
                    "Moves to the next match without reopening the dialog. If you have not "
                    "searched yet, opens the search dialog."
                ),
            ),
            CommandDoc(
                "findPreviousHandler",
                details=(
                    "Moves to the previous match without reopening the dialog. If you have not "
                    "searched yet, opens the search dialog."
                ),
            ),
        ),
        summary="Search visible contents in a window and move flat review to a match.",
        see_also=("reviewing.orca-find",),
    )


def get_commands(owner: FlatReviewFinder) -> list[Command]:
    """Returns commands for flat-review find."""

    kb_unmodified_kp_delete = keybindings.KeyBinding(
        "KP_Delete",
        keybindings.NO_MODIFIER_MASK,
    )
    kb_orca_bracketleft = keybindings.KeyBinding(
        "bracketleft",
        keybindings.ORCA_MODIFIER_MASK,
    )
    kb_orca_kp_delete = keybindings.KeyBinding(
        "KP_Delete",
        keybindings.ORCA_MODIFIER_MASK,
    )
    kb_orca_bracketright = keybindings.KeyBinding(
        "bracketright",
        keybindings.ORCA_MODIFIER_MASK,
    )
    kb_orca_shift_kp_delete = keybindings.KeyBinding(
        "KP_Delete",
        keybindings.ORCA_SHIFT_MODIFIER_MASK,
    )
    kb_orca_ctrl_bracketright = keybindings.KeyBinding(
        "bracketright",
        keybindings.ORCA_CTRL_MODIFIER_MASK,
    )

    return [
        KeyboardCommand(
            "findHandler",
            owner.show_dialog,
            owner.GROUP_LABEL,
            cmdnames.SHOW_FIND_GUI,
            desktop_keybinding=kb_unmodified_kp_delete,
            laptop_keybinding=kb_orca_bracketleft,
        ),
        KeyboardCommand(
            "findNextHandler",
            owner.find_next,
            owner.GROUP_LABEL,
            cmdnames.FIND_NEXT,
            desktop_keybinding=kb_orca_kp_delete,
            laptop_keybinding=kb_orca_bracketright,
        ),
        KeyboardCommand(
            "findPreviousHandler",
            owner.find_previous,
            owner.GROUP_LABEL,
            cmdnames.FIND_PREVIOUS,
            desktop_keybinding=kb_orca_shift_kp_delete,
            laptop_keybinding=kb_orca_ctrl_bracketright,
        ),
    ]
