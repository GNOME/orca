# Unit tests for typing_echo_presenter.py methods.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Unit tests for typing_echo_presenter.py methods."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


class _FakeGtkGrid:  # noqa: D401 - simple test stub
    """Minimal stub used in unit tests."""

    def __init__(self, *_args, **_kwargs):
        """Initialize fake GTK grid."""
        self._children = []

    def attach(self, *args, **kwargs):
        """Attach widget to grid."""
        self._children.append((args, kwargs))

    def set_border_width(self, *_args, **_kwargs):
        """Set border width."""
        return None

    def set_margin_start(self, *_args, **_kwargs):
        """Set margin start."""
        return None

    def show_all(self):
        """Show all widgets."""
        return None


class _FakeCheckButton:  # noqa: D401 - simple test stub
    """Minimal stub emulating Gtk.CheckButton for unit tests."""

    def __init__(self, label: str):
        self.label = label
        self.name = label
        self._active = False
        self._signal_handlers: dict[str, tuple] = {}

    @classmethod
    def new_with_mnemonic(cls, label: str) -> "_FakeCheckButton":
        """Create new check button with mnemonic."""
        return cls(label)

    def set_name(self, name: str) -> None:
        """Set widget name."""
        self.name = name

    def set_use_underline(self, *_args, **_kwargs) -> None:  # pragma: no cover - unused
        """Set use underline."""
        return None

    def set_receives_default(self, *_args, **_kwargs) -> None:  # pragma: no cover
        """Set receives default."""
        return None

    def connect(self, signal: str, handler, data) -> None:
        """Connect signal handler."""
        self._signal_handlers[signal] = (handler, data)

    def set_active(self, active: bool) -> None:
        """Set active state."""
        self._active = active

    def get_active(self) -> bool:  # pragma: no cover - helper when needed
        """Get active state."""
        return self._active

    def set_sensitive(self, _sensitive: bool) -> None:
        """Set sensitive state."""
        return None


@pytest.mark.unit
class TestTypingEchoPresenter:
    """Test TypingEchoPresenter and TypingEchoPreferencesGrid."""

    def _setup_presenter(self, test_context: OrcaTestContext):
        """Set up presenter and dependencies for testing."""
        additional_modules = [
            "gi",
            "gi.repository",
            "orca.cmdnames",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
            "orca.braille_presenter",
            "orca.presentation_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        # Set up cmdnames with all required values for structural_navigator
        cmdnames = essential_modules["orca.cmdnames"]
        cmdnames.STRUCTURAL_NAVIGATION_MODE_CYCLE = "cycle_mode"
        cmdnames.BLOCKQUOTE_PREV = "previous_blockquote"
        cmdnames.BLOCKQUOTE_NEXT = "next_blockquote"
        cmdnames.BLOCKQUOTE_LIST = "list_blockquotes"
        cmdnames.BUTTON_PREV = "previous_button"
        cmdnames.BUTTON_NEXT = "next_button"
        cmdnames.BUTTON_LIST = "list_buttons"
        cmdnames.CHECK_BOX_PREV = "previous_checkbox"
        cmdnames.CHECK_BOX_NEXT = "next_checkbox"
        cmdnames.CHECK_BOX_LIST = "list_checkboxes"
        cmdnames.COMBO_BOX_PREV = "previous_combobox"
        cmdnames.COMBO_BOX_NEXT = "next_combobox"
        cmdnames.COMBO_BOX_LIST = "list_comboboxes"
        cmdnames.ENTRY_PREV = "previous_entry"
        cmdnames.ENTRY_NEXT = "next_entry"
        cmdnames.ENTRY_LIST = "list_entries"
        cmdnames.FORM_FIELD_PREV = "previous_form_field"
        cmdnames.FORM_FIELD_NEXT = "next_form_field"
        cmdnames.FORM_FIELD_LIST = "list_form_fields"
        cmdnames.HEADING_PREV = "previous_heading"
        cmdnames.HEADING_NEXT = "next_heading"
        cmdnames.HEADING_LIST = "list_headings"
        cmdnames.HEADING_AT_LEVEL_PREV = "previous_heading_level_%d"
        cmdnames.HEADING_AT_LEVEL_NEXT = "next_heading_level_%d"
        cmdnames.HEADING_AT_LEVEL_LIST = "list_headings_level_%d"
        cmdnames.IFRAME_PREV = "previous_iframe"
        cmdnames.IFRAME_NEXT = "next_iframe"
        cmdnames.IFRAME_LIST = "list_iframes"
        cmdnames.IMAGE_PREV = "previous_image"
        cmdnames.IMAGE_NEXT = "next_image"
        cmdnames.IMAGE_LIST = "list_images"
        cmdnames.LANDMARK_PREV = "previous_landmark"
        cmdnames.LANDMARK_NEXT = "next_landmark"
        cmdnames.LANDMARK_LIST = "list_landmarks"
        cmdnames.LIST_PREV = "previous_list"
        cmdnames.LIST_NEXT = "next_list"
        cmdnames.LIST_LIST = "list_lists"
        cmdnames.LIST_ITEM_PREV = "previous_list_item"
        cmdnames.LIST_ITEM_NEXT = "next_list_item"
        cmdnames.LIST_ITEM_LIST = "list_list_items"
        cmdnames.LIVE_REGION_PREV = "previous_live_region"
        cmdnames.LIVE_REGION_NEXT = "next_live_region"
        cmdnames.LIVE_REGION_LAST = "last_live_region"
        cmdnames.PARAGRAPH_PREV = "previous_paragraph"
        cmdnames.PARAGRAPH_NEXT = "next_paragraph"
        cmdnames.PARAGRAPH_LIST = "list_paragraphs"
        cmdnames.RADIO_BUTTON_PREV = "previous_radio_button"
        cmdnames.RADIO_BUTTON_NEXT = "next_radio_button"
        cmdnames.RADIO_BUTTON_LIST = "list_radio_buttons"
        cmdnames.SEPARATOR_PREV = "previous_separator"
        cmdnames.SEPARATOR_NEXT = "next_separator"
        cmdnames.TABLE_PREV = "previous_table"
        cmdnames.TABLE_NEXT = "next_table"
        cmdnames.TABLE_LIST = "list_tables"
        cmdnames.UNVISITED_LINK_PREV = "previous_unvisited_link"
        cmdnames.UNVISITED_LINK_NEXT = "next_unvisited_link"
        cmdnames.UNVISITED_LINK_LIST = "list_unvisited_links"
        cmdnames.VISITED_LINK_PREV = "previous_visited_link"
        cmdnames.VISITED_LINK_NEXT = "next_visited_link"
        cmdnames.VISITED_LINK_LIST = "list_visited_links"
        cmdnames.LINK_PREV = "previous_link"
        cmdnames.LINK_NEXT = "next_link"
        cmdnames.LINK_LIST = "list_links"
        cmdnames.CLICKABLE_PREV = "previous_clickable"
        cmdnames.CLICKABLE_NEXT = "next_clickable"
        cmdnames.CLICKABLE_LIST = "list_clickables"
        cmdnames.LARGE_OBJECT_PREV = "previous_large_object"
        cmdnames.LARGE_OBJECT_NEXT = "next_large_object"
        cmdnames.LARGE_OBJECT_LIST = "list_large_objects"
        cmdnames.CONTAINER_START = "container_start"
        cmdnames.CONTAINER_END = "container_end"

        # Set up settings mock for structural_navigator
        settings_mock = essential_modules["orca.settings"]
        settings_mock.structuralNavigationEnabled = True
        settings_mock.structNavTriggersFocusMode = True
        settings_mock.wrappedStructuralNavigation = True
        settings_mock.largeObjectTextLength = 75

        essential_modules["orca.orca_i18n"]._ = lambda x: x
        essential_modules["orca.debug"].print_message = test_context.Mock()
        essential_modules["orca.debug"].LEVEL_INFO = 800

        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module.return_value = None
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = controller_mock

        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_locus_of_focus.return_value = None
        essential_modules["orca.focus_manager"].get_manager.return_value = focus_manager_instance

        essential_modules["orca.AXObject"].supports_collection.return_value = True
        essential_modules["orca.AXUtilities"].is_heading.return_value = False

        test_context.patch("gi.repository.Gtk.Grid", new=_FakeGtkGrid)
        test_context.patch("gi.repository.Gtk.CheckButton", new=_FakeCheckButton)

        guilabels_mock = essential_modules["orca.guilabels"]
        guilabels_mock.ECHO_ENABLE_KEY_ECHO = "Enable _key echo"
        guilabels_mock.ECHO_ALPHABETIC_KEYS = "Enable _alphabetic keys"
        guilabels_mock.ECHO_NUMERIC_KEYS = "Enable n_umeric keys"
        guilabels_mock.ECHO_PUNCTUATION_KEYS = "Enable _punctuation keys"
        guilabels_mock.ECHO_SPACE = "Enable _space"
        guilabels_mock.ECHO_MODIFIER_KEYS = "Enable _modifier keys"
        guilabels_mock.ECHO_FUNCTION_KEYS = "Enable _function keys"
        guilabels_mock.ECHO_ACTION_KEYS = "Enable ac_tion keys"
        guilabels_mock.ECHO_NAVIGATION_KEYS = "Enable _navigation keys"
        guilabels_mock.ECHO_DIACRITICAL_KEYS = "Enable non-spacing _diacritical keys"
        guilabels_mock.ECHO_CHARACTER = "Enable echo by cha_racter"
        guilabels_mock.ECHO_WORD = "Enable echo by _word"
        guilabels_mock.ECHO_SENTENCE = "Enable echo by _sentence"

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = settings_manager_mock.get_manager.return_value
        settings_mock = essential_modules["orca.settings"]

        value_map = {
            "enableKeyEcho": True,
            "enableAlphabeticKeys": True,
            "enableNumericKeys": False,
            "enablePunctuationKeys": False,
            "enableSpace": True,
            "enableModifierKeys": False,
            "enableFunctionKeys": True,
            "enableActionKeys": False,
            "enableNavigationKeys": True,
            "enableDiacriticalKeys": False,
            "enableEchoByCharacter": True,
            "enableEchoByWord": False,
            "enableEchoBySentence": True,
        }

        for key, value in value_map.items():
            setattr(settings_mock, key, value)

        def set_setting(key: str, value: bool) -> bool:
            value_map[key] = value
            setattr(settings_mock, key, value)
            return True

        manager_instance.set_setting.side_effect = set_setting

        from gi.repository import Atspi

        test_context.patch_object(Atspi, "Accessible", new=type("Accessible", (), {}))
        test_context.patch_object(Atspi, "Hyperlink", new=type("Hyperlink", (), {}))
        test_context.patch_object(
            Atspi, "Role", new=type("Role", (), {"PASSWORD_TEXT": 42, "PANEL": 36})
        )
        test_context.patch_object(
            Atspi,
            "CollectionMatchType",
            new=type("CollectionMatchType", (), {"ALL": 0, "ANY": 1}),
        )
        test_context.patch_object(Atspi, "MatchRule", new=type("MatchRule", (), {}))
        test_context.patch_object(
            Atspi,
            "RelationType",
            new=type("RelationType", (), {"LABELLED_BY": 0}),
        )
        test_context.patch_object(Atspi, "Relation", new=type("Relation", (), {}))

        from orca.typing_echo_presenter import TypingEchoPresenter

        presenter = TypingEchoPresenter()
        return presenter, manager_instance, value_map, settings_mock

    @pytest.mark.parametrize(
        "getter_name,setter_name,setting_key,test_value",
        [
            ("get_key_echo_enabled", "set_key_echo_enabled", "enableKeyEcho", False),
            (
                "get_character_echo_enabled",
                "set_character_echo_enabled",
                "enableEchoByCharacter",
                False,
            ),
            ("get_word_echo_enabled", "set_word_echo_enabled", "enableEchoByWord", True),
            (
                "get_sentence_echo_enabled",
                "set_sentence_echo_enabled",
                "enableEchoBySentence",
                False,
            ),
            (
                "get_alphabetic_keys_enabled",
                "set_alphabetic_keys_enabled",
                "enableAlphabeticKeys",
                False,
            ),
            ("get_numeric_keys_enabled", "set_numeric_keys_enabled", "enableNumericKeys", True),
            (
                "get_punctuation_keys_enabled",
                "set_punctuation_keys_enabled",
                "enablePunctuationKeys",
                True,
            ),
            ("get_space_enabled", "set_space_enabled", "enableSpace", False),
            ("get_modifier_keys_enabled", "set_modifier_keys_enabled", "enableModifierKeys", True),
            ("get_function_keys_enabled", "set_function_keys_enabled", "enableFunctionKeys", False),
            ("get_action_keys_enabled", "set_action_keys_enabled", "enableActionKeys", True),
            (
                "get_navigation_keys_enabled",
                "set_navigation_keys_enabled",
                "enableNavigationKeys",
                False,
            ),
            (
                "get_diacritical_keys_enabled",
                "set_diacritical_keys_enabled",
                "enableDiacriticalKeys",
                True,
            ),
        ],
    )
    def test_presenter_getters_and_setters(
        self,
        test_context: OrcaTestContext,
        getter_name: str,
        setter_name: str,
        setting_key: str,
        test_value: bool,
    ) -> None:
        """Test presenter getter and setter methods."""
        presenter, manager_instance, value_map, _settings_mock = self._setup_presenter(test_context)

        getter = getattr(presenter, getter_name)
        setter = getattr(presenter, setter_name)

        assert getter() is value_map[setting_key]
        setter(test_value)
        assert getattr(_settings_mock, setting_key) == test_value

    def test_locking_keys_presented_getter_and_setter(self, test_context: OrcaTestContext) -> None:
        """Test locking keys presented getter and setter with special logic."""
        presenter, _manager, _value_map, settings_mock = self._setup_presenter(test_context)

        settings_mock.presentLockingKeys = True
        assert presenter.get_locking_keys_presented() is True

        settings_mock.presentLockingKeys = False
        assert presenter.get_locking_keys_presented() is False

        settings_mock.presentLockingKeys = None

        speech_presenter_patch = test_context.patch("orca.speech_presenter.get_presenter")
        speech_presenter_instance = speech_presenter_patch.return_value

        speech_presenter_instance.get_only_speak_displayed_text.return_value = False
        assert presenter.get_locking_keys_presented() is True

        speech_presenter_instance.get_only_speak_displayed_text.return_value = True
        assert presenter.get_locking_keys_presented() is False

        presenter.set_locking_keys_presented(True)
        assert settings_mock.presentLockingKeys is True

        presenter.set_locking_keys_presented(None)
        assert settings_mock.presentLockingKeys is None

    def test_cycle_key_echo_basic_transitions(self, test_context: OrcaTestContext) -> None:
        """Test cycle_key_echo method basic state transitions."""
        presenter, manager_instance, value_map, _settings_mock = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()

        value_map["enableKeyEcho"] = False
        value_map["enableEchoByWord"] = False
        value_map["enableEchoBySentence"] = False
        _settings_mock.enableKeyEcho = False
        _settings_mock.enableEchoByWord = False
        _settings_mock.enableEchoBySentence = False

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert _settings_mock.enableKeyEcho is True
        assert _settings_mock.enableEchoByWord is False
        assert _settings_mock.enableEchoBySentence is False

        value_map["enableKeyEcho"] = True
        value_map["enableEchoByWord"] = False
        value_map["enableEchoBySentence"] = False
        _settings_mock.enableKeyEcho = True
        _settings_mock.enableEchoByWord = False
        _settings_mock.enableEchoBySentence = False

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert _settings_mock.enableKeyEcho is False
        assert _settings_mock.enableEchoByWord is True
        assert _settings_mock.enableEchoBySentence is False

    def test_cycle_key_echo_advanced_transitions(self, test_context: OrcaTestContext) -> None:
        """Test cycle_key_echo method advanced state transitions."""
        presenter, manager_instance, value_map, _settings_mock = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()

        value_map["enableKeyEcho"] = False
        value_map["enableEchoByWord"] = True
        value_map["enableEchoBySentence"] = False
        _settings_mock.enableKeyEcho = False
        _settings_mock.enableEchoByWord = True
        _settings_mock.enableEchoBySentence = False

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert _settings_mock.enableKeyEcho is False
        assert _settings_mock.enableEchoByWord is False
        assert _settings_mock.enableEchoBySentence is True

        value_map["enableKeyEcho"] = False
        value_map["enableEchoByWord"] = False
        value_map["enableEchoBySentence"] = True
        _settings_mock.enableKeyEcho = False
        _settings_mock.enableEchoByWord = False
        _settings_mock.enableEchoBySentence = True

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert _settings_mock.enableKeyEcho is True
        assert _settings_mock.enableEchoByWord is True
        assert _settings_mock.enableEchoBySentence is False

        value_map["enableKeyEcho"] = True
        value_map["enableEchoByWord"] = True
        value_map["enableEchoBySentence"] = False
        _settings_mock.enableKeyEcho = True
        _settings_mock.enableEchoByWord = True
        _settings_mock.enableEchoBySentence = False

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert _settings_mock.enableKeyEcho is False
        assert _settings_mock.enableEchoByWord is True
        assert _settings_mock.enableEchoBySentence is True

        value_map["enableKeyEcho"] = True
        value_map["enableEchoByWord"] = False
        value_map["enableEchoBySentence"] = True
        _settings_mock.enableKeyEcho = True
        _settings_mock.enableEchoByWord = False
        _settings_mock.enableEchoBySentence = True

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert _settings_mock.enableKeyEcho is False
        assert _settings_mock.enableEchoByWord is False
        assert _settings_mock.enableEchoBySentence is False

    def test_cycle_key_echo_with_script_presentation(self, test_context: OrcaTestContext) -> None:
        """Test cycle_key_echo calls present_message when script is provided."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        script_mock = test_context.mocker.MagicMock()

        value_map["enableKeyEcho"] = False
        value_map["enableEchoByWord"] = False
        value_map["enableEchoBySentence"] = False
        _settings_mock.enableKeyEcho = False
        _settings_mock.enableEchoByWord = False
        _settings_mock.enableEchoBySentence = False

        from orca import presentation_manager

        pres_manager: Any = presentation_manager.get_manager()
        pres_manager.present_message.reset_mock()

        presenter.cycle_key_echo(script_mock, None, True)
        pres_manager.present_message.assert_called_once()

        pres_manager.present_message.reset_mock()
        presenter.cycle_key_echo(script_mock, None, False)
        pres_manager.present_message.assert_not_called()

        presenter.cycle_key_echo(None, None, True)

    def test_should_echo_keyboard_event_basic_cases(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for basic cases."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "a"

        event_mock.is_pressed_key.return_value = False
        assert presenter.should_echo_keyboard_event(event_mock) is False

        event_mock.is_pressed_key.return_value = True
        value_map["enableKeyEcho"] = False
        _settings_mock.enableKeyEcho = False
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = False
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_orca_modifier(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for Orca modifier keys."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "Insert_L"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = True

        event_mock.get_click_count.return_value = 2
        assert presenter.should_echo_keyboard_event(event_mock) is True

        event_mock.get_click_count.return_value = 1
        value_map["enableKeyEcho"] = True
        value_map["enableModifierKeys"] = True
        _settings_mock.enableKeyEcho = True
        _settings_mock.enableModifierKeys = True
        assert presenter.should_echo_keyboard_event(event_mock) is True

        value_map["enableModifierKeys"] = False
        _settings_mock.enableModifierKeys = False
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_modified_keys(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for modified keys."""
        presenter, _manager_instance, _value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "a"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False

        event_mock.is_alt_control_or_orca_modified.return_value = True
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_character_echoable(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test should_echo_keyboard_event when character is echoable."""
        presenter, _manager_instance, _value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "a"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False

        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=True)
        assert presenter.should_echo_keyboard_event(event_mock) is False

    @pytest.mark.parametrize(
        "key_type,setting_key,expected_result",
        [
            # Standard key types - enabled
            ("alphabetic", "enableAlphabeticKeys", True),
            ("numeric", "enableNumericKeys", True),
            ("punctuation", "enablePunctuationKeys", True),
            ("modifier", "enableModifierKeys", True),
            ("function", "enableFunctionKeys", True),
            ("action", "enableActionKeys", True),
            ("navigation", "enableNavigationKeys", True),
            ("diacritical", "enableDiacriticalKeys", True),
            # Standard key types - disabled
            ("alphabetic", "enableAlphabeticKeys", False),
            ("numeric", "enableNumericKeys", False),
            ("punctuation", "enablePunctuationKeys", False),
            ("modifier", "enableModifierKeys", False),
            ("function", "enableFunctionKeys", False),
            ("action", "enableActionKeys", False),
            ("navigation", "enableNavigationKeys", False),
            ("diacritical", "enableDiacriticalKeys", False),
        ],
    )
    def test_should_echo_keyboard_event_key_types(
        self, test_context: OrcaTestContext, key_type: str, setting_key: str, expected_result: bool
    ) -> None:
        """Test should_echo_keyboard_event for different key types."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "test_key"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = False
        event_mock.is_space.return_value = False
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)

        # Set all key type checks to False first
        event_mock.is_alphabetic_key.return_value = False
        event_mock.is_numeric_key.return_value = False
        event_mock.is_punctuation_key.return_value = False
        event_mock.is_modifier_key.return_value = False
        event_mock.is_function_key.return_value = False
        event_mock.is_action_key.return_value = False
        event_mock.is_navigation_key.return_value = False
        event_mock.is_diacritical_key.return_value = False

        # Enable the specific key type being tested
        setattr(event_mock, f"is_{key_type}_key", lambda: True)

        value_map["enableKeyEcho"] = True
        value_map[setting_key] = expected_result
        _settings_mock.enableKeyEcho = True
        setattr(_settings_mock, setting_key, expected_result)

        result = presenter.should_echo_keyboard_event(event_mock)
        assert result is expected_result

    def test_should_echo_keyboard_event_space_key_scenarios(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test should_echo_keyboard_event for space key with different settings."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "space"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = False
        event_mock.is_space.return_value = True
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)

        # Set all other key types to False
        event_mock.is_alphabetic_key.return_value = False
        event_mock.is_numeric_key.return_value = False
        event_mock.is_punctuation_key.return_value = False
        event_mock.is_modifier_key.return_value = False
        event_mock.is_function_key.return_value = False
        event_mock.is_action_key.return_value = False
        event_mock.is_navigation_key.return_value = False
        event_mock.is_diacritical_key.return_value = False

        value_map["enableKeyEcho"] = True
        _settings_mock.enableKeyEcho = True

        # Test space key with space setting enabled
        value_map["enableSpace"] = True
        value_map["enableEchoByCharacter"] = False
        _settings_mock.enableSpace = True
        _settings_mock.enableEchoByCharacter = False
        assert presenter.should_echo_keyboard_event(event_mock) is True

        # Test space key with space disabled but character echo enabled (should echo)
        value_map["enableSpace"] = False
        value_map["enableEchoByCharacter"] = True
        _settings_mock.enableSpace = False
        _settings_mock.enableEchoByCharacter = True
        assert presenter.should_echo_keyboard_event(event_mock) is True

        # Test space key with both space and character echo disabled
        value_map["enableSpace"] = False
        value_map["enableEchoByCharacter"] = False
        _settings_mock.enableSpace = False
        _settings_mock.enableEchoByCharacter = False
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_locking_keys(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for locking keys."""
        presenter, _manager_instance, value_map, settings_mock = self._setup_presenter(test_context)

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "Caps_Lock"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = True
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)

        value_map["enableKeyEcho"] = True
        settings_mock.enableKeyEcho = True

        # Test locking key when locking keys are presented
        settings_mock.presentLockingKeys = True
        assert presenter.should_echo_keyboard_event(event_mock) is True

        # Test locking key when locking keys are not presented
        settings_mock.presentLockingKeys = False
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_password_text_obscuring(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test should_echo_keyboard_event with password text that should be obscured."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()
        event_mock.get_key_name.return_value = "a"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = False
        # Set all other key type checks to False so we get to password text check
        event_mock.is_navigation_key.return_value = False
        event_mock.is_action_key.return_value = False
        event_mock.is_modifier_key.return_value = False
        event_mock.is_function_key.return_value = False
        event_mock.is_diacritical_key.return_value = False
        event_mock.is_alphabetic_key.return_value = True
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)

        value_map["enableKeyEcho"] = True
        value_map["enableAlphabeticKeys"] = True
        _settings_mock.enableKeyEcho = True
        _settings_mock.enableAlphabeticKeys = True

        # Test with password text that should be obscured - should not echo
        event_mock.should_obscure.return_value = True
        test_context.patch("orca.ax_utilities.AXUtilities.is_password_text", return_value=True)
        assert presenter.should_echo_keyboard_event(event_mock) is False

        # Test with password text that should not be obscured - should echo alphabetic
        event_mock.should_obscure.return_value = False
        test_context.patch("orca.ax_utilities.AXUtilities.is_password_text", return_value=False)
        assert presenter.should_echo_keyboard_event(event_mock) is True

    def test_is_character_echoable(self, test_context: OrcaTestContext) -> None:
        """Test is_character_echoable method."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        event_mock = test_context.mocker.MagicMock()

        value_map["enableEchoByCharacter"] = False
        _settings_mock.enableEchoByCharacter = False
        assert presenter.is_character_echoable(event_mock) is False

        value_map["enableEchoByCharacter"] = True
        _settings_mock.enableEchoByCharacter = True

        event_mock.is_alt_control_or_orca_modified.return_value = True
        assert presenter.is_character_echoable(event_mock) is False

        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_printable_key.return_value = False
        assert presenter.is_character_echoable(event_mock) is False

        event_mock.is_printable_key.return_value = True
        obj_mock = test_context.mocker.MagicMock()
        event_mock.get_object.return_value = obj_mock

        test_context.patch("orca.ax_utilities.AXUtilities.is_password_text", return_value=True)
        assert presenter.is_character_echoable(event_mock) is False

        test_context.patch("orca.ax_utilities.AXUtilities.is_password_text", return_value=False)
        test_context.patch("orca.ax_utilities.AXUtilities.is_editable", return_value=True)
        test_context.patch("orca.ax_utilities.AXUtilities.is_terminal", return_value=False)
        assert presenter.is_character_echoable(event_mock) is True

        test_context.patch("orca.ax_utilities.AXUtilities.is_editable", return_value=False)
        test_context.patch("orca.ax_utilities.AXUtilities.is_terminal", return_value=True)
        assert presenter.is_character_echoable(event_mock) is True

        test_context.patch("orca.ax_utilities.AXUtilities.is_terminal", return_value=False)
        assert presenter.is_character_echoable(event_mock) is False

    def test_echo_previous_word(self, test_context: OrcaTestContext) -> None:
        """Test echo_previous_word method."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        script_mock = test_context.mocker.MagicMock()
        obj_mock = test_context.mocker.MagicMock()

        value_map["enableEchoByWord"] = False
        _settings_mock.enableEchoByWord = False
        assert presenter.echo_previous_word(script_mock, obj_mock) is False

        value_map["enableEchoByWord"] = True
        _settings_mock.enableEchoByWord = True

        test_context.patch("orca.ax_text.AXText.get_caret_offset", return_value=5)
        test_context.patch("orca.ax_text.AXText.get_character_count", return_value=10)

        test_context.patch("orca.ax_text.AXText.get_caret_offset", return_value=0)
        assert presenter.echo_previous_word(script_mock, obj_mock) is False

        test_context.patch("orca.ax_text.AXText.get_caret_offset", return_value=5)
        char_mock_1 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_1.side_effect = [("a", 4, 5), ("b", 3, 4)]
        assert presenter.echo_previous_word(script_mock, obj_mock) is False

        char_mock_2 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_2.side_effect = [(" ", 4, 5), (" ", 3, 4)]
        assert presenter.echo_previous_word(script_mock, obj_mock) is False

        char_mock_3 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_3.side_effect = [(" ", 4, 5), ("a", 3, 4)]
        test_context.patch("orca.ax_text.AXText.get_word_at_offset", return_value=("hello", 0, 5))

        script_mock.speech_generator.voice.return_value = ["voice"]

        from orca import presentation_manager

        pres_manager: Any = presentation_manager.get_manager()
        pres_manager.speak_message.reset_mock()

        result = presenter.echo_previous_word(script_mock, obj_mock)
        assert result is True
        pres_manager.speak_message.assert_called_with("hello", ["voice"], obj=obj_mock)

        char_mock_4 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_4.side_effect = [(" ", 4, 5), ("a", 3, 4)]
        test_context.patch("orca.ax_text.AXText.get_word_at_offset", return_value=("", 0, 0))
        assert presenter.echo_previous_word(script_mock, obj_mock) is False

    def test_echo_previous_sentence(self, test_context: OrcaTestContext) -> None:
        """Test echo_previous_sentence method."""
        presenter, _manager_instance, value_map, _settings_mock = self._setup_presenter(
            test_context
        )

        script_mock = test_context.mocker.MagicMock()
        obj_mock = test_context.mocker.MagicMock()

        value_map["enableEchoBySentence"] = False
        _settings_mock.enableEchoBySentence = False
        assert presenter.echo_previous_sentence(script_mock, obj_mock) is False

        value_map["enableEchoBySentence"] = True
        _settings_mock.enableEchoBySentence = True

        test_context.patch("orca.ax_text.AXText.get_caret_offset", return_value=10)

        char_mock_1 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_1.side_effect = [("a", 9, 10), ("b", 8, 9)]
        assert presenter.echo_previous_sentence(script_mock, obj_mock) is False

        char_mock_2 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_2.side_effect = [(" ", 9, 10), (".", 8, 9)]
        test_context.patch(
            "orca.ax_text.AXText.get_sentence_at_offset", return_value=("Hello world.", 0, 12)
        )

        script_mock.speech_generator.voice.return_value = ["voice"]

        from orca import presentation_manager

        pres_manager: Any = presentation_manager.get_manager()
        pres_manager.speak_message.reset_mock()

        result = presenter.echo_previous_sentence(script_mock, obj_mock)
        assert result is True
        pres_manager.speak_message.assert_called_with("Hello world.", ["voice"], obj=obj_mock)

        char_mock_3 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_3.side_effect = [(" ", 9, 10), (".", 8, 9)]
        test_context.patch("orca.ax_text.AXText.get_sentence_at_offset", return_value=("", 0, 0))
        assert presenter.echo_previous_sentence(script_mock, obj_mock) is False

    def test_commands_and_bindings(self, test_context: OrcaTestContext) -> None:
        """Test commands are registered in CommandManager."""
        presenter, _manager_instance, _value_map, _settings_mock = self._setup_presenter(
            test_context
        )
        from orca import command_manager

        # Commands are registered during setup()
        presenter.set_up_commands()

        # Verify commands are registered in CommandManager
        cmd_manager = command_manager.get_manager()
        assert cmd_manager.get_keyboard_command("cycleKeyEchoHandler") is not None
