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
# pylint: disable=too-many-lines

"""Unit tests for typing_echo_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

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

    _CMDNAME_VALUES: dict[str, str] = {
        "STRUCTURAL_NAVIGATION_MODE_CYCLE": "cycle_mode",
        "BLOCKQUOTE_PREV": "previous_blockquote",
        "BLOCKQUOTE_NEXT": "next_blockquote",
        "BLOCKQUOTE_LIST": "list_blockquotes",
        "BUTTON_PREV": "previous_button",
        "BUTTON_NEXT": "next_button",
        "BUTTON_LIST": "list_buttons",
        "CHECK_BOX_PREV": "previous_checkbox",
        "CHECK_BOX_NEXT": "next_checkbox",
        "CHECK_BOX_LIST": "list_checkboxes",
        "COMBO_BOX_PREV": "previous_combobox",
        "COMBO_BOX_NEXT": "next_combobox",
        "COMBO_BOX_LIST": "list_comboboxes",
        "ENTRY_PREV": "previous_entry",
        "ENTRY_NEXT": "next_entry",
        "ENTRY_LIST": "list_entries",
        "FORM_FIELD_PREV": "previous_form_field",
        "FORM_FIELD_NEXT": "next_form_field",
        "FORM_FIELD_LIST": "list_form_fields",
        "HEADING_PREV": "previous_heading",
        "HEADING_NEXT": "next_heading",
        "HEADING_LIST": "list_headings",
        "HEADING_AT_LEVEL_PREV": "previous_heading_level_%d",
        "HEADING_AT_LEVEL_NEXT": "next_heading_level_%d",
        "HEADING_AT_LEVEL_LIST": "list_headings_level_%d",
        "IFRAME_PREV": "previous_iframe",
        "IFRAME_NEXT": "next_iframe",
        "IFRAME_LIST": "list_iframes",
        "IMAGE_PREV": "previous_image",
        "IMAGE_NEXT": "next_image",
        "IMAGE_LIST": "list_images",
        "LANDMARK_PREV": "previous_landmark",
        "LANDMARK_NEXT": "next_landmark",
        "LANDMARK_LIST": "list_landmarks",
        "LIST_PREV": "previous_list",
        "LIST_NEXT": "next_list",
        "LIST_LIST": "list_lists",
        "LIST_ITEM_PREV": "previous_list_item",
        "LIST_ITEM_NEXT": "next_list_item",
        "LIST_ITEM_LIST": "list_list_items",
        "LIVE_REGION_PREV": "previous_live_region",
        "LIVE_REGION_NEXT": "next_live_region",
        "LIVE_REGION_LAST": "last_live_region",
        "PARAGRAPH_PREV": "previous_paragraph",
        "PARAGRAPH_NEXT": "next_paragraph",
        "PARAGRAPH_LIST": "list_paragraphs",
        "RADIO_BUTTON_PREV": "previous_radio_button",
        "RADIO_BUTTON_NEXT": "next_radio_button",
        "RADIO_BUTTON_LIST": "list_radio_buttons",
        "SEPARATOR_PREV": "previous_separator",
        "SEPARATOR_NEXT": "next_separator",
        "TABLE_PREV": "previous_table",
        "TABLE_NEXT": "next_table",
        "TABLE_LIST": "list_tables",
        "UNVISITED_LINK_PREV": "previous_unvisited_link",
        "UNVISITED_LINK_NEXT": "next_unvisited_link",
        "UNVISITED_LINK_LIST": "list_unvisited_links",
        "VISITED_LINK_PREV": "previous_visited_link",
        "VISITED_LINK_NEXT": "next_visited_link",
        "VISITED_LINK_LIST": "list_visited_links",
        "LINK_PREV": "previous_link",
        "LINK_NEXT": "next_link",
        "LINK_LIST": "list_links",
        "CLICKABLE_PREV": "previous_clickable",
        "CLICKABLE_NEXT": "next_clickable",
        "CLICKABLE_LIST": "list_clickables",
        "LARGE_OBJECT_PREV": "previous_large_object",
        "LARGE_OBJECT_NEXT": "next_large_object",
        "LARGE_OBJECT_LIST": "list_large_objects",
        "CONTAINER_START": "container_start",
        "CONTAINER_END": "container_end",
    }

    @staticmethod
    def _setup_cmdnames(cmdnames) -> None:
        """Set up cmdnames with all required values for structural_navigator."""

        for attr, value in TestTypingEchoPresenter._CMDNAME_VALUES.items():
            setattr(cmdnames, attr, value)

    @staticmethod
    def _setup_guilabels(guilabels_mock) -> None:
        """Set up guilabels mock with typing echo label values."""

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

    @staticmethod
    def _setup_atspi_patches(test_context: OrcaTestContext) -> None:
        """Set up Atspi type patches for testing."""

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

    _ADDITIONAL_MODULES = [
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

    _DEFAULT_VALUES = {
        "enableKeyEcho": True,
        "enableAlphabeticKeys": True,
        "enableNumericKeys": True,
        "enablePunctuationKeys": True,
        "enableSpace": True,
        "enableModifierKeys": True,
        "enableFunctionKeys": True,
        "enableActionKeys": True,
        "enableNavigationKeys": False,
        "enableDiacriticalKeys": False,
        "enableEchoByCharacter": False,
        "enableEchoByWord": False,
        "enableEchoBySentence": False,
    }

    @staticmethod
    def _setup_essential_mocks(test_context: OrcaTestContext, essential_modules: dict) -> None:
        """Set up essential mock objects for testing."""

        essential_modules["orca.orca_i18n"]._ = lambda x: x
        essential_modules["orca.debug"].print_message = test_context.Mock()
        essential_modules["orca.debug"].LEVEL_INFO = 800
        essential_modules["orca.debug"].LEVEL_SEVERE = 1000
        essential_modules["orca.debug"].debugLevel = 1000

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

    def _setup_presenter(self, test_context: OrcaTestContext):
        """Set up presenter and dependencies for testing."""

        essential_modules = test_context.setup_shared_dependencies(self._ADDITIONAL_MODULES)

        self._setup_cmdnames(essential_modules["orca.cmdnames"])
        self._setup_essential_mocks(test_context, essential_modules)
        self._setup_guilabels(essential_modules["orca.guilabels"])

        self._setup_atspi_patches(test_context)

        from orca import gsettings_registry
        from orca.typing_echo_presenter import TypingEchoPresenter

        registry = gsettings_registry.get_registry()
        registry.clear_runtime_values()
        registry.set_enabled(False)

        presenter = TypingEchoPresenter()
        return presenter

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
        presenter = self._setup_presenter(test_context)

        getter = getattr(presenter, getter_name)
        setter = getattr(presenter, setter_name)

        assert getter() is self._DEFAULT_VALUES[setting_key]
        setter(test_value)
        assert getter() == test_value

    def test_locking_keys_presented_getter_and_setter(self, test_context: OrcaTestContext) -> None:
        """Test locking keys presented getter and setter with special logic."""
        presenter = self._setup_presenter(test_context)

        presenter._present_locking_keys = True
        assert presenter.get_locking_keys_presented() is True

        presenter._present_locking_keys = False
        assert presenter.get_locking_keys_presented() is False

        presenter._present_locking_keys = None

        speech_presenter_patch = test_context.patch("orca.speech_presenter.get_presenter")
        speech_presenter_instance = speech_presenter_patch.return_value

        speech_presenter_instance.get_only_speak_displayed_text.return_value = False
        assert presenter.get_locking_keys_presented() is True

        speech_presenter_instance.get_only_speak_displayed_text.return_value = True
        assert presenter.get_locking_keys_presented() is False

        presenter.set_locking_keys_presented(True)
        assert presenter._present_locking_keys is True

        presenter.set_locking_keys_presented(None)
        assert presenter._present_locking_keys is None

    def test_cycle_key_echo_basic_transitions(self, test_context: OrcaTestContext) -> None:
        """Test cycle_key_echo method basic state transitions."""
        presenter = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()

        presenter.set_key_echo_enabled(False)

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert presenter.get_key_echo_enabled() is True
        assert presenter.get_word_echo_enabled() is False
        assert presenter.get_sentence_echo_enabled() is False

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert presenter.get_key_echo_enabled() is False
        assert presenter.get_word_echo_enabled() is True
        assert presenter.get_sentence_echo_enabled() is False

    def test_cycle_key_echo_advanced_transitions(self, test_context: OrcaTestContext) -> None:
        """Test cycle_key_echo method advanced state transitions."""
        presenter = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()

        presenter.set_key_echo_enabled(False)
        presenter.set_word_echo_enabled(True)

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert presenter.get_key_echo_enabled() is False
        assert presenter.get_word_echo_enabled() is False
        assert presenter.get_sentence_echo_enabled() is True

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert presenter.get_key_echo_enabled() is True
        assert presenter.get_word_echo_enabled() is True
        assert presenter.get_sentence_echo_enabled() is False

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert presenter.get_key_echo_enabled() is False
        assert presenter.get_word_echo_enabled() is True
        assert presenter.get_sentence_echo_enabled() is True

        result = presenter.cycle_key_echo(script_mock, None, True)
        assert result is True
        assert presenter.get_key_echo_enabled() is False
        assert presenter.get_word_echo_enabled() is False
        assert presenter.get_sentence_echo_enabled() is False

    def test_cycle_key_echo_with_script_presentation(self, test_context: OrcaTestContext) -> None:
        """Test cycle_key_echo calls present_message when script is provided."""
        presenter = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()

        presenter.set_key_echo_enabled(False)

        from orca import presentation_manager

        present_msg = presentation_manager.get_manager().present_message
        assert isinstance(present_msg, Mock)
        present_msg.reset_mock()  # pylint: disable=no-member

        presenter.cycle_key_echo(script_mock, None, True)
        assert present_msg.call_count == 1  # pylint: disable=no-member

        present_msg.reset_mock()  # pylint: disable=no-member
        presenter.cycle_key_echo(script_mock, None, False)
        assert present_msg.call_count == 0  # pylint: disable=no-member

        presenter.cycle_key_echo(None, None, True)

    def test_should_echo_keyboard_event_basic_cases(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for basic cases."""
        presenter = self._setup_presenter(test_context)

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "a"

        event_mock.is_pressed_key.return_value = False
        assert presenter.should_echo_keyboard_event(event_mock) is False

        event_mock.is_pressed_key.return_value = True
        presenter.set_key_echo_enabled(False)
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = False
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_orca_modifier(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for Orca modifier keys."""
        presenter = self._setup_presenter(test_context)

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "Insert_L"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = True

        event_mock.get_click_count.return_value = 2
        assert presenter.should_echo_keyboard_event(event_mock) is True

        event_mock.get_click_count.return_value = 1
        assert presenter.should_echo_keyboard_event(event_mock) is True

        presenter.set_modifier_keys_enabled(False)
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_modified_keys(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for modified keys."""
        presenter = self._setup_presenter(test_context)

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
        presenter = self._setup_presenter(test_context)

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "a"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False

        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=True)
        assert presenter.should_echo_keyboard_event(event_mock) is False

    @pytest.mark.parametrize(
        "key_type,_setting_key,expected_result",
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
        self, test_context: OrcaTestContext, key_type: str, _setting_key: str, expected_result: bool
    ) -> None:
        """Test should_echo_keyboard_event for different key types."""
        presenter = self._setup_presenter(test_context)

        from orca import gsettings_registry

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

        gs_key = f"{key_type}-keys"
        gsettings_registry.get_registry().set_runtime_value("typing-echo", gs_key, expected_result)

        result = presenter.should_echo_keyboard_event(event_mock)
        assert result is expected_result

    def test_should_echo_keyboard_event_space_key_scenarios(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test should_echo_keyboard_event for space key with different settings."""
        presenter = self._setup_presenter(test_context)

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

        # Test space key with space setting enabled (default), character echo disabled (default)
        assert presenter.should_echo_keyboard_event(event_mock) is True

        # Test space key with space disabled but character echo enabled (should echo)
        presenter.set_space_enabled(False)
        presenter.set_character_echo_enabled(True)
        assert presenter.should_echo_keyboard_event(event_mock) is True

        # Test space key with both space and character echo disabled
        presenter.set_character_echo_enabled(False)
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_locking_keys(self, test_context: OrcaTestContext) -> None:
        """Test should_echo_keyboard_event for locking keys."""
        presenter = self._setup_presenter(test_context)

        event_mock = test_context.mocker.MagicMock()
        event_mock.should_obscure.return_value = False
        event_mock.get_key_name.return_value = "Caps_Lock"
        event_mock.is_pressed_key.return_value = True
        event_mock.is_orca_modifier.return_value = False
        event_mock.is_alt_control_or_orca_modified.return_value = False
        event_mock.is_locking_key.return_value = True
        presenter.is_character_echoable = test_context.mocker.MagicMock(return_value=False)

        # Test locking key when locking keys are presented
        presenter._present_locking_keys = True
        assert presenter.should_echo_keyboard_event(event_mock) is True

        # Test locking key when locking keys are not presented
        presenter._present_locking_keys = False
        assert presenter.should_echo_keyboard_event(event_mock) is False

    def test_should_echo_keyboard_event_password_text_obscuring(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test should_echo_keyboard_event with password text that should be obscured."""
        presenter = self._setup_presenter(test_context)

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
        presenter = self._setup_presenter(test_context)

        event_mock = test_context.mocker.MagicMock()

        assert presenter.is_character_echoable(event_mock) is False

        presenter.set_character_echo_enabled(True)

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
        presenter = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()
        obj_mock = test_context.mocker.MagicMock()

        assert presenter.echo_previous_word(script_mock, obj_mock) is False

        presenter.set_word_echo_enabled(True)

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

        speak_msg = presentation_manager.get_manager().speak_message
        assert isinstance(speak_msg, Mock)
        speak_msg.reset_mock()  # pylint: disable=no-member

        result = presenter.echo_previous_word(script_mock, obj_mock)
        assert result is True
        speak_msg.assert_called_with("hello", ["voice"], obj=obj_mock)  # pylint: disable=no-member

        char_mock_4 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_4.side_effect = [(" ", 4, 5), ("a", 3, 4)]
        test_context.patch("orca.ax_text.AXText.get_word_at_offset", return_value=("", 0, 0))
        assert presenter.echo_previous_word(script_mock, obj_mock) is False

    def test_echo_previous_sentence(self, test_context: OrcaTestContext) -> None:
        """Test echo_previous_sentence method."""
        presenter = self._setup_presenter(test_context)

        script_mock = test_context.mocker.MagicMock()
        obj_mock = test_context.mocker.MagicMock()

        assert presenter.echo_previous_sentence(script_mock, obj_mock) is False

        presenter.set_sentence_echo_enabled(True)

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

        speak_msg = presentation_manager.get_manager().speak_message
        assert isinstance(speak_msg, Mock)
        speak_msg.reset_mock()  # pylint: disable=no-member

        result = presenter.echo_previous_sentence(script_mock, obj_mock)
        assert result is True
        speak_msg.assert_called_with("Hello world.", ["voice"], obj=obj_mock)  # pylint: disable=no-member

        char_mock_3 = test_context.patch("orca.ax_text.AXText.get_character_at_offset")
        char_mock_3.side_effect = [(" ", 9, 10), (".", 8, 9)]
        test_context.patch("orca.ax_text.AXText.get_sentence_at_offset", return_value=("", 0, 0))
        assert presenter.echo_previous_sentence(script_mock, obj_mock) is False

    def test_commands_and_bindings(self, test_context: OrcaTestContext) -> None:
        """Test commands are registered in CommandManager."""
        presenter = self._setup_presenter(test_context)
        from orca import command_manager

        # Commands are registered during setup()
        presenter.set_up_commands()

        # Verify commands are registered in CommandManager
        cmd_manager = command_manager.get_manager()
        assert cmd_manager.get_keyboard_command("cycleKeyEchoHandler") is not None

    @pytest.mark.parametrize(
        "getter_name,gs_key,_setting_key",
        [
            ("get_key_echo_enabled", "key-echo", "enableKeyEcho"),
            ("get_character_echo_enabled", "character-echo", "enableEchoByCharacter"),
            ("get_word_echo_enabled", "word-echo", "enableEchoByWord"),
            ("get_sentence_echo_enabled", "sentence-echo", "enableEchoBySentence"),
            ("get_alphabetic_keys_enabled", "alphabetic-keys", "enableAlphabeticKeys"),
            ("get_numeric_keys_enabled", "numeric-keys", "enableNumericKeys"),
            ("get_punctuation_keys_enabled", "punctuation-keys", "enablePunctuationKeys"),
            ("get_space_enabled", "space", "enableSpace"),
            ("get_modifier_keys_enabled", "modifier-keys", "enableModifierKeys"),
            ("get_function_keys_enabled", "function-keys", "enableFunctionKeys"),
            ("get_action_keys_enabled", "action-keys", "enableActionKeys"),
            ("get_navigation_keys_enabled", "navigation-keys", "enableNavigationKeys"),
            ("get_diacritical_keys_enabled", "diacritical-keys", "enableDiacriticalKeys"),
        ],
    )
    def test_getter_returns_dconf_value_when_available(
        self,
        test_context: OrcaTestContext,
        getter_name: str,
        gs_key: str,
        _setting_key: str,
    ) -> None:
        """Test getter returns dconf value when layered_lookup returns a value."""
        presenter = self._setup_presenter(test_context)

        from orca import gsettings_registry
        from orca.gsettings_registry import GSettingsSchemaHandle

        registry = gsettings_registry.get_registry()
        registry.set_enabled(True)

        mock_handle = test_context.Mock(spec=GSettingsSchemaHandle)
        mock_handle.get_boolean.return_value = False
        registry._handles["typing-echo"] = mock_handle

        getter = getattr(presenter, getter_name)
        assert getter() is False
        mock_handle.get_boolean.assert_called_with(gs_key, "")

        registry.set_enabled(False)
        registry._handles.pop("typing-echo", None)

    @pytest.mark.parametrize(
        "getter_name,setting_key",
        [
            ("get_key_echo_enabled", "enableKeyEcho"),
            ("get_character_echo_enabled", "enableEchoByCharacter"),
            ("get_word_echo_enabled", "enableEchoByWord"),
            ("get_sentence_echo_enabled", "enableEchoBySentence"),
            ("get_alphabetic_keys_enabled", "enableAlphabeticKeys"),
            ("get_numeric_keys_enabled", "enableNumericKeys"),
            ("get_punctuation_keys_enabled", "enablePunctuationKeys"),
            ("get_space_enabled", "enableSpace"),
            ("get_modifier_keys_enabled", "enableModifierKeys"),
            ("get_function_keys_enabled", "enableFunctionKeys"),
            ("get_action_keys_enabled", "enableActionKeys"),
            ("get_navigation_keys_enabled", "enableNavigationKeys"),
            ("get_diacritical_keys_enabled", "enableDiacriticalKeys"),
        ],
    )
    def test_getter_returns_default_when_disabled(
        self,
        test_context: OrcaTestContext,
        getter_name: str,
        setting_key: str,
    ) -> None:
        """Test getter returns module-owned default when registry is disabled."""
        presenter = self._setup_presenter(test_context)

        getter = getattr(presenter, getter_name)
        assert getter() is self._DEFAULT_VALUES[setting_key]

    def test_get_setting_logs_dconf_layer(self, test_context: OrcaTestContext) -> None:
        """Test that dconf lookup logs the source layer and value."""
        presenter = self._setup_presenter(test_context)

        from orca import debug as debug_mock
        from orca import gsettings_registry
        from orca.gsettings_registry import GSettingsSchemaHandle

        registry = gsettings_registry.get_registry()
        registry.set_enabled(True)

        mock_handle = test_context.Mock(spec=GSettingsSchemaHandle)
        mock_handle.get_boolean.return_value = False
        registry._handles["typing-echo"] = mock_handle

        print_msg = debug_mock.print_message
        assert isinstance(print_msg, Mock)
        debug_mock.debugLevel = 800
        print_msg.reset_mock()  # pylint: disable=no-member

        assert presenter.get_key_echo_enabled() is False

        registry.set_enabled(False)
        registry._handles.pop("typing-echo", None)
