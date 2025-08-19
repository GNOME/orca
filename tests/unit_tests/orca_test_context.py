# Orca Test Context - Test Isolation Framework
#
# Copyright 2025 Igalia, S.L.
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

"""Test isolation framework for Orca screen reader tests."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi  # pylint: disable=wrong-import-position

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from _pytest.monkeypatch import MonkeyPatch

class OrcaTestContext:
    """Test isolation framework for Orca tests."""

    def __init__(self, mocker: MockerFixture, monkeypatch: MonkeyPatch):
        """Initialize the test context."""

        self.mocker: MockerFixture = mocker
        self.monkeypatch: MonkeyPatch = monkeypatch
        self.patches: dict[str, Any] = {}
        self.mocks: dict[str, MagicMock] = {}

    def patch(self, target: str, **kwargs) -> MagicMock:
        """Convenience method for creating patches."""

        return self.mocker.patch(target, **kwargs)

    def patch_object(self, target: object, attribute: str, **kwargs) -> MagicMock:
        """Convenience method for patching object attributes."""

        return self.mocker.patch.object(target, attribute, **kwargs)

    def Mock(self, **kwargs) -> MagicMock:  # pylint: disable=invalid-name
        """Convenience method for creating Mock objects."""

        return self.mocker.Mock(**kwargs)

    def patch_env(self, env_vars: dict[str, str],
                  remove_vars: list[str] | None = None) -> MagicMock | None:
        """Convenience method for patching environment variables."""

        if remove_vars:
            for var in remove_vars:
                if var in os.environ:
                    del os.environ[var]

        if env_vars:
            return self.mocker.patch.dict(os.environ, env_vars)
        return None

    def patch_module(self, module_name: str, mock_module: Any) -> MagicMock:
        """Convenience method for patching sys.modules entries."""

        return self.mocker.patch.dict(sys.modules, {module_name: mock_module})

    def patch_modules(self, modules: dict[str, Any]) -> MagicMock:
        """Convenience method for patching multiple sys.modules entries."""

        return self.mocker.patch.dict(sys.modules, modules)

    def _setup_required_imports(self) -> None:
        """Sets up commonly required module imports that real modules need."""

        required_modules = [
            "orca.orca_i18n",
            "orca.cmdnames",
            "orca.input_event",
            "orca.keybindings",
            "orca.messages",
            "orca.text_attribute_names",
            "orca.settings",
        ]

        for module_name in required_modules:
            if module_name not in self.mocks:
                mock_module = self.mocker.patch(module_name, create=True)
                if module_name == "orca.orca_i18n":
                    mock_module._ = lambda x: x
                self.mocks[module_name] = mock_module

    def _setup_essential_modules(self, module_names: list[str]) -> dict[str, MagicMock]:
        """Returns dictionary mapping module names to mock objects."""

        essential_modules = {}
        for module_name in module_names:
            mock_module = self.mocker.Mock()
            self.patch_module(module_name, mock_module)
            essential_modules[module_name] = mock_module
        return essential_modules

    def setup_shared_dependencies(
        self, additional_modules: list[str] | None = None
    ) -> dict[str, MagicMock]:
        """Returns common/shared dependencies used across most Orca test modules."""

        core_modules = [
            "orca.debug",
            "orca.messages",
            "orca.input_event",
            "orca.settings",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.ax_object",
            "orca.settings_manager",
            "orca.dbus_service",
            "orca.script_manager",
            "orca.orca_i18n",
            "orca.guilabels",
            "orca.text_attribute_names",
            "orca.focus_manager",
            "orca.braille",
        ]

        if additional_modules:
            core_modules.extend(additional_modules)

        essential_modules = self._setup_essential_modules(core_modules)
        self.configure_shared_module_behaviors(essential_modules)
        return essential_modules

    # pylint: disable-next=too-many-locals, too-many-statements
    def configure_shared_module_behaviors(self, essential_modules: dict[str, MagicMock]) -> None:
        """Configure standard behaviors for shared modules to reduce duplication."""

        if "orca.orca_i18n" in essential_modules:
            i18n_mock = essential_modules["orca.orca_i18n"]
            i18n_mock._ = lambda x: x
            i18n_mock.C_ = lambda c, x: x
            i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p

        if "orca.debug" in essential_modules:
            debug_mock = essential_modules["orca.debug"]
            debug_mock.LEVEL_INFO = 800
            debug_mock.LEVEL_SEVERE = 1000
            debug_mock.print_message = self.mocker.Mock()
            debug_mock.print_tokens = self.mocker.Mock()
            debug_mock.println = self.mocker.Mock()

        if "orca.keybindings" in essential_modules:
            keybindings_mock = essential_modules["orca.keybindings"]
            bindings_instance = self.mocker.Mock()
            bindings_instance.is_empty = self.mocker.Mock(return_value=True)
            bindings_instance.add = self.mocker.Mock()
            keybindings_mock.KeyBindings = self.mocker.Mock(return_value=bindings_instance)
            keybindings_mock.KeyBinding = self.mocker.Mock(return_value=self.mocker.Mock())
            keybindings_mock.DEFAULT_MODIFIER_MASK = 1
            keybindings_mock.ORCA_SHIFT_MODIFIER_MASK = 2

        if "orca.settings_manager" in essential_modules:
            settings_manager_mock = essential_modules["orca.settings_manager"]
            manager_instance = self.mocker.Mock()
            manager_instance.get_setting = self.mocker.Mock(return_value=True)
            manager_instance.set_setting = self.mocker.Mock(return_value=True)
            settings_manager_mock.get_manager = self.mocker.Mock(return_value=manager_instance)

        if "orca.focus_manager" in essential_modules:
            focus_manager_mock = essential_modules["orca.focus_manager"]
            manager_instance = self.mocker.Mock()
            manager_instance.get_locus_of_focus = self.mocker.Mock(return_value=None)
            manager_instance.set_locus_of_focus = self.mocker.Mock()
            focus_manager_mock.get_manager = self.mocker.Mock(return_value=manager_instance)
            essential_modules["focus_manager_instance"] = manager_instance

        if "orca.dbus_service" in essential_modules:
            dbus_service_mock = essential_modules["orca.dbus_service"]
            controller_mock = self.mocker.Mock()
            controller_mock.register_decorated_module = self.mocker.Mock()
            dbus_service_mock.get_remote_controller = self.mocker.Mock(return_value=controller_mock)
            dbus_service_mock.command = lambda func: func
            dbus_service_mock.getter = lambda func: func
            dbus_service_mock.setter = lambda func: func
            dbus_service_mock.parameterized_command = lambda func: func

        if "orca.script_manager" in essential_modules:
            script_manager_mock = essential_modules["orca.script_manager"]
            manager_instance = self.mocker.Mock()
            script_instance = self.mocker.Mock()
            script_instance.present_message = self.mocker.Mock()
            script_instance.present_object = self.mocker.Mock()
            script_instance.speak_message = self.mocker.Mock()
            script_instance.update_braille = self.mocker.Mock()
            script_instance.speech_generator = self.mocker.Mock()
            script_instance.braille_generator = self.mocker.Mock()
            manager_instance.get_active_script = self.mocker.Mock(return_value=script_instance)
            manager_instance.get_script = self.mocker.Mock(return_value=script_instance)
            manager_instance.get_manager = self.mocker.Mock(return_value=manager_instance)
            script_manager_mock.get_manager = self.mocker.Mock(return_value=manager_instance)

        if "orca.ax_object" in essential_modules:
            ax_object_mock = essential_modules["orca.ax_object"]
            ax_object_class_mock = self.mocker.Mock()
            ax_object_class_mock.is_valid = self.mocker.Mock(return_value=True)
            ax_object_class_mock.is_dead = self.mocker.Mock(return_value=False)
            ax_object_class_mock.get_name = self.mocker.Mock(return_value="")
            ax_object_class_mock.get_role = self.mocker.Mock(return_value=Atspi.Role.PANEL)
            ax_object_class_mock.get_parent = self.mocker.Mock(return_value=None)
            ax_object_class_mock.find_ancestor = self.mocker.Mock(return_value=None)
            ax_object_class_mock.clear_cache = self.mocker.Mock()
            ax_object_mock.AXObject = ax_object_class_mock

        if "orca.ax_utilities" in essential_modules:
            ax_utilities_mock = essential_modules["orca.ax_utilities"]
            ax_utilities_class_mock = self.mocker.Mock()
            ax_utilities_class_mock.is_focused = self.mocker.Mock(return_value=True)
            ax_utilities_class_mock.is_table_cell_or_header = self.mocker.Mock(return_value=False)
            ax_utilities_class_mock.is_list_item = self.mocker.Mock(return_value=False)
            ax_utilities_class_mock.is_layout_only = self.mocker.Mock(return_value=False)
            ax_utilities_class_mock.get_status_bar = self.mocker.Mock(return_value=None)
            ax_utilities_class_mock.get_info_bar = self.mocker.Mock(return_value=None)
            ax_utilities_class_mock.is_showing = self.mocker.Mock(return_value=True)
            ax_utilities_class_mock.is_visible = self.mocker.Mock(return_value=True)
            ax_utilities_class_mock.is_sensitive = self.mocker.Mock(return_value=True)
            ax_utilities_mock.AXUtilities = ax_utilities_class_mock

        if "orca.input_event" in essential_modules:
            input_event_mock = essential_modules["orca.input_event"]
            input_event_mock.KEY_PRESSED_EVENT = "key-pressed"
            input_event_mock.KEY_RELEASED_EVENT = "key-released"
            input_event_mock.MOUSE_BUTTON_CLICKED_EVENT = "mouse-clicked"

    def get_mock(self, name: str) -> MagicMock | None:
        """Returns mock object if it exists, None otherwise."""

        return self.mocks.get(name)

    def __enter__(self) -> OrcaTestContext:
        """Enter the test context."""

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the test context and clean up all patches."""

        for patch_obj in self.patches.values():
            patch_obj.stop()

        self.patches.clear()
        self.mocks.clear()
