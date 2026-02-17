# Unit tests for speech_presenter.py methods.
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
# pylint: disable=too-many-lines
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Unit tests for speech_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestSpeechPresenter:
    """Test SpeechPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for speech_presenter dependencies."""

        additional_modules = [
            "orca.mathsymbols",
            "orca.object_properties",
            "orca.phonnames",
            "orca.pronunciation_dictionary_manager",
            "orca.ax_hypertext",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.ax_document",
            "orca.presentation_manager",
            "orca.preferences_grid_base",
            "orca.speech",
            "orca.speech_manager",
            "orca.speech_monitor",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        settings_mock = essential_modules["orca.settings"]
        settings_mock.VERBOSITY_LEVEL_BRIEF = 0
        settings_mock.VERBOSITY_LEVEL_VERBOSE = 1
        settings_mock.speakNumbersAsDigits = False

        settings_mock.PROGRESS_BAR_ALL = 0
        settings_mock.PROGRESS_BAR_APPLICATION = 1
        settings_mock.PROGRESS_BAR_WINDOW = 2

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance._prefs_dir = "/tmp/orca-test"
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

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message.return_value = None
        debug_mock.print_tokens.return_value = None
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 900

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
        ax_text_mock.AXText.string_has_spelling_error = test_context.Mock(return_value=False)
        ax_text_mock.AXText.string_has_grammar_error = test_context.Mock(return_value=False)

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.AXUtilities = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_math_related = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities.is_text_input_telephone = test_context.Mock(
            return_value=False
        )
        ax_utilities_mock.AXUtilities.is_code = test_context.Mock(return_value=False)

        ax_document_mock = essential_modules["orca.ax_document"]
        ax_document_mock.AXDocument = test_context.Mock()
        ax_document_mock.AXDocument.is_plain_text = test_context.Mock(return_value=False)

        ax_table_mock = essential_modules["orca.ax_table"]
        ax_table_mock.AXTable = test_context.Mock()
        ax_table_mock.AXTable.get_table = test_context.Mock(return_value=None)

        mathsymbols_mock = essential_modules["orca.mathsymbols"]
        mathsymbols_mock.adjust_for_speech = test_context.Mock(side_effect=lambda x: x)

        object_properties_mock = essential_modules["orca.object_properties"]
        object_properties_mock.STATE_INVALID_GRAMMAR_SPEECH = "grammar error"

        pronunciation_dict_mock = essential_modules["orca.pronunciation_dictionary_manager"]
        pron_manager_instance = test_context.Mock()
        pron_manager_instance.get_pronunciation = test_context.Mock(side_effect=lambda x: x)
        pronunciation_dict_mock.get_manager = test_context.Mock(return_value=pron_manager_instance)

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

        orca_i18n_mock = essential_modules["orca.orca_i18n"]
        orca_i18n_mock._ = lambda x: x
        orca_i18n_mock.C_ = lambda c, x: x
        orca_i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p

        messages_mock = essential_modules["orca.messages"]
        messages_mock.LINK = "link"
        messages_mock.MISSPELLED = "misspelled"
        messages_mock.repeated_char_count = test_context.Mock(
            side_effect=lambda char, count: f"{char} repeated {count} times"
        )
        messages_mock.spaces_count = test_context.Mock(side_effect=lambda count: f"{count} spaces")
        messages_mock.tabs_count = test_context.Mock(side_effect=lambda count: f"{count} tabs")

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test presenter initialization and D-Bus registration."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()

        # Verify D-Bus registration occurred
        controller = essential_modules["orca.dbus_service"].get_remote_controller()
        controller.register_decorated_module.assert_called_with("SpeechPresenter", presenter)

        # Monitor callbacks are not registered in __init__ (deferred to set_up_commands
        # to avoid circular imports during module loading).

    def test_set_up_commands(self, test_context: OrcaTestContext) -> None:
        """Test that set_up_commands registers commands in CommandManager."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter
        from orca import command_manager

        presenter = SpeechPresenter()
        presenter.set_up_commands()

        # Verify commands are registered in CommandManager
        cmd_manager = command_manager.get_manager()
        assert cmd_manager.get_command("changeNumberStyleHandler") is not None
        assert cmd_manager.get_command("toggleSpeechVerbosityHandler") is not None
        assert cmd_manager.get_command("toggleSpeakingIndentationJustificationHandler") is not None
        assert cmd_manager.get_command("toggleTableCellReadModeHandler") is not None

    def test_set_up_commands_registers_monitor_callbacks(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that set_up_commands registers speech monitor callbacks."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        speech_mock = essential_modules["orca.speech"]
        speech_mock.set_monitor_callbacks.reset_mock()

        presenter.set_up_commands()

        speech_mock.set_monitor_callbacks.assert_called_once_with(
            write_text=presenter.write_to_monitor,
            write_key=presenter.write_key_to_monitor,
            write_character=presenter.write_character_to_monitor,
            begin_group=presenter._begin_monitor_group,
            end_group=presenter._end_monitor_group,
        )

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "verbose_true", "setting_value": 1, "expected": True},
            {"id": "verbose_false", "setting_value": 0, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_use_verbose_speech(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test use_verbose_speech method."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        nick = "verbose" if case["setting_value"] == 1 else "brief"
        gsettings_registry.get_registry().set_runtime_value("speech", "verbosity-level", nick)

        result = presenter.use_verbose_speech()
        assert result == case["expected"]

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

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        nick = "verbose" if case["setting_value"] == 1 else "brief"
        gsettings_registry.get_registry().set_runtime_value("speech", "verbosity-level", nick)

        result = presenter.get_verbosity_level()
        assert result == case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "set_verbosity_brief",
                "input_value": "brief",
                "expected": True,
            },
            {
                "id": "set_verbosity_verbose",
                "input_value": "verbose",
                "expected": True,
            },
            {
                "id": "set_verbosity_invalid",
                "input_value": "invalid",
                "expected": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_set_verbosity_level(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_verbosity_level method."""

        self._setup_dependencies(test_context)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()

        result = presenter.set_verbosity_level(case["input_value"])
        assert result == case["expected"]

        if case["expected"]:
            assert presenter.get_verbosity_level() == case["input_value"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "speak_blank_lines_true", "setting_value": True, "expected": True},
            {"id": "speak_blank_lines_false", "setting_value": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_speak_blank_lines(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test get_speak_blank_lines method."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        gsettings_registry.get_registry().set_runtime_value(
            "speech", "speak-blank-lines", case["setting_value"]
        )

        result = presenter.get_speak_blank_lines()
        assert result == case["expected"]

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

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        gsettings_registry.get_registry().set_runtime_value(
            "speech", "only-speak-displayed-text", case["setting_value"]
        )

        result = presenter.get_only_speak_displayed_text()
        assert result == case["expected"]

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

        self._setup_dependencies(test_context)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()

        result = presenter.set_only_speak_displayed_text(case["input_value"])
        assert result == case["expected"]
        assert presenter.get_only_speak_displayed_text() == case["input_value"]

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

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        gsettings_registry.get_registry().set_runtime_value(
            "speech", "speak-indentation-and-justification", case["setting_value"]
        )

        result = presenter.get_speak_indentation_and_justification()
        assert result == case["expected"]

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

        self._setup_dependencies(test_context)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()

        result = presenter.set_speak_indentation_and_justification(case["input_value"])
        assert result == case["expected"]
        assert presenter.get_speak_indentation_and_justification() == case["input_value"]

    def test_get_indentation_description_disabled(self, test_context: OrcaTestContext) -> None:
        """Test get_indentation_description method when disabled."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value("speech", "only-speak-displayed-text", True)
        registry.set_runtime_value("speech", "speak-indentation-and-justification", False)

        presenter = SpeechPresenter()
        line = "    Hello world"
        result = presenter.get_indentation_description(line)
        assert result == ""

    def test_get_indentation_description_enabled(self, test_context: OrcaTestContext) -> None:
        """Test get_indentation_description method when enabled."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value("speech", "only-speak-displayed-text", False)
        registry.set_runtime_value("speech", "speak-indentation-and-justification", True)
        registry.set_runtime_value("speech", "speak-indentation-only-if-changed", False)

        presenter = SpeechPresenter()
        line = "    Hello world"
        result = presenter.get_indentation_description(line)
        assert result != ""

    def test_get_indentation_description_only_if_changed(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_indentation_description with only-if-changed enabled."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value("speech", "only-speak-displayed-text", False)
        registry.set_runtime_value("speech", "speak-indentation-and-justification", True)
        registry.set_runtime_value("speech", "speak-indentation-only-if-changed", True)

        presenter = SpeechPresenter()
        line = "    Hello world"

        # First call should return a description
        result1 = presenter.get_indentation_description(line)
        assert result1 != ""

        # Second call with same indentation should return empty
        result2 = presenter.get_indentation_description(line)
        assert result2 == ""

    def test_get_error_description_basic(self, test_context: OrcaTestContext) -> None:
        """Test get_error_description method with basic scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        ax_text_mock = essential_modules["orca.ax_text"]
        ax_text_mock.AXText.get_character_at_offset = test_context.Mock(return_value=("a", 0))
        ax_text_mock.AXText.string_has_spelling_error = test_context.Mock(return_value=True)
        ax_text_mock.AXText.string_has_grammar_error = test_context.Mock(return_value=False)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        mock_obj = test_context.Mock()
        result = presenter.get_error_description(mock_obj, 0)
        assert result == "misspelled"

    def test_get_error_description_disabled(self, test_context: OrcaTestContext) -> None:
        """Test get_error_description method when misspelled indicator is disabled."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        gsettings_registry.get_registry().set_runtime_value(
            "speech", "speak-misspelled-indicator", False
        )

        presenter = SpeechPresenter()
        mock_obj = test_context.Mock()
        result = presenter.get_error_description(mock_obj, 0)
        assert result == ""

    def test_adjust_for_presentation(self, test_context: OrcaTestContext) -> None:
        """Test adjust_for_presentation with all sub-adjustments mocked."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        return_text = "Hello world"

        test_context.patch_object(presenter, "_adjust_for_links", return_value=return_text)
        test_context.patch_object(presenter, "adjust_for_digits", return_value=return_text)
        test_context.patch_object(presenter, "_adjust_for_repeats", return_value=return_text)
        test_context.patch_object(
            presenter,
            "_adjust_for_verbalized_punctuation",
            return_value=return_text,
        )
        test_context.patch_object(
            presenter, "_apply_pronunciation_dictionary", return_value=return_text
        )

        mock_obj = test_context.Mock()
        result = presenter.adjust_for_presentation(mock_obj, "Hello world", start_offset=0)
        assert result == return_text

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "digits_on",
                "speak_digits": True,
                "is_telephone": False,
                "input_text": "123 Main",
                "expected": "1 2 3 Main",
            },
            {
                "id": "digits_off",
                "speak_digits": False,
                "is_telephone": False,
                "input_text": "123 Main",
                "expected": "123 Main",
            },
            {
                "id": "telephone_field",
                "speak_digits": False,
                "is_telephone": True,
                "input_text": "555",
                "expected": "5 5 5",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_adjust_for_digits(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test adjust_for_digits method with speakNumbersAsDigits on/off."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        essential_modules["orca.settings"].speakNumbersAsDigits = case["speak_digits"]
        essential_modules[
            "orca.ax_utilities"
        ].AXUtilities.is_text_input_telephone = test_context.Mock(return_value=case["is_telephone"])

        from orca.speech_presenter import SpeechPresenter

        mock_obj = test_context.Mock()
        result = SpeechPresenter.adjust_for_digits(mock_obj, case["input_text"])
        assert result == case["expected"]

    def test_adjust_for_repeats(self, test_context: OrcaTestContext) -> None:
        """Test _adjust_for_repeats with repeated characters."""

        self._setup_dependencies(test_context)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        text = "----"
        result = presenter._adjust_for_repeats(text)
        # Should describe repeated characters
        assert "repeated" in result or result != text

    def test_adjust_for_repeats_short_text(self, test_context: OrcaTestContext) -> None:
        """Test _adjust_for_repeats with text shorter than limit."""

        self._setup_dependencies(test_context)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        text = "hi"
        result = presenter._adjust_for_repeats(text)
        # Short text should be returned unchanged
        assert result == text

    def test_get_speech_preferences(self, test_context: OrcaTestContext) -> None:
        """Test get_speech_preferences returns correct tuple structure."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        result = presenter.get_speech_preferences()

        assert isinstance(result, tuple)
        assert len(result) == 3

        general, object_details, announcements = result

        # general should have 1 preference
        assert len(general) == 1
        assert general[0].prefs_key == "messagesAreDetailed"

        # object_details should have 5 preferences
        assert len(object_details) == 5
        assert object_details[0].prefs_key == "onlySpeakDisplayedText"

        # announcements should have 6 preferences
        assert len(announcements) == 6
        assert announcements[0].prefs_key == "speakContextBlockquote"

    def test_apply_speech_preferences(self, test_context: OrcaTestContext) -> None:
        """Test apply_speech_preferences applies values correctly."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter, SpeechPreference

        presenter = SpeechPresenter()

        mock_setter1 = test_context.Mock(return_value=True)
        mock_setter2 = test_context.Mock(return_value=True)
        pref1 = SpeechPreference("key1", "Label 1", lambda: True, mock_setter1)
        pref2 = SpeechPreference("key2", "Label 2", lambda: False, mock_setter2)

        updates = [(pref1, False), (pref2, True)]
        result = presenter.apply_speech_preferences(updates)

        assert result == {"key1": False, "key2": True}
        mock_setter1.assert_called_once_with(False)
        mock_setter2.assert_called_once_with(True)

    def test_toggle_indentation_and_justification(self, test_context: OrcaTestContext) -> None:
        """Test toggle_indentation_and_justification method."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        result = presenter.toggle_indentation_and_justification()
        assert result is True

    def test_change_number_style(self, test_context: OrcaTestContext) -> None:
        """Test change_number_style method."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        result = presenter.change_number_style()
        assert result is True

    def test_should_verbalize_punctuation_false(self, test_context: OrcaTestContext) -> None:
        """Test _should_verbalize_punctuation static method returns False."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        essential_modules["orca.ax_object"].AXObject.find_ancestor_inclusive.return_value = None
        mock_obj = test_context.Mock()
        result = SpeechPresenter._should_verbalize_punctuation(mock_obj)
        assert result is False

    def test_should_verbalize_punctuation_true(self, test_context: OrcaTestContext) -> None:
        """Test _should_verbalize_punctuation static method returns True."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        mock_code_obj = test_context.Mock()
        (
            essential_modules["orca.ax_object"].AXObject.find_ancestor_inclusive.return_value
        ) = mock_code_obj
        essential_modules["orca.ax_document"].AXDocument.is_plain_text.return_value = False
        mock_obj = test_context.Mock()
        result = SpeechPresenter._should_verbalize_punctuation(mock_obj)
        assert result is True

    def test_adjust_for_verbalized_punctuation(self, test_context: OrcaTestContext) -> None:
        """Test _adjust_for_verbalized_punctuation static method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        mock_code_obj = test_context.Mock()
        (
            essential_modules["orca.ax_object"].AXObject.find_ancestor_inclusive.return_value
        ) = mock_code_obj
        essential_modules["orca.ax_document"].AXDocument.is_plain_text.return_value = False
        mock_obj = test_context.Mock()
        text = "Hello, world! How are you?"
        result = SpeechPresenter._adjust_for_verbalized_punctuation(mock_obj, text)

        expected = "Hello ,  world !  How are you ? "
        assert result == expected

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "set_speak_blank_lines_true", "input_value": True, "expected": True},
            {"id": "set_speak_blank_lines_false", "input_value": False, "expected": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_set_speak_blank_lines(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test set_speak_blank_lines method."""

        self._setup_dependencies(test_context)

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()

        result = presenter.set_speak_blank_lines(case["input_value"])
        assert result == case["expected"]
        assert presenter.get_speak_blank_lines() == case["input_value"]

    def test_get_presenter_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter function returns the same instance."""

        self._setup_dependencies(test_context)
        from orca import speech_presenter

        presenter1 = speech_presenter.get_presenter()
        presenter2 = speech_presenter.get_presenter()

        assert presenter1 is presenter2
        assert isinstance(presenter1, speech_presenter.SpeechPresenter)

    def _setup_speech_output_dependencies(
        self, test_context: OrcaTestContext
    ) -> dict[str, MagicMock]:
        """Set up additional mocks needed for speech output method testing."""

        essential_modules = self._setup_dependencies(test_context)

        # Add speech module mock
        speech_mock = essential_modules["orca.speech"]
        speech_mock.speak = test_context.Mock()
        speech_mock.speak_character = test_context.Mock()
        speech_mock.speak_key_event = test_context.Mock()

        # Add phonnames module mock
        phonnames_mock = essential_modules["orca.phonnames"]
        phonnames_mock.get_phonetic_name = test_context.Mock(side_effect=lambda c: f"phonetic_{c}")

        # Add speech_manager mock
        speech_manager_mock = essential_modules["orca.speech_manager"]
        speech_manager_instance = test_context.Mock()
        speech_manager_instance.get_speech_is_muted = test_context.Mock(return_value=False)
        speech_manager_instance.get_speech_is_enabled_and_not_muted = test_context.Mock(
            return_value=True
        )
        speech_manager_instance.get_capitalization_style = test_context.Mock(return_value="icon")
        speech_manager_instance.set_capitalization_style = test_context.Mock()
        speech_manager_instance.get_punctuation_level = test_context.Mock(return_value="all")
        speech_manager_instance.set_punctuation_level = test_context.Mock()
        speech_manager_mock.get_manager = test_context.Mock(return_value=speech_manager_instance)

        # Add script_manager mock for _get_active_script / _get_voice
        script_manager_mock = essential_modules["orca.script_manager"]
        mock_script = test_context.Mock()
        mock_script.speech_generator.voice = test_context.Mock(return_value=[{"family": "default"}])
        mock_script.speech_generator.generate_contents = test_context.Mock(
            return_value=["generated speech"]
        )
        script_manager_instance = test_context.Mock()
        script_manager_instance.get_active_script = test_context.Mock(return_value=mock_script)
        script_manager_mock.get_manager = test_context.Mock(return_value=script_manager_instance)

        # Settings for voice resolution
        settings_mock = essential_modules["orca.settings"]
        settings_mock.voices = {"default": {}, "system": {}}
        settings_mock.SYSTEM_VOICE = "system"

        return essential_modules

    def test_get_voice_with_active_script(self, test_context: OrcaTestContext) -> None:
        """Test _get_voice returns voice from active script."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        voice = presenter._get_voice(text="test")

        script_manager = essential_modules["orca.script_manager"].get_manager()
        script = script_manager.get_active_script()
        script.speech_generator.voice.assert_called_with(string="test")
        assert voice == [{"family": "default"}]

    def test_get_voice_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test _get_voice returns empty list when no active script."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        script_manager = essential_modules["orca.script_manager"].get_manager()
        script_manager.get_active_script.return_value = None

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        voice = presenter._get_voice(text="test")

        assert voice == []

    def test_speak_message(self, test_context: OrcaTestContext) -> None:
        """Test speak_message speaks text via speech module."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.speak_message("Hello world")

        essential_modules["orca.speech"].speak.assert_called()

    def test_speak_message_non_string(self, test_context: OrcaTestContext) -> None:
        """Test speak_message with non-string returns early."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.speak_message(123)  # type: ignore

        essential_modules["orca.debug"].print_exception.assert_called()
        essential_modules["orca.speech"].speak.assert_not_called()

    def test_speak_message_muted(self, test_context: OrcaTestContext) -> None:
        """Test speak_message when speech is muted."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        speech_manager = essential_modules["orca.speech_manager"].get_manager()
        speech_manager.get_speech_is_muted.return_value = True

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.speak_message("Hello world")

        essential_modules["orca.speech"].speak.assert_not_called()

    def test_speak_message_only_displayed_text(self, test_context: OrcaTestContext) -> None:
        """Test speak_message when only_speak_displayed_text is true."""

        essential_modules = self._setup_speech_output_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        gsettings_registry.get_registry().set_runtime_value(
            "speech", "only-speak-displayed-text", True
        )

        presenter = SpeechPresenter()
        presenter.speak_message("Hello world")

        essential_modules["orca.speech"].speak.assert_not_called()

    def test_speak_character(self, test_context: OrcaTestContext) -> None:
        """Test speak_character speaks a single character."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.speak_character("a")

        essential_modules["orca.speech"].speak_character.assert_called_once()

    def test_spell_item(self, test_context: OrcaTestContext) -> None:
        """Test spell_item speaks each character."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.spell_item("abc")

        assert essential_modules["orca.speech"].speak_character.call_count == 3

    def test_spell_phonetically(self, test_context: OrcaTestContext) -> None:
        """Test spell_phonetically speaks phonetic names."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.spell_phonetically("ab")

        essential_modules["orca.phonnames"].get_phonetic_name.assert_called()
        assert essential_modules["orca.speech"].speak.call_count >= 2

    def test_speak_contents(self, test_context: OrcaTestContext) -> None:
        """Test speak_contents generates and speaks contents."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        presenter.speak_contents(mock_contents)

        script_manager = essential_modules["orca.script_manager"].get_manager()
        script = script_manager.get_active_script()
        script.speech_generator.generate_contents.assert_called_once()
        essential_modules["orca.speech"].speak.assert_called()

    def test_speak_contents_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test speak_contents returns early when no active script."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        script_manager = essential_modules["orca.script_manager"].get_manager()
        script_manager.get_active_script.return_value = None

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        presenter.speak_contents(mock_contents)

        essential_modules["orca.speech"].speak.assert_not_called()

    def test_present_key_event(self, test_context: OrcaTestContext) -> None:
        """Test present_key_event speaks key via speech module."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        mock_event = test_context.Mock()
        mock_event.is_printable_key.return_value = True
        mock_event.get_key_name.return_value = "a"
        presenter.present_key_event(mock_event)

        essential_modules["orca.speech"].speak_key_event.assert_called_once()

    def test_present_message_speaks(self, test_context: OrcaTestContext) -> None:
        """Test present_message delegates to speak_message when enabled."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.present_message("Full message", "Brief")

        essential_modules["orca.speech"].speak.assert_called()

    def test_present_message_disabled(self, test_context: OrcaTestContext) -> None:
        """Test present_message does nothing when speech disabled."""

        essential_modules = self._setup_speech_output_dependencies(test_context)
        speech_manager = essential_modules["orca.speech_manager"].get_manager()
        speech_manager.get_speech_is_enabled_and_not_muted.return_value = False

        from orca.speech_presenter import SpeechPresenter

        presenter = SpeechPresenter()
        presenter.present_message("Full message", "Brief")

        essential_modules["orca.speech"].speak.assert_not_called()

    def test_present_message_uses_brief(self, test_context: OrcaTestContext) -> None:
        """Test present_message uses brief when messages not detailed."""

        essential_modules = self._setup_speech_output_dependencies(test_context)

        from orca import gsettings_registry
        from orca.speech_presenter import SpeechPresenter

        gsettings_registry.get_registry().set_runtime_value(
            "speech", "messages-are-detailed", False
        )

        presenter = SpeechPresenter()
        presenter.present_message("Full message", "Brief")

        # The speech.speak call should contain "Brief" not "Full message"
        call_args = essential_modules["orca.speech"].speak.call_args
        assert call_args is not None
        assert "Brief" in str(call_args)

    def test_get_set_monitor_is_enabled(self, test_context: OrcaTestContext) -> None:
        """Test getting and setting speech monitor enabled status."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()

        result = presenter.set_monitor_is_enabled(True)
        assert result is True
        assert presenter.get_monitor_is_enabled() is True

        result = presenter.set_monitor_is_enabled(False)
        assert result is True
        assert presenter.get_monitor_is_enabled() is False

    def test_ensure_monitor_creates_when_enabled(self, test_context: OrcaTestContext) -> None:
        """Test _ensure_monitor creates monitor on demand when enabled."""

        essential_modules = self._setup_dependencies(test_context)
        speech_monitor_mock = essential_modules["orca.speech_monitor"]
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        mock_monitor = test_context.Mock()
        speech_monitor_mock.SpeechMonitor.return_value = mock_monitor

        result = presenter._ensure_monitor()

        speech_monitor_mock.SpeechMonitor.assert_called_once()
        mock_monitor.show_all.assert_called_once()
        assert result is mock_monitor

    def test_ensure_monitor_returns_none_when_disabled(self, test_context: OrcaTestContext) -> None:
        """Test _ensure_monitor returns None when disabled."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(False)
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        result = presenter._ensure_monitor()

        assert result is None

    def test_write_to_monitor(self, test_context: OrcaTestContext) -> None:
        """Test write_to_monitor writes text when monitor active and not focused."""

        essential_modules = self._setup_dependencies(test_context)
        speech_monitor_mock = essential_modules["orca.speech_monitor"]
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        mock_monitor = test_context.Mock()
        mock_monitor.has_toplevel_focus.return_value = False
        speech_monitor_mock.SpeechMonitor.return_value = mock_monitor

        presenter.write_to_monitor("hello world")

        mock_monitor.write_text.assert_called_once_with("hello world")

    def test_write_to_monitor_skips_when_focused(self, test_context: OrcaTestContext) -> None:
        """Test write_to_monitor skips when monitor has focus."""

        essential_modules = self._setup_dependencies(test_context)
        speech_monitor_mock = essential_modules["orca.speech_monitor"]
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        mock_monitor = test_context.Mock()
        mock_monitor.has_toplevel_focus.return_value = True
        speech_monitor_mock.SpeechMonitor.return_value = mock_monitor

        presenter.write_to_monitor("hello world")

        mock_monitor.write_text.assert_not_called()

    def test_write_key_to_monitor(self, test_context: OrcaTestContext) -> None:
        """Test write_key_to_monitor writes key event."""

        essential_modules = self._setup_dependencies(test_context)
        speech_monitor_mock = essential_modules["orca.speech_monitor"]
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        mock_monitor = test_context.Mock()
        mock_monitor.has_toplevel_focus.return_value = False
        speech_monitor_mock.SpeechMonitor.return_value = mock_monitor

        presenter.write_key_to_monitor("Return")

        mock_monitor.write_key_event.assert_called_once_with("Return")

    def test_write_character_to_monitor(self, test_context: OrcaTestContext) -> None:
        """Test write_character_to_monitor writes character."""

        essential_modules = self._setup_dependencies(test_context)
        speech_monitor_mock = essential_modules["orca.speech_monitor"]
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        presenter.set_monitor_is_enabled(True)
        mock_monitor = test_context.Mock()
        mock_monitor.has_toplevel_focus.return_value = False
        speech_monitor_mock.SpeechMonitor.return_value = mock_monitor

        presenter.write_character_to_monitor("a")

        mock_monitor.write_character.assert_called_once_with("a")

    def test_destroy_monitor(self, test_context: OrcaTestContext) -> None:
        """Test destroy_monitor destroys existing speech monitor."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        mock_monitor = test_context.Mock()
        presenter._monitor = mock_monitor

        presenter.destroy_monitor()

        mock_monitor.destroy.assert_called_once()
        assert presenter._monitor is None

    def test_destroy_monitor_no_op_when_none(self, test_context: OrcaTestContext) -> None:
        """Test destroy_monitor does nothing when no monitor exists."""

        self._setup_dependencies(test_context)
        from orca.speech_presenter import get_presenter

        presenter = get_presenter()
        assert presenter._monitor is None

        presenter.destroy_monitor()

        assert presenter._monitor is None
