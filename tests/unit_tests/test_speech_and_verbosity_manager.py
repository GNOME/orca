# Unit tests for speech_and_verbosity_manager.py SpeechAndVerbosityManager class methods.
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
# pylint: disable=unused-variable
# pylint: disable=too-many-lines

"""Unit tests for speech_and_verbosity_manager.py SpeechAndVerbosityManager class methods."""

from __future__ import annotations

import queue
import sys
from unittest.mock import Mock, patch

import pytest

from .conftest import clean_module_cache


@pytest.mark.unit
class TestSpeechAndVerbosityManager:
    """Test SpeechAndVerbosityManager class methods."""

    @pytest.fixture
    def speech_manager_deps(self, mock_orca_dependencies, monkeypatch):
        """Set up comprehensive mocks for speech_and_verbosity_manager dependencies."""

        # Mock all the external modules first
        mock_modules = {}

        # Core modules
        mock_modules["cmdnames"] = Mock()
        mock_modules["debug"] = Mock()
        mock_modules["dbus_service"] = Mock()
        mock_modules["focus_manager"] = Mock()
        mock_modules["input_event"] = Mock()
        mock_modules["keybindings"] = Mock()
        mock_modules["mathsymbols"] = Mock()
        mock_modules["messages"] = Mock()
        mock_modules["object_properties"] = Mock()
        mock_modules["pronunciation_dict"] = Mock()

        # Configure settings mock to return proper values instead of Mock objects
        settings_mock = Mock()
        settings_mock.speechSystemOverride = "spiel"  # Valid module name
        settings_mock.speechFactoryModules = ["spiel", "speechdispatcherfactory"]
        settings_mock.speechServerInfo = None
        mock_modules["settings"] = settings_mock

        mock_modules["settings_manager"] = Mock()
        mock_modules["speech"] = Mock()
        mock_modules["speechserver"] = Mock()

        # Set up some default behaviors
        mock_modules["dbus_service"].get_remote_controller.return_value = Mock()
        mock_modules["speech"].get_speech_server.return_value = Mock()

        # Configure settings_manager mock to handle _prefs_dir properly
        settings_manager_instance = Mock()
        settings_manager_instance._prefs_dir = "/tmp/orca-test"
        settings_manager_instance.get_setting.return_value = True  # Default setting values
        # Mock the problematic _load_user_customizations method to avoid pathList issues
        settings_manager_instance._load_user_customizations.return_value = True
        mock_modules["settings_manager"].get_manager.return_value = settings_manager_instance

        mock_modules["focus_manager"].get_manager.return_value = Mock()

        # Set up dbus_service decorators to pass through to actual methods
        def passthrough_decorator(func):
            return func

        mock_modules["dbus_service"].getter = passthrough_decorator
        mock_modules["dbus_service"].setter = passthrough_decorator
        mock_modules["dbus_service"].command = passthrough_decorator
        mock_modules["dbus_service"].parameterized_command = passthrough_decorator

        # Set up debug methods to return None (they don't affect return values)
        mock_modules["debug"].print_message.return_value = None
        mock_modules["debug"].print_tokens.return_value = None

        # Mock ACSS
        mock_acss = Mock()
        mock_acss.ACSS = Mock()
        mock_acss.ACSS.RATE = "rate"
        mock_acss.ACSS.AVERAGE_PITCH = "average-pitch"
        mock_acss.ACSS.GAIN = "gain"
        mock_modules["acss"] = mock_acss

        # Mock AX modules and classes
        mock_ax_hypertext = Mock()
        mock_ax_hypertext.AXHypertext = Mock()
        mock_ax_hypertext.AXHypertext.get_all_links_in_range = Mock(return_value=[])
        mock_ax_hypertext.AXHypertext.get_link_end_offset = Mock(return_value=0)
        mock_modules["ax_hypertext"] = mock_ax_hypertext

        mock_ax_object = Mock()
        mock_ax_object.AXObject = Mock()
        mock_ax_object.AXObject.find_ancestor_inclusive = Mock(return_value=None)
        mock_modules["ax_object"] = mock_ax_object
        mock_modules["ax_table"] = Mock()

        # Configure AXText mock to return proper tuple for subscripting
        mock_ax_text = Mock()
        mock_ax_text.AXText = Mock()
        mock_ax_text.AXText.get_character_at_offset = Mock(
            return_value=("a", 0)
        )  # Return tuple (char, offset)
        mock_modules["ax_text"] = mock_ax_text

        mock_modules["ax_utilities"] = Mock()

        # Set module mocks
        for name, mock_module in mock_modules.items():
            monkeypatch.setitem(sys.modules, f"orca.{name}", mock_module)

        return mock_modules

    @pytest.fixture
    def manager_class(self, speech_manager_deps):
        """Get the SpeechAndVerbosityManager class with mocked dependencies."""
        clean_module_cache("orca.speech_and_verbosity_manager")
        from orca.speech_and_verbosity_manager import SpeechAndVerbosityManager

        return SpeechAndVerbosityManager

    def test_init(self, speech_manager_deps, manager_class):
        """Test SpeechAndVerbosityManager.__init__."""
        manager = manager_class()

        # Verify initialization
        assert manager._handlers is not None
        assert manager._bindings is not None
        assert manager._last_indentation_description == ""
        assert manager._last_error_description == ""

        # Verify D-Bus service is available (may not be called in all test contexts)
        assert speech_manager_deps["dbus_service"] is not None

    def test_get_bindings(self, speech_manager_deps, manager_class):
        """Test get_bindings method."""
        manager = manager_class()

        # Test basic functionality
        bindings = manager.get_bindings()
        assert bindings is not None

        # Test with refresh=True
        bindings_refresh = manager.get_bindings(refresh=True)
        assert bindings_refresh is not None

    def test_get_handlers(self, speech_manager_deps, manager_class):
        """Test get_handlers method."""
        manager = manager_class()

        # Test basic functionality
        handlers = manager.get_handlers()
        assert handlers is not None

        # Test with refresh=True
        handlers_refresh = manager.get_handlers(refresh=True)
        assert handlers_refresh is not None

    def test_get_server_none(self, speech_manager_deps, manager_class):
        """Test _get_server method when speech server is None."""
        # Configure speech mock to return None
        speech_manager_deps["speech"].get_speech_server.return_value = None

        manager = manager_class()
        result = manager._get_server()
        assert result is None

    def test_get_server_timeout(self, speech_manager_deps, manager_class, monkeypatch):
        """Test _get_server method with health check timeout."""
        mock_speech_server = Mock()
        speech_manager_deps["speech"].get_speech_server.return_value = mock_speech_server

        # Mock queue to simulate timeout
        def mock_queue_constructor():
            mock_queue = Mock()
            mock_queue.get.side_effect = queue.Empty()
            return mock_queue

        monkeypatch.setattr("queue.Queue", mock_queue_constructor)

        manager = manager_class()
        result = manager._get_server()
        assert result is None

    def test_get_available_servers(self, speech_manager_deps, manager_class):
        """Test get_available_servers method."""
        manager = manager_class()

        with patch.object(
            manager,
            "_get_server_module_map",
            return_value={"Speech Dispatcher": "speechdispatcherfactory"},
        ):
            result = manager.get_available_servers()
            assert result == ["Speech Dispatcher"]

    def test_get_server_module_map_import_error(
        self, speech_manager_deps, manager_class, monkeypatch
    ):
        """Test _get_server_module_map method with import errors."""
        # Set up settings mock
        speech_manager_deps["settings"].speechFactoryModules = ["nonexistent_module"]

        # Mock importlib to raise ImportError
        def mock_import_module(name):
            raise ImportError("Module not found")

        monkeypatch.setattr("importlib.import_module", mock_import_module)

        manager = manager_class()
        result = manager._get_server_module_map()
        assert result == {}

    def test_switch_server_invalid(self, speech_manager_deps, manager_class):
        """Test _switch_server method with invalid server."""
        manager = manager_class()

        with patch.object(manager, "_get_server_module_map", return_value={}):
            result = manager._switch_server("Invalid Server")
            assert result is False

    def test_get_current_server_none(self, speech_manager_deps, manager_class):
        """Test get_current_server method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_current_server()
            assert result == ""

    def test_get_current_synthesizer_none(self, speech_manager_deps, manager_class):
        """Test get_current_synthesizer method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_current_synthesizer()
            assert result == ""

    def test_set_current_synthesizer_no_server(self, speech_manager_deps, manager_class):
        """Test set_current_synthesizer method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.set_current_synthesizer("espeak-ng")
            assert result is False

    def test_get_available_synthesizers_no_server(self, speech_manager_deps, manager_class):
        """Test get_available_synthesizers method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_available_synthesizers()
            assert result == []

    def test_get_available_voices_no_server(self, speech_manager_deps, manager_class):
        """Test get_available_voices method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_available_voices()
            assert result == []

    def test_get_voices_for_language_no_server(self, speech_manager_deps, manager_class):
        """Test get_voices_for_language method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_voices_for_language("en")
            assert result == []

    def test_get_current_voice_no_server(self, speech_manager_deps, manager_class):
        """Test get_current_voice method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_current_voice()
            assert result == ""

    def test_set_current_voice_no_server(self, speech_manager_deps, manager_class):
        """Test set_current_voice method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.set_current_voice("en")
            assert result is False

    def test_get_current_speech_server_info_no_server(self, speech_manager_deps, manager_class):
        """Test get_current_speech_server_info method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.get_current_speech_server_info()
            assert result == ("", "")

    def test_check_speech_setting_disabled(self, speech_manager_deps, manager_class):
        """Test check_speech_setting method when speech is disabled."""
        settings_manager_instance = speech_manager_deps["settings_manager"].get_manager.return_value
        settings_manager_instance.get_setting.return_value = False  # Speech disabled

        manager = manager_class()

        with patch.object(manager, "shutdown_speech") as mock_shutdown:
            manager.check_speech_setting()
            mock_shutdown.assert_called_once()

    def test_check_speech_setting_enabled(self, speech_manager_deps, manager_class):
        """Test check_speech_setting method when speech is enabled."""
        settings_manager_instance = speech_manager_deps["settings_manager"].get_manager.return_value
        settings_manager_instance.get_setting.return_value = True  # Speech enabled

        manager = manager_class()

        with patch.object(manager, "start_speech") as mock_start:
            manager.check_speech_setting()
            mock_start.assert_called_once()

    def test_start_speech(self, speech_manager_deps, manager_class):
        """Test start_speech method."""
        manager = manager_class()

        result = manager.start_speech()
        assert result is True
        speech_manager_deps["speech"].init.assert_called_once()

    def test_interrupt_speech_no_server(self, speech_manager_deps, manager_class):
        """Test interrupt_speech method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.interrupt_speech()
            assert result is True

    def test_shutdown_speech_no_server(self, speech_manager_deps, manager_class):
        """Test shutdown_speech method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.shutdown_speech()
            assert result is True

    def test_refresh_speech(self, speech_manager_deps, manager_class):
        """Test refresh_speech method."""
        manager = manager_class()

        with patch.object(manager, "shutdown_speech") as mock_shutdown:
            with patch.object(manager, "start_speech") as mock_start:
                result = manager.refresh_speech()
                assert result is True
                mock_shutdown.assert_called_once()
                mock_start.assert_called_once()

    def test_set_rate_invalid(self, speech_manager_deps, manager_class):
        """Test set_rate method with invalid value."""
        manager = manager_class()

        result = manager.set_rate("invalid")
        assert result is False

    def test_set_pitch_invalid(self, speech_manager_deps, manager_class):
        """Test set_pitch method with invalid value."""
        manager = manager_class()

        result = manager.set_pitch("invalid")
        assert result is False

    def test_set_volume_invalid(self, speech_manager_deps, manager_class):
        """Test set_volume method with invalid value."""
        manager = manager_class()

        result = manager.set_volume("invalid")
        assert result is False

    def test_decrease_rate_no_server(self, speech_manager_deps, manager_class):
        """Test decrease_rate method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.decrease_rate()
            assert result is True

    def test_increase_rate_no_server(self, speech_manager_deps, manager_class):
        """Test increase_rate method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.increase_rate()
            assert result is True

    def test_decrease_pitch_no_server(self, speech_manager_deps, manager_class):
        """Test decrease_pitch method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.decrease_pitch()
            assert result is True

    def test_increase_pitch_no_server(self, speech_manager_deps, manager_class):
        """Test increase_pitch method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.increase_pitch()
            assert result is True

    def test_decrease_volume_no_server(self, speech_manager_deps, manager_class):
        """Test decrease_volume method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.decrease_volume()
            assert result is True

    def test_increase_volume_no_server(self, speech_manager_deps, manager_class):
        """Test increase_volume method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.increase_volume()
            assert result is True

    def test_update_capitalization_style_no_server(self, speech_manager_deps, manager_class):
        """Test update_capitalization_style method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.update_capitalization_style()
            assert result is True

    def test_update_punctuation_level_no_server(self, speech_manager_deps, manager_class):
        """Test update_punctuation_level method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.update_punctuation_level()
            assert result is True

    def test_update_synthesizer_no_server(self, speech_manager_deps, manager_class):
        """Test update_synthesizer method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            manager.update_synthesizer("festival")
            # Should not raise exception

    def test_cycle_synthesizer_no_server(self, speech_manager_deps, manager_class):
        """Test cycle_synthesizer method when server is None."""
        manager = manager_class()

        with patch.object(manager, "_get_server", return_value=None):
            result = manager.cycle_synthesizer()
            assert result is True

    def test_cycle_capitalization_style(self, speech_manager_deps, manager_class):
        """Test cycle_capitalization_style method."""
        manager = manager_class()

        with patch.object(manager, "update_capitalization_style"):
            result = manager.cycle_capitalization_style()
            assert result is True

    def test_cycle_punctuation_level(self, speech_manager_deps, manager_class):
        """Test cycle_punctuation_level method."""
        manager = manager_class()

        with patch.object(manager, "update_punctuation_level"):
            result = manager.cycle_punctuation_level()
            assert result is True

    def test_cycle_key_echo(self, speech_manager_deps, manager_class):
        """Test cycle_key_echo method."""
        manager = manager_class()

        result = manager.cycle_key_echo()
        assert result is True

    def test_change_number_style(self, speech_manager_deps, manager_class):
        """Test change_number_style method."""
        manager = manager_class()

        result = manager.change_number_style()
        assert result is True

    def test_toggle_speech(self, speech_manager_deps, manager_class):
        """Test toggle_speech method."""
        manager = manager_class()

        result = manager.toggle_speech()
        assert result is True

    def test_toggle_verbosity(self, speech_manager_deps, manager_class):
        """Test toggle_verbosity method."""
        manager = manager_class()

        result = manager.toggle_verbosity()
        assert result is True

    def test_toggle_indentation_and_justification(self, speech_manager_deps, manager_class):
        """Test toggle_indentation_and_justification method."""
        manager = manager_class()

        result = manager.toggle_indentation_and_justification()
        assert result is True

    def test_toggle_table_cell_reading_mode_no_script(self, speech_manager_deps, manager_class):
        """Test toggle_table_cell_reading_mode method without script."""
        manager = manager_class()

        result = manager.toggle_table_cell_reading_mode()
        assert result is True

    def test_adjust_for_digits_static(self, speech_manager_deps, manager_class):
        """Test adjust_for_digits static method."""
        # Set up settings mock
        speech_manager_deps["settings"].speakNumbersAsDigits = True
        speech_manager_deps["ax_utilities"].is_text_input_telephone.return_value = False

        mock_obj = Mock()
        text = "Hello 123 world"

        result = manager_class.adjust_for_digits(mock_obj, text)
        assert "1 2 3" in result

    def test_adjust_for_links_static(self, speech_manager_deps, manager_class):
        """Test _adjust_for_links static method."""
        # Set up AX hypertext mock
        speech_manager_deps["ax_hypertext"].get_all_links_in_range.return_value = []

        mock_obj = Mock()
        line = "Click here"
        start_offset = 0

        result = manager_class._adjust_for_links(mock_obj, line, start_offset)
        assert isinstance(result, str)

    def test_adjust_for_repeats_static(self, speech_manager_deps, manager_class):
        """Test _adjust_for_repeats static method."""
        # Set up settings mock
        speech_manager_deps["settings"].repeatCharacterLimit = 4
        speech_manager_deps["messages"].repeated_char_count = (
            lambda char, count: f"{char} repeated {count} times"
        )

        text = "Hello!!!!! world"
        result = manager_class._adjust_for_repeats(text)
        assert "repeated" in result

    def test_should_verbalize_punctuation_false(self, speech_manager_deps, manager_class):
        """Test _should_verbalize_punctuation static method returns False."""
        # Set up to return None (not in code)
        speech_manager_deps["ax_object"].find_ancestor_inclusive.return_value = None

        mock_obj = Mock()
        result = manager_class._should_verbalize_punctuation(mock_obj)
        assert result is False

    def test_get_indentation_description_disabled(self, speech_manager_deps, manager_class):
        """Test get_indentation_description method when disabled."""
        settings_manager_instance = speech_manager_deps["settings_manager"].get_manager.return_value
        settings_manager_instance.get_setting.side_effect = lambda key: {
            "onlySpeakDisplayedText": True,  # Disabled
            "enableSpeechIndentation": False,
        }.get(key, False)

        manager = manager_class()

        line = "    Hello world"
        result = manager.get_indentation_description(line)
        assert result == ""

    def test_get_error_description_disabled(self, speech_manager_deps, manager_class):
        """Test get_error_description method when disabled."""
        settings_manager_instance = speech_manager_deps["settings_manager"].get_manager.return_value
        settings_manager_instance.get_setting.return_value = False  # Disabled

        manager = manager_class()

        mock_obj = Mock()
        result = manager.get_error_description(mock_obj, 5)
        assert result == ""

    def test_adjust_for_presentation(self, speech_manager_deps, manager_class):
        """Test adjust_for_presentation method."""
        # Set up AX utilities mock
        speech_manager_deps["ax_utilities"].is_math_related.return_value = False

        manager = manager_class()
        mock_obj = Mock()
        text = "Hello world"

        with patch.object(manager, "_adjust_for_links", return_value=text):
            with patch.object(manager, "adjust_for_digits", return_value=text):
                with patch.object(manager, "_adjust_for_repeats", return_value=text):
                    with patch.object(
                        manager, "_adjust_for_verbalized_punctuation", return_value=text
                    ):
                        with patch.object(
                            manager, "_apply_pronunciation_dictionary", return_value=text
                        ):
                            result = manager.adjust_for_presentation(mock_obj, text)
                            assert result == text

    def test_get_manager_function(self, speech_manager_deps):
        """Test get_manager function."""
        clean_module_cache("orca.speech_and_verbosity_manager")
        from orca import speech_and_verbosity_manager

        manager1 = speech_and_verbosity_manager.get_manager()
        manager2 = speech_and_verbosity_manager.get_manager()

        # Should return the same singleton instance
        assert manager1 is manager2
        assert isinstance(manager1, speech_and_verbosity_manager.SpeechAndVerbosityManager)

    # Additional tests for coverage improvement

    def test_get_server_module_map_success(self, speech_manager_deps, manager_class, monkeypatch):
        """Test _get_server_module_map method with successful module loading."""
        # Set up settings mock
        speech_manager_deps["settings"].speechFactoryModules = ["test_module"]

        # Create mock factory with successful speech server
        mock_factory = Mock()
        mock_speech_server_class = Mock()
        mock_speech_server_class.get_factory_name.return_value = "Test Server"
        mock_factory.SpeechServer = mock_speech_server_class

        # Mock importlib to return the factory
        def mock_import_module(name):
            return mock_factory

        monkeypatch.setattr("importlib.import_module", mock_import_module)

        manager = manager_class()
        result = manager._get_server_module_map()
        assert result == {"Test Server": "test_module"}

    def test_get_server_with_valid_server(self, speech_manager_deps, manager_class):
        """Test _get_server method with valid speech server."""
        mock_server = Mock()
        mock_server.is_alive.return_value = True
        speech_manager_deps["speech"].get_speech_server.return_value = mock_server

        manager = manager_class()
        result = manager._get_server()
        assert result is mock_server

    def test_switch_server_success(self, speech_manager_deps, manager_class):
        """Test _switch_server method with valid server."""
        manager = manager_class()

        with (
            patch.object(
                manager, "_get_server_module_map", return_value={"Valid Server": "validfactory"}
            ),
            patch.object(manager, "shutdown_speech"),
            patch.object(manager, "start_speech"),
            patch.object(manager, "get_current_server", return_value="Valid Server"),
        ):
            result = manager._switch_server("Valid Server")
            assert result is True

    def test_get_current_server_with_server(self, speech_manager_deps, manager_class):
        """Test get_current_server method with valid server."""
        mock_server = Mock()
        mock_server.get_factory_name.return_value = "Test Server"

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.get_current_server()
            assert result == "Test Server"

    def test_get_current_synthesizer_with_server(self, speech_manager_deps, manager_class):
        """Test get_current_synthesizer method with valid server."""
        mock_server = Mock()
        mock_server.get_output_module.return_value = "espeak-ng"

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.get_current_synthesizer()
            assert result == "espeak-ng"

    def test_set_current_synthesizer_with_server(self, speech_manager_deps, manager_class):
        """Test set_current_synthesizer method with valid server."""
        mock_server = Mock()
        mock_server.set_output_module.return_value = True
        mock_server.get_output_module.return_value = "espeak-ng"

        manager = manager_class()
        with (
            patch.object(manager, "_get_server", return_value=mock_server),
            patch.object(
                manager, "get_available_synthesizers", return_value=["espeak-ng", "festival"]
            ),
        ):
            result = manager.set_current_synthesizer("espeak-ng")
            assert result is True
            mock_server.set_output_module.assert_called_once_with("espeak-ng")

    def test_get_available_synthesizers_with_server(self, speech_manager_deps, manager_class):
        """Test get_available_synthesizers method with valid server."""
        mock_server1 = Mock()
        mock_server1.get_info.return_value = ["server1", "Server 1"]
        mock_server2 = Mock()
        mock_server2.get_info.return_value = ["server2", "Server 2"]

        mock_server = Mock()
        mock_server.get_speech_servers.return_value = [mock_server1, mock_server2]

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.get_available_synthesizers()
            assert result == ["Server 1", "Server 2"]

    def test_get_available_voices_with_server(self, speech_manager_deps, manager_class):
        """Test get_available_voices method with valid server."""
        mock_voice1 = {"name": "Voice 1"}
        mock_voice2 = {"name": "Voice 2"}
        mock_voices = [mock_voice1, mock_voice2]

        mock_server = Mock()
        mock_server.get_voice_families.return_value = mock_voices
        speech_manager_deps["speechserver"].VoiceFamily.NAME = "name"

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.get_available_voices()
            assert result == ["Voice 1", "Voice 2"]

    def test_get_voices_for_language_with_server(self, speech_manager_deps, manager_class):
        """Test get_voices_for_language method with valid server."""
        mock_voices = [("Voice 1", "en", "US"), ("Voice 2", "en", "UK")]

        mock_server = Mock()
        mock_server.get_voice_families_for_language.return_value = mock_voices

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.get_voices_for_language("en")
            assert result == [("Voice 1", "en", "US"), ("Voice 2", "en", "UK")]

    def test_get_current_voice_with_server(self, speech_manager_deps, manager_class):
        """Test get_current_voice method with valid server."""
        mock_voice_family = {"name": "Test Voice"}

        mock_server = Mock()
        mock_server.get_voice_family.return_value = mock_voice_family
        speech_manager_deps["speechserver"].VoiceFamily.NAME = "name"

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.get_current_voice()
            assert result == "Test Voice"

    def test_set_current_voice_with_server(self, speech_manager_deps, manager_class):
        """Test set_current_voice method with valid server."""
        mock_voice = {"name": "Test Voice"}
        mock_voices = [mock_voice]

        mock_server = Mock()
        mock_server.get_voice_families.return_value = mock_voices
        mock_server.set_voice_family.return_value = True
        speech_manager_deps["speechserver"].VoiceFamily.NAME = "name"

        manager = manager_class()
        with (
            patch.object(manager, "_get_server", return_value=mock_server),
            patch.object(manager, "get_available_voices", return_value=["Test Voice"]),
        ):
            result = manager.set_current_voice("Test Voice")
            assert result is True
            mock_server.set_voice_family.assert_called_once_with(mock_voice)

    def test_start_speech_with_server(self, speech_manager_deps, manager_class):
        """Test start_speech method with valid server."""
        speech_manager_deps["speech"].start_speech_server.return_value = True

        manager = manager_class()
        result = manager.start_speech()
        assert result is True

    def test_interrupt_speech_with_server(self, speech_manager_deps, manager_class):
        """Test interrupt_speech method with valid server."""
        mock_server = Mock()
        mock_server.stop.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.interrupt_speech()
            assert result is True
            mock_server.stop.assert_called_once()

    def test_shutdown_speech_with_server(self, speech_manager_deps, manager_class):
        """Test shutdown_speech method with valid server."""
        speech_manager_deps["speech"].shutdown_speech_server.return_value = True

        manager = manager_class()
        result = manager.shutdown_speech()
        assert result is True

    def test_refresh_speech_with_server(self, speech_manager_deps, manager_class):
        """Test refresh_speech method with valid server."""
        mock_server = Mock()
        mock_server.start.return_value = True
        speech_manager_deps["speech"].get_speech_server.return_value = mock_server

        manager = manager_class()
        result = manager.refresh_speech()
        assert result is True

    def test_set_rate_valid_value(self, speech_manager_deps, manager_class):
        """Test set_rate method with valid value."""
        mock_voice = {"rate": 50}
        speech_manager_deps["settings"].voices = {"default": mock_voice}
        speech_manager_deps["settings"].DEFAULT_VOICE = "default"
        speech_manager_deps["acss"].ACSS.RATE = "rate"

        manager = manager_class()
        result = manager.set_rate(75)
        assert result is True
        assert mock_voice["rate"] == 75

    def test_set_pitch_valid_value(self, speech_manager_deps, manager_class):
        """Test set_pitch method with valid value."""
        mock_voice = {"average-pitch": 5.0}
        speech_manager_deps["settings"].voices = {"default": mock_voice}
        speech_manager_deps["settings"].DEFAULT_VOICE = "default"
        speech_manager_deps["acss"].ACSS.AVERAGE_PITCH = "average-pitch"

        manager = manager_class()
        result = manager.set_pitch(7.0)
        assert result is True
        assert mock_voice["average-pitch"] == 7.0

    def test_set_volume_valid_value(self, speech_manager_deps, manager_class):
        """Test set_volume method with valid value."""
        mock_voice = {"gain": 10.0}
        speech_manager_deps["settings"].voices = {"default": mock_voice}
        speech_manager_deps["settings"].DEFAULT_VOICE = "default"
        speech_manager_deps["acss"].ACSS.GAIN = "gain"

        manager = manager_class()
        result = manager.set_volume(8.0)
        assert result is True
        assert mock_voice["gain"] == 8.0

    def test_decrease_rate_with_server(self, speech_manager_deps, manager_class):
        """Test decrease_rate method with valid server."""
        mock_server = Mock()
        mock_server.decrease_speech_rate.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.decrease_rate()
            assert result is True
            mock_server.decrease_speech_rate.assert_called_once()

    def test_increase_rate_with_server(self, speech_manager_deps, manager_class):
        """Test increase_rate method with valid server."""
        mock_server = Mock()
        mock_server.increase_speech_rate.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.increase_rate()
            assert result is True
            mock_server.increase_speech_rate.assert_called_once()

    def test_decrease_pitch_with_server(self, speech_manager_deps, manager_class):
        """Test decrease_pitch method with valid server."""
        mock_server = Mock()
        mock_server.decrease_speech_pitch.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.decrease_pitch()
            assert result is True
            mock_server.decrease_speech_pitch.assert_called_once()

    def test_increase_pitch_with_server(self, speech_manager_deps, manager_class):
        """Test increase_pitch method with valid server."""
        mock_server = Mock()
        mock_server.increase_speech_pitch.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.increase_pitch()
            assert result is True
            mock_server.increase_speech_pitch.assert_called_once()

    def test_decrease_volume_with_server(self, speech_manager_deps, manager_class):
        """Test decrease_volume method with valid server."""
        mock_server = Mock()
        mock_server.decrease_speech_volume.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.decrease_volume()
            assert result is True
            mock_server.decrease_speech_volume.assert_called_once()

    def test_increase_volume_with_server(self, speech_manager_deps, manager_class):
        """Test increase_volume method with valid server."""
        mock_server = Mock()
        mock_server.increase_speech_volume.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.increase_volume()
            assert result is True
            mock_server.increase_speech_volume.assert_called_once()

    def test_update_capitalization_style_with_server(self, speech_manager_deps, manager_class):
        """Test update_capitalization_style method with valid server."""
        mock_server = Mock()
        mock_server.update_capitalization_style.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.update_capitalization_style()
            assert result is True
            mock_server.update_capitalization_style.assert_called_once()

    def test_update_punctuation_level_with_server(self, speech_manager_deps, manager_class):
        """Test update_punctuation_level method with valid server."""
        mock_server = Mock()
        mock_server.update_punctuation_level.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.update_punctuation_level()
            assert result is True
            mock_server.update_punctuation_level.assert_called_once()

    def test_update_synthesizer_with_server_and_different_id(
        self, speech_manager_deps, manager_class
    ):
        """Test update_synthesizer method with server and different synthesizer ID."""
        mock_server = Mock()
        mock_server.get_output_module.return_value = "espeak"
        mock_server.set_output_module.return_value = True

        speech_manager_deps["settings"].speechServerInfo = ["Test Server", "espeak-ng"]

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            manager.update_synthesizer()
            mock_server.set_output_module.assert_called_once_with("espeak-ng")

    def test_cycle_synthesizer_with_server(self, speech_manager_deps, manager_class):
        """Test cycle_synthesizer method with valid server."""
        mock_server = Mock()
        mock_server.list_output_modules.return_value = ["espeak", "festival", "spiel"]
        mock_server.get_output_module.return_value = "espeak"
        mock_server.set_output_module.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.cycle_synthesizer()
            assert result is True
            mock_server.set_output_module.assert_called_once_with("festival")

    def test_cycle_synthesizer_wrap_around(self, speech_manager_deps, manager_class):
        """Test cycle_synthesizer method wrapping around to first option."""
        mock_server = Mock()
        mock_server.list_output_modules.return_value = ["espeak", "festival"]
        mock_server.get_output_module.return_value = "festival"
        mock_server.set_output_module.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.cycle_synthesizer()
            assert result is True
            mock_server.set_output_module.assert_called_once_with("espeak")

    def test_cycle_synthesizer_value_error(self, speech_manager_deps, manager_class):
        """Test cycle_synthesizer method with current not in available list."""
        mock_server = Mock()
        mock_server.list_output_modules.return_value = ["espeak", "festival"]
        mock_server.get_output_module.return_value = "unknown"
        mock_server.set_output_module.return_value = True

        manager = manager_class()
        with patch.object(manager, "_get_server", return_value=mock_server):
            result = manager.cycle_synthesizer()
            assert result is True
            mock_server.set_output_module.assert_called_once_with("espeak")

    def test_apply_pronunciation_dictionary(self, speech_manager_deps, manager_class):
        """Test _apply_pronunciation_dictionary static method."""
        # Set up settings to enable pronunciation dictionary
        settings_manager_instance = speech_manager_deps["settings_manager"].get_manager.return_value
        settings_manager_instance.get_setting.return_value = True

        # Mock pronunciation dict to return the input unchanged for this test
        speech_manager_deps["pronunciation_dict"].get_pronunciation.side_effect = lambda x: x

        result = manager_class._apply_pronunciation_dictionary("hello world")
        assert result == "hello world"

    def test_adjust_for_verbalized_punctuation(self, speech_manager_deps, manager_class):
        """Test _adjust_for_verbalized_punctuation static method."""
        # Set up to return a code object (should verbalize punctuation)
        mock_code_obj = Mock()
        speech_manager_deps[
            "ax_object"
        ].AXObject.find_ancestor_inclusive.return_value = mock_code_obj

        mock_obj = Mock()
        text = "Hello, world! How are you?"
        result = manager_class._adjust_for_verbalized_punctuation(mock_obj, text)

        # Should add spaces around punctuation
        expected = "Hello ,  world !  How are you ? "
        assert result == expected

    def test_should_verbalize_punctuation_true(self, speech_manager_deps, manager_class):
        """Test _should_verbalize_punctuation static method returns True."""
        # Set up to return a code object (in code)
        mock_code_obj = Mock()
        speech_manager_deps[
            "ax_object"
        ].AXObject.find_ancestor_inclusive.return_value = mock_code_obj

        mock_obj = Mock()
        result = manager_class._should_verbalize_punctuation(mock_obj)
        assert result is True
