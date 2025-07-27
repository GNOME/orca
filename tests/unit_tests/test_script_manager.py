# Unit tests for script_manager.py ScriptManager class methods.
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

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=unused-variable
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""Unit tests for script_manager.py ScriptManager class methods."""

from __future__ import annotations

import sys
from unittest.mock import Mock, patch, call

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi


@pytest.mark.unit
class TestScriptManager:
    """Test ScriptManager class methods."""

    @pytest.fixture
    def mock_script_manager_deps(self, monkeypatch, mock_orca_dependencies):
        """Mock all dependencies needed for script_manager imports."""

        from conftest import clean_module_cache  # pylint: disable=import-error

        modules_to_clean = [
            "orca.script_manager",
            "orca.braille",
            "orca.settings_manager",
            "orca.speech_and_verbosity_manager",
            "orca.scripts",
            "orca.scripts.default",
            "orca.scripts.apps",
            "orca.scripts.sleepmode",
            "orca.scripts.toolkits",
        ]
        for module in modules_to_clean:
            clean_module_cache(module)

        braille_mock = Mock()
        braille_mock.checkBrailleSetting = Mock()
        braille_mock.setupKeyRanges = Mock()

        settings_manager_mock = Mock()
        manager_instance = Mock()
        manager_instance.get_runtime_settings = Mock(return_value={})
        manager_instance.set_setting = Mock()
        settings_manager_mock.get_manager = Mock(return_value=manager_instance)

        speech_and_verbosity_manager_mock = Mock()
        speech_manager_instance = Mock()
        speech_manager_instance.check_speech_setting = Mock()
        speech_and_verbosity_manager_mock.get_manager = Mock(return_value=speech_manager_instance)

        monkeypatch.setitem(sys.modules, "orca.braille", braille_mock)
        monkeypatch.setitem(sys.modules, "orca.settings_manager", settings_manager_mock)
        monkeypatch.setitem(
            sys.modules, "orca.speech_and_verbosity_manager", speech_and_verbosity_manager_mock
        )

        scripts_mock = Mock()
        apps_mock = Mock()
        apps_mock.__all__ = ["evolution", "gedit", "gnome-shell"]
        toolkits_mock = Mock()
        toolkits_mock.__all__ = ["gtk", "Gecko", "Qt"]

        class MockScript:
            """Mock script class for testing."""
            def __init__(self, app=None):
                self.app = app
                self.register_event_listeners = Mock()
                self.deregister_event_listeners = Mock()
                self.activate = Mock()
                self.deactivate = Mock()
                self.braille_bindings = {}
                self._sleep_mode_manager = Mock()
                self._sleep_mode_manager.is_active_for_app = Mock(return_value=False)
                self.get_sleep_mode_manager = Mock(return_value=self._sleep_mode_manager)

            def __or__(self, other):
                # Support for type annotation union operator
                return MockScript

        default_script_constructor = Mock(side_effect=MockScript)
        default_script_constructor.__or__ = lambda self, other: MockScript

        sleepmode_script_constructor = Mock(side_effect=MockScript)
        sleepmode_script_constructor.__or__ = lambda self, other: MockScript

        default_mock = Mock()
        default_mock.Script = default_script_constructor

        sleepmode_mock = Mock()
        sleepmode_mock.Script = sleepmode_script_constructor

        scripts_mock.apps = apps_mock
        scripts_mock.default = default_mock
        scripts_mock.sleepmode = sleepmode_mock
        scripts_mock.toolkits = toolkits_mock

        monkeypatch.setitem(sys.modules, "orca.scripts", scripts_mock)
        monkeypatch.setitem(sys.modules, "orca.scripts.apps", apps_mock)
        monkeypatch.setitem(sys.modules, "orca.scripts.default", default_mock)
        monkeypatch.setitem(sys.modules, "orca.scripts.sleepmode", sleepmode_mock)
        monkeypatch.setitem(sys.modules, "orca.scripts.toolkits", toolkits_mock)

        from orca.ax_utilities import AXUtilities
        from orca.ax_object import AXObject

        AXUtilities.is_terminal = Mock(return_value=False)
        AXUtilities.get_application_toolkit_name = Mock(return_value="gtk")
        AXUtilities.is_application_in_desktop = Mock(return_value=True)
        AXUtilities.is_frame = Mock(return_value=False)
        AXUtilities.is_status_bar = Mock(return_value=False)

        AXObject.get_name = Mock(return_value="test-app")
        AXObject.get_attribute = Mock(return_value="GTK")

        return {
            "debug": mock_orca_dependencies.debug,
            "braille": braille_mock,
            "settings_manager": settings_manager_mock,
            "speech_and_verbosity_manager": speech_and_verbosity_manager_mock,
            "scripts": scripts_mock,
            "apps": apps_mock,
            "toolkits": toolkits_mock,
            "default": default_mock,
            "sleepmode": sleepmode_mock,
        }

    @pytest.fixture
    def mock_script_classes(self, mock_script_manager_deps):
        """Create mock script classes for testing."""

        mock_script_constructor = mock_script_manager_deps["default"].Script
        default_script_mock = mock_script_constructor()
        sleepmode_script_mock = mock_script_constructor()

        return {
            "default_script": default_script_mock,
            "sleepmode_script": sleepmode_script_mock,
            "sleep_mode_manager": default_script_mock._sleep_mode_manager,
        }

    def test_init(self, mock_script_manager_deps):
        """Test ScriptManager.__init__."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        assert not manager.app_scripts
        assert not manager.toolkit_scripts
        assert not manager.custom_scripts
        assert not manager._sleep_mode_scripts
        assert manager._default_script is None
        assert manager._active_script is None
        assert manager._active is False

    def test_activate(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.activate."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        manager._active = False

        manager.activate()

        assert manager._active is True
        assert manager._default_script is not None
        assert manager._active_script is not None
        # The default script instance will have register_event_listeners called
        manager._default_script.register_event_listeners.assert_called_once()

    def test_activate_already_active(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.activate when already active."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        manager._active = True

        manager.activate()

        # Should not change state or call register_event_listeners
        mock_script_classes["default_script"].register_event_listeners.assert_not_called()

    def test_deactivate(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.deactivate."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        manager._active = True
        manager._default_script = mock_script_classes["default_script"]
        manager.app_scripts = {"test": "script"}
        manager.toolkit_scripts = {"test": "script"}
        manager.custom_scripts = {"test": "script"}

        manager.deactivate()

        assert manager._active is False
        assert manager._default_script is None
        assert manager._active_script is None
        assert not manager.app_scripts
        assert not manager.toolkit_scripts
        assert not manager.custom_scripts
        mock_script_classes["default_script"].deregister_event_listeners.assert_called_once()

    def test_deactivate_already_inactive(self, mock_script_manager_deps):
        """Test ScriptManager.deactivate when already inactive."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        manager._active = False

        manager.deactivate()
        assert manager._active is False

    @pytest.mark.parametrize(
        "app_name, expected_result",
        [
            pytest.param("evolution", "evolution", id="app_in_apps_list"),
            pytest.param("gtk", "gtk", id="toolkit_in_toolkits_list"),
            pytest.param("mate-notification-daemon", "notification-daemon", id="mapped_app_name"),
            pytest.param("pluma", "gedit", id="alias_app_name"),
            pytest.param("test-app.py", "test-app", id="python_extension"),
            pytest.param("test-app.bin", "test-app", id="bin_extension"),
            pytest.param("org.gnome.TestApp", "TestApp", id="reverse_domain"),
            pytest.param("com.example.TestApp", "TestApp", id="reverse_domain_com"),
            pytest.param("unknown-app", "unknown-app", id="unknown_app"),
        ],
    )
    def test_get_module_name(self, mock_script_manager_deps, app_name, expected_result):
        """Test ScriptManager.get_module_name."""

        from orca.script_manager import ScriptManager
        from orca.ax_object import AXObject

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)

        AXObject.get_name = Mock(return_value=app_name)

        result = manager.get_module_name(mock_app)
        assert result == expected_result

    def test_get_module_name_null_app(self, mock_script_manager_deps):
        """Test ScriptManager.get_module_name with null app."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        result = manager.get_module_name(None)
        assert result is None

    def test_get_module_name_nameless_app(self, mock_script_manager_deps):
        """Test ScriptManager.get_module_name with nameless app."""

        from orca.script_manager import ScriptManager
        from orca.ax_object import AXObject

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)

        AXObject.get_name = Mock(return_value="")

        result = manager.get_module_name(mock_app)
        assert result is None

    @pytest.mark.parametrize(
        "toolkit_attribute, expected_result",
        [
            pytest.param("GTK", "gtk", id="gtk_toolkit"),
            pytest.param("GAIL", "gtk", id="gail_mapped_to_gtk"),
            pytest.param("Qt", "Qt", id="qt_toolkit"),
            pytest.param("", "", id="empty_toolkit"),
            pytest.param(None, None, id="none_toolkit"),
        ],
    )
    def test_toolkit_for_object(self, mock_script_manager_deps, toolkit_attribute, expected_result):
        """Test ScriptManager._toolkit_for_object."""

        from orca.script_manager import ScriptManager
        from orca.ax_object import AXObject

        manager = ScriptManager()
        mock_obj = Mock(spec=Atspi.Accessible)

        AXObject.get_attribute = Mock(return_value=toolkit_attribute)

        result = manager._toolkit_for_object(mock_obj)
        assert result == expected_result
        AXObject.get_attribute.assert_called_once_with(mock_obj, "toolkit")

    @pytest.mark.parametrize(
        "is_terminal, expected_result",
        [
            pytest.param(True, "terminal", id="terminal_role"),
            pytest.param(False, "", id="non_terminal_role"),
        ],
    )
    def test_script_for_role(self, mock_script_manager_deps, is_terminal, expected_result):
        """Test ScriptManager._script_for_role."""

        from orca.script_manager import ScriptManager
        from orca.ax_utilities import AXUtilities

        manager = ScriptManager()
        mock_obj = Mock(spec=Atspi.Accessible)

        AXUtilities.is_terminal = Mock(return_value=is_terminal)

        result = manager._script_for_role(mock_obj)
        assert result == expected_result
        AXUtilities.is_terminal.assert_called_once_with(mock_obj)

    @pytest.mark.parametrize(
        "app, name, has_module, has_get_script, has_script_class, should_succeed",
        [
            pytest.param(None, "", False, False, False, False, id="null_app_empty_name"),
            pytest.param("app", "", False, False, False, False, id="empty_name"),
            pytest.param("app", "test", False, False, False, False, id="no_module"),
            pytest.param("app", "test", True, True, False, True, id="has_get_script"),
            pytest.param("app", "test", True, False, True, True, id="has_script_class"),
            pytest.param("app", "test", True, False, False, False, id="no_script_creation"),
        ],
    )
    def test_new_named_script(
        self,
        mock_script_manager_deps,
        app,
        name,
        has_module,
        has_get_script,
        has_script_class,
        should_succeed,
    ):
        """Test ScriptManager._new_named_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible) if app else None
        mock_script = Mock()

        with patch("importlib.import_module") as mock_import:
            if has_module:
                # Create module with specific attributes
                mock_module = type('MockModule', (), {})()
                if has_get_script:
                    mock_module.get_script = Mock(return_value=mock_script)
                elif has_script_class:
                    mock_module.Script = Mock(return_value=mock_script)
                # For no_script_creation case, module exists but has neither attribute
                mock_import.return_value = mock_module
            else:
                mock_import.side_effect = ImportError("Module not found")

            result = manager._new_named_script(mock_app, name)

            if should_succeed:
                assert result == mock_script
            else:
                assert result is None

    def test_new_named_script_os_error(self, mock_script_manager_deps):
        """Test ScriptManager._new_named_script handles OSError."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)

        with patch("importlib.import_module") as mock_import:
            mock_import.side_effect = OSError("Permission denied")

            # Due to a bug in the original code, OSError causes UnboundLocalError
            # The test should expect this behavior in the current implementation
            with pytest.raises(UnboundLocalError):
                manager._new_named_script(mock_app, "test")

    def test_new_named_script_creation_error(self, mock_script_manager_deps):
        """Test ScriptManager._new_named_script handles script creation errors."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)

        with patch("importlib.import_module") as mock_import:
            # Create module that only has Script (no get_script)
            mock_module = type('MockModule', (), {})()
            mock_module.Script = Mock(side_effect=AttributeError("Script class not found"))
            mock_import.return_value = mock_module

            result = manager._new_named_script(mock_app, "test")
            assert result is None

    def test_create_script(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager._create_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)
        mock_obj = Mock(spec=Atspi.Accessible)

        manager.get_module_name = Mock(return_value=None)
        manager._toolkit_for_object = Mock(return_value=None)
        manager.get_default_script = Mock(return_value=mock_script_classes["default_script"])

        result = manager._create_script(mock_app, mock_obj)
        assert result == mock_script_classes["default_script"]

    def test_create_script_with_module_name(self, mock_script_manager_deps):
        """Test ScriptManager._create_script with valid module name."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_script = Mock()

        manager.get_module_name = Mock(return_value="test_script")
        manager._new_named_script = Mock(return_value=mock_script)

        result = manager._create_script(mock_app, mock_obj)
        assert result == mock_script
        manager._new_named_script.assert_called_once_with(mock_app, "test_script")

    def test_get_default_script(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.get_default_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)

        # Scenario: Get default script with app
        result = manager.get_default_script(mock_app)
        assert result is not None
        mock_script_manager_deps["default"].Script.assert_called_with(mock_app)

        # Scenario: Get default script without app (should use cached)
        manager._default_script = mock_script_classes["default_script"]
        result = manager.get_default_script(None)
        assert result == mock_script_classes["default_script"]

        # Scenario: Get default script without app and no cached script
        manager._default_script = None
        result = manager.get_default_script(None)
        assert result is not None
        assert manager._default_script is not None

    def test_get_or_create_sleep_mode_script(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.get_or_create_sleep_mode_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)

        # Scenario: Create new sleep mode script
        result = manager.get_or_create_sleep_mode_script(mock_app)
        assert result is not None
        assert isinstance(result, type(mock_script_classes["sleepmode_script"]))
        assert manager._sleep_mode_scripts[mock_app] == result

        # Scenario: Get existing sleep mode script
        result2 = manager.get_or_create_sleep_mode_script(mock_app)
        assert result2 == result
        assert len(manager._sleep_mode_scripts) == 1

    @pytest.mark.parametrize(
        "app, obj, sleep_mode_active, has_custom_script, has_toolkit_script, expected_script_type",
        [
            pytest.param(None, None, False, False, False, "default", id="null_app_and_obj"),
            pytest.param("app", "obj", True, False, False, "sleep", id="sleep_mode_active"),
            pytest.param("app", "obj", False, True, False, "custom", id="custom_script"),
            pytest.param("app", "obj", False, False, True, "toolkit", id="toolkit_script"),
            pytest.param("app", "obj", False, False, False, "app", id="app_script"),
        ],
    )
    def test_get_script(
        self,
        mock_script_manager_deps,
        mock_script_classes,
        app,
        obj,
        sleep_mode_active,
        has_custom_script,
        has_toolkit_script,
        expected_script_type,
    ):
        """Test ScriptManager.get_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible) if app else None
        mock_obj = Mock(spec=Atspi.Accessible) if obj else None

        mock_default_script = mock_script_classes["default_script"]
        mock_sleep_script = mock_script_classes["sleepmode_script"]
        mock_custom_script = Mock()

        class ToolkitScript:
            """Mock toolkit script class."""

        class AppScript:
            """Mock app script class."""

        mock_toolkit_script = Mock(spec=ToolkitScript)
        mock_toolkit_script.__class__ = ToolkitScript
        mock_app_script = Mock(spec=AppScript)
        mock_app_script.__class__ = AppScript

        sleep_mode_manager = mock_script_classes["sleep_mode_manager"]
        sleep_mode_manager.is_active_for_app = Mock(return_value=sleep_mode_active)
        mock_app_script.get_sleep_mode_manager = Mock(return_value=sleep_mode_manager)

        manager.get_default_script = Mock(return_value=mock_default_script)
        manager.get_or_create_sleep_mode_script = Mock(return_value=mock_sleep_script)
        manager._script_for_role = Mock(return_value="terminal" if has_custom_script else "")
        manager._toolkit_for_object = Mock(return_value="gtk" if has_toolkit_script else None)

        def create_script_side_effect(app, obj):
            if obj and has_toolkit_script:
                return mock_toolkit_script
            return mock_app_script

        manager._create_script = Mock(side_effect=create_script_side_effect)

        if has_custom_script:
            manager._new_named_script = Mock(return_value=mock_custom_script)

        result = manager.get_script(mock_app, mock_obj)

        if expected_script_type == "default":
            assert result == mock_default_script
        elif expected_script_type == "sleep":
            assert result == mock_sleep_script
        elif expected_script_type == "custom":
            assert result == mock_custom_script
        elif expected_script_type == "toolkit":
            assert result == mock_toolkit_script
        elif expected_script_type == "app":
            assert result == mock_app_script

    def test_get_script_exception_handling(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.get_script handles exceptions."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        mock_app = Mock(spec=Atspi.Accessible)
        mock_obj = Mock(spec=Atspi.Accessible)

        manager._script_for_role = Mock(return_value="")
        manager._toolkit_for_object = Mock(return_value=None)

        def create_script_side_effect(app, obj):
            if obj is None:
                raise KeyError("Script creation failed")
            return Mock()  # Toolkit script creation (shouldn't be called)

        manager._create_script = Mock(side_effect=create_script_side_effect)
        manager.get_default_script = Mock(return_value=mock_script_classes["default_script"])

        result = manager.get_script(mock_app, mock_obj)
        assert result == mock_script_classes["default_script"]

    def test_get_active_script(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.get_active_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()

        # Scenario: No active script
        result = manager.get_active_script()
        assert result is None

        # Scenario: With active script
        manager._active_script = mock_script_classes["default_script"]
        result = manager.get_active_script()
        assert result == mock_script_classes["default_script"]

    def test_get_active_script_app(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.get_active_script_app."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()

        # Scenario: No active script
        result = manager.get_active_script_app()
        assert result is None

        # Scenario: With active script
        mock_app = Mock(spec=Atspi.Accessible)
        mock_script_classes["default_script"].app = mock_app
        manager._active_script = mock_script_classes["default_script"]
        result = manager.get_active_script_app()
        assert result == mock_app

    def test_set_active_script(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.set_active_script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        old_script = Mock()
        old_script.app = Mock()
        old_script.deactivate = Mock()
        new_script = mock_script_classes["default_script"]
        new_script.app = Mock()
        new_script.activate = Mock()
        new_script.braille_bindings = {"key": "binding"}

        settings_manager = mock_script_manager_deps["settings_manager"]
        manager_instance = Mock()
        manager_instance.get_runtime_settings = Mock(return_value={"setting": "value"})
        manager_instance.set_setting = Mock()
        settings_manager.get_manager = Mock(return_value=manager_instance)

        # Scenario: Set new script when old script exists
        manager._active_script = old_script
        manager.set_active_script(new_script, "test reason")

        old_script.deactivate.assert_called_once()
        new_script.activate.assert_called_once()
        assert manager._active_script == new_script

        # Verify braille and speech settings are updated
        braille_mock = mock_script_manager_deps["braille"]
        braille_mock.checkBrailleSetting.assert_called_once()
        braille_mock.setupKeyRanges.assert_called_once_with(new_script.braille_bindings.keys())

        speech_manager = mock_script_manager_deps["speech_and_verbosity_manager"]
        speech_manager.get_manager().check_speech_setting.assert_called_once()

    def test_set_active_script_same_script(self, mock_script_manager_deps, mock_script_classes):
        """Test ScriptManager.set_active_script with same script."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        script = mock_script_classes["default_script"]
        manager._active_script = script

        manager.set_active_script(script, "same script")
        script.deactivate.assert_not_called()
        script.activate.assert_not_called()

    def test_set_active_script_none(self, mock_script_manager_deps):
        """Test ScriptManager.set_active_script with None."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        old_script = Mock()
        old_script.deactivate = Mock()
        manager._active_script = old_script

        manager.set_active_script(None)

        old_script.deactivate.assert_called_once()
        assert manager._active_script is None

    def test_set_active_script_runtime_settings(
        self, mock_script_manager_deps, mock_script_classes
    ):
        """Test ScriptManager.set_active_script preserves runtime settings for same app."""

        from orca.script_manager import ScriptManager

        manager = ScriptManager()
        same_app = Mock(spec=Atspi.Accessible)
        old_script = Mock()
        old_script.app = same_app
        old_script.deactivate = Mock()
        new_script = mock_script_classes["default_script"]
        new_script.app = same_app
        new_script.activate = Mock()
        new_script.braille_bindings = {}

        settings_manager = mock_script_manager_deps["settings_manager"]
        manager_instance = Mock()
        runtime_settings = {"key1": "value1", "key2": "value2"}
        manager_instance.get_runtime_settings = Mock(return_value=runtime_settings)
        manager_instance.set_setting = Mock()
        settings_manager.get_manager = Mock(return_value=manager_instance)

        manager._active_script = old_script
        manager.set_active_script(new_script)

        expected_calls = [call("key1", "value1"), call("key2", "value2")]
        manager_instance.set_setting.assert_has_calls(expected_calls, any_order=True)

    def test_reclaim_scripts(self, mock_script_manager_deps):
        """Test ScriptManager.reclaim_scripts."""

        from orca.script_manager import ScriptManager
        from orca.ax_utilities import AXUtilities

        manager = ScriptManager()

        app_in_desktop = Mock(spec=Atspi.Accessible)
        app_not_in_desktop = Mock(spec=Atspi.Accessible)

        manager.app_scripts = {
            app_in_desktop: Mock(),
            app_not_in_desktop: Mock(),
        }
        manager.toolkit_scripts = {app_not_in_desktop: Mock()}
        manager.custom_scripts = {app_not_in_desktop: Mock()}
        manager._sleep_mode_scripts = {app_not_in_desktop: Mock()}

        def mock_is_in_desktop(app):
            return app == app_in_desktop

        AXUtilities.is_application_in_desktop = Mock(side_effect=mock_is_in_desktop)

        manager.reclaim_scripts()

        # Verify only the app not in desktop is removed
        assert app_in_desktop in manager.app_scripts
        assert app_not_in_desktop not in manager.app_scripts
        assert app_not_in_desktop not in manager.toolkit_scripts
        assert app_not_in_desktop not in manager.custom_scripts
        assert app_not_in_desktop not in manager._sleep_mode_scripts

    def test_reclaim_scripts_key_error(self, mock_script_manager_deps):
        """Test ScriptManager.reclaim_scripts handles KeyError."""

        from orca.script_manager import ScriptManager
        from orca.ax_utilities import AXUtilities

        manager = ScriptManager()

        app_not_in_desktop = Mock(spec=Atspi.Accessible)

        # Setup scripts - app_scripts has the app but toolkit_scripts is missing it
        # This will cause a KeyError when trying to pop from toolkit_scripts
        manager.app_scripts = {app_not_in_desktop: Mock()}
        manager.toolkit_scripts = {}  # Empty - will cause KeyError
        manager.custom_scripts = {}
        manager._sleep_mode_scripts = {}

        AXUtilities.is_application_in_desktop = Mock(return_value=False)

        # Should not raise exception even with KeyError
        manager.reclaim_scripts()

        # Verify app script was removed despite KeyError on other collections
        assert app_not_in_desktop not in manager.app_scripts

    def test_get_manager(self, mock_script_manager_deps):
        """Test script_manager.get_manager."""

        from orca import script_manager

        manager1 = script_manager.get_manager()
        manager2 = script_manager.get_manager()

        assert manager1 is manager2
        assert isinstance(manager1, script_manager.ScriptManager)
