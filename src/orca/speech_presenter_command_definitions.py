# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Command definitions for speech presentation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .speech_presenter import SpeechPresenter


def get_commands(owner: SpeechPresenter) -> list[Command]:
    """Returns commands for speech presentation."""

    kb_orca_v = keybindings.KeyBinding("v", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_f11 = keybindings.KeyBinding("F11", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_shift_d = keybindings.KeyBinding("d", keybindings.ORCA_SHIFT_MODIFIER_MASK)

    return [
        KeyboardCommand(
            "changeNumberStyleHandler",
            owner.change_number_style,
            owner.GROUP_LABEL,
            cmdnames.CHANGE_NUMBER_STYLE,
        ),
        KeyboardCommand(
            "toggleSpeechVerbosityHandler",
            owner.toggle_verbosity,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_SPEECH_VERBOSITY,
            desktop_keybinding=kb_orca_v,
            laptop_keybinding=kb_orca_v,
        ),
        KeyboardCommand(
            "toggleSpeakingIndentationHandler",
            owner.toggle_indentation,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_SPOKEN_INDENTATION,
        ),
        KeyboardCommand(
            "toggleTableCellReadModeHandler",
            owner.toggle_table_cell_reading_mode,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_TABLE_CELL_READ_MODE,
            desktop_keybinding=kb_orca_f11,
            laptop_keybinding=kb_orca_f11,
        ),
        KeyboardCommand(
            "toggle_speech_monitor",
            owner.toggle_monitor,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_SPEECH_MONITOR,
            desktop_keybinding=kb_orca_shift_d,
            laptop_keybinding=kb_orca_shift_d,
        ),
        KeyboardCommand(
            "cycle_text_attribute_change_mode",
            owner.cycle_text_attribute_change_mode,
            owner.GROUP_LABEL,
            cmdnames.CYCLE_TEXT_ATTRIBUTE_CHANGE_MODE,
        ),
    ]
