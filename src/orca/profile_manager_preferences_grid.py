# Orca
#
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

"""Preferences grid for Orca profile management."""

from __future__ import annotations

import time
import unicodedata
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # pylint: disable=no-name-in-module

from . import debug, gsettings_registry, guilabels, preferences_grid_base

if TYPE_CHECKING:
    from collections.abc import Callable

    from .profile_manager import ProfileManager


class ProfilePreferencesGrid(  # pylint: disable=too-many-instance-attributes
    preferences_grid_base.PreferencesGridBase,
):
    """GtkGrid containing the Profile management preferences page."""

    # pylint: disable=no-member

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for profile preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title="Profiles",
            panel_id="manual.profiles",
            summary="Use these settings to create, switch, rename, and remove Orca settings "
            "profiles.",
            description=guilabels.PROFILES_INFO,
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.CURRENT_PROFILE,
                    kind="list",
                    summary="Lists the profiles you can select to use or modify.",
                    dynamic_values=True,
                    actions=(
                        preferences_grid_base.PreferenceActionDoc(
                            label=guilabels.PROFILE_CREATE_NEW,
                            summary="Creates a new profile by copying the current profile's "
                            "settings.",
                            placement="header",
                        ),
                    ),
                    item_actions=(
                        preferences_grid_base.PreferenceActionDoc(
                            label="Rename Profile",
                            summary="Renames the selected profile.",
                        ),
                        preferences_grid_base.PreferenceActionDoc(
                            label="Remove Profile",
                            summary="Removes the selected profile.",
                        ),
                    ),
                ),
            ),
        )

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        manager: ProfileManager,
        profile_loaded_callback: Callable[[list[str]], None],
        is_app_specific: bool = False,
        labels_update_callback: Callable[[], None] | None = None,
        unsaved_changes_checker: Callable[[], bool] | None = None,
    ) -> None:
        super().__init__(guilabels.GENERAL_PROFILES)
        self.set_margin_start(0)
        self.set_margin_end(0)
        self.set_margin_top(0)
        self.set_margin_bottom(0)
        self.set_border_width(0)

        self._manager: ProfileManager = manager
        self._profile_loaded_callback = profile_loaded_callback
        self._is_app_specific: bool = is_app_specific
        self._labels_update_callback = labels_update_callback
        self._unsaved_changes_checker = unsaved_changes_checker
        self._initializing: bool = True
        self._default_profile: list[str] = [guilabels.PROFILE_DEFAULT, "default"]
        self._auto_grid: preferences_grid_base.AutoPreferencesGrid | None = None
        self._pending_renames: dict[str, list[str]] = {}

        self._build()
        self.refresh()
        self._initializing = False

    def _build(self) -> None:
        available_profiles = self._get_available_profiles()
        profile_labels = [p[0] for p in available_profiles]
        profile_values = [p[1] for p in available_profiles]

        controls = [
            preferences_grid_base.SelectionPreferenceControl(
                label=guilabels.CURRENT_PROFILE,
                options=profile_labels,
                getter=self._get_active_profile,
                setter=self._set_active_profile,
                values=profile_values,
                member_of=guilabels.CURRENT_PROFILE,
                get_actions_for_option=None if self._is_app_specific else self._get_profile_actions,
                tracks_changes=False,
            ),
        ]

        self._auto_grid = preferences_grid_base.AutoPreferencesGrid(
            tab_label="",
            controls=controls,
            info_message=guilabels.PROFILES_INFO,
        )
        self.attach(self._auto_grid, 0, 0, 1, 1)

        if not self._is_app_specific:
            self._auto_grid.add_button_to_group_header(
                guilabels.CURRENT_PROFILE,
                "list-add-symbolic",
                self._on_new_profile_clicked,
                guilabels.PROFILE_CREATE_NEW.replace("_", ""),
            )

    def _on_new_profile_clicked(self, _button: Gtk.Button) -> None:
        """Handle New Profile button click."""

        if self._unsaved_changes_checker and self._unsaved_changes_checker():
            dialog = Gtk.MessageDialog(
                transient_for=self.get_toplevel(),
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text=guilabels.PROFILE_CREATE_UNSAVED_WARNING,
            )
            response = dialog.run()
            dialog.destroy()
            if response != Gtk.ResponseType.YES:
                return

        new_profile = self.get_new_profile_name()
        if new_profile is None:
            return

        if not self._manager.create_profile(new_profile):
            self._show_error_dialog(guilabels.PROFILE_CONFLICT_MESSAGE % new_profile[0])
            return

        self._manager.load_profile(new_profile[1])
        self._rebuild_ui()
        self._profile_loaded_callback(new_profile)

    def _get_available_profiles(self) -> list[list[str]]:
        """Get list of available profiles, including any pending renames."""

        profiles = self._manager.get_available_profiles()
        if not profiles or len(profiles) == 0:
            return [self._default_profile]

        result = []
        for profile in profiles:
            if profile is None:
                continue
            internal_name = profile[1]
            if internal_name in self._pending_renames:
                result.append(self._pending_renames[internal_name])
            elif internal_name == "default":
                result.append(self._default_profile)
            else:
                result.append(profile)
        return result or [self._default_profile]

    def _get_active_profile(self) -> str:
        return self._manager.get_active_profile()

    def get_profile_label(self, internal_name: str) -> str:
        """Get the display label for a profile by its internal name."""

        if internal_name in self._pending_renames:
            return self._pending_renames[internal_name][0]

        if internal_name == "default":
            return self._default_profile[0]

        for profile in self._manager.get_available_profiles():
            if profile is not None and profile[1] == internal_name:
                return profile[0]
        return internal_name

    def get_current_profile_label(self) -> str:
        """Get the display label for the current profile, including pending renames."""

        return self.get_profile_label(self._manager.get_active_profile())

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

    def _get_profile_actions(self, internal_name: str) -> list[tuple[str, str, Callable[[], None]]]:
        """Get the list of actions (label, icon_name, callback) for a profile."""

        if internal_name == "default":
            return []

        return [
            (
                guilabels.MENU_RENAME,
                "document-edit-symbolic",
                lambda: self._on_rename_profile(internal_name),
            ),
            (
                guilabels.MENU_REMOVE_PROFILE,
                "user-trash-symbolic",
                lambda: self._on_remove_profile(internal_name),
            ),
        ]

    @staticmethod
    def _sanitize_profile_label(name: str) -> str:
        """Strip control characters and surrounding whitespace from a profile label."""

        return "".join(c for c in name if unicodedata.category(c)[0] != "C").strip()

    def _validate_profile_name(
        self,
        name: str,
        exclude_internal_name: str | None = None,
    ) -> tuple[bool, str]:
        """Validate a profile name and return (is_valid, error_message)."""

        registry = gsettings_registry.get_registry()
        internal_name = registry.sanitize_gsettings_path(name)
        if not internal_name:
            return (False, guilabels.PROFILE_CONFLICT_MESSAGE % name)

        saved_profiles = self._manager.get_available_profiles()

        for profile in saved_profiles:
            if exclude_internal_name and profile[1] == exclude_internal_name:
                continue
            if registry.sanitize_gsettings_path(profile[1]) == internal_name:
                return (False, guilabels.PROFILE_CONFLICT_MESSAGE % name)

        for old_name, new_profile in self._pending_renames.items():
            if exclude_internal_name and old_name == exclude_internal_name:
                continue
            if registry.sanitize_gsettings_path(new_profile[1]) == internal_name:
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
            guilabels.PROFILE_REMOVE_LABEL,
            guilabels.PROFILE_REMOVE_MESSAGE % profile[0],
        ):
            return

        self._manager.remove_profile(internal_name)

        active_profile_name = self._manager.get_active_profile()
        if active_profile_name == internal_name:
            self._manager.set_active_profile(self._default_profile[1])
            self._profile_loaded_callback(self._default_profile)

        self._rebuild_ui()

    def _on_rename_profile(self, internal_name: str) -> None:
        profile = None
        for p in self._get_available_profiles():
            if p[1] == internal_name:
                profile = p
                break

        if profile is None:
            return

        dialog, ok_button = self._create_header_bar_dialog(
            guilabels.MENU_RENAME,
            guilabels.DIALOG_CANCEL,
            guilabels.DIALOG_APPLY,
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
        entry.set_text(profile[0])
        entry.set_hexpand(True)
        entry.set_activates_default(True)
        entry.connect(
            "changed",
            lambda e: ok_button.set_sensitive(bool(self._sanitize_profile_label(e.get_text()))),
        )
        label.set_mnemonic_widget(entry)
        hbox.pack_start(entry, True, True, 0)

        content_area.pack_start(hbox, False, False, 0)

        dialog.show_all()
        ok_button.grab_default()
        entry.set_position(-1)
        entry.grab_focus()

        response = dialog.run()
        new_name = self._sanitize_profile_label(entry.get_text())
        dialog.destroy()

        if response != Gtk.ResponseType.OK or not new_name:
            return

        is_valid, error_msg = self._validate_profile_name(
            new_name,
            exclude_internal_name=internal_name,
        )
        if not is_valid:
            self._show_error_dialog(error_msg)
            return

        # Stage the rename - don't write to disk yet
        new_profile = [new_name, internal_name]
        self._pending_renames[internal_name] = new_profile
        self._has_unsaved_changes = True

        self._rebuild_ui()

        if self._labels_update_callback:
            self._labels_update_callback()

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
        entry.connect(
            "changed",
            lambda e: ok_button.set_sensitive(bool(self._sanitize_profile_label(e.get_text()))),
        )
        label.set_mnemonic_widget(entry)
        hbox.pack_start(entry, True, True, 0)

        content_area.pack_start(hbox, False, False, 0)

        ok_button.set_sensitive(False)
        dialog.show_all()
        ok_button.grab_default()
        entry.grab_focus()

        response = dialog.run()
        new_name = self._sanitize_profile_label(entry.get_text())
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

    def save_settings(self, _profile: str = "", _app_name: str = "") -> dict:
        """Save settings and return a dictionary of the current values for those settings."""

        result = {}

        if self._pending_renames:
            self._apply_pending_renames()

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

    def set_focus_sidebar_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback to focus the sidebar navigation list."""

        super().set_focus_sidebar_callback(callback)
        if self._auto_grid:
            self._auto_grid.set_focus_sidebar_callback(callback)

    def _apply_pending_renames(self) -> None:
        """Apply all pending profile renames."""

        active_profile_name = self._manager.get_active_profile()

        for old_internal_name, pending_profile in self._pending_renames.items():
            new_name = pending_profile[0]
            new_internal_name = gsettings_registry.get_registry().sanitize_gsettings_path(new_name)
            new_profile = [new_name, new_internal_name]

            self._manager.rename_profile(old_internal_name, new_profile)

            if active_profile_name == old_internal_name:
                self._manager.set_active_profile(new_internal_name)
                active_profile_name = new_internal_name

        self._pending_renames.clear()

    def refresh(self) -> None:
        """Update UI to reflect current profiles and settings."""

        self._initializing = True
        if self._auto_grid:
            self._auto_grid.refresh()
        self._initializing = False
