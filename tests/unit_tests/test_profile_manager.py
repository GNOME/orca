# Unit tests for profile_manager.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for profile_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestProfileManager:
    """Test ProfileManager methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for profile_manager dependencies."""

        additional_modules = [
            "orca.braille",
            "orca.orca",
            "orca.speech_and_verbosity_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_mock.get_manager.return_value.available_profiles.return_value = [
            ["Default", "default"],
            ["Spanish", "spanish"],
            ["Work", "work"],
        ]
        settings_manager_mock.get_manager.return_value.get_profile.return_value = "default"
        settings_manager_mock.get_manager.return_value.get_general_settings.return_value = {
            "startingProfile": ["Default", "default"],
        }

        speech_manager_mock = essential_modules["orca.speech_and_verbosity_manager"]
        speech_manager_mock.get_manager.return_value.refresh_speech.return_value = None

        braille_mock = essential_modules["orca.braille"]
        braille_mock.checkBrailleSetting.return_value = None

        orca_mock = essential_modules["orca.orca"]
        orca_mock.load_user_settings.return_value = None

        messages_mock = essential_modules["orca.messages"]
        messages_mock.PROFILE_NOT_FOUND = "No profiles found."
        messages_mock.PROFILE_CHANGED = "Profile set to %s."
        messages_mock.PROFILE_CURRENT = "Current profile is %s."

        return essential_modules

    def test_get_available_profiles(self, test_context: OrcaTestContext) -> None:
        """Test getting available profiles."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        profiles = manager.get_available_profiles()

        assert profiles == [["Default", "default"], ["Spanish", "spanish"], ["Work", "work"]]
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.available_profiles.assert_called_once()

    def test_get_active_profile(self, test_context: OrcaTestContext) -> None:
        """Test getting active profile."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        profile = manager.get_active_profile()

        assert profile == "default"
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_profile.assert_called_once()

    def test_set_active_profile(self, test_context: OrcaTestContext) -> None:
        """Test setting active profile."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.set_active_profile("spanish")

        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_profile.assert_called_once_with("spanish", False)

    def test_set_active_profile_with_locale_update(self, test_context: OrcaTestContext) -> None:
        """Test setting active profile with locale update."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.set_active_profile("spanish", update_locale=True)

        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_profile.assert_called_once_with("spanish", True)

    def test_load_profile(self, test_context: OrcaTestContext) -> None:
        """Test loading a profile calls set_active_profile and load_user_settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.load_profile("spanish")

        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_profile.assert_called_once_with("spanish", False)
        essential_modules["orca.orca"].load_user_settings.assert_called_once_with(
            skip_reload_message=True
        )

    def test_get_starting_profile(self, test_context: OrcaTestContext) -> None:
        """Test getting starting profile."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        profile = manager.get_starting_profile()

        assert profile == ["Default", "default"]

    def test_get_starting_profile_default_fallback(self, test_context: OrcaTestContext) -> None:
        """Test getting starting profile falls back to default."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_general_settings.return_value = {}
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        profile = manager.get_starting_profile()

        assert profile == ["Default", "default"]

    def test_set_starting_profile(self, test_context: OrcaTestContext) -> None:
        """Test setting starting profile is a no-op for backwards compatibility."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        # set_starting_profile is a no-op - it returns True without doing anything
        result = manager.set_starting_profile(["Spanish", "spanish"])

        assert result is True

    def test_remove_profile(self, test_context: OrcaTestContext) -> None:
        """Test removing a profile."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.remove_profile("spanish")

        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.remove_profile.assert_called_once_with("spanish")

    def test_rename_profile(self, test_context: OrcaTestContext) -> None:
        """Test renaming a profile."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager

        manager = ProfileManager()
        manager.rename_profile("spanish", ["Espanol", "espanol"])

        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.rename_profile.assert_called_once_with(
            "spanish", ["Espanol", "espanol"]
        )

    def test_commands_registered(self, test_context: OrcaTestContext) -> None:
        """Test that profile manager commands are registered with CommandManager."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager
        from orca import command_manager

        manager = ProfileManager()
        manager.set_up_commands()
        cmd_manager = command_manager.get_manager()

        assert cmd_manager.get_keyboard_command("cycleSettingsProfileHandler") is not None
        assert cmd_manager.get_keyboard_command("presentCurrentProfileHandler") is not None

    def test_cycle_settings_profile_cycles_to_next(self, test_context: OrcaTestContext) -> None:
        """Test cycle_settings_profile cycles to next profile."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager
        from unittest.mock import MagicMock

        manager = ProfileManager()
        mock_script = MagicMock()

        result = manager.cycle_settings_profile(script=mock_script)

        assert result is True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_profile.assert_called_with("spanish", True)
        mock_script.present_message.assert_called()

    def test_cycle_settings_profile_wraps_around(self, test_context: OrcaTestContext) -> None:
        """Test cycle_settings_profile wraps to first profile at end."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_profile.return_value = "work"
        from orca.profile_manager import ProfileManager
        from unittest.mock import MagicMock

        manager = ProfileManager()
        mock_script = MagicMock()

        result = manager.cycle_settings_profile(script=mock_script)

        assert result is True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_profile.assert_called_with("default", True)

    def test_cycle_settings_profile_no_profiles(self, test_context: OrcaTestContext) -> None:
        """Test cycle_settings_profile handles no profiles."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.available_profiles.return_value = []
        from orca.profile_manager import ProfileManager
        from unittest.mock import MagicMock

        manager = ProfileManager()
        mock_script = MagicMock()

        result = manager.cycle_settings_profile(script=mock_script)

        assert result is True
        mock_script.present_message.assert_called()

    def test_present_current_profile(self, test_context: OrcaTestContext) -> None:
        """Test present_current_profile presents the current profile name."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager
        from unittest.mock import MagicMock

        manager = ProfileManager()
        mock_script = MagicMock()

        result = manager.present_current_profile(script=mock_script)

        assert result is True
        mock_script.present_message.assert_called()
        call_args = mock_script.present_message.call_args
        assert "Default" in call_args[0][0]


@pytest.mark.unit
class TestProfilePreferencesGridUI:
    """Test ProfilePreferencesGrid UI creation."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ProfilePreferencesGrid dependencies."""

        additional_modules = [
            "orca.braille",
            "orca.orca",
            "orca.speech_and_verbosity_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_mock.get_manager.return_value.available_profiles.return_value = [
            ["Default", "default"],
            ["Spanish", "spanish"],
        ]
        settings_manager_mock.get_manager.return_value.get_profile.return_value = "default"
        settings_manager_mock.get_manager.return_value.get_general_settings.return_value = {
            "startingProfile": ["Default", "default"],
        }

        guilabels_mock = essential_modules["orca.guilabels"]
        guilabels_mock.GENERAL_PROFILES = "Profiles"
        guilabels_mock.GENERAL_START_UP_PROFILE = "Start-up profile"
        guilabels_mock.PROFILE_DEFAULT = "Default"
        guilabels_mock.PROFILE_CONFLICT_MESSAGE = "Profile %s already exists"
        guilabels_mock.PROFILE_REMOVE_LABEL = "Remove Profile"
        guilabels_mock.PROFILE_REMOVE_MESSAGE = "Remove profile %s?"
        guilabels_mock.MENU_REMOVE_PROFILE = "Remove"
        guilabels_mock.MENU_RENAME = "Rename"
        guilabels_mock.PROFILE_SAVE_AS_TITLE = "Save Profile As"
        guilabels_mock.PROFILE_NAME_LABEL = "Profile name:"
        guilabels_mock.DIALOG_CANCEL = "Cancel"
        guilabels_mock.DIALOG_APPLY = "Apply"
        guilabels_mock.DIALOG_ADD = "Add"
        guilabels_mock.PROFILES_INFO = "Select a profile to edit or create a new one."
        guilabels_mock.CURRENT_PROFILE = "Current Profile"
        guilabels_mock.PROFILE_CREATE_NEW = "_Create New Profile"

        return essential_modules

    def test_grid_creates_successfully(self, test_context: OrcaTestContext) -> None:
        """Test ProfilePreferencesGrid creates without error."""

        from gi.repository import Gtk

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        assert isinstance(grid, Gtk.Grid)

    def test_grid_has_auto_grid(self, test_context: OrcaTestContext) -> None:
        """Test ProfilePreferencesGrid has auto_grid with controls."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        assert grid._auto_grid is not None

    def test_grid_save_settings_returns_dict(self, test_context: OrcaTestContext) -> None:
        """Test save_settings returns a dictionary."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        result = grid.save_settings()

        assert isinstance(result, dict)

    def test_grid_has_changes_initially_false(self, test_context: OrcaTestContext) -> None:
        """Test has_changes returns False initially."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        assert grid.has_changes() is False

    def test_grid_reload_clears_pending_renames(self, test_context: OrcaTestContext) -> None:
        """Test reload clears pending renames."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        grid._pending_renames["old"] = ["New", "new"]
        assert len(grid._pending_renames) == 1

        grid.reload()

        assert len(grid._pending_renames) == 0

    def test_grid_app_specific_disables_startup_setter(self, test_context: OrcaTestContext) -> None:
        """Test app-specific grid disables startup profile setter."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback, is_app_specific=True)

        assert grid._is_app_specific is True

    def test_validate_profile_name_detects_conflict(self, test_context: OrcaTestContext) -> None:
        """Test _validate_profile_name detects existing profile names."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        is_valid, error_msg = grid._validate_profile_name("Default")

        assert is_valid is False
        assert "Default" in error_msg

    def test_validate_profile_name_allows_unique(self, test_context: OrcaTestContext) -> None:
        """Test _validate_profile_name allows unique names."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        is_valid, error_msg = grid._validate_profile_name("NewProfile")

        assert is_valid is True
        assert error_msg == ""

    def test_get_available_profiles_includes_pending_renames(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _get_available_profiles includes pending renames."""

        self._setup_dependencies(test_context)
        from orca.profile_manager import ProfileManager, ProfilePreferencesGrid

        manager = ProfileManager()

        def callback(profile):
            return None

        grid = ProfilePreferencesGrid(manager, callback)

        grid._pending_renames["spanish"] = ["Espanol", "spanish"]
        profiles = grid._get_available_profiles()

        profile_names = [p[0] for p in profiles]
        assert "Espanol" in profile_names
        assert "Spanish" not in profile_names
