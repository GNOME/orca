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
from .help_metadata import CommandDoc, CommandGroupDoc

if TYPE_CHECKING:
    from .mouse_presenter import MousePresenter


def get_documentation() -> CommandGroupDoc:
    """Returns documentation metadata for mouse commands."""

    return CommandGroupDoc(
        commands=(
            CommandDoc(
                "toggleMouseReviewHandler",
                details=(
                    "Turns mouse review on or off for the current session, whether or not it is "
                    "enabled in preferences."
                ),
            ),
            CommandDoc(
                "routePointerToItemHandler",
                details=(
                    "Routes the pointer to the flat review location when flat review is active, "
                    "or to the focused object otherwise."
                ),
            ),
            CommandDoc(
                "leftClickReviewItemHandler",
                details=(
                    "Acts on the flat review location when flat review is active, or on the "
                    "focused object otherwise. Orca first tries suitable accessible actions "
                    "exposed by the object through its application or toolkit. If no suitable "
                    "action succeeds, Orca tries to simulate a mouse click at the object's "
                    "location. Simulated clicks do not currently work on Wayland."
                ),
            ),
            CommandDoc(
                "rightClickReviewItemHandler",
                details=(
                    "Acts on the flat review location when flat review is active, or on the "
                    "focused object otherwise. Orca first tries suitable accessible actions "
                    "exposed by the object through its application or toolkit. If no suitable "
                    "action succeeds, Orca tries to simulate a mouse click at the object's "
                    "location. Simulated clicks do not currently work on Wayland."
                ),
            ),
        ),
        summary="Toggle Mouse Review, route the pointer, or click the current item.",
        see_also=("reviewing.mouse-review",),
    )


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
