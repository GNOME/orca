# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements

"""Manager for Orca profile creation, loading, and management."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2026 Igalia, S.L."
__license__   = "LGPL"

import time
from typing import Callable, TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from . import braille
from . import cmdnames
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import orca
from . import preferences_grid_base
from . import settings_manager
from . import speech_and_verbosity_manager

if TYPE_CHECKING:
    from .scripts import default


class ProfilePreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Profile management preferences page."""

    def __init__(
        self,
        manager: ProfileManager,
        profile_loaded_callback: Callable[[list[str]], None],
        is_app_specific: bool = False,
    ) -> None:
        super().__init__(guilabels.GENERAL_PROFILES)
        # Clear margins - the embedded AutoPreferencesGrid provides them
        self.set_margin_start(0)
        self.set_margin_end(0)
        self.set_margin_top(0)
        self.set_margin_bottom(0)
        self.set_border_width(0)

        self._manager: ProfileManager = manager
        self._profile_loaded_callback = profile_loaded_callback
        self._is_app_specific: bool = is_app_specific
        self._initializing: bool = True
        self._default_profile: list[str] = [guilabels.PROFILE_DEFAULT, "default"]
        self._auto_grid: preferences_grid_base.AutoPreferencesGrid | None = None
        self._pending_renames: dict[
            str, list[str]
        ] = {}  # old_internal_name -> [new_name, new_internal_name]

        self._build()
        self.refresh()
        self._initializing = False

    def _build(self) -> None:
        row = 0

        available_profiles = self._get_available_profiles()
        profile_labels = [p[0] for p in available_profiles]
        profile_values = [p[1] for p in available_profiles]

        # For app-specific preferences, disable changing the global startup profile
        # but allow switching active profile (to edit app settings for different profiles)
        starting_profile_setter = None if self._is_app_specific else self._set_starting_profile
        startup_sensitivity = (lambda: False) if self._is_app_specific else None

        controls = [
            preferences_grid_base.SelectionPreferenceControl(
                label=guilabels.GENERAL_START_UP_PROFILE,
                options=profile_labels,
                getter=self._get_starting_profile,
                setter=starting_profile_setter,
                values=profile_values,
                prefs_key="startingProfile",
                get_actions_for_option=None,
                determine_sensitivity=startup_sensitivity,
            ),
            preferences_grid_base.SelectionPreferenceControl(
                label=guilabels.GENERAL_PROFILES,
                options=profile_labels,
                getter=self._get_active_profile,
                setter=self._set_active_profile,
                values=profile_values,
                prefs_key="activeProfile",
                member_of=guilabels.GENERAL_PROFILES,
                get_actions_for_option=None if self._is_app_specific else self._get_profile_actions,
                apply_immediately=True,
            ),
        ]

        self._auto_grid = preferences_grid_base.AutoPreferencesGrid(tab_label="", controls=controls)
        self.attach(self._auto_grid, 0, row, 1, 1)

    def _get_available_profiles(self) -> list[list[str]]:
        """Get list of available profiles, including any pending renames."""

        profiles = self._manager.get_available_profiles()
        if not profiles or len(profiles) == 0:
            return [self._default_profile]

        result = []
        for profile in profiles:
            internal_name = profile[1]
            if internal_name in self._pending_renames:
                result.append(self._pending_renames[internal_name])
            else:
                result.append(profile)
        return result

    def _get_active_profile(self) -> str:
        return self._manager.get_active_profile()

    def _set_active_profile(self, internal_name: str) -> None:
        if self._initializing:
            return

        profile = None
        for p in self._get_available_profiles():
            if p[1] == internal_name:
                profile = p
                break

        if profile is None:
            return

        def do_load_profile():
            try:
                self._manager.load_profile(internal_name)
                self._profile_loaded_callback(profile)
            except (KeyError, FileNotFoundError) as error:
                tokens = ["PROFILE MANAGER: Failed to load profile", internal_name, error]
                debug.print_tokens(debug.LEVEL_SEVERE, tokens, True)
                self.reload()
            return False

        GLib.idle_add(do_load_profile)

    def _get_starting_profile(self) -> str:
        """Get the starting profile's internal name."""

        starting_profile = self._manager.get_starting_profile()
        return starting_profile[1]  # internal name

    def _set_starting_profile(self, internal_name: str) -> None:
        """Set the starting profile by internal name."""

        if self._initializing:
            return

        for profile in self._get_available_profiles():
            if profile[1] == internal_name:
                self._manager.set_starting_profile(profile)
                break

    def _get_profile_actions(self, internal_name: str) -> list[tuple[str, str, Callable[[], None]]]:
        """Get the list of actions (label, icon_name, callback) for a profile."""

        if internal_name == "default":
            return []

        return [
            (
                guilabels.MENU_REMOVE_PROFILE,
                "user-trash-symbolic",
                lambda: self._on_remove_profile(internal_name),
            ),
            (
                guilabels.MENU_RENAME,
                "document-edit-symbolic",
                lambda: self._on_rename_profile(internal_name),
            ),
        ]

    def _validate_profile_name(
        self, name: str, exclude_internal_name: str | None = None
    ) -> tuple[bool, str]:
        """Validate a profile name and return (is_valid, error_message)."""

        internal_name = name.replace(" ", "_").lower()

        saved_profiles = self._manager.get_available_profiles()

        for profile in saved_profiles:
            if exclude_internal_name and profile[1] == exclude_internal_name:
                continue
            if profile[1].lower() == internal_name:
                return (False, guilabels.PROFILE_CONFLICT_MESSAGE % name)

        for old_name, new_profile in self._pending_renames.items():
            if exclude_internal_name and old_name == exclude_internal_name:
                continue
            if new_profile[1].lower() == internal_name:
                return (False, guilabels.PROFILE_CONFLICT_MESSAGE % name)

        return (True, "")

    def _show_error_dialog(self, message: str) -> None:
        """Show an error dialog to the user."""

        parent = self.get_toplevel()
        dialog = Gtk.MessageDialog(
            transient_for=parent if parent.is_toplevel() else None,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.present_with_time(time.time())
        dialog.run()
        dialog.destroy()

    def _show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a confirmation dialog and return True if user clicked Yes."""

        parent = self.get_toplevel()
        dialog = Gtk.MessageDialog(
            transient_for=parent if parent.is_toplevel() else None,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.present_with_time(time.time())
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def _on_remove_profile(self, internal_name: str) -> None:
        """Handle Remove Profile action from three-dot menu."""

        profile = None
        for p in self._get_available_profiles():
            if p[1] == internal_name:
                profile = p
                break

        if profile is None:
            return

        if not self._show_confirmation_dialog(
            guilabels.PROFILE_REMOVE_LABEL, guilabels.PROFILE_REMOVE_MESSAGE % profile[0]
        ):
            return

        self._manager.remove_profile(internal_name)

        active_profile_name = self._manager.get_active_profile()
        starting_profile = self._manager.get_starting_profile()

        if starting_profile[1] == internal_name:
            self._manager.set_starting_profile(self._default_profile)

        if active_profile_name == internal_name:
            self._manager.set_active_profile(self._default_profile[1])
            self._profile_loaded_callback(self._default_profile)
        else:
            self.reload()

    def _on_rename_profile(self, internal_name: str) -> None:
        profile = None
        for p in self._get_available_profiles():
            if p[1] == internal_name:
                profile = p
                break

        if profile is None:
            return

        dialog, ok_button = self._create_header_bar_dialog(
            guilabels.MENU_RENAME, guilabels.DIALOG_CANCEL, guilabels.DIALOG_APPLY, width=400
        )

        content_area = dialog.get_content_area()
        content_area.set_spacing(12)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)
        hbox.set_margin_top(12)
        hbox.set_margin_bottom(12)

        label = Gtk.Label(label=guilabels.PROFILE_NAME_LABEL, xalign=0)
        label.set_use_underline(True)
        hbox.pack_start(label, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(profile[0])
        entry.set_hexpand(True)
        entry.set_activates_default(True)
        entry.connect("changed", lambda e: ok_button.set_sensitive(bool(e.get_text().strip())))
        label.set_mnemonic_widget(entry)
        hbox.pack_start(entry, True, True, 0)

        content_area.pack_start(hbox, False, False, 0)

        dialog.show_all()
        ok_button.grab_default()
        entry.set_position(-1)
        entry.grab_focus()

        response = dialog.run()
        new_name = entry.get_text().strip()
        dialog.destroy()

        if response != Gtk.ResponseType.OK or not new_name:
            return

        is_valid, error_msg = self._validate_profile_name(
            new_name, exclude_internal_name=internal_name
        )
        if not is_valid:
            self._show_error_dialog(error_msg)
            return

        # Stage the rename - don't write to disk yet
        new_profile = [new_name, internal_name]
        self._pending_renames[internal_name] = new_profile
        self._has_unsaved_changes = True

        self._rebuild_ui()

    def get_new_profile_name(self) -> list[str] | None:
        """Show dialog to get a new profile name. Returns [label, name] or None if cancelled."""

        dialog, ok_button = self._create_header_bar_dialog(
            guilabels.PROFILE_SAVE_AS_TITLE,
            guilabels.DIALOG_CANCEL,
            guilabels.DIALOG_ADD,
            width=400,
        )

        content_area = dialog.get_content_area()
        content_area.set_spacing(12)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)
        hbox.set_margin_top(12)
        hbox.set_margin_bottom(12)

        label = Gtk.Label(label=guilabels.PROFILE_NAME_LABEL, xalign=0)
        label.set_use_underline(True)
        hbox.pack_start(label, False, False, 0)

        entry = Gtk.Entry()
        entry.set_hexpand(True)
        entry.set_activates_default(True)
        entry.connect("changed", lambda e: ok_button.set_sensitive(bool(e.get_text().strip())))
        label.set_mnemonic_widget(entry)
        hbox.pack_start(entry, True, True, 0)

        content_area.pack_start(hbox, False, False, 0)

        ok_button.set_sensitive(False)
        dialog.show_all()
        ok_button.grab_default()
        entry.grab_focus()

        response = dialog.run()
        new_name = entry.get_text().strip()
        dialog.destroy()

        if response != Gtk.ResponseType.OK or not new_name:
            return None

        is_valid, error_msg = self._validate_profile_name(new_name)
        if not is_valid:
            self._show_error_dialog(error_msg)
            return None

        internal_name = new_name.replace(" ", "_").lower()
        return [new_name, internal_name]

    def _rebuild_ui(self) -> None:
        """Rebuild the UI without discarding pending changes."""

        if self._auto_grid:
            self.remove(self._auto_grid)
            self._auto_grid.destroy()
            self._auto_grid = None

        self._build()
        self.show_all()

    def reload(self) -> None:
        """Reload settings from the settings_manager and refresh the UI."""

        self._pending_renames.clear()
        self._rebuild_ui()

    def save_settings(self) -> dict:
        """Save settings and return a dictionary of the current values for those settings."""

        result = {}

        if self._pending_renames:
            result.update(self._apply_pending_renames())

        if self._auto_grid:
            result.update(self._auto_grid.save_settings())

        return result

    def has_changes(self) -> bool:
        """Return True if the user has made changes that haven't been written to file."""

        if self._pending_renames:
            return True

        if self._auto_grid:
            return self._auto_grid.has_changes()
        return False

    def _apply_pending_renames(self) -> dict:
        """Apply all pending profile renames and return updated settings."""

        result = {}

        active_profile_name = self._manager.get_active_profile()
        starting_profile = self._manager.get_starting_profile()

        for old_internal_name, pending_profile in self._pending_renames.items():
            new_name = pending_profile[0]
            new_internal_name = new_name.replace(" ", "_").lower()
            new_profile = [new_name, new_internal_name]

            self._manager.rename_profile(old_internal_name, new_profile)

            if starting_profile[1] == old_internal_name:
                self._manager.set_starting_profile(new_profile)
                result["startingProfile"] = new_profile

            if active_profile_name == old_internal_name:
                self._manager.set_active_profile(new_internal_name)
                result["activeProfile"] = new_profile
                active_profile_name = new_internal_name

        self._pending_renames.clear()

        return result

    def refresh(self) -> None:
        """Update UI to reflect current profiles and settings."""

        self._initializing = True
        if self._auto_grid:
            self._auto_grid.refresh()
        self._initializing = False


class ProfileManager:
    """Manager for Orca profiles."""

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()

        msg = "PROFILE MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("ProfileManager", self)

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the profile manager handlers."""

        if refresh:
            msg = "PROFILE MANAGER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the profile manager input event handlers."""

        self._handlers = {}

        self._handlers["cycleSettingsProfileHandler"] = \
            input_event.InputEventHandler(
                self.cycle_settings_profile,
                cmdnames.CYCLE_SETTINGS_PROFILE)

        self._handlers["presentCurrentProfileHandler"] = \
            input_event.InputEventHandler(
                self.present_current_profile,
                cmdnames.PRESENT_CURRENT_PROFILE)

        msg = "PROFILE MANAGER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the profile manager keybindings."""

        if refresh:
            msg = f"PROFILE MANAGER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("PROFILE MANAGER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def _setup_bindings(self) -> None:
        """Sets up the profile manager key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.NO_MODIFIER_MASK,
                self._handlers["cycleSettingsProfileHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.NO_MODIFIER_MASK,
                self._handlers["presentCurrentProfileHandler"]))

        msg = "PROFILE MANAGER: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.getter
    def get_available_profiles(self) -> list[list[str]]:
        """Returns list of available profiles as [display_name, internal_name] pairs."""

        return settings_manager.get_manager().available_profiles()

    @dbus_service.getter
    def get_active_profile(self) -> str:
        """Returns the internal name of the currently active profile."""

        return settings_manager.get_manager().get_profile()

    @dbus_service.setter
    def set_active_profile(self, internal_name: str, update_locale: bool = False) -> bool:
        """Sets the active profile by internal name."""

        settings_manager.get_manager().set_profile(internal_name, update_locale)
        return True

    def load_profile(self, internal_name: str, update_locale: bool = False) -> None:
        """Loads a profile by setting it active and reloading user settings."""

        msg = f"PROFILE MANAGER: Loading profile '{internal_name}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.set_active_profile(internal_name, update_locale)
        orca.load_user_settings(skip_reload_message=True)

    @dbus_service.getter
    def get_starting_profile(self) -> list[str]:
        """Returns the starting profile as [display_name, internal_name]."""

        prefs = settings_manager.get_manager().get_general_settings()
        return prefs.get("startingProfile", ["Default", "default"])

    @dbus_service.setter
    def set_starting_profile(self, profile: list[str]) -> bool:
        """Sets the starting profile."""

        settings_manager.get_manager().set_starting_profile(profile)
        return True

    def remove_profile(self, internal_name: str) -> None:
        """Removes a profile by internal name."""

        settings_manager.get_manager().remove_profile(internal_name)

    def rename_profile(self, old_internal_name: str, new_profile: list[str]) -> None:
        """Renames a profile."""

        settings_manager.get_manager().rename_profile(old_internal_name, new_profile)

    @dbus_service.command
    def cycle_settings_profile(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Cycle through the user's existing settings profiles."""

        tokens = ["PROFILE MANAGER: cycle_settings_profile. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        profile_names = self.get_available_profiles()
        if not profile_names:
            if script is not None and notify_user:
                script.present_message(messages.PROFILE_NOT_FOUND)
            return True

        profiles = [(profile[0], profile[1]) for profile in profile_names]
        current_profile = self.get_active_profile()

        current_index = 0
        for i, (_, internal_name) in enumerate(profiles):
            if internal_name == current_profile:
                current_index = i
                break

        try:
            name, profile_id = profiles[current_index + 1]
        except IndexError:
            name, profile_id = profiles[0]

        self.set_active_profile(profile_id, update_locale=True)

        braille.checkBrailleSetting()
        speech_and_verbosity_manager.get_manager().refresh_speech()

        if script is not None:
            script.setup_input_event_handlers()
            if notify_user:
                script.present_message(messages.PROFILE_CHANGED % name, name)

        return True

    @dbus_service.command
    def present_current_profile(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Present the name of the currently active profile."""

        tokens = ["PROFILE MANAGER: present_current_profile. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        profile_names = self.get_available_profiles()
        current_profile_id = self.get_active_profile()

        name = current_profile_id
        for display_name, internal_name in profile_names:
            if internal_name == current_profile_id:
                name = display_name
                break

        if script is not None and notify_user:
            script.present_message(messages.PROFILE_CURRENT % name, name)

        return True

    def create_preferences_grid(
        self, profile_loaded_callback: Callable[[list[str]], None], is_app_specific: bool = False
    ) -> ProfilePreferencesGrid:
        """Returns the GtkGrid containing the profile management UI."""

        return ProfilePreferencesGrid(self, profile_loaded_callback, is_app_specific)


_manager = ProfileManager()


def get_manager() -> ProfileManager:
    """Returns the profile-manager singleton."""

    return _manager
