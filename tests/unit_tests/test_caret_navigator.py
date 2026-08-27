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
from unittest.mock import call

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

        essential_modules["orca.ax_text"].AXText.get_character_at_offset = test_context.Mock(
            return_value=("", 0, 0)
        )
        test_context.patch(
            "orca.ax_utilities.AXUtilities.set_document_text_selection_endpoints",
            return_value=False,
        )
        test_context.patch(
            "orca.ax_utilities.AXUtilities.has_selected_text",
            return_value=False,
        )
        test_context.patch(
            "orca.ax_utilities.AXUtilities.get_document_text_selection_endpoints",
            return_value=((None, -1), (None, -1)),
        )
        test_context.patch(
            "orca.ax_utilities.AXUtilities.update_cached_selected_text",
        )
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

        dbus_service_mock = essential_modules["orca.dbus_service"]
        dbus_service_mock.testing_command.side_effect = lambda func: func
        dbus_service_mock.testing_user_command.side_effect = lambda func: func
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module.return_value = None
        dbus_service_mock.get_remote_controller.return_value = controller_mock

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
        from orca.caret_navigator import (  # pylint: disable=import-outside-toplevel
            AXUtilities,
            CaretNavigator,
        )

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject.supports_text.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_valid.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_ancestor.side_effect = lambda obj, root, same: (
            obj is not None and root is not None
        )

        navigator = CaretNavigator()
        test_context.patch_object(navigator, "_get_root_object", return_value=None)
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock() if event_provided else None
        mock_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.return_value = (mock_obj, 9)

        if context_available:
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
        "forward,expected_offset",
        [
            pytest.param(True, 34, id="right_moves_to_selection_end"),
            pytest.param(False, 0, id="left_moves_to_selection_start"),
        ],
    )
    def test_character_navigation_clears_selection_and_moves_to_start_or_end(
        self,
        test_context: OrcaTestContext,
        forward: bool,
        expected_offset: int,
    ) -> None:
        """Test character navigation clears selected text and moves to its start or end."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXObject,
            AXText,
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
            text_selection_manager,
            text_selection_presenter,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.return_value = (mock_obj, 0)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("selected", 0, 34),
        )
        get_root = test_context.patch_object(
            navigator,
            "_get_root_object",
            return_value=mock_obj,
        )
        selection_manager = test_context.Mock()
        selection_manager.get_known_text_selection_endpoints.return_value = (
            (mock_obj, 0),
            (mock_obj, 34),
        )
        selection_manager.clear_selection_for_navigation.return_value = [mock_obj]
        test_context.patch_object(
            text_selection_manager,
            "get_manager",
            return_value=selection_manager,
        )
        presenter = test_context.Mock()
        test_context.patch_object(
            text_selection_presenter,
            "get_presenter",
            return_value=presenter,
        )
        test_context.patch_object(
            AXText,
            "get_character_count",
            return_value=34,
        )
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)

        command = navigator.next_character if forward else navigator.previous_character
        assert command(mock_script, mock_event) is True
        mock_script.utilities.next_context.assert_not_called()
        mock_script.utilities.previous_context.assert_not_called()
        mock_script.utilities.set_caret_position.assert_called_once_with(
            mock_obj,
            expected_offset,
            reason=CaretSetReason.CARET_NAVIGATION,
        )
        selection_manager.get_known_text_selection_endpoints.assert_called_once_with(mock_obj)
        get_root.assert_called_once_with(mock_script)

    def test_caret_navigation_clears_selection_in_other_text_objects(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test ordinary caret navigation clears a selection spanning text objects."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            CaretNavigator,
            CaretSetReason,
            text_selection_manager,
            text_selection_presenter,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        root = test_context.Mock()
        destination = test_context.Mock()
        other_page = test_context.Mock()
        test_context.patch_object(navigator, "_get_root_object", return_value=root)
        selection_manager = test_context.Mock()
        selection_manager.clear_selection_for_navigation.return_value = [other_page]
        test_context.patch_object(
            text_selection_manager,
            "get_manager",
            return_value=selection_manager,
        )
        presenter = test_context.Mock()
        test_context.patch_object(
            text_selection_presenter,
            "get_presenter",
            return_value=presenter,
        )

        navigator._set_caret_position(
            mock_script,
            destination,
            0,
            reason=CaretSetReason.CARET_NAVIGATION,
        )

        selection_manager.clear_selection_for_navigation.assert_called_once_with(
            root,
            destination,
        )
        presenter.present_selection_removed.assert_called_once_with()
        mock_script.utilities.set_caret_position.assert_called_once_with(
            destination,
            0,
            reason=CaretSetReason.CARET_NAVIGATION,
        )

    def test_select_next_character_continues_existing_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting the next character continues an existing selection."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (  # pylint: disable=import-outside-toplevel
            AXObject,
            AXText,
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (mock_obj, 1),
            (mock_obj, 1),
            (mock_obj, 2),
        ]
        mock_script.utilities.next_context.return_value = (mock_obj, 2)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXText,
            "get_character_at_offset",
            return_value=("n", 2, 3),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("L", 0, 1),
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        mock_script.utilities.in_document_content.return_value = False
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)

        assert navigator.select_next_character(mock_script, mock_event) is True
        mock_script.utilities.next_context.assert_called_once_with()
        mock_script.utilities.set_caret_position.assert_called_once_with(
            mock_obj,
            2,
            reason=CaretSetReason.TEXT_SELECTION_BY_CHARACTER,
        )
        set_selected_text.assert_called_once_with(mock_obj, 0, 2)

    @pytest.mark.parametrize(
        "testing_method_name,selection_method_name",
        [
            ("select_next_character_for_testing", "select_next_character"),
            ("select_previous_character_for_testing", "select_previous_character"),
            ("select_next_word_for_testing", "select_next_word"),
            ("select_previous_word_for_testing", "select_previous_word"),
            ("select_next_line_for_testing", "select_next_line"),
            ("select_previous_line_for_testing", "select_previous_line"),
            ("select_start_of_file_for_testing", "select_start_of_file"),
            ("select_end_of_file_for_testing", "select_end_of_file"),
            ("select_start_of_line_for_testing", "select_start_of_line"),
            ("select_end_of_line_for_testing", "select_end_of_line"),
        ],
    )
    def test_selection_testing_commands_call_selection_methods(
        self,
        test_context: OrcaTestContext,
        testing_method_name: str,
        selection_method_name: str,
    ) -> None:
        """Test each integration-testing command calls its selection method."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        selection_method = test_context.patch_object(
            navigator,
            selection_method_name,
            return_value=True,
        )

        testing_method = getattr(navigator, testing_method_name)
        assert testing_method("token", mock_script, mock_event, False) is True
        selection_method.assert_called_once_with(mock_script, mock_event, False)

    def test_select_next_character_includes_final_character_before_next_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test forward selection reaches the text object's end before leaving it."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXText, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        text_obj = test_context.Mock()
        next_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.return_value = (text_obj, 8)
        mock_script.utilities.next_context.return_value = (next_obj, 1)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        get_character = test_context.patch_object(
            AXText,
            "get_character_at_offset",
            return_value=("a", 8, 9),
        )
        test_context.patch_object(AXText, "get_character_count", return_value=9)

        result = navigator._get_text_selection_character_navigation_context(
            mock_script,
            forward=True,
        )

        assert result == (text_obj, 9)
        mock_script.utilities.next_context.assert_called_once_with()
        get_character.assert_called_once_with(
            text_obj,
            8,
            ensure_whole_characters=True,
        )

    def test_previous_character_clears_selection_and_moves_to_its_start(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test moving left clears selection and moves to its resolved start position."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXUtilities, CaretNavigator, text_selection_manager

        navigator = CaretNavigator()
        current_obj = test_context.Mock()
        root = test_context.Mock()
        endpoint_obj = test_context.Mock()
        caret_obj = test_context.Mock()
        selection_manager = test_context.Mock()
        selection_manager.get_known_text_selection_endpoints.return_value = (
            (endpoint_obj, 15),
            (current_obj, 2),
        )
        test_context.patch_object(
            text_selection_manager,
            "get_manager",
            return_value=selection_manager,
        )
        resolve = test_context.patch_object(
            AXUtilities,
            "get_caret_context_for_text_selection_endpoint",
            return_value=(caret_obj, 0),
        )
        has_selected_text = test_context.patch_object(AXUtilities, "has_selected_text")
        get_endpoints = test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
        )

        result = navigator._get_caret_context_for_collapsing_selection(
            root,
            forward=False,
        )

        assert result == (caret_obj, 0)
        selection_manager.get_known_text_selection_endpoints.assert_called_once_with(root)
        resolve.assert_called_once_with(
            endpoint_obj,
            15,
            endpoint_is_start=True,
        )
        has_selected_text.assert_not_called()
        get_endpoints.assert_not_called()

    def test_select_next_character_includes_current_text_before_embedded_child(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test forward selection does not skip text before an embedded child."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXText, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        text_obj = test_context.Mock()
        child = test_context.Mock()
        mock_script.utilities.get_caret_context.return_value = (text_obj, 10)
        mock_script.utilities.next_context.return_value = (child, 0)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        get_character = test_context.patch_object(
            AXText,
            "get_character_at_offset",
            return_value=(" ", 10, 11),
        )
        test_context.patch_object(AXText, "get_character_count", return_value=12)

        result = navigator._get_text_selection_character_navigation_context(
            mock_script,
            forward=True,
        )

        assert result == (text_obj, 11)
        get_character.assert_called_once_with(
            text_obj,
            10,
            ensure_whole_characters=True,
        )

    def test_select_next_character_includes_first_character_in_next_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test forward selection includes the first character after crossing objects."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXText, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        text_obj = test_context.Mock()
        next_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.return_value = (text_obj, 9)
        mock_script.utilities.next_context.return_value = (next_obj, 1)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        get_character = test_context.patch_object(
            AXText,
            "get_character_at_offset",
            return_value=(",", 1, 2),
        )
        test_context.patch_object(AXText, "get_character_count", return_value=9)

        result = navigator._get_text_selection_character_navigation_context(
            mock_script,
            forward=True,
        )

        assert result == (next_obj, 2)
        get_character.assert_called_once_with(
            next_obj,
            1,
            ensure_whole_characters=True,
        )

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
        "direction,boundary,context_result,word_contents,expected_offset",
        [
            pytest.param(
                "next",
                ("selection-end", 20),
                ("next-word", 21),
                [("next-word", 21, 30, "following")],
                30,
                id="next_word_from_selection_end",
            ),
            pytest.param(
                "previous",
                ("selection-start", 10),
                ("previous-word", 9),
                [("previous-word", 1, 9, "previous")],
                1,
                id="previous_word_from_selection_start",
            ),
        ],
    )
    def test_word_navigation_starts_from_selection_boundary(
        self,
        test_context: OrcaTestContext,
        direction: str,
        boundary: tuple,
        context_result: tuple,
        word_contents: list,
        expected_offset: int,
    ) -> None:
        """Test word navigation starts from the appropriate selection boundary."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator, CaretSetReason

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        root = test_context.Mock()
        test_context.patch_object(navigator, "_get_root_object", return_value=root)
        get_boundary = test_context.patch_object(
            navigator,
            "_get_caret_context_for_collapsing_selection",
            return_value=boundary,
        )
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)
        set_caret_position = test_context.patch_object(navigator, "_set_caret_position")
        context_method = getattr(mock_script.utilities, f"{direction}_context")
        context_method.return_value = context_result
        mock_script.utilities.get_word_contents_at_offset.return_value = word_contents

        assert getattr(navigator, f"{direction}_word")(mock_script, mock_event)

        context_method.assert_called_once_with(*boundary, skip_space=True)
        get_boundary.assert_called_once_with(root, forward=direction == "next")
        set_caret_position.assert_called_once_with(
            mock_script,
            word_contents[0][0],
            expected_offset,
            reason=CaretSetReason.CARET_NAVIGATION,
            selection_root=root,
        )

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

    def test_get_end_of_file_keeps_native_text_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test native text is not replaced by its container at the end of the file."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXText, AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_script.utilities.in_document_content.return_value = False
        test_context.patch_object(navigator, "_get_embedded_document_frame", return_value=None)
        test_context.patch_object(navigator, "_get_root_object", return_value="text")
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        find_deepest = test_context.patch_object(
            AXUtilities,
            "find_deepest_descendant",
            return_value="panel",
        )
        test_context.patch_object(
            AXUtilities,
            "is_ancestor",
            side_effect=lambda obj, root, _same: obj == root,
        )
        test_context.patch_object(AXUtilities, "is_web_element", return_value=False)
        get_parent = test_context.patch_object(AXObject, "get_parent", return_value="scroll pane")
        test_context.patch_object(AXText, "get_character_count", return_value=34)

        assert navigator._get_end_of_file(mock_script) == ("text", 34)
        find_deepest.assert_not_called()
        mock_script.utilities.in_document_content.assert_called_once_with("text")
        get_parent.assert_not_called()

    def test_get_end_of_file_uses_parent_of_document_static_text(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test document static-text leaves are replaced by their navigable parent."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXText, AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.next_context.return_value = (None, -1)
        test_context.patch_object(navigator, "_get_embedded_document_frame", return_value=None)
        test_context.patch_object(navigator, "_get_root_object", return_value="document")
        test_context.patch_object(
            AXUtilities,
            "find_deepest_descendant",
            return_value="static text",
        )
        test_context.patch_object(
            AXUtilities,
            "is_web_element",
            side_effect=lambda obj: obj == "paragraph",
        )
        get_parent = test_context.patch_object(AXObject, "get_parent", return_value="paragraph")
        test_context.patch_object(AXText, "get_character_count", return_value=10)

        assert navigator._get_end_of_file(mock_script) == ("paragraph", 9)
        get_parent.assert_called_once_with("static text")
        mock_script.utilities.next_context.assert_called_once_with(
            "paragraph",
            9,
            restrict_to="document",
        )

    def test_get_end_of_file_returns_text_object_when_parent_is_not_web_element(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test the text object is returned when its parent is not a web element."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXText, AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_script.utilities.in_document_content.return_value = True
        mock_script.utilities.next_context.side_effect = [("page 2", 51), (None, -1)]
        test_context.patch_object(navigator, "_get_embedded_document_frame", return_value=None)
        test_context.patch_object(navigator, "_get_root_object", return_value="document")
        test_context.patch_object(
            AXUtilities,
            "find_deepest_descendant",
            return_value="page 2",
        )
        test_context.patch_object(AXUtilities, "is_web_element", return_value=False)
        test_context.patch_object(AXUtilities, "is_ancestor", return_value=True)
        get_parent = test_context.patch_object(
            AXObject,
            "get_parent",
            return_value="document",
        )
        test_context.patch_object(AXText, "get_character_count", return_value=51)

        assert navigator._get_end_of_file(mock_script) == ("page 2", 51)
        get_parent.assert_called_once_with("page 2")
        assert mock_script.utilities.next_context.call_args_list == [
            call("page 2", 50, restrict_to="document"),
            call("page 2", 51, restrict_to="document"),
        ]

    def test_next_line_rejects_invalid_destination(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a malformed next-line result cannot invalidate the caret context."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        current_obj = test_context.Mock()
        current_line = [(current_obj, 0, 10, "Last line.")]
        mock_script.utilities.get_caret_context.return_value = (current_obj, 10)
        mock_script.utilities.get_line_contents_at_offset.return_value = current_line
        mock_script.utilities.get_next_line_contents.return_value = [(None, 0, 0, "")]
        test_context.patch_object(
            AXObject,
            "supports_text",
            side_effect=lambda obj: obj is current_obj,
        )
        test_context.patch_object(navigator, "_get_root_object", return_value=None)

        assert navigator.next_line(mock_script, mock_event) is False
        mock_script.utilities.set_caret_position.assert_not_called()
        presenter = essential_modules["orca.presentation_manager"].get_manager()
        presenter.interrupt_presentation.assert_not_called()
        presenter.present_contents.assert_not_called()

    def test_toggle_disabled_clears_caret_context(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test returning caret control to the application clears Orca's context."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_cmd_mgr = test_context.Mock()
        mock_cmd_mgr.is_group_enabled.return_value = True
        essential_modules["orca.command_manager"].get_manager.return_value = mock_cmd_mgr
        set_is_enabled = test_context.patch_object(
            navigator,
            "set_is_enabled",
            return_value=True,
        )

        assert navigator.toggle_enabled(mock_script, notify_user=False) is True
        mock_script.utilities.clear_caret_context.assert_called_once_with()
        set_is_enabled.assert_called_once_with(False)

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
        pres_manager.present_contents.reset_mock()

        navigation_method = getattr(navigator, f"{navigation_type}")
        result = navigation_method(mock_script, mock_event)

        assert result == expected_result

        if expected_result and not in_say_all:
            assert navigator._last_input_event == mock_event
            mock_script.utilities.set_caret_position.assert_called()
            pres_manager.interrupt_presentation.assert_called_once()
            pres_manager.present_contents.assert_called_once()
        elif in_say_all:
            assert navigator._last_input_event != mock_event

    def test_next_line_does_not_move_to_ui_control(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test next-line navigation does not move into a neighboring UI control."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_script.utilities.get_caret_context.return_value = ("text", 26)
        mock_script.utilities.get_line_contents_at_offset.return_value = [
            ("text", 26, 34, "The end."),
        ]
        mock_script.utilities.get_next_line_contents.return_value = [
            ("scrollbar", 0, 0, ""),
        ]
        is_navigable = test_context.patch_object(
            navigator,
            "_is_navigable_object",
            return_value=False,
        )
        test_context.patch_object(
            navigator,
            "_get_end_of_file",
            return_value=("other text", 34),
        )
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.interrupt_presentation.reset_mock()

        assert navigator.next_line(mock_script, mock_event) is False
        is_navigable.assert_called_once_with(mock_script, "scrollbar")
        mock_script.utilities.set_caret_position.assert_not_called()
        pres_manager.interrupt_presentation.assert_not_called()
        assert navigator._last_input_event is None

    def test_select_next_line_moves_to_end_when_next_contents_are_outside_document(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test line selection includes the final line before an adjacent UI control."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator, CaretSetReason

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        current_line = [("text", 26, 34, "The end.")]
        mock_script.utilities.get_caret_context.return_value = ("text", 26)
        mock_script.utilities.get_line_contents_at_offset.return_value = current_line
        mock_script.utilities.get_next_line_contents.return_value = [("scrollbar", 0, 0, "")]
        test_context.patch_object(
            navigator,
            "_is_navigable_object",
            side_effect=lambda _script, obj: obj == "text",
        )
        test_context.patch_object(
            navigator,
            "_get_end_of_file",
            return_value=("text", 34),
        )

        assert navigator._move_to_next_line(
            mock_script,
            mock_event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        mock_script.utilities.set_caret_position.assert_called_once_with(
            "text",
            34,
            reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )

    def test_select_next_line_from_line_end_moves_to_end_of_next_line(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test line selection at a line end includes the entire next line."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator, CaretSetReason

        navigator = CaretNavigator()
        script = test_context.Mock()
        event = test_context.Mock()
        current_obj = test_context.Mock()
        next_obj = test_context.Mock()
        current_line = [(current_obj, 0, 4, "One.")]
        next_line = [(next_obj, 0, 6, "Two.\n")]
        script.utilities.get_caret_context.return_value = (current_obj, 4)
        script.utilities.get_line_contents_at_offset.return_value = current_line
        script.utilities.get_next_line_contents.return_value = next_line
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)
        set_caret_position = test_context.patch_object(navigator, "_set_caret_position")

        assert navigator._move_to_next_line(
            script,
            event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        set_caret_position.assert_called_once_with(
            script,
            next_obj,
            6,
            reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
            selection_root=None,
        )

    def test_select_previous_line_from_line_end_moves_to_start_of_current_line(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test backward line selection at a line end includes the current line."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import CaretNavigator, CaretSetReason

        navigator = CaretNavigator()
        script = test_context.Mock()
        event = test_context.Mock()
        obj = test_context.Mock()
        line = [(obj, 4, 8, "Two.")]
        script.utilities.get_caret_context.return_value = (obj, 8)
        script.utilities.get_line_contents_at_offset.side_effect = [
            [(obj, -2, -1, "")],
            line,
        ]
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)
        set_caret_position = test_context.patch_object(navigator, "_set_caret_position")

        assert navigator._move_to_previous_line(
            script,
            event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        assert script.utilities.get_line_contents_at_offset.call_args_list == [
            call(obj, 8),
            call(obj, 7),
        ]
        script.utilities.get_previous_line_contents.assert_not_called()
        set_caret_position.assert_called_once_with(
            script,
            obj,
            4,
            reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
            selection_root=None,
        )

    def test_previous_line_moves_before_start_of_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test Up clears a multi-object selection and moves above its start."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
            text_selection_manager,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        page1 = test_context.Mock()
        page2 = test_context.Mock()
        root = test_context.Mock()
        current_line = [(page2, 12, 30, "Here's a new page.")]
        previous_line = [(page1, 65, 77, "Another one!")]
        mock_script.utilities.get_caret_context.return_value = (page2, 51)
        mock_script.utilities.get_line_contents_at_offset.return_value = current_line
        mock_script.utilities.get_previous_line_contents.return_value = previous_line
        selection_manager = test_context.Mock()
        selection_manager.get_known_text_selection_endpoints.return_value = (
            (page1, 78),
            (page2, 50),
        )
        test_context.patch_object(
            text_selection_manager,
            "get_manager",
            return_value=selection_manager,
        )
        test_context.patch_object(
            AXUtilities,
            "get_caret_context_for_text_selection_endpoint",
            side_effect=lambda obj, offset, *, endpoint_is_start: (obj, offset),
        )
        test_context.patch_object(navigator, "_get_root_object", return_value=root)
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)
        set_caret_position = test_context.patch_object(navigator, "_set_caret_position")

        assert navigator.previous_line(mock_script, mock_event) is True

        mock_script.utilities.get_previous_line_contents.assert_called_once_with(page1, 78)
        set_caret_position.assert_called_once_with(
            mock_script,
            page1,
            65,
            reason=CaretSetReason.CARET_NAVIGATION,
            selection_root=root,
        )
        presenter = essential_modules["orca.presentation_manager"].get_manager()
        presenter.present_contents.assert_called_once_with(previous_line, prior_obj=page2)

    def test_next_line_moves_after_end_of_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test Down clears a multi-object selection and moves below its end."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
            text_selection_manager,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        page1 = test_context.Mock()
        page2 = test_context.Mock()
        root = test_context.Mock()
        current_line = [(page1, 65, 77, "Another one!")]
        next_line = [(page2, 31, 50, "I really like pages.")]
        mock_script.utilities.get_caret_context.return_value = (page1, 65)
        mock_script.utilities.get_line_contents_at_offset.return_value = current_line
        mock_script.utilities.get_next_line_contents.return_value = next_line
        selection_manager = test_context.Mock()
        selection_manager.get_known_text_selection_endpoints.return_value = (
            (page1, 65),
            (page2, 30),
        )
        test_context.patch_object(
            text_selection_manager,
            "get_manager",
            return_value=selection_manager,
        )
        test_context.patch_object(
            AXUtilities,
            "get_caret_context_for_text_selection_endpoint",
            side_effect=lambda obj, offset, *, endpoint_is_start: (obj, offset),
        )
        test_context.patch_object(navigator, "_get_root_object", return_value=root)
        test_context.patch_object(navigator, "_is_navigable_object", return_value=True)
        set_caret_position = test_context.patch_object(navigator, "_set_caret_position")

        assert navigator.next_line(mock_script, mock_event) is True

        mock_script.utilities.get_next_line_contents.assert_called_once_with(page2, 30)
        set_caret_position.assert_called_once_with(
            mock_script,
            page2,
            31,
            reason=CaretSetReason.CARET_NAVIGATION,
            selection_root=root,
        )
        presenter = essential_modules["orca.presentation_manager"].get_manager()
        presenter.present_contents.assert_called_once_with(next_line, prior_obj=page1)

    @pytest.mark.parametrize(
        "is_page,expected_prior_obj",
        [
            pytest.param(True, "destination", id="page_role_suppressed"),
            pytest.param(False, "source", id="source_context_preserved"),
        ],
    )
    def test_end_of_file_does_not_present_page_role(
        self,
        test_context: OrcaTestContext,
        is_page: bool,
        expected_prior_obj: str | None,
    ) -> None:
        """Test end-of-file presentation does not include a page role."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_text import AXText
        from orca.ax_utilities import AXUtilities
        from orca.caret_navigator import CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        contents = [("destination", 26, 34, "The end.")]
        mock_script.utilities.get_caret_context.return_value = ("source", 12)
        mock_script.utilities.get_line_contents_at_offset.return_value = contents
        test_context.patch_object(navigator, "_get_end_of_file", return_value=("destination", 34))
        test_context.patch_object(AXText, "get_character_count", return_value=34)
        test_context.patch_object(AXUtilities, "is_page", return_value=is_page)
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.present_contents.reset_mock()

        assert navigator.end_of_file(mock_script, mock_event) is True
        mock_script.utilities.get_line_contents_at_offset.assert_called_once_with(
            "destination",
            33,
        )
        pres_manager.present_contents.assert_called_once_with(
            contents,
            prior_obj=expected_prior_obj,
        )

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
    def test_start_and_end_of_line_navigation(
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

    def test_select_next_line_selects_unterminated_final_line(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting the final line uses the end of the text."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXObject,
            AXText,
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (mock_obj, 26),
            (mock_obj, 34),
        ]
        mock_script.utilities.get_line_contents_at_offset.return_value = [
            (mock_obj, 26, 34, "The end."),
        ]
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=34)
        mock_script.utilities.in_document_content.return_value = False
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("Hello world.\nBla bla bla.\n", 0, 26),
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        next_line = test_context.patch_object(navigator, "_move_to_next_line", return_value=True)
        end_of_line = test_context.patch_object(
            navigator,
            "_move_to_end_of_line",
            return_value=True,
        )
        test_context.patch_object(
            navigator,
            "_get_end_of_file",
            return_value=(mock_obj, 34),
        )

        assert navigator.select_next_line(mock_script, mock_event) is True
        next_line.assert_called_once_with(
            mock_script,
            mock_event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        end_of_line.assert_not_called()
        set_selected_text.assert_called_once_with(mock_obj, 0, 34)

    def test_select_next_line_at_object_end_adds_selection_in_next_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting the next line starts a selection in the next object."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXText,
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
            text_selection_manager,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        old_obj = test_context.Mock()
        new_obj = test_context.Mock()
        document = test_context.Mock()
        old_selection = ("First page.", 0, 11)
        new_selection = ("Next", 0, 4)
        mock_script.utilities.get_caret_context.side_effect = [
            (old_obj, 11),
            (new_obj, 4),
        ]
        mock_script.utilities.get_line_contents_at_offset.return_value = [
            (old_obj, 0, 11, "First page."),
        ]
        mock_script.utilities.active_document.return_value = document
        test_context.patch_object(
            AXText,
            "get_character_count",
            side_effect=lambda obj: 11 if obj == old_obj else 20,
        )
        get_selected_text = test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[old_selection, ("", 0, 0), old_selection, old_selection, new_selection],
        )
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        next_line = test_context.patch_object(navigator, "_move_to_next_line", return_value=True)
        end_of_line = test_context.patch_object(
            navigator,
            "_move_to_end_of_line",
            return_value=True,
        )

        assert navigator.select_next_line(mock_script, mock_event) is True

        next_line.assert_called_once_with(
            mock_script,
            mock_event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        end_of_line.assert_not_called()
        set_selected_text.assert_called_once_with(new_obj, 0, 4)
        assert get_selected_text.call_args_list == [
            call(old_obj),
            call(new_obj),
        ]
        selection_manager = text_selection_manager.get_manager()
        command = selection_manager.get_current_selection_command()
        assert command is not None
        assert command.get_objects() == (old_obj, new_obj)
        assert command.should_notify_user()

    def test_select_next_line_does_not_treat_web_element_end_as_file_end(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selection moves from a complete web element to the next visual line."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXObject,
            AXText,
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        current_obj = test_context.Mock()
        final_obj = test_context.Mock()
        next_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (current_obj, 0),
            (next_obj, 0),
        ]
        line = [(current_obj, 0, 26, "current line")]
        mock_script.utilities.get_line_contents_at_offset.return_value = line
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=26)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("", 0, 0),
        )
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_endpoint_for_caret_context",
            side_effect=lambda obj, offset, *, after_embedded_object: (obj, offset),
        )
        test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        test_context.patch_object(
            navigator,
            "_get_end_of_file",
            return_value=(final_obj, 10),
        )
        next_line = test_context.patch_object(navigator, "_move_to_next_line", return_value=True)
        end_of_line = test_context.patch_object(
            navigator,
            "_move_to_end_of_line",
            return_value=True,
        )

        assert navigator.select_next_line(mock_script, mock_event) is True
        next_line.assert_called_once_with(
            mock_script,
            mock_event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        end_of_line.assert_not_called()

    def test_selection_across_objects_uses_document_interface(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selection across objects uses the document interface."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXUtilities, CaretNavigator, text_selection_manager

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        old_obj = test_context.Mock()
        new_obj = test_context.Mock()
        document = test_context.Mock()
        selection_manager = text_selection_manager.get_manager()
        mock_script.utilities.get_caret_context.side_effect = [
            (old_obj, 10),
            (new_obj, 5),
        ]
        mock_script.utilities.active_document.return_value = document
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("selection", 0, 10),
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((old_obj, 2), (old_obj, 10)),
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_endpoint_for_caret_context",
            side_effect=lambda obj, offset, *, after_embedded_object: (obj, offset),
        )
        set_document_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                mock_event,
                False,
                move,
                selection_forward=True,
            )
            is True
        )

        set_document_selection.assert_called_once_with(
            document,
            old_obj,
            2,
            new_obj,
            5,
        )
        set_selected_text.assert_not_called()
        command = selection_manager.get_current_selection_command()
        assert command is not None
        assert command.get_objects() == (new_obj,)
        assert not command.should_notify_user()

    def test_selection_through_embedded_object_ends_after_its_character(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test forward selection through an image ends after its character in the parent."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXUtilities, CaretNavigator, text_selection_manager

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        heading = test_context.Mock()
        image = test_context.Mock()
        link = test_context.Mock()
        document = test_context.Mock()
        selection_manager = text_selection_manager.get_manager()
        mock_script.utilities.get_caret_context.side_effect = [
            (heading, 29),
            (image, 0),
        ]
        mock_script.utilities.active_document.return_value = document
        get_selection_point = test_context.patch_object(
            AXUtilities,
            "get_text_selection_endpoint_for_caret_context",
            side_effect=[(heading, 29), (link, 1)],
        )
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("selected heading", 0, 29),
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((heading, 0), (heading, 29)),
        )
        set_document_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                mock_event,
                False,
                move,
                selection_forward=True,
            )
            is True
        )

        set_document_selection.assert_called_once_with(
            document,
            heading,
            0,
            link,
            1,
        )
        assert get_selection_point.call_args_list == [
            call(heading, 29, after_embedded_object=False),
            call(image, 0, after_embedded_object=True),
        ]
        command = selection_manager.get_current_selection_command()
        assert command is not None
        assert command.get_objects() == (image,)
        assert not command.should_notify_user()

    def test_selection_continues_from_embedded_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selection can continue when the Orca caret is on a non-text object."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXUtilities, CaretNavigator, text_selection_manager

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        heading = test_context.Mock()
        image = test_context.Mock()
        link = test_context.Mock()
        paragraph = test_context.Mock()
        document = test_context.Mock()
        selection_manager = text_selection_manager.get_manager()
        mock_script.utilities.get_caret_context.side_effect = [
            (image, 0),
            (paragraph, 12),
        ]
        mock_script.utilities.active_document.return_value = document
        get_selection_point = test_context.patch_object(
            AXUtilities,
            "get_text_selection_endpoint_for_caret_context",
            side_effect=[(link, 0), (paragraph, 12)],
        )
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("embedded object", 0, 1),
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((heading, 0), (link, 0)),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=1,
        )
        test_context.patch_object(
            AXUtilities,
            "text_selection_positions_are_equivalent",
            side_effect=[False, True],
        )
        set_document_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                mock_event,
                False,
                move,
                selection_forward=True,
            )
            is True
        )

        move.assert_called_once_with(mock_script, mock_event, False)
        set_document_selection.assert_called_once_with(
            document,
            heading,
            0,
            paragraph,
            12,
        )
        assert get_selection_point.call_args_list == [
            call(image, 0, after_embedded_object=False),
            call(paragraph, 12, after_embedded_object=True),
        ]
        command = selection_manager.get_current_selection_command()
        assert command is not None
        assert command.get_objects() == (paragraph,)
        assert not command.should_notify_user()

    def test_select_next_character_keeps_end_as_anchor_for_backward_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting right in a backward selection keeps its end as the anchor."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        obj = test_context.Mock()
        document = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (obj, 3),
            (obj, 4),
        ]
        mock_script.utilities.active_document.return_value = document
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("selected", 3, 10),
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((obj, 3), (obj, 10)),
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_endpoint_for_caret_context",
            side_effect=lambda obj, offset, *, after_embedded_object: (obj, offset),
        )
        set_document_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=True,
        )
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                mock_event,
                False,
                move,
                selection_forward=True,
            )
            is True
        )

        set_document_selection.assert_called_once_with(
            document,
            obj,
            10,
            obj,
            4,
        )
        set_selected_text.assert_not_called()

    def test_selecting_backward_unselects_text_after_new_position(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting backward keeps text before the new position selected."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXText,
            AXUtilities,
            CaretNavigator,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        page1 = test_context.Mock()
        page2 = test_context.Mock()
        document = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (page2, 51),
            (page2, 31),
        ]
        mock_script.utilities.active_document.return_value = document
        test_context.patch_object(
            AXUtilities,
            "get_text_selection_endpoint_for_caret_context",
            side_effect=lambda obj, offset, *, after_embedded_object: (obj, offset),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("More pages!\nHere's a new page.\nI really like pages.", 0, 52),
        )
        set_document_selection = test_context.patch_object(
            AXUtilities,
            "set_document_text_selection_endpoints",
            return_value=False,
        )
        test_context.patch_object(
            AXUtilities,
            "get_document_text_selection_endpoints",
            return_value=((page1, 0), (page2, 50)),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=51,
        )
        test_context.patch_object(
            AXUtilities,
            "text_selection_positions_are_equivalent",
            side_effect=[False, True],
        )
        test_context.patch_object(AXText, "get_character_count", return_value=51)
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                None,
                False,
                move,
                selection_forward=False,
            )
            is True
        )

        set_document_selection.assert_called_once_with(document, page1, 0, page2, 31)
        set_selected_text.assert_called_once_with(page2, 0, 31)

    def test_selecting_backward_into_object_selects_through_its_end(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting backward into an object selects through its end."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXText, AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        old_obj = test_context.Mock()
        new_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (old_obj, 0),
            (new_obj, 12),
        ]
        mock_script.utilities.active_document.return_value = test_context.Mock()
        old_selection = ("Old", 0, 3)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                old_selection,
                ("", 0, 0),
                old_selection,
                old_selection,
                ("trailing", 12, 20),
            ],
        )
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        test_context.patch_object(AXText, "get_character_count", return_value=20)
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                None,
                False,
                move,
                selection_forward=False,
            )
            is True
        )

        set_selected_text.assert_called_once_with(new_obj, 12, 20)

    def test_selecting_backward_into_selected_object_ends_at_new_position(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test backward selection in the destination ends at the new position."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        old_obj = test_context.Mock()
        new_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (old_obj, 0),
            (new_obj, 81),
        ]
        mock_script.utilities.active_document.return_value = test_context.Mock()
        empty_selection = ("", 0, 0)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                empty_selection,
                ("whole first page", 0, 89),
                empty_selection,
                empty_selection,
                ("remaining", 0, 81),
            ],
        )
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                None,
                False,
                move,
                selection_forward=False,
            )
            is True
        )

        set_selected_text.assert_called_once_with(new_obj, 0, 81)

    def test_selecting_forward_into_selected_object_starts_at_new_position(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test forward selection in the destination starts at the new position."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXText, AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        old_obj = test_context.Mock()
        new_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (old_obj, 20),
            (new_obj, 8),
        ]
        mock_script.utilities.active_document.return_value = test_context.Mock()
        empty_selection = ("", 0, 0)
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                empty_selection,
                ("whole second page", 0, 20),
                empty_selection,
                empty_selection,
                ("remaining", 8, 20),
            ],
        )
        set_selected_text = test_context.patch_object(
            AXUtilities,
            "set_selected_text",
            return_value=True,
        )
        test_context.patch_object(AXText, "get_character_count", return_value=20)
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                None,
                False,
                move,
                selection_forward=True,
            )
            is True
        )

        set_selected_text.assert_called_once_with(new_obj, 8, 20)

    def test_selection_preserves_anchor_when_reported_range_omits_newline(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a newline omitted from the reported range does not replace the anchor."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import AXObject, AXUtilities, CaretNavigator

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (mock_obj, 13),
            (mock_obj, 26),
        ]
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        mock_script.utilities.in_document_content.return_value = False
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("Hello world.", 0, 12),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selection_anchor_offset",
            return_value=0,
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        move = test_context.Mock(return_value=True)

        assert (
            navigator._select_with_command(
                mock_script,
                mock_event,
                False,
                move,
                selection_forward=True,
            )
            is True
        )
        move.assert_called_once_with(mock_script, mock_event, False)
        set_selected_text.assert_called_once_with(mock_obj, 0, 26)

    def test_select_previous_line_unselects_only_final_line(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test selecting the previous line from the text end unselects only the final line."""

        self._setup_dependencies(test_context)
        from orca.caret_navigator import (
            AXObject,
            AXUtilities,
            CaretNavigator,
            CaretSetReason,
        )

        navigator = CaretNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_script.utilities.get_caret_context.side_effect = [
            (mock_obj, 34),
            (mock_obj, 26),
        ]
        mock_script.utilities.get_line_contents_at_offset.return_value = [
            (mock_obj, 26, 34, "The end."),
        ]
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        mock_script.utilities.in_document_content.return_value = False
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            return_value=("Hello world.\nBla bla bla.\nThe end.", 0, 34),
        )
        set_selected_text = test_context.patch_object(AXUtilities, "set_selected_text")
        previous_line = test_context.patch_object(
            navigator,
            "_move_to_previous_line",
            return_value=True,
        )
        start_of_line = test_context.patch_object(
            navigator,
            "_move_to_start_of_line",
            return_value=True,
        )

        assert navigator.select_previous_line(mock_script, mock_event) is True
        previous_line.assert_called_once_with(
            mock_script,
            mock_event,
            False,
            caret_set_reason=CaretSetReason.TEXT_SELECTION_BY_LINE,
        )
        start_of_line.assert_not_called()
        set_selected_text.assert_called_once_with(mock_obj, 0, 26)

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
        from orca.caret_navigator import AXUtilities, CaretNavigator

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject.supports_text.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_valid.side_effect = lambda obj: obj is not None
        ax_object_mock.AXObject.is_ancestor.side_effect = lambda obj, root, same: (
            obj is not None and root is not None
        )

        focus_manager_mock = essential_modules["orca.focus_manager"]
        manager_instance = test_context.Mock()
        focus_manager_mock.get_manager.return_value = manager_instance
        focus_manager_mock.CARET_NAVIGATOR = focus_manager.CARET_NAVIGATOR

        navigator = CaretNavigator()
        get_root = test_context.patch_object(navigator, "_get_root_object", return_value=None)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        mock_obj = test_context.Mock()

        mock_script.utilities.get_caret_context.return_value = (mock_obj, 9)
        mock_script.utilities.next_context.return_value = (mock_obj, 10)
        test_context.patch_object(AXUtilities, "get_selected_text", return_value=("", 0, 0))

        result = navigator.next_character(mock_script, mock_event)

        assert result is True
        get_root.assert_called_once_with(mock_script)
        manager_instance.emit_region_changed.assert_called()
        call_kwargs = manager_instance.emit_region_changed.call_args
        assert call_kwargs.kwargs.get("mode") == focus_manager.CARET_NAVIGATOR
