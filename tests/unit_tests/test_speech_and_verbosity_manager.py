# Unit tests for speech_and_verbosity_manager.py methods.
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
# pylint: disable=too-many-lines

"""Unit tests for speech_and_verbosity_manager.py methods."""

from __future__ import annotations

import queue
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestSpeechAndVerbosityManager:
    """Test SpeechAndVerbosityManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for speech_and_verbosity_manager dependencies."""

        additional_modules = [
            "orca.mathsymbols",
            "orca.object_properties",
            "orca.pronunciation_dict",
            "orca.speech",
            "orca.speechserver",
            "orca.acss",
            "orca.ax_hypertext",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.colornames",
            "orca.ax_utilities_text",
            "orca.ax_document",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_mock = essential_modules["orca.settings"]
        settings_mock.speechSystemOverride = "spiel"
        settings_mock.speechFactoryModules = ["spiel", "speechdispatcherfactory"]
        settings_mock.speechServerInfo = None
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
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance._prefs_dir = "/tmp/orca-test"
        settings_manager_instance.get_setting.return_value = True
        settings_manager_instance._load_user_customizations.return_value = True
        settings_manager_mock.get_manager.return_value = settings_manager_instance

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
        speech_mock.get_speech_server.return_value = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message.return_value = None
        debug_mock.print_tokens.return_value = None

        acss_mock = essential_modules["orca.acss"]
        acss_mock.ACSS = test_context.Mock()
        acss_mock.ACSS.RATE = "rate"
        acss_mock.ACSS.AVERAGE_PITCH = "average-pitch"
        acss_mock.ACSS.GAIN = "gain"

        ax_hypertext_mock = essential_modules["orca.ax_hypertext"]
        ax_hypertext_mock.AXHypertext = test_context.Mock()
        ax_hypertext_mock.AXHypertext.get_all_links_in_range = test_context.Mock(return_value=[])
        ax_hypertext_mock.AXHypertext.get_link_end_offset = test_context.Mock(return_value=0)

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject = test_context.Mock()
        ax_object_mock.AXObject.find_ancestor_inclusive = test_context.Mock(return_value=None)

        ax_text_mock = essential_modules["orca.ax_text"]
        ax_text_mock.AXText = test_context.Mock()
        ax_text_mock.AXText.get_character_at_offset = test_context.Mock(return_value=("a", 0))

        orca_i18n_mock = essential_modules["orca.orca_i18n"]
        orca_i18n_mock._ = lambda x: x
        orca_i18n_mock.C_ = lambda c, x: x
        orca_i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p

        return essential_modules

    def _setup_presentation_adjustment_mocks(
        self, test_context, manager, return_text="Hello world"
    ):
        """Set up common mocks for presentation adjustment testing."""
        test_context.patch_object(manager, "_adjust_for_links", return_value=return_text)
        test_context.patch_object(manager, "adjust_for_digits", return_value=return_text)
        test_context.patch_object(manager, "_adjust_for_repeats", return_value=return_text)
        test_context.patch_object(
            manager,
            "_adjust_for_verbalized_punctuation",
            return_value=return_text,
        )
        test_context.patch_object(
            manager, "_apply_pronunciation_dictionary", return_value=return_text
        )

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test get_handlers method."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        handlers = manager.get_handlers()
        assert handlers is not None

        handlers_refresh = manager.get_handlers(refresh=True)
        assert handlers_refresh is not None

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
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        if case["scenario"] == "none_server":
            essential_modules["orca.speech"].get_speech_server.return_value = None
        else:  # timeout scenario
            mock_speech_server = test_context.Mock()
            essential_modules["orca.speech"].get_speech_server.return_value = mock_speech_server

            def mock_queue_constructor():
                mock_queue = test_context.Mock()
                mock_queue.get.side_effect = queue.Empty()
                return mock_queue

            test_context.patch("queue.Queue", new=mock_queue_constructor)

        manager = SpeechAndVerbosityManager()
        result = manager._get_server()
        assert result is case["expected_result"]

    def test_get_available_servers(self, test_context: OrcaTestContext) -> None:
        """Test _get_server_module_map method with import errors."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        essential_modules["orca.settings"].speechFactoryModules = ["nonexistent_module"]

        def mock_import_module(name) -> None:
            raise ImportError("Module not found")

        test_context.patch("importlib.import_module", new=mock_import_module)
        manager = SpeechAndVerbosityManager()
        result = manager._get_server_module_map()
        assert not result

    def test_switch_server_invalid(self, test_context: OrcaTestContext) -> None:
        """Test _switch_server method with invalid server."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
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
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

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

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
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
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
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
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["speech_enabled"]
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        mock_method = test_context.Mock()
        test_context.patch_object(manager, case["expected_method"], new=mock_method)
        manager.check_speech_setting()
        mock_method.assert_called_once()

    def test_start_speech(self, test_context: OrcaTestContext) -> None:
        """Test refresh_speech method."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        mock_shutdown = test_context.Mock()
        test_context.patch_object(manager, "shutdown_speech", new=mock_shutdown)
        mock_start = test_context.Mock()
        test_context.patch_object(manager, "start_speech", new=mock_start)
        result = manager.refresh_speech()
        assert result is True
        mock_shutdown.assert_called_once()
        mock_start.assert_called_once()

    def test_cycle_capitalization_style(self, test_context: OrcaTestContext) -> None:
        """Test cycle_capitalization_style method."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        test_context.patch_object(manager, "update_capitalization_style", new=test_context.Mock())
        result = manager.cycle_capitalization_style()
        assert result is True

    def test_cycle_punctuation_level(self, test_context: OrcaTestContext) -> None:
        """Test change_number_style method."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        result = manager.change_number_style()
        assert result is True

    def test_toggle_speech(self, test_context: OrcaTestContext) -> None:
        """Test toggle_indentation_and_justification method."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        result = manager.toggle_indentation_and_justification()
        assert result is True

    def test_toggle_table_cell_reading_mode_no_script(self, test_context: OrcaTestContext) -> None:
        """Test _adjust_for_links static method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        essential_modules["orca.ax_hypertext"].get_all_links_in_range.return_value = []
        mock_obj = test_context.Mock()
        line = "Click here"
        start_offset = 0
        result = SpeechAndVerbosityManager._adjust_for_links(mock_obj, line, start_offset)
        assert isinstance(result, str)

    def test_adjust_for_repeats_static(self, test_context: OrcaTestContext) -> None:
        """Test _should_verbalize_punctuation static method returns False."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        essential_modules["orca.ax_object"].find_ancestor_inclusive.return_value = None
        mock_obj = test_context.Mock()
        result = SpeechAndVerbosityManager._should_verbalize_punctuation(mock_obj)
        assert result is False

    def test_get_indentation_description_disabled(self, test_context: OrcaTestContext) -> None:
        """Test get_indentation_description method when disabled."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.side_effect = lambda key: {
            "onlySpeakDisplayedText": True,
            "enableSpeechIndentation": False,
        }.get(key, False)
        manager = SpeechAndVerbosityManager()
        line = "    Hello world"
        result = manager.get_indentation_description(line)
        assert result == ""

    def test_get_error_description_disabled(self, test_context: OrcaTestContext) -> None:
        """Test get_manager function."""

        (self._setup_dependencies(test_context))
        from orca import speech_and_verbosity_manager

        manager1 = speech_and_verbosity_manager.get_manager()
        manager2 = speech_and_verbosity_manager.get_manager()

        assert manager1 is manager2
        assert isinstance(manager1, speech_and_verbosity_manager.SpeechAndVerbosityManager)

    def test_get_server_module_map_success(self, test_context: OrcaTestContext) -> None:
        """Test _get_server method with valid speech server."""

        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        mock_server = test_context.Mock()
        mock_server.is_alive.return_value = True
        test_context.patch(
            "orca.speech_and_verbosity_manager.speech.get_speech_server",
            side_effect=lambda: mock_server,
        )
        result = manager._get_server()
        assert result is mock_server

    def test_switch_server_success(self, test_context: OrcaTestContext) -> None:
        """Test get_current_synthesizer method with valid server."""

        mock_server = test_context.Mock()
        mock_server.get_output_module.return_value = "espeak-ng"
        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = manager.get_current_synthesizer()
        assert result == "espeak-ng"

    def test_set_current_synthesizer_with_server(self, test_context: OrcaTestContext) -> None:
        """Test get_available_voices method with valid server."""

        mock_voice1 = {"name": "Voice 1"}
        mock_voice2 = {"name": "Voice 2"}
        mock_voices = [mock_voice1, mock_voice2]
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.speechserver"].VoiceFamily.NAME = "name"
        mock_server = test_context.Mock()
        mock_server.get_voice_families.return_value = mock_voices
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = manager.get_available_voices()
        assert result == ["Voice 1", "Voice 2"]

    def test_get_voices_for_language_with_server(self, test_context: OrcaTestContext) -> None:
        """Test set_current_voice method with valid server."""

        mock_voice = {"name": "Test Voice"}
        mock_voices = [mock_voice]
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.speechserver"].VoiceFamily.NAME = "name"
        mock_server = test_context.Mock()
        mock_server.get_voice_families.return_value = mock_voices
        mock_server.set_voice_family.return_value = True
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        test_context.patch_object(manager, "get_available_voices", return_value=["Test Voice"])
        result = manager.set_current_voice("Test Voice")
        assert result is True
        mock_server.set_voice_family.assert_called_once_with(mock_voice)

    def test_start_speech_with_server(self, test_context: OrcaTestContext) -> None:
        """Test shutdown_speech method with valid server."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.speech"].shutdown_speech_server.return_value = True
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        result = manager.shutdown_speech()
        assert result is True

    def test_refresh_speech_with_server(self, test_context: OrcaTestContext) -> None:
        """Test set_rate method with valid value."""

        mock_voice = {"rate": 50}
        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        test_context.patch("orca.speech_and_verbosity_manager.ACSS.RATE", new="rate")
        test_context.patch(
            "orca.speech_and_verbosity_manager.settings.voices", new={"default": mock_voice}
        )
        test_context.patch(
            "orca.speech_and_verbosity_manager.settings.DEFAULT_VOICE", new="default"
        )
        result = manager.set_rate(75)
        assert result is True
        assert mock_voice["rate"] == 75

    def test_set_pitch_valid_value(self, test_context: OrcaTestContext) -> None:
        """Test set_volume method with valid value."""

        mock_voice = {"gain": 10.0}
        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        test_context.patch("orca.speech_and_verbosity_manager.ACSS.GAIN", new="gain")
        test_context.patch(
            "orca.speech_and_verbosity_manager.settings.voices", new={"default": mock_voice}
        )
        test_context.patch(
            "orca.speech_and_verbosity_manager.settings.DEFAULT_VOICE", new="default"
        )
        result = manager.set_volume(8.0)
        assert result is True
        assert mock_voice["gain"] == 8.0

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
        """Test rate adjustment methods with valid server."""

        mock_server = test_context.Mock()
        setattr(getattr(mock_server, case["server_method"]), "return_value", True)
        self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
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
        """Test pitch adjustment methods with valid server."""

        mock_server = test_context.Mock()
        setattr(getattr(mock_server, case["server_method"]), "return_value", True)
        self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
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
        """Test volume adjustment methods with valid server."""

        mock_server = test_context.Mock()
        setattr(getattr(mock_server, case["server_method"]), "return_value", True)
        self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = getattr(manager, case["method_name"])()
        assert result is True
        getattr(mock_server, case["server_method"]).assert_called_once()

    def test_update_capitalization_style_with_server(self, test_context: OrcaTestContext) -> None:
        """Test update_synthesizer method with server and different synthesizer ID."""

        mock_server = test_context.Mock()
        mock_server.get_output_module.return_value = "espeak"
        mock_server.set_output_module.return_value = True
        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        test_context.patch(
            "orca.speech_and_verbosity_manager.settings.speechServerInfo",
            new=["Test Server", "espeak-ng"],
        )
        manager.update_synthesizer()
        mock_server.set_output_module.assert_called_once_with("espeak-ng")

    def test_cycle_synthesizer_with_server(self, test_context: OrcaTestContext) -> None:
        """Test cycle_synthesizer method with current not in available list."""

        mock_server = test_context.Mock()
        mock_server.list_output_modules.return_value = ["espeak", "festival"]
        mock_server.get_output_module.return_value = "unknown"
        mock_server.set_output_module.return_value = True
        (self._setup_dependencies(test_context))
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        test_context.patch_object(manager, "_get_server", return_value=mock_server)
        result = manager.cycle_synthesizer()
        assert result is True
        mock_server.set_output_module.assert_called_once_with("espeak")

    def test_apply_pronunciation_dictionary(self, test_context: OrcaTestContext) -> None:
        """Test _adjust_for_verbalized_punctuation static method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        mock_code_obj = test_context.Mock()
        (
            essential_modules["orca.ax_object"].AXObject.find_ancestor_inclusive.return_value
        ) = mock_code_obj
        essential_modules["orca.ax_document"].AXDocument.is_plain_text.return_value = False
        mock_obj = test_context.Mock()
        text = "Hello, world! How are you?"
        result = SpeechAndVerbosityManager._adjust_for_verbalized_punctuation(mock_obj, text)

        expected = "Hello ,  world !  How are you ? "
        assert result == expected

    def test_should_verbalize_punctuation_true(self, test_context: OrcaTestContext) -> None:
        """Test _should_verbalize_punctuation static method returns True."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        mock_code_obj = test_context.Mock()
        (
            essential_modules["orca.ax_object"].AXObject.find_ancestor_inclusive.return_value
        ) = mock_code_obj
        essential_modules["orca.ax_document"].AXDocument.is_plain_text.return_value = False
        mock_obj = test_context.Mock()
        result = SpeechAndVerbosityManager._should_verbalize_punctuation(mock_obj)
        assert result is True

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
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_capitalization_style()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("capitalizationStyle")

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

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        mock_update = test_context.Mock()
        test_context.patch_object(manager, "update_capitalization_style", new=mock_update)

        result = manager.set_capitalization_style(case["input_value"])
        assert result == case["expected"]

        if case["expected"]:
            settings_manager_instance.set_setting.assert_called_with(
                "capitalizationStyle", case["input_value"]
            )
            mock_update.assert_called_once()
        else:
            settings_manager_instance.set_setting.assert_not_called()
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
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_punctuation_level()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("verbalizePunctuationStyle")

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

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()
        mock_update = test_context.Mock()
        test_context.patch_object(manager, "update_punctuation_level", new=mock_update)

        result = manager.set_punctuation_level(case["input_value"])
        assert result == case["expected"]

        if case["expected"]:
            settings_manager_instance.set_setting.assert_called_with(
                "verbalizePunctuationStyle", case["setting_int"]
            )
            mock_update.assert_called_once()
        else:
            settings_manager_instance.set_setting.assert_not_called()
            mock_update.assert_not_called()

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "verbosity_brief", "setting_value": 0, "expected": "brief"},
            {"id": "verbosity_verbose", "setting_value": 1, "expected": "verbose"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_verbosity_level(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_verbosity_level method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_verbosity_level()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("speechVerbosityLevel")

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "set_verbosity_brief",
                "input_value": "brief",
                "expected": True,
                "setting_int": 0,
            },
            {
                "id": "set_verbosity_verbose",
                "input_value": "verbose",
                "expected": True,
                "setting_int": 1,
            },
            {
                "id": "set_verbosity_invalid",
                "input_value": "invalid",
                "expected": False,
                "setting_int": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_set_verbosity_level(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_verbosity_level method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.set_verbosity_level(case["input_value"])
        assert result == case["expected"]

        if case["expected"]:
            settings_manager_instance.set_setting.assert_called_with(
                "speechVerbosityLevel", case["setting_int"]
            )
        else:
            settings_manager_instance.set_setting.assert_not_called()

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
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_speak_numbers_as_digits()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("speakNumbersAsDigits")

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

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.set_speak_numbers_as_digits(case["input_value"])
        assert result == case["expected"]
        settings_manager_instance.set_setting.assert_called_with(
            "speakNumbersAsDigits", case["input_value"]
        )

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
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_speech_is_muted()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("silenceSpeech")

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_speech_muted_true", "input_value": True, "expected": True},
            {"id": "set_speech_muted_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_speech_is_muted(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_speech_is_muted method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.set_speech_is_muted(case["input_value"])
        assert result == case["expected"]
        settings_manager_instance.set_setting.assert_called_with(
            "silenceSpeech", case["input_value"]
        )

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "only_speak_displayed_true", "setting_value": True, "expected": True},
            {"id": "only_speak_displayed_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_only_speak_displayed_text(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_only_speak_displayed_text method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_only_speak_displayed_text()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("onlySpeakDisplayedText")

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_only_speak_displayed_true", "input_value": True, "expected": True},
            {"id": "set_only_speak_displayed_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_only_speak_displayed_text(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_only_speak_displayed_text method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.set_only_speak_displayed_text(case["input_value"])
        assert result == case["expected"]
        settings_manager_instance.set_setting.assert_called_with(
            "onlySpeakDisplayedText", case["input_value"]
        )

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "speak_indentation_true", "setting_value": True, "expected": True},
            {"id": "speak_indentation_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_speak_indentation_and_justification(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test get_speak_indentation_and_justification method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value
        settings_manager_instance.get_setting.return_value = case["setting_value"]

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.get_speak_indentation_and_justification()
        assert result == case["expected"]
        settings_manager_instance.get_setting.assert_called_with("enableSpeechIndentation")

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_speak_indentation_true", "input_value": True, "expected": True},
            {"id": "set_speak_indentation_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_speak_indentation_and_justification(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test set_speak_indentation_and_justification method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        settings_manager_instance = essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value

        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        manager = SpeechAndVerbosityManager()

        result = manager.set_speak_indentation_and_justification(case["input_value"])
        assert result == case["expected"]
        settings_manager_instance.set_setting.assert_called_with(
            "enableSpeechIndentation", case["input_value"]
        )
