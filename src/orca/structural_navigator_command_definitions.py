# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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

"""Command definitions for structural navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from collections.abc import Callable

    from .input_event import InputEvent
    from .scripts import default
    from .structural_navigator import StructuralNavigator

    CommandCallback = Callable[[default.Script, InputEvent | None, bool], bool]


NAVIGATION_BINDINGS = (
    ("q", "blockquote", "blockquotes"),
    ("b", "button", "buttons"),
    ("x", "checkbox", "checkboxes"),
    ("c", "combobox", "comboboxes"),
    ("e", "entry", "entries"),
    ("f", "form_field", "form_fields"),
    ("h", "heading", "headings"),
    ("g", "image", "images"),
    ("m", "landmark", "landmarks"),
    ("l", "list", "lists"),
    ("i", "list_item", "list_items"),
    ("p", "paragraph", "paragraphs"),
    ("r", "radio_button", "radio_buttons"),
    ("t", "table", "tables"),
    ("k", "link", "links"),
    ("u", "unvisited_link", "unvisited_links"),
    ("v", "visited_link", "visited_links"),
    ("o", "large_object", "large_objects"),
    ("a", "clickable", "clickables"),
)

COMMAND_SPECS = (
    ("previous_annotation", "previous_annotation", cmdnames.ANNOTATION_PREV),
    ("next_annotation", "next_annotation", cmdnames.ANNOTATION_NEXT),
    ("list_annotations", "list_annotations", cmdnames.ANNOTATION_LIST),
    ("previous_blockquote", "previous_blockquote", cmdnames.BLOCKQUOTE_PREV),
    ("next_blockquote", "next_blockquote", cmdnames.BLOCKQUOTE_NEXT),
    ("list_blockquotes", "list_blockquotes", cmdnames.BLOCKQUOTE_LIST),
    ("previous_button", "previous_button", cmdnames.BUTTON_PREV),
    ("next_button", "next_button", cmdnames.BUTTON_NEXT),
    ("list_buttons", "list_buttons", cmdnames.BUTTON_LIST),
    ("previous_checkbox", "previous_checkbox", cmdnames.CHECK_BOX_PREV),
    ("next_checkbox", "next_checkbox", cmdnames.CHECK_BOX_NEXT),
    ("list_checkboxes", "list_checkboxes", cmdnames.CHECK_BOX_LIST),
    ("previous_combobox", "previous_combobox", cmdnames.COMBO_BOX_PREV),
    ("next_combobox", "next_combobox", cmdnames.COMBO_BOX_NEXT),
    ("list_comboboxes", "list_comboboxes", cmdnames.COMBO_BOX_LIST),
    ("previous_entry", "previous_entry", cmdnames.ENTRY_PREV),
    ("next_entry", "next_entry", cmdnames.ENTRY_NEXT),
    ("list_entries", "list_entries", cmdnames.ENTRY_LIST),
    ("previous_form_field", "previous_form_field", cmdnames.FORM_FIELD_PREV),
    ("next_form_field", "next_form_field", cmdnames.FORM_FIELD_NEXT),
    ("list_form_fields", "list_form_fields", cmdnames.FORM_FIELD_LIST),
    ("previous_heading", "previous_heading", cmdnames.HEADING_PREV),
    ("next_heading", "next_heading", cmdnames.HEADING_NEXT),
    ("list_headings", "list_headings", cmdnames.HEADING_LIST),
    ("previous_iframe", "previous_iframe", cmdnames.IFRAME_PREV),
    ("next_iframe", "next_iframe", cmdnames.IFRAME_NEXT),
    ("list_iframes", "list_iframes", cmdnames.IFRAME_LIST),
    ("previous_image", "previous_image", cmdnames.IMAGE_PREV),
    ("next_image", "next_image", cmdnames.IMAGE_NEXT),
    ("list_images", "list_images", cmdnames.IMAGE_LIST),
    ("previous_landmark", "previous_landmark", cmdnames.LANDMARK_PREV),
    ("next_landmark", "next_landmark", cmdnames.LANDMARK_NEXT),
    ("list_landmarks", "list_landmarks", cmdnames.LANDMARK_LIST),
    ("previous_list", "previous_list", cmdnames.LIST_PREV),
    ("next_list", "next_list", cmdnames.LIST_NEXT),
    ("list_lists", "list_lists", cmdnames.LIST_LIST),
    ("previous_list_item", "previous_list_item", cmdnames.LIST_ITEM_PREV),
    ("next_list_item", "next_list_item", cmdnames.LIST_ITEM_NEXT),
    ("list_list_items", "list_list_items", cmdnames.LIST_ITEM_LIST),
    ("previous_live_region", "previous_live_region", cmdnames.LIVE_REGION_PREV),
    ("next_live_region", "next_live_region", cmdnames.LIVE_REGION_NEXT),
    ("last_live_region", "_last_live_region", cmdnames.LIVE_REGION_LAST),
    ("previous_paragraph", "previous_paragraph", cmdnames.PARAGRAPH_PREV),
    ("next_paragraph", "next_paragraph", cmdnames.PARAGRAPH_NEXT),
    ("list_paragraphs", "list_paragraphs", cmdnames.PARAGRAPH_LIST),
    ("previous_radio_button", "previous_radio_button", cmdnames.RADIO_BUTTON_PREV),
    ("next_radio_button", "next_radio_button", cmdnames.RADIO_BUTTON_NEXT),
    ("list_radio_buttons", "list_radio_buttons", cmdnames.RADIO_BUTTON_LIST),
    ("previous_separator", "previous_separator", cmdnames.SEPARATOR_PREV),
    ("next_separator", "next_separator", cmdnames.SEPARATOR_NEXT),
    ("previous_table", "previous_table", cmdnames.TABLE_PREV),
    ("next_table", "next_table", cmdnames.TABLE_NEXT),
    ("list_tables", "list_tables", cmdnames.TABLE_LIST),
    ("previous_link", "previous_link", cmdnames.LINK_PREV),
    ("next_link", "next_link", cmdnames.LINK_NEXT),
    ("list_links", "list_links", cmdnames.LINK_LIST),
    ("previous_unvisited_link", "previous_unvisited_link", cmdnames.UNVISITED_LINK_PREV),
    ("next_unvisited_link", "next_unvisited_link", cmdnames.UNVISITED_LINK_NEXT),
    ("list_unvisited_links", "list_unvisited_links", cmdnames.UNVISITED_LINK_LIST),
    ("previous_visited_link", "previous_visited_link", cmdnames.VISITED_LINK_PREV),
    ("next_visited_link", "next_visited_link", cmdnames.VISITED_LINK_NEXT),
    ("list_visited_links", "list_visited_links", cmdnames.VISITED_LINK_LIST),
    ("previous_large_object", "previous_large_object", cmdnames.LARGE_OBJECT_PREV),
    ("next_large_object", "next_large_object", cmdnames.LARGE_OBJECT_NEXT),
    ("list_large_objects", "list_large_objects", cmdnames.LARGE_OBJECT_LIST),
    ("previous_clickable", "previous_clickable", cmdnames.CLICKABLE_PREV),
    ("next_clickable", "next_clickable", cmdnames.CLICKABLE_NEXT),
    ("list_clickables", "list_clickables", cmdnames.CLICKABLE_LIST),
    ("container_start", "container_start", cmdnames.CONTAINER_START),
    ("container_end", "container_end", cmdnames.CONTAINER_END),
)


def _get_command_bindings() -> dict[str, keybindings.KeyBinding | None]:
    """Returns command name to keybinding mapping."""

    command_bindings: dict[str, keybindings.KeyBinding | None] = {}
    for key, singular, plural in NAVIGATION_BINDINGS:
        command_bindings[f"previous_{singular}"] = keybindings.KeyBinding(
            key,
            keybindings.SHIFT_MODIFIER_MASK,
        )
        command_bindings[f"next_{singular}"] = keybindings.KeyBinding(
            key,
            keybindings.NO_MODIFIER_MASK,
        )
        command_bindings[f"list_{plural}"] = keybindings.KeyBinding(
            key,
            keybindings.SHIFT_ALT_MODIFIER_MASK,
        )

    command_bindings["previous_separator"] = keybindings.KeyBinding(
        "s",
        keybindings.SHIFT_MODIFIER_MASK,
    )
    command_bindings["next_separator"] = keybindings.KeyBinding(
        "s",
        keybindings.NO_MODIFIER_MASK,
    )
    command_bindings["previous_live_region"] = keybindings.KeyBinding(
        "d",
        keybindings.SHIFT_MODIFIER_MASK,
    )
    command_bindings["next_live_region"] = keybindings.KeyBinding(
        "d",
        keybindings.NO_MODIFIER_MASK,
    )
    command_bindings["last_live_region"] = keybindings.KeyBinding(
        "y",
        keybindings.NO_MODIFIER_MASK,
    )
    command_bindings["container_start"] = keybindings.KeyBinding(
        "comma",
        keybindings.SHIFT_MODIFIER_MASK,
    )
    command_bindings["container_end"] = keybindings.KeyBinding(
        "comma",
        keybindings.NO_MODIFIER_MASK,
    )
    command_bindings["previous_annotation"] = None
    command_bindings["next_annotation"] = None
    command_bindings["list_annotations"] = None
    command_bindings["previous_iframe"] = None
    command_bindings["next_iframe"] = None
    command_bindings["list_iframes"] = None
    return command_bindings


def _command_callback(owner: StructuralNavigator, method_name: str) -> CommandCallback:
    """Returns the command callback for method_name."""

    return getattr(owner, method_name)  # pylint: disable=protected-access


def get_commands(owner: StructuralNavigator) -> list[Command]:
    """Returns commands for structural navigation."""

    kb_orca_z = keybindings.KeyBinding("z", keybindings.ORCA_MODIFIER_MASK)
    commands: list[Command] = [
        KeyboardCommand(
            "structural_navigator_mode_cycle",
            owner.cycle_mode,
            owner.GROUP_LABEL,
            cmdnames.STRUCTURAL_NAVIGATION_MODE_CYCLE,
            desktop_keybinding=kb_orca_z,
            laptop_keybinding=kb_orca_z,
            is_group_toggle=True,
        ),
    ]

    command_bindings = _get_command_bindings()
    for name, method_name, description in COMMAND_SPECS:
        kb = command_bindings.get(name)
        commands.append(
            KeyboardCommand(
                name,
                _command_callback(owner, method_name),
                owner.GROUP_LABEL,
                description,
                desktop_keybinding=kb,
                laptop_keybinding=kb,
            ),
        )

    for level in range(1, 7):
        kb_previous = keybindings.KeyBinding(str(level), keybindings.SHIFT_MODIFIER_MASK)
        kb_next = keybindings.KeyBinding(str(level), keybindings.NO_MODIFIER_MASK)
        kb_list = keybindings.KeyBinding(str(level), keybindings.SHIFT_ALT_MODIFIER_MASK)

        heading_commands = (
            (
                f"previous_heading_level_{level}",
                f"previous_heading_level_{level}",
                cmdnames.HEADING_AT_LEVEL_PREV % level,
                kb_previous,
            ),
            (
                f"next_heading_level_{level}",
                f"next_heading_level_{level}",
                cmdnames.HEADING_AT_LEVEL_NEXT % level,
                kb_next,
            ),
            (
                f"list_headings_level_{level}",
                f"list_headings_level_{level}",
                cmdnames.HEADING_AT_LEVEL_LIST % level,
                kb_list,
            ),
        )
        for name, method_name, description, kb in heading_commands:
            commands.append(
                KeyboardCommand(
                    name,
                    _command_callback(owner, method_name),
                    owner.GROUP_LABEL,
                    description,
                    desktop_keybinding=kb,
                    laptop_keybinding=kb,
                ),
            )

    return commands
