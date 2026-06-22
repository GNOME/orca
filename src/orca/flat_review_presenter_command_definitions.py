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

"""Command definitions for flat review."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import braille, cmdnames, keybindings
from .command import BrailleCommand, Command, KeyboardCommand

if TYPE_CHECKING:
    from collections.abc import Callable

    from .flat_review_presenter import FlatReviewPresenter
    from .input_event import InputEvent
    from .scripts import default

    CommandCallback = Callable[[default.Script, InputEvent | None, bool], bool]


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _append_braille_command(
    commands: list[Command],
    name: str,
    function: CommandCallback,
    group: str,
    description: str,
    binding: int | None,
) -> None:
    """Appends a braille command if binding is available."""

    if binding is None:
        return

    commands.append(
        BrailleCommand(
            name,
            function,
            group,
            description,
            braille_bindings=(binding,),
        )
    )


# pylint: disable-next=too-many-locals,too-many-statements
def get_commands(
    owner: FlatReviewPresenter,
) -> list[Command]:
    """Returns commands for flat review."""

    kb_unmodified_kp_subtract = keybindings.KeyBinding(
        "KP_Subtract",
        keybindings.NO_MODIFIER_MASK,
    )
    kb_orca_p = keybindings.KeyBinding("p", keybindings.ORCA_MODIFIER_MASK)
    kb_unmodified_kp_add_2 = keybindings.KeyBinding(
        "KP_Add",
        keybindings.NO_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_semicolon_2 = keybindings.KeyBinding(
        "semicolon",
        keybindings.ORCA_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_kp_home = keybindings.KeyBinding("KP_Home", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_ctrl_u = keybindings.KeyBinding("u", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_unmodified_kp_home = keybindings.KeyBinding("KP_Home", keybindings.NO_MODIFIER_MASK)
    kb_orca_u = keybindings.KeyBinding("u", keybindings.ORCA_MODIFIER_MASK)
    kb_unmodified_kp_up = keybindings.KeyBinding("KP_Up", keybindings.NO_MODIFIER_MASK)
    kb_orca_i = keybindings.KeyBinding("i", keybindings.ORCA_MODIFIER_MASK)
    kb_unmodified_kp_up_2 = keybindings.KeyBinding(
        "KP_Up",
        keybindings.NO_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_i_2 = keybindings.KeyBinding("i", keybindings.ORCA_MODIFIER_MASK, click_count=2)
    kb_unmodified_kp_up_3 = keybindings.KeyBinding(
        "KP_Up",
        keybindings.NO_MODIFIER_MASK,
        click_count=3,
    )
    kb_orca_i_3 = keybindings.KeyBinding("i", keybindings.ORCA_MODIFIER_MASK, click_count=3)
    kb_unmodified_kp_page_up = keybindings.KeyBinding(
        "KP_Page_Up",
        keybindings.NO_MODIFIER_MASK,
    )
    kb_orca_o = keybindings.KeyBinding("o", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_kp_page_up = keybindings.KeyBinding(
        "KP_Page_Up",
        keybindings.ORCA_MODIFIER_MASK,
    )
    kb_orca_ctrl_o = keybindings.KeyBinding("o", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_unmodified_kp_left = keybindings.KeyBinding("KP_Left", keybindings.NO_MODIFIER_MASK)
    kb_orca_j = keybindings.KeyBinding("j", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_kp_left = keybindings.KeyBinding("KP_Left", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_ctrl_j = keybindings.KeyBinding("j", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_unmodified_kp_begin = keybindings.KeyBinding("KP_Begin", keybindings.NO_MODIFIER_MASK)
    kb_orca_k = keybindings.KeyBinding("k", keybindings.ORCA_MODIFIER_MASK)
    kb_unmodified_kp_begin_2 = keybindings.KeyBinding(
        "KP_Begin",
        keybindings.NO_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_k_2 = keybindings.KeyBinding("k", keybindings.ORCA_MODIFIER_MASK, click_count=2)
    kb_unmodified_kp_begin_3 = keybindings.KeyBinding(
        "KP_Begin",
        keybindings.NO_MODIFIER_MASK,
        click_count=3,
    )
    kb_orca_k_3 = keybindings.KeyBinding("k", keybindings.ORCA_MODIFIER_MASK, click_count=3)
    kb_orca_kp_begin = keybindings.KeyBinding("KP_Begin", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_ctrl_k = keybindings.KeyBinding("k", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_unmodified_kp_right = keybindings.KeyBinding("KP_Right", keybindings.NO_MODIFIER_MASK)
    kb_orca_l = keybindings.KeyBinding("l", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_kp_right = keybindings.KeyBinding("KP_Right", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_ctrl_l = keybindings.KeyBinding("l", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_unmodified_kp_end = keybindings.KeyBinding("KP_End", keybindings.NO_MODIFIER_MASK)
    kb_orca_m = keybindings.KeyBinding("m", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_kp_end = keybindings.KeyBinding("KP_End", keybindings.ORCA_MODIFIER_MASK)
    kb_orca_ctrl_m = keybindings.KeyBinding("m", keybindings.ORCA_CTRL_MODIFIER_MASK)
    kb_unmodified_kp_down = keybindings.KeyBinding("KP_Down", keybindings.NO_MODIFIER_MASK)
    kb_orca_comma = keybindings.KeyBinding("comma", keybindings.ORCA_MODIFIER_MASK)
    kb_unmodified_kp_down_2 = keybindings.KeyBinding(
        "KP_Down",
        keybindings.NO_MODIFIER_MASK,
        click_count=2,
    )
    kb_orca_comma_2 = keybindings.KeyBinding(
        "comma",
        keybindings.ORCA_MODIFIER_MASK,
        click_count=2,
    )
    kb_unmodified_kp_down_3 = keybindings.KeyBinding(
        "KP_Down",
        keybindings.NO_MODIFIER_MASK,
        click_count=3,
    )
    kb_orca_comma_3 = keybindings.KeyBinding(
        "comma",
        keybindings.ORCA_MODIFIER_MASK,
        click_count=3,
    )
    kb_unmodified_kp_page_down = keybindings.KeyBinding(
        "KP_Page_Down",
        keybindings.NO_MODIFIER_MASK,
    )
    kb_orca_period = keybindings.KeyBinding("period", keybindings.ORCA_MODIFIER_MASK)

    commands: list[Command] = [
        KeyboardCommand(
            "toggleFlatReviewModeHandler",
            owner.toggle_flat_review_mode,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_FLAT_REVIEW,
            desktop_keybinding=kb_unmodified_kp_subtract,
            laptop_keybinding=kb_orca_p,
        ),
        KeyboardCommand(
            "reviewHomeHandler",
            owner.go_home,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_HOME,
            desktop_keybinding=kb_orca_kp_home,
            laptop_keybinding=kb_orca_ctrl_u,
        ),
        KeyboardCommand(
            "reviewEndHandler",
            owner.go_end,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_END,
            desktop_keybinding=kb_orca_kp_page_up,
            laptop_keybinding=kb_orca_ctrl_o,
        ),
        KeyboardCommand(
            "reviewBottomLeftHandler",
            owner.go_bottom_left,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_BOTTOM_LEFT,
        ),
        KeyboardCommand(
            "reviewPreviousLineHandler",
            owner.go_previous_line,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_PREVIOUS_LINE,
            desktop_keybinding=kb_unmodified_kp_home,
            laptop_keybinding=kb_orca_u,
        ),
        KeyboardCommand(
            "reviewCurrentLineHandler",
            owner.present_line,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_CURRENT_LINE,
            desktop_keybinding=kb_unmodified_kp_up,
            laptop_keybinding=kb_orca_i,
        ),
        KeyboardCommand(
            "reviewNextLineHandler",
            owner.go_next_line,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_NEXT_LINE,
            desktop_keybinding=kb_unmodified_kp_page_up,
            laptop_keybinding=kb_orca_o,
        ),
        KeyboardCommand(
            "reviewSpellCurrentLineHandler",
            owner.spell_line,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_SPELL_CURRENT_LINE,
            desktop_keybinding=kb_unmodified_kp_up_2,
            laptop_keybinding=kb_orca_i_2,
        ),
        KeyboardCommand(
            "reviewPhoneticCurrentLineHandler",
            owner.phonetic_line,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_PHONETIC_CURRENT_LINE,
            desktop_keybinding=kb_unmodified_kp_up_3,
            laptop_keybinding=kb_orca_i_3,
        ),
        KeyboardCommand(
            "reviewEndOfLineHandler",
            owner.go_end_of_line,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_END_OF_LINE,
            desktop_keybinding=kb_orca_kp_end,
            laptop_keybinding=kb_orca_ctrl_m,
        ),
        KeyboardCommand(
            "reviewPreviousItemHandler",
            owner.go_previous_item,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_PREVIOUS_ITEM,
            desktop_keybinding=kb_unmodified_kp_left,
            laptop_keybinding=kb_orca_j,
        ),
        KeyboardCommand(
            "reviewCurrentItemHandler",
            owner.present_item,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_CURRENT_ITEM,
            desktop_keybinding=kb_unmodified_kp_begin,
            laptop_keybinding=kb_orca_k,
        ),
        KeyboardCommand(
            "reviewNextItemHandler",
            owner.go_next_item,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_NEXT_ITEM,
            desktop_keybinding=kb_unmodified_kp_right,
            laptop_keybinding=kb_orca_l,
        ),
        KeyboardCommand(
            "reviewSpellCurrentItemHandler",
            owner.spell_item,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_SPELL_CURRENT_ITEM,
            desktop_keybinding=kb_unmodified_kp_begin_2,
            laptop_keybinding=kb_orca_k_2,
        ),
        KeyboardCommand(
            "reviewPhoneticCurrentItemHandler",
            owner.phonetic_item,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_PHONETIC_CURRENT_ITEM,
            desktop_keybinding=kb_unmodified_kp_begin_3,
            laptop_keybinding=kb_orca_k_3,
        ),
        KeyboardCommand(
            "reviewPreviousCharacterHandler",
            owner.go_previous_character,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_PREVIOUS_CHARACTER,
            desktop_keybinding=kb_unmodified_kp_end,
            laptop_keybinding=kb_orca_m,
        ),
        KeyboardCommand(
            "reviewCurrentCharacterHandler",
            owner.present_character,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_CURRENT_CHARACTER,
            desktop_keybinding=kb_unmodified_kp_down,
            laptop_keybinding=kb_orca_comma,
        ),
        KeyboardCommand(
            "reviewSpellCurrentCharacterHandler",
            owner.spell_character,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_SPELL_CURRENT_CHARACTER,
            desktop_keybinding=kb_unmodified_kp_down_2,
            laptop_keybinding=kb_orca_comma_2,
        ),
        KeyboardCommand(
            "reviewUnicodeCurrentCharacterHandler",
            owner.unicode_current_character,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_UNICODE_CURRENT_CHARACTER,
            desktop_keybinding=kb_unmodified_kp_down_3,
            laptop_keybinding=kb_orca_comma_3,
        ),
        KeyboardCommand(
            "reviewNextCharacterHandler",
            owner.go_next_character,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_NEXT_CHARACTER,
            desktop_keybinding=kb_unmodified_kp_page_down,
            laptop_keybinding=kb_orca_period,
        ),
        KeyboardCommand(
            "reviewCurrentAccessibleHandler",
            owner.present_object,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_CURRENT_ACCESSIBLE,
            desktop_keybinding=kb_orca_kp_begin,
            laptop_keybinding=kb_orca_ctrl_k,
        ),
        KeyboardCommand(
            "reviewAboveHandler",
            owner.go_above,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_ABOVE,
            desktop_keybinding=kb_orca_kp_left,
            laptop_keybinding=kb_orca_ctrl_j,
        ),
        KeyboardCommand(
            "reviewBelowHandler",
            owner.go_below,
            owner.GROUP_LABEL,
            cmdnames.REVIEW_BELOW,
            desktop_keybinding=kb_orca_kp_right,
            laptop_keybinding=kb_orca_ctrl_l,
        ),
        KeyboardCommand(
            "showContentsHandler",
            owner.show_contents,
            owner.GROUP_LABEL,
            cmdnames.FLAT_REVIEW_SHOW_CONTENTS,
        ),
        KeyboardCommand(
            "flatReviewCopyHandler",
            owner.copy_to_clipboard,
            owner.GROUP_LABEL,
            cmdnames.FLAT_REVIEW_COPY,
        ),
        KeyboardCommand(
            "flatReviewAppendHandler",
            owner.append_to_clipboard,
            owner.GROUP_LABEL,
            cmdnames.FLAT_REVIEW_APPEND,
        ),
        KeyboardCommand(
            "flatReviewSayAllHandler",
            owner.say_all,
            owner.GROUP_LABEL,
            cmdnames.SAY_ALL_FLAT_REVIEW,
            desktop_keybinding=kb_unmodified_kp_add_2,
            laptop_keybinding=kb_orca_semicolon_2,
        ),
        KeyboardCommand(
            "flatReviewToggleRestrictHandler",
            owner.toggle_restrict,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_RESTRICT_FLAT_REVIEW,
        ),
        KeyboardCommand(
            "move_review_to_focus",
            owner.move_review_to_focus,
            owner.GROUP_LABEL,
            cmdnames.MOVE_REVIEW_TO_FOCUS,
        ),
        KeyboardCommand(
            "move_focus_to_review",
            owner.move_focus_to_review,
            owner.GROUP_LABEL,
            cmdnames.MOVE_FOCUS_TO_REVIEW,
        ),
    ]
    _append_braille_command(
        commands,
        "toggleFlatReviewModeHandler",
        owner.toggle_flat_review_mode,
        owner.GROUP_LABEL,
        cmdnames.TOGGLE_FLAT_REVIEW,
        braille.BRLAPI_KEY_CMD_FREEZE,
    )
    _append_braille_command(
        commands,
        "reviewHomeHandler",
        owner.go_home,
        owner.GROUP_LABEL,
        cmdnames.REVIEW_HOME,
        braille.BRLAPI_KEY_CMD_TOP_LEFT,
    )
    _append_braille_command(
        commands,
        "reviewBottomLeftHandler",
        owner.go_bottom_left,
        owner.GROUP_LABEL,
        cmdnames.REVIEW_BOTTOM_LEFT,
        braille.BRLAPI_KEY_CMD_BOT_LEFT,
    )
    _append_braille_command(
        commands,
        "reviewAboveHandler",
        owner.go_above,
        owner.GROUP_LABEL,
        cmdnames.REVIEW_ABOVE,
        braille.BRLAPI_KEY_CMD_LNUP,
    )
    _append_braille_command(
        commands,
        "reviewBelowHandler",
        owner.go_below,
        owner.GROUP_LABEL,
        cmdnames.REVIEW_BELOW,
        braille.BRLAPI_KEY_CMD_LNDN,
    )
    return commands
