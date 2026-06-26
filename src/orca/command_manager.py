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

# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

"""Manager for script commands and keybindings."""

from __future__ import annotations

import contextlib
import time
import weakref
from enum import Enum
from typing import TYPE_CHECKING, Protocol

import gi

gi.require_version("Atk", "1.0")
from gi.repository import GLib  # pylint: disable=no-name-in-module

from . import (
    ax_device_manager,
    cmdnames,
    dbus_service,
    debug,
    gsettings_registry,
    guilabels,
    input_event,
    keybindings,
    messages,
    orca_modifier_manager,
    presentation_manager,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .command_manager_preferences_grid import KeybindingsPreferencesGrid
    from .scripts import default


from .command import BrailleCommand, Command, KeyboardCommand


class ModalInputHandler(Protocol):
    """Something that can claim keyboard events while active, e.g. learn mode."""

    def will_handle_event(
        self,
        script: default.Script,
        event: input_event.KeyboardEvent,
        command: KeyboardCommand | None,
    ) -> bool:
        """Returns True to claim the event; False lets it pass through."""

    def handle_event(
        self,
        script: default.Script,
        event: input_event.KeyboardEvent,
        command: KeyboardCommand | None,
    ) -> bool:
        """Handles a claimed event (runs deferred)."""


# pylint: disable-next=too-many-instance-attributes
@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.KeyboardLayout",
    values={"desktop": 1, "laptop": 2},
)
class KeyboardLayout(Enum):
    """Keyboard layout enumeration."""

    DESKTOP = 1
    LAPTOP = 2

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


# pylint: disable-next=too-many-public-methods
@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.Keybindings",
    name="keybindings",
)
class CommandManager:  # pylint: disable=too-many-instance-attributes
    """Singleton manager for coordinating commands between scripts and UI."""

    _SCHEMA = "keybindings"

    def __init__(self) -> None:
        """Initializes the command manager."""

        self._keyboard_commands: dict[str, KeyboardCommand] = {}
        self._braille_commands: dict[str, BrailleCommand] = {}
        self._commands_by_keyval: dict[int, list[KeyboardCommand]] = {}
        self._commands_by_keycode: dict[int, list[KeyboardCommand]] = {}
        self._is_desktop: bool = True
        self._initialized: bool = False
        self._group_enabled: dict[str, bool | None] = {}
        self._exclusive_groups: list[set[str]] = []
        self._numlock_on: bool = False
        self._modal_handler: ModalInputHandler | None = None
        self._user_extensions: weakref.WeakSet[object] = weakref.WeakSet()
        self._prior_suspended: set[str] = set()

        msg = "COMMAND MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("CommandManager", self)

    def is_desktop_layout(self) -> bool:
        """Returns True if the current keyboard layout is desktop."""

        return self._is_desktop

    @gsettings_registry.get_registry().gsetting(
        key="keyboard-layout",
        schema="keybindings",
        genum="org.gnome.Orca.KeyboardLayout",
        default="desktop",
        summary="Keyboard layout (desktop, laptop)",
        migration_key="keyboardLayout",
    )
    @dbus_service.getter
    def get_keyboard_layout_is_desktop(self) -> bool:
        """Returns True if the current keyboard layout is desktop."""

        return self._is_desktop

    def get_keyboard_layout_value(self) -> int:
        """Returns the keyboard layout as an integer value for saving."""

        if self._is_desktop:
            return KeyboardLayout.DESKTOP.value
        return KeyboardLayout.LAPTOP.value

    @dbus_service.setter
    def set_keyboard_layout_is_desktop(self, is_desktop: bool) -> bool:
        """Sets whether the keyboard layout is desktop (True) or laptop (False)."""

        msg = f"COMMAND MANAGER: Setting keyboard layout is_desktop to {is_desktop}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        layout_changed = self._is_desktop != is_desktop
        if layout_changed:
            self._is_desktop = is_desktop

        has_device = ax_device_manager.get_manager().is_active()

        if has_device:
            old_bindings = self._get_active_bindings(self._keyboard_commands)
            old_key_to_cmd = self._get_key_to_cmd_mapping(self._keyboard_commands)

        if layout_changed:
            self._apply_layout_to_commands()
        self.apply_user_overrides()

        if has_device:
            self._diff_and_update_grabs(
                self._keyboard_commands,
                "keyboard layout change",
                old_bindings,
                old_key_to_cmd,
            )
        else:
            msg = "COMMAND MANAGER: Device not ready, skipping grab updates."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        layout = "desktop" if is_desktop else "laptop"
        msg = f"COMMAND MANAGER: Keyboard layout set to {layout}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def load_keyboard_layout(self, is_desktop: bool | None = None) -> None:
        """Loads the keyboard layout from dconf or sets it explicitly."""

        if is_desktop is None:
            layout = gsettings_registry.get_registry().layered_lookup(
                self._SCHEMA,
                "keyboard-layout",
                "",
                genum="org.gnome.Orca.KeyboardLayout",
                default="desktop",
            )
            is_desktop = layout == "desktop"
        self.set_keyboard_layout_is_desktop(is_desktop)

    @gsettings_registry.get_registry().gsetting(
        key="desktop-modifier-keys",
        schema="keybindings",
        gtype="as",
        default=["Insert", "KP_Insert"],
        summary="Keys used as the Orca modifier for the desktop layout",
    )
    @dbus_service.getter
    def get_desktop_modifier_keys(self) -> list[str]:
        """Returns the per-layout modifier keys for the desktop layout."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "desktop-modifier-keys",
            "as",
            default=["Insert", "KP_Insert"],
        )

    @dbus_service.setter
    def set_desktop_modifier_keys(self, keys: list[str]) -> bool:
        """Sets the per-layout modifier keys for the desktop layout."""

        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "desktop-modifier-keys",
            keys,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="laptop-modifier-keys",
        schema="keybindings",
        gtype="as",
        default=["Caps_Lock", "Shift_Lock"],
        summary="Keys used as the Orca modifier for the laptop layout",
    )
    @dbus_service.getter
    def get_laptop_modifier_keys(self) -> list[str]:
        """Returns the per-layout modifier keys for the laptop layout."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "laptop-modifier-keys",
            "as",
            default=["Caps_Lock", "Shift_Lock"],
        )

    @dbus_service.setter
    def set_laptop_modifier_keys(self, keys: list[str]) -> bool:
        """Sets the per-layout modifier keys for the laptop layout."""

        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "laptop-modifier-keys",
            keys,
        )
        return True

    def get_modifier_keys_for_layout(self, is_desktop: bool, app_name: str = "") -> list[str]:
        """Returns the per-layout modifier keys for the given layout."""

        if app_name:
            key = "desktop-modifier-keys" if is_desktop else "laptop-modifier-keys"
            if (
                keys := gsettings_registry.get_registry().layered_lookup(
                    self._SCHEMA,
                    key,
                    "as",
                    app_name=app_name,
                )
            ) is not None:
                return keys
        if is_desktop:
            return self.get_desktop_modifier_keys()
        return self.get_laptop_modifier_keys()

    def check_keyboard_settings(self) -> None:
        """Checks if keyboard layout or modifier keys changed and updates if needed."""

        self.load_keyboard_layout()

        mod_mgr = orca_modifier_manager.get_manager()
        if not mod_mgr.needs_modifier_refresh():
            return

        msg = f"COMMAND MANAGER: Modifier keys changing to {mod_mgr.get_orca_modifier_keys()}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        mod_mgr.refresh_orca_modifiers("Keyboard settings changed.")

    @dbus_service.command
    def toggle_keyboard_layout(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles between desktop and laptop keyboard layout."""

        tokens = [
            "COMMAND MANAGER: toggle_keyboard_layout. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        new_is_desktop = not self._is_desktop
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "keyboard-layout",
            "desktop" if new_is_desktop else "laptop",
        )
        orca_modifier_manager.get_manager().set_modifiers_for_layout()
        self.set_keyboard_layout_is_desktop(new_is_desktop)

        if script is not None and notify_user:
            if new_is_desktop:
                presentation_manager.get_manager().present_message(messages.KEYBOARD_LAYOUT_DESKTOP)
            else:
                presentation_manager.get_manager().present_message(messages.KEYBOARD_LAYOUT_LAPTOP)

        return True

    def set_modal_handler(self, handler: ModalInputHandler) -> bool:
        """Sets the modal handler. Returns True if the request was accepted."""

        if not self._can_replace_modal_handler(handler):
            msg = "COMMAND MANAGER: Refusing to replace active modal handler."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        self._modal_handler = handler
        msg = "COMMAND MANAGER: Modal handler is now set."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def clear_modal_handler(self, handler: ModalInputHandler) -> bool:
        """Clears the modal handler if handler owns it."""

        if self._modal_handler is not handler:
            msg = "COMMAND MANAGER: Refusing to clear modal handler owned by another handler."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        self._modal_handler = None
        msg = "COMMAND MANAGER: Modal handler is now cleared."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if self._is_desktop:
            self._update_numlock_grabs()
        return True

    def _can_replace_modal_handler(self, handler: ModalInputHandler) -> bool:
        """Returns True if the requested modal handler change is allowed."""

        if self._modal_handler is None:
            return True

        if self._modal_handler is handler:
            return True

        active_handler_is_user_extension = self._is_user_extension_handler(self._modal_handler)
        new_handler_is_user_extension = self._is_user_extension_handler(handler)
        return active_handler_is_user_extension and not new_handler_is_user_extension

    def register_user_extension(self, extension: object) -> None:
        """Records extension as a user-provided extension."""

        self._user_extensions.add(extension)

    def _is_user_extension_handler(self, handler: ModalInputHandler) -> bool:
        """Returns True if handler belongs to a user extension."""

        return handler in self._user_extensions

    def get_modal_handler(self) -> ModalInputHandler | None:
        """Returns the active modal key handler, if any."""

        return self._modal_handler

    def handle_numlock_toggled(self, numlock_on: bool) -> None:
        """Handles NumLock state changes by updating grabs for keypad commands."""

        self._numlock_on = numlock_on

        if not self._is_desktop:
            return

        msg = f"COMMAND MANAGER: NumLock toggled to {'on' if numlock_on else 'off'}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self._modal_handler is not None:
            msg = "COMMAND MANAGER: Skipping grab updates while a modal handler is active."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._update_numlock_grabs()

    def _update_numlock_grabs(self) -> None:
        """Updates KP_* grabs based on current NumLock state."""

        msg = f"COMMAND MANAGER: Updating NumLock grabs. NumLock is on: {self._numlock_on}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        orca_modifiers = orca_modifier_manager.get_manager().get_orca_modifier_keys()

        def update_grabs() -> bool:
            for cmd in self._keyboard_commands.values():
                if not cmd.is_active():
                    continue
                kb = cmd.get_keybinding()
                if kb is None or not kb.keysymstring.startswith("KP_"):
                    continue

                if self._numlock_on and kb.has_grabs():
                    kb.remove_grabs()
                elif not self._numlock_on and not kb.has_grabs():
                    kb.add_grabs(orca_modifiers)
            return False

        GLib.idle_add(update_grabs)

    def set_up_commands(self) -> None:
        """Sets up commands owned by CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        self.add_command(
            KeyboardCommand(
                "toggle_keyboard_layout",
                self.toggle_keyboard_layout,
                guilabels.KEYBOARD_LAYOUT,
                cmdnames.TOGGLE_KEYBOARD_LAYOUT,
            ),
        )

        msg = "COMMAND MANAGER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

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
            with contextlib.suppress(ValueError):
                self._commands_by_keyval[kb.keyval].remove(cmd)

        if kb.keycode in self._commands_by_keycode:
            with contextlib.suppress(ValueError):
                self._commands_by_keycode[kb.keycode].remove(cmd)

    def add_command(self, command: Command) -> None:
        """Adds a command to the registry and sets its active keybinding."""

        if isinstance(command, KeyboardCommand):
            name = command.get_name()
            old_cmd = self._keyboard_commands.get(name)
            if old_cmd is not None:
                tokens = ["COMMAND MANAGER: Unexpected re-registration of", command]
                debug.print_tokens(debug.LEVEL_WARNING, tokens, True)
                self._remove_from_key_index(old_cmd)

            self._keyboard_commands[name] = command
            command.set_keybinding(command.get_default_keybinding(self._is_desktop))
            self._add_to_key_index(command)

        elif isinstance(command, BrailleCommand):
            self._braille_commands[command.get_name()] = command

    def remove_command(self, command_name: str) -> None:
        """Removes a command from the registry and key indexes."""

        command = self._keyboard_commands.pop(command_name, None)
        if command is not None:
            self._remove_from_key_index(command)
            return

        self._braille_commands.pop(command_name, None)

    def remove_commands(self, command_names: list[str], reason: str = "") -> None:
        """Removes commands from the registry and updates grabs."""

        if not command_names:
            return

        old_bindings = self._get_active_bindings(self._keyboard_commands)
        old_key_to_cmd = self._get_key_to_cmd_mapping(self._keyboard_commands)

        for command_name in command_names:
            self.remove_command(command_name)

        self._diff_and_update_grabs(
            self._keyboard_commands,
            reason,
            old_bindings,
            old_key_to_cmd,
        )

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
        group_label: str,
    ) -> tuple[KeyboardCommand, ...]:
        """Returns all keyboard commands with the specified group label."""

        return tuple(
            cmd for cmd in self._keyboard_commands.values() if cmd.get_group_label() == group_label
        )

    # pylint: disable-next=too-many-locals
    def apply_user_overrides(self) -> None:
        """Applies user-customized keybindings from settings to Commands."""

        # First, reset all keybindings to their layout defaults.
        # This ensures that app-specific unbindings from a previous app
        # don't persist when switching to a different app.
        self._apply_layout_to_commands()

        keybindings_dict = gsettings_registry.get_registry().layered_lookup(
            "keybindings",
            "entries",
            "a{saas}",
            default={},
        )
        if keybindings_dict:
            msg = f"COMMAND MANAGER: Applying {len(keybindings_dict)} user overrides"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "COMMAND MANAGER: No user overrides to apply"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        for command_name, binding_tuples in keybindings_dict.items():
            cmd = self.get_keyboard_command(command_name)
            if cmd is None:
                msg = f"COMMAND MANAGER: Override for unknown command '{command_name}'"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue

            old_kb = cmd.get_keybinding()

            # Empty list means the user explicitly unbound this command
            if binding_tuples == []:
                if old_kb is not None:
                    tokens = ["COMMAND MANAGER: Unbinding", command_name, "(user override)"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    self._remove_from_key_index(cmd)
                    cmd.set_keybinding(None)
                continue

            # Apply the customized binding
            for binding_tuple in binding_tuples:
                keysym, _mask, mods, clicks = binding_tuple
                if not keysym:
                    if old_kb is not None:
                        tokens = ["COMMAND MANAGER: Unbinding", command_name, "(empty keysym)"]
                        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                        self._remove_from_key_index(cmd)
                        cmd.set_keybinding(None)
                else:
                    # Check if the binding actually changed
                    old_key = self._binding_key(old_kb) if old_kb else None
                    new_key = (keysym, int(mods), int(clicks))
                    if old_key == new_key:
                        # Binding unchanged, skip to preserve grabs
                        continue

                    msg = (
                        f"COMMAND MANAGER: Applying override for '{command_name}': "
                        f"{old_key} -> {new_key}"
                    )
                    debug.print_message(debug.LEVEL_INFO, msg, True)

                    self._remove_from_key_index(cmd)
                    kb = keybindings.KeyBinding(keysym, int(mods), click_count=int(clicks))
                    cmd.set_keybinding(kb)
                    self._add_to_key_index(cmd)

    def get_command_for_event(
        self,
        event: input_event.KeyboardEvent,
        active_only: bool = True,
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
            if event.is_keypad_key_with_numlock_on() and kb.keysymstring.startswith("KP_"):
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

    def add_exclusive_groups(self, *group_labels: str) -> None:
        """Registers a set of groups as mutually exclusive."""

        # Groups that are mutually exclusive can share key bindings because
        # only one group in the set is active at a time. The key binding
        # preferences UI will not flag shared bindings as conflicts.
        self._exclusive_groups.append(set(group_labels))

    def are_groups_exclusive(self, group_a: str, group_b: str) -> bool:
        """Returns True if the two groups are mutually exclusive."""

        if group_a == group_b:
            return False
        return any(
            group_a in group_set and group_b in group_set for group_set in self._exclusive_groups
        )

    def is_group_enabled(self, group_label: str) -> bool:
        """Returns the enabled state of the specified command group."""

        stored = self._group_enabled.get(group_label)
        if stored is not None:
            return stored
        for cmd in self._get_keyboard_commands_by_group_label(group_label):
            if not cmd.is_group_toggle():
                return cmd.is_enabled()
        return False

    def set_group_enabled(self, group_label: str, enabled: bool) -> None:
        """Sets the enabled state for all commands in a group."""

        self._group_enabled[group_label] = enabled

        orca_modifiers = orca_modifier_manager.get_manager().get_orca_modifier_keys()
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
                kb.add_grabs(orca_modifiers)
                added_count += 1

        if removed_count or added_count:
            msg = (
                f"COMMAND MANAGER: set_group_enabled({group_label}, {enabled}): "
                f"removed {removed_count}, added {added_count}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_group_suspended(self, group_label: str, suspended: bool) -> None:
        """Sets the suspended state for all commands in a group."""

        orca_modifiers = orca_modifier_manager.get_manager().get_orca_modifier_keys()
        added_count = 0
        removed_count = 0

        for cmd in self._get_keyboard_commands_by_group_label(group_label):
            if cmd.is_group_toggle():
                continue

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
                kb.add_grabs(orca_modifiers)
                added_count += 1

        if removed_count or added_count:
            msg = (
                f"COMMAND MANAGER: set_group_suspended({group_label}, {suspended}): "
                f"removed {removed_count}, added {added_count}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_all_suspended(self, suspended: bool, exceptions: frozenset[str] | None = None) -> None:
        """Sets the suspended state for all commands, optionally excluding exceptions."""

        if suspended:
            self._prior_suspended = {
                cmd.get_name() for cmd in self._keyboard_commands.values() if cmd.is_suspended()
            }

        orca_modifiers = orca_modifier_manager.get_manager().get_orca_modifier_keys()
        added_count = 0
        removed_count = 0

        for cmd in self._keyboard_commands.values():
            if exceptions and cmd.get_name() in exceptions:
                continue

            target_suspended = suspended or cmd.get_name() in self._prior_suspended
            was_active = cmd.is_active()
            cmd.set_suspended(target_suspended)
            is_active = cmd.is_active()

            kb = cmd.get_keybinding()
            if kb is None:
                continue

            if was_active and not is_active and kb.has_grabs():
                kb.remove_grabs()
                removed_count += 1
            elif not was_active and is_active and not kb.has_grabs():
                kb.add_grabs(orca_modifiers)
                added_count += 1

        if not suspended:
            self._prior_suspended = set()

        if removed_count or added_count:
            msg = (
                f"COMMAND MANAGER: set_all_suspended({suspended}): "
                f"removed {removed_count}, added {added_count}"
            )
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
        reason: str = "",
    ) -> None:
        """Updates grabs based on diff between old and new binding maps."""

        orca_modifiers = orca_modifier_manager.get_manager().get_orca_modifier_keys()
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
            elif old_kb.has_grabs():
                old_kb.remove_grabs()
                removed.append(key)

        transferred_keys = set(transferred)
        for key, new_kb in new_bindings.items():
            if key not in transferred_keys and not new_kb.has_grabs():
                if self._is_desktop and self._numlock_on and key[0].startswith("KP_"):
                    continue
                new_kb.add_grabs(orca_modifiers)
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
        commands: dict[str, KeyboardCommand],
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
        commands: dict[str, KeyboardCommand],
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
        old_key_to_cmd: dict[tuple[str, int, int], str] | None = None,
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

    @gsettings_registry.get_registry().gsetting(
        key="entries",
        schema="keybindings",
        gtype="a{saas}",
        default={},
        summary="User keybinding overrides",
    )
    def get_keybinding_overrides(self) -> dict:
        """Returns the user's keybinding overrides."""

        return gsettings_registry.get_registry().layered_lookup(
            "keybindings",
            "entries",
            "a{saas}",
            default={},
        )

    def _keybinding_in_use(self, keysym: str, modifiers: int, click_count: int = 1) -> bool:
        """Returns True if an active command is already bound to keysym+modifiers."""

        for cmd in self._keyboard_commands.values():
            binding = cmd.get_keybinding()
            if (
                binding is not None
                and binding.keysymstring == keysym
                and binding.modifiers == modifiers
                and binding.click_count == click_count
            ):
                return True
        return False

    @dbus_service.testing_command
    def get_available_keybindings_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        count: int = 1,
        script: default.Script | None = None,  # pylint: disable=unused-argument
        event: input_event.InputEvent | None = None,  # pylint: disable=unused-argument
    ) -> list[tuple[str, int]]:
        """Returns up to count currently-unbound Orca-modified keybindings (test-only)."""

        # Gated by a launch secret; never call from production code. Each result is
        # (keysym, modifiers) for a combo no active command uses, so a test can bind to it
        # without colliding with a real shortcut even as default bindings change.
        modifiers = keybindings.ORCA_MODIFIER_MASK
        candidates = [chr(c) for c in range(ord("a"), ord("z") + 1)]
        candidates += [str(digit) for digit in range(10)]
        available: list[tuple[str, int]] = []
        for keysym in candidates:
            if len(available) >= count:
                break
            if not self._keybinding_in_use(keysym, modifiers):
                available.append((keysym, modifiers))
        return available

    @dbus_service.testing_command
    def bind_command_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        command_name: str = "",
        keysym: str = "",
        modifiers: int = 0,
        script: default.Script | None = None,  # pylint: disable=unused-argument
        event: input_event.InputEvent | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """Writes a keybinding override for command_name (test-only)."""

        # Gated by a launch secret; never call from production code. Does not refresh grabs;
        # call refresh_keybindings_for_testing afterwards so the change takes effect.
        kb = keybindings.KeyBinding(keysym, modifiers)
        binding_data = [
            kb.keysymstring,
            str(kb.modifier_mask),
            str(kb.modifiers),
            str(kb.click_count),
        ]
        overrides = self.get_keybinding_overrides()
        overrides[command_name] = [binding_data]
        gsettings_registry.get_registry().set_runtime_value("keybindings", "entries", overrides)
        return True

    @dbus_service.testing_command
    def unbind_command_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        command_name: str = "",
        script: default.Script | None = None,  # pylint: disable=unused-argument
        event: input_event.InputEvent | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """Removes the keybinding override for command_name (test-only)."""

        # Gated by a launch secret; never call from production code. Does not refresh grabs;
        # call refresh_keybindings_for_testing afterwards.
        overrides = self.get_keybinding_overrides()
        overrides.pop(command_name, None)
        gsettings_registry.get_registry().set_runtime_value("keybindings", "entries", overrides)
        return True

    @dbus_service.testing_command
    def refresh_keybindings_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        script: default.Script | None = None,  # pylint: disable=unused-argument
        event: input_event.InputEvent | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """Re-applies keybinding overrides and refreshes grabs (test-only)."""

        # Gated by a launch secret; never call from production code.
        get_manager().activate_commands("test rebind")
        return True

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def register_command(
        self,
        name: str,
        function: Callable[..., bool],
        description: str = "",
        key: str = "",
        modifiers: int = 0,
        click_count: int = 1,
        group_label: str = "",
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
            laptop_keybinding=kb,
        )
        self.add_command(cmd)
        return cmd

    def create_preferences_grid(
        self,
        script: default.Script,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> KeybindingsPreferencesGrid:
        """Returns the GtkGrid containing the keybindings preferences UI."""

        # pylint: disable-next=import-outside-toplevel
        from .command_manager_preferences_grid import KeybindingsPreferencesGrid

        return KeybindingsPreferencesGrid(script, title_change_callback)


_manager: CommandManager = CommandManager()


def get_manager() -> CommandManager:
    """Returns the CommandManager singleton."""
    return _manager
