# Unit tests for say_all_presenter.py methods.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Unit tests for say_all_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext

@pytest.mark.unit
class TestSayAllPresenter:
    """Test SayAllPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Any]:
        """Set up mocks for say_all_presenter dependencies."""

        additional_modules = [
            "orca.ax_event_synthesizer",
            "orca.structural_navigator",
            "orca.input_event",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.guilabels",
            "orca.ax_object",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.messages",
            "orca.input_event_manager",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
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

        return essential_modules

    def test_say_all_should_skip_content(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter._say_all_should_skip_content empty content handling."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        content = (mock_obj, 0, 0, "test text")
        should_skip, reason = presenter._say_all_should_skip_content(content, [])
        assert should_skip is True
        assert reason == "start_offset equals end_offset"

    def test_parse_utterances(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter._parse_utterances with various input formats."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speech  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()

        mock_acss = test_context.Mock(spec=speech.ACSS)

        elements, voices = presenter._parse_utterances([])
        assert len(elements) == 0
        assert len(voices) == 0

        elements, voices = presenter._parse_utterances(["Hello world"])
        assert len(elements) == 1
        assert elements[0] == "Hello world"

        elements, voices = presenter._parse_utterances([["Hello"], ["world"]])
        assert len(elements) == 2
        assert elements[0] == "Hello"
        assert elements[1] == "world"

        elements, voices = presenter._parse_utterances(["Hello", mock_acss])
        assert len(elements) == 1
        assert len(voices) == 1
        assert elements[0] == "Hello"
        assert voices[0] == mock_acss

    def test_get_presenter_singleton(self, test_context: OrcaTestContext) -> None:
        """Test that get_presenter returns a singleton instance."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import get_presenter  # pylint: disable=import-outside-toplevel

        presenter1 = get_presenter()
        presenter2 = get_presenter()
        assert presenter1 is presenter2
        assert presenter1 is not None

    def test_say_all_presenter_initialization(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter initialization sets up required attributes."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        assert presenter is not None
        assert hasattr(presenter, "get_handlers")
        assert hasattr(presenter, "get_bindings")

    @pytest.mark.parametrize(
        "refresh,expected_setup_calls",
        [
            pytest.param(True, 1, id="refresh_true_calls_setup"),
            pytest.param(False, 0, id="refresh_false_uses_cache"),
        ],
    )
    def test_get_handlers(
        self,
        test_context: OrcaTestContext,
        refresh: bool,
        expected_setup_calls: int,
    ) -> None:
        """Test SayAllPresenter.get_handlers with refresh parameter."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        original_setup = presenter._setup_handlers
        setup_calls = [0]

        def mock_setup():
            setup_calls[0] += 1
            return original_setup()

        test_context.patch_object(presenter, "_setup_handlers", side_effect=mock_setup)
        handlers = presenter.get_handlers(refresh=refresh)
        assert isinstance(handlers, dict)
        assert setup_calls[0] == expected_setup_calls

    @pytest.mark.parametrize(
        "is_desktop",
        [
            pytest.param(True, id="desktop_bindings"),
            pytest.param(False, id="laptop_bindings"),
        ],
    )
    def test_get_bindings(
        self,
        test_context: OrcaTestContext,
        is_desktop: bool,
    ) -> None:
        """Test SayAllPresenter.get_bindings with different keyboard layouts."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_bindings = test_context.Mock()
        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBindings = test_context.Mock(return_value=mock_bindings)

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        settings_manager_mock.get_manager.return_value = manager_instance
        manager_instance.is_desktop_keyboard_layout.return_value = is_desktop

        result = presenter.get_bindings(refresh=True)
        assert result is not None
        keybindings_mock.KeyBindings.assert_called()

    def test_say_all_no_object_scenario(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter.say_all with no focus object scenario."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_locus_of_focus.return_value = None

        messages_mock = essential_modules["orca.messages"]
        messages_mock.LOCATION_NOT_FOUND_FULL = "Location not found"

        result = presenter.say_all(mock_script, obj=None)
        assert result is True

        mock_script.interrupt_presentation.assert_called_once()
        mock_script.present_message.assert_called_once_with("Location not found")

    @pytest.mark.parametrize(
        "direction,enabled,contents_available,obj_valid,expected_result",
        [
            pytest.param("rewind", False, True, True, False, id="rewind_disabled"),
            pytest.param("rewind", True, False, True, True, id="rewind_no_contents_valid_context"),
            pytest.param(
                "rewind", True, False, False, False, id="rewind_no_contents_invalid_context_obj"
            ),
            pytest.param("rewind", True, True, True, True, id="rewind_success"),
            pytest.param("fast_forward", False, True, True, False, id="fast_forward_disabled"),
            pytest.param(
                "fast_forward", True, False, True, True, id="fast_forward_no_contents_valid_context"
            ),
            pytest.param(
                "fast_forward",
                True,
                False,
                False,
                False,
                id="fast_forward_no_contents_invalid_context_obj",
            ),
            pytest.param("fast_forward", True, True, True, True, id="fast_forward_success"),
        ],
    )
    def test_navigation_controls(
        self,
        test_context: OrcaTestContext,
        direction: str,
        enabled: bool,
        contents_available: bool,
        obj_valid: bool,
        expected_result: bool,
    ) -> None:
        """Test _rewind and _fast_forward navigation controls with various conditions."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        settings_mock = essential_modules["orca.settings"]
        settings_mock.rewindAndFastForwardInSayAll = enabled

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        mock_context.obj = "context_obj" if obj_valid else None

        if direction == "rewind":
            mock_context.start_offset = 15
        else:
            mock_context.end_offset = 25

        if contents_available:
            if direction == "rewind":
                presenter._contents = [("content_obj", 5, 10, "text")]
            else:
                presenter._contents = [("first_obj", 0, 5, "first"), ("last_obj", 20, 30, "last")]
        else:
            presenter._contents = []

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = focus_instance

        mock_script.utilities.set_caret_context = test_context.Mock()

        if direction == "rewind":
            mock_script.utilities.previous_context.return_value = ("prev_obj", 8)
        else:
            mock_script.utilities.next_context.return_value = ("next_obj", 35)

        presenter.say_all = test_context.Mock(return_value=True)
        navigation_method = getattr(presenter, f"_{direction}")
        result = navigation_method(mock_context)
        assert result == expected_result

        if expected_result:
            focus_instance.set_locus_of_focus.assert_called()
            mock_script.utilities.set_caret_context.assert_called()
            if direction == "rewind":
                mock_script.utilities.previous_context.assert_called()
            else:
                mock_script.utilities.next_context.assert_called()
            presenter.say_all.assert_called_once()

    @pytest.mark.parametrize(
        "command_method",
        [
            pytest.param("rewind", id="rewind_command"),
            pytest.param("fast_forward", id="fast_forward_command"),
        ],
    )
    def test_dbus_navigation_commands(
        self,
        test_context: OrcaTestContext,
        command_method: str,
    ) -> None:
        """Test D-Bus navigation commands delegate to private methods."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()

        private_method_name = f"_{command_method}"
        test_context.patch_object(presenter, private_method_name, return_value=True)

        command = getattr(presenter, command_method)
        result = command(mock_script, mock_event, notify_user=True)

        assert result is True
        debug_mock.print_tokens.assert_called_once()
        private_method = getattr(presenter, private_method_name)
        private_method.assert_called_once_with(None, True)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "rewind_setting_disabled_no_override",
                "direction": "rewind",
                "override_setting": False,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": False,
            },
            {
                "id": "rewind_setting_disabled_with_override",
                "direction": "rewind",
                "override_setting": True,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "rewind_setting_enabled_no_override",
                "direction": "rewind",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "rewind_setting_enabled_with_override",
                "direction": "rewind",
                "override_setting": True,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "rewind_with_provided_context",
                "direction": "rewind",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": True,
                "expected_result": True,
            },
            {
                "id": "fast_forward_setting_disabled_no_override",
                "direction": "fast_forward",
                "override_setting": False,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": False,
            },
            {
                "id": "fast_forward_setting_disabled_with_override",
                "direction": "fast_forward",
                "override_setting": True,
                "setting_enabled": False,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "fast_forward_setting_enabled_no_override",
                "direction": "fast_forward",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "fast_forward_setting_enabled_with_override",
                "direction": "fast_forward",
                "override_setting": True,
                "setting_enabled": True,
                "context_provided": False,
                "expected_result": True,
            },
            {
                "id": "fast_forward_with_provided_context",
                "direction": "fast_forward",
                "override_setting": False,
                "setting_enabled": True,
                "context_provided": True,
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_navigation_methods_with_parameters(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test _rewind and _fast_forward methods with override_setting parameter."""

        direction = case["direction"]
        override_setting = case["override_setting"]
        setting_enabled = case["setting_enabled"]
        context_provided = case["context_provided"]
        expected_result = case["expected_result"]

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        settings_mock = essential_modules["orca.settings"]
        settings_mock.rewindAndFastForwardInSayAll = setting_enabled

        mock_context = (test_context.Mock(spec=speechserver.SayAllContext)
                        if context_provided else None)
        if context_provided and mock_context is not None:
            mock_context.obj = "provided_obj"
            if direction == "rewind":
                mock_context.start_offset = 10
            else:
                mock_context.end_offset = 20

        current_context = test_context.Mock(spec=speechserver.SayAllContext)
        current_context.obj = "current_obj"
        if direction == "rewind":
            current_context.start_offset = 5
        else:
            current_context.end_offset = 15
        presenter._current_context = current_context

        if direction == "rewind":
            presenter._contents = [("content_obj", 0, 10, "text")]
        else:
            presenter._contents = [("first_obj", 0, 5, "first"),
                                   ("last_obj", 10, 20, "last")]

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = focus_instance

        mock_script.utilities.set_caret_context = test_context.Mock()
        if direction == "rewind":
            mock_script.utilities.previous_context.return_value = ("prev_obj", 3)
        else:
            mock_script.utilities.next_context.return_value = ("next_obj", 25)

        presenter.say_all = test_context.Mock(return_value=True)

        navigation_method = getattr(presenter, f"_{direction}")
        result = navigation_method(mock_context, override_setting)

        assert result == expected_result

        if expected_result:
            focus_instance.set_locus_of_focus.assert_called()
            mock_script.utilities.set_caret_context.assert_called()
            presenter.say_all.assert_called_once()

    def test_say_all_initialization_clears_state(self, test_context: OrcaTestContext) -> None:
        """Test say_all method clears contexts, contents, and current_context at start."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()

        presenter._contexts = [test_context.Mock(spec=speechserver.SayAllContext)]
        presenter._contents = [("old_obj", 0, 5, "old")]
        presenter._current_context = test_context.Mock(spec=speechserver.SayAllContext)

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_locus_of_focus.return_value = "focus_obj"

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()

        from orca import speech  # pylint: disable=import-outside-toplevel
        test_context.patch_object(speech, "say_all", return_value=None)

        mock_script.utilities.get_caret_context.return_value = ("obj", 10)

        result = presenter.say_all(mock_script, None)
        assert result is True

        assert not presenter._contexts
        assert not presenter._contents
        assert presenter._current_context is None

    def test_progress_callback_sets_current_context(self, test_context: OrcaTestContext) -> None:
        """Test that _progress_callback sets the current context."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        assert presenter._current_context is None

        presenter._current_context = mock_context
        assert presenter._current_context is mock_context

    def test_say_all_is_running_initialized_to_false(self, test_context: OrcaTestContext) -> None:
        """Test that _say_all_is_running is initialized to False."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        assert presenter._say_all_is_running is False

    def test_say_all_clears_say_all_is_running(self, test_context: OrcaTestContext) -> None:
        """Test that say_all resets _say_all_is_running to False."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()

        presenter._say_all_is_running = True

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.get_locus_of_focus.return_value = None

        messages_mock = essential_modules["orca.messages"]
        messages_mock.LOCATION_NOT_FOUND_FULL = "Location not found"

        presenter.say_all(mock_script)
        assert presenter._say_all_is_running is False

    def test_progress_callback_sets_say_all_is_running_true(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that _progress_callback sets _say_all_is_running to True."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel
        from orca.ax_text import AXText  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        mock_context.obj = test_context.Mock()
        mock_context.current_offset = 5
        mock_context.current_end_offset = 10

        test_context.patch_object(AXText, "character_at_offset_is_eoc", return_value=False)

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = focus_instance
        focus_manager_mock.SAY_ALL = "say-all"

        assert presenter._say_all_is_running is False

        presenter._progress_callback(mock_context, speechserver.SayAllContext.PROGRESS)

        assert presenter._say_all_is_running is True

    def test_progress_callback_uses_say_all_mode_when_running(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that _progress_callback uses SAY_ALL mode when _say_all_is_running is True."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel
        from orca.ax_text import AXText  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        mock_context.obj = test_context.Mock()
        mock_context.current_offset = 5
        mock_context.current_end_offset = 10

        test_context.patch_object(AXText, "character_at_offset_is_eoc", return_value=False)

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = focus_instance
        focus_manager_mock.SAY_ALL = "say-all"

        presenter._progress_callback(mock_context, speechserver.SayAllContext.PROGRESS)

        focus_instance.emit_region_changed.assert_called_once_with(
            mock_context.obj, mock_context.current_offset, mock_context.current_end_offset,
            "say-all"
        )

    def test_progress_callback_uses_focus_tracking_mode_when_interrupted(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that _progress_callback uses FOCUS_TRACKING mode when interrupted by keyboard."""

        self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel
        from orca.ax_text import AXText  # pylint: disable=import-outside-toplevel
        from orca import input_event_manager  # pylint: disable=import-outside-toplevel
        from orca import focus_manager as fm  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        presenter._script = mock_script

        mock_context = test_context.Mock(spec=speechserver.SayAllContext)
        mock_context.obj = test_context.Mock()
        mock_context.current_offset = 5
        mock_context.current_end_offset = 10

        test_context.patch_object(AXText, "character_at_offset_is_eoc", return_value=False)
        test_context.patch_object(AXText, "set_caret_offset", return_value=True)

        focus_instance = test_context.Mock()
        test_context.patch_object(fm, "get_manager", return_value=focus_instance)

        iem_instance = test_context.Mock()
        iem_instance.last_event_was_keyboard.return_value = True
        iem_instance.last_event_was_down.return_value = False
        iem_instance.last_event_was_up.return_value = False
        test_context.patch_object(input_event_manager, "get_manager", return_value=iem_instance)

        from orca import settings as orca_settings
        test_context.patch_object(orca_settings, "sayAllStyle", new=0)
        test_context.patch_object(orca_settings, "structNavInSayAll", new=False)

        presenter._progress_callback(mock_context, speechserver.SayAllContext.INTERRUPTED)

        assert presenter._say_all_is_running is False
        focus_instance.emit_region_changed.assert_called_once_with(
            mock_context.obj, mock_context.current_offset, None, fm.FOCUS_TRACKING
        )

    @pytest.mark.parametrize(
        "end_offset, expected_next_context_offset",
        [
            pytest.param(16, 15, id="normal_offset_passes_end_minus_one"),
            pytest.param(1, 0, id="small_offset_passes_end_minus_one"),
            pytest.param(0, 0, id="zero_offset_passes_zero_not_negative"),
            pytest.param(100, 99, id="large_offset_passes_end_minus_one"),
        ],
    )
    def test_say_all_iter_next_context_uses_end_offset_minus_one(
        self,
        test_context: OrcaTestContext,
        end_offset: int,
        expected_next_context_offset: int,
    ) -> None:
        """Test that _say_all_iter passes end_offset - 1 to next_context.

        The end offset from sentence contents is exclusive (position end is NOT
        part of the content). find_next_caret_in_order looks at offset + 1, so
        passing end directly would skip position end. We must pass end - 1 so
        that find_next_caret_in_order looks at position end, which is where
        embedded object characters (FFFC) representing child elements may be.
        """

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import settings  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        # Set up the presenter's script
        presenter._script = mock_script

        # Set up settings for sentence-by-sentence say all
        test_context.patch_object(settings, "sayAllStyle", new=settings.SAYALL_STYLE_SENTENCE)

        # Mock utilities - return contents once, then return empty to exit loop
        call_count = [0]
        def mock_get_sentence_contents(obj, offset):
            call_count[0] += 1
            if call_count[0] == 1:
                return [(mock_obj, 0, end_offset, "Test sentence.")]
            return []

        mock_script.utilities.get_sentence_contents_at_offset.side_effect = mock_get_sentence_contents
        mock_script.utilities.filter_contents_for_presentation.side_effect = lambda x: x

        # next_context returns None to end the loop
        mock_script.utilities.next_context.return_value = (None, -1)

        # Mock speech generator to return something so the content is processed
        mock_script.speech_generator.generate_contents.return_value = [["Test"], []]

        # Mock AXUtilities
        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.is_text.return_value = False
        ax_utilities_mock.is_terminal.return_value = False

        # Mock _say_all_should_skip_content to avoid dependency issues
        test_context.patch_object(presenter, "_say_all_should_skip_content",
                                  return_value=(False, ""))

        # Mock debug
        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.print_message = test_context.Mock()

        # Mock focus_manager for set_locus_of_focus
        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance

        # Mock event_synthesizer
        essential_modules["orca.ax_event_synthesizer"].get_synthesizer.return_value.scroll_into_view = test_context.Mock()

        # Mock utilities.set_caret_offset
        mock_script.utilities.set_caret_offset = test_context.Mock()

        # Consume the generator to trigger next_context call
        generator = presenter._say_all_iter(mock_obj, 0)
        for _ in generator:
            pass

        # Verify next_context was called with end_offset - 1 (or 0 if that would be negative)
        mock_script.utilities.next_context.assert_called_once()
        call_args = mock_script.utilities.next_context.call_args
        # next_context is called with positional args: (last_obj, offset, restrict_to=...)
        actual_offset = call_args[0][1]
        assert actual_offset == expected_next_context_offset, (
            f"Expected next_context to be called with offset {expected_next_context_offset}, "
            f"but was called with {actual_offset}"
        )

    def test_stop_clears_all_state(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter.stop clears contexts, contents, current_context and running flag."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel
        from orca import speechserver  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        presenter._contexts = [test_context.Mock(spec=speechserver.SayAllContext)]
        presenter._contents = [("obj", 0, 5, "text")]
        presenter._current_context = test_context.Mock(spec=speechserver.SayAllContext)
        presenter._say_all_is_running = True

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance

        presenter.stop()

        assert presenter._contexts == []
        assert presenter._contents == []
        assert presenter._current_context is None
        assert presenter._say_all_is_running is False
        manager_instance.reset_active_mode.assert_called_once_with(
            "SAY ALL PRESENTER: Stopped Say All."
        )

    def test_stop_from_empty_state(self, test_context: OrcaTestContext) -> None:
        """Test SayAllPresenter.stop works correctly when already in empty state."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.say_all_presenter import SayAllPresenter  # pylint: disable=import-outside-toplevel

        presenter = SayAllPresenter()
        assert presenter._contexts == []
        assert presenter._contents == []
        assert presenter._current_context is None
        assert presenter._say_all_is_running is False

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance

        presenter.stop()

        assert presenter._contexts == []
        assert presenter._contents == []
        assert presenter._current_context is None
        assert presenter._say_all_is_running is False
        manager_instance.reset_active_mode.assert_called_once()
