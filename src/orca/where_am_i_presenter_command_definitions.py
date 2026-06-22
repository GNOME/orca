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

"""Command definitions for Where Am I."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .where_am_i_presenter import WhereAmIPresenter


def get_commands(owner: WhereAmIPresenter) -> list[Command]:
    """Returns commands for Where Am I."""

    kb_orca_f = keybindings.KeyBinding("f", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_e = keybindings.KeyBinding("e", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_shift_up = keybindings.KeyBinding("Up", keybindings.ORCA_SHIFT_MODIFIER_MASK)

    kb_orca_equal = keybindings.KeyBinding("equal", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_kp_enter = keybindings.KeyBinding("KP_Enter", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_kp_enter_2 = keybindings.KeyBinding(
        "KP_Enter",
        keybindings.ORCA_MODIFIER_MASK,
        click_count=2,
    )
    kb_kp_enter = keybindings.KeyBinding("KP_Enter", keybindings.NO_MODIFIER_MASK)
    kb_kp_enter_2 = keybindings.KeyBinding(
        "KP_Enter",
        keybindings.NO_MODIFIER_MASK,
        click_count=2,
    )

    kb_orca_slash = keybindings.KeyBinding("slash", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_slash_2 = keybindings.KeyBinding(
        "slash",
        keybindings.ORCA_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_return = keybindings.KeyBinding("Return", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_return_2 = keybindings.KeyBinding(
        "Return",
        keybindings.ORCA_MODIFIER_MASK,
        click_count=2,
    )

    return [
        KeyboardCommand(
            "readCharAttributesHandler",
            owner.present_character_attributes,
            owner.GROUP_LABEL,
            cmdnames.READ_CHAR_ATTRIBUTES,
            desktop_keybinding=kb_orca_f,
            laptop_keybinding=kb_orca_f,
        ),
        KeyboardCommand(
            "presentSizeAndPositionHandler",
            owner.present_size_and_position,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_SIZE_AND_POSITION,
        ),
        KeyboardCommand(
            "getTitleHandler",
            owner.present_title,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_TITLE,
            desktop_keybinding=kb_orca_kp_enter,
            laptop_keybinding=kb_orca_slash,
        ),
        KeyboardCommand(
            "getStatusBarHandler",
            owner.present_status_bar,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_STATUS_BAR,
            desktop_keybinding=kb_orca_kp_enter_2,
            laptop_keybinding=kb_orca_slash_2,
        ),
        KeyboardCommand(
            "present_default_button",
            owner.present_default_button,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_DEFAULT_BUTTON,
            desktop_keybinding=kb_orca_e,
            laptop_keybinding=kb_orca_e,
        ),
        KeyboardCommand(
            "present_cell_formula",
            owner.present_cell_formula,
            owner.GROUP_LABEL,
            cmdnames.PRESENT_CELL_FORMULA,
            desktop_keybinding=kb_orca_equal,
        ),
        KeyboardCommand(
            "whereAmIBasicHandler",
            owner.where_am_i_basic,
            owner.GROUP_LABEL,
            cmdnames.WHERE_AM_I_BASIC,
            desktop_keybinding=kb_kp_enter,
            laptop_keybinding=kb_orca_return,
        ),
        KeyboardCommand(
            "whereAmIDetailedHandler",
            owner.where_am_i_detailed,
            owner.GROUP_LABEL,
            cmdnames.WHERE_AM_I_DETAILED,
            desktop_keybinding=kb_kp_enter_2,
            laptop_keybinding=kb_orca_return_2,
        ),
        KeyboardCommand(
            "whereAmILinkHandler",
            owner.present_link,
            owner.GROUP_LABEL,
            cmdnames.WHERE_AM_I_LINK,
        ),
        KeyboardCommand(
            "whereAmISelectionHandler",
            owner.present_selection,
            owner.GROUP_LABEL,
            cmdnames.WHERE_AM_I_SELECTION,
            desktop_keybinding=kb_orca_shift_up,
            laptop_keybinding=kb_orca_shift_up,
        ),
    ]
