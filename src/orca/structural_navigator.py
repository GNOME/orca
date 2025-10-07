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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches

"""Implements structural navigation."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

from enum import Enum
from typing import Callable, TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import cmdnames
from . import dbus_service
from . import debug
from . import focus_manager
from . import guilabels
from . import input_event_manager
from . import keybindings
from . import messages
from . import object_properties
from . import orca_gui_navlist
from . import say_all_presenter
from . import script_manager
from . import settings_manager
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .input_event import InputEvent, InputEventHandler

if TYPE_CHECKING:
    from .scripts import default

class NavigationMode(Enum):
    """Represents the structural navigation modes available."""

    OFF = "OFF"
    DOCUMENT = "DOCUMENT"
    GUI = "GUI"

class StructuralNavigator:
    """Implements the structural navigation support available to scripts."""

    def __init__(self) -> None:
        self._last_input_event: InputEvent | None = None

        # To make it possible for focus mode to suspend this navigation without
        # changing the user's preferred setting.
        self._suspended: bool = False
        self._handlers: dict = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._mode_for_script: dict[default.Script, NavigationMode] = {}
        self._previous_mode_for_script: dict[default.Script, NavigationMode] = {}

        msg = "STRUCTURAL NAVIGATOR: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("StructuralNavigator", self)

    def get_handlers(self, refresh: bool = False) -> dict[str, InputEventHandler]:
        """Returns the structural navigation input event handlers."""

        if refresh:
            msg = "STRUCTURAL NAVIGATOR: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the structural navigation input event handlers."""

        self._handlers = {}

        self._handlers["structural_navigator_mode_cycle"] = \
            InputEventHandler(
                self.cycle_mode,
                cmdnames.STRUCTURAL_NAVIGATION_MODE_CYCLE,
                enabled = not self._suspended)

        enabled = self.get_is_enabled() and not self._suspended

        self._handlers["previous_blockquote"] = InputEventHandler(
            self.previous_blockquote, cmdnames.BLOCKQUOTE_PREV, enabled=enabled)
        self._handlers["next_blockquote"] = InputEventHandler(
                self.next_blockquote, cmdnames.BLOCKQUOTE_NEXT, enabled=enabled)
        self._handlers["list_blockquotes"] = InputEventHandler(
                self.list_blockquotes, cmdnames.BLOCKQUOTE_LIST, enabled=enabled)

        self._handlers["previous_button"] = InputEventHandler(
            self.previous_button, cmdnames.BUTTON_PREV, enabled=enabled)
        self._handlers["next_button"] = InputEventHandler(
            self.next_button, cmdnames.BUTTON_NEXT, enabled=enabled)
        self._handlers["list_buttons"] = InputEventHandler(
            self.list_buttons, cmdnames.BUTTON_LIST, enabled=enabled)

        self._handlers["previous_checkbox"] = InputEventHandler(
            self.previous_checkbox, cmdnames.CHECK_BOX_PREV, enabled=enabled)
        self._handlers["next_checkbox"] = InputEventHandler(
            self.next_checkbox, cmdnames.CHECK_BOX_NEXT, enabled=enabled)
        self._handlers["list_checkboxes"] = InputEventHandler(
            self.list_checkboxes, cmdnames.CHECK_BOX_LIST, enabled=enabled)

        self._handlers["previous_combobox"] = InputEventHandler(
            self.previous_combobox, cmdnames.COMBO_BOX_PREV, enabled=enabled)
        self._handlers["next_combobox"] = InputEventHandler(
            self.next_combobox, cmdnames.COMBO_BOX_NEXT, enabled=enabled)
        self._handlers["list_comboboxes"] = InputEventHandler(
            self.list_comboboxes, cmdnames.COMBO_BOX_LIST, enabled=enabled)

        self._handlers["previous_entry"] = InputEventHandler(
            self.previous_entry, cmdnames.ENTRY_PREV, enabled=enabled)
        self._handlers["next_entry"] = InputEventHandler(
            self.next_entry, cmdnames.ENTRY_NEXT, enabled=enabled)
        self._handlers["list_entries"] = InputEventHandler(
            self.list_entries, cmdnames.ENTRY_LIST, enabled=enabled)

        self._handlers["previous_form_field"] = InputEventHandler(
            self.previous_form_field, cmdnames.FORM_FIELD_PREV, enabled=enabled)
        self._handlers["next_form_field"] = InputEventHandler(
            self.next_form_field, cmdnames.FORM_FIELD_NEXT, enabled=enabled)
        self._handlers["list_form_fields"] = InputEventHandler(
            self.list_form_fields, cmdnames.FORM_FIELD_LIST, enabled=enabled)

        self._handlers["previous_heading"] = InputEventHandler(
            self.previous_heading, cmdnames.HEADING_PREV, enabled=enabled)
        self._handlers["next_heading"] = InputEventHandler(
            self.next_heading, cmdnames.HEADING_NEXT, enabled=enabled)
        self._handlers["list_headings"] = InputEventHandler(
            self.list_headings, cmdnames.HEADING_LIST, enabled=enabled)
        for i in range(1, 7):
            self._handlers[f"previous_heading_level_{i}"] = InputEventHandler(
                getattr(self, f"previous_heading_level_{i}"),
                cmdnames.HEADING_AT_LEVEL_PREV % i, enabled=enabled)
            self._handlers[f"next_heading_level_{i}"] = InputEventHandler(
                getattr(self, f"next_heading_level_{i}"),
                cmdnames.HEADING_AT_LEVEL_NEXT % i, enabled=enabled)
            self._handlers[f"list_headings_level_{i}"] = InputEventHandler(
                getattr(self, f"list_headings_level_{i}"),
                cmdnames.HEADING_AT_LEVEL_LIST % i, enabled=enabled)

        self._handlers["previous_iframe"] = InputEventHandler(
            self.previous_iframe, cmdnames.IFRAME_PREV, enabled=enabled)
        self._handlers["next_iframe"] = InputEventHandler(
            self.next_iframe, cmdnames.IFRAME_NEXT, enabled=enabled)
        self._handlers["list_iframes"] = InputEventHandler(
            self.list_iframes, cmdnames.IFRAME_LIST, enabled=enabled)

        self._handlers["previous_image"] = InputEventHandler(
            self.previous_image, cmdnames.IMAGE_PREV, enabled=enabled)
        self._handlers["next_image"] = InputEventHandler(
            self.next_image, cmdnames.IMAGE_NEXT, enabled=enabled)
        self._handlers["list_images"] = InputEventHandler(
            self.list_images, cmdnames.IMAGE_LIST, enabled=enabled)

        self._handlers["previous_landmark"] = InputEventHandler(
            self.previous_landmark, cmdnames.LANDMARK_PREV, enabled=enabled)
        self._handlers["next_landmark"] = InputEventHandler(
            self.next_landmark, cmdnames.LANDMARK_NEXT, enabled=enabled)
        self._handlers["list_landmarks"] = InputEventHandler(
            self.list_landmarks, cmdnames.LANDMARK_LIST, enabled=enabled)

        self._handlers["previous_list"] = InputEventHandler(
            self.previous_list, cmdnames.LIST_PREV, enabled=enabled)
        self._handlers["next_list"] = InputEventHandler(
            self.next_list, cmdnames.LIST_NEXT, enabled=enabled)
        self._handlers["list_lists"] = InputEventHandler(
            self.list_lists, cmdnames.LIST_LIST, enabled=enabled)

        self._handlers["previous_list_item"] = InputEventHandler(
            self.previous_list_item, cmdnames.LIST_ITEM_PREV, enabled=enabled)
        self._handlers["next_list_item"] = InputEventHandler(
            self.next_list_item, cmdnames.LIST_ITEM_NEXT, enabled=enabled)
        self._handlers["list_list_items"] = InputEventHandler(
            self.list_list_items, cmdnames.LIST_ITEM_LIST, enabled=enabled)

        self._handlers["previous_live_region"] = InputEventHandler(
            self.previous_live_region, cmdnames.LIVE_REGION_PREV, enabled=enabled)
        self._handlers["next_live_region"] = InputEventHandler(
            self.next_live_region, cmdnames.LIVE_REGION_NEXT, enabled=enabled)
        self._handlers["last_live_region"] = InputEventHandler(
            self._last_live_region, cmdnames.LIVE_REGION_LAST, enabled=enabled)

        self._handlers["previous_paragraph"] = InputEventHandler(
            self.previous_paragraph, cmdnames.PARAGRAPH_PREV, enabled=enabled)
        self._handlers["next_paragraph"] = InputEventHandler(
            self.next_paragraph, cmdnames.PARAGRAPH_NEXT, enabled=enabled)
        self._handlers["list_paragraphs"] = InputEventHandler(
            self.list_paragraphs, cmdnames.PARAGRAPH_LIST, enabled=enabled)

        self._handlers["previous_radio_button"] = InputEventHandler(
            self.previous_radio_button, cmdnames.RADIO_BUTTON_PREV, enabled=enabled)
        self._handlers["next_radio_button"] = InputEventHandler(
            self.next_radio_button, cmdnames.RADIO_BUTTON_NEXT, enabled=enabled)
        self._handlers["list_radio_buttons"] = InputEventHandler(
            self.list_radio_buttons, cmdnames.RADIO_BUTTON_LIST, enabled=enabled)

        self._handlers["previous_separator"] = InputEventHandler(
            self.previous_separator, cmdnames.SEPARATOR_PREV, enabled=enabled)
        self._handlers["next_separator"] = InputEventHandler(
            self.next_separator, cmdnames.SEPARATOR_NEXT, enabled=enabled)

        self._handlers["previous_table"] = InputEventHandler(
            self.previous_table, cmdnames.TABLE_PREV, enabled=enabled)
        self._handlers["next_table"] = InputEventHandler(
            self.next_table, cmdnames.TABLE_NEXT, enabled=enabled)
        self._handlers["list_tables"] = InputEventHandler(
            self.list_tables, cmdnames.TABLE_LIST, enabled=enabled)

        self._handlers["previous_link"] = InputEventHandler(
            self.previous_link, cmdnames.LINK_PREV, enabled=enabled)
        self._handlers["next_link"] = InputEventHandler(
            self.next_link, cmdnames.LINK_NEXT, enabled=enabled)
        self._handlers["list_links"] = InputEventHandler(
            self.list_links, cmdnames.LINK_LIST, enabled=enabled)
        self._handlers["previous_unvisited_link"] = InputEventHandler(
            self.previous_unvisited_link, cmdnames.UNVISITED_LINK_PREV, enabled=enabled)
        self._handlers["next_unvisited_link"] = InputEventHandler(
            self.next_unvisited_link, cmdnames.UNVISITED_LINK_NEXT, enabled=enabled)
        self._handlers["list_unvisited_links"] = InputEventHandler(
            self.list_unvisited_links, cmdnames.UNVISITED_LINK_LIST, enabled=enabled)
        self._handlers["previous_visited_link"] = InputEventHandler(
            self.previous_visited_link, cmdnames.VISITED_LINK_PREV, enabled=enabled)
        self._handlers["next_visited_link"] = InputEventHandler(
            self.next_visited_link, cmdnames.VISITED_LINK_NEXT, enabled=enabled)
        self._handlers["list_visited_links"] = InputEventHandler(
            self.list_visited_links, cmdnames.VISITED_LINK_LIST, enabled=enabled)

        self._handlers["previous_large_object"] = InputEventHandler(
            self.previous_large_object, cmdnames.LARGE_OBJECT_PREV, enabled=enabled)
        self._handlers["next_large_object"] = InputEventHandler(
            self.next_large_object, cmdnames.LARGE_OBJECT_NEXT, enabled=enabled)
        self._handlers["list_large_objects"] = InputEventHandler(
            self.list_large_objects, cmdnames.LARGE_OBJECT_LIST, enabled=enabled)

        self._handlers["previous_clickable"] = InputEventHandler(
            self.previous_clickable, cmdnames.CLICKABLE_PREV, enabled=enabled)
        self._handlers["next_clickable"] = InputEventHandler(
            self.next_clickable, cmdnames.CLICKABLE_NEXT, enabled=enabled)
        self._handlers["list_clickables"] = InputEventHandler(
            self.list_clickables, cmdnames.CLICKABLE_LIST, enabled=enabled)

        self._handlers["container_start"] = InputEventHandler(
            self.container_start, cmdnames.CONTAINER_START, enabled=enabled)
        self._handlers["container_end"] = InputEventHandler(
            self.container_end, cmdnames.CONTAINER_END, enabled=enabled)

        msg = f"STRUCTURAL NAVIGATOR: Handlers set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the structural navigation keybindings."""

        if refresh:
            msg = f"STRUCTURAL NAVIGATOR: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("STRUCTURAL NAVIGATOR: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def _setup_bindings(self) -> None:
        """Sets up the structural navigation keybindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "z",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["structural_navigator_mode_cycle"],
                1,
                not self._suspended))

        enabled = self.get_is_enabled() and not self._suspended

        self._bindings.add(
            keybindings.KeyBinding(
                "q",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_blockquote"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "q",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_blockquote"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "q",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_blockquotes"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_button"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_button"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "b",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_buttons"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "x",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_checkbox"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "x",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_checkbox"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "x",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_checkboxes"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_combobox"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_combobox"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "c",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_comboboxes"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_entry"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_entry"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_entries"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_form_field"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_form_field"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_form_fields"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "h",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_heading"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "h",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_heading"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "h",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_headings"],
                1,
                enabled))

        for i in range(1, 7):
            self._bindings.add(
                keybindings.KeyBinding(
                    str(i),
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.SHIFT_MODIFIER_MASK,
                    self._handlers[f"previous_heading_level_{i}"],
                    1,
                    enabled))

            self._bindings.add(
                keybindings.KeyBinding(
                    str(i),
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.NO_MODIFIER_MASK,
                    self._handlers[f"next_heading_level_{i}"],
                    1,
                    enabled))

            self._bindings.add(
                keybindings.KeyBinding(
                    str(i),
                    keybindings.DEFAULT_MODIFIER_MASK,
                    keybindings.SHIFT_ALT_MODIFIER_MASK,
                    self._handlers[f"list_headings_level_{i}"],
                    1,
                    enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_iframe"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_iframe"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_iframes"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "g",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_image"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "g",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_image"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "g",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_images"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_landmark"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_landmark"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "m",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_landmarks"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_list"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_list"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "l",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_lists"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_list_item"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_list_item"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "i",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_list_items"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "d",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_live_region"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "d",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_live_region"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "y",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["last_live_region"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "p",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_paragraph"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "p",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_paragraph"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "p",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_paragraphs"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_radio_button"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_radio_button"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "r",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_radio_buttons"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "s",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_separator"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "s",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_separator"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_table"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_table"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "t",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_tables"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_link"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_link"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "k",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_links"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_unvisited_link"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_unvisited_link"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "u",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_unvisited_links"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "v",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_visited_link"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "v",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_visited_link"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "v",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_visited_links"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_large_object"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_large_object"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "o",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_large_objects"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["previous_clickable"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["next_clickable"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_ALT_MODIFIER_MASK,
                self._handlers["list_clickables"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.SHIFT_MODIFIER_MASK,
                self._handlers["container_start"],
                1,
                enabled))

        self._bindings.add(
            keybindings.KeyBinding(
                "comma",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["container_end"],
                1,
                enabled))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

        msg = f"STRUCTURAL NAVIGATOR: Bindings set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _is_active_script(self, script):
        active_script = script_manager.get_manager().get_active_script()
        if active_script == script:
            return True

        tokens = ["STRUCTURAL NAVIGATOR:", script, "is not the active script", active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def get_mode(self, script: default.Script) -> NavigationMode:
        """Returns the current structural-navigator mode associated with script."""

        mode = self._mode_for_script.get(script, NavigationMode.OFF)
        tokens = ["STRUCTURAL NAVIGATOR: Mode for", script, f"is {mode}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return mode

    def set_mode(self, script: default.Script, mode: NavigationMode) -> None:
        """Sets the structural-navigator mode."""

        tokens = ["STRUCTURAL NAVIGATOR: Setting mode for", script, f"to {mode}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._mode_for_script[script] = mode

        if not (script and self._is_active_script(script)):
            return

        enabled = mode != NavigationMode.OFF
        settings_manager.get_manager().set_setting("structuralNavigationEnabled", enabled)
        self.refresh_bindings_and_grabs(script, "Setting structural navigator mode")

    def last_input_event_was_navigation_command(self) -> bool:
        """Returns true if the last input event was a navigation command."""

        if self._last_input_event is None:
            return False

        manager = input_event_manager.get_manager()
        result = manager.last_event_equals_or_is_release_for_event(self._last_input_event)
        if self._last_input_event is not None:
            string = self._last_input_event.as_single_line_string()
        else:
            string = "None"

        msg = (
            f"STRUCTURAL NAVIGATOR: Last navigation event ({string}) "
            f"is last input event: {result}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def last_command_prevents_focus_mode(self) -> bool:
        """Returns True if the last command was navigation but the setting disallows focus mode."""

        if not self.last_input_event_was_navigation_command():
            return False

        return not self.get_triggers_focus_mode()

    def add_bindings(self, script: default.Script, reason: str = "") -> None:
        """Adds structural navigation bindings for script."""

        tokens = ["STRUCTURAL NAVIGATOR: Adding bindings for", script]
        if reason:
            tokens.append(f": {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and self._is_active_script(script)):
            return

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["STRUCTURAL NAVIGATOR:", script,
                      f"had {len(has_grabs)} key grabs prior to adding bindings."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.add(binding, include_grabs=not self._suspended)

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["STRUCTURAL NAVIGATOR:", script, f"now has {len(has_grabs)} key grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def remove_bindings(self, script: default.Script, reason: str = "") -> None:
        """Removes structural navigation bindings for script."""

        tokens = ["STRUCTURAL NAVIGATOR: Removing bindings for", script]
        if reason:
            tokens.append(f": {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and self._is_active_script(script)):
            return

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["STRUCTURAL NAVIGATOR:", script,
                      f"had {len(has_grabs)} key grabs prior to removing bindings."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.remove(binding, include_grabs=True)

        if debug.LEVEL_INFO >= debug.debugLevel:
            has_grabs = script.key_bindings.get_bindings_with_grabs_for_debugging()
            tokens = ["STRUCTURAL NAVIGATOR:", script, f"now has {len(has_grabs)} key grabs."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def refresh_bindings_and_grabs(self, script: default.Script, reason: str = "") -> None:
        """Refreshes structural navigation bindings and grabs for script."""

        reason = " ".join([reason, "(refreshing)"])
        if not (script and self._is_active_script(script)):
            return

        self.remove_bindings(script, reason)
        self.add_bindings(script, reason)

    @dbus_service.getter
    def get_navigation_wraps(self) -> bool:
        """Returns whether navigation wraps when reaching the top/bottom of the document."""

        return settings_manager.get_manager().get_setting("wrappedStructuralNavigation")

    @dbus_service.setter
    def set_navigation_wraps(self, value: bool) -> bool:
        """Sets whether navigation wraps when reaching the top/bottom of the document."""

        msg = f"STRUCTURAL NAVIGATOR: Setting navigation wraps to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("wrappedStructuralNavigation", value)
        return True

    @dbus_service.getter
    def get_large_object_text_length(self) -> int:
        """Returns the minimum number of characters to be considered a 'large object'."""

        return settings_manager.get_manager().get_setting("largeObjectTextLength")

    @dbus_service.setter
    def set_large_object_text_length(self, value: int) -> bool:
        """Sets the minimum number of characters to be considered a 'large object'."""

        msg = f"STRUCTURAL NAVIGATOR: Setting large object text length to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("largeObjectTextLength", value)
        return True

    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether structural navigation is enabled."""

        return settings_manager.get_manager().get_setting("structuralNavigationEnabled")

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether structural navigation is enabled."""

        if self.get_is_enabled() == value:
            return True

        msg = f"STRUCTURAL NAVIGATOR: Setting enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("structuralNavigationEnabled", value)

        script = script_manager.get_manager().get_active_script()
        if not script:
            return True

        current_mode = self.get_mode(script)
        if not value and current_mode == NavigationMode.OFF:
            return True

        self._last_input_event = None
        if value:
            if previous_mode := self._previous_mode_for_script.get(script):
                tokens = ["STRUCTURAL NAVIGATOR: Restoring mode for", script, "to", previous_mode]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                self._mode_for_script[script] = previous_mode
        else:
            self._previous_mode_for_script[script] = current_mode
            tokens = ["STRUCTURAL NAVIGATOR: Saving", current_mode, "as previous mode for", script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._mode_for_script[script] = NavigationMode.OFF

        self.refresh_bindings_and_grabs(script, "D-Bus setter changed enabled state")
        return True

    @dbus_service.getter
    def get_triggers_focus_mode(self) -> bool:
        """Returns whether structural navigation triggers focus mode."""

        return settings_manager.get_manager().get_setting("structNavTriggersFocusMode")

    @dbus_service.setter
    def set_triggers_focus_mode(self, value: bool) -> bool:
        """Sets whether structural navigation triggers focus mode."""

        if self.get_triggers_focus_mode() == value:
            return True

        msg = f"STRUCTURAL NAVIGATOR: Setting triggers focus mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("structNavTriggersFocusMode", value)
        return True

    @dbus_service.command
    def cycle_mode(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Cycles among the structural navigation modes."""

        tokens = ["STRUCTURAL NAVIGATOR: cycle_mode. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (script and self._is_active_script(script)):
            return False

        self._last_input_event = None
        previous_mode = self.get_mode(script)
        msg = ""
        mode = None
        if previous_mode == NavigationMode.OFF:
            mode = NavigationMode.DOCUMENT
            msg = messages.STRUCTURAL_NAVIGATION_KEYS_DOCUMENT
        elif previous_mode == NavigationMode.GUI:
            mode = NavigationMode.OFF
            msg = messages.STRUCTURAL_NAVIGATION_KEYS_OFF
        else:
            mode = NavigationMode.GUI
            msg = messages.STRUCTURAL_NAVIGATION_KEYS_GUI

        if notify_user:
            script.present_message(msg)
        self.set_mode(script, mode)
        if mode != NavigationMode.OFF:
            root = self._determine_root_container(script)
            if not AXObject.supports_collection(root) and notify_user:
                script.present_message(messages.STRUCTURAL_NAVIGATION_NOT_SUPPORTED_FULL,
                                      messages.STRUCTURAL_NAVIGATION_NOT_SUPPORTED_BRIEF)
        return True

    def suspend_commands(self, script, suspended, reason=""):
        """Suspends structural navigation independent of the enabled setting."""

        if not (script and self._is_active_script(script)):
            return

        msg = f"STRUCTURAL NAVIGATOR: Suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._suspended = suspended
        self.refresh_bindings_and_grabs(script, f"Suspended changed to {suspended}")

    def _get_object_in_direction(
        self,
        script: default.Script,
        objects: list[Atspi.Accessible],
        is_next: bool,
        should_wrap: bool | None = None,
        notify_user: bool = True
    ) -> Atspi.Accessible | None:
        """Returns the next/previous object in relation to the current location."""

        if not objects:
            return None

        if should_wrap is None:
            should_wrap = self.get_navigation_wraps()

        # If we're in a matching object, return the next/previous one in the list.
        obj = focus_manager.get_manager().get_locus_of_focus()
        candidate = obj
        while candidate:
            if candidate not in objects:
                candidate = AXObject.get_parent(candidate)
                continue

            # If an author put an ARIA heading inside a native heading (or vice versa), candidate
            # could be the inner heading. If we treat the outer heading as as the previous heading
            # and then set the caret context to the first position inside the outer heading, i.e.
            # the inner heading, we'll get stuck. Thanks authors.
            if AXUtilities.is_heading(candidate) and not is_next:
                if ancestor := AXObject.find_ancestor(candidate, AXUtilities.is_heading):
                    tokens = ["STRUCTURAL NAVIGATOR: Current heading", candidate,
                              "is inside another heading", ancestor,
                              "Treating the ancestor is the current heading."]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    candidate = ancestor

            index = objects.index(candidate)
            if is_next:
                if index + 1 < len(objects):
                    return objects[index + 1]
                if not should_wrap:
                    return None
                if notify_user:
                    script.present_message(messages.WRAPPING_TO_TOP)
                return objects[0]
            if index > 0:
                return objects[index - 1]
            if not should_wrap:
                return None
            if notify_user:
                script.present_message(messages.WRAPPING_TO_BOTTOM)
            return objects[-1]

        # If we're not in a matching object, find the next/previous one based on the path.
        if not is_next:
            objects = list(reversed(objects))

        current_path = AXObject.get_path(obj)
        for match in objects:
            path = AXObject.get_path(match)
            comparison = script.utilities.path_comparison(path, current_path)
            if (comparison > 0 and is_next) or (comparison < 0 and not is_next):
                return match

        if not should_wrap:
            return None

        if is_next:
            if notify_user:
                script.present_message(messages.WRAPPING_TO_TOP)
        else:
            if notify_user:
                script.present_message(messages.WRAPPING_TO_BOTTOM)
        if obj != objects[0]:
            return objects[0]

        return None

    def _get_state_string(self, obj: Atspi.Accessible) -> str:
        if obj is None:
            return ""

        if AXUtilities.is_switch(obj):
            off, on = object_properties.SWITCH_INDICATORS_SPEECH
            if AXUtilities.is_checked(obj):
                return on
            return off

        if AXUtilities.is_check_box(obj):
            unchecked, checked, partially = object_properties.CHECK_BOX_INDICATORS_SPEECH
            if AXUtilities.is_indeterminate(obj):
                return partially
            if AXUtilities.is_checked(obj):
                return checked
            return unchecked

        if AXUtilities.is_radio_button(obj):
            unselected, selected = object_properties.RADIO_BUTTON_INDICATORS_SPEECH
            if AXUtilities.is_checked(obj):
                return selected
            return unselected

        if AXUtilities.is_link(obj):
            if AXUtilities.is_visited(obj):
                return object_properties.STATE_VISITED
            return object_properties.STATE_UNVISITED

        return ""

    def _get_item_string(self, script: default.Script, obj: Atspi.Accessible) -> str:
        if obj is None:
            return ""

        result = AXObject.get_name(obj) or AXObject.get_description(obj) \
            or AXUtilities.get_displayed_label(obj) or AXUtilities.get_displayed_description(obj)
        if result:
            return result

        if AXUtilities.is_table(obj):
            if caption := AXTable.get_caption(obj):
                return AXText.get_all_text(caption)
            return ""

        if AXUtilities.is_internal_frame(obj):
            result = self._get_item_string(script, AXObject.get_child(obj, 0))
            return result or AXUtilities.get_localized_role_name(obj)

        if AXUtilities.is_list(obj):
            children = list(AXObject.iter_children(obj, AXUtilities.is_list_item))
            if AXUtilities.get_nesting_level(obj):
                return messages.nested_list_item_count(len(children))
            return messages.list_item_count(len(children))

        if AXUtilities.is_description_list(obj):
            children = AXUtilities.find_all_description_terms(obj)
            return messages.description_list_term_count(len(children))

        if AXUtilities.is_page_tab_list(obj):
            children = list(AXObject.iter_children(obj, AXUtilities.is_page_tab))
            return messages.tab_list_item_count(len(children))

        if AXUtilities.is_image(obj):
            if result := AXObject.get_image_description(obj):
                return result
            parent = AXObject.get_parent(obj)
            if AXUtilities.is_link(parent):
                return self._get_item_string(script, parent)
            return AXUtilities.get_localized_role_name(obj)

        if result := script.utilities.expand_eocs(obj):
            return result

        if AXUtilities.is_link(obj):
            result = AXHypertext.get_link_basename(obj)

        return result

    def _present_line(
        self,
        script: default.Script,
        obj: Atspi.Accessible | None = None,
        offset: int | None = None,
        notify_user: bool = True
    ) -> None:

        if obj is None:
            return

        manager = focus_manager.get_manager()
        presenter = say_all_presenter.get_presenter()
        if manager.in_say_all() and presenter.get_structural_navigation_enabled():
            presenter.say_all(script, event=None, obj=obj, offset=offset)
            return

        if not notify_user:
            msg = "STRUCTURAL NAVIGATOR: _present_line called with notify_user=False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            manager.set_locus_of_focus(None, obj, False)
            if AXObject.supports_text(obj):
                script.utilities.set_caret_position(obj, offset or 0)
            return

        script.update_braille(obj)
        script.say_line(obj, offset)

    def _present_object(
        self,
        script: default.Script,
        obj: Atspi.Accessible | None = None,
        not_found_message: str = messages.STRUCTURAL_NAVIGATION_NOT_FOUND,
        offset: int | None = None,
        notify_user: bool = True
    ) -> None:
        if obj is None:
            if notify_user:
                script.present_message(not_found_message, messages.STRUCTURAL_NAVIGATION_NOT_FOUND)
            return

        if offset is None:
            offset = 0

        if self.get_mode(script) == NavigationMode.GUI:
            focus_manager.get_manager().set_locus_of_focus(None, obj)
            AXObject.grab_focus(obj)
            AXObject.clear_cache(obj, False, "Checking state after focus grab")
            if not AXUtilities.is_focused(obj) and notify_user:
                script.present_message(messages.NOT_FOCUSED)
            return

        manager = focus_manager.get_manager()
        presenter = say_all_presenter.get_presenter()
        if manager.in_say_all() and presenter.get_structural_navigation_enabled():
            presenter.say_all(script, event=None, obj=obj, offset=offset)
            return

        if not notify_user:
            msg = "STRUCTURAL NAVIGATOR: _present_object called with notify_user=False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            manager.set_locus_of_focus(None, obj, False)
            if AXObject.supports_text(obj):
                script.utilities.set_caret_position(obj, offset)

            return

        script.present_object(obj, offset=offset, interrupt=True)

    def _present_object_list(
        self,
        script: default.Script,
        objects: list[Atspi.Accessible],
        dialog_title: str,
        column_headers: list[str],
        row_data_func: Callable,
        notify_user: bool = True
    ) -> None:
        dialog_title = f"{dialog_title}: {messages.items_found(len(objects))}"
        if not objects:
            if notify_user:
                script.present_message(dialog_title)
            return

        current_object = script.utilities.get_caret_context()[0]
        try:
            index = objects.index(current_object)
        except ValueError:
            index = 0

        rows = [[obj, -1] + row_data_func(obj) for obj in objects]
        orca_gui_navlist.show_ui(dialog_title, column_headers, rows, index)

    def _determine_root_container(self, script: default.Script) -> Atspi.Accessible:
        mode = self.get_mode(script)
        focus = focus_manager.get_manager().get_locus_of_focus()
        root = AXObject.find_ancestor_inclusive(focus, AXUtilities.is_modal_dialog)
        if root is None:
            if mode == NavigationMode.DOCUMENT:
                root = script.utilities.get_top_level_document_for_object(focus)
            elif mode == NavigationMode.GUI:
                root = AXObject.find_ancestor_inclusive(focus, AXUtilities.is_dialog_or_window)
                if root is None:
                    root = focus_manager.get_manager().get_active_window()

        tokens = ["STRUCTURAL NAVIGATOR: Root for", focus, "is", root, f"mode: {mode}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return root

    def _is_non_document_object(self, obj: Atspi.Accessible, must_be_showing: bool = True) -> bool:
        if AXObject.find_ancestor_inclusive(obj, AXUtilities.is_document) is not None:
            return False
        if must_be_showing and not AXUtilities.is_showing(obj):
            return False
        return True

    ########################
    #                      #
    # Blockquotes          #
    #                      #
    ########################

    def _get_all_blockquotes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_block_quotes(root, pred=pred)

    @dbus_service.command
    def previous_blockquote(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous blockquote."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_blockquote. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_blockquotes(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_BLOCKQUOTES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_blockquote(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next blockquote."""

        tokens = ["STRUCTURAL NAVIGATOR: next_blockquote. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_blockquotes(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_BLOCKQUOTES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_blockquotes(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of blockquotes."""

        tokens = ["STRUCTURAL NAVIGATOR: list_blockquotes. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_blockquotes(script),
            guilabels.SN_TITLE_BLOCKQUOTE,
            [guilabels.SN_HEADER_BLOCKQUOTE],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Buttons              #
    #                      #
    ########################

    def _get_all_buttons(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_buttons(root, pred=pred)

    @dbus_service.command
    def previous_button(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous button."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_button. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_buttons(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_BUTTONS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_button(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next button."""

        tokens = ["STRUCTURAL NAVIGATOR: next_button. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_buttons(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_BUTTONS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_buttons(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of buttons."""

        tokens = ["STRUCTURAL NAVIGATOR: list_buttons. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_buttons(script),
            guilabels.SN_TITLE_BUTTON,
            [guilabels.SN_HEADER_BUTTON],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Check boxes          #
    #                      #
    ########################

    def _get_all_checkboxes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_check_boxes(root, pred=pred)

    @dbus_service.command
    def previous_checkbox(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous checkbox."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_checkbox. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_checkboxes(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_CHECK_BOXES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_checkbox(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next checkbox."""

        tokens = ["STRUCTURAL NAVIGATOR: next_checkbox. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_checkboxes(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_CHECK_BOXES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_checkboxes(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of checkboxes."""

        tokens = ["STRUCTURAL NAVIGATOR: list_checkboxes. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_checkboxes(script),
            guilabels.SN_TITLE_CHECK_BOX,
            [guilabels.SN_HEADER_CHECK_BOX, guilabels.SN_HEADER_STATE],
            lambda obj: [self._get_item_string(script, obj), self._get_state_string(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Large Objects        #
    #                      #
    ########################

    def _get_all_large_objects(self, script: default.Script) -> list[Atspi.Accessible]:
        minimum_length = self.get_large_object_text_length()

        def _is_large(obj):
            if AXUtilities.is_heading(obj):
                return True
            text = AXText.get_all_text(obj)
            return len(text) > minimum_length and text.count("\ufffc")/len(text) < 0.05

        root = self._determine_root_container(script)
        roles = AXUtilities.get_large_container_roles() + \
            [Atspi.Role.HEADING, Atspi.Role.PARAGRAPH, Atspi.Role.SECTION]
        return AXUtilities.find_all_with_role(root, roles, pred=_is_large)

    @dbus_service.command
    def previous_large_object(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous large object."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_large_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_large_objects(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_LARGE_OBJECTS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_large_object(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next large object."""

        tokens = ["STRUCTURAL NAVIGATOR: next_large_object. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_large_objects(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_LARGE_OBJECTS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_large_objects(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of large objects."""

        tokens = ["STRUCTURAL NAVIGATOR: list_large_objects. Script:", script,
                  "Event:", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_large_objects(script),
            guilabels.SN_TITLE_LARGE_OBJECT,
            [guilabels.SN_HEADER_OBJECT, guilabels.SN_HEADER_ROLE],
            lambda obj: [self._get_item_string(script, obj),
                         AXUtilities.get_localized_role_name(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Combo Boxes          #
    #                      #
    ########################

    def _get_all_comboboxes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_combo_boxes(root, pred=pred)

    @dbus_service.command
    def previous_combobox(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous combo box."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_combobox. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_comboboxes(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_COMBO_BOXES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_combobox(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next combo box."""

        tokens = ["STRUCTURAL NAVIGATOR: next_combobox. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_comboboxes(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_COMBO_BOXES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_comboboxes(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of combo boxes."""

        tokens = ["STRUCTURAL NAVIGATOR: list_comboboxes. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_comboboxes(script),
            guilabels.SN_TITLE_COMBO_BOX,
            [guilabels.SN_HEADER_COMBO_BOX],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Entries              #
    #                      #
    ########################

    def _get_all_entries(self, script: default.Script) -> list[Atspi.Accessible]:
        def parent_is_not_editable(obj):
            parent = AXObject.get_parent(obj)
            return parent is not None and not AXUtilities.is_editable(parent)

        if self.get_mode(script) == NavigationMode.GUI:
            def pred(x):
                return self._is_non_document_object(x)
        else:
            pred = parent_is_not_editable

        root = self._determine_root_container(script)
        return AXUtilities.find_all_editable_objects(root, pred=pred)

    @dbus_service.command
    def previous_entry(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous entry."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_entry. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_entries(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_ENTRIES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_entry(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next entry."""

        tokens = ["STRUCTURAL NAVIGATOR: next_entry. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_entries(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_ENTRIES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_entries(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of entries."""

        tokens = ["STRUCTURAL NAVIGATOR: list_entries. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_entries(script),
            guilabels.SN_TITLE_ENTRY,
            [guilabels.SN_HEADER_LABEL, guilabels.SN_HEADER_VALUE],
            lambda obj: [self._get_item_string(script, obj), AXText.get_all_text(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Form Fields          #
    #                      #
    ########################

    def _get_all_form_fields(self, script: default.Script) -> list[Atspi.Accessible]:
        def is_not_noneditable_doc_frame(obj):
            if AXUtilities.is_document_frame(obj):
                return AXUtilities.is_editable(obj)
            return True

        def pred(x):
            if self.get_mode(script) == NavigationMode.GUI:
                return self._is_non_document_object(x)
            return is_not_noneditable_doc_frame(x)

        root = self._determine_root_container(script)
        return AXUtilities.find_all_form_fields(root, pred=pred)

    @dbus_service.command
    def previous_form_field(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous form field."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_form_field. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_form_fields(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_FORM_FIELDS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_form_field(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next form field."""

        tokens = ["STRUCTURAL NAVIGATOR: next_form_field. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_form_fields(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_FORM_FIELDS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_form_fields(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of form fields."""

        tokens = ["STRUCTURAL NAVIGATOR: list_form_fields. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_form_fields(script),
            guilabels.SN_TITLE_FORM_FIELD,
            [guilabels.SN_HEADER_LABEL, guilabels.SN_HEADER_ROLE, guilabels.SN_HEADER_VALUE],
            lambda obj: [self._get_item_string(script, obj),
                         AXUtilities.get_localized_role_name(obj),
                         AXText.get_all_text(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Headings             #
    #                      #
    ########################

    def _get_all_headings(self,
        script: default.Script,
        level: int | None = None
    ) -> list[Atspi.Accessible]:

        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        if level is None:
            return AXUtilities.find_all_headings(root, pred=pred)
        return AXUtilities.find_all_headings_at_level(root, level, pred=pred)

    @dbus_service.command
    def previous_heading(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_HEADINGS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_HEADINGS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING,
            [guilabels.SN_HEADER_HEADING, guilabels.SN_HEADER_LEVEL],
            lambda obj: [self._get_item_string(script, obj),
                         str(AXUtilities.get_heading_level(obj))],
            notify_user=notify_user
        )
        return True

    @dbus_service.command
    def previous_heading_level_1(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous level 1 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading_level_1. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 1)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 1, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading_level_1(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next level 1 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading_level_1. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 1)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 1, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings_level_1(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of level 1 headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings_level_1. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 1,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    @dbus_service.command
    def previous_heading_level_2(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous level 2 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading_level_2. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 2)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 2, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading_level_2(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next level 2 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading_level_2. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 2)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 2, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings_level_2(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of level 2 headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings_level_2. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 2,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    @dbus_service.command
    def previous_heading_level_3(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous level 3 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading_level_3. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 3)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 3, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading_level_3(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next level 3 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading_level_3. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 3)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 3, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings_level_3(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of level 3 headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings_level_3. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 3,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    @dbus_service.command
    def previous_heading_level_4(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous level 4 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading_level_4. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 4)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 4, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading_level_4(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next level 4 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading_level_4. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 4)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 4, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings_level_4(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of level 4 headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings_level_4. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 4,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    @dbus_service.command
    def previous_heading_level_5(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous level 5 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading_level_5. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 5)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 5, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading_level_5(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next level 5 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading_level_5. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 5)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 5, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings_level_5(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of level 5 headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings_level_5. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 5,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    @dbus_service.command
    def previous_heading_level_6(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous level 6 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_heading_level_6. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 6)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 6, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_heading_level_6(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next level 6 heading."""

        tokens = ["STRUCTURAL NAVIGATOR: next_heading_level_6. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_headings(script, 6)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_HEADINGS_AT_LEVEL % 6, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_headings_level_6(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of level 6 headings."""

        tokens = ["STRUCTURAL NAVIGATOR: list_headings_level_6. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_headings(script),
            guilabels.SN_TITLE_HEADING_AT_LEVEL % 6,
            [guilabels.SN_HEADER_HEADING],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Iframes              #
    #                      #
    ########################

    def _get_all_iframes(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_internal_frames(root, pred=pred)

    @dbus_service.command
    def previous_iframe(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous iframe."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_iframe. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_iframes(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_IFRAMES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_iframe(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next iframe."""

        tokens = ["STRUCTURAL NAVIGATOR: next_iframe. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_iframes(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_IFRAMES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_iframes(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of iframes."""

        tokens = ["STRUCTURAL NAVIGATOR: list_iframes. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_iframes(script),
            guilabels.SN_TITLE_IFRAME,
            [guilabels.SN_HEADER_IFRAME],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Images               #
    #                      #
    ########################

    def _get_all_images(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_images_and_image_maps(root, pred=pred)

    @dbus_service.command
    def previous_image(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous image."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_image. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_images(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_IMAGES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_image(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next image."""

        tokens = ["STRUCTURAL NAVIGATOR: next_image. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_images(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_IMAGES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_images(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of images."""

        tokens = ["STRUCTURAL NAVIGATOR: list_images. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_images(script),
            guilabels.SN_TITLE_IMAGE,
            [guilabels.SN_HEADER_IMAGE],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Landmarks            #
    #                      #
    ########################

    def _get_all_landmarks(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_landmarks(root, pred=pred)

    def _present_landmark(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        notify_user: bool
    ) -> None:
        if obj is None:
            self._present_object(script, obj, messages.NO_LANDMARK_FOUND, notify_user=notify_user)
            return

        if notify_user:
            script.present_message(AXObject.get_name(obj))
        self._present_line(script, obj, 0)

    @dbus_service.command
    def previous_landmark(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous landmark."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_landmark. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_landmarks(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_landmark(script, result, notify_user)
        return True

    @dbus_service.command
    def next_landmark(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next landmark."""

        tokens = ["STRUCTURAL NAVIGATOR: next_landmark. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_landmarks(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_landmark(script, result, notify_user)
        return True

    @dbus_service.command
    def list_landmarks(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of landmarks."""

        tokens = ["STRUCTURAL NAVIGATOR: list_landmarks. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_landmarks(script),
            guilabels.SN_TITLE_LANDMARK,
            [guilabels.SN_HEADER_LANDMARK, guilabels.SN_HEADER_ROLE],
            lambda obj: [self._get_item_string(script, obj),
                         AXUtilities.get_localized_role_name(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Lists                #
    #                      #
    ########################

    def _get_all_lists(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_lists(
            root, include_description_lists=True, include_tab_lists=True, pred=pred)

    def _get_first_item(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        # The reason we present the item (or first child) rather than the full list are twofold:
        # 1. Given a huge list, navigating to the item and presenting the ancestor list is more
        #    performant.
        # 2. When we calculate what's on the same line, it should be based on the item's bounding
        #    box; not the list's.
        # TODO - JD: Handle the second issue in the utilities which calculate the line.
        return AXObject.get_child(obj, 0)

    @dbus_service.command
    def previous_list(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous list."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_list. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_lists(script)
        result = self._get_object_in_direction(script, matches, False)
        result = self._get_first_item(result) or result
        self._present_object(script, result, messages.NO_MORE_LISTS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_list(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next list."""

        tokens = ["STRUCTURAL NAVIGATOR: next_list. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_lists(script)
        result = self._get_object_in_direction(script, matches, True)
        result = self._get_first_item(result) or result
        self._present_object(script, result, messages.NO_MORE_LISTS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_lists(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of lists."""

        tokens = ["STRUCTURAL NAVIGATOR: list_lists. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_lists(script),
            guilabels.SN_TITLE_LIST,
            [guilabels.SN_HEADER_LIST],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # List Items           #
    #                      #
    ########################

    def _get_all_list_items(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_list_items(
            root, include_description_terms=True, include_tabs=True, pred=pred)

    @dbus_service.command
    def previous_list_item(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous list item."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_list_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_list_items(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_LIST_ITEMS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_list_item(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next list item."""

        tokens = ["STRUCTURAL NAVIGATOR: next_list_item. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_list_items(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_LIST_ITEMS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_list_items(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of list items."""

        tokens = ["STRUCTURAL NAVIGATOR: list_list_items. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_list_items(script),
            guilabels.SN_TITLE_LIST_ITEM,
            [guilabels.SN_HEADER_LIST_ITEM],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Live Regions         #
    #                      #
    ########################

    def _get_all_live_regions(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        return AXUtilities.find_all_live_regions(root, pred=pred)

    @dbus_service.command
    def previous_live_region(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous live region."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_live_region. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_live_regions(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_LIVE_REGIONS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_live_region(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next live region."""

        tokens = ["STRUCTURAL NAVIGATOR: next_live_region. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_live_regions(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_LIVE_REGIONS, notify_user=notify_user)
        return True

    def _last_live_region(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the last live region."""

        tokens = ["STRUCTURAL NAVIGATOR: last_live_region. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        if settings_manager.get_manager().get_setting("inferLiveRegions"):
            if script.live_region_manager is not None:
                script.live_region_manager.goLastLiveRegion()
        elif notify_user:
            script.present_message(messages.LIVE_REGIONS_OFF)
        return True

    ########################
    #                      #
    # Paragraphs           #
    #                      #
    ########################

    def _get_all_paragraphs(self, script: default.Script) -> list[Atspi.Accessible]:
        def has_at_least_three_characters(obj):
            if AXUtilities.is_heading(obj):
                return True
            # We're choosing 3 characters as the minimum because some paragraphs contain a single
            # image or link and a text of length 2: An embedded object character and a space.
            # We want to skip these.
            return AXText.get_character_count(obj) > 2

        def pred(x):
            if self.get_mode(script) == NavigationMode.GUI:
                return self._is_non_document_object(x)
            return has_at_least_three_characters(x)

        root = self._determine_root_container(script)
        return AXUtilities.find_all_paragraphs(root, True, pred=pred)

    @dbus_service.command
    def previous_paragraph(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous paragraph."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_paragraph. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_paragraphs(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_PARAGRAPHS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_paragraph(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next paragraph."""

        tokens = ["STRUCTURAL NAVIGATOR: next_paragraph. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_paragraphs(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_PARAGRAPHS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_paragraphs(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of paragraphs."""

        tokens = ["STRUCTURAL NAVIGATOR: list_paragraphs. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_paragraphs(script),
            guilabels.SN_TITLE_PARAGRAPH,
            [guilabels.SN_HEADER_PARAGRAPH],
            lambda obj: [self._get_item_string(script, obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Radio Buttons        #
    #                      #
    ########################

    def _get_all_radio_buttons(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_radio_buttons(root, pred=pred)

    @dbus_service.command
    def previous_radio_button(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous radio button."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_radio_button. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_radio_buttons(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_RADIO_BUTTONS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_radio_button(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next radio button."""

        tokens = ["STRUCTURAL NAVIGATOR: next_radio_button. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_radio_buttons(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_RADIO_BUTTONS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_radio_buttons(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of radio buttons."""

        tokens = ["STRUCTURAL NAVIGATOR: list_radio_buttons. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_radio_buttons(script),
            guilabels.SN_TITLE_RADIO_BUTTON,
            [guilabels.SN_HEADER_RADIO_BUTTON, guilabels.SN_HEADER_STATE],
            lambda obj: [self._get_item_string(script, obj), self._get_state_string(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Separators           #
    #                      #
    ########################

    def _get_all_separators(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_separators(root, pred=pred)

    @dbus_service.command
    def previous_separator(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous separator."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_separator. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_separators(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_SEPARATORS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_separator(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next separator."""

        tokens = ["STRUCTURAL NAVIGATOR: next_separator. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_separators(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_SEPARATORS, notify_user=notify_user)
        return True

    ########################
    #                      #
    # Tables               #
    #                      #
    ########################

    def _get_all_tables(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_tables(root, pred=pred)

    def _get_first_table_cell(self, table: Atspi.Accessible) -> Atspi.Accessible | None:
        # The reason we present the cell rather than the full table are twofold:
        # 1. Given a huge table, navigating to the cell and presenting the ancestor table is more
        #    performant.
        # 2. When we calculate what's on the same line, it should be based on the cell's bounding
        #    box; not the table's.
        # TODO - JD: Handle the second issue in the utilities which calculate the line.
        if not AXUtilities.is_table(table):
            return None

        if cell := AXTable.get_cell_at(table, 0, 0):
            return cell

        tokens = ["STRUCTURAL NAVIGATOR: Broken table interface for", table]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        cell = AXObject.find_descendant(table, AXUtilities.is_table_cell)
        if cell:
            tokens = ["STRUCTURAL NAVIGATOR: Located", cell, "for first cell"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return None

    @dbus_service.command
    def previous_table(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous table."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_table. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_tables(script)
        result = self._get_object_in_direction(script, matches, False)
        obj = self._get_first_table_cell(result) or result
        self._present_object(script, obj, messages.NO_MORE_TABLES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_table(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next table."""

        tokens = ["STRUCTURAL NAVIGATOR: next_table. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_tables(script)
        result = self._get_object_in_direction(script, matches, True)
        obj = self._get_first_table_cell(result) or result
        self._present_object(script, obj, messages.NO_MORE_TABLES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_tables(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of tables."""

        tokens = ["STRUCTURAL NAVIGATOR: list_tables. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_tables(script),
            guilabels.SN_TITLE_TABLE,
            [guilabels.SN_HEADER_CAPTION, guilabels.SN_HEADER_DESCRIPTION],
            lambda obj: [self._get_item_string(script, obj),
                         AXTable.get_table_description_for_presentation(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Unvisited Links      #
    #                      #
    ########################

    def _get_all_unvisited_links(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_unvisited_links(root, pred=pred)

    @dbus_service.command
    def previous_unvisited_link(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous unvisited link."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_unvisited_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_unvisited_links(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_UNVISITED_LINKS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_unvisited_link(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next unvisited link."""

        tokens = ["STRUCTURAL NAVIGATOR: next_unvisited_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_unvisited_links(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_UNVISITED_LINKS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_unvisited_links(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of unvisited links."""

        tokens = ["STRUCTURAL NAVIGATOR: list_unvisited_links. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_unvisited_links(script),
            guilabels.SN_TITLE_UNVISITED_LINK,
            [guilabels.SN_HEADER_LINK, guilabels.SN_HEADER_URI],
            lambda obj: [self._get_item_string(script, obj), AXHypertext.get_link_uri(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Visited Links        #
    #                      #
    ########################

    def _get_all_visited_links(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_visited_links(root, pred=pred)

    @dbus_service.command
    def previous_visited_link(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous visited link."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_visited_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_visited_links(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(
            script, result, messages.NO_MORE_VISITED_LINKS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_visited_link(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next visited link."""

        tokens = ["STRUCTURAL NAVIGATOR: next_visited_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_visited_links(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(
            script, result, messages.NO_MORE_VISITED_LINKS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_visited_links(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of visited links."""

        tokens = ["STRUCTURAL NAVIGATOR: list_visited_links. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_visited_links(script),
            guilabels.SN_TITLE_VISITED_LINK,
            [guilabels.SN_HEADER_LINK, guilabels.SN_HEADER_URI],
            lambda obj: [self._get_item_string(script, obj), AXHypertext.get_link_uri(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Links                #
    #                      #
    ########################

    def _get_all_links(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object


        root = self._determine_root_container(script)
        return AXUtilities.find_all_links(root, pred=pred)

    @dbus_service.command
    def previous_link(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous link."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_links(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_LINKS, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_link(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next link."""

        tokens = ["STRUCTURAL NAVIGATOR: next_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_links(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_LINKS, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_links(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of links."""

        tokens = ["STRUCTURAL NAVIGATOR: list_links. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_links(script),
            guilabels.SN_TITLE_LINK,
            [guilabels.SN_HEADER_LINK, guilabels.SN_HEADER_STATE, guilabels.SN_HEADER_URI],
            lambda obj: [self._get_item_string(script, obj),
                         self._get_state_string(obj),
                         AXHypertext.get_link_uri(obj)],
            notify_user=notify_user
        )
        return True

    ########################
    #                      #
    # Clickables           #
    #                      #
    ########################

    def _get_all_clickables(self, script: default.Script) -> list[Atspi.Accessible]:
        pred = None
        if self.get_mode(script) == NavigationMode.GUI:
            pred = self._is_non_document_object

        root = self._determine_root_container(script)
        result = AXUtilities.find_all_clickables(root, pred=pred)
        result += AXUtilities.find_all_focusable_objects_with_click_ancestor(root, pred=pred)
        return result

    @dbus_service.command
    def previous_clickable(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the previous clickable."""

        tokens = ["STRUCTURAL NAVIGATOR: previous_clickable. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_clickables(script)
        result = self._get_object_in_direction(script, matches, False)
        self._present_object(script, result, messages.NO_MORE_CLICKABLES, notify_user=notify_user)
        return True

    @dbus_service.command
    def next_clickable(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Goes to the next clickable."""

        tokens = ["STRUCTURAL NAVIGATOR: next_clickable. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        matches = self._get_all_clickables(script)
        result = self._get_object_in_direction(script, matches, True)
        self._present_object(script, result, messages.NO_MORE_CLICKABLES, notify_user=notify_user)
        return True

    @dbus_service.command
    def list_clickables(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Displays a list of clickables."""

        tokens = ["STRUCTURAL NAVIGATOR: list_clickables. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        self._present_object_list(
            script,
            self._get_all_clickables(script),
            guilabels.SN_TITLE_CLICKABLE,
            [guilabels.SN_HEADER_CLICKABLE, guilabels.SN_HEADER_ROLE],
            lambda obj: [self._get_item_string(script, obj),
                         AXUtilities.get_localized_role_name(obj)],
        )
        return True

    ########################
    #                      #
    # Containers           #
    #                      #
    ########################

    def _get_current_container(self, script: default.Script) -> Atspi.Accessible | None:
        focus = focus_manager.get_manager().get_locus_of_focus()
        if container := AXObject.find_ancestor_inclusive(focus, AXUtilities.is_large_container):
            root = self._determine_root_container(script)
            if not AXObject.is_ancestor(container, root):
                return None
        return container

    @dbus_service.command
    def container_start(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the start of the current container."""

        tokens = ["STRUCTURAL NAVIGATOR: container_start. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        container = self._get_current_container(script)
        if container is None:
            if notify_user:
                script.present_message(messages.CONTAINER_NOT_IN_A)
            return True

        obj, offset = script.utilities.next_context(container, -1)
        self._present_line(script, obj, offset, notify_user)
        return True

    @dbus_service.command
    def container_end(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Moves to the end of the current container."""

        tokens = ["STRUCTURAL NAVIGATOR: container_end. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._last_input_event = event
        container = self._get_current_container(script)
        if container is None:
            if notify_user:
                script.present_message(messages.CONTAINER_NOT_IN_A)
            return True

        # Unlike going to the start of the container, when we move to the next edge
        # we pass beyond it on purpose. This makes us consistent with NVDA.
        obj, offset = script.utilities.last_context(container)
        next_object, next_offset = script.utilities.next_context(obj, offset)
        if next_object is None:
            next_object, next_offset = obj, offset

        self._present_line(script, next_object, next_offset, notify_user)
        return True

_navigator = StructuralNavigator()
def get_navigator() -> StructuralNavigator:
    """Returns the Structural Navigator"""

    return _navigator
