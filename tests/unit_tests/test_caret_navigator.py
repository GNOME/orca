# Unit tests for caret_navigator.py methods.
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

"""Unit tests for caret_navigator.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestCaretNavigator:
    """Test CaretNavigator class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Any]:
        """Set up mocks for caret_navigator dependencies."""

        additional_modules = [
            "orca.command_manager",
            "orca.input_event_manager",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.guilabels",
            "orca.debug",
            "orca.ax_object",
            "orca.ax_text",
            "orca.script_manager",
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

    @pytest.mark.parametrize(
        "direction,event_provided,context_available,expected_result",
        [
            pytest.param("next", False, True, True, id="next_char_no_event_returns_true"),
            pytest.param("next", True, False, False, id="next_char_no_context_returns_false"),
            pytest.param("next", True, True, True, id="next_char_valid_navigation_succeeds"),
            pytest.param("previous", False, True, True, id="prev_char_no_event_returns_true"),
            pytest.param("previous", True, False, False, id="prev_char_no_context_returns_false"),
            pytest.param("previous", True, True, True, id="prev_char_valid_navigation_succeeds"),
        ],
    )
    def test_character_navigation(
        self,
        test_context: OrcaTestContext,
        direction: str,
        event_provided: bool,
        context_available: bool,
        expected_result: bool,
    ) -> None:
        """Test character navigation (next/previous) with various conditions."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject.supports_text.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_valid.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_ancestor.side_effect = (
            lambda obj, root, same: obj is not None and root is not None
        )

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_get_root_object", return_value=None)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock() if event_provided else None

        if context_available:
            mock_obj = test_context.Mock()
            if direction == "next":
                mock_script.utilities.next_context.return_value = (mock_obj, 10)
            else:
                mock_script.utilities.previous_context.return_value = (mock_obj, 5)
        elif direction == "next":
            mock_script.utilities.next_context.return_value = (None, 0)
        else:
            mock_script.utilities.previous_context.return_value = (None, 0)

        navigation_method = getattr(navigator, f"{direction}_character")
        result = navigation_method(mock_script, mock_event)
        assert result == expected_result

        if expected_result:
            pres_manager = essential_modules["orca.presentation_manager"].get_manager()
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called_once()
            pres_manager.interrupt_presentation.assert_called_once()
            mock_script.update_braille.assert_called_once()
            mock_script.say_character.assert_called_once()

    @pytest.mark.parametrize(
        "direction,context_result,word_contents,expected_result",
        [
            pytest.param("next", (None, 0), None, False, id="next_word_no_context"),
            pytest.param("next", ("obj", 20), [], False, id="next_word_no_contents"),
            pytest.param(
                "next",
                ("obj", 20),
                [("obj", 20, 25, "word")],
                True,
                id="next_word_success",
            ),
            pytest.param("previous", (None, 0), None, False, id="previous_word_no_context"),
            pytest.param("previous", ("obj", 15), [], False, id="previous_word_no_contents"),
            pytest.param(
                "previous",
                ("obj", 15),
                [("obj", 10, 15, "word")],
                True,
                id="previous_word_success",
            ),
        ],
    )
    def test_word_navigation(
        self,
        test_context: OrcaTestContext,
        direction: str,
        context_result: tuple,
        word_contents: list | None,
        expected_result: bool,
    ) -> None:
        """Test word navigation (next/previous) with various error conditions."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        if direction == "next":
            mock_script.utilities.next_context.return_value = context_result
        else:
            mock_script.utilities.previous_context.return_value = context_result

        mock_script.utilities.get_word_contents_at_offset.return_value = word_contents or []

        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.update_braille = test_context.Mock()
        mock_script.say_word = test_context.Mock()

        navigation_method = getattr(navigator, f"{direction}_word")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        if expected_result:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            pres_manager.interrupt_presentation.assert_called_once()
            mock_script.update_braille.assert_called_once()
            mock_script.say_word.assert_called_once()
        else:
            mock_script.utilities.set_caret_position.assert_not_called()
            pres_manager.interrupt_presentation.assert_not_called()

    @pytest.mark.parametrize(
        "test_method,expected_result",
        [
            pytest.param("suspend_commands", True, id="suspend_commands"),
            pytest.param("toggle_enabled", True, id="toggle_enabled"),
        ],
    )
    def test_navigator_control_methods(
        self,
        test_context: OrcaTestContext,
        test_method: str,
        expected_result: bool,
    ) -> None:
        """Test CaretNavigator control methods."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        if test_method == "suspend_commands":
            mock_cmd_mgr = test_context.Mock()
            essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
            test_context.patch_object(navigator, "_is_active_script", return_value=True)
            navigator._suspended = False
            navigator.suspend_commands(mock_script, True, "test reason")
            assert navigator._suspended == expected_result
            mock_cmd_mgr.set_group_suspended.assert_called_once()

        elif test_method == "toggle_enabled":
            mock_cmd_mgr = test_context.Mock()
            essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr

            guilabels_mock = essential_modules["orca.guilabels"]
            guilabels_mock.CARET_NAVIGATION_ENABLED = "Caret navigation enabled"
            guilabels_mock.CARET_NAVIGATION_DISABLED = "Caret navigation disabled"

            result = navigator.toggle_enabled(mock_script, mock_event)
            assert result == expected_result
            mock_cmd_mgr.set_group_enabled.assert_called_once()

    def test_navigator_initialization(self, test_context: OrcaTestContext) -> None:
        """Test CaretNavigator initialization."""
        self._setup_dependencies(test_context)
        from orca import command_manager
        from orca.caret_navigator import CaretNavigator

        navigator = CaretNavigator()

        assert hasattr(navigator, "_last_input_event")
        assert hasattr(navigator, "_suspended")
        assert navigator._last_input_event is None
        assert navigator._suspended is False
        # Commands are registered in CommandManager
        cmd_manager = command_manager.get_manager()
        assert cmd_manager is not None

    @pytest.mark.parametrize(
        "navigation_type,in_say_all,current_line,next_prev_contents,expected_result",
        [
            pytest.param(
                "next_line",
                True,
                [("obj", 0, 10, "text")],
                [],
                True,
                id="next_line_in_say_all",
            ),
            pytest.param("next_line", False, [], [], False, id="next_line_no_current_line"),
            pytest.param(
                "next_line",
                False,
                [("obj", 0, 10, "text")],
                [],
                False,
                id="next_line_no_next_contents",
            ),
            pytest.param(
                "next_line",
                False,
                [("obj", 0, 10, "text")],
                [("obj2", 11, 21, "next")],
                True,
                id="next_line_success",
            ),
            pytest.param(
                "previous_line",
                True,
                [("obj", 0, 10, "text")],
                [],
                True,
                id="previous_line_in_say_all",
            ),
            pytest.param("previous_line", False, [], [], False, id="previous_line_no_contents"),
            pytest.param(
                "previous_line",
                False,
                [("obj", 0, 10, "text")],
                [("obj", 0, 10, "prev")],
                True,
                id="previous_line_success",
            ),
        ],
    )
    def test_line_navigation(
        self,
        test_context: OrcaTestContext,
        navigation_type: str,
        in_say_all: bool,
        current_line: list | None,
        next_prev_contents: list,
        expected_result: bool,
    ) -> None:
        """Test line navigation including say-all mode handling."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        manager_instance.in_say_all.return_value = in_say_all

        if in_say_all:
            from orca import say_all_presenter  # pylint: disable=import-outside-toplevel

            say_all_presenter.get_presenter().set_rewind_and_fast_forward_enabled(True)

        if navigation_type == "next_line" and not in_say_all:
            mock_script.utilities.get_caret_context.return_value = ("obj", 5)
            mock_script.utilities.get_line_contents_at_offset.return_value = current_line
            mock_script.utilities.get_next_line_contents.return_value = next_prev_contents
            test_context.patch_object(navigator, "_get_end_of_file", return_value=(None, -1))
            test_context.patch_object(navigator, "_line_contains_context", return_value=False)
            test_context.patch_object(navigator, "_is_navigable_object", return_value=True)
        elif navigation_type == "previous_line" and not in_say_all:
            mock_script.utilities.get_caret_context.return_value = ("obj", 5)
            mock_script.utilities.get_line_contents_at_offset.return_value = current_line
            mock_script.utilities.get_previous_line_contents.return_value = next_prev_contents
            test_context.patch_object(navigator, "_get_start_of_file", return_value=(None, -1))
            test_context.patch_object(navigator, "_line_contains_context", return_value=False)
            test_context.patch_object(navigator, "_is_navigable_object", return_value=True)

        mock_script.utilities.set_caret_position = test_context.Mock()

        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.interrupt_presentation.reset_mock()
        pres_manager.speak_contents.reset_mock()
        pres_manager.display_contents.reset_mock()

        navigation_method = getattr(navigator, f"{navigation_type}")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result and not in_say_all:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            pres_manager.interrupt_presentation.assert_called_once()
            pres_manager.speak_contents.assert_called_once()
            pres_manager.display_contents.assert_called_once()
        elif in_say_all:
            assert navigator._last_input_event != mock_event

    @pytest.mark.parametrize(
        "navigation_type,line_contents,expected_result",
        [
            pytest.param("start_of_line", [], False, id="start_of_line_no_line"),
            pytest.param(
                "start_of_line",
                [("obj", 5, 15, "text")],
                True,
                id="start_of_line_success",
            ),
            pytest.param("end_of_line", [], False, id="end_of_line_no_line"),
            pytest.param(
                "end_of_line",
                [("obj", 5, 15, "text ")],
                True,
                id="end_of_line_with_space",
            ),
            pytest.param("end_of_line", [("obj", 5, 15, "text")], True, id="end_of_line_no_space"),
        ],
    )
    def test_line_boundary_navigation(
        self,
        test_context: OrcaTestContext,
        navigation_type: str,
        line_contents: list,
        expected_result: bool,
    ) -> None:
        """Test start/end of line navigation."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        mock_script.utilities.get_caret_context.return_value = ("obj", 10)
        mock_script.utilities.get_line_contents_at_offset.return_value = line_contents

        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.say_character = test_context.Mock()

        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.interrupt_presentation.reset_mock()
        pres_manager.display_contents.reset_mock()

        navigation_method = getattr(navigator, f"{navigation_type}")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            pres_manager.interrupt_presentation.assert_called_once()
            mock_script.say_character.assert_called_once()
            pres_manager.display_contents.assert_called_once()

    @pytest.mark.parametrize(
        "script_is_active,expected_result",
        [
            pytest.param(True, True, id="script_is_active"),
            pytest.param(False, False, id="script_is_not_active"),
        ],
    )
    def test_is_active_script(
        self,
        test_context: OrcaTestContext,
        script_is_active: bool,
        expected_result: bool,
    ) -> None:
        """Test _is_active_script method with active and non-active scripts."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_active_script = test_context.Mock()

        script_manager_mock = essential_modules["orca.script_manager"]
        manager_instance = test_context.Mock()
        script_manager_mock.get_manager.return_value = manager_instance

        if script_is_active:
            manager_instance.get_active_script.return_value = mock_script
        else:
            manager_instance.get_active_script.return_value = mock_active_script

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_tokens = test_context.Mock()

        result = navigator._is_active_script(mock_script)
        assert result == expected_result

        if not script_is_active:
            debug_mock.print_tokens.assert_called_once()

    def test_get_is_enabled(self, test_context: OrcaTestContext) -> None:
        """Test get_is_enabled returns setting value."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.get_is_enabled()
        assert result is True

    def test_set_is_enabled_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_is_enabled still calls set_group_enabled even if value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        mock_cmd_mgr = test_context.Mock()
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.set_is_enabled(True)
        assert result is True
        mock_cmd_mgr.set_group_enabled.assert_called_once()

    def test_set_is_enabled_updates_setting(self, test_context: OrcaTestContext) -> None:
        """Test set_is_enabled updates setting and calls CommandManager."""

        essential_modules = self._setup_dependencies(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_runtime_value("caret-navigation", "enabled", False)
        mock_script = test_context.Mock()
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        mock_cmd_mgr = test_context.Mock()
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()

        result = navigator.set_is_enabled(True)
        assert result is True
        assert navigator.get_is_enabled() is True
        assert navigator._last_input_event is None
        mock_cmd_mgr.set_group_enabled.assert_called_once()

    def test_set_is_enabled_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test set_is_enabled updates state even with no active script."""

        essential_modules = self._setup_dependencies(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_runtime_value("caret-navigation", "enabled", False)
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = None
        mock_cmd_mgr = test_context.Mock()
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()

        result = navigator.set_is_enabled(True)
        assert result is True
        mock_cmd_mgr.set_group_enabled.assert_called_once()

    def test_get_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test get_triggers_focus_mode returns setting value."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.get_triggers_focus_mode()
        assert result is False

    def test_set_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test set_triggers_focus_mode updates setting."""

        self._setup_dependencies(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_runtime_value(
            "caret-navigation",
            "triggers-focus-mode",
            True,
        )
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.set_triggers_focus_mode(False)
        assert result is True
        assert navigator.get_triggers_focus_mode() is False

    def test_set_triggers_focus_mode_no_change(self, test_context: OrcaTestContext) -> None:
        """Test set_triggers_focus_mode returns early if unchanged."""

        self._setup_dependencies(test_context)
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_runtime_value(
            "caret-navigation",
            "triggers-focus-mode",
            True,
        )
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.set_triggers_focus_mode(True)
        assert result is True
        # set_setting no longer used - settings are set directly

    def test_get_enabled_for_script(self, test_context: OrcaTestContext) -> None:
        """Test get_enabled_for_script returns script-specific state."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        navigator._enabled_for_script[mock_script] = True
        result = navigator.get_enabled_for_script(mock_script)
        assert result is True

    def test_get_enabled_for_script_default(self, test_context: OrcaTestContext) -> None:
        """Test get_enabled_for_script returns False by default."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        result = navigator.get_enabled_for_script(mock_script)
        assert result is False

    def test_set_enabled_for_script(self, test_context: OrcaTestContext) -> None:
        """Test set_enabled_for_script updates script-specific state and calls set_is_enabled."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca import gsettings_registry

        gsettings_registry.get_registry().set_runtime_value("caret-navigation", "enabled", False)
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        mock_cmd_mgr = test_context.Mock()
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_is_active_script", return_value=True)

        navigator.set_enabled_for_script(mock_script, True)
        assert navigator._enabled_for_script[mock_script] is True
        mock_cmd_mgr.set_group_enabled.assert_called_once()

    def test_set_enabled_for_script_inactive_script(self, test_context: OrcaTestContext) -> None:
        """Test set_enabled_for_script doesn't call set_group_enabled for inactive script."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_cmd_mgr = test_context.Mock()
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_is_active_script", return_value=False)

        navigator.set_enabled_for_script(mock_script, True)
        assert navigator._enabled_for_script[mock_script] is True
        mock_cmd_mgr.set_group_enabled.assert_not_called()

    def test_set_enabled_for_script_always_calls_set_group_enabled(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test set_enabled_for_script always calls set_group_enabled even if setting matches.

        This is a regression test for issue #655 where caret navigation commands
        were not being enabled because set_is_enabled() would early-return when
        the setting already matched the desired value.
        """

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        mock_cmd_mgr = test_context.Mock()
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_is_active_script", return_value=True)

        navigator.set_enabled_for_script(mock_script, True)
        assert navigator._enabled_for_script[mock_script] is True
        mock_cmd_mgr.set_group_enabled.assert_called_once()

    def test_last_command_prevents_focus_mode_true(self, test_context: OrcaTestContext) -> None:
        """Test last_command_prevents_focus_mode returns True."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        mock_event = test_context.Mock()
        navigator._last_input_event = mock_event
        test_context.patch_object(
            navigator,
            "last_input_event_was_navigation_command",
            return_value=True,
        )
        result = navigator.last_command_prevents_focus_mode()
        assert result is True

    def test_last_command_prevents_focus_mode_false_no_event(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test last_command_prevents_focus_mode returns False if no event."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        navigator._last_input_event = None
        result = navigator.last_command_prevents_focus_mode()
        assert result is False

    def test_last_command_prevents_focus_mode_false_setting_true(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test last_command_prevents_focus_mode returns False if setting True."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator  # pylint: disable=import-outside-toplevel

        navigator = CaretNavigator()
        navigator.set_triggers_focus_mode(True)
        mock_event = test_context.Mock()
        navigator._last_input_event = mock_event
        test_context.patch_object(
            navigator,
            "last_input_event_was_navigation_command",
            return_value=True,
        )
        result = navigator.last_command_prevents_focus_mode()
        assert result is False

    def test_successful_navigation_emits_region_changed(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test successful caret navigation emits region_changed with CARET_NAVIGATOR mode."""

        essential_modules = self._setup_dependencies(test_context)
        from orca import focus_manager
        from orca.caret_navigator import CaretNavigator

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject.supports_text.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_valid.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_ancestor.side_effect = (
            lambda obj, root, same: obj is not None and root is not None
        )

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        focus_manager_mock.CARET_NAVIGATOR = focus_manager.CARET_NAVIGATOR

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_get_root_object", return_value=None)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()

        mock_script.utilities.next_context.return_value = (mock_obj, 10)

        result = navigator.next_character(mock_script, mock_event)

        assert result is True
        manager_instance.emit_region_changed.assert_called()
        call_kwargs = manager_instance.emit_region_changed.call_args
        assert call_kwargs.kwargs.get("mode") == focus_manager.CARET_NAVIGATOR
