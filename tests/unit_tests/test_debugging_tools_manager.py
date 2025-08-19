# Unit tests for debugging_tools_manager.py methods.
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Unit tests for debugging_tools_manager.py methods."""

from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import call
import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestDebuggingToolsManager:
    """Test DebuggingToolsManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for debugging_tools_manager dependencies."""

        additional_modules = [
            "orca.orca_platform",
            "orca.ax_utilities",
            "orca.ax_utilities_debugging",
            "faulthandler",
            "subprocess",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.debugFile = None
        debug_mock.debugLevel = 1000
        debug_mock.LEVEL_ALL = 0
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 900
        debug_mock.LEVEL_SEVERE = 1000
        debug_mock.LEVEL_OFF = 10000
        debug_mock.print_message = test_context.Mock()

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.DEBUG_CYCLE_LEVEL = "cycleDebugLevel"
        cmdnames_mock.DEBUG_CLEAR_ATSPI_CACHE_FOR_APPLICATION = "clearAtSpiCache"
        cmdnames_mock.DEBUG_CAPTURE_SNAPSHOT = "captureSnapshot"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )
        input_event_mock.InputEvent = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        key_bindings_instance = test_context.Mock()
        key_bindings_instance.is_empty = test_context.Mock(return_value=True)
        key_bindings_instance.remove_key_grabs = test_context.Mock(return_value=None)
        key_bindings_instance.add = test_context.Mock(return_value=None)
        keybindings_mock.KeyBindings = test_context.Mock(return_value=key_bindings_instance)
        keybindings_mock.KeyBinding = test_context.Mock()
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.NO_MODIFIER_MASK = 0

        messages_mock = essential_modules["orca.messages"]
        messages_mock.DEBUG_CLEAR_CACHE_FAILED = "Failed to clear cache"
        messages_mock.DEBUG_CLEAR_CACHE = "Cache cleared"
        messages_mock.DEBUG_CAPTURE_SNAPSHOT_START = "Snapshot started"
        messages_mock.DEBUG_CAPTURE_SNAPSHOT_END = "Snapshot ended"

        orca_platform_mock = essential_modules["orca.orca_platform"]
        orca_platform_mock.version = "3.50.0"
        orca_platform_mock.revision = "abc123"

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.override_key_bindings = test_context.Mock(
            return_value=key_bindings_instance
        )
        settings_manager_instance.get_overridden_settings_for_debugging = test_context.Mock(
            return_value={}
        )
        settings_manager_instance.customized_settings = {}
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_active_mode_and_object_of_interest = test_context.Mock(
            return_value=("focus", test_context.Mock(spec=Atspi.Accessible))
        )
        focus_manager_mock.get_manager = test_context.Mock(return_value=focus_manager_instance)

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.get_name = test_context.Mock(return_value="TestApp")
        ax_object_mock.clear_cache = test_context.Mock()

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.get_application = test_context.Mock(
            return_value=test_context.Mock(spec=Atspi.Accessible)
        )
        test_apps = [
            test_context.Mock(spec=Atspi.Accessible),
            test_context.Mock(spec=Atspi.Accessible),
        ]
        ax_utilities_mock.get_all_applications = test_context.Mock(return_value=test_apps)
        ax_utilities_mock.get_process_id = test_context.Mock(return_value=12345)
        ax_utilities_mock.is_application_unresponsive = test_context.Mock(return_value=False)

        ax_utilities_debugging_mock = essential_modules["orca.ax_utilities_debugging"]
        ax_utilities_debugging_mock.as_string = test_context.Mock(return_value="debug_info")

        faulthandler_mock = essential_modules["faulthandler"]
        faulthandler_mock.enable = test_context.Mock()

        subprocess_mock = essential_modules["subprocess"]
        subprocess_mock.getoutput = test_context.Mock(return_value="test_command")
        subprocess_mock.SubprocessError = Exception

        essential_modules["input_event_handler"] = input_event_handler_mock
        essential_modules["key_bindings_instance"] = key_bindings_instance
        essential_modules["settings_manager_instance"] = settings_manager_instance
        essential_modules["focus_manager_instance"] = focus_manager_instance

        return essential_modules

    @pytest.mark.parametrize(
        "debug_file_config",
        [
            pytest.param(None, id="basic"),
            pytest.param("mock_file", id="with_debug_file"),
            pytest.param(None, id="without_debug_file"),
        ],
    )
    def test_init_scenarios(
        self,
        test_context: OrcaTestContext,
        debug_file_config: str | None,
    ) -> None:
        """Test DebuggingToolsManager.__init__ with various scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        if debug_file_config == "mock_file":
            debug_file_mock = test_context.Mock()
            debug_file_mock.name = "/tmp/debug.log"
            essential_modules["orca.debug"].debugFile = debug_file_mock
            test_context.patch("os.path.exists", return_value=True)
        elif debug_file_config is None:
            essential_modules["orca.debug"].debugFile = None

        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()

        assert manager is not None
        assert manager._handlers is not None
        assert manager._bindings is not None
        assert isinstance(manager._handlers, dict)

    @pytest.mark.parametrize(
        "method_name,refresh,is_empty,expects_remove_grabs,expected_type",
        [
            pytest.param("get_bindings", False, True, False, None, id="bindings_no_refresh_empty"),
            pytest.param("get_bindings", True, True, True, None, id="bindings_refresh_empty"),
            pytest.param(
                "get_bindings", False, False, False, None, id="bindings_no_refresh_not_empty"
            ),
            pytest.param("get_handlers", False, False, False, dict, id="handlers_no_refresh"),
            pytest.param("get_handlers", True, False, False, dict, id="handlers_refresh"),
        ],
    )
    def test_get_methods(
        self,
        test_context: OrcaTestContext,
        method_name: str,
        refresh: bool,
        is_empty: bool,
        expects_remove_grabs: bool,
        expected_type: type | None,
    ) -> None:
        """Test DebuggingToolsManager.get_bindings and get_handlers methods."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()

        if method_name == "get_bindings" and not is_empty:
            test_context.patch_object(manager._bindings, "is_empty", return_value=False)

        method = getattr(manager, method_name)
        if method_name == "get_bindings":
            result = method(refresh=refresh, is_desktop=not refresh)
            if not is_empty and not refresh:
                assert result == manager._bindings
        else:
            result = method(refresh=refresh)

        assert result is not None
        if expected_type:
            assert isinstance(result, expected_type)

        if refresh:
            if method_name == "get_bindings":
                essential_modules["orca.keybindings"].KeyBindings.assert_called()
            essential_modules["orca.debug"].print_message.assert_called()

        if expects_remove_grabs:
            key_bindings_instance = essential_modules["key_bindings_instance"]
            key_bindings_instance.remove_key_grabs.assert_called_once()

    @pytest.mark.parametrize(
        "setup_method,expected_attrs",
        [
            pytest.param(
                "_setup_handlers",
                ["cycleDebugLevelHandler", "clear_atspi_app_cache", "capture_snapshot"],
                id="setup_handlers",
            ),
            pytest.param("_setup_bindings", [], id="setup_bindings"),
        ],
    )
    def test_setup_methods(
        self,
        test_context: OrcaTestContext,
        setup_method: str,
        expected_attrs: list[str],
    ) -> None:
        """Test DebuggingToolsManager setup methods."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()
        method = getattr(manager, setup_method)
        method()

        if setup_method == "_setup_handlers":
            for attr in expected_attrs:
                assert attr in manager._handlers
            assert essential_modules["orca.input_event"].InputEventHandler.call_count >= 3
        elif setup_method == "_setup_bindings":
            essential_modules["orca.keybindings"].KeyBindings.assert_called()
            settings_instance = essential_modules["settings_manager_instance"]
            settings_instance.override_key_bindings.assert_called_once()

    @pytest.mark.parametrize(
        "initial_level,expected_level,expected_message,expected_brief,has_event",
        [
            pytest.param(0, 800, "Debug level info.", "info", False, id="all_to_info"),
            pytest.param(10000, 0, "Debug level all.", "all", False, id="off_to_all"),
            pytest.param(
                800, 900, "Debug level warning.", "warning", True, id="info_to_warning_with_event"
            ),
            pytest.param(900, 1000, "Debug level severe.", "severe", False, id="warning_to_severe"),
            pytest.param(1000, 10000, "Debug level off.", "off", False, id="severe_to_off"),
        ],
    )
    def test_cycle_debug_level_comprehensive(
        self,
        test_context: OrcaTestContext,
        initial_level: int,
        expected_level: int,
        expected_message: str,
        expected_brief: str,
        has_event: bool,
    ) -> None:
        """Test DebuggingToolsManager._cycle_debug_level cycling through all levels."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.debug"].debugLevel = initial_level
        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()
        script_mock = test_context.Mock()
        event_mock = test_context.Mock() if has_event else None

        result = manager._cycle_debug_level(script_mock, event_mock)
        assert result
        assert essential_modules["orca.debug"].debugLevel == expected_level
        script_mock.present_message.assert_called_with(expected_message, expected_brief)

    @pytest.mark.parametrize(
        "test_scenario,focus_object,application_object,expected_message,"
        "expects_clear_cache,expects_debug_call",
        [
            pytest.param(
                "success",
                "mock_obj",
                "mock_app",
                "Cache cleared",
                True,
                False,
                id="successful_cache_clear",
            ),
            pytest.param(
                "null_object",
                None,
                "mock_app",
                "Failed to clear cache",
                False,
                True,
                id="null_object_failure",
            ),
            pytest.param(
                "null_application",
                "mock_obj",
                None,
                "Failed to clear cache",
                False,
                True,
                id="null_application_failure",
            ),
        ],
    )
    def test_clear_atspi_app_cache_comprehensive(
        self,
        test_context: OrcaTestContext,
        test_scenario: str,
        focus_object: str | None,
        application_object: str | None,
        expected_message: str,
        expects_clear_cache: bool,
        expects_debug_call: bool,
    ) -> None:
        """Test DebuggingToolsManager._clear_atspi_app_cache with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()
        script_mock = test_context.Mock()

        test_obj = test_context.Mock(spec=Atspi.Accessible) if focus_object else None
        test_app = test_context.Mock(spec=Atspi.Accessible) if application_object else None

        if test_scenario == "null_object":
            focus_instance = essential_modules["focus_manager_instance"]
            focus_instance.get_active_mode_and_object_of_interest.return_value = ("focus", None)
        else:
            mock_focus_instance = test_context.Mock()
            mock_focus_instance.get_active_mode_and_object_of_interest.return_value = (
                "focus",
                test_obj,
            )
            test_context.patch(
                "orca.debugging_tools_manager.focus_manager.get_manager",
                return_value=mock_focus_instance
            )

        test_context.patch(
            "orca.debugging_tools_manager.AXUtilities.get_application", return_value=test_app
        )

        mock_clear_cache = test_context.patch(
            "orca.debugging_tools_manager.AXObject.clear_cache"
        )
        mock_debug_print = test_context.patch(
            "orca.debugging_tools_manager.debug.print_message"
        )

        result = manager._clear_atspi_app_cache(script_mock)
        assert result
        script_mock.present_message.assert_called_with(expected_message)

        if expects_clear_cache:
            mock_clear_cache.assert_called_once_with(
                test_app, recursive=True, reason="User request."
            )
        else:
            mock_clear_cache.assert_not_called()

        if expects_debug_call:
            if test_scenario == "null_object":
                debug_calls = [
                    call
                    for call in essential_modules["orca.debug"].print_message.call_args_list
                    if "Cannot clear cache on null object" in str(call)
                ]
                assert len(debug_calls) >= 1
            else:
                mock_debug_print.assert_called()

    @pytest.mark.parametrize(
        "test_method,scenario_data",
        [
            pytest.param(
                "_capture_snapshot",
                {
                    "original_level": 1,
                    "expected_calls": ["Snapshot started", "Snapshot ended"],
                    "expects_debug": True,
                    "expects_print_running": True,
                },
                id="capture_snapshot",
            ),
            pytest.param(
                "_get_running_applications_as_string_iter",
                {
                    "is_command_line": True,
                    "app_count": 2,
                    "expected_length": 3,
                    "header_contains": "Desktop has 2 app(s):",
                },
                id="get_running_apps_cli",
            ),
            pytest.param(
                "_get_running_applications_as_string_iter",
                {
                    "is_command_line": False,
                    "app_count": 1,
                    "expected_length": 2,
                    "header_contains": "DEBUGGING TOOLS MANAGER:",
                },
                id="get_running_apps_not_cli",
            ),
        ],
    )
    def test_debug_utility_methods(
        self, test_context: OrcaTestContext, test_method: str, scenario_data: dict
    ) -> None:
        """Test DebuggingToolsManager debug utility methods."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()
        script_mock = test_context.Mock()

        if test_method == "_capture_snapshot":
            essential_modules["orca.debug"].debugLevel = scenario_data["original_level"]
            mock_print_running = test_context.Mock()
            test_context.patch_object(
                manager, "print_running_applications", side_effect=mock_print_running
            )

            result = manager._capture_snapshot(script_mock)
            assert result
            assert essential_modules["orca.debug"].debugLevel == scenario_data["original_level"]

            expected_calls = [call(msg) for msg in scenario_data["expected_calls"]]
            script_mock.present_message.assert_has_calls(expected_calls)

            if scenario_data["expects_debug"]:
                essential_modules["orca.debug"].print_message.assert_called()
            if scenario_data["expects_print_running"]:
                mock_print_running.assert_called_once()

        elif test_method == "_get_running_applications_as_string_iter":
            app_count = scenario_data["app_count"]
            test_apps = [test_context.Mock(spec=Atspi.Accessible) for _ in range(app_count)]

            test_context.patch(
                "orca.debugging_tools_manager.AXUtilities.get_all_applications",
                return_value=test_apps,
            )
            test_context.patch(
                "orca.debugging_tools_manager.AXUtilities.get_process_id", return_value=12345
            )
            test_context.patch(
                "orca.debugging_tools_manager.AXUtilities.is_application_unresponsive",
                return_value=False,
            )
            test_context.patch(
                "orca.debugging_tools_manager.AXObject.get_name", return_value="TestApp"
            )
            test_context.patch(
                "orca.debugging_tools_manager.subprocess.getoutput", return_value="test_command"
            )

            result_list = list(
                manager._get_running_applications_as_string_iter(
                    is_command_line=scenario_data["is_command_line"]
                )
            )
            assert len(result_list) == scenario_data["expected_length"]
            assert scenario_data["header_contains"] in result_list[0]

    @pytest.mark.parametrize(
        "force,is_command_line,debug_level,expects_method_call,expects_debug,expects_stdout",
        [
            pytest.param(True, False, 1000, True, True, False, id="force_true_not_cli"),
            pytest.param(False, True, 1000, True, False, True, id="no_force_cli"),
            pytest.param(False, False, 900, False, False, False, id="debug_level_too_low"),
        ],
    )
    def test_print_running_applications(
        self,
        test_context: OrcaTestContext,
        force: bool,
        is_command_line: bool,
        debug_level: int,
        expects_method_call: bool,
        expects_debug: bool,
        expects_stdout: bool,
        capsys,
    ) -> None:
        """Test DebuggingToolsManager.print_running_applications."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.debug"].debugLevel = debug_level
        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()
        expected_output = ["Header", "App 1", "App 2"]
        mock_get_apps = test_context.patch_object(
            manager, "_get_running_applications_as_string_iter", return_value=expected_output
        )

        manager.print_running_applications(force=force, is_command_line=is_command_line)

        if not expects_method_call:
            mock_get_apps.assert_not_called()
        else:
            mock_get_apps.assert_called_once()
            if expects_debug:
                expected_calls = [call(1000, line, True) for line in expected_output]
                essential_modules["orca.debug"].print_message.assert_has_calls(expected_calls)
            if expects_stdout:
                captured = capsys.readouterr()
                for line in expected_output:
                    assert line in captured.out

    @pytest.mark.parametrize(
        "is_command_line,revision,session_type,session_desktop,"
        "expects_stdout,expects_revision,expects_session",
        [
            pytest.param(
                True,
                "abc123",
                "wayland",
                "gnome",
                True,
                True,
                True,
                id="cli_with_revision_and_session",
            ),
            pytest.param(
                False,
                "abc123",
                "x11",
                "",
                False,
                True,
                True,
                id="not_cli_x11_no_desktop",
            ),
            pytest.param(
                False,
                None,
                "wayland",
                "gnome",
                False,
                False,
                True,
                id="not_cli_no_revision",
            ),
            pytest.param(
                False,
                "abc123",
                None,
                None,
                False,
                True,
                False,
                id="not_cli_no_session_env",
            ),
        ],
    )
    def test_print_session_details_comprehensive(  # pylint: disable=too-many-branches
        self,
        test_context: OrcaTestContext,
        is_command_line: bool,
        revision: str | None,
        session_type: str | None,
        session_desktop: str | None,
        expects_stdout: bool,
        expects_revision: bool,
        expects_session: bool,
        capsys,
    ) -> None:
        """Test DebuggingToolsManager.print_session_details with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        if revision is None:
            essential_modules["orca.orca_platform"].revision = None

        mock_atspi = test_context.Mock()
        mock_atspi.get_version.return_value = (2, 48, 0)
        test_context.patch("gi.repository.Atspi", new=mock_atspi)

        env_patches = {}
        remove_vars = []

        if session_type:
            env_patches["XDG_SESSION_TYPE"] = session_type
        else:
            remove_vars.append("XDG_SESSION_TYPE")

        if session_desktop:
            env_patches["XDG_SESSION_DESKTOP"] = session_desktop
        else:
            remove_vars.append("XDG_SESSION_DESKTOP")

        test_context.patch_env(env_patches, remove_vars=remove_vars)

        from orca.debugging_tools_manager import DebuggingToolsManager

        manager = DebuggingToolsManager()
        manager.print_session_details(is_command_line=is_command_line)

        if expects_stdout:
            captured = capsys.readouterr()
            assert "Orca version 3.50.0" in captured.out
            assert "AT-SPI2 version: 2.48.0" in captured.out

            if expects_revision:
                assert "rev abc123" in captured.out

            if expects_session:
                if session_desktop:
                    assert f"Session: {session_type} {session_desktop}" in captured.out
                else:
                    assert f"Session: {session_type}" in captured.out
        else:
            session_calls = [
                call
                for call in essential_modules["orca.debug"].print_message.call_args_list
                if "Orca version" in str(call)
            ]
            assert len(session_calls) >= 1
            call_args = session_calls[0]

            if not is_command_line:
                assert "DEBUGGING TOOLS MANAGER:" in call_args[0][1]

            assert "Orca version 3.50.0" in call_args[0][1]
            assert "AT-SPI2 version: 2.48.0" in call_args[0][1]

            if expects_revision:
                assert "rev abc123" in call_args[0][1]
            else:
                assert "rev" not in call_args[0][1]

            if expects_session:
                if session_desktop:
                    assert f"Session: {session_type} {session_desktop}" in call_args[0][1]
                else:
                    assert f"Session: {session_type}" in call_args[0][1]
            else:
                assert "Session:" not in call_args[0][1]

    def test_get_manager_singleton(self, test_context: OrcaTestContext) -> None:
        """Test debugging_tools_manager.get_manager singleton behavior."""
        self._setup_dependencies(test_context)
        from orca import debugging_tools_manager

        manager1 = debugging_tools_manager.get_manager()
        manager2 = debugging_tools_manager.get_manager()

        assert manager1 is manager2
        assert manager1._handlers is not None
        assert manager1._bindings is not None
