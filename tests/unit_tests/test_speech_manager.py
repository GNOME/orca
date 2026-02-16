# Unit tests for speech_manager.py methods.
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

"""Unit tests for speech_manager.py methods."""

from __future__ import annotations

import queue
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestSpeechManager:
    """Test SpeechManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for speech_manager dependencies."""

        additional_modules = [
            "orca.speech",
            "orca.speechserver",
            "orca.acss",
            "orca.presentation_manager",
            "orca.preferences_grid_base",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_mock = essential_modules["orca.settings"]
        settings_mock.speechFactoryModules = ["spiel", "speechdispatcherfactory"]
        settings_mock.speechServerInfo = None
        settings_mock.speechServerFactory = "spiel"
        settings_mock.voices = {}
        settings_mock.DEFAULT_VOICE = "default"

        # Set up constants for enum testing
        settings_mock.CAPITALIZATION_STYLE_NONE = "none"
        settings_mock.CAPITALIZATION_STYLE_SPELL = "spell"
        settings_mock.CAPITALIZATION_STYLE_ICON = "icon"
        settings_mock.PUNCTUATION_STYLE_NONE = 3
        settings_mock.PUNCTUATION_STYLE_SOME = 2
        settings_mock.PUNCTUATION_STYLE_MOST = 1
        settings_mock.PUNCTUATION_STYLE_ALL = 0

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance._prefs_dir = "/tmp/orca-test"
        settings_manager_instance._load_user_customizations.return_value = True
        settings_manager_mock.get_manager.return_value = settings_manager_instance

        settings_mock.enableSpeech = True

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_manager_mock.get_manager.return_value = test_context.Mock()

        dbus_service_mock = essential_modules["orca.dbus_service"]
        dbus_service_mock.get_remote_controller.return_value = test_context.Mock()

        def passthrough_decorator(func):
            return func

        dbus_service_mock.getter = passthrough_decorator
        dbus_service_mock.setter = passthrough_decorator
        dbus_service_mock.command = passthrough_decorator
        dbus_service_mock.parameterized_command = passthrough_decorator

        speech_mock = essential_modules["orca.speech"]
        speech_mock.speak.return_value = None
        speech_mock.get_mute_speech.return_value = False

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message.return_value = None
        debug_mock.print_tokens.return_value = None
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 900

        acss_mock = essential_modules["orca.acss"]
        acss_mock.ACSS = test_context.Mock()
        acss_mock.ACSS.RATE = "rate"
        acss_mock.ACSS.AVERAGE_PITCH = "average-pitch"
        acss_mock.ACSS.GAIN = "gain"
        acss_mock.ACSS.FAMILY = "family"

        speechserver_mock = essential_modules["orca.speechserver"]
        speechserver_mock.VoiceFamily = test_context.Mock()
        speechserver_mock.VoiceFamily.NAME = "name"
        speechserver_mock.VoiceFamily.LANG = "lang"
        speechserver_mock.VoiceFamily.DIALECT = "dialect"
        speechserver_mock.VoiceFamily.VARIANT = "variant"

        orca_i18n_mock = essential_modules["orca.orca_i18n"]
        orca_i18n_mock._ = lambda x: x
        orca_i18n_mock.C_ = lambda c, x: x
        orca_i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test manager initialization and D-Bus registration."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        # Verify D-Bus registration occurred
        controller = essential_modules["orca.dbus_service"].get_remote_controller()
        controller.register_decorated_module.assert_called_with("SpeechManager", manager)

    def test_set_up_commands(self, test_context: OrcaTestContext) -> None:
        """Test that set_up_commands registers commands in CommandManager."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager
        from orca import command_manager

        manager = SpeechManager()
        manager.set_up_commands()

        # Verify commands are registered in CommandManager
        cmd_manager = command_manager.get_manager()
        assert cmd_manager.get_command("toggleSilenceSpeechHandler") is not None
        assert cmd_manager.get_command("cycleCapitalizationStyleHandler") is not None
        assert cmd_manager.get_command("cycleSpeakingPunctuationLevelHandler") is not None
        assert cmd_manager.get_command("cycleSynthesizerHandler") is not None

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "server_none", "scenario": "none_server", "expected_result": None},
            {"id": "server_timeout", "scenario": "timeout", "expected_result": None},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_server_scenarios(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test _get_server method scenarios."""
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        if case["scenario"] == "none_server":
            manager._server = None
        else:  # timeout scenario
            mock_speech_server = test_context.Mock()
            manager._server = mock_speech_server

            def mock_queue_constructor():
                mock_queue = test_context.Mock()
                mock_queue.get.side_effect = queue.Empty()
                return mock_queue

            test_context.patch("queue.Queue", new=mock_queue_constructor)

        result = manager._get_server()
        assert result is case["expected_result"]

    def test_get_server_module_map_import_errors(self, test_context: OrcaTestContext) -> None:
        """Test _get_server_module_map method with import errors."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        essential_modules["orca.settings"].speechFactoryModules = ["nonexistent_module"]

        def mock_import_module(name) -> None:
            raise ImportError("Module not found")

        test_context.patch("importlib.import_module", new=mock_import_module)
        manager = SpeechManager()
        result = manager._get_server_module_map()
        assert not result

    def test_switch_server_invalid(self, test_context: OrcaTestContext) -> None:
        """Test _switch_server method with invalid server."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server_module_map", return_value={})
        result = manager._switch_server("Invalid Server")
        assert result is False

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "none", "server_return": None, "expected_result": ""},
            {"id": "with_server", "server_return": "mock_server", "expected_result": "Test Server"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_current_server_scenarios(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_current_server method with various scenarios."""
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        if case["server_return"] == "mock_server":
            mock_server = test_context.Mock()
            mock_server.get_factory_name.return_value = "Test Server"
            test_context.patch_object(manager, "_get_server", return_value=mock_server)
        else:
            test_context.patch_object(manager, "_get_server", return_value=case["server_return"])

        result = manager.get_current_server()
        assert result == case["expected_result"]

    def test_get_current_synthesizer_none(self, test_context: OrcaTestContext) -> None:
        """Test get_current_synthesizer method when server is None."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=None)
        result = manager.get_current_synthesizer()
        assert result == ""

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "set_current_synthesizer",
                "method_name": "set_current_synthesizer",
                "method_args": ["espeak-ng"],
                "expected_result": False,
            },
            {
                "id": "get_available_synthesizers",
                "method_name": "get_available_synthesizers",
                "method_args": [],
                "expected_result": [],
            },
            {
                "id": "get_available_voices",
                "method_name": "get_available_voices",
                "method_args": [],
                "expected_result": [],
            },
            {
                "id": "get_voices_for_language",
                "method_name": "get_voices_for_language",
                "method_args": ["en"],
                "expected_result": [],
            },
            {
                "id": "get_current_voice",
                "method_name": "get_current_voice",
                "method_args": [],
                "expected_result": "",
            },
            {
                "id": "set_current_voice",
                "method_name": "set_current_voice",
                "method_args": ["en"],
                "expected_result": False,
            },
            {
                "id": "interrupt_speech",
                "method_name": "interrupt_speech",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "shutdown_speech",
                "method_name": "shutdown_speech",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "decrease_rate",
                "method_name": "decrease_rate",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "increase_rate",
                "method_name": "increase_rate",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "decrease_pitch",
                "method_name": "decrease_pitch",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "increase_pitch",
                "method_name": "increase_pitch",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "decrease_volume",
                "method_name": "decrease_volume",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "increase_volume",
                "method_name": "increase_volume",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "update_capitalization_style",
                "method_name": "update_capitalization_style",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "update_punctuation_level",
                "method_name": "update_punctuation_level",
                "method_args": [],
                "expected_result": True,
            },
            {
                "id": "update_synthesizer",
                "method_name": "update_synthesizer",
                "method_args": [],
                "expected_result": None,
            },
            {
                "id": "cycle_synthesizer",
                "method_name": "cycle_synthesizer",
                "method_args": [],
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_methods_no_server(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test various methods when speech server is None."""
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=None)

        method = getattr(manager, case["method_name"])
        result = method(*case["method_args"])

        if case["expected_result"] is False:
            assert not result
        else:
            assert result == case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "get_capitalization_style", "setting_value": "spell", "expected": "spell"},
            {"id": "get_capitalization_style_none", "setting_value": "none", "expected": "none"},
            {"id": "get_capitalization_style_icon", "setting_value": "icon", "expected": "icon"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_capitalization_style(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_capitalization_style method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].capitalizationStyle = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_capitalization_style()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_capitalization_style_valid", "input_value": "spell", "expected": True},
            {"id": "set_capitalization_style_none", "input_value": "none", "expected": True},
            {"id": "set_capitalization_style_icon", "input_value": "icon", "expected": True},
            {"id": "set_capitalization_style_invalid", "input_value": "invalid", "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_capitalization_style(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_capitalization_style method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        mock_update = test_context.Mock()
        test_context.patch_object(manager, "update_capitalization_style", new=mock_update)

        result = manager.set_capitalization_style(case["input_value"])
        assert result == case["expected"]

        if case["expected"]:
            assert manager.get_capitalization_style() == case["input_value"]
            mock_update.assert_called_once()
        else:
            mock_update.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "punctuation_none", "setting_value": 3, "expected": "none"},
            {"id": "punctuation_some", "setting_value": 2, "expected": "some"},
            {"id": "punctuation_most", "setting_value": 1, "expected": "most"},
            {"id": "punctuation_all", "setting_value": 0, "expected": "all"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_punctuation_level(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_punctuation_level method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].verbalizePunctuationStyle = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_punctuation_level()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "set_punctuation_none",
                "input_value": "none",
                "expected": True,
                "setting_int": 3,
            },
            {
                "id": "set_punctuation_some",
                "input_value": "some",
                "expected": True,
                "setting_int": 2,
            },
            {
                "id": "set_punctuation_most",
                "input_value": "most",
                "expected": True,
                "setting_int": 1,
            },
            {"id": "set_punctuation_all", "input_value": "all", "expected": True, "setting_int": 0},
            {
                "id": "set_punctuation_invalid",
                "input_value": "invalid",
                "expected": False,
                "setting_int": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_set_punctuation_level(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_punctuation_level method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        mock_update = test_context.Mock()
        test_context.patch_object(manager, "update_punctuation_level", new=mock_update)

        result = manager.set_punctuation_level(case["input_value"])
        assert result == case["expected"]

        if case["expected"]:
            assert manager.get_punctuation_level() == case["input_value"]
            mock_update.assert_called_once()
        else:
            mock_update.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "speech_enabled_true", "setting_value": True, "expected": True},
            {"id": "speech_enabled_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_speech_is_enabled(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_speech_is_enabled method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].enableSpeech = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_speech_is_enabled()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "speech_muted_true", "setting_value": True, "expected": True},
            {"id": "speech_muted_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_speech_is_muted(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_speech_is_muted method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.speech"].get_mute_speech.return_value = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_speech_is_muted()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "enabled_and_not_muted",
                "enable_speech": True,
                "silence_speech": False,
                "expected": True,
            },
            {
                "id": "enabled_and_muted",
                "enable_speech": True,
                "silence_speech": True,
                "expected": False,
            },
            {
                "id": "disabled_and_not_muted",
                "enable_speech": False,
                "silence_speech": False,
                "expected": False,
            },
            {
                "id": "disabled_and_muted",
                "enable_speech": False,
                "silence_speech": True,
                "expected": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_speech_is_enabled_and_not_muted(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test get_speech_is_enabled_and_not_muted method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].enableSpeech = case["enable_speech"]
        essential_modules["orca.speech"].get_mute_speech.return_value = case["silence_speech"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_speech_is_enabled_and_not_muted()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "speech_disabled",
                "speech_enabled": False,
                "expected_method": "shutdown_speech",
            },
            {"id": "speech_enabled", "speech_enabled": True, "expected_method": "start_speech"},
        ],
        ids=lambda case: case["id"],
    )
    def test_check_speech_setting(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test check_speech_setting method with various speech enabled settings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].enableSpeech = case["speech_enabled"]
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        mock_method = test_context.Mock()
        test_context.patch_object(manager, case["expected_method"], new=mock_method)
        manager.check_speech_setting()
        mock_method.assert_called_once()

    def test_refresh_speech(self, test_context: OrcaTestContext) -> None:
        """Test refresh_speech method."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        mock_shutdown = test_context.Mock()
        test_context.patch_object(manager, "shutdown_speech", new=mock_shutdown)
        mock_start = test_context.Mock()
        test_context.patch_object(manager, "start_speech", new=mock_start)
        result = manager.refresh_speech()
        assert result is True
        mock_shutdown.assert_called_once()
        mock_start.assert_called_once()

    def test_get_server_with_valid_server(self, test_context: OrcaTestContext) -> None:
        """Test _get_server method with valid speech server."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        mock_server = test_context.Mock()
        mock_server.is_alive.return_value = True
        manager._server = mock_server
        result = manager._get_server()
        assert result is mock_server

    def test_get_current_synthesizer_with_server(self, test_context: OrcaTestContext) -> None:
        """Test get_current_synthesizer method with valid server."""

        mock_server = test_context.Mock()
        mock_server.get_output_module.return_value = "espeak-ng"
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = manager.get_current_synthesizer()
        assert result == "espeak-ng"

    def test_cycle_capitalization_style(self, test_context: OrcaTestContext) -> None:
        """Test cycle_capitalization_style method."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "update_capitalization_style", new=test_context.Mock())
        result = manager.cycle_capitalization_style()
        assert result is True

    def test_cycle_synthesizer_with_server(self, test_context: OrcaTestContext) -> None:
        """Test cycle_synthesizer method with current not in available list."""

        mock_server = test_context.Mock()
        mock_server.list_output_modules.return_value = ["espeak", "festival"]
        mock_server.get_output_module.return_value = "unknown"
        mock_server.set_output_module.return_value = True
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = manager.cycle_synthesizer()
        assert result is True
        mock_server.set_output_module.assert_called_once_with("espeak")

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "decrease_rate",
                "method_name": "decrease_rate",
                "server_method": "decrease_speech_rate",
            },
            {
                "id": "increase_rate",
                "method_name": "increase_rate",
                "server_method": "increase_speech_rate",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_rate_adjustment_with_server(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test rate adjustment methods delegate to the speech server."""

        mock_server = test_context.Mock()
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = getattr(manager, case["method_name"])()
        assert result is True
        getattr(mock_server, case["server_method"]).assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "decrease_pitch",
                "method_name": "decrease_pitch",
                "server_method": "decrease_speech_pitch",
            },
            {
                "id": "increase_pitch",
                "method_name": "increase_pitch",
                "server_method": "increase_speech_pitch",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_pitch_adjustment_with_server(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test pitch adjustment methods delegate to the speech server."""

        mock_server = test_context.Mock()
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = getattr(manager, case["method_name"])()
        assert result is True
        getattr(mock_server, case["server_method"]).assert_called_once()

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "decrease_volume",
                "method_name": "decrease_volume",
                "server_method": "decrease_speech_volume",
            },
            {
                "id": "increase_volume",
                "method_name": "increase_volume",
                "server_method": "increase_speech_volume",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_volume_adjustment_with_server(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test volume adjustment methods delegate to the speech server."""

        mock_server = test_context.Mock()
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = getattr(manager, case["method_name"])()
        assert result is True
        getattr(mock_server, case["server_method"]).assert_called_once()

    def test_set_rate_valid(self, test_context: OrcaTestContext) -> None:
        """Test set_rate method with valid value."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_rate(75)
        assert result is True
        assert manager.get_rate() == 75

    def test_set_volume_valid(self, test_context: OrcaTestContext) -> None:
        """Test set_volume method with valid value."""

        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_volume(8.0)
        assert result is True
        assert manager.get_volume() == 8.0

    def test_update_synthesizer_with_server(self, test_context: OrcaTestContext) -> None:
        """Test update_synthesizer method with server and different synthesizer ID."""

        mock_server = test_context.Mock()
        mock_server.get_output_module.return_value = "espeak"
        mock_server.set_output_module.return_value = True
        self._setup_dependencies(test_context)
        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        from orca import gsettings_registry

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value("speech", "synthesizer", "espeak-ng")
        manager.update_synthesizer()
        mock_server.set_output_module.assert_called_once_with("espeak-ng")
        registry.clear_runtime_values()

    def test_get_manager_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_manager function returns the same instance."""

        self._setup_dependencies(test_context)
        from orca import speech_manager

        manager1 = speech_manager.get_manager()
        manager2 = speech_manager.get_manager()

        assert manager1 is manager2
        assert isinstance(manager1, speech_manager.SpeechManager)

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "speak_numbers_true", "setting_value": True, "expected": True},
            {"id": "speak_numbers_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_speak_numbers_as_digits(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_speak_numbers_as_digits method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].speakNumbersAsDigits = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_speak_numbers_as_digits()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_speak_numbers_true", "input_value": True, "expected": True},
            {"id": "set_speak_numbers_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_speak_numbers_as_digits(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_speak_numbers_as_digits method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_speak_numbers_as_digits(case["input_value"])
        assert result == case["expected"]
        assert manager.get_speak_numbers_as_digits() == case["input_value"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "use_pronunciation_dict_true", "setting_value": True, "expected": True},
            {"id": "use_pronunciation_dict_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_use_pronunciation_dictionary(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test get_use_pronunciation_dictionary method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].usePronunciationDictionary = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_use_pronunciation_dictionary()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_pronunciation_dict_true", "input_value": True, "expected": True},
            {"id": "set_pronunciation_dict_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_use_pronunciation_dictionary(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test set_use_pronunciation_dictionary method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_use_pronunciation_dictionary(case["input_value"])
        assert result == case["expected"]
        assert manager.get_use_pronunciation_dictionary() == case["input_value"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "use_color_names_true", "setting_value": True, "expected": True},
            {"id": "use_color_names_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_use_color_names(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_use_color_names method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].useColorNames = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_use_color_names()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_color_names_true", "input_value": True, "expected": True},
            {"id": "set_color_names_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_use_color_names(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_use_color_names method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_use_color_names(case["input_value"])
        assert result == case["expected"]
        assert manager.get_use_color_names() == case["input_value"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "insert_pauses_true", "setting_value": True, "expected": True},
            {"id": "insert_pauses_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_insert_pauses_between_utterances(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test get_insert_pauses_between_utterances method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].enablePauseBreaks = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_insert_pauses_between_utterances()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_pauses_true", "input_value": True, "expected": True},
            {"id": "set_pauses_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_insert_pauses_between_utterances(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test set_insert_pauses_between_utterances method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_insert_pauses_between_utterances(case["input_value"])
        assert result == case["expected"]
        assert manager.get_insert_pauses_between_utterances() == case["input_value"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "auto_lang_true", "setting_value": True, "expected": True},
            {"id": "auto_lang_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_auto_language_switching(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_auto_language_switching method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].enableAutoLanguageSwitching = case["setting_value"]

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.get_auto_language_switching()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_auto_lang_true", "input_value": True, "expected": True},
            {"id": "set_auto_lang_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_auto_language_switching(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_auto_language_switching method."""

        self._setup_dependencies(test_context)

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()

        result = manager.set_auto_language_switching(case["input_value"])
        assert result == case["expected"]
        assert manager.get_auto_language_switching() == case["input_value"]

    def test_toggle_speech_unmutes_when_muted(self, test_context: OrcaTestContext) -> None:
        """Test toggle_speech unmutes when speech is currently muted."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        speech_mock = essential_modules["orca.speech"]
        speech_mock.get_mute_speech.return_value = True
        settings_mock = essential_modules["orca.settings"]
        settings_mock.enableSpeech = True

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        script = test_context.Mock()
        manager.toggle_speech(script)

        speech_mock.set_mute_speech.assert_called_with(False)

    def test_toggle_speech_enables_when_disabled(self, test_context: OrcaTestContext) -> None:
        """Test toggle_speech enables speech when enableSpeech is False."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.enableSpeech = False

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        mock_init = test_context.patch_object(manager, "_init_server")
        script = test_context.Mock()
        manager.toggle_speech(script)

        assert manager.get_speech_is_enabled() is True
        mock_init.assert_called()

    def test_toggle_speech_mutes_when_app_profile_has_speech_enabled(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test toggle_speech mutes when the app profile has enableSpeech=True."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        speech_mock = essential_modules["orca.speech"]
        settings_mock = essential_modules["orca.settings"]
        settings_mock.enableSpeech = True

        settings_manager_instance = essential_modules["orca.settings_manager"].get_manager()
        settings_manager_instance.get_app_setting.return_value = True

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        script = test_context.Mock()
        manager.toggle_speech(script)

        speech_mock.set_mute_speech.assert_called_with(True)
        assert manager.get_speech_is_enabled() is True

    def test_toggle_speech_disables_when_app_profile_has_speech_disabled(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test toggle_speech restores enableSpeech=False when app profile disables speech."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.enableSpeech = True

        settings_manager_instance = essential_modules["orca.settings_manager"].get_manager()
        settings_manager_instance.get_app_setting.return_value = False

        from orca.speech_manager import SpeechManager

        manager = SpeechManager()
        script = test_context.Mock()
        manager.toggle_speech(script)

        assert manager.get_speech_is_enabled() is False


class TestVoicesPreferencesGridUI:  # pylint: disable=too-few-public-methods
    """Test VoicesPreferencesGrid save behavior."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for VoicesPreferencesGrid dependencies."""

        additional_modules = [
            "orca.speech",
            "orca.speechserver",
            "orca.acss",
            "orca.presentation_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_mock = essential_modules["orca.settings"]
        settings_mock.speechFactoryModules = ["spiel", "speechdispatcherfactory"]
        settings_mock.speechServerInfo = None
        settings_mock.speechServerFactory = "spiel"
        settings_mock.voices = {}
        settings_mock.DEFAULT_VOICE = "default"
        settings_mock.UPPERCASE_VOICE = "uppercase"
        settings_mock.HYPERLINK_VOICE = "hyperlink"
        settings_mock.SYSTEM_VOICE = "system"

        settings_mock.CAPITALIZATION_STYLE_NONE = "none"
        settings_mock.CAPITALIZATION_STYLE_SPELL = "spell"
        settings_mock.CAPITALIZATION_STYLE_ICON = "icon"
        settings_mock.PUNCTUATION_STYLE_NONE = 3
        settings_mock.PUNCTUATION_STYLE_SOME = 2
        settings_mock.PUNCTUATION_STYLE_MOST = 1
        settings_mock.PUNCTUATION_STYLE_ALL = 0

        settings_mock.verbalizePunctuationStyle = 2
        settings_mock.capitalizationStyle = "none"
        settings_mock.enableSpeech = True
        settings_mock.speakNumbersAsDigits = False
        settings_mock.useColorNames = True
        settings_mock.enablePauseBreaks = True
        settings_mock.usePronunciationDictionary = True
        settings_mock.enableAutoLanguageSwitching = False

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance._prefs_dir = "/tmp/orca-test"
        settings_manager_instance._load_user_customizations.return_value = True
        settings_manager_mock.get_manager.return_value = settings_manager_instance

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

        return essential_modules

    def test_save_settings_includes_speech_server_factory(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test save_settings includes speechServerFactory."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        settings_mock.speechServerFactory = "spiel"

        from orca.speech_manager import SpeechManager, VoicesPreferencesGrid

        manager = SpeechManager()
        mock_server = test_context.Mock()
        mock_server.get_factory_name.return_value = "Spiel"
        mock_server.get_output_module.return_value = "Piper"
        test_context.patch_object(manager, "_get_server", return_value=mock_server)

        grid_mock = test_context.Mock()
        grid_mock._manager = manager
        grid_mock._default_voice = {}
        grid_mock._uppercase_voice = {}
        grid_mock._hyperlink_voice = {}
        grid_mock._system_voice = {}
        grid_mock._has_unsaved_changes = True

        result = VoicesPreferencesGrid.save_settings(grid_mock)

        assert result["speechServerFactory"] == "spiel"
        assert result["speechServerInfo"] == ["Spiel", "Piper"]
