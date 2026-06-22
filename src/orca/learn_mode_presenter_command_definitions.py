# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2023 Igalia, S.L.
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

"""Command definitions for learn mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .learn_mode_presenter import LearnModePresenter


def get_commands(owner: LearnModePresenter) -> list[Command]:
    """Returns commands for learn mode."""

    kb_orca_h = keybindings.KeyBinding("h", keybindings.ORCA_MODIFIER_MASK)
    return [
        KeyboardCommand(
            "enterLearnModeHandler",
            owner.start,
            owner.GROUP_LABEL,
            cmdnames.ENTER_LEARN_MODE,
            desktop_keybinding=kb_orca_h,
            laptop_keybinding=kb_orca_h,
        ),
    ]
