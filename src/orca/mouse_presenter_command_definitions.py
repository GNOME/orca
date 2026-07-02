# Mouse presenter for Orca
#
# Copyright 2008 Eitan Isaacson
# Copyright 2016 Igalia, S.L.
# Copyright 2026 SUSE LLC.
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

"""Command definitions for mouse presentation and interaction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .mouse_presenter import MousePresenter


def get_commands(owner: MousePresenter) -> list[Command]:
    """Returns commands for mouse presentation and interaction."""

    kb_orca_kp_divide = keybindings.KeyBinding(
        "KP_Divide",
        keybindings.ORCA_MODIFIER_MASK,
    )
    kb_unmodified_kp_divide = keybindings.KeyBinding(
        "KP_Divide",
        keybindings.NO_MODIFIER_MASK,
    )
    kb_unmodified_kp_multiply = keybindings.KeyBinding(
        "KP_Multiply",
        keybindings.NO_MODIFIER_MASK,
    )
    kb_orca_9 = keybindings.KeyBinding("9", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_7 = keybindings.KeyBinding("7", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_8 = keybindings.KeyBinding("8", keybindings.ORCA_MODIFIER_MASK)

    return [
        KeyboardCommand(
            "toggleMouseReviewHandler",
            owner.toggle_mouse_review,
            owner.GROUP_LABEL,
            cmdnames.MOUSE_REVIEW_TOGGLE,
        ),
        KeyboardCommand(
            "routePointerToItemHandler",
            owner.route_pointer_to_item,
            owner.GROUP_LABEL,
            cmdnames.ROUTE_POINTER_TO_ITEM,
            desktop_keybinding=kb_orca_kp_divide,
            laptop_keybinding=kb_orca_9,
        ),
        KeyboardCommand(
            "leftClickReviewItemHandler",
            owner.left_click_item,
            owner.GROUP_LABEL,
            cmdnames.LEFT_CLICK_REVIEW_ITEM,
            desktop_keybinding=kb_unmodified_kp_divide,
            laptop_keybinding=kb_orca_7,
        ),
        KeyboardCommand(
            "rightClickReviewItemHandler",
            owner.right_click_item,
            owner.GROUP_LABEL,
            cmdnames.RIGHT_CLICK_REVIEW_ITEM,
            desktop_keybinding=kb_unmodified_kp_multiply,
            laptop_keybinding=kb_orca_8,
        ),
    ]
