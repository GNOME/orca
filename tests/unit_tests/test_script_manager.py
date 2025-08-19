# Unit tests for script_manager.py methods.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines

"""Unit tests for script_manager.py methods."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest.mock import call, Mock

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestScriptManager:
    """Test ScriptManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for script_manager module testing."""

        modules_to_clean = ["orca.script_manager"]
        for module_name in modules_to_clean:
            if module_name in sys.modules:
                del sys.modules[module_name]

        additional_modules = [
            "gi",
            "gi.repository",
            "gi.repository.Atspi",
            "orca.ax_utilities",
            "orca.scripts",
            "orca.scripts.apps",
            "orca.scripts.default",
            "orca.scripts.sleepmode",
            "orca.scripts.toolkits",
            "orca.speech_and_verbosity_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        if "orca.script_manager" in essential_modules:
            del essential_modules["orca.script_manager"]
        if "orca.script_manager" in sys.modules:
            del sys.modules["orca.script_manager"]

        gi_repository_mock = essential_modules["gi.repository"]
        atspi_mock = essential_modules["gi.repository.Atspi"]

        class UnionSupportingMock(Mock):
            """Mock that supports union operations for Atspi.Accessible."""

            def __or__(self, other):
                return UnionSupportingMock()

        atspi_mock.Accessible = UnionSupportingMock()
        gi_repository_mock.Atspi = atspi_mock

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.get_name = test_context.Mock(return_value="test-app")
        ax_object_class_mock.get_attribute = test_context.Mock(return_value="GTK")
        ax_object_mock.AXObject = ax_object_class_mock

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_class_mock = test_context.Mock()
        ax_utilities_class_mock.is_terminal = test_context.Mock(return_value=False)
        ax_utilities_class_mock.get_application_toolkit_name = test_context.Mock(
            return_value="gtk"
        )
        ax_utilities_class_mock.is_application_in_desktop = test_context.Mock(
            return_value=True
        )
        ax_utilities_class_mock.is_frame = test_context.Mock(return_value=False)
        ax_utilities_class_mock.is_status_bar = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities = ax_utilities_class_mock

        braille_mock = essential_modules["orca.braille"]
        braille_mock.checkBrailleSetting = test_context.Mock()
        braille_mock.setupKeyRanges = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.get_runtime_settings = test_context.Mock(return_value={})
        settings_manager_instance.set_setting = test_context.Mock()
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        speech_verbosity_mock = essential_modules["orca.speech_and_verbosity_manager"]
        speech_manager_instance = test_context.Mock()
        speech_manager_instance.check_speech_setting = test_context.Mock()
        speech_verbosity_mock.get_manager = test_context.Mock(
            return_value=speech_manager_instance
        )

        scripts_mock = essential_modules["orca.scripts"]
        apps_mock = essential_modules["orca.scripts.apps"]
        toolkits_mock = essential_modules["orca.scripts.toolkits"]
        default_mock = essential_modules["orca.scripts.default"]
        sleepmode_mock = essential_modules["orca.scripts.sleepmode"]

        apps_mock.__all__ = ["evolution", "gedit", "gnome-shell"]
        toolkits_mock.__all__ = ["gtk", "Gecko", "Qt"]

        class MockScript:
            """Mock script class for testing."""

            def __init__(self, app=None):
                self.app = app
                self.register_event_listeners = test_context.Mock()
                self.deregister_event_listeners = test_context.Mock()
                self.activate = test_context.Mock()
                self.deactivate = test_context.Mock()
                self.braille_bindings = {}
                self._sleep_mode_manager = test_context.Mock()
                self._sleep_mode_manager.is_active_for_app = test_context.Mock(
                    return_value=False
                )
                self.get_sleep_mode_manager = test_context.Mock(
                    return_value=self._sleep_mode_manager
                )

            def __or__(self, other):
                return MockScript

        default_script_constructor = test_context.Mock(return_value=MockScript())
        default_script_constructor.__or__ = lambda self, other: MockScript()
        sleepmode_script_constructor = test_context.Mock(return_value=MockScript())
        sleepmode_script_constructor.__or__ = lambda self, other: MockScript()

        default_mock.Script = default_script_constructor
        sleepmode_mock.Script = sleepmode_script_constructor

        scripts_mock.apps = apps_mock
        scripts_mock.default = default_mock
        scripts_mock.sleepmode = sleepmode_mock
        scripts_mock.toolkits = toolkits_mock

        essential_modules["settings_manager_instance"] = settings_manager_instance
        essential_modules["speech_manager_instance"] = speech_manager_instance

        default_script = test_context.Mock()
        default_script.app = test_context.Mock()
        default_script.register_event_listeners = test_context.Mock()
        default_script.deregister_event_listeners = test_context.Mock()
        default_script.activate = test_context.Mock()
        default_script.deactivate = test_context.Mock()
        default_script.braille_bindings = {}

        sleepmode_script = test_context.Mock()
        sleepmode_script.app = test_context.Mock()
        sleepmode_script.register_event_listeners = test_context.Mock()
        sleepmode_script.deregister_event_listeners = test_context.Mock()
        sleepmode_script.activate = test_context.Mock()
        sleepmode_script.deactivate = test_context.Mock()

        sleep_mode_manager = test_context.Mock()
        sleep_mode_manager.is_active_for_app = test_context.Mock(return_value=False)

        essential_modules["default_script"] = default_script
        essential_modules["sleepmode_script"] = sleepmode_script
        essential_modules["sleep_mode_manager"] = sleep_mode_manager

        default_module = test_context.Mock()
        default_module.Script = test_context.Mock(return_value=test_context.Mock())

        sleepmode_module = test_context.Mock()
        sleepmode_module.Script = test_context.Mock(return_value=test_context.Mock())

        deps_settings_manager = test_context.Mock()
        deps_settings_manager_instance = test_context.Mock()
        deps_settings_manager_instance.get_runtime_settings = test_context.Mock(return_value={})
        deps_settings_manager_instance.set_setting = test_context.Mock()
        deps_settings_manager.get_manager = test_context.Mock(
            return_value=deps_settings_manager_instance
        )

        deps_speech_manager = test_context.Mock()
        deps_speech_manager_instance = test_context.Mock()
        deps_speech_manager_instance.check_speech_setting = test_context.Mock()
        deps_speech_manager.get_manager = test_context.Mock(
            return_value=deps_speech_manager_instance
        )

        braille_module = test_context.Mock()
        braille_module.checkBrailleSetting = test_context.Mock()
        braille_module.setupKeyRanges = test_context.Mock()

        essential_modules["default_module"] = default_module
        essential_modules["sleepmode_module"] = sleepmode_module
        essential_modules["deps_settings_manager"] = deps_settings_manager
        essential_modules["deps_speech_manager"] = deps_speech_manager
        essential_modules["braille_module"] = braille_module

        return essential_modules


    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test ScriptManager.__init__."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        assert not manager.app_scripts
        assert not manager.toolkit_scripts
        assert not manager.custom_scripts
        assert not manager._sleep_mode_scripts
        assert manager._default_script is None
        assert manager._active_script is None
        assert manager._active is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "inactive_to_active",
                "initially_active": False,
                "expects_script_creation": True,
            },
            {"id": "already_active", "initially_active": True, "expects_script_creation": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_activate(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test ScriptManager.activate with different initial states."""

        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]

        if case["expects_script_creation"]:
            mock_default_script = test_context.Mock()
            test_context.patch(
                "orca.script_manager.default.Script", new=mock_default_script
            )
            mock_default_script.return_value = default_script

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        manager._active = case["initially_active"]
        manager.activate()

        assert manager._active is True

        if case["expects_script_creation"]:
            assert manager._default_script is not None
            assert manager._active_script is not None
            default_script.register_event_listeners.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "active_to_inactive", "initially_active": True, "expects_cleanup": True},
            {"id": "already_inactive", "initially_active": False, "expects_cleanup": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_deactivate(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test ScriptManager.deactivate with different initial states."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        manager._active = case["initially_active"]

        if case["expects_cleanup"]:
            mock_script = test_context.Mock()
            mock_script.deregister_event_listeners = test_context.Mock()
            manager._default_script = mock_script
            manager.app_scripts = {"test": "script"}
            manager.toolkit_scripts = {"test": "script"}
            manager.custom_scripts = {"test": "script"}

        manager.deactivate()
        assert manager._active is False

        if case["expects_cleanup"]:
            assert manager._default_script is None
            assert manager._active_script is None
            assert not manager.app_scripts
            assert not manager.toolkit_scripts
            assert not manager.custom_scripts
            mock_script.deregister_event_listeners.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "app_in_apps_list",
                "app_name": "evolution",
                "expected_result": "evolution",
                "use_null_app": False,
            },
            {
                "id": "toolkit_in_toolkits_list",
                "app_name": "gtk",
                "expected_result": "gtk",
                "use_null_app": False,
            },
            {
                "id": "mapped_app_name",
                "app_name": "mate-notification-daemon",
                "expected_result": "notification-daemon",
                "use_null_app": False,
            },
            {
                "id": "alias_app_name",
                "app_name": "pluma",
                "expected_result": "gedit",
                "use_null_app": False,
            },
            {
                "id": "python_extension",
                "app_name": "test-app.py",
                "expected_result": "test-app",
                "use_null_app": False,
            },
            {
                "id": "bin_extension",
                "app_name": "test-app.bin",
                "expected_result": "test-app",
                "use_null_app": False,
            },
            {
                "id": "reverse_domain",
                "app_name": "org.gnome.TestApp",
                "expected_result": "TestApp",
                "use_null_app": False,
            },
            {
                "id": "reverse_domain_com",
                "app_name": "com.example.TestApp",
                "expected_result": "TestApp",
                "use_null_app": False,
            },
            {
                "id": "unknown_app",
                "app_name": "unknown-app",
                "expected_result": "unknown-app",
                "use_null_app": False,
            },
            {"id": "null_app", "app_name": None, "expected_result": None, "use_null_app": True},
            {"id": "nameless_app", "app_name": "", "expected_result": None, "use_null_app": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_module_name_scenarios(self, test_context, case: dict) -> None:
        """Test ScriptManager.get_module_name with various scenarios."""
        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()

        if case["use_null_app"]:
            result = manager.get_module_name(None)
        else:
            mock_app = test_context.Mock()
            mock_ax_object = test_context.Mock()
            test_context.patch("orca.script_manager.AXObject", new=mock_ax_object)
            mock_ax_object.get_name.return_value = case["app_name"]
            result = manager.get_module_name(mock_app)

        assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "gtk_toolkit", "toolkit_attribute": "GTK", "expected_result": "gtk"},
            {"id": "gail_mapped_to_gtk", "toolkit_attribute": "GAIL", "expected_result": "gtk"},
            {"id": "qt_toolkit", "toolkit_attribute": "Qt", "expected_result": "Qt"},
            {"id": "empty_toolkit", "toolkit_attribute": "", "expected_result": ""},
            {"id": "none_toolkit", "toolkit_attribute": None, "expected_result": None},
        ],
        ids=lambda case: case["id"],
    )
    def test_toolkit_for_object(self, test_context, case: dict) -> None:
        """Test ScriptManager._toolkit_for_object."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_obj = test_context.Mock()

        mock_ax_object = test_context.Mock()
        test_context.patch("orca.script_manager.AXObject", new=mock_ax_object)
        mock_ax_object.get_attribute.return_value = case["toolkit_attribute"]
        result = manager._toolkit_for_object(mock_obj)
        assert result == case["expected_result"]
        mock_ax_object.get_attribute.assert_called_once_with(mock_obj, "toolkit")

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "terminal_role", "is_terminal": True, "expected_result": "terminal"},
            {"id": "non_terminal_role", "is_terminal": False, "expected_result": ""},
        ],
        ids=lambda case: case["id"],
    )
    def test_script_for_role(self, test_context, case: dict) -> None:
        """Test ScriptManager._script_for_role."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_obj = test_context.Mock()

        mock_ax_utilities = test_context.Mock()
        test_context.patch("orca.script_manager.AXUtilities", new=mock_ax_utilities)
        mock_ax_utilities.is_terminal.return_value = case["is_terminal"]
        result = manager._script_for_role(mock_obj)
        assert result == case["expected_result"]
        mock_ax_utilities.is_terminal.assert_called_once_with(mock_obj)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "null_app_empty_name",
                "app": None,
                "name": "",
                "has_module": False,
                "has_get_script": False,
                "has_script_class": False,
                "should_succeed": False,
            },
            {
                "id": "empty_name",
                "app": "app",
                "name": "",
                "has_module": False,
                "has_get_script": False,
                "has_script_class": False,
                "should_succeed": False,
            },
            {
                "id": "no_module",
                "app": "app",
                "name": "test",
                "has_module": False,
                "has_get_script": False,
                "has_script_class": False,
                "should_succeed": False,
            },
            {
                "id": "has_get_script",
                "app": "app",
                "name": "test",
                "has_module": True,
                "has_get_script": True,
                "has_script_class": False,
                "should_succeed": True,
            },
            {
                "id": "has_script_class",
                "app": "app",
                "name": "test",
                "has_module": True,
                "has_get_script": False,
                "has_script_class": True,
                "should_succeed": True,
            },
            {
                "id": "no_script_creation",
                "app": "app",
                "name": "test",
                "has_module": True,
                "has_get_script": False,
                "has_script_class": False,
                "should_succeed": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_new_named_script(self, test_context, case: dict) -> None:
        """Test ScriptManager._new_named_script."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = test_context.Mock() if case["app"] else None
        mock_script = test_context.Mock()
        mock_import = test_context.Mock()
        test_context.patch("importlib.import_module", side_effect=mock_import)
        if case["has_module"]:
            mock_module = type("MockModule", (), {})()
            if case["has_get_script"]:
                mock_module.get_script = test_context.Mock(return_value=mock_script)
            elif case["has_script_class"]:
                mock_module.Script = test_context.Mock(return_value=mock_script)
            mock_import.return_value = mock_module
        else:
            mock_import.side_effect = ImportError("Module not found")
        result = manager._new_named_script(mock_app, case["name"])
        if case["should_succeed"]:
            assert result == mock_script
        else:
            assert result is None

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "os_error_causes_unboundlocal",
                "exception_type": "OSError",
            },
            {
                "id": "script_creation_error",
                "exception_type": "AttributeError",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_new_named_script_error_handling(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test ScriptManager._new_named_script handles various errors."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = test_context.Mock()
        mock_import = test_context.Mock()
        test_context.patch("importlib.import_module", side_effect=mock_import)

        if case["exception_type"] == "OSError":
            mock_import.side_effect = OSError("Permission denied")
            with pytest.raises(UnboundLocalError):
                manager._new_named_script(mock_app, "test")
        else:
            mock_module = type("MockModule", (), {})()
            mock_module.Script = test_context.Mock(
                side_effect=AttributeError("Script class not found")
            )
            mock_import.return_value = mock_module
            result = manager._new_named_script(mock_app, "test")
            assert result is None

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "no_module_name", "module_name": None, "expected_result_type": "default_script"},
            {
                "id": "with_module_name",
                "module_name": "test_script",
                "expected_result_type": "named_script",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_create_script(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test ScriptManager._create_script with different module name scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_script = test_context.Mock()

        test_context.patch_object(
            manager, "get_module_name", return_value=case["module_name"]
        )
        test_context.patch_object(
            manager, "_toolkit_for_object", return_value=None
        )
        test_context.patch_object(
            manager, "get_default_script", return_value=default_script
        )

        test_context.patch(
            "orca.script_manager.AXUtilities.get_application_toolkit_name",
            return_value=None,
        )

        if case["expected_result_type"] == "default_script":
            mock_new_named_script = test_context.Mock(return_value=None)
        else:
            mock_new_named_script = test_context.Mock(return_value=mock_script)
        test_context.patch_object(manager, "_new_named_script", side_effect=mock_new_named_script)

        result = manager._create_script(mock_app, mock_obj)

        if case["expected_result_type"] == "default_script":
            assert result == default_script
        else:
            assert result == mock_script
            mock_new_named_script.assert_called_once_with(mock_app, case["module_name"])

    def test_get_default_script(self, test_context: OrcaTestContext) -> None:
        """Test ScriptManager.get_default_script."""

        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]
        from orca.script_manager import ScriptManager

        mock_default_script = test_context.Mock()
        test_context.patch("orca.script_manager.default.Script", new=mock_default_script)
        mock_default_script.return_value = default_script
        manager = ScriptManager()
        mock_app = test_context.Mock()

        result = manager.get_default_script(mock_app)
        assert result is not None
        mock_default_script.assert_called_with(mock_app)

        manager._default_script = default_script
        result = manager.get_default_script(None)
        assert result == default_script

        manager._default_script = None
        result = manager.get_default_script(None)
        assert result is not None
        assert manager._default_script is not None

    def test_get_or_create_sleep_mode_script(self, test_context: OrcaTestContext) -> None:
        """Test ScriptManager.get_or_create_sleep_mode_script."""

        essential_modules = self._setup_dependencies(test_context)
        sleepmode_script = essential_modules["sleepmode_script"]
        from orca.script_manager import ScriptManager

        mock_sleepmode_script = test_context.Mock()
        test_context.patch(
            "orca.script_manager.sleepmode.Script", new=mock_sleepmode_script
        )
        mock_sleepmode_script.return_value = sleepmode_script
        manager = ScriptManager()
        mock_app = test_context.Mock()

        result = manager.get_or_create_sleep_mode_script(mock_app)
        assert result is not None
        assert result == sleepmode_script
        assert manager._sleep_mode_scripts[mock_app] == result

        result2 = manager.get_or_create_sleep_mode_script(mock_app)
        assert result2 == result
        assert len(manager._sleep_mode_scripts) == 1

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "null_app_and_obj",
                "app": None,
                "obj": None,
                "sleep_mode_active": False,
                "has_custom_script": False,
                "has_toolkit_script": False,
                "expected_script_type": "default",
            },
            {
                "id": "sleep_mode_active",
                "app": "app",
                "obj": "obj",
                "sleep_mode_active": True,
                "has_custom_script": False,
                "has_toolkit_script": False,
                "expected_script_type": "sleep",
            },
            {
                "id": "custom_script",
                "app": "app",
                "obj": "obj",
                "sleep_mode_active": False,
                "has_custom_script": True,
                "has_toolkit_script": False,
                "expected_script_type": "custom",
            },
            {
                "id": "toolkit_script",
                "app": "app",
                "obj": "obj",
                "sleep_mode_active": False,
                "has_custom_script": False,
                "has_toolkit_script": True,
                "expected_script_type": "toolkit",
            },
            {
                "id": "app_script",
                "app": "app",
                "obj": "obj",
                "sleep_mode_active": False,
                "has_custom_script": False,
                "has_toolkit_script": False,
                "expected_script_type": "app",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_script(self, test_context, case: dict) -> None:
        """Test ScriptManager.get_script."""

        essential_modules = self._setup_dependencies(test_context)
        sleepmode_script = essential_modules["sleepmode_script"]
        sleep_mode_manager = essential_modules["sleep_mode_manager"]
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = test_context.Mock() if case["app"] else None
        mock_obj = test_context.Mock() if case["obj"] else None
        mock_sleep_script = sleepmode_script
        mock_custom_script = test_context.Mock()

        class ToolkitScript:
            """Mock toolkit script class."""

        class AppScript:
            """Mock app script class."""

        mock_toolkit_script = test_context.Mock(spec=ToolkitScript)
        mock_app_script = test_context.Mock(spec=AppScript)
        sleep_mode_manager.is_active_for_app = test_context.Mock(
            return_value=case["sleep_mode_active"]
        )
        mock_app_script.get_sleep_mode_manager = test_context.Mock(return_value=sleep_mode_manager)
        test_context.patch_object(
            manager,
            "get_or_create_sleep_mode_script",
            return_value=mock_sleep_script,
        )
        test_context.patch_object(
            manager,
            "_script_for_role",
            return_value="terminal" if case["has_custom_script"] else "",
        )
        test_context.patch_object(
            manager,
            "_toolkit_for_object",
            return_value="gtk" if case["has_toolkit_script"] else None,
        )

        def create_script_side_effect(_app, obj):
            if obj and case["has_toolkit_script"]:
                return mock_toolkit_script
            return mock_app_script

        test_context.patch_object(
            manager, "_create_script", side_effect=create_script_side_effect
        )
        if case["has_custom_script"]:
            test_context.patch_object(
                manager, "_new_named_script", return_value=mock_custom_script
            )
        result = manager.get_script(mock_app, mock_obj)
        if case["expected_script_type"] == "default":
            assert result is not None
            assert hasattr(result, "register_event_listeners")
        elif case["expected_script_type"] == "sleep":
            assert result == mock_sleep_script
        elif case["expected_script_type"] == "custom":
            assert result == mock_custom_script
        elif case["expected_script_type"] == "toolkit":
            assert result == mock_toolkit_script
        elif case["expected_script_type"] == "app":
            assert result == mock_app_script

    def test_get_script_exception_handling(self, test_context: OrcaTestContext) -> None:
        """Test ScriptManager.get_script handles exceptions."""

        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = test_context.Mock()
        mock_obj = test_context.Mock()
        test_context.patch_object(
            manager, "_script_for_role", return_value=""
        )
        test_context.patch_object(
            manager, "_toolkit_for_object", return_value=None
        )

        def create_script_side_effect(app, obj):
            raise KeyError("Script creation failed")

        test_context.patch_object(
            manager, "_create_script", side_effect=create_script_side_effect
        )
        result = manager.get_script(mock_app, mock_obj)
        assert result is not None
        assert hasattr(result, "register_event_listeners")

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "no_active_script", "has_active_script": False, "test_type": "script"},
            {"id": "has_active_script", "has_active_script": True, "test_type": "script"},
            {"id": "no_active_script_app", "has_active_script": False, "test_type": "app"},
            {"id": "has_active_script_app", "has_active_script": True, "test_type": "app"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_active_script_and_app(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test ScriptManager.get_active_script and get_active_script_app."""
        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = test_context.Mock()

        if case["has_active_script"]:
            default_script.app = mock_app
            manager._active_script = default_script

        if case["test_type"] == "script":
            result = manager.get_active_script()
            expected = default_script if case["has_active_script"] else None
        else:
            result = manager.get_active_script_app()
            expected = mock_app if case["has_active_script"] else None

        assert result == expected

    def test_set_active_script(self, test_context: OrcaTestContext) -> None:
        """Test ScriptManager.set_active_script."""

        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]
        settings_manager = essential_modules["deps_settings_manager"]
        from orca.script_manager import ScriptManager

        mock_check_braille = test_context.Mock()
        test_context.patch(
            "orca.script_manager.braille.checkBrailleSetting", new=mock_check_braille
        )
        mock_setup_ranges = test_context.Mock()
        test_context.patch(
            "orca.script_manager.braille.setupKeyRanges", new=mock_setup_ranges
        )
        mock_get_speech_manager = test_context.Mock()
        test_context.patch(
            "orca.script_manager.speech_and_verbosity_manager.get_manager",
            new=mock_get_speech_manager,
        )
        mock_speech_manager_instance = test_context.Mock()
        mock_get_speech_manager.return_value = mock_speech_manager_instance
        manager = ScriptManager()
        old_script = test_context.Mock()
        old_script.app = test_context.Mock()
        old_script.deactivate = test_context.Mock()
        new_script = default_script
        new_script.app = test_context.Mock()
        new_script.activate = test_context.Mock()
        new_script.braille_bindings = {"key": "binding"}
        manager_instance = test_context.Mock()
        manager_instance.get_runtime_settings = test_context.Mock(return_value={"setting": "value"})
        manager_instance.set_setting = test_context.Mock()
        settings_manager.get_manager = test_context.Mock(return_value=manager_instance)

        manager._active_script = old_script
        manager.set_active_script(new_script, "test reason")
        old_script.deactivate.assert_called_once()
        new_script.activate.assert_called_once()
        assert manager._active_script == new_script

        mock_check_braille.assert_called_once()
        mock_setup_ranges.assert_called_once_with(new_script.braille_bindings.keys())
        mock_speech_manager_instance.check_speech_setting.assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "same_script_no_change",
                "new_script_type": "same",
                "expects_deactivate": False,
                "expects_activate": False,
            },
            {
                "id": "set_to_none",
                "new_script_type": "none",
                "expects_deactivate": True,
                "expects_activate": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_set_active_script_special_cases(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test ScriptManager.set_active_script special cases."""
        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]
        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        old_script = test_context.Mock()
        old_script.deactivate = test_context.Mock()
        manager._active_script = old_script

        if case["new_script_type"] == "same":
            manager._active_script = default_script
            manager.set_active_script(default_script, "same script")
            if case["expects_deactivate"]:
                default_script.deactivate.assert_called_once()
            else:
                default_script.deactivate.assert_not_called()
                default_script.activate.assert_not_called()
        else:
            manager.set_active_script(None)
            if case["expects_deactivate"]:
                old_script.deactivate.assert_called_once()
            assert manager._active_script is None

    def test_set_active_script_runtime_settings(self, test_context: OrcaTestContext) -> None:
        """Test ScriptManager.set_active_script preserves runtime settings for same app."""

        essential_modules = self._setup_dependencies(test_context)
        default_script = essential_modules["default_script"]
        from orca.script_manager import ScriptManager

        settings_patch = "orca.script_manager.settings_manager.get_manager"
        mock_get_settings_manager = test_context.Mock()
        test_context.patch(settings_patch, new=mock_get_settings_manager)
        test_context.patch(
            "orca.script_manager.braille.checkBrailleSetting", return_value=None
        )
        test_context.patch(
            "orca.script_manager.braille.setupKeyRanges", return_value=None
        )
        speech_patch = "orca.script_manager.speech_and_verbosity_manager.get_manager"
        mock_get_speech_manager = test_context.Mock()
        test_context.patch(speech_patch, new=mock_get_speech_manager)
        manager_instance = test_context.Mock()
        runtime_settings = {"key1": "value1", "key2": "value2"}
        manager_instance.get_runtime_settings = test_context.Mock(return_value=runtime_settings)
        manager_instance.set_setting = test_context.Mock()
        mock_get_settings_manager.return_value = manager_instance

        speech_manager_instance = test_context.Mock()
        mock_get_speech_manager.return_value = speech_manager_instance
        manager = ScriptManager()
        same_app = test_context.Mock()
        old_script = test_context.Mock()
        old_script.app = same_app
        old_script.deactivate = test_context.Mock()
        new_script = default_script
        new_script.app = same_app
        new_script.activate = test_context.Mock()
        new_script.braille_bindings = {}
        manager._active_script = old_script
        manager.set_active_script(new_script)
        expected_calls = [
            call("key1", "value1"),
            call("key2", "value2"),
        ]
        manager_instance.set_setting.assert_has_calls(expected_calls, any_order=True)

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "mixed_apps_normal", "has_app_in_desktop": True, "has_key_error": False},
            {
                "id": "no_desktop_apps_with_key_error",
                "has_app_in_desktop": False,
                "has_key_error": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_reclaim_scripts(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test ScriptManager.reclaim_scripts with various scenarios."""
        self._setup_dependencies(test_context)
        from orca.script_manager import ScriptManager

        desktop_patch = "orca.script_manager.AXUtilities.is_application_in_desktop"
        mock_is_in_desktop = test_context.Mock()
        test_context.patch(desktop_patch, new=mock_is_in_desktop)
        manager = ScriptManager()
        app_not_in_desktop = test_context.Mock()

        if case["has_app_in_desktop"]:
            app_in_desktop = test_context.Mock()
            manager.app_scripts = {
                app_in_desktop: test_context.Mock(),
                app_not_in_desktop: test_context.Mock(),
            }
            manager.toolkit_scripts = {app_not_in_desktop: test_context.Mock()}
            manager.custom_scripts = {app_not_in_desktop: test_context.Mock()}
            manager._sleep_mode_scripts = {app_not_in_desktop: test_context.Mock()}

            def mock_is_in_desktop_func(app):
                return app == app_in_desktop

            mock_is_in_desktop.side_effect = mock_is_in_desktop_func
            manager.reclaim_scripts()
            assert app_in_desktop in manager.app_scripts
            assert app_not_in_desktop not in manager.app_scripts
            assert app_not_in_desktop not in manager.toolkit_scripts
            assert app_not_in_desktop not in manager.custom_scripts
            assert app_not_in_desktop not in manager._sleep_mode_scripts
        else:
            manager.app_scripts = {app_not_in_desktop: test_context.Mock()}
            if case["has_key_error"]:
                manager.toolkit_scripts = {}
                manager.custom_scripts = {}
                manager._sleep_mode_scripts = {}
            else:
                manager.toolkit_scripts = {app_not_in_desktop: test_context.Mock()}
                manager.custom_scripts = {app_not_in_desktop: test_context.Mock()}
                manager._sleep_mode_scripts = {app_not_in_desktop: test_context.Mock()}

            mock_is_in_desktop.return_value = False
            manager.reclaim_scripts()
            assert app_not_in_desktop not in manager.app_scripts
            if not case["has_key_error"]:
                assert app_not_in_desktop not in manager.toolkit_scripts
                assert app_not_in_desktop not in manager.custom_scripts
                assert app_not_in_desktop not in manager._sleep_mode_scripts

    def test_get_manager(self, test_context: OrcaTestContext) -> None:
        """Test script_manager.get_manager."""

        self._setup_dependencies(test_context)
        from orca import script_manager

        manager1 = script_manager.get_manager()
        manager2 = script_manager.get_manager()
        assert manager1 is manager2
        assert isinstance(manager1, script_manager.ScriptManager)
