# Orca
#
# Copyright 2025 Igalia, S.L.
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
# pylint: disable=too-many-statements

"""Manager for script commands and keybindings."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2025 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING, Any, Callable

import gi
gi.require_version("Atk", "1.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from . import guilabels
from . import input_event
from . import input_event_manager
from . import keybindings
from . import keynames
from . import messages
from . import preferences_grid_base
from . import script_manager
from . import settings
from .ax_object import AXObject

if TYPE_CHECKING:
    from .scripts import default


class Command:  # pylint: disable=too-many-instance-attributes
    """Represents an Orca command with its handler and optional key binding.

    Commands have two independent activity states:

    enabled: User preference for whether this command should be active.
        - Set via user settings or toggle commands (e.g., "toggle caret navigation")
        - Persists across sessions
        - Example: User prefers caret navigation on

    suspended: Temporary system override that deactivates the command.
        - Set by Orca modes (e.g., focus mode suspends browse-mode commands)
        - Does NOT change the user's enabled preference
        - When suspension is lifted, command returns to its enabled state
        - Example: Focus mode suspends structural navigation; leaving focus
          mode automatically restores it

    A command is active (responds to key events) only when:
        enabled=True AND suspended=False AND keybinding is not None
    """

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        handler_name: str,
        handler: input_event.InputEventHandler,
        group_label: str,
        description: str = "",
        keybinding: keybindings.KeyBinding | None = None,
        learn_mode_enabled: bool = True,
        enabled: bool = True,
        suspended: bool = False
    ) -> None:
        """Initializes a command."""

        self._handler_name = handler_name
        self._handler = handler
        self._group_label = group_label
        self._description = description
        self._default_keybinding = keybinding  # The uncustomized default binding
        self._keybinding = keybinding  # The current binding (after customization)
        self._learn_mode_enabled = learn_mode_enabled
        self._enabled = enabled
        self._suspended = suspended

    def get_handler_name(self) -> str:
        """Returns the handler name."""

        return self._handler_name

    def get_handler(self) -> input_event.InputEventHandler:
        """Returns the input event handler."""

        return self._handler

    def get_group_label(self) -> str:
        """Returns the group label for display grouping."""

        return self._group_label

    def get_description(self) -> str:
        """Returns the command description."""

        return self._description

    def get_keybinding(self) -> keybindings.KeyBinding | None:
        """Returns the current key binding, or None if unbound."""

        return self._keybinding

    def get_default_keybinding(self) -> keybindings.KeyBinding | None:
        """Returns the default (uncustomized) key binding, or None if unbound by default."""

        return self._default_keybinding

    def get_learn_mode_enabled(self) -> bool:
        """Returns whether this command is enabled in learn mode."""

        return self._learn_mode_enabled

    def set_keybinding(self, keybinding: keybindings.KeyBinding | None) -> None:
        """Sets the current key binding."""

        self._keybinding = keybinding

    def set_default_keybinding(self, keybinding: keybindings.KeyBinding | None) -> None:
        """Sets the default (uncustomized) key binding."""

        self._default_keybinding = keybinding

    def set_group_label(self, group_label: str) -> None:
        """Sets the group label."""

        self._group_label = group_label

    def set_learn_mode_enabled(self, enabled: bool) -> None:
        """Sets whether this command is enabled in learn mode."""

        self._learn_mode_enabled = enabled

    def is_enabled(self) -> bool:
        """Returns True if the user has enabled this command."""

        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Sets whether the user has enabled this command."""

        self._enabled = enabled

    def is_suspended(self) -> bool:
        """Returns True if this command is temporarily suspended by the system."""

        return self._suspended

    def set_suspended(self, suspended: bool) -> None:
        """Sets whether this command is temporarily suspended by the system."""

        self._suspended = suspended

    def is_active(self) -> bool:
        """Returns True if this command should respond to key events."""

        return self._enabled and not self._suspended and self._keybinding is not None

    def execute(
        self,
        script: "default.Script",
        event: input_event.InputEvent | None = None
    ) -> bool:
        """Executes this command's handler function and returns True if handled."""

        return self._handler.function(script, event)

# pylint: disable-next=too-many-instance-attributes
class KeybindingsPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Grid widget for keybindings preferences."""

    def __init__(
        self,
        script: default.Script,
        title_change_callback: Callable[[str], None] | None = None
    ) -> None:
        """Initialize the keybindings preferences grid."""

        super().__init__(guilabels.COMMANDS)
        self._script = script
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._categories: dict[str, list[Command]] = {}
        self._current_category: str | None = None
        self._captured_key: tuple[str, int, int] = ("", 0, 0)
        self._pending_key_bindings: dict[str, str] = {}
        self._pending_already_bound_message_id: int | None = None
        self._keybinding_being_edited: str | None = None

        self.keyboard_layout_combo: Gtk.ComboBox | None = None
        self._orca_modifier_combo: Gtk.ComboBox | None = None
        self._combos_grid: Gtk.Grid | None = None

        self._build()
        self._initializing = False

    def _build(self) -> None:
        """Build the keybindings UI."""

        row = 0

        self._combos_grid = Gtk.Grid()
        self._combos_grid.set_column_spacing(24)
        self._combos_grid.set_row_spacing(12)

        keyboard_layout_model = Gtk.ListStore(str, int)
        keyboard_layout_model.append([guilabels.KEYBOARD_LAYOUT_DESKTOP,
                                      settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP])
        keyboard_layout_model.append([guilabels.KEYBOARD_LAYOUT_LAPTOP,
                                      settings.GENERAL_KEYBOARD_LAYOUT_LAPTOP])
        self.keyboard_layout_combo = self._create_labeled_combo_box(
            self._combos_grid, 0, guilabels.KEYBOARD_LAYOUT,
            keyboard_layout_model, self._on_keyboard_layout_changed)

        orca_model = Gtk.ListStore(str)
        orca_model.append(["Insert, KP_Insert"])
        orca_model.append(["KP_Insert"])
        orca_model.append(["Insert"])
        orca_model.append(["Caps_Lock, Shift_Lock"])
        self._orca_modifier_combo = self._create_labeled_combo_box(
            self._combos_grid, 1, guilabels.KEY_BINDINGS_SCREEN_READER_MODIFIER_KEY_S,
            orca_model, self._on_orca_modifier_changed)

        self.attach(self._combos_grid, 0, row, 1, 1)
        row += 1

        stack, _categories_listbox, _detail_listbox = self._create_stacked_preferences(
            on_category_activated=self._on_category_activated,
            on_detail_row_activated=self._on_keybinding_activated
        )
        self.attach(stack, 0, row, 1, 1)

        self._register_stack_disable_widgets(self._combos_grid)

    def reload(self) -> None:
        """Reload keybindings from the script."""

        self._script.register_commands()
        self._populate_keybindings()
        self._has_unsaved_changes = False
        self.refresh()

    def _populate_keybindings(self) -> None:
        """Build categories dictionary and populate the categories list."""

        if self._categories_listbox is None:
            return

        self._categories.clear()
        for child in self._categories_listbox.get_children():
            self._categories_listbox.remove(child)

        app_name = AXObject.get_name(self._script.app) if self._script.app else ""
        if app_name:
            self._categories[app_name] = []

        all_commands = get_manager().get_all_commands()

        for cmd in all_commands:
            group_label = cmd.get_group_label()
            if group_label not in self._categories:
                self._categories[group_label] = []
            self._categories[group_label].append(cmd)

        if app_name and app_name in self._categories and not self._categories[app_name]:
            del self._categories[app_name]

        self._categories_listbox.set_header_func(self._separator_header_func, None)

        # Custom sort: For app-specific, app name first then Default. For non-app, Default first.
        # After that, sort alphabetically.
        def sort_key(category_name):
            if app_name and category_name == app_name:
                return (0, category_name)
            if category_name == guilabels.KB_GROUP_DEFAULT:
                if app_name and app_name in self._categories:
                    return (1, category_name)
                return (0, category_name)
            return (2, category_name)

        sorted_categories = sorted(self._categories.keys(), key=sort_key)
        for category_name in sorted_categories:
            self._add_stack_category_row(
                self._categories_listbox,
                category_name,
                category=category_name
            )

        self._categories_listbox.show_all()

        self._pending_key_bindings = {}

    @staticmethod
    def _separator_header_func(row, before, _user_data):
        """Add separator between rows (standard GTK ListBox pattern)."""

        if before is not None:
            row.set_header(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

    def _on_category_activated(self, row: Gtk.ListBoxRow) -> None:
        """Handle category selection - navigate to detail page."""

        if not isinstance(row, preferences_grid_base.CategoryListBoxRow):
            return

        category_name = row.category
        if not category_name or category_name not in self._categories:
            return

        self._current_category = category_name
        self._populate_category_detail(category_name)
        self._show_stack_detail()

    def on_becoming_visible(self) -> None:
        """Reset to the categories view when this grid becomes visible."""

        self._show_stack_categories()
        if self._categories_listbox:
            self._categories_listbox.grab_focus()

    def _show_stack_categories(self) -> None:
        """Switch to categories view and update title to main page."""

        super()._show_stack_categories()
        if self._title_change_callback:
            self._title_change_callback(guilabels.COMMANDS)

    def _show_stack_detail(self) -> None:
        """Switch to detail view and update title to category name."""

        super()._show_stack_detail()
        if self._title_change_callback and self._current_category:
            self._title_change_callback(self._current_category)

    def _populate_category_detail(self, category_name: str) -> None:
        """Populate the detail page with keybindings for the given category."""

        if self._detail_listbox is None or category_name not in self._categories:
            return

        for child in self._detail_listbox.get_children():
            self._detail_listbox.remove(child)

        commands = self._categories[category_name]
        for i, cmd in enumerate(commands):
            row = preferences_grid_base.CommandListBoxRow()
            row.set_activatable(True)

            outer_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

            if i > 0:
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                outer_vbox.pack_start(separator, False, False, 0)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vbox.set_margin_start(12)
            vbox.set_margin_end(12)
            vbox.set_margin_top(12)
            vbox.set_margin_bottom(12)

            description = cmd.get_description() if cmd.get_description() else cmd.get_handler_name()
            desc_label = Gtk.Label(label=description, xalign=0)
            desc_label.set_line_wrap(True)
            desc_label.set_hexpand(True)
            vbox.pack_start(desc_label, False, False, 0)

            binding = cmd.get_keybinding()
            binding_text = self._format_keybinding_text(binding) or ""

            binding_label = Gtk.Label(label=binding_text, xalign=0)
            binding_label.set_opacity(0.5)
            vbox.pack_start(binding_label, False, False, 0)

            outer_vbox.pack_start(vbox, False, False, 0)
            row.add(outer_vbox)

            row.command = cmd
            row.vbox = vbox
            row.binding_label = binding_label
            row.show_all()
            self._detail_listbox.add(row)

        self._detail_listbox.show_all()

    def _on_keybinding_activated(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Handle keybinding row activation - start inline editing."""

        if not isinstance(row, preferences_grid_base.CommandListBoxRow):
            return

        command = row.command
        if not command:
            return

        vbox = row.vbox
        binding_label = row.binding_label
        if not vbox or not binding_label:
            return

        self._start_inline_editing(row, command, vbox, binding_label)


    def _start_inline_editing(
        self,
        row: Gtk.ListBoxRow,
        command: Command,
        vbox: Gtk.Box,
        binding_label: Gtk.Label
    ) -> None:
        """Start inline editing of a keybinding."""

        vbox.remove(binding_label)

        capture_entry = Gtk.Entry()
        capture_entry.set_alignment(0.0)
        capture_entry.get_style_context().add_class("dim-label")

        binding = command.get_keybinding()
        if binding and binding.keysymstring:
            current_text = self._format_keybinding_text(binding)
            capture_entry.set_text(current_text or "")
        else:
            capture_entry.set_text("")

        vbox.pack_start(capture_entry, False, False, 0)
        capture_entry.show()
        capture_entry.grab_focus()

        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = command.get_handler_name()

        def on_key_press(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
            if event.keyval == Gdk.KEY_Escape:
                self._finish_inline_editing(row, command, vbox, capture_entry, binding_label, canceled=True)
                return True

            if event.keyval == Gdk.KEY_Return:
                # Check for duplicates when confirming
                if self._captured_key[0]:
                    key_name, modifiers, click_count = self._captured_key
                    handler_name = command.get_handler_name()
                    description_dup = self._find_duplicate_binding(key_name, modifiers, click_count, handler_name)
                    if description_dup:
                        script = script_manager.get_manager().get_active_script()
                        def present_duplicate_error():
                            script.present_message(messages.KB_ALREADY_BOUND % description_dup)
                            return False
                        GLib.idle_add(present_duplicate_error)
                        capture_entry.set_text("")
                        self._captured_key = ("", 0, 0)
                        return True

                self._finish_inline_editing(row, command, vbox, capture_entry, binding_label, canceled=False)
                return True

            key_processed = self._process_key_captured(event)
            if not key_processed or not self._captured_key[0]:
                return True

            key_name, modifiers, click_count = self._captured_key
            script = script_manager.get_manager().get_active_script()

            is_orca_modifier = modifiers & keybindings.ORCA_MODIFIER_MASK
            if key_name in ["Delete", "BackSpace"] and not is_orca_modifier:
                capture_entry.set_text("")
                self._captured_key = ("", 0, 0)

                def present_delete_message():
                    script.present_message(messages.KB_DELETED)
                    return False

                GLib.idle_add(present_delete_message)
                return True

            modifier_names = keybindings.get_modifier_names(modifiers)
            click_count_string = keynames.get_click_count_string(click_count)
            if click_count_string:
                click_count_string = f" ({click_count_string})"
            new_string = modifier_names + key_name + click_count_string
            capture_entry.set_text(new_string)

            def present_message_after_keypress():
                script.present_message(messages.KB_CAPTURED % new_string)
                return False

            GLib.idle_add(present_message_after_keypress)

            return True

        capture_entry.connect("key-press-event", on_key_press)
        row.capture_entry = capture_entry

        script = script_manager.get_manager().get_active_script()
        assert script
        script.present_message(messages.KB_ENTER_NEW_KEY)
        self._script.remove_key_grabs()
        input_event_manager.get_manager().unmap_all_modifiers()

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments, too-many-locals
    def _finish_inline_editing(
        self,
        row: Gtk.ListBoxRow,
        command: Command,
        vbox: Gtk.Box,
        capture_entry: Gtk.Entry,
        binding_label: Gtk.Label,
        canceled: bool
    ) -> None:
        """Finish inline editing of a keybinding."""

        self._script.refresh_key_grabs()

        if not canceled:
            captured_text = capture_entry.get_text().strip()
            script = script_manager.get_manager().get_active_script()
            if not captured_text:
                command.set_keybinding(None)
                self._has_unsaved_changes = True

                def present_delete_confirmation():
                    script.present_message(messages.KB_DELETED_CONFIRMATION)
                    return False

                GLib.idle_add(present_delete_confirmation)
            else:
                key_name, modifiers, click_count = self._captured_key
                if key_name:
                    new_kb = keybindings.KeyBinding(
                        key_name,
                        modifiers,
                        command.get_handler(),
                        click_count
                    )
                    command.set_keybinding(new_kb)
                    self._has_unsaved_changes = True

                    def present_confirmation():
                        msg = messages.KB_CAPTURED_CONFIRMATION % captured_text
                        script.present_message(msg)
                        return False

                    GLib.idle_add(present_confirmation)

            binding = command.get_keybinding()
            binding_text = self._format_keybinding_text(binding) or ""
            binding_label.set_text(binding_text)

        vbox.remove(capture_entry)
        vbox.pack_start(binding_label, False, False, 0)
        binding_label.show()
        row.grab_focus()

        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = None

    def _find_duplicate_binding(
        self,
        key_name: str,
        modifiers: int,
        click_count: int,
        exclude_handler: str | None = None
    ) -> str | None:
        """Find if a keybinding is already used and return its description."""

        for category_commands in self._categories.values():
            for cmd in category_commands:
                if exclude_handler and cmd.get_handler_name() == exclude_handler:
                    continue

                binding = cmd.get_keybinding()
                if not binding or not binding.keysymstring:
                    continue

                if (binding.keysymstring == key_name and
                    binding.modifiers == modifiers and
                    binding.click_count == click_count):
                    return cmd.get_description() or cmd.get_handler_name()

        return None


    def _process_key_captured(self, event: Gdk.EventKey) -> bool:
        """Process a captured key press event."""

        keycode = event.hardware_keycode
        keymap = Gdk.Keymap.get_default() # pylint: disable=no-value-for-parameter
        entries_for_keycode = keymap.get_entries_for_keycode(keycode)
        entries = entries_for_keycode[-1]
        event_string = Gdk.keyval_name(entries[0])
        event_state = event.state

        orca_mods = settings.orcaModifierKeys
        if event_string in orca_mods:
            self._captured_key = ("", keybindings.ORCA_MODIFIER_MASK, 0)
            return False

        modifier_keys = ["Alt_L", "Alt_R", "Control_L", "Control_R",
                        "Shift_L", "Shift_R", "Meta_L", "Meta_R",
                        "Num_Lock", "Caps_Lock", "Shift_Lock"]
        if event_string in modifier_keys:
            return False

        event_state = event_state & Gtk.accelerator_get_default_mod_mask()  # pylint: disable=no-value-for-parameter

        # Return and Escape are used to confirm/cancel editing, not as captured keys
        # Return False to let GTK process them normally
        if event_string in ["Return", "Escape"]:
            return False

        if not self._captured_key[0]:
            # Preserve Orca modifier if it was already captured.
            if self._captured_key[1] & keybindings.ORCA_MODIFIER_MASK:
                event_state |= keybindings.ORCA_MODIFIER_MASK
            self._captured_key = (event_string, event_state, 1)
            return True

        string, modifiers, click_count = self._captured_key

        # Preserve Orca modifier from previous key if present before comparing
        if modifiers & keybindings.ORCA_MODIFIER_MASK:
            event_state |= keybindings.ORCA_MODIFIER_MASK

        if string != event_string or modifiers != event_state:
            self._captured_key = (event_string, event_state, 1)
            return True

        # Same key pressed again - increment click count
        self._captured_key = (event_string, event_state, click_count + 1)
        return True

    # pylint: disable-next=too-many-locals
    def _show_key_capture_dialog(self, command: Command) -> None:
        """Show dialog to capture a new key binding for the given command."""

        description = command.get_description() or command.get_handler_name()
        handler_name = command.get_handler_name()

        dialog = Gtk.Dialog(transient_for=self.get_toplevel())
        dialog.set_modal(True)
        dialog.set_title(guilabels.KB_HEADER_KEY_BINDING)
        dialog.set_default_size(500, -1)

        content = dialog.get_content_area()
        content.set_spacing(18)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)

        desc_label = Gtk.Label(label=description)
        desc_label.set_line_wrap(True)
        desc_label.set_xalign(0)
        content.pack_start(desc_label, False, False, 0)

        entry = Gtk.Entry()
        entry.set_editable(False)
        entry.set_can_focus(True)
        entry.set_width_chars(40)

        binding = command.get_keybinding()
        if binding and binding.keysymstring:
            current_text = self._format_keybinding_text(binding)
            entry.set_text(current_text or "")
        else:
            entry.set_text("")

        content.pack_start(entry, False, False, 0)

        instructions = Gtk.Label(label=messages.KB_ENTER_NEW_KEY)
        instructions.set_line_wrap(True)
        instructions.set_xalign(0)
        instructions.get_style_context().add_class("dim-label")
        content.pack_start(instructions, False, False, 0)

        dialog.add_button(guilabels.BTN_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(guilabels.BTN_OK, Gtk.ResponseType.OK)

        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = handler_name

        script = script_manager.get_manager().get_active_script()
        assert script

        # pylint: disable=too-many-return-statements
        def on_key_press(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
            if event.keyval == Gdk.KEY_Escape:
                dialog.response(Gtk.ResponseType.CANCEL)
                return True

            if event.keyval in [Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab]:
                return False

            key_processed = self._process_key_captured(event)

            if not key_processed:
                return False

            if not self._captured_key[0]:
                return False

            key_name, modifiers, click_count = self._captured_key

            if not key_name:
                return False

            is_orca_modifier = modifiers & keybindings.ORCA_MODIFIER_MASK
            if key_name in ["Delete", "BackSpace"] and not is_orca_modifier:
                entry.set_text("")
                script.present_message(messages.KB_DELETED)
                self._captured_key = ("", 0, 0)
                return True

            modifier_names = keybindings.get_modifier_names(modifiers)
            click_count_string = keynames.get_click_count_string(click_count)
            if click_count_string:
                click_count_string = f" ({click_count_string})"
            new_string = modifier_names + key_name + click_count_string

            entry.set_text(new_string)

            description_dup = self._find_duplicate_binding(
                key_name, modifiers, click_count, handler_name)
            if description_dup:
                msg = messages.KB_ALREADY_BOUND % description_dup
            else:
                msg = messages.KB_CAPTURED % new_string
            script.present_message(msg)

            return True

        entry.connect("key-press-event", on_key_press)

        script.present_message(messages.KB_ENTER_NEW_KEY)

        dialog.show_all()
        entry.grab_focus()
        entry.grab_add()

        while Gtk.events_pending():
            Gtk.main_iteration()

        self._script.remove_key_grabs()
        input_event_manager.get_manager().unmap_all_modifiers()

        response = dialog.run()

        entry.grab_remove()
        self._script.refresh_key_grabs()

        if response == Gtk.ResponseType.OK:
            entry_text = entry.get_text().strip()
            if not entry_text:
                command.set_keybinding(None)
            else:
                key_name, modifiers, click_count = self._captured_key
                if key_name:
                    new_kb = keybindings.KeyBinding(
                        key_name,
                        modifiers,
                        command.get_handler(),
                        click_count
                    )
                    command.set_keybinding(new_kb)

            self._has_unsaved_changes = True
            if self._current_category:
                self._populate_category_detail(self._current_category)

        dialog.destroy()
        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = None

    def save_settings(self) -> dict[str, list[list[Any]] | int | list[str]]:
        """Save settings and return a dictionary of the current values for those settings."""

        result: dict[str, list[list[Any]] | int | list[str]] = {}

        if self.keyboard_layout_combo is not None:
            tree_iter = self.keyboard_layout_combo.get_active_iter()
            if tree_iter is not None:
                model = self.keyboard_layout_combo.get_model()
                layout_value = model.get_value(tree_iter, 1)
                result["keyboardLayout"] = layout_value

        if self._orca_modifier_combo is not None:
            tree_iter = self._orca_modifier_combo.get_active_iter()
            if tree_iter is not None:
                model = self._orca_modifier_combo.get_model()
                orca_modifier = model.get_value(tree_iter, 0)
                result["orcaModifierKeys"] = orca_modifier.split(", ")

        for category_commands in self._categories.values():
            for cmd in category_commands:
                handler_name = cmd.get_handler_name()
                current_kb = cmd.get_keybinding()
                default_kb = cmd.get_default_keybinding()

                current_text = self._format_keybinding_text(current_kb)
                default_text = self._format_keybinding_text(default_kb)

                if current_text != default_text:
                    if current_kb and current_kb.keysymstring:
                        binding_data = [
                            current_kb.keysymstring,
                            str(current_kb.modifier_mask),
                            str(current_kb.modifiers),
                            str(current_kb.click_count)
                        ]
                        result[handler_name] = [binding_data]
                    elif default_kb and default_kb.keysymstring:
                        # Was unbound - save empty list to indicate unbinding
                        result[handler_name] = []

        self._has_unsaved_changes = False
        return result

    def refresh(self) -> None:
        """Refresh the keyboard layout and orca modifier displays."""

        self._initializing = True

        if self.keyboard_layout_combo is not None:
            current_layout = settings.keyboardLayout
            model = self.keyboard_layout_combo.get_model()
            if model:
                for i, row in enumerate(model):
                    if row[1] == current_layout:
                        self.keyboard_layout_combo.set_active(i)
                        break

        if self._orca_modifier_combo is not None:
            orca_modifier_keys = settings.orcaModifierKeys
            key_string = ", ".join(orca_modifier_keys)
            orca_model = self._orca_modifier_combo.get_model()
            if orca_model:
                orca_iter = orca_model.get_iter_first()
                for i in range(len(orca_model)):
                    if orca_model.get_value(orca_iter, 0) == key_string:
                        self._orca_modifier_combo.set_active(i)
                        break
                    orca_iter = orca_model.iter_next(orca_iter)

        self._initializing = False

    def _on_keyboard_layout_changed(self, combo: Gtk.ComboBox) -> None:
        """Handle keyboard layout changes."""

        if self._initializing:
            return

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            layout_value = model.get_value(tree_iter, 1)

            settings.keyboardLayout = layout_value

            if self._orca_modifier_combo is not None:
                if layout_value == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
                    self._orca_modifier_combo.set_active(0)
                    settings.orcaModifierKeys = settings.DESKTOP_MODIFIER_KEYS
                else:
                    self._orca_modifier_combo.set_active(3)
                    settings.orcaModifierKeys = settings.LAPTOP_MODIFIER_KEYS

        self._script.register_commands()
        self._populate_keybindings()
        self._has_unsaved_changes = True

    def _on_orca_modifier_changed(self, combo: Gtk.ComboBox) -> None:
        """Handle orca modifier combo box changes."""

        if self._initializing:
            return

        tree_iter = combo.get_active_iter()
        if tree_iter is None:
            return

        model = combo.get_model()
        orca_modifier = model.get_value(tree_iter, 0)
        settings.orcaModifierKeys = orca_modifier.split(", ")
        self._has_unsaved_changes = True

    def _format_keybinding_text(self, kb: keybindings.KeyBinding | None) -> str | None:
        """Format a keybinding as text for display."""

        if not kb or not kb.keysymstring:
            return None

        click_count_str = keynames.get_click_count_string(kb.click_count)
        if click_count_str:
            click_count_str = f" ({click_count_str})"

        return keybindings.get_modifier_names(kb.modifiers) + kb.keysymstring + click_count_str



class CommandManager:
    """Singleton manager for coordinating commands between scripts and UI."""

    def __init__(self) -> None:
        """Initializes the command manager."""

        self._commands_by_name: dict[str, Command] = {}

    def add_command(self, command: Command) -> None:
        """Adds a command to the registry."""

        self._commands_by_name[command.get_handler_name()] = command

    def get_command(self, handler_name: str) -> Command | None:
        """Returns the command with the specified handler name, or None."""

        return self._commands_by_name.get(handler_name)

    def get_all_commands(self) -> tuple[Command, ...]:
        """Returns all registered commands."""

        return tuple(self._commands_by_name.values())

    def get_commands_by_group_label(self, group_label: str) -> tuple[Command, ...]:
        """Returns all commands with the specified group label."""

        return tuple(
            cmd for cmd in self._commands_by_name.values()
            if cmd.get_group_label() == group_label
        )

    def clear_commands(self) -> None:
        """Removes all commands from the registry."""

        self._commands_by_name.clear()

    def set_default_bindings_from_module(
        self,
        handlers: dict[str, input_event.InputEventHandler],
        module_bindings: keybindings.KeyBindings,
        skip_handlers: frozenset[str]
    ) -> None:
        """Sets default keybindings on Commands from module bindings before user customization."""

        for kb in module_bindings.key_bindings:
            for name, handler in handlers.items():
                if name in skip_handlers:
                    continue
                if handler.function == kb.handler.function:
                    if cmd := self.get_command(name):
                        if cmd.get_default_keybinding() is None:
                            cmd.set_default_keybinding(kb)
                            cmd.set_keybinding(kb)
                    break

    def clear_deleted_bindings(
        self,
        handlers: dict[str, input_event.InputEventHandler],
        profile_keybindings: dict[str, Any],
        skip_handlers: frozenset[str]
    ) -> None:
        """Clears keybindings for handlers explicitly unbound in profile settings."""

        for name in handlers:
            if name in skip_handlers:
                continue
            if name in profile_keybindings:
                if profile_keybindings[name] == []:
                    if cmd := self.get_command(name):
                        cmd.set_keybinding(None)

    def apply_customized_bindings(
        self,
        handlers: dict[str, input_event.InputEventHandler],
        customized: keybindings.KeyBindings,
        group_label: str,
        skip_handlers: frozenset[str],
        update_group_label: bool = True
    ) -> None:
        """Updates or adds Commands from customized keybindings."""

        for kb in customized.key_bindings:
            for name, handler in handlers.items():
                if name in skip_handlers:
                    continue
                if handler.function == kb.handler.function:
                    if cmd := self.get_command(name):
                        cmd.set_keybinding(kb)
                        if group_label and update_group_label:
                            cmd.set_group_label(group_label)
                    else:
                        self.add_command(Command(
                            name, handler, group_label, handler.description,
                            kb, handler.learn_mode_enabled))
                    break

    def get_command_for_event(
        self,
        event: input_event.KeyboardEvent,
        active_only: bool = True
    ) -> Command | None:
        """Returns the command matching the keyboard event, or None."""

        click_count = event.get_click_count()
        for cmd in self._commands_by_name.values():
            if active_only and not cmd.is_active():
                continue
            kb = cmd.get_keybinding()
            if kb is None:
                continue
            if not kb.matches(event.id, event.hw_code, event.modifiers):
                continue
            if kb.modifiers == event.modifiers and kb.click_count == click_count:
                return cmd
        return None

    def set_group_enabled(self, group_label: str, enabled: bool) -> None:
        """Sets the enabled state for all commands in a group."""

        for cmd in self.get_commands_by_group_label(group_label):
            cmd.set_enabled(enabled)

    def set_group_suspended(self, group_label: str, suspended: bool) -> None:
        """Sets the suspended state for all commands in a group."""

        for cmd in self.get_commands_by_group_label(group_label):
            cmd.set_suspended(suspended)

    def add_grabs_for_command(self, handler_name: str) -> None:
        """Adds key grabs for the specified command."""

        cmd = self.get_command(handler_name)
        if cmd is None or (kb := cmd.get_keybinding()) is None:
            return
        kb.add_grabs()

    def remove_grabs_for_command(self, handler_name: str) -> None:
        """Removes key grabs for the specified command."""

        cmd = self.get_command(handler_name)
        if cmd is None or (kb := cmd.get_keybinding()) is None:
            return
        kb.remove_grabs()

    def add_grabs_for_group(self, group_label: str) -> None:
        """Adds key grabs for all active commands in a group."""

        for cmd in self.get_commands_by_group_label(group_label):
            if cmd.is_active() and (kb := cmd.get_keybinding()) is not None:
                kb.add_grabs()

    def remove_grabs_for_group(self, group_label: str) -> None:
        """Removes key grabs for all commands in a group."""

        for cmd in self.get_commands_by_group_label(group_label):
            kb = cmd.get_keybinding()
            if kb is not None:
                kb.remove_grabs()

    def refresh_grabs_for_group(self, group_label: str) -> None:
        """Removes existing grabs and adds new grabs for active commands in a group."""

        self.remove_grabs_for_group(group_label)
        self.add_grabs_for_group(group_label)

    def create_preferences_grid(
        self,
        script: default.Script,
        title_change_callback: Callable[[str], None] | None = None
    ) -> KeybindingsPreferencesGrid:
        """Returns the GtkGrid containing the keybindings preferences UI."""

        return KeybindingsPreferencesGrid(script, title_change_callback)


_manager: CommandManager = CommandManager()

def get_manager() -> CommandManager:
    """Returns the CommandManager singleton."""
    return _manager
