# Orca
#
# Copyright 2025-2026 Igalia, S.L.
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

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes

"""Preferences grid for Orca commands and keybindings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # pylint: disable=no-name-in-module

from . import (
    ax_device_manager,
    command_manager,
    debug,
    gsettings_registry,
    guilabels,
    keybindings,
    keynames,
    messages,
    orca_modifier_manager,
    preferences_grid_base,
    presentation_manager,
    script_manager,
)
from .ax_object import AXObject

if TYPE_CHECKING:
    from collections.abc import Callable

    from .command import KeyboardCommand
    from .scripts import default


class KeybindingsPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """Grid widget for keybindings preferences."""

    # pylint: disable=no-member

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for commands preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.COMMANDS,
            panel_id="manual.commands",
            description=(
                "Commands settings let you choose the keyboard layout and screen reader "
                "modifier keys, and customize command keybindings.\n\n"
                "Orca commands are organized into groups in the Commands list. Choose a "
                "group from the list, then activate its row, or press Right Arrow, to "
                "open its commands. Press Left Arrow, Escape, or Alt+Left to return to "
                "the list.\n\n"
                "After choosing a command, press the new key combination, then press "
                "Return to bind it. Press Delete or Backspace without modifiers to "
                "unbind the command. Press Escape to cancel. Orca warns you if the "
                "binding is already used by another active command."
            ),
            schema="keybindings",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.KEYBOARD_LAYOUT,
                    kind="choice",
                    summary="Choose the layout that matches your keyboard.",
                    schema="keybindings",
                    key="keyboard-layout",
                    values=(guilabels.KEYBOARD_LAYOUT_DESKTOP, guilabels.KEYBOARD_LAYOUT_LAPTOP),
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.KEYBOARD_LAYOUT_DESKTOP,
                            value="desktop",
                            summary="Intended for use with a full-size keyboard. The desktop "
                            "layout uses the numeric keypad for some Orca commands.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.KEYBOARD_LAYOUT_LAPTOP,
                            value="laptop",
                            summary="Intended for use with a laptop-style keyboard, including "
                            "keyboards that lack a numeric keypad.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MODIFIER_KEYS,
                    kind="list",
                    summary=(
                        "Chooses which keys act as the Orca modifier for the selected "
                        "keyboard layout."
                    ),
                    values=(
                        guilabels.MODIFIER_INSERT,
                        guilabels.MODIFIER_KP_INSERT,
                        guilabels.MODIFIER_CAPS_LOCK,
                    ),
                ),
            ),
        )

    def __init__(
        self,
        script: default.Script,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize the keybindings preferences grid."""

        super().__init__(guilabels.COMMANDS)
        self._script = script
        self._initializing = True
        self._title_change_callback = title_change_callback

        self._categories: dict[str, list[KeyboardCommand]] = {}
        self._current_category: str | None = None
        self._captured_key: tuple[str, int, int] = ("", 0, 0)
        self._orca_modifier_pressed_during_capture: bool = False
        self._binding_cleared: bool = False
        self._pending_key_bindings: dict[str, str] = {}
        self._pending_already_bound_message_id: int | None = None
        # Store modified keybindings separately so they survive apply_user_overrides()
        self._modified_keybindings: dict[str, keybindings.KeyBinding | None] = {}
        self._keybinding_being_edited: str | None = None
        self._saved_commands: dict[str, KeyboardCommand] = {}

        self._original_keyboard_layout_is_desktop: bool = (
            command_manager.get_manager().get_keyboard_layout_is_desktop()
        )

        self.keyboard_layout_combo: Gtk.ComboBox | None = None
        self._modifier_switches: dict[str, Gtk.Switch] = {}
        self._settings_listbox: preferences_grid_base.FocusManagedListBox | None = None

        self._build()
        self._initializing = False

    _MODIFIER_KEY_OPTIONS: ClassVar[list[tuple[str, list[str]]]] = [
        (guilabels.MODIFIER_INSERT, ["Insert"]),
        (guilabels.MODIFIER_KP_INSERT, ["KP_Insert"]),
        (guilabels.MODIFIER_CAPS_LOCK, ["Caps_Lock", "Shift_Lock"]),
    ]

    def _build(self) -> None:
        """Build the keybindings UI."""

        row = 0

        keyboard_layout_model = Gtk.ListStore(str, int)
        keyboard_layout_model.append(
            [guilabels.KEYBOARD_LAYOUT_DESKTOP, command_manager.KeyboardLayout.DESKTOP.value],
        )
        keyboard_layout_model.append(
            [guilabels.KEYBOARD_LAYOUT_LAPTOP, command_manager.KeyboardLayout.LAPTOP.value],
        )

        self._settings_listbox = preferences_grid_base.FocusManagedListBox()

        layout_row, layout_combo, _label = self._create_combo_box_row(
            guilabels.KEYBOARD_LAYOUT,
            keyboard_layout_model,
            self._on_keyboard_layout_changed,
            include_top_separator=False,
        )
        self._settings_listbox.add_row_with_widget(layout_row, layout_combo)
        self.keyboard_layout_combo = layout_combo

        self.attach(self._settings_listbox, 0, row, 1, 1)
        row += 1

        modifier_listbox = preferences_grid_base.FocusManagedListBox(guilabels.MODIFIER_KEYS)

        for label, keys in self._MODIFIER_KEY_OPTIONS:
            switch_row, switch, _label = self._create_switch_row(
                label,
                self._on_modifier_switch_toggled,
                state=False,
                include_top_separator=False,
            )
            self._modifier_switches[keys[0]] = switch
            modifier_listbox.add_row_with_widget(switch_row, switch)

        self.attach(modifier_listbox.get_container(), 0, row, 1, 1)
        row += 1

        commands_heading = self._create_heading_label(guilabels.COMMANDS)
        self.attach(commands_heading, 0, row, 1, 1)
        row += 1

        stack, _categories_listbox, _detail_listbox = self._create_stacked_preferences(
            on_category_activated=self._on_category_activated,
            on_detail_row_activated=self._on_keybinding_activated,
        )
        if self._categories_listbox:
            self._categories_listbox.get_accessible().set_name(guilabels.COMMANDS)
        self.attach(stack, 0, row, 1, 1)

        self._register_stack_disable_widgets(
            self._settings_listbox,
            modifier_listbox.get_container(),
            commands_heading,
        )

    def reload(self) -> None:
        """Reload keybindings from the script."""

        app_name = AXObject.get_name(self._script.app) if self._script.app else ""
        layout = gsettings_registry.get_registry().layered_lookup(
            "keybindings",
            "keyboard-layout",
            "",
            genum="org.gnome.Orca.KeyboardLayout",
            app_name=app_name or None,
            default="desktop",
        )
        command_manager.get_manager().set_keyboard_layout_is_desktop(layout == "desktop")
        self._original_keyboard_layout_is_desktop = (
            command_manager.get_manager().get_keyboard_layout_is_desktop()
        )
        # set_keyboard_layout_is_desktop() already applied the overrides and updated the grabs.
        self._populate_keybindings()
        if self._current_category and self._current_category in self._categories:
            self._populate_category_detail(self._current_category)
        self._modified_keybindings.clear()
        self._has_unsaved_changes = False
        self.refresh()

    def revert_changes(self) -> None:
        """Revert keyboard layout and orca modifier to their original values."""

        current_is_desktop = command_manager.get_manager().get_keyboard_layout_is_desktop()
        if current_is_desktop != self._original_keyboard_layout_is_desktop:
            command_manager.get_manager().load_keyboard_layout(
                self._original_keyboard_layout_is_desktop
            )

        orca_modifier_manager.get_manager().set_modifier_keys_override(None)

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

        all_commands = command_manager.get_manager().get_all_keyboard_commands()

        for cmd in all_commands:
            group_label = cmd.get_group_label()
            if group_label not in self._categories:
                self._categories[group_label] = []
            self._categories[group_label].append(cmd)

        if app_name and app_name in self._categories and not self._categories[app_name]:
            del self._categories[app_name]

        for commands in self._categories.values():
            commands.sort(key=lambda command: command.is_transient())

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
                category=category_name,
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

        self.reload()
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
        if self._current_category:
            if self._title_change_callback:
                self._title_change_callback(self._current_category)
            if self._detail_listbox:
                self._detail_listbox.get_accessible().set_name(self._current_category)

    # pylint: disable=no-member

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

            description = cmd.get_description() or cmd.get_name()
            desc_label = Gtk.Label(label=description, xalign=0)
            desc_label.set_line_wrap(True)
            desc_label.set_hexpand(True)
            vbox.pack_start(desc_label, False, False, 0)

            binding = cmd.get_keybinding()
            binding_text = self._format_keybinding_text(binding) or ""

            binding_label = Gtk.Label(xalign=0)
            binding_label.set_markup(f"<small>{GLib.markup_escape_text(binding_text, -1)}</small>")
            binding_label.get_style_context().add_class("dim-label")
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

        if self._keybinding_being_edited is not None:
            return

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

    def _create_capture_entry(self, command: KeyboardCommand) -> Gtk.Entry:
        """Creates and returns an entry widget configured for key capture."""

        entry = Gtk.Entry()
        entry.set_alignment(0.0)
        binding = command.get_keybinding()
        if binding and binding.keysymstring:
            current_text = self._format_keybinding_text(binding)
            entry.set_text(current_text or "")
        else:
            entry.set_text("")
        return entry

    def _start_inline_editing(
        self,
        row: Gtk.ListBoxRow,
        command: KeyboardCommand,
        vbox: Gtk.Box,
        binding_label: Gtk.Label,
    ) -> None:
        """Start inline editing of a keybinding."""

        binding_label.hide()

        capture_entry = self._create_capture_entry(command)
        vbox.pack_start(capture_entry, False, False, 0)
        capture_entry.show()

        def swap_widgets():
            vbox.remove(binding_label)
            capture_entry.grab_focus()
            return False

        GLib.idle_add(swap_widgets)

        self._captured_key = ("", 0, 0)
        self._orca_modifier_pressed_during_capture = False
        self._keybinding_being_edited = command.get_name()

        def on_key_release(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
            event_string = Gdk.keyval_name(event.keyval)
            orca_mods = orca_modifier_manager.get_manager().get_orca_modifier_keys()
            if event_string in orca_mods:
                self._orca_modifier_pressed_during_capture = False
            return False

        def on_key_press(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
            if event.keyval == Gdk.KEY_Escape and not self._orca_modifier_pressed_during_capture:
                self._finish_inline_editing(
                    row,
                    command,
                    vbox,
                    capture_entry,
                    canceled=True,
                )
                return True

            if event.keyval == Gdk.KEY_Return and not self._orca_modifier_pressed_during_capture:
                if self._captured_key[0]:
                    key_name, modifiers, click_count = self._captured_key
                    handler_name = command.get_name()
                    description_dup = self._find_duplicate_binding(
                        key_name,
                        modifiers,
                        click_count,
                        handler_name,
                        command.get_group_label(),
                    )
                    if description_dup:

                        def present_duplicate_error():
                            presentation_manager.get_manager().present_message(
                                messages.KB_ALREADY_BOUND % description_dup,
                            )
                            return False

                        GLib.idle_add(present_duplicate_error)
                        capture_entry.set_text("")
                        self._captured_key = ("", 0, 0)
                        return True

                self._finish_inline_editing(
                    row,
                    command,
                    vbox,
                    capture_entry,
                    canceled=False,
                )
                return True

            key_processed = self._process_key_captured(event)
            if not key_processed or not self._captured_key[0]:
                return True

            key_name, modifiers, click_count = self._captured_key

            if key_name in ["Delete", "BackSpace"] and not modifiers:
                capture_entry.set_text("")
                self._captured_key = ("", 0, 0)

                def present_delete_message():
                    presentation_manager.get_manager().present_message(messages.KB_DELETED)
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
                presentation_manager.get_manager().present_message(
                    messages.KB_CAPTURED % new_string,
                )
                return False

            GLib.idle_add(present_message_after_keypress)

            return True

        capture_entry.connect("key-press-event", on_key_press)
        capture_entry.connect("key-release-event", on_key_release)
        row.capture_entry = capture_entry

        script = script_manager.get_manager().get_active_script()
        assert script
        presentation_manager.get_manager().present_message(messages.KB_ENTER_NEW_KEY)
        self._saved_commands = command_manager.get_manager().get_keyboard_commands()
        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        command_manager.get_manager().set_active_commands({}, "Capturing keys")
        ax_device_manager.get_manager().unmap_all_modifiers()

    def _finish_inline_editing(
        self,
        row: Gtk.ListBoxRow,
        command: KeyboardCommand,
        vbox: Gtk.Box,
        capture_entry: Gtk.Entry,
        canceled: bool,
    ) -> None:
        """Finish inline editing of a keybinding."""

        # Update keybinding before restoring commands so grabs match actual keybindings.
        # Otherwise a deleted binding's grab remains, consuming keystrokes without executing
        # anything (is_active() returns False when keybinding is None).
        if not canceled:
            captured_text = capture_entry.get_text().strip()
            script_manager.get_manager().get_active_script()
            handler_name = command.get_name()
            if not captured_text:
                command.set_keybinding(None)
                self._modified_keybindings[handler_name] = None
                self._has_unsaved_changes = True

                def present_delete_confirmation():
                    presentation_manager.get_manager().present_message(
                        messages.KB_DELETED_CONFIRMATION,
                    )
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
                        presentation_manager.get_manager().present_message(msg)
                        return False

                    GLib.idle_add(present_confirmation)

        command_manager.get_manager().set_active_commands(
            self._saved_commands,
            "Done capturing keys",
        )
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

        binding = command.get_keybinding()
        binding_text = self._format_keybinding_text(binding) or ""
        new_label = Gtk.Label(xalign=0)
        new_label.set_markup(
            f"<small>{GLib.markup_escape_text(binding_text, -1)}</small>",
        )
        new_label.get_style_context().add_class("dim-label")
        row.binding_label = new_label

        capture_entry.hide()
        vbox.pack_start(new_label, False, False, 0)
        new_label.show()

        def swap_widgets():
            vbox.remove(capture_entry)
            row.grab_focus()
            return False

        GLib.idle_add(swap_widgets)

        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = None

    def _find_duplicate_binding(
        self,
        key_name: str,
        modifiers: int,
        click_count: int,
        exclude_handler: str | None = None,
        group_label: str = "",
    ) -> str | None:
        """Find if a keybinding is already used and return its description."""

        mgr = command_manager.get_manager()
        for category_label, category_commands in self._categories.items():
            if group_label and mgr.are_groups_exclusive(group_label, category_label):
                continue

            for cmd in category_commands:
                if exclude_handler and cmd.get_name() == exclude_handler:
                    continue

                binding = cmd.get_keybinding()
                if not binding or not binding.keysymstring:
                    continue

                if (
                    binding.keysymstring == key_name
                    and binding.modifiers == modifiers
                    and binding.click_count == click_count
                ):
                    return cmd.get_description() or cmd.get_name()

        return None

    def _process_key_captured(self, event: Gdk.EventKey) -> bool:
        """Process a captured key press event."""

        keycode = event.hardware_keycode
        keymap = Gdk.Keymap.get_default()  # pylint: disable=no-value-for-parameter
        entries_for_keycode = keymap.get_entries_for_keycode(keycode)
        entries = entries_for_keycode[-1]
        event_string = Gdk.keyval_name(entries[0])
        event_state = event.state

        orca_mods = orca_modifier_manager.get_manager().get_orca_modifier_keys()
        if event_string in orca_mods:
            self._orca_modifier_pressed_during_capture = True
            self._captured_key = ("", keybindings.ORCA_MODIFIER_MASK, 0)
            return False

        modifier_keys = [
            "Alt_L",
            "Alt_R",
            "Control_L",
            "Control_R",
            "Shift_L",
            "Shift_R",
            "Meta_L",
            "Meta_R",
            "Super_L",
            "Super_R",
            "Num_Lock",
            "Caps_Lock",
            "Shift_Lock",
            "ISO_Level3_Shift",
        ]
        if event_string in modifier_keys:
            return False

        event_state = event_state & keybindings.NON_LOCKING_MODIFIER_MASK

        # Return and Escape are used to confirm/cancel editing, not as captured keys
        # Return False to let GTK process them normally
        if event_string in ["Return", "Escape"] and not self._orca_modifier_pressed_during_capture:
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

    def _create_key_capture_dialog(
        self,
        description: str,
        command: KeyboardCommand,
    ) -> tuple[Gtk.Dialog, Gtk.Entry]:
        """Creates and returns a dialog and entry configured for key capture."""

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

        return dialog, entry

    def _handle_dialog_key_press(
        self,
        event: Gdk.EventKey,
        entry: Gtk.Entry,
        handler_name: str,
        group_label: str,
        dialog: Gtk.Dialog,
    ) -> bool:
        """Handles a key press event in the key capture dialog."""

        if event.keyval == Gdk.KEY_Escape:
            dialog.response(Gtk.ResponseType.CANCEL)
            return True

        if event.keyval in (Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab):
            return False

        if not self._process_key_captured(event) or not self._captured_key[0]:
            return False

        key_name, modifiers, click_count = self._captured_key

        if key_name in ("Delete", "BackSpace") and not modifiers:
            entry.set_text("")
            presentation_manager.get_manager().present_message(messages.KB_DELETED)
            self._captured_key = ("", 0, 0)
            self._binding_cleared = True
            return True

        modifier_names = keybindings.get_modifier_names(modifiers)
        click_count_string = keynames.get_click_count_string(click_count)
        if click_count_string:
            click_count_string = f" ({click_count_string})"
        new_string = modifier_names + key_name + click_count_string

        entry.set_text(new_string)

        description_dup = self._find_duplicate_binding(
            key_name,
            modifiers,
            click_count,
            handler_name,
            group_label,
        )
        if description_dup:
            msg = messages.KB_ALREADY_BOUND % description_dup
        else:
            msg = messages.KB_CAPTURED % new_string
        presentation_manager.get_manager().present_message(msg)

        return True

    def _apply_dialog_key_capture(
        self,
        response: Gtk.ResponseType,
        command: KeyboardCommand,
    ) -> None:
        """Applies the result of a key capture dialog."""

        if response != Gtk.ResponseType.OK:
            return

        handler_name = command.get_name()
        key_name, modifiers, click_count = self._captured_key
        if self._binding_cleared:
            command.set_keybinding(None)
            self._modified_keybindings[handler_name] = None
        elif key_name:
            new_kb = keybindings.KeyBinding(key_name, modifiers, click_count)
            command.set_keybinding(new_kb)
            self._modified_keybindings[handler_name] = new_kb

        self._has_unsaved_changes = True
        if self._current_category:
            self._populate_category_detail(self._current_category)

    def _show_key_capture_dialog(self, command: KeyboardCommand) -> None:
        """Show dialog to capture a new key binding for the given command."""

        description = command.get_description() or command.get_name()
        handler_name = command.get_name()

        dialog, entry = self._create_key_capture_dialog(description, command)

        self._captured_key = ("", 0, 0)
        self._binding_cleared = False
        self._keybinding_being_edited = handler_name

        script = script_manager.get_manager().get_active_script()
        assert script

        def on_key_press(_widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
            return self._handle_dialog_key_press(
                event,
                entry,
                handler_name,
                command.get_group_label(),
                dialog,
            )

        entry.connect("key-press-event", on_key_press)

        presentation_manager.get_manager().present_message(messages.KB_ENTER_NEW_KEY)

        dialog.show_all()
        entry.grab_focus()
        entry.grab_add()

        while Gtk.events_pending():  # pylint: disable=no-value-for-parameter
            Gtk.main_iteration()

        saved_commands = command_manager.get_manager().get_keyboard_commands()
        orca_modifier_manager.get_manager().remove_grabs_for_orca_modifiers()
        command_manager.get_manager().set_active_commands({}, "Capturing keys")
        ax_device_manager.get_manager().unmap_all_modifiers()

        response = dialog.run()

        entry.grab_remove()
        command_manager.get_manager().set_active_commands(saved_commands, "Done capturing keys")
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()

        self._apply_dialog_key_capture(response, command)

        dialog.destroy()
        self._captured_key = ("", 0, 0)
        self._keybinding_being_edited = None

    # pylint: enable=no-member

    def save_settings(  # pylint: disable=too-many-locals, too-many-branches
        self,
        profile: str = "",
        app_name: str = "",
    ) -> tuple[dict[str, int | list[str]], dict[str, list[list[Any]]]]:
        """Save settings and return (general_settings, keybindings) tuple."""

        general: dict[str, int | list[str]] = {}
        bindings: dict[str, list[list[Any]]] = {}

        layout_value = command_manager.get_manager().get_keyboard_layout_value()
        if self.keyboard_layout_combo is not None:
            layout_iter = self.keyboard_layout_combo.get_active_iter()
            if layout_iter is not None:
                layout_value = self.keyboard_layout_combo.get_model().get_value(layout_iter, 1)
        general["keyboard-layout"] = layout_value

        is_desktop = layout_value == command_manager.KeyboardLayout.DESKTOP.value
        if self._modifier_switches:
            modifier_keys = self._get_selected_modifier_keys()
            if modifier_keys:
                if is_desktop:
                    general["desktop-modifier-keys"] = modifier_keys
                else:
                    general["laptop-modifier-keys"] = modifier_keys

        parent_overrides: dict[str, list[list[str]]] = {}
        if profile and (profile != "default" or app_name):
            registry = gsettings_registry.get_registry()
            if profile != "default":
                parent_overrides |= registry.get_keybindings("default", "")
            if app_name:
                parent_overrides |= registry.get_keybindings(profile, "")

        for category_commands in self._categories.values():
            for cmd in category_commands:
                handler_name = cmd.get_name()
                if command_manager.get_manager().get_keyboard_command(handler_name) is None:
                    continue
                if handler_name in self._modified_keybindings:
                    current_kb = self._modified_keybindings[handler_name]
                else:
                    current_kb = cmd.get_keybinding()

                current_text = self._format_keybinding_text(current_kb)

                if handler_name in parent_overrides:
                    parent_text = self._format_binding_data_text(parent_overrides[handler_name])
                else:
                    parent_text = self._format_keybinding_text(
                        cmd.get_default_keybinding(
                            command_manager.get_manager().is_desktop_layout(),
                        ),
                    )

                if current_text != parent_text:
                    msg = (
                        f"KEYBINDINGS GRID: Saving {handler_name}: '{current_text}' "
                        f"(parent '{parent_text}')"
                    )
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    if current_kb and current_kb.keysymstring:
                        binding_data = [
                            current_kb.keysymstring,
                            str(current_kb.modifier_mask),
                            str(current_kb.modifiers),
                            str(current_kb.click_count),
                        ]
                        bindings[handler_name] = [binding_data]
                    elif parent_text is not None:
                        bindings[handler_name] = []

        self._modified_keybindings.clear()
        self._has_unsaved_changes = False

        if profile:
            registry = gsettings_registry.get_registry()
            skip = not app_name and profile == "default"
            registry.save_schema("keybindings", general, profile, app_name, skip)
            kb_gs = registry.get_settings("keybindings", profile, "keybindings", app_name)
            if kb_gs is not None:
                if bindings:
                    kb_gs.set_value("entries", GLib.Variant("a{saas}", bindings))
                elif self._categories and kb_gs.get_user_value("entries") is not None:
                    kb_gs.reset("entries")

        return general, bindings

    def refresh(self) -> None:
        """Refresh the keyboard layout and orca modifier displays."""

        self._initializing = True

        if self.keyboard_layout_combo is not None:
            current_layout = command_manager.get_manager().get_keyboard_layout_value()
            model = self.keyboard_layout_combo.get_model()
            if model:
                for i, row in enumerate(model):
                    if row[1] == current_layout:
                        self.keyboard_layout_combo.set_active(i)
                        break

        if self._modifier_switches:
            layout_value = command_manager.get_manager().get_keyboard_layout_value()
            is_desktop = layout_value == command_manager.KeyboardLayout.DESKTOP.value
            app_name = AXObject.get_name(self._script.app) if self._script.app else ""
            modifier_keys = command_manager.get_manager().get_modifier_keys_for_layout(
                is_desktop,
                app_name,
            )
            for primary_key, switch in self._modifier_switches.items():
                switch.set_active(primary_key in modifier_keys)

        self._initializing = False

    def _on_keyboard_layout_changed(self, combo: Gtk.ComboBox) -> None:
        """Handle keyboard layout changes."""

        if self._initializing:
            return

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            layout_value = model.get_value(tree_iter, 1)

            is_desktop = layout_value == command_manager.KeyboardLayout.DESKTOP.value
            command_manager.get_manager().load_keyboard_layout(is_desktop)

            if self._modifier_switches:
                self._initializing = True
                app_name = AXObject.get_name(self._script.app) if self._script.app else ""
                saved_keys = command_manager.get_manager().get_modifier_keys_for_layout(
                    is_desktop,
                    app_name,
                )
                for primary_key, switch in self._modifier_switches.items():
                    switch.set_active(primary_key in saved_keys)
                self._initializing = False
                orca_modifier_manager.get_manager().set_modifier_keys_override(
                    self._get_selected_modifier_keys(),
                )

        # load_keyboard_layout() already applied the overrides and updated the grabs.
        self._populate_keybindings()
        self._has_unsaved_changes = True

    def _get_selected_modifier_keys(self) -> list[str]:
        """Returns the list of modifier keys from the current switch states."""

        keys: list[str] = []
        for _label, key_names in self._MODIFIER_KEY_OPTIONS:
            if self._modifier_switches.get(key_names[0], Gtk.Switch()).get_active():
                keys.extend(key_names)
        return keys

    def _on_modifier_switch_toggled(self, switch: Gtk.Switch, _pspec: Any) -> None:
        """Handle modifier key switch toggles."""

        if self._initializing:
            return

        selected = self._get_selected_modifier_keys()
        if not selected:
            switch.set_active(True)
            return

        orca_modifier_manager.get_manager().set_modifier_keys_override(selected)
        self._has_unsaved_changes = True

    def _format_keybinding_text(self, kb: keybindings.KeyBinding | None) -> str | None:
        """Format a keybinding as text for display."""

        if not kb or not kb.keysymstring:
            return None

        click_count_str = keynames.get_click_count_string(kb.click_count)
        if click_count_str:
            click_count_str = f" ({click_count_str})"

        return keybindings.get_modifier_names(kb.modifiers) + kb.keysymstring + click_count_str

    @staticmethod
    def _format_binding_data_text(binding_data: list[list[str]]) -> str | None:
        """Format raw dconf binding data as text, matching _format_keybinding_text output."""

        if not binding_data:
            return None
        entry = binding_data[0]
        if len(entry) < 4 or not entry[0]:
            return None
        click_count_str = keynames.get_click_count_string(int(entry[3]))
        if click_count_str:
            click_count_str = f" ({click_count_str})"
        return keybindings.get_modifier_names(int(entry[2])) + entry[0] + click_count_str
