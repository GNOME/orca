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
# pylint: disable=too-many-lines

"""Manager for script commands and keybindings."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2025 Igalia, S.L."
__license__   = "LGPL"

import time
from typing import TYPE_CHECKING, Any, Callable

import gi
gi.require_version("Atk", "1.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from . import cmdnames
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event
from . import input_event_manager
from . import keybindings
from . import keynames
from . import messages
from . import orca_modifier_manager
from . import preferences_grid_base
from . import script_manager
from . import settings
from . import settings_manager
from .ax_object import AXObject

if TYPE_CHECKING:
    from .scripts import default


class Command:
    """Base class for Orca commands.

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
    """

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        name: str,
        function: Callable[..., bool],
        group_label: str,
        description: str = "",
        enabled: bool = True,
        suspended: bool = False
    ) -> None:
        """Initializes a command."""

        self._name = name
        self._function = function
        self._group_label = group_label
        self._description = description
        self._enabled = enabled
        self._suspended = suspended

    def __str__(self) -> str:
        """Returns a string representation of the command."""

        parts = [f"Command({self._name})"]
        if self._suspended:
            parts.append("SUSPENDED")
        return " ".join(parts)

    def get_name(self) -> str:
        """Returns the command name."""

        return self._name

    def get_function(self) -> Callable[..., bool]:
        """Returns the command function."""

        return self._function

    def get_group_label(self) -> str:
        """Returns the group label for display grouping."""

        return self._group_label

    def get_description(self) -> str:
        """Returns the command description."""

        return self._description

    def set_group_label(self, group_label: str) -> None:
        """Sets the group label."""

        self._group_label = group_label

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

    def execute(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None
    ) -> bool:
        """Executes this command's function and returns True if handled."""

        return self._function(script, event)


class KeyboardCommand(Command):  # pylint: disable=too-many-instance-attributes
    """A command that can be bound to keyboard keys."""

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        name: str,
        function: Callable[..., bool],
        group_label: str,
        description: str = "",
        desktop_keybinding: keybindings.KeyBinding | None = None,
        laptop_keybinding: keybindings.KeyBinding | None = None,
        enabled: bool = True,
        suspended: bool = False,
        is_group_toggle: bool = False
    ) -> None:
        """Initializes a keyboard command."""

        super().__init__(name, function, group_label, description, enabled, suspended)

        # The default bindings.
        self._desktop_keybinding = desktop_keybinding
        self._laptop_keybinding = laptop_keybinding

        # The actual binding, taking into account user overrides.
        self._keybinding: keybindings.KeyBinding | None = None
        self._is_group_toggle = is_group_toggle

    def __str__(self) -> str:
        """Returns a string representation of the command."""

        parts = [f"KeyboardCommand({self._name})"]
        if self._keybinding:
            parts.append(str(self._keybinding))
        else:
            parts.append("UNBOUND")
        if self._suspended:
            parts.append("SUSPENDED")
        return " ".join(parts)

    def get_keybinding(self) -> keybindings.KeyBinding | None:
        """Returns the current key binding, or None if unbound."""

        return self._keybinding

    def get_default_keybinding(
        self,
        is_desktop: bool | None = None
    ) -> keybindings.KeyBinding | None:
        """Returns the default key binding for the specified or current layout."""

        if is_desktop is None:
            is_desktop = get_manager().is_desktop_layout()
        return self._desktop_keybinding if is_desktop else self._laptop_keybinding

    def has_default_keybinding(self) -> bool:
        """Returns True if this command has a default keybinding for either layout."""

        return self._desktop_keybinding is not None or self._laptop_keybinding is not None

    def set_keybinding(self, keybinding: keybindings.KeyBinding | None) -> None:
        """Sets the current key binding."""

        self._keybinding = keybinding

    def is_group_toggle(self) -> bool:
        """Returns True if this command toggles its group's enabled state."""

        return self._is_group_toggle

    def is_active(self) -> bool:
        """Returns True if this command should respond to key events."""

        return self._enabled and not self._suspended and self._keybinding is not None


class BrailleCommand(Command):
    """A command that can only be triggered by braille hardware."""

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        name: str,
        function: Callable[..., bool],
        group_label: str,
        description: str = "",
        enabled: bool = True,
        suspended: bool = False,
        braille_bindings: tuple[int, ...] = (),
        executes_in_learn_mode: bool = False
    ) -> None:
        """Initializes a braille command."""

        super().__init__(name, function, group_label, description, enabled, suspended)
        self._braille_bindings = braille_bindings
        self._executes_in_learn_mode = executes_in_learn_mode

    def __str__(self) -> str:
        """Returns a string representation of the command."""

        parts = [f"BrailleCommand({self._name})"]
        if self._braille_bindings:
            parts.append(f"braille={self._braille_bindings}")
        if self._suspended:
            parts.append("SUSPENDED")
        return " ".join(parts)

    def get_braille_bindings(self) -> tuple[int, ...]:
        """Returns the braille bindings (BrlAPI key codes)."""

        return self._braille_bindings

    def executes_in_learn_mode(self) -> bool:
        """Returns True if this command should execute in learn mode (e.g., pan commands)."""

        return self._executes_in_learn_mode


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

        self._categories: dict[str, list[KeyboardCommand]] = {}
        self._current_category: str | None = None
        self._captured_key: tuple[str, int, int] = ("", 0, 0)
        self._pending_key_bindings: dict[str, str] = {}
        self._pending_already_bound_message_id: int | None = None
        # Store modified keybindings separately so they survive apply_user_overrides()
        self._modified_keybindings: dict[str, keybindings.KeyBinding | None] = {}
        self._keybinding_being_edited: str | None = None
        self._saved_commands: dict[str, KeyboardCommand] = {}

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

        get_manager().apply_user_overrides()
        self._populate_keybindings()
        self._modified_keybindings.clear()
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

        all_commands = get_manager().get_all_keyboard_commands()

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

            description = cmd.get_description() if cmd.get_description() else cmd.get_name()
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
        command: KeyboardCommand,
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
        self._keybinding_being_edited = command.get_name()

        def on_key_press(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
            if event.keyval == Gdk.KEY_Escape:
                self._finish_inline_editing(
                    row, command, vbox, capture_entry, binding_label, canceled=True)
                return True

            if event.keyval == Gdk.KEY_Return:
                if self._captured_key[0]:
                    key_name, modifiers, click_count = self._captured_key
                    handler_name = command.get_name()
                    description_dup = self._find_duplicate_binding(
                        key_name, modifiers, click_count, handler_name)
                    if description_dup:
                        script = script_manager.get_manager().get_active_script()
                        def present_duplicate_error():
                            script.present_message(messages.KB_ALREADY_BOUND % description_dup)
                            return False
                        GLib.idle_add(present_duplicate_error)
                        capture_entry.set_text("")
                        self._captured_key = ("", 0, 0)
                        return True

                self._finish_inline_editing(
                    row, command, vbox, capture_entry, binding_label, canceled=False)
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
        self._saved_commands = get_manager().get_keyboard_commands()
        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        get_manager().set_active_commands({}, "Capturing keys")
        input_event_manager.get_manager().unmap_all_modifiers()

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments, too-many-locals
    def _finish_inline_editing(
        self,
        row: Gtk.ListBoxRow,
        command: KeyboardCommand,
        vbox: Gtk.Box,
        capture_entry: Gtk.Entry,
        binding_label: Gtk.Label,
        canceled: bool
    ) -> None:
        """Finish inline editing of a keybinding."""

        get_manager().set_active_commands(self._saved_commands, "Done capturing keys")
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

        if not canceled:
            captured_text = capture_entry.get_text().strip()
            script = script_manager.get_manager().get_active_script()
            handler_name = command.get_name()
            if not captured_text:
                command.set_keybinding(None)
                self._modified_keybindings[handler_name] = None
                self._has_unsaved_changes = True

                def present_delete_confirmation():
                    script.present_message(messages.KB_DELETED_CONFIRMATION)
                    return False

                GLib.idle_add(present_delete_confirmation)
            else:
                key_name, modifiers, click_count = self._captured_key
                if key_name:
                    new_kb = keybindings.KeyBinding(key_name, modifiers, click_count)
                    command.set_keybinding(new_kb)
                    self._modified_keybindings[handler_name] = new_kb
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
                if exclude_handler and cmd.get_name() == exclude_handler:
                    continue

                binding = cmd.get_keybinding()
                if not binding or not binding.keysymstring:
                    continue

                if (binding.keysymstring == key_name and
                    binding.modifiers == modifiers and
                    binding.click_count == click_count):
                    return cmd.get_description() or cmd.get_name()

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
    def _show_key_capture_dialog(self, command: KeyboardCommand) -> None:
        """Show dialog to capture a new key binding for the given command."""

        description = command.get_description() or command.get_name()
        handler_name = command.get_name()

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

        while Gtk.events_pending(): # pylint: disable=no-value-for-parameter
            Gtk.main_iteration()

        saved_commands = get_manager().get_keyboard_commands()
        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        get_manager().set_active_commands({}, "Capturing keys")
        input_event_manager.get_manager().unmap_all_modifiers()

        response = dialog.run()

        entry.grab_remove()
        get_manager().set_active_commands(saved_commands, "Done capturing keys")
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

        if response == Gtk.ResponseType.OK:
            entry_text = entry.get_text().strip()
            handler_name = command.get_name()
            if not entry_text:
                command.set_keybinding(None)
                self._modified_keybindings[handler_name] = None
            else:
                key_name, modifiers, click_count = self._captured_key
                if key_name:
                    new_kb = keybindings.KeyBinding(key_name, modifiers, click_count)
                    command.set_keybinding(new_kb)
                    self._modified_keybindings[handler_name] = new_kb

            self._has_unsaved_changes = True
            if self._current_category:
                self._populate_category_detail(self._current_category)

        dialog.destroy()
        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = None

    def save_settings(
        self
    ) -> tuple[dict[str, int | list[str]], dict[str, list[list[Any]]]]:
        """Save settings and return (general_settings, keybindings) tuple."""

        general: dict[str, int | list[str]] = {}
        keybindings: dict[str, list[list[Any]]] = {}

        general["keyboardLayout"] = get_manager().get_keyboard_layout_value()

        if self._orca_modifier_combo is not None:
            tree_iter = self._orca_modifier_combo.get_active_iter()
            if tree_iter is not None:
                model = self._orca_modifier_combo.get_model()
                orca_modifier = model.get_value(tree_iter, 0)
                general["orcaModifierKeys"] = orca_modifier.split(", ")

        for category_commands in self._categories.values():
            for cmd in category_commands:
                handler_name = cmd.get_name()
                if handler_name in self._modified_keybindings:
                    current_kb = self._modified_keybindings[handler_name]
                else:
                    current_kb = cmd.get_keybinding()
                default_kb = cmd.get_default_keybinding()

                current_text = self._format_keybinding_text(current_kb)
                default_text = self._format_keybinding_text(default_kb)

                if current_text != default_text:
                    msg = f"KEYBINDINGS GRID: Saving {handler_name}: '{current_text}' (was '{default_text}')"
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    if current_kb and current_kb.keysymstring:
                        binding_data = [
                            current_kb.keysymstring,
                            str(current_kb.modifier_mask),
                            str(current_kb.modifiers),
                            str(current_kb.click_count)
                        ]
                        keybindings[handler_name] = [binding_data]
                    elif default_kb and default_kb.keysymstring:
                        # Was unbound - save empty list to indicate unbinding
                        keybindings[handler_name] = []

        self._modified_keybindings.clear()
        self._has_unsaved_changes = False
        return general, keybindings

    def refresh(self) -> None:
        """Refresh the keyboard layout and orca modifier displays."""

        self._initializing = True

        if self.keyboard_layout_combo is not None:
            current_layout = get_manager().get_keyboard_layout_value()
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

            is_desktop = layout_value == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
            get_manager().set_keyboard_layout(is_desktop)

            if self._orca_modifier_combo is not None:
                if is_desktop:
                    self._orca_modifier_combo.set_active(0)
                    settings.orcaModifierKeys = settings.DESKTOP_MODIFIER_KEYS
                else:
                    self._orca_modifier_combo.set_active(3)
                    settings.orcaModifierKeys = settings.LAPTOP_MODIFIER_KEYS

        get_manager().apply_user_overrides()
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

# pylint: disable-next=too-many-public-methods
class CommandManager:
    """Singleton manager for coordinating commands between scripts and UI."""

    def __init__(self) -> None:
        """Initializes the command manager."""

        self._keyboard_commands: dict[str, KeyboardCommand] = {}
        self._braille_commands: dict[str, BrailleCommand] = {}
        self._commands_by_keyval: dict[int, list[KeyboardCommand]] = {}
        self._commands_by_keycode: dict[int, list[KeyboardCommand]] = {}
        self._is_desktop: bool = settings.keyboardLayout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
        self._initialized: bool = False

        msg = "COMMAND MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("CommandManager", self)

    def is_desktop_layout(self) -> bool:
        """Returns True if the current keyboard layout is desktop."""

        return self._is_desktop

    @dbus_service.getter
    def get_keyboard_layout_is_desktop(self) -> bool:
        """Returns True if the current keyboard layout is desktop."""

        return self._is_desktop

    def get_keyboard_layout_value(self) -> int:
        """Returns the keyboard layout as an integer value for saving."""

        if self._is_desktop:
            return settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
        return settings.GENERAL_KEYBOARD_LAYOUT_LAPTOP

    @dbus_service.setter
    def set_keyboard_layout_is_desktop(self, is_desktop: bool) -> bool:
        """Sets whether the keyboard layout is desktop (True) or laptop (False)."""

        msg = f"COMMAND MANAGER: Setting keyboard layout is_desktop to {is_desktop}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self._is_desktop == is_desktop:
            return True

        self._is_desktop = is_desktop
        orca_modifier_manager.get_manager().set_modifiers_for_layout(is_desktop)

        has_device = input_event_manager.get_manager().has_device()

        if has_device:
            old_bindings = self._get_active_bindings(self._keyboard_commands)
            old_key_to_cmd = self._get_key_to_cmd_mapping(self._keyboard_commands)

        self._apply_layout_to_commands()
        self.apply_user_overrides()

        if has_device:
            self._diff_and_update_grabs(
                self._keyboard_commands, "keyboard layout change", old_bindings, old_key_to_cmd)
        else:
            msg = "COMMAND MANAGER: Device not ready, skipping grab updates."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        layout = "desktop" if is_desktop else "laptop"
        msg = f"COMMAND MANAGER: Keyboard layout set to {layout}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def set_keyboard_layout(self, is_desktop: bool) -> None:
        """Sets the keyboard layout and updates all command keybindings."""

        self.set_keyboard_layout_is_desktop(is_desktop)

    @dbus_service.command
    def toggle_keyboard_layout(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles between desktop and laptop keyboard layout."""

        tokens = ["COMMAND MANAGER: toggle_keyboard_layout. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        new_is_desktop = not self._is_desktop
        self.set_keyboard_layout_is_desktop(new_is_desktop)

        if script is not None and notify_user:
            if new_is_desktop:
                script.present_message(messages.KEYBOARD_LAYOUT_DESKTOP)
            else:
                script.present_message(messages.KEYBOARD_LAYOUT_LAPTOP)

        return True

    def set_up_commands(self) -> None:
        """Sets up commands owned by CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        msg = "COMMAND MANAGER: Setting up commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.add_command(KeyboardCommand(
            "toggle_keyboard_layout",
            self.toggle_keyboard_layout,
            guilabels.KB_GROUP_DEFAULT,
            cmdnames.TOGGLE_KEYBOARD_LAYOUT,
            desktop_keybinding=None,
            laptop_keybinding=None
        ))

    def _apply_layout_to_commands(self) -> None:
        """Updates all keyboard commands' active keybindings based on current layout."""

        restored_names: list[str] = []
        for cmd in self._keyboard_commands.values():
            old_kb = cmd.get_keybinding()
            default_kb = cmd.get_default_keybinding(self._is_desktop)
            if old_kb is not default_kb:
                self._remove_from_key_index(cmd)
                cmd.set_keybinding(default_kb)
                self._add_to_key_index(cmd)
                if old_kb is None and default_kb is not None:
                    restored_names.append(cmd.get_name())
        if restored_names:
            msg = f"COMMAND MANAGER: Restored {len(restored_names)} commands to default bindings:"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            for name in restored_names:
                debug.print_message(debug.LEVEL_INFO, f"    {name}", True)

    def _add_to_key_index(self, cmd: KeyboardCommand) -> None:
        """Adds a command to the key indexes for fast lookup."""

        kb = cmd.get_keybinding()
        if kb is None:
            return

        if not kb.keycode:
            kb.keyval, kb.keycode = keybindings.get_keycodes(kb.keysymstring)

        if kb.keyval not in self._commands_by_keyval:
            self._commands_by_keyval[kb.keyval] = []
        self._commands_by_keyval[kb.keyval].append(cmd)

        if kb.keycode not in self._commands_by_keycode:
            self._commands_by_keycode[kb.keycode] = []
        self._commands_by_keycode[kb.keycode].append(cmd)

    def _remove_from_key_index(self, cmd: KeyboardCommand) -> None:
        """Removes a command from the key indexes."""

        kb = cmd.get_keybinding()
        if kb is None:
            return

        if kb.keyval in self._commands_by_keyval:
            try:
                self._commands_by_keyval[kb.keyval].remove(cmd)
            except ValueError:
                pass  # Command wasn't in the list

        if kb.keycode in self._commands_by_keycode:
            try:
                self._commands_by_keycode[kb.keycode].remove(cmd)
            except ValueError:
                pass  # Command wasn't in the list

    def add_command(self, command: Command) -> None:
        """Adds a command to the registry and sets its active keybinding."""

        if isinstance(command, KeyboardCommand):
            self._keyboard_commands[command.get_name()] = command
            default_kb = command.get_default_keybinding(self._is_desktop)
            command.set_keybinding(default_kb)
            self._add_to_key_index(command)
        elif isinstance(command, BrailleCommand):
            self._braille_commands[command.get_name()] = command

    def get_command(self, command_name: str) -> Command | None:
        """Returns the command with the specified name, or None."""

        if command_name in self._keyboard_commands:
            return self._keyboard_commands[command_name]
        return self._braille_commands.get(command_name)

    def get_keyboard_command(self, command_name: str) -> KeyboardCommand | None:
        """Returns the keyboard command with the specified name, or None."""

        return self._keyboard_commands.get(command_name)

    def get_all_keyboard_commands(self) -> tuple[KeyboardCommand, ...]:
        """Returns all registered keyboard commands."""

        return tuple(self._keyboard_commands.values())

    def get_all_braille_commands(self) -> tuple[BrailleCommand, ...]:
        """Returns all registered braille commands."""

        return tuple(self._braille_commands.values())

    def _get_keyboard_commands_by_group_label(
        self,
        group_label: str
    ) -> tuple[KeyboardCommand, ...]:
        """Returns all keyboard commands with the specified group label."""

        return tuple(
            cmd for cmd in self._keyboard_commands.values()
            if cmd.get_group_label() == group_label
        )

    def apply_user_overrides(self) -> None:
        """Applies user-customized keybindings from settings to Commands."""

        # First, reset all keybindings to their layout defaults.
        # This ensures that app-specific unbindings from a previous app
        # don't persist when switching to a different app.
        self._apply_layout_to_commands()

        keybindings_dict = settings_manager.get_manager().get_active_keybindings()
        if keybindings_dict:
            msg = f"COMMAND MANAGER: Applying {len(keybindings_dict)} user overrides"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "COMMAND MANAGER: No user overrides to apply"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        for command_name, binding_tuples in keybindings_dict.items():
            cmd = self.get_keyboard_command(command_name)
            if cmd is None:
                continue

            old_kb = cmd.get_keybinding()

            # Empty list means the user explicitly unbound this command
            if binding_tuples == []:
                if old_kb is not None:
                    self._remove_from_key_index(cmd)
                    cmd.set_keybinding(None)
                continue

            # Apply the customized binding
            for binding_tuple in binding_tuples:
                keysym, _mask, mods, clicks = binding_tuple
                if not keysym:
                    if old_kb is not None:
                        self._remove_from_key_index(cmd)
                        cmd.set_keybinding(None)
                else:
                    # Check if the binding actually changed
                    old_key = self._binding_key(old_kb) if old_kb else None
                    new_key = (keysym, int(mods), int(clicks))
                    if old_key == new_key:
                        # Binding unchanged, skip to preserve grabs
                        continue

                    self._remove_from_key_index(cmd)
                    kb = keybindings.KeyBinding(keysym, int(mods), click_count=int(clicks))
                    cmd.set_keybinding(kb)
                    self._add_to_key_index(cmd)

    def get_command_for_event(
        self,
        event: input_event.KeyboardEvent,
        active_only: bool = True
    ) -> KeyboardCommand | None:
        """Returns the keyboard command matching the keyboard event, or None."""

        click_count = event.get_click_count()
        # Check both keyval and keycode indexes since Shift changes the keyval
        # (e.g., 'h' vs 'H') but not the keycode.
        candidates = set(self._commands_by_keyval.get(event.id, []))
        candidates.update(self._commands_by_keycode.get(event.hw_code, []))
        for cmd in candidates:
            if active_only and not cmd.is_active():
                continue
            kb = cmd.get_keybinding()
            if kb is None:
                continue
            if not kb.matches(event.id, event.hw_code, event.modifiers):
                continue
            if kb.click_count == click_count:
                return cmd
        return None

    def get_command_for_braille_event(self, braille_key: int) -> BrailleCommand | None:
        """Returns the braille command matching the braille key code, or None."""

        for cmd in self._braille_commands.values():
            if braille_key in cmd.get_braille_bindings():
                return cmd
        return None

    def get_command_for_keybinding(
        self, keysymstring: str, modifiers: int, click_count: int
    ) -> KeyboardCommand | None:
        """Returns the keyboard command matching the keybinding properties, or None."""

        for cmd in self._keyboard_commands.values():
            kb = cmd.get_keybinding()
            if kb is None:
                continue
            if (kb.keysymstring == keysymstring
                    and kb.modifiers == modifiers
                    and kb.click_count == click_count):
                return cmd
        return None

    def has_multi_click_bindings(self, keyval: int, keycode: int, modifiers: int) -> bool:
        """Returns True if there are any bindings for this key with click_count > 1."""

        # Check both keyval and keycode indexes since Shift changes the keyval.
        candidates = set(self._commands_by_keyval.get(keyval, []))
        candidates.update(self._commands_by_keycode.get(keycode, []))
        for cmd in candidates:
            kb = cmd.get_keybinding()
            if kb is None:
                continue
            if kb.matches(keyval, keycode, modifiers) and kb.click_count > 1:
                return True
        return False

    def set_group_enabled(self, group_label: str, enabled: bool) -> None:
        """Sets the enabled state for all commands in a group."""

        added_count = 0
        removed_count = 0

        for cmd in self._get_keyboard_commands_by_group_label(group_label):
            # Group toggle commands are skipped since they must remain active to re-enable
            # the group.
            if cmd.is_group_toggle():
                continue

            was_active = cmd.is_active()
            cmd.set_enabled(enabled)
            is_active = cmd.is_active()

            kb = cmd.get_keybinding()
            if kb is None:
                continue

            if was_active and not is_active and kb.has_grabs():
                kb.remove_grabs()
                removed_count += 1
            elif not was_active and is_active and not kb.has_grabs():
                kb.add_grabs()
                added_count += 1

        if removed_count or added_count:
            msg = (f"COMMAND MANAGER: set_group_enabled({group_label}, {enabled}): "
                   f"removed {removed_count}, added {added_count}")
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_group_suspended(self, group_label: str, suspended: bool) -> None:
        """Sets the suspended state for all commands in a group."""

        added_count = 0
        removed_count = 0

        for cmd in self._get_keyboard_commands_by_group_label(group_label):
            was_active = cmd.is_active()
            cmd.set_suspended(suspended)
            is_active = cmd.is_active()

            kb = cmd.get_keybinding()
            if kb is None:
                continue

            if was_active and not is_active and kb.has_grabs():
                kb.remove_grabs()
                removed_count += 1
            elif not was_active and is_active and not kb.has_grabs():
                kb.add_grabs()
                added_count += 1

        if removed_count or added_count:
            msg = (f"COMMAND MANAGER: set_group_suspended({group_label}, {suspended}): "
                   f"removed {removed_count}, added {added_count}")
            debug.print_message(debug.LEVEL_INFO, msg, True)

    @staticmethod
    def _binding_key(kb: keybindings.KeyBinding | None) -> tuple[str, int, int] | None:
        """Returns a hashable key for a keybinding, or None if no binding."""

        if kb is None or not kb.keysymstring:
            return None
        return (kb.keysymstring, kb.modifiers, kb.click_count)

    def _format_binding_key(self, key: tuple[str, int, int]) -> str:
        """Formats a binding key tuple as a readable string."""
        keysym, mods, clicks = key
        mod_str = keybindings.get_modifier_names(mods) if mods else ""
        click_str = f" x{clicks}" if clicks > 1 else ""
        return f"{mod_str}{keysym}{click_str}"

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments,too-many-branches,too-many-locals
    def _diff_bindings(
        self,
        old_bindings: dict[tuple[str, int, int], keybindings.KeyBinding],
        new_bindings: dict[tuple[str, int, int], keybindings.KeyBinding],
        old_key_to_cmd: dict[tuple[str, int, int], str],
        new_key_to_cmd: dict[tuple[str, int, int], str],
        reason: str = ""
    ) -> None:
        """Updates grabs based on diff between old and new binding maps."""

        removed: list[tuple[str, int, int]] = []
        added: list[tuple[str, int, int]] = []
        transferred: list[tuple[str, int, int]] = []
        start_time = time.time()

        for key, old_kb in old_bindings.items():
            if key in new_bindings:
                new_kb = new_bindings[key]
                if old_kb is not new_kb and old_kb.has_grabs():
                    new_kb.set_grab_ids(old_kb.get_grab_ids())
                    old_kb.set_grab_ids([])
                    transferred.append(key)
            else:
                if old_kb.has_grabs():
                    old_kb.remove_grabs()
                    removed.append(key)

        transferred_keys = set(transferred)
        for key, new_kb in new_bindings.items():
            if key not in transferred_keys and not new_kb.has_grabs():
                new_kb.add_grabs()
                if new_kb.has_grabs():
                    added.append(key)

        msg = f"COMMAND MANAGER: Grab diff: {reason}"
        msg += f" (old: {len(old_bindings)}, new: {len(new_bindings)})"
        debug.print_message(debug.LEVEL_INFO, f"\nvvvvv {msg} vvvvv", False)

        if not removed and not added and not transferred:
            debug.print_message(debug.LEVEL_INFO, "  No grab changes", True)
        else:
            if removed:
                debug.print_message(debug.LEVEL_INFO, f"  Removed ({len(removed)}):", True)
                for key in removed:
                    binding_str = self._format_binding_key(key)
                    cmd_name = old_key_to_cmd.get(key, "unknown")
                    debug.print_message(debug.LEVEL_INFO, f"    {binding_str}: {cmd_name}", True)
            if added:
                debug.print_message(debug.LEVEL_INFO, f"  Added ({len(added)}):", True)
                for key in added:
                    binding_str = self._format_binding_key(key)
                    cmd_name = new_key_to_cmd.get(key, "unknown")
                    msg = f"    {binding_str}: {cmd_name}"
                    debug.print_message(debug.LEVEL_INFO, msg, True)
            if transferred:
                debug.print_message(debug.LEVEL_INFO, f"  Transferred ({len(transferred)}):", True)
                for key in transferred:
                    binding_str = self._format_binding_key(key)
                    cmd_name = new_key_to_cmd.get(key, "unknown")
                    debug.print_message(debug.LEVEL_INFO, f"    {binding_str}: {cmd_name}", True)

        msg = (
            f"^^^^^ COMMAND MANAGER: Diff completed in {time.time() - start_time:.4f}s. "
            f"Removed {len(removed)}, added {len(added)}, transferred {len(transferred)} ^^^^^\n"
        )
        debug.print_message(debug.LEVEL_INFO, msg, False)

    def _get_active_bindings(
        self,
        commands: dict[str, KeyboardCommand]
    ) -> dict[tuple[str, int, int], keybindings.KeyBinding]:
        """Returns a map of binding keys to KeyBinding objects for active commands."""

        bindings: dict[tuple[str, int, int], keybindings.KeyBinding] = {}
        for cmd in commands.values():
            if cmd.is_active():
                kb = cmd.get_keybinding()
                key = self._binding_key(kb)
                if key is not None and kb is not None:
                    bindings[key] = kb
        return bindings

    def _get_key_to_cmd_mapping(
        self,
        commands: dict[str, KeyboardCommand]
    ) -> dict[tuple[str, int, int], str]:
        """Returns a map of binding keys to command names."""

        key_to_cmd: dict[tuple[str, int, int], str] = {}
        for cmd in commands.values():
            kb = cmd.get_keybinding()
            key = self._binding_key(kb)
            if key is not None:
                key_to_cmd[key] = cmd.get_name()
        return key_to_cmd

    def _diff_and_update_grabs(
        self,
        new_commands: dict[str, KeyboardCommand],
        reason: str = "",
        old_bindings: dict[tuple[str, int, int], keybindings.KeyBinding] | None = None,
        old_key_to_cmd: dict[tuple[str, int, int], str] | None = None
    ) -> None:
        """Updates grabs by diffing old vs new bindings; computes old state if not provided."""

        if old_bindings is None:
            old_bindings = self._get_active_bindings(self._keyboard_commands)
        if old_key_to_cmd is None:
            old_key_to_cmd = self._get_key_to_cmd_mapping(self._keyboard_commands)
        new_bindings = self._get_active_bindings(new_commands)
        new_key_to_cmd = self._get_key_to_cmd_mapping(new_commands)
        self._diff_bindings(old_bindings, new_bindings, old_key_to_cmd, new_key_to_cmd, reason)

    def set_active_commands(self, commands: dict[str, KeyboardCommand], reason: str = "") -> None:
        """Sets the active commands."""

        msg = "COMMAND MANAGER: Setting active commands"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        old_bindings = self._get_active_bindings(self._keyboard_commands)
        old_key_to_cmd = self._get_key_to_cmd_mapping(self._keyboard_commands)

        self._keyboard_commands = commands
        self._commands_by_keyval.clear()
        self._commands_by_keycode.clear()
        for cmd in commands.values():
            self._add_to_key_index(cmd)

        self._diff_and_update_grabs(commands, reason, old_bindings, old_key_to_cmd)

    def activate_commands(self, reason: str = "") -> None:
        """Applies user overrides and updates grabs for the active script."""

        msg = "COMMAND MANAGER: Activating commands"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        old_bindings = self._get_active_bindings(self._keyboard_commands)
        old_key_to_cmd = self._get_key_to_cmd_mapping(self._keyboard_commands)
        self.apply_user_overrides()
        self._diff_and_update_grabs(self._keyboard_commands, reason, old_bindings, old_key_to_cmd)

    def get_keyboard_commands(self) -> dict[str, KeyboardCommand]:
        """Returns the current keyboard commands dict."""

        return self._keyboard_commands

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def register_command(
        self,
        name: str,
        function: Callable[..., bool],
        description: str = "",
        key: str = "",
        modifiers: int = 0,
        click_count: int = 1,
        group_label: str = ""
    ) -> KeyboardCommand:
        """Convenience method to create and register a command with optional key binding."""

        kb = None
        if key:
            kb = keybindings.KeyBinding(key, modifiers, click_count=click_count)

        cmd = KeyboardCommand(
            name,
            function,
            group_label,
            description,
            desktop_keybinding=kb,
            laptop_keybinding=kb
        )
        self.add_command(cmd)
        return cmd

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
