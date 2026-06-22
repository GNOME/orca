# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2026 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Command definitions for system information."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .system_information_presenter import SystemInformationPresenter


def get_commands(owner: SystemInformationPresenter) -> list[Command]:
    """Returns commands for system information."""

    kb_orca_t = keybindings.KeyBinding("t", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_t_2 = keybindings.KeyBinding("t", keybindings.ORCA_MODIFIER_MASK, click_count=2)

    return [
        KeyboardCommand(
            "presentTimeHandler",
            owner.present_time,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_CURRENT_TIME,
            desktop_keybinding=kb_orca_t,
            laptop_keybinding=kb_orca_t,
        ),
        KeyboardCommand(
            "presentDateHandler",
            owner.present_date,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_CURRENT_DATE,
            desktop_keybinding=kb_orca_t_2,
            laptop_keybinding=kb_orca_t_2,
        ),
        KeyboardCommand(
            "present_battery_status",
            owner.present_battery_status,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_BATTERY_STATUS,
        ),
        KeyboardCommand(
            "present_cpu_and_memory_usage",
            owner.present_cpu_and_memory_usage,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_CPU_AND_MEMORY_USAGE,
        ),
        KeyboardCommand(
            "present_modifier_keys_state",
            owner.present_modifier_keys_state,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_MODIFIER_KEYS_STATE,
        ),
    ]
