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

"""Command definitions for document presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .document_presenter import DocumentPresenter


def get_commands(owner: DocumentPresenter) -> list[Command]:
    """Returns commands for document presentation."""

    kb_orca_a = keybindings.KeyBinding("a", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_a_2 = keybindings.KeyBinding("a", keybindings.ORCA_MODIFIER_MASK, click_count=2)
    kb_orca_a_3 = keybindings.KeyBinding("a", keybindings.ORCA_MODIFIER_MASK, click_count=3)

    return [
        KeyboardCommand(
            "toggle_presentation_mode",
            owner.toggle_presentation_mode,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_PRESENTATION_MODE,
            desktop_keybinding=kb_orca_a,
            laptop_keybinding=kb_orca_a,
        ),
        KeyboardCommand(
            "enable_sticky_focus_mode",
            owner.enable_sticky_focus_mode,
            owner.GROUP_LABEL,
            cmdnames.SET_FOCUS_MODE_STICKY,
            desktop_keybinding=kb_orca_a_2,
            laptop_keybinding=kb_orca_a_2,
        ),
        KeyboardCommand(
            "enable_sticky_browse_mode",
            owner.enable_sticky_browse_mode,
            owner.GROUP_LABEL,
            cmdnames.SET_BROWSE_MODE_STICKY,
            desktop_keybinding=kb_orca_a_3,
            laptop_keybinding=kb_orca_a_3,
        ),
    ]
