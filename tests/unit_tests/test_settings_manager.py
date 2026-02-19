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

# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

"""Unit tests for settings_manager.py with real file I/O.

These tests exercise the SettingsManager's file persistence capabilities
using actual file operations (not mocked) to verify settings are correctly
saved and loaded.
"""

from __future__ import annotations

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

        essential_modules: dict[str, Any] = {}

        debug_mock = test_context.Mock()
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_ALL = 0
        debug_mock.debugFile = None  # Needed for debugging_tools_manager initialization
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

        pronun_manager_mock = test_context.Mock()
        pronun_manager_mock.set_dictionary = test_context.Mock()
        pronun_manager_mock.set_pronunciation = test_context.Mock()
        pronun_manager_mock.get_pronunciation = test_context.Mock(side_effect=lambda w: w)
        pronun_manager_mock.get_dictionary = test_context.Mock(return_value={})
        pronun_module_mock = test_context.Mock()
        pronun_module_mock.get_manager = test_context.Mock(return_value=pronun_manager_mock)
        test_context.patch_module("orca.pronunciation_dictionary_manager", pronun_module_mock)
        essential_modules["orca.pronunciation_dictionary_manager"] = pronun_module_mock

        # Mock orca_platform (generated at build time)
        platform_mock = test_context.Mock()
        platform_mock.version = "test_version"
        platform_mock.tablesdir = "/usr/share/liblouis/tables"  # Standard location
        test_context.patch_module("orca.orca_platform", platform_mock)
        essential_modules["orca.orca_platform"] = platform_mock

        # Mock messages (uses orca_platform)
        messages_mock = test_context.Mock()
        test_context.patch_module("orca.messages", messages_mock)
        essential_modules["orca.messages"] = messages_mock

        # Mock pronunciation_dictionary_manager (uses messages)
        pronun_dict_manager_mock = test_context.Mock()
        pronun_dict_manager_mock.get_manager = test_context.Mock(return_value=test_context.Mock())
        test_context.patch_module("orca.pronunciation_dictionary_manager", pronun_dict_manager_mock)
        essential_modules["orca.pronunciation_dictionary_manager"] = pronun_dict_manager_mock

        keybindings_mock = test_context.Mock()
        keybindings_mock.KeyBinding = test_context.Mock()
        test_context.patch_module("orca.keybindings", keybindings_mock)
        essential_modules["orca.keybindings"] = keybindings_mock

        # Mock script_manager to avoid cascading dependencies
        script_manager_mock = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock(return_value=test_context.Mock())
        test_context.patch_module("orca.script_manager", script_manager_mock)
        essential_modules["orca.script_manager"] = script_manager_mock

        ax_object_mock = test_context.Mock()
        ax_object_mock.get_name = test_context.Mock(return_value="TestApp")
        ax_object_class = test_context.Mock()
        ax_object_class.get_name = test_context.Mock(return_value="TestApp")
        ax_object_mock.AXObject = ax_object_class
        test_context.patch_module("orca.ax_object", ax_object_mock)
        essential_modules["orca.ax_object"] = ax_object_mock

        # Mock gsettings_registry so file I/O tests use the JSON path
        gsettings_registry_mock = test_context.Mock()
        mock_registry = test_context.Mock()
        mock_registry.is_enabled.return_value = False
        mock_registry.layered_lookup.return_value = None
        gsettings_registry_mock.get_registry.return_value = mock_registry
        test_context.patch_module("orca.gsettings_registry", gsettings_registry_mock)
        essential_modules["orca.gsettings_registry"] = gsettings_registry_mock

        return essential_modules

    def _create_fresh_manager(self, _test_context: OrcaTestContext, prefs_dir: str) -> Any:
        """Create a fresh SettingsManager instance for testing."""

        from orca import settings_manager

        manager = settings_manager.SettingsManager()
        manager.activate(prefs_dir=prefs_dir)
        return manager

    def test_profiles_from_json_default(self, test_context: OrcaTestContext) -> None:
        """Test that a fresh start has the 'default' profile available."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            profiles = manager.profiles_from_json()
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

            manager.set_profile("work")
            assert manager.get_profile() == "work"

            manager.set_profile("default")
            assert manager.get_profile() == "default"

    def test_get_prefs_dir(self, test_context: OrcaTestContext) -> None:
        """Test that get_prefs_dir returns the configured preferences directory."""

        self._setup_dependencies(test_context)

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = self._create_fresh_manager(test_context, temp_dir)

            assert manager.get_prefs_dir() == temp_dir

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
