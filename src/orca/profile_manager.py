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

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Manager for Orca profile creation, loading, and management."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from . import (
    command_manager,
    dbus_service,
    debug,
    gsettings_registry,
    guilabels,
    input_event,
    messages,
    orca,
    orca_modifier_manager,
    presentation_manager,
    profile_manager_command_definitions,
)
from .extension import Extension

if TYPE_CHECKING:
    from collections.abc import Callable

    from .command import Command
    from .profile_manager_preferences_grid import ProfilePreferencesGrid
    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.ProfileMetadata",
    name="metadata",
)
class ProfileManager(Extension):
    """Manager for Orca profiles."""

    GROUP_LABEL = guilabels.GENERAL_PROFILES

    @gsettings_registry.get_registry().gsetting(
        key="display-name",
        schema="metadata",
        gtype="s",
        default="",
        summary="Original display name (label) of the profile or app",
    )
    def get_display_name(self) -> str:
        """Returns the display name for the active profile."""

        return gsettings_registry.get_registry().get_active_profile()

    @gsettings_registry.get_registry().gsetting(
        key="internal-name",
        schema="metadata",
        gtype="s",
        default="",
        summary="Original internal name (JSON dict key) of the profile",
    )
    def get_internal_name(self) -> str:
        """Returns the internal name for the active profile."""

        return gsettings_registry.get_registry().get_active_profile()

    def _get_commands(self) -> list[Command]:
        """Returns commands for registration."""

        return profile_manager_command_definitions.get_commands(self)

    @dbus_service.getter
    def get_available_profiles(self) -> list[list[str]]:
        """Returns list of available profiles as [display_name, internal_name] pairs."""

        profiles = self._get_stored_profiles(gsettings_registry.get_registry())
        for profile in profiles:
            if profile[1] == "default":
                profile[0] = guilabels.PROFILE_DEFAULT
                break
        return profiles

    @staticmethod
    def _get_stored_profiles(
        registry: gsettings_registry.GSettingsRegistry,
    ) -> list[list[str]]:
        """Returns available profiles by enumerating stored metadata."""

        try:
            result = subprocess.run(  # noqa: S603
                ["dconf", "list", gsettings_registry.GSETTINGS_PATH_PREFIX],  # noqa: S607
                capture_output=True,
                text=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return [["Default", "default"]]

        default_profile: list[str] | None = None
        profiles: list[list[str]] = []
        for entry in result.stdout.strip().split("\n"):
            if not entry.endswith("/"):
                continue
            sanitized_name = entry.rstrip("/")
            gs = registry.get_settings("metadata", sanitized_name)
            if gs is None:
                continue
            display_variant = gs.get_user_value("display-name")
            internal_variant = gs.get_user_value("internal-name")
            if display_variant is None or internal_variant is None:
                continue
            display_name = display_variant.get_string()
            internal_name = internal_variant.get_string()
            profile = [display_name, internal_name]
            if internal_name == "default":
                default_profile = profile
            else:
                profiles.append(profile)

        if default_profile is not None:
            profiles.insert(0, default_profile)
        elif not profiles:
            profiles.append(["Default", "default"])
        return profiles

    @dbus_service.getter
    def get_active_profile(self) -> str:
        """Returns the internal name of the currently active profile."""

        return gsettings_registry.get_registry().get_active_profile()

    @dbus_service.setter
    def set_active_profile(self, internal_name: str) -> bool:
        """Sets the active profile by internal name."""

        registry = gsettings_registry.get_registry()
        registry.clear_runtime_values()
        registry.set_active_profile(internal_name)
        return True

    def load_profile(self, internal_name: str) -> None:
        """Loads a profile by setting it active and reloading user settings."""

        msg = f"PROFILE MANAGER: Loading profile '{internal_name}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.set_active_profile(internal_name)
        orca.load_user_settings(skip_reload_message=True)

    def create_profile(self, new_profile: list[str]) -> bool:
        """Create a new profile by copying the current active profile to dconf."""

        current_profile = self.get_active_profile()
        msg = f"PROFILE MANAGER: Creating profile '{new_profile[1]}' from '{current_profile}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        registry = gsettings_registry.get_registry()
        old_profile = registry.sanitize_gsettings_path(current_profile)
        new_name = registry.sanitize_gsettings_path(new_profile[1])

        for schema_name in registry.get_schema_names():
            if schema_name == "voice":
                for voice_type in gsettings_registry.VOICE_TYPES:
                    sub = gsettings_registry.get_registry().voice_set_sub_path(voice_type)
                    old_gs = registry.get_settings("voice", old_profile, sub)
                    new_gs = registry.get_settings("voice", new_name, sub)
                    registry.copy_user_keys(old_gs, new_gs)
                continue
            old_gs = registry.get_settings(schema_name, old_profile)
            new_gs = registry.get_settings(schema_name, new_name)
            registry.copy_user_keys(old_gs, new_gs)

        metadata_gs = registry.get_settings("metadata", new_name)
        if metadata_gs is not None:
            metadata_gs.set_string("display-name", new_profile[0])
            metadata_gs.set_string("internal-name", new_profile[1])

        return True

    @dbus_service.getter
    def get_starting_profile(self) -> list[str]:
        """Returns the starting profile (always Default)."""

        return ["Default", "default"]

    @dbus_service.setter
    def set_starting_profile(self, _profile: list[str]) -> bool:
        """No-op for backwards compatibility. Starting profile is always Default."""

        return True

    def remove_profile(self, internal_name: str) -> None:
        """Removes a profile by internal name."""

        registry = gsettings_registry.get_registry()
        sanitized_name = registry.sanitize_gsettings_path(internal_name)
        path = f"{gsettings_registry.GSETTINGS_PATH_PREFIX}{sanitized_name}/"
        try:
            subprocess.run(  # noqa: S603 - dconf is a system dependency, not untrusted input
                ["dconf", "reset", "-f", path],  # noqa: S607 - full path would break across distros
                check=True,
            )
            msg = f"PROFILE MANAGER: Cleared GSettings for profile: {internal_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            msg = f"PROFILE MANAGER: Failed to clear GSettings for profile: {internal_name}: {e}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def rename_profile(self, old_internal_name: str, new_profile: list[str]) -> None:
        """Renames a profile."""

        gsettings_registry.get_registry().rename_profile(
            old_internal_name,
            new_profile[0],
            new_profile[1],
        )

    @dbus_service.command
    def cycle_settings_profile(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycle through the user's existing settings profiles."""

        tokens = [
            "PROFILE MANAGER: cycle_settings_profile. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        profile_names = self.get_available_profiles()
        if not profile_names:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.PROFILE_NOT_FOUND)
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

        self.set_active_profile(profile_id)

        orca_modifier_manager.get_manager().unset_orca_modifiers("Profile changing.")
        command_manager.get_manager().load_keyboard_layout()
        orca_modifier_manager.get_manager().refresh_orca_modifiers("Profile changed.")
        presentation_manager.get_manager().refresh_presenters()

        if script is not None:
            script.set_up_commands()
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.PROFILE_CHANGED % name,
                    name,
                )

        return True

    @dbus_service.command
    def present_current_profile(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Present the name of the currently active profile."""

        tokens = [
            "PROFILE MANAGER: present_current_profile. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        profile_names = self.get_available_profiles()
        current_profile_id = self.get_active_profile()

        name = current_profile_id
        for display_name, internal_name in profile_names:
            if internal_name == current_profile_id:
                name = display_name
                break

        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(
                messages.PROFILE_CURRENT % name,
                name,
            )

        return True

    def create_preferences_grid(
        self,
        profile_loaded_callback: Callable[[list[str]], None],
        is_app_specific: bool = False,
        labels_update_callback: Callable[[], None] | None = None,
        unsaved_changes_checker: Callable[[], bool] | None = None,
    ) -> ProfilePreferencesGrid:
        """Returns the GtkGrid containing the profile management UI."""

        # pylint: disable-next=import-outside-toplevel
        from .profile_manager_preferences_grid import ProfilePreferencesGrid

        return ProfilePreferencesGrid(
            self,
            profile_loaded_callback,
            is_app_specific,
            labels_update_callback,
            unsaved_changes_checker,
        )


_manager = ProfileManager()


def get_manager() -> ProfileManager:
    """Returns the profile-manager singleton."""

    return _manager
