# Unit tests for settings_manager.py methods.
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
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=too-many-statements

"""Unit tests for settings_manager.py with real file I/O.

These tests exercise the SettingsManager's file persistence capabilities
using actual file operations (not mocked) to verify settings are correctly
saved and loaded.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestSettingsManagerFileIO:
    """Test SettingsManager file I/O operations with real files."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Any]:
        """Set up dependencies for settings_manager testing.

        We mock only the dependencies of settings_manager, not settings_manager
        itself. We allow the real settings_manager and json_backend to execute
        since we're testing actual file I/O.
        """

        import sys
        from types import ModuleType

        # ModuleType allows settings_manager to set attributes on it dynamically
        settings_obj: Any = ModuleType("orca.settings")
        settings_obj.enableEchoByWord = True
        settings_obj.enableEchoByCharacter = True
        settings_obj.enableKeyEcho = True
        settings_obj.speechServerFactory = None
        settings_obj.speechServerInfo = None
        settings_obj.voices = {"default": {}}
        settings_obj.profile = ["Default", "default"]
        settings_obj.startingProfile = ["Default", "default"]
        settings_obj.activeProfile = ["Default", "default"]
        settings_obj.enableSpeech = True
        settings_obj.onlySpeakDisplayedText = False
        settings_obj.orcaModifierKeys = ["Insert", "KP_Insert"]
        settings_obj.presentTimeFormat = "%X"

        essential_modules: dict[str, Any] = {}

        debug_mock = test_context.Mock()
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_ALL = 0
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        test_context.patch_module("orca.debug", debug_mock)
        essential_modules["orca.debug"] = debug_mock

        i18n_mock = test_context.Mock()
        i18n_mock._ = lambda x: x
        i18n_mock.C_ = lambda c, x: x
        i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p
        i18n_mock.setLocaleForNames = test_context.Mock()
        i18n_mock.setLocaleForMessages = test_context.Mock()
        i18n_mock.setLocaleForGUI = test_context.Mock()
        test_context.patch_module("orca.orca_i18n", i18n_mock)
        essential_modules["orca.orca_i18n"] = i18n_mock

        acss_mock = test_context.Mock()
        acss_class_mock = test_context.Mock()
        acss_class_mock.getLocale = test_context.Mock(return_value="en_US")
        acss_class_mock.getDialect = test_context.Mock(return_value=None)
        acss_mock.ACSS = test_context.Mock(return_value=acss_class_mock)
        test_context.patch_module("orca.acss", acss_mock)
        essential_modules["orca.acss"] = acss_mock

        pronun_mock = test_context.Mock()
        pronun_mock.pronunciation_dict = {}
        pronun_mock.set_pronunciation = test_context.Mock()
        test_context.patch_module("orca.pronunciation_dict", pronun_mock)
        essential_modules["orca.pronunciation_dict"] = pronun_mock

        keybindings_mock = test_context.Mock()
        keybindings_mock.KeyBinding = test_context.Mock()
        test_context.patch_module("orca.keybindings", keybindings_mock)
        essential_modules["orca.keybindings"] = keybindings_mock

        ax_object_mock = test_context.Mock()
        ax_object_mock.get_name = test_context.Mock(return_value="TestApp")
        ax_object_class = test_context.Mock()
        ax_object_class.get_name = test_context.Mock(return_value="TestApp")
        ax_object_mock.AXObject = ax_object_class
        test_context.patch_module("orca.ax_object", ax_object_mock)
        essential_modules["orca.ax_object"] = ax_object_mock

        # Inject settings AFTER other mocks but BEFORE importing settings_manager
        sys.modules["orca.settings"] = settings_obj
        essential_modules["orca.settings"] = settings_obj

        return essential_modules

    def _create_fresh_manager(
        self, test_context: OrcaTestContext, prefs_dir: str
    ) -> Any:
        """Create a fresh SettingsManager instance for testing."""

        from orca import settings_manager

        manager = settings_manager.SettingsManager()
        manager.activate(prefs_dir=prefs_dir)
        return manager

    def test_save_settings_creates_file(self, test_context: OrcaTestContext) -> None:
        """Test that save_settings creates the user-settings.conf file."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            self._create_fresh_manager(test_context, temp_dir)

            settings_file = os.path.join(temp_dir, "user-settings.conf")
            assert os.path.exists(settings_file)

            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "startingProfile" in data
            assert "profiles" in data
            # Legacy keys for backwards compatibility with older Orca versions
            assert "general" in data
            assert "pronunciations" in data
            assert "keybindings" in data

    def test_save_settings_persists_general(self, test_context: OrcaTestContext) -> None:
        """Test that general settings are persisted to file and can be reloaded."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            test_value = False
            general_settings = manager.get_settings()
            general_settings["enableEchoByWord"] = test_value
            general_settings["profile"] = ["Default", "default"]

            manager.save_settings(mock_script, general_settings, {}, {})

            manager2 = self._create_fresh_manager(test_context, temp_dir)
            loaded_general = manager2.get_general_settings("default")
            assert loaded_general.get("enableEchoByWord") == test_value

    def test_save_settings_persists_pronunciations(self, test_context: OrcaTestContext) -> None:
        """Test that pronunciation settings are persisted to file."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            test_pronunciations = {"API": ["API", "A P I"]}
            general_settings = manager.get_settings()
            general_settings["profile"] = ["Default", "default"]

            manager.save_settings(mock_script, general_settings, test_pronunciations, {})

            manager2 = self._create_fresh_manager(test_context, temp_dir)
            loaded_pronunciations = manager2.get_pronunciations("default")
            assert loaded_pronunciations.get("API") == ["API", "A P I"]

    def test_save_settings_persists_keybindings(self, test_context: OrcaTestContext) -> None:
        """Test that keybinding settings are persisted to file."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            test_keybindings = {"someHandler": [("a", 1, 0, 1)]}
            general_settings = manager.get_settings()
            general_settings["profile"] = ["Default", "default"]

            manager.save_settings(mock_script, general_settings, {}, test_keybindings)

            manager2 = self._create_fresh_manager(test_context, temp_dir)
            loaded_keybindings = manager2.get_keybindings("default")
            assert loaded_keybindings.get("someHandler") == [["a", 1, 0, 1]]

    def test_available_profiles_default(self, test_context: OrcaTestContext) -> None:
        """Test that a fresh start has the 'default' profile available."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            profiles = manager.available_profiles()
            assert any("default" in str(p).lower() for p in profiles)

    def test_get_profile_returns_current(self, test_context: OrcaTestContext) -> None:
        """Test that get_profile returns the current profile name."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            profile = manager.get_profile()
            assert profile == "default"

    def test_set_profile_switches_context(self, test_context: OrcaTestContext) -> None:
        """Test that set_profile switches to the specified profile."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            general_work = manager.get_settings()
            general_work["profile"] = ["Work", "work"]
            general_work["enableEchoByWord"] = True
            manager.save_settings(mock_script, general_work, {}, {})

            manager.set_profile("default")
            general_default = manager.get_settings()
            general_default["profile"] = ["Default", "default"]
            general_default["enableEchoByWord"] = False
            manager.save_settings(mock_script, general_default, {}, {})

            manager.set_profile("work")
            assert manager.get_profile() == "work"

            manager.set_profile("default")
            assert manager.get_profile() == "default"

    def test_save_profile_settings_separate_from_default(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that multiple profiles don't interfere with each other."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            general_work = manager.get_settings()
            general_work["profile"] = ["Work", "work"]
            general_work["enableEchoByWord"] = True
            manager.save_settings(mock_script, general_work, {}, {})

            manager.set_profile("default")
            general_default = manager.get_settings()
            general_default["profile"] = ["Default", "default"]
            general_default["enableEchoByWord"] = False
            manager.save_settings(mock_script, general_default, {}, {})

            manager2 = self._create_fresh_manager(test_context, temp_dir)

            work_settings = manager2.get_general_settings("work")
            default_settings = manager2.get_general_settings("default")

            assert work_settings.get("enableEchoByWord") is True
            assert default_settings.get("enableEchoByWord") is False

    def test_remove_profile(self, test_context: OrcaTestContext) -> None:
        """Test that remove_profile removes a profile."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            general_temp = manager.get_settings()
            general_temp["profile"] = ["Temporary", "temporary"]
            manager.save_settings(mock_script, general_temp, {}, {})

            profiles_before = manager.available_profiles()
            assert any("temporary" in str(p).lower() for p in profiles_before)

            manager.remove_profile("temporary")

            manager2 = self._create_fresh_manager(test_context, temp_dir)
            profiles_after = manager2.available_profiles()
            assert not any("temporary" in str(p).lower() for p in profiles_after)

    def test_save_app_settings_creates_app_file(self, test_context: OrcaTestContext) -> None:
        """Test that app-specific settings are saved to a separate file."""

        essential_modules = self._setup_dependencies(test_context)

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.get_name = test_context.Mock(return_value="TestApp")

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            from orca import settings_manager
            test_context.patch_object(
                settings_manager, "AXObject", new=ax_object_mock
            )

            mock_script = test_context.Mock()
            mock_app = test_context.Mock()
            mock_script.app = mock_app

            general_settings = manager.get_settings()
            general_settings["enableEchoByWord"] = True

            manager.save_settings(mock_script, general_settings, {}, {})

            app_settings_file = os.path.join(temp_dir, "app-settings", "TestApp.conf")
            assert os.path.exists(app_settings_file)

            with open(app_settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "profiles" in data

    def test_get_prefs_dir(self, test_context: OrcaTestContext) -> None:
        """Test that get_prefs_dir returns the configured preferences directory."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            assert manager.get_prefs_dir() == temp_dir

    def test_settings_file_structure(self, test_context: OrcaTestContext) -> None:
        """Test that the settings file has the expected JSON structure."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            self._create_fresh_manager(test_context, temp_dir)

            settings_file = os.path.join(temp_dir, "user-settings.conf")
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "startingProfile" in data
            assert "profiles" in data
            assert "default" in data["profiles"]
            # Legacy keys for backwards compatibility with older Orca versions
            assert "general" in data
            assert "pronunciations" in data
            assert "keybindings" in data
            # Legacy general must contain all default settings for backwards compatibility
            assert "orcaModifierKeys" in data["general"]
            assert "presentTimeFormat" in data["general"]

    def test_starting_profile_persistence(self, test_context: OrcaTestContext) -> None:
        """Test that the starting profile setting is persisted correctly."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            manager.set_starting_profile(["Work", "work"])

            settings_file = os.path.join(temp_dir, "user-settings.conf")
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["startingProfile"] == ["Work", "work"]
            # Legacy key for backwards compatibility with older Orca versions
            assert data["general"]["startingProfile"] == ["Work", "work"]

    def test_configuring_mode(self, test_context: OrcaTestContext) -> None:
        """Test that set_configuring and is_configuring work correctly."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            assert manager.is_configuring() is False

            manager.set_configuring(True)
            assert manager.is_configuring() is True

            manager.set_configuring(False)
            assert manager.is_configuring() is False

    def test_rename_profile(self, test_context: OrcaTestContext) -> None:
        """Test that rename_profile renames a profile's label and internal name."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            mock_script = test_context.Mock()
            mock_script.app = None

            general_old = manager.get_settings()
            general_old["profile"] = ["Old Name", "old_name"]
            general_old["enableEchoByWord"] = True
            manager.save_settings(mock_script, general_old, {}, {})

            profiles_before = manager.available_profiles()
            assert any("old_name" in str(p) for p in profiles_before)

            manager.rename_profile("old_name", ["New Name", "new_name"])

            manager2 = self._create_fresh_manager(test_context, temp_dir)
            profiles_after = manager2.available_profiles()

            assert not any("old_name" in str(p) for p in profiles_after)
            assert any("new_name" in str(p) for p in profiles_after)

            new_settings = manager2.get_general_settings("new_name")
            assert new_settings.get("enableEchoByWord") is True
            assert new_settings.get("profile") == ["New Name", "new_name"]

    def test_rename_profile_nonexistent(self, test_context: OrcaTestContext) -> None:
        """Test that rename_profile does nothing for a nonexistent profile."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            profiles_before = manager.available_profiles()

            manager.rename_profile("nonexistent", ["New Name", "new_name"])

            manager2 = self._create_fresh_manager(test_context, temp_dir)
            profiles_after = manager2.available_profiles()

            assert profiles_before == profiles_after

    def test_snapshot_settings_captures_values(self, test_context: OrcaTestContext) -> None:
        """Test that snapshot_settings captures current runtime settings."""

        essential_modules = self._setup_dependencies(test_context)
        settings_obj = essential_modules["orca.settings"]

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            settings_obj.enableEchoByWord = True
            settings_obj.enableKeyEcho = False

            snapshot = manager.snapshot_settings()

            assert snapshot.get("enableEchoByWord") is True
            assert snapshot.get("enableKeyEcho") is False

    def test_snapshot_settings_excludes_excluded_settings(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that snapshot_settings excludes settings in _EXCLUDED_SETTINGS."""

        essential_modules = self._setup_dependencies(test_context)
        settings_obj = essential_modules["orca.settings"]

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            settings_obj.silenceSpeech = True

            snapshot = manager.snapshot_settings()

            assert "silenceSpeech" not in snapshot

    def test_restore_settings_restores_values(self, test_context: OrcaTestContext) -> None:
        """Test that restore_settings restores values from a snapshot."""

        essential_modules = self._setup_dependencies(test_context)
        settings_obj = essential_modules["orca.settings"]

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            settings_obj.enableEchoByWord = True
            settings_obj.enableKeyEcho = False
            snapshot = manager.snapshot_settings()

            settings_obj.enableEchoByWord = False
            settings_obj.enableKeyEcho = True

            manager.restore_settings(snapshot)

            assert settings_obj.enableEchoByWord is True
            assert settings_obj.enableKeyEcho is False

    def test_snapshot_restore_preserves_excluded_settings(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that excluded settings are not affected by snapshot/restore."""

        essential_modules = self._setup_dependencies(test_context)
        settings_obj = essential_modules["orca.settings"]

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            settings_obj.silenceSpeech = False
            snapshot = manager.snapshot_settings()

            settings_obj.silenceSpeech = True

            manager.restore_settings(snapshot)

            # silenceSpeech should remain True because it's excluded from snapshots
            assert settings_obj.silenceSpeech is True
