# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

# pylint: disable=wrong-import-position

"""Manager for text attribute presentation preferences."""

from __future__ import annotations


import enum

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk

from . import dbus_service
from . import debug
from . import gsettings_registry
from . import guilabels
from . import settings
from .ax_text import AXText, AXTextAttribute
from .preferences_grid_base import PreferencesGridBase


class PresentationMode(enum.IntEnum):
    """How a text attribute should be presented."""

    NONE = 0
    SPEAK = 1
    BRAILLE = 2
    SPEAK_AND_BRAILLE = 3


class TextAttributePreferencesGrid(PreferencesGridBase):
    """Preferences grid for text attribute presentation settings."""

    # pylint: disable=no-member, c-extension-no-member
    def __init__(self) -> None:
        super().__init__(guilabels.TEXT_ATTRIBUTES)
        self._initializing: bool = True
        self._listbox: Gtk.ListBox | None = None
        self._attributes: list[tuple[AXTextAttribute, PresentationMode]] = []
        self._drag_source_index: int | None = None
        self._focus_target_index: int | None = None

        self._build()
        self._initializing = False

    def _build(self) -> None:
        """Build the UI components."""

        row = 0

        info_listbox = self._create_info_listbox(guilabels.TEXT_ATTRIBUTES_INFO)
        self.attach(info_listbox, 0, row, 1, 1)
        row += 1

        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self._listbox.get_accessible().set_name(guilabels.TEXT_ATTRIBUTES)
        self._listbox.get_style_context().add_class("frame")
        scrolled_window = self._create_scrolled_window(self._listbox)
        self.attach(scrolled_window, 0, row, 1, 1)
        self.show_all()

    def _create_presentation_mode_model(self) -> Gtk.ListStore:
        """Create the model for presentation mode combo boxes."""

        model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        model.append([guilabels.TEXT_ATTRIBUTES_PRESENTATION_NONE, PresentationMode.NONE])
        model.append([guilabels.PRESENTATION_SPEAK, PresentationMode.SPEAK])
        model.append([guilabels.PRESENTATION_MARK_IN_BRAILLE, PresentationMode.BRAILLE])
        model.append([guilabels.PRESENTATION_SPEAK_AND_MARK, PresentationMode.SPEAK_AND_BRAILLE])
        return model

    # pylint: disable-next=too-many-locals,too-many-statements
    def _create_attribute_row(
        self,
        attribute: AXTextAttribute,
        presentation_mode: PresentationMode,
        index: int,
        include_top_separator: bool = True,
    ) -> Gtk.ListBoxRow:
        """Create a ListBoxRow for a text attribute."""

        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        row.get_accessible().set_name(attribute.get_localized_name())

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        if include_top_separator:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox.pack_start(separator, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)
        hbox.set_margin_top(12)
        hbox.set_margin_bottom(12)

        drag_area = Gtk.EventBox()
        drag_area_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        drag_icon = Gtk.Image.new_from_icon_name("list-drag-handle-symbolic", Gtk.IconSize.DND)
        drag_icon.set_opacity(0.5)
        drag_icon.set_margin_end(6)
        drag_area_hbox.pack_start(drag_icon, False, False, 0)

        name_label = Gtk.Label(label=attribute.get_localized_name(), xalign=0)
        name_label.set_hexpand(True)
        drag_area_hbox.pack_start(name_label, True, True, 0)

        drag_area.add(drag_area_hbox)
        hbox.pack_start(drag_area, True, True, 0)

        presentation_combo = Gtk.ComboBox()
        presentation_combo.set_model(self._create_presentation_mode_model())
        renderer = Gtk.CellRendererText()
        presentation_combo.pack_start(renderer, True)
        presentation_combo.add_attribute(renderer, "text", 0)
        presentation_combo.set_active(presentation_mode)
        presentation_combo.connect("changed", self._on_presentation_mode_changed, index)
        hbox.pack_start(presentation_combo, False, False, 0)

        menu_button = Gtk.MenuButton()
        menu_button.set_relief(Gtk.ReliefStyle.NONE)
        icon = Gtk.Image.new_from_icon_name("view-more-symbolic", Gtk.IconSize.DND)
        menu_button.set_image(icon)
        menu_button.get_accessible().set_name(guilabels.TEXT_ATTRIBUTES_REORDER)

        menu = Gtk.Menu()
        move_to_top = Gtk.MenuItem(label=guilabels.TEXT_ATTRIBUTES_MOVE_TO_TOP)
        move_to_top.connect("activate", self._on_menu_move, row, "top")
        menu.append(move_to_top)

        move_up = Gtk.MenuItem(label=guilabels.TEXT_ATTRIBUTES_MOVE_UP_ONE)
        move_up.connect("activate", self._on_menu_move, row, "up")
        menu.append(move_up)

        move_down = Gtk.MenuItem(label=guilabels.TEXT_ATTRIBUTES_MOVE_DOWN_ONE)
        move_down.connect("activate", self._on_menu_move, row, "down")
        menu.append(move_down)

        move_to_bottom = Gtk.MenuItem(label=guilabels.TEXT_ATTRIBUTES_MOVE_TO_BOTTOM)
        move_to_bottom.connect("activate", self._on_menu_move, row, "bottom")
        menu.append(move_to_bottom)

        menu.show_all()
        menu_button.set_popup(menu)
        hbox.pack_end(menu_button, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)
        row.add(vbox)

        row.attribute_index = index
        row.presentation_combo = presentation_combo

        target_entry = Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags.SAME_APP, 0)

        drag_area.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK, [target_entry], Gdk.DragAction.MOVE
        )
        drag_area.connect("drag-begin", self._on_drag_begin, row)
        drag_area.connect("drag-data-get", self._on_drag_data_get, row)
        drag_area.connect("drag-end", self._on_drag_end, row)

        row.drag_dest_set(Gtk.DestDefaults.ALL, [target_entry], Gdk.DragAction.MOVE)
        row.connect("drag-data-received", self._on_drag_data_received)

        return row

    def _on_presentation_mode_changed(self, combo: Gtk.ComboBox, index: int) -> None:
        """Handle presentation mode combo box changes."""

        if self._initializing:
            return

        tree_iter = combo.get_active_iter()
        if tree_iter:
            model = combo.get_model()
            mode = model[tree_iter][1]
            self._attributes[index] = (self._attributes[index][0], mode)
            self._has_unsaved_changes = True

    def _on_menu_move(self, _menu_item: Gtk.MenuItem, row: Gtk.ListBoxRow, direction: str) -> None:
        """Handle menu item activation for moving attributes."""

        index = row.attribute_index
        self._move_attribute(index, direction)

    def _move_attribute(self, index: int, direction: str) -> None:
        """Move an attribute in the list."""

        new_index = index

        if direction == "top":
            attribute = self._attributes.pop(index)
            self._attributes.insert(0, attribute)
            new_index = 0
        elif direction == "up" and index > 0:
            self._attributes[index], self._attributes[index - 1] = (
                self._attributes[index - 1],
                self._attributes[index],
            )
            new_index = index - 1
        elif direction == "down" and index < len(self._attributes) - 1:
            self._attributes[index], self._attributes[index + 1] = (
                self._attributes[index + 1],
                self._attributes[index],
            )
            new_index = index + 1
        elif direction == "bottom":
            attribute = self._attributes.pop(index)
            self._attributes.append(attribute)
            new_index = len(self._attributes) - 1

        self._focus_target_index = new_index
        self._has_unsaved_changes = True
        self.refresh()

    def _on_drag_begin(
        self, _widget: Gtk.EventBox, _drag_context: Gdk.DragContext, row: Gtk.ListBoxRow
    ) -> None:
        """Handle drag begin - store source index."""

        self._drag_source_index = row.attribute_index

    def _on_drag_data_get(
        self,
        _widget: Gtk.EventBox,
        _drag_context: Gdk.DragContext,
        data: Gtk.SelectionData,
        _info: int,
        _time: int,
        row: Gtk.ListBoxRow,
    ) -> None:
        """Handle drag data get - send source index."""

        data.set_text(str(row.attribute_index), -1)

    def _on_drag_data_received(
        self,
        row: Gtk.ListBoxRow,
        _drag_context: Gdk.DragContext,
        _x: int,
        _y: int,
        data: Gtk.SelectionData,
        _info: int,
        _time: int,
    ) -> None:
        """Handle drag data received - perform the move."""

        source_index_str = data.get_text()
        if source_index_str is None:
            return

        try:
            source_index = int(source_index_str)
        except ValueError:
            return

        target_index = row.attribute_index

        if source_index == target_index:
            return

        attribute = self._attributes.pop(source_index)
        self._attributes.insert(target_index, attribute)
        self._has_unsaved_changes = True
        self.refresh()

    def _on_drag_end(
        self, _widget: Gtk.EventBox, _drag_context: Gdk.DragContext, _row: Gtk.ListBoxRow
    ) -> None:
        """Handle drag end - clean up."""

        self._drag_source_index = None

    def reload(self) -> None:
        """Reload settings from the settings manager and update UI."""

        self._initializing = True

        spoken_attrs = settings.textAttributesToSpeak
        if not spoken_attrs:
            spoken_attrs = [
                attr.get_attribute_name()
                for attr in AXText.get_all_supported_text_attributes()
                if attr.should_present_by_default()
            ]

        brailled_attrs = settings.textAttributesToBraille
        if not brailled_attrs:
            brailled_attrs = []

        self._attributes = []
        spoken_set = set(spoken_attrs)
        brailled_set = set(brailled_attrs)

        for attr_name in spoken_attrs:
            attr = AXTextAttribute.from_string(attr_name)
            if attr is None:
                continue

            if attr_name in spoken_set and attr_name in brailled_set:
                mode = PresentationMode.SPEAK_AND_BRAILLE
            elif attr_name in spoken_set:
                mode = PresentationMode.SPEAK
            elif attr_name in brailled_set:
                mode = PresentationMode.BRAILLE
            else:
                mode = PresentationMode.NONE

            self._attributes.append((attr, mode))

        for attr in AXText.get_all_supported_text_attributes():
            attr_name = attr.get_attribute_name()
            if attr_name not in spoken_set:
                if attr_name in brailled_set:
                    mode = PresentationMode.BRAILLE
                else:
                    mode = PresentationMode.NONE
                self._attributes.append((attr, mode))

        self._initializing = False
        self.refresh()

    def refresh(self) -> None:
        """Update UI widgets from current state."""

        if self._listbox is None:
            return

        self._initializing = True

        for child in self._listbox.get_children():
            self._listbox.remove(child)

        for index, (attribute, mode) in enumerate(self._attributes):
            row = self._create_attribute_row(
                attribute, mode, index, include_top_separator=index > 0
            )
            self._listbox.add(row)

        self._listbox.show_all()
        self._initializing = False

        if self._focus_target_index is not None:
            target_row = self._listbox.get_row_at_index(self._focus_target_index)
            if target_row:
                target_row.grab_focus()
            self._focus_target_index = None

    def save_settings(self, profile: str = "", app_name: str = "") -> dict[str, list[str]]:
        """Save current settings and return dict of changed preferences."""

        spoken_attributes = []
        brailled_attributes = []

        for attribute, mode in self._attributes:
            key = attribute.get_attribute_name()
            if mode in (PresentationMode.SPEAK, PresentationMode.SPEAK_AND_BRAILLE):
                spoken_attributes.append(key)
            if mode in (PresentationMode.BRAILLE, PresentationMode.SPEAK_AND_BRAILLE):
                brailled_attributes.append(key)

        self._has_unsaved_changes = False

        result = {
            "textAttributesToSpeak": spoken_attributes,
            "textAttributesToBraille": brailled_attributes,
        }

        if profile:
            registry = gsettings_registry.get_registry()
            if registry.is_enabled():
                skip = not app_name and profile == "default"
                registry.save_schema_to_gsettings(
                    "text-attributes", result, profile, app_name, skip
                )

        return result

    # pylint: enable=no-member, c-extension-no-member


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.TextAttributes",
    name="text-attributes",
)
class TextAttributeManager:
    """Manager for text attribute presentation settings."""

    def __init__(self) -> None:
        msg = "TEXT ATTRIBUTE MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("TextAttributeManager", self)

    def create_preferences_grid(self) -> TextAttributePreferencesGrid:
        """Create and return a preferences grid for text attributes."""

        return TextAttributePreferencesGrid()

    @gsettings_registry.get_registry().gsetting(
        key="attributes-to-speak",
        schema="text-attributes",
        gtype="as",
        default=[],
        summary="Text attributes to speak",
        settings_key="textAttributesToSpeak",
    )
    @dbus_service.getter
    def get_attributes_to_speak(self) -> list[str]:
        """Returns the list of text attributes to speak."""

        return settings.textAttributesToSpeak

    @dbus_service.setter
    def set_attributes_to_speak(self, value: list[str]) -> bool:
        """Sets the list of text attributes to speak."""

        if self.get_attributes_to_speak() == value:
            return True

        msg = f"TEXT ATTRIBUTE MANAGER: Setting attributes to speak to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.textAttributesToSpeak = value
        return True

    @gsettings_registry.get_registry().gsetting(
        key="attributes-to-braille",
        schema="text-attributes",
        gtype="as",
        default=[],
        summary="Text attributes to mark in braille",
        settings_key="textAttributesToBraille",
    )
    @dbus_service.getter
    def get_attributes_to_braille(self) -> list[str]:
        """Returns the list of text attributes to mark in braille."""

        return settings.textAttributesToBraille

    @dbus_service.setter
    def set_attributes_to_braille(self, value: list[str]) -> bool:
        """Sets the list of text attributes to mark in braille."""

        if self.get_attributes_to_braille() == value:
            return True

        msg = f"TEXT ATTRIBUTE MANAGER: Setting attributes to braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.textAttributesToBraille = value
        return True


_manager = TextAttributeManager()


def get_manager() -> TextAttributeManager:
    """Return the singleton TextAttributeManager instance."""

    return _manager
