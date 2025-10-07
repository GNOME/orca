# Unit tests for structural_navigator.py methods.
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

"""Unit tests for structural_navigator.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestStructuralNavigator:
    """Test StructuralNavigator class methods."""

    def _setup_dependencies(self, test_context):
        """Set up dependencies for structural_navigator module testing."""

        additional_modules = [
            "orca.cmdnames",
            "orca.dbus_service",
            "orca.debug",
            "orca.focus_manager",
            "orca.guilabels",
            "orca.input_event_manager",
            "orca.keybindings",
            "orca.messages",
            "orca.object_properties",
            "orca.orca_gui_navlist",
            "orca.orca_i18n",
            "orca.script_manager",
            "orca.settings_manager",
            "orca.AXHypertext",
            "orca.AXObject",
            "orca.AXTable",
            "orca.AXText",
            "orca.AXUtilities",
            "orca.input_event",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)
        self._setup_mocks(test_context, essential_modules)
        return essential_modules

    def _setup_cycle_navigation_mode_mocks(
        self, test_context, nav, current_mode, supports_collection=True
    ):
        """Set up common navigator mocks for cycle_mode testing scenarios."""

        mock_get_mode = test_context.Mock(return_value=current_mode)
        test_context.patch_object(nav, "get_mode", new=mock_get_mode)

        mock_set_mode = test_context.Mock()
        test_context.patch_object(nav, "set_mode", new=mock_set_mode)

        test_context.patch_object(nav, "_is_active_script", return_value=True)

        mock_determine_root = None
        if supports_collection:
            mock_root = test_context.Mock()
            mock_determine_root = test_context.Mock(return_value=mock_root)
            test_context.patch_object(nav, "_determine_root_container", new=mock_determine_root)

        return mock_get_mode, mock_set_mode, mock_determine_root

    def _setup_mocks(self, test_context, essential_modules) -> None:
        """Set up common mocks for StructuralNavigator tests."""

        input_event_handler_mock = test_context.Mock()
        essential_modules["orca.input_event"].InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )
        key_bindings_instance = test_context.Mock()
        essential_modules["orca.keybindings"].KeyBindings = test_context.Mock(
            return_value=key_bindings_instance
        )
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.get_setting.return_value = True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value = settings_manager_instance
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module.return_value = None
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = controller_mock
        essential_modules["orca.debug"].print_message = test_context.Mock()
        essential_modules["orca.debug"].LEVEL_INFO = 800
        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_locus_of_focus.return_value = None
        essential_modules["orca.focus_manager"].get_manager.return_value = focus_manager_instance
        essential_modules["orca.AXObject"].get_parent.return_value = None
        essential_modules["orca.AXObject"].supports_collection.return_value = True
        essential_modules["orca.AXObject"].find_ancestor.return_value = None
        essential_modules["orca.AXUtilities"].is_web_application.return_value = False
        essential_modules["orca.AXUtilities"].is_heading.return_value = False
        essential_modules["orca.AXUtilities"].find_descendant.return_value = None
        script_manager_instance = test_context.Mock()
        script_manager_instance.get_active_script.return_value = None
        essential_modules["orca.script_manager"].get_manager.return_value = script_manager_instance
        essential_modules["orca.orca_i18n"]._ = lambda msg: msg
        essential_modules["orca.messages"].STRUCTURAL_NAVIGATION_KEYS_DOCUMENT = "Document mode"
        essential_modules["orca.messages"].STRUCTURAL_NAVIGATION_KEYS_GUI = "GUI mode"
        essential_modules["orca.messages"].STRUCTURAL_NAVIGATION_KEYS_OFF = "Off mode"
        essential_modules[
            "orca.messages"
        ].STRUCTURAL_NAVIGATION_NOT_SUPPORTED_FULL = "Not supported full"
        essential_modules[
            "orca.messages"
        ].STRUCTURAL_NAVIGATION_NOT_SUPPORTED_BRIEF = "Not supported brief"
        essential_modules["orca.messages"].WRAPPING_TO_TOP = "Wrapping to top"
        essential_modules["orca.messages"].WRAPPING_TO_BOTTOM = "Wrapping to bottom"
        essential_modules["orca.cmdnames"].STRUCTURAL_NAVIGATION_MODE_CYCLE = "cycle_mode"
        essential_modules["orca.cmdnames"].BLOCKQUOTE_PREV = "previous_blockquote"
        essential_modules["orca.cmdnames"].BLOCKQUOTE_NEXT = "next_blockquote"
        essential_modules["orca.cmdnames"].BLOCKQUOTE_LIST = "list_blockquotes"
        essential_modules["orca.cmdnames"].BUTTON_PREV = "previous_button"
        essential_modules["orca.cmdnames"].BUTTON_NEXT = "next_button"
        essential_modules["orca.cmdnames"].BUTTON_LIST = "list_buttons"
        essential_modules["orca.cmdnames"].CHECK_BOX_PREV = "previous_checkbox"
        essential_modules["orca.cmdnames"].CHECK_BOX_NEXT = "next_checkbox"
        essential_modules["orca.cmdnames"].CHECK_BOX_LIST = "list_checkboxes"
        essential_modules["orca.cmdnames"].COMBO_BOX_PREV = "previous_combobox"
        essential_modules["orca.cmdnames"].COMBO_BOX_NEXT = "next_combobox"
        essential_modules["orca.cmdnames"].COMBO_BOX_LIST = "list_comboboxes"
        essential_modules["orca.cmdnames"].ENTRY_PREV = "previous_entry"
        essential_modules["orca.cmdnames"].ENTRY_NEXT = "next_entry"
        essential_modules["orca.cmdnames"].ENTRY_LIST = "list_entries"
        essential_modules["orca.cmdnames"].FORM_FIELD_PREV = "previous_form_field"
        essential_modules["orca.cmdnames"].FORM_FIELD_NEXT = "next_form_field"
        essential_modules["orca.cmdnames"].FORM_FIELD_LIST = "list_form_fields"
        essential_modules["orca.cmdnames"].HEADING_PREV = "previous_heading"
        essential_modules["orca.cmdnames"].HEADING_NEXT = "next_heading"
        essential_modules["orca.cmdnames"].HEADING_LIST = "list_headings"
        essential_modules["orca.cmdnames"].HEADING_AT_LEVEL_PREV = "previous_heading_level_%d"
        essential_modules["orca.cmdnames"].HEADING_AT_LEVEL_NEXT = "next_heading_level_%d"
        essential_modules["orca.cmdnames"].HEADING_AT_LEVEL_LIST = "list_headings_level_%d"
        essential_modules["orca.cmdnames"].IFRAME_PREV = "previous_iframe"
        essential_modules["orca.cmdnames"].IFRAME_NEXT = "next_iframe"
        essential_modules["orca.cmdnames"].IFRAME_LIST = "list_iframes"
        essential_modules["orca.cmdnames"].IMAGE_PREV = "previous_image"
        essential_modules["orca.cmdnames"].IMAGE_NEXT = "next_image"
        essential_modules["orca.cmdnames"].IMAGE_LIST = "list_images"
        essential_modules["orca.cmdnames"].LANDMARK_PREV = "previous_landmark"
        essential_modules["orca.cmdnames"].LANDMARK_NEXT = "next_landmark"
        essential_modules["orca.cmdnames"].LANDMARK_LIST = "list_landmarks"
        essential_modules["orca.cmdnames"].LIST_PREV = "previous_list"
        essential_modules["orca.cmdnames"].LIST_NEXT = "next_list"
        essential_modules["orca.cmdnames"].LIST_LIST = "list_lists"
        essential_modules["orca.cmdnames"].LIST_ITEM_PREV = "previous_list_item"
        essential_modules["orca.cmdnames"].LIST_ITEM_NEXT = "next_list_item"
        essential_modules["orca.cmdnames"].LIST_ITEM_LIST = "list_list_items"
        essential_modules["orca.cmdnames"].LIVE_REGION_PREV = "previous_live_region"
        essential_modules["orca.cmdnames"].LIVE_REGION_NEXT = "next_live_region"
        essential_modules["orca.cmdnames"].LIVE_REGION_LAST = "last_live_region"
        essential_modules["orca.cmdnames"].PARAGRAPH_PREV = "previous_paragraph"
        essential_modules["orca.cmdnames"].PARAGRAPH_NEXT = "next_paragraph"
        essential_modules["orca.cmdnames"].PARAGRAPH_LIST = "list_paragraphs"
        essential_modules["orca.cmdnames"].RADIO_BUTTON_PREV = "previous_radio_button"
        essential_modules["orca.cmdnames"].RADIO_BUTTON_NEXT = "next_radio_button"
        essential_modules["orca.cmdnames"].RADIO_BUTTON_LIST = "list_radio_buttons"
        essential_modules["orca.cmdnames"].SEPARATOR_PREV = "previous_separator"
        essential_modules["orca.cmdnames"].SEPARATOR_NEXT = "next_separator"
        essential_modules["orca.cmdnames"].TABLE_PREV = "previous_table"
        essential_modules["orca.cmdnames"].TABLE_NEXT = "next_table"
        essential_modules["orca.cmdnames"].TABLE_LIST = "list_tables"
        essential_modules["orca.cmdnames"].LINK_PREV = "previous_link"
        essential_modules["orca.cmdnames"].LINK_NEXT = "next_link"
        essential_modules["orca.cmdnames"].LINK_LIST = "list_links"
        essential_modules["orca.cmdnames"].UNVISITED_LINK_PREV = "previous_unvisited_link"
        essential_modules["orca.cmdnames"].UNVISITED_LINK_NEXT = "next_unvisited_link"
        essential_modules["orca.cmdnames"].UNVISITED_LINK_LIST = "list_unvisited_links"
        essential_modules["orca.cmdnames"].VISITED_LINK_PREV = "previous_visited_link"
        essential_modules["orca.cmdnames"].VISITED_LINK_NEXT = "next_visited_link"
        essential_modules["orca.cmdnames"].VISITED_LINK_LIST = "list_visited_links"
        essential_modules["orca.cmdnames"].LARGE_OBJECT_PREV = "previous_large_object"
        essential_modules["orca.cmdnames"].LARGE_OBJECT_NEXT = "next_large_object"
        essential_modules["orca.cmdnames"].LARGE_OBJECT_LIST = "list_large_objects"
        essential_modules["orca.cmdnames"].CLICKABLE_PREV = "previous_clickable"
        essential_modules["orca.cmdnames"].CLICKABLE_NEXT = "next_clickable"
        essential_modules["orca.cmdnames"].CLICKABLE_LIST = "list_clickables"

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator initialization through get_navigator function."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        assert (
            nav._last_input_event is None or nav._last_input_event is not None
        )  # May be set by other tests
        assert isinstance(nav._suspended, bool)
        assert isinstance(nav._handlers, dict)
        assert nav._bindings is not None
        assert isinstance(nav._mode_for_script, dict)

    @pytest.mark.parametrize(
        "refresh_value, expects_setup_call, expects_debug_message",
        [
            pytest.param(True, True, True, id="refresh_true_calls_setup"),
            pytest.param(False, False, False, id="refresh_false_no_setup"),
            pytest.param(None, False, False, id="default_no_setup"),
        ],
    )
    def test_get_handlers_refresh_scenarios(
        self,
        test_context: OrcaTestContext,
        refresh_value,
        expects_setup_call,
        expects_debug_message,
    ) -> None:
        """Test StructuralNavigator.get_handlers with various refresh scenarios."""
        essential_modules = self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_setup = test_context.Mock()
        test_context.patch_object(nav, "_setup_handlers", new=mock_setup)

        if refresh_value is None:
            handlers = nav.get_handlers()
        else:
            handlers = nav.get_handlers(refresh=refresh_value)

        assert isinstance(handlers, dict)

        if expects_setup_call:
            mock_setup.assert_called_once()
        else:
            mock_setup.assert_not_called()

        if expects_debug_message:
            essential_modules["orca.debug"].print_message.assert_any_call(
                essential_modules["orca.debug"].LEVEL_INFO,
                "STRUCTURAL NAVIGATOR: Refreshing handlers.",
                True,
                True,
            )

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._setup_handlers creates handler dictionary."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        nav._setup_handlers()
        assert isinstance(nav._handlers, dict)
        assert len(nav._handlers) > 0
        assert "structural_navigator_mode_cycle" in nav._handlers
        assert "previous_button" in nav._handlers
        assert "next_button" in nav._handlers
        assert "list_buttons" in nav._handlers

    def test_setup_handlers_creates_navigation_handlers(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test StructuralNavigator._setup_handlers creates expected navigation handlers."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        nav._setup_handlers()
        expected_prefixes = ["previous_", "next_", "list_"]
        expected_elements = [
            "blockquote",
            "button",
            "checkbox",
            "combobox",
            "entry",
            "form_field",
            "heading",
            "iframe",
            "image",
            "landmark",
            "list",
            "list_item",
            "live_region",
            "paragraph",
            "radio_button",
            "separator",
            "table",
            "link",
            "large_object",
            "clickable",
        ]
        for element in expected_elements:
            for prefix in expected_prefixes:
                if prefix == "list_" and element in ["separator"]:
                    continue
                handler_key = f"{prefix}{element}"
                if element == "list" and prefix == "list_":
                    handler_key = "list_lists"
                elif element == "list_item" and prefix == "list_":
                    handler_key = "list_list_items"
                if handler_key in nav._handlers:
                    assert nav._handlers[handler_key] is not None

    def test_setup_handlers_creates_heading_level_handlers(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test StructuralNavigator._setup_handlers creates heading level handlers."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        nav._setup_handlers()
        for level in range(1, 7):
            assert f"previous_heading_level_{level}" in nav._handlers
            assert f"next_heading_level_{level}" in nav._handlers
            assert f"list_headings_level_{level}" in nav._handlers

    @pytest.mark.parametrize(
        "current_mode, expected_next_mode, supports_collection",
        [
            pytest.param("OFF", "DOCUMENT", True, id="off_to_document"),
            pytest.param("DOCUMENT", "GUI", True, id="document_to_gui"),
            pytest.param("GUI", "OFF", False, id="gui_to_off"),
        ],
    )
    def test_cycle_mode_transitions(
        self, test_context: OrcaTestContext, current_mode, expected_next_mode, supports_collection
    ) -> None:
        """Test StructuralNavigator.cycle_mode transitions."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        current_nav_mode = getattr(NavigationMode, current_mode)
        expected_nav_mode = getattr(NavigationMode, expected_next_mode)

        mock_get_mode, mock_set_mode = self._setup_cycle_navigation_mode_mocks(
            test_context, nav, current_nav_mode, supports_collection=supports_collection
        )[:2]

        if supports_collection:
            essential_modules["orca.AXObject"].supports_collection.return_value = True

        result = nav.cycle_mode(mock_script, None, True)
        assert result is True
        mock_get_mode.assert_called_once_with(mock_script)
        mock_set_mode.assert_called_once_with(mock_script, expected_nav_mode)
        mock_script.present_message.assert_called()

    @pytest.mark.parametrize(
        "scenario, notify_user, is_active_script, expected_result, expects_message_call",
        [
            pytest.param("no_notify", False, True, True, False, id="no_notify_no_message"),
            pytest.param(
                "inactive_script", True, False, False, None, id="inactive_script_returns_false"
            ),
        ],
    )
    def test_cycle_mode_edge_scenarios(
        self,
        test_context: OrcaTestContext,
        scenario,
        notify_user,
        is_active_script,
        expected_result,
        expects_message_call,
    ) -> None:
        """Test StructuralNavigator.cycle_mode edge scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()

        if scenario == "no_notify":
            self._setup_cycle_navigation_mode_mocks(test_context, nav, NavigationMode.OFF)
            essential_modules["orca.AXObject"].supports_collection.return_value = True
        else:
            mock_is_active_script = test_context.Mock(return_value=is_active_script)
            test_context.patch_object(nav, "_is_active_script", new=mock_is_active_script)

        result = nav.cycle_mode(mock_script, None, notify_user)
        assert result is expected_result

        if expects_message_call is False:
            mock_script.present_message.assert_not_called()
        elif scenario == "inactive_script":
            mock_is_active_script.assert_called_once_with(mock_script)

    @pytest.mark.parametrize(
        "suspend_value, is_active, initial_suspended, expected_suspended, expects_debug, "
        "expects_refresh",
        [
            pytest.param(True, True, False, True, True, True, id="suspend_navigation"),
            pytest.param(False, True, True, False, True, True, id="resume_navigation"),
            pytest.param(
                True,
                False,
                False,
                False,
                False,
                False,
                id="inactive_script_no_change",
            ),
        ],
    )
    def test_suspend_commands_scenarios(
        self,
        test_context: OrcaTestContext,
        suspend_value,
        is_active,
        initial_suspended,
        expected_suspended,
        expects_debug,
        expects_refresh,
    ) -> None:
        """Test StructuralNavigator.suspend_commands various scenarios."""

        essential_modules = (
            self._setup_dependencies(test_context)
            if expects_debug
            else self._setup_dependencies(test_context)
        )
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        nav._suspended = initial_suspended
        test_context.patch_object(nav, "_is_active_script", return_value=is_active)
        mock_refresh = test_context.Mock()
        test_context.patch_object(nav, "refresh_bindings_and_grabs", new=mock_refresh)

        nav.suspend_commands(mock_script, suspend_value, "test reason")

        assert nav._suspended == expected_suspended

        if expects_debug:
            essential_modules["orca.debug"].print_message.assert_any_call(
                essential_modules["orca.debug"].LEVEL_INFO,
                f"STRUCTURAL NAVIGATOR: Suspended: {suspend_value}: test reason",
                True,
            )

        if expects_refresh:
            mock_refresh.assert_called_once_with(
                mock_script, f"Suspended changed to {suspend_value}"
            )
        else:
            mock_refresh.assert_not_called()

    def test_get_object_in_direction_empty_objects(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_object_in_direction with empty objects list."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav._get_object_in_direction(mock_script, [], True)
        assert result is None

    def test_get_object_in_direction_next_object(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_object_in_direction returns next object."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_obj1 = test_context.Mock()
        mock_obj2 = test_context.Mock()
        mock_obj3 = test_context.Mock()
        objects = [mock_obj1, mock_obj2, mock_obj3]

        essential_modules[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = mock_obj2
        essential_modules["orca.AXObject"].get_parent.return_value = mock_obj2

        def mock_get_path(obj):
            if obj == mock_obj1:
                return [0, 0]
            if obj == mock_obj2:
                return [0, 1]
            if obj == mock_obj3:
                return [0, 2]
            return []

        essential_modules["orca.AXObject"].get_path.side_effect = mock_get_path

        mock_script = test_context.Mock()

        def mock_path_comparison(path1, _path2):
            if path1 == [0, 0]:  # obj1
                return -1
            if path1 == [0, 1]:  # obj2
                return 0
            if path1 == [0, 2]:  # obj3
                return 1
            return 0

        mock_script.utilities.path_comparison.side_effect = mock_path_comparison

        result = nav._get_object_in_direction(mock_script, objects, True)
        assert result == mock_obj3

    def test_get_object_in_direction_previous_object(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_object_in_direction returns previous object."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_obj1 = test_context.Mock()
        mock_obj2 = test_context.Mock()
        mock_obj3 = test_context.Mock()
        objects = [mock_obj1, mock_obj2, mock_obj3]

        essential_modules[
            "orca.focus_manager"
        ].get_manager.return_value.get_locus_of_focus.return_value = mock_obj2
        essential_modules["orca.AXObject"].get_parent.return_value = mock_obj2

        def mock_get_path(obj):
            if obj == mock_obj1:
                return [0, 0]
            if obj == mock_obj2:
                return [0, 1]
            if obj == mock_obj3:
                return [0, 2]  # Later in tree
            return []

        essential_modules["orca.AXObject"].get_path.side_effect = mock_get_path

        mock_script = test_context.Mock()

        def mock_path_comparison(path1, _path2):
            if path1 == [0, 0]:  # obj1
                return -1
            if path1 == [0, 1]:  # obj2
                return 0
            if path1 == [0, 2]:  # obj3
                return 1
            return 0

        mock_script.utilities.path_comparison.side_effect = mock_path_comparison

        result = nav._get_object_in_direction(mock_script, objects, False)
        assert result == mock_obj1

    def test_get_object_in_direction_wrap_to_beginning(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_object_in_direction wraps to beginning when at end."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_result = test_context.Mock()
        mock_script = test_context.Mock()

        test_context.patch_object(nav, "_get_object_in_direction", return_value=mock_result)

        result = nav._get_object_in_direction(mock_script, [], True, True)
        assert result == mock_result

    def test_get_object_in_direction_wrap_to_end(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_object_in_direction wraps to end when at beginning."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_result = test_context.Mock()
        mock_script = test_context.Mock()

        test_context.patch_object(nav, "_get_object_in_direction", return_value=mock_result)

        result = nav._get_object_in_direction(mock_script, [], False, True)
        assert result == mock_result

    def test_get_object_in_direction_no_wrap_at_end(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_object_in_direction returns None at end when no wrap."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_script = test_context.Mock()

        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)

        result = nav._get_object_in_direction(mock_script, [], True, False)
        assert result is None

    def test_previous_button_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_button method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_get_buttons = test_context.Mock(return_value=[])
        test_context.patch_object(nav, "_get_all_buttons", new=mock_get_buttons)
        mock_get_in_direction = test_context.Mock(return_value=None)
        test_context.patch_object(nav, "_get_object_in_direction", new=mock_get_in_direction)
        mock_present = test_context.Mock()
        test_context.patch_object(nav, "_present_object", new=mock_present)
        result = nav.previous_button(mock_script, mock_event, True)
        assert result is True
        mock_get_buttons.assert_called_once_with(mock_script)
        mock_get_in_direction.assert_called_once()
        mock_present.assert_called_once()

    def test_next_button_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_button method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_get_buttons = test_context.Mock(return_value=[])
        test_context.patch_object(nav, "_get_all_buttons", new=mock_get_buttons)
        mock_get_in_direction = test_context.Mock(return_value=None)
        test_context.patch_object(nav, "_get_object_in_direction", new=mock_get_in_direction)
        mock_present = test_context.Mock()
        test_context.patch_object(nav, "_present_object", new=mock_present)
        result = nav.next_button(mock_script, mock_event, True)
        assert result is True
        mock_get_buttons.assert_called_once_with(mock_script)
        mock_get_in_direction.assert_called_once()
        mock_present.assert_called_once()

    def test_list_buttons_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.list_buttons method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_get_buttons = test_context.Mock(return_value=[])
        test_context.patch_object(nav, "_get_all_buttons", new=mock_get_buttons)
        mock_present = test_context.Mock()
        test_context.patch_object(nav, "_present_object_list", new=mock_present)
        result = nav.list_buttons(mock_script, mock_event)
        assert result is True
        mock_get_buttons.assert_called_once_with(mock_script)
        mock_present.assert_called_once()

    def test_get_bindings_refresh_true(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_bindings with refresh=True updates bindings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_setup = test_context.Mock()
        test_context.patch_object(nav, "_setup_bindings", new=mock_setup)
        bindings = nav.get_bindings(refresh=True)
        assert bindings.key_bindings is not None
        essential_modules["orca.debug"].print_message.assert_any_call(
            essential_modules["orca.debug"].LEVEL_INFO,
            "STRUCTURAL NAVIGATOR: Refreshing bindings. Is desktop: True",
            True,
        )
        mock_setup.assert_called_once()

    def test_get_bindings_refresh_false(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_bindings with refresh=False returns cached bindings."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_bindings = test_context.Mock()
        mock_bindings.key_bindings = []
        test_context.patch_object(nav, "get_bindings", return_value=mock_bindings)

        bindings = nav.get_bindings(refresh=False)
        assert bindings.key_bindings is not None
        assert bindings == mock_bindings

    def test_setup_bindings(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._setup_bindings creates keybindings."""
        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_bindings = test_context.Mock()
        mock_bindings.key_bindings = []

        def mock_setup_bindings():
            nav._bindings = mock_bindings

        test_context.patch_object(nav, "_setup_bindings", new=mock_setup_bindings)
        nav._setup_bindings()
        assert nav._bindings.key_bindings is not None
        assert nav._bindings == mock_bindings

    @pytest.mark.parametrize(
        "is_same_script,expected",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_is_active_script(
        self, test_context: OrcaTestContext, is_same_script: bool, expected: bool
    ) -> None:
        """Test StructuralNavigator._is_active_script with active and inactive scripts."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_active_script = mock_script if is_same_script else test_context.Mock()
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_active_script
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav._is_active_script(mock_script)
        assert result is expected

    def test_get_mode_default(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_mode returns default mode for new script."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        result = nav.get_mode(mock_script)
        assert result == NavigationMode.OFF

    def test_get_mode_cached(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_mode returns cached mode for known script."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        nav._mode_for_script[mock_script] = NavigationMode.DOCUMENT
        result = nav.get_mode(mock_script)
        assert result == NavigationMode.DOCUMENT

    def test_set_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_mode sets mode for script."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        nav.set_mode(mock_script, NavigationMode.GUI)
        assert nav._mode_for_script[mock_script] == NavigationMode.GUI

    def test_determine_root_container_document_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._determine_root_container for document mode."""
        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_focus = test_context.Mock()
        mock_document = test_context.Mock()

        essential_modules[
            "orca.focus_manager"
        ].get_manager().get_locus_of_focus.return_value = mock_focus
        essential_modules["orca.AXObject"].find_ancestor_inclusive.side_effect = (
            lambda focus, predicate: None
        )
        mock_script.utilities.get_top_level_document_for_object.return_value = mock_document

        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_determine_root_container", return_value=mock_document)

        result = nav._determine_root_container(mock_script)
        assert result == mock_document

    def test_determine_root_container_fallback(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._determine_root_container fallback to app."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        mock_script.app = mock_app
        essential_modules["orca.AXUtilities"].is_web_application.return_value = False
        essential_modules["orca.AXObject"].find_ancestor_inclusive.return_value = mock_app
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_determine_root_container", return_value=mock_app)
        result = nav._determine_root_container(mock_script)
        assert result == mock_app

    @pytest.mark.parametrize(
        "element_type,ax_method",
        [
            pytest.param("buttons", "find_all_buttons", id="get_all_buttons"),
            pytest.param("headings", "find_all_headings", id="get_all_headings"),
            pytest.param("links", "find_all_links", id="get_all_links"),
            pytest.param("tables", "find_all_tables", id="get_all_tables"),
            pytest.param("lists", "find_all_lists", id="get_all_lists"),
            pytest.param("checkboxes", "find_all_check_boxes", id="get_all_checkboxes"),
            pytest.param("entries", "find_all_editable_objects", id="get_all_entries"),
            pytest.param("form_fields", "find_all_form_fields", id="get_all_form_fields"),
            pytest.param("images", "find_all_images_and_image_maps", id="get_all_images"),
            pytest.param("landmarks", "find_all_landmarks", id="get_all_landmarks"),
            pytest.param("paragraphs", "find_all_paragraphs", id="get_all_paragraphs"),
        ],
    )
    def test_get_all_elements(
        self,
        test_context: OrcaTestContext,
        element_type: str,
        ax_method: str,
    ) -> None:
        """Test StructuralNavigator._get_all_* methods with various element types."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_elements = [test_context.Mock(), test_context.Mock()]

        if element_type == "lists":
            test_context.patch(
                f"orca.structural_navigator.AXUtilities.{ax_method}",
                side_effect=lambda root,
                include_description_lists=False,
                include_tab_lists=False,
                pred=None: mock_elements,
            )
        elif element_type == "paragraphs":
            test_context.patch(
                f"orca.structural_navigator.AXUtilities.{ax_method}",
                side_effect=lambda root, include_items=False, pred=None: mock_elements,
            )
        else:
            test_context.patch(
                f"orca.structural_navigator.AXUtilities.{ax_method}",
                side_effect=lambda root, pred=None: mock_elements,
            )

        if element_type in ["links", "entries", "images"]:
            mock_root = test_context.Mock()
            test_context.patch_object(
                nav, "_determine_root_container", side_effect=lambda script: mock_root
            )

        navigation_method = getattr(nav, f"_get_all_{element_type}")
        result = navigation_method(mock_script)
        assert result == mock_elements

    def test_get_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_mode method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        result = nav.get_mode(mock_script)
        assert result == NavigationMode.OFF

    def test_last_input_event_was_navigation_command(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.last_input_event_was_navigation_command method."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.input_event_manager"
        ].get_manager().last_event_equals_or_is_release_for_event.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_event = test_context.Mock()
        mock_event.as_single_line_string = test_context.Mock(return_value="mock event")
        nav._last_input_event = mock_event

        result = nav.last_input_event_was_navigation_command()
        assert isinstance(result, bool)
        assert result is True

    def test_get_state_string(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_state_string method."""

        essential_modules = self._setup_dependencies(test_context)
        mock_obj = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        essential_modules["orca.AXObject"].get_state_set.return_value = None
        essential_modules["orca.AXUtilities"].is_switch.return_value = False
        essential_modules["orca.AXUtilities"].is_checked.return_value = False
        essential_modules["orca.AXUtilities"].is_expanded.return_value = False
        essential_modules["orca.AXUtilities"].is_pressed.return_value = False
        essential_modules["orca.AXUtilities"].is_selected.return_value = False
        test_context.patch_object(nav, "_get_state_string", return_value="test state")
        result = nav._get_state_string(mock_obj)
        assert isinstance(result, str)
        assert result == "test state"

    def test_get_item_string(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._get_item_string method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(
            nav, "_get_item_string", return_value="Test Object: Test Description"
        )
        result = nav._get_item_string(mock_script, mock_obj)
        assert isinstance(result, str)
        assert "Test Description" in result

    def test_is_non_document_object(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator._is_non_document_object method."""

        essential_modules = self._setup_dependencies(test_context)
        mock_obj = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        essential_modules["orca.AXUtilities"].is_application.return_value = False
        essential_modules["orca.AXUtilities"].is_document.return_value = False
        essential_modules["orca.AXUtilities"].is_frame.return_value = False
        essential_modules["orca.AXObject"].get_role.return_value = None
        result = nav._is_non_document_object(mock_obj)
        assert isinstance(result, bool)

    def test_add_bindings(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.add_bindings method."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules["orca.debug"].debugLevel = 0
        mock_script = test_context.Mock()
        mock_key_bindings = test_context.Mock()
        mock_key_bindings.get_bindings_with_grabs_for_debugging.return_value = []
        mock_script.get_key_bindings.return_value = mock_key_bindings
        mock_script.key_bindings = mock_key_bindings
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_bindings = test_context.Mock()
        mock_bindings.key_bindings = []
        nav._bindings = mock_bindings
        test_context.patch_object(nav, "_is_active_script", return_value=True)
        test_context.patch_object(nav, "get_bindings", return_value=mock_bindings)
        nav.add_bindings(mock_script, "test")
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_remove_bindings(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.remove_bindings method."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules["orca.debug"].debugLevel = 0
        mock_script = test_context.Mock()
        mock_key_bindings = test_context.Mock()
        mock_key_bindings.get_bindings_with_grabs_for_debugging.return_value = []
        mock_script.get_key_bindings.return_value = mock_key_bindings
        mock_script.key_bindings = mock_key_bindings
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_bindings = test_context.Mock()
        mock_bindings.key_bindings = []
        nav._bindings = mock_bindings
        test_context.patch_object(nav, "_is_active_script", return_value=True)
        nav.remove_bindings(mock_script, "test")
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_refresh_bindings_and_grabs(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.refresh_bindings_and_grabs method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_is_active_script", return_value=True)
        test_context.patch_object(nav, "remove_bindings", new=test_context.Mock())
        test_context.patch_object(nav, "add_bindings", new=test_context.Mock())
        nav.refresh_bindings_and_grabs(mock_script, "test")

    def test_previous_heading_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_heading method."""
        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_headings", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_heading(mock_script, mock_event, True)
        assert result is True

    def test_next_heading_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_heading method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_headings", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_heading(mock_script, mock_event, True)
        assert result is True

    def test_list_headings_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.list_headings method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_headings", return_value=[])
        test_context.patch_object(nav, "_present_object_list", new=test_context.Mock())
        result = nav.list_headings(mock_script, mock_event)
        assert result is True

    def test_previous_link_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_link method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_links", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_link(mock_script, mock_event, True)
        assert result is True

    def test_next_link_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_link method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_links", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_link(mock_script, mock_event, True)
        assert result is True

    def test_list_links_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.list_links method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_links", return_value=[])
        test_context.patch_object(nav, "_present_object_list", new=test_context.Mock())
        result = nav.list_links(mock_script, mock_event)
        assert result is True

    def test_previous_table_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_table method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_tables", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_table(mock_script, mock_event, True)
        assert result is True

    def test_next_table_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_table method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_tables", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_table(mock_script, mock_event, True)
        assert result is True

    def test_list_tables_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.list_tables method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_tables", return_value=[])
        test_context.patch_object(nav, "_present_object_list", new=test_context.Mock())
        result = nav.list_tables(mock_script, mock_event)
        assert result is True

    def test_previous_list_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_list method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_lists", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_list(mock_script, mock_event, True)
        assert result is True

    def test_next_list_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_list method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_lists", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_list(mock_script, mock_event, True)
        assert result is True

    def test_list_lists_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.list_lists method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_lists", return_value=[])
        test_context.patch_object(nav, "_present_object_list", new=test_context.Mock())
        result = nav.list_lists(mock_script, mock_event)
        assert result is True

    def test_previous_blockquote_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_blockquote method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_blockquotes", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_blockquote(mock_script, mock_event, True)
        assert result is True

    def test_next_blockquote_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_blockquote method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_blockquotes", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_blockquote(mock_script, mock_event, True)
        assert result is True

    def test_previous_checkbox_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_checkbox method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_checkboxes", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_checkbox(mock_script, mock_event, True)
        assert result is True

    def test_next_checkbox_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_checkbox method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_checkboxes", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_checkbox(mock_script, mock_event, True)
        assert result is True

    def test_previous_entry_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_entry method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_entries", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_entry(mock_script, mock_event, True)
        assert result is True

    def test_next_entry_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_entry method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_entries", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_entry(mock_script, mock_event, True)
        assert result is True

    def test_previous_form_field_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_form_field method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_form_fields", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_form_field(mock_script, mock_event, True)
        assert result is True

    def test_next_form_field_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_form_field method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_form_fields", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_form_field(mock_script, mock_event, True)
        assert result is True

    def test_previous_image_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_image method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_images", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_image(mock_script, mock_event, True)
        assert result is True

    def test_next_image_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_image method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_images", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_image(mock_script, mock_event, True)
        assert result is True

    def test_previous_landmark_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_landmark method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_landmarks", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_landmark(mock_script, mock_event, True)
        assert result is True

    def test_next_landmark_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_landmark method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_landmarks", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_landmark(mock_script, mock_event, True)
        assert result is True

    def test_previous_paragraph_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.previous_paragraph method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_paragraphs", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.previous_paragraph(mock_script, mock_event, True)
        assert result is True

    def test_next_paragraph_method(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.next_paragraph method."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_get_all_paragraphs", return_value=[])
        test_context.patch_object(nav, "_get_object_in_direction", return_value=None)
        test_context.patch_object(nav, "_present_object", new=test_context.Mock())
        result = nav.next_paragraph(mock_script, mock_event, True)
        assert result is True

    @pytest.mark.parametrize(
        "expected_next_method,expected_prev_method",
        [
            pytest.param("next_heading_level_1", "previous_heading_level_1", id="heading_level_1"),
            pytest.param("next_heading_level_2", "previous_heading_level_2", id="heading_level_2"),
            pytest.param("next_heading_level_3", "previous_heading_level_3", id="heading_level_3"),
            pytest.param("next_heading_level_4", "previous_heading_level_4", id="heading_level_4"),
            pytest.param("next_heading_level_5", "previous_heading_level_5", id="heading_level_5"),
            pytest.param("next_heading_level_6", "previous_heading_level_6", id="heading_level_6"),
        ],
    )
    def test_heading_level_navigation_methods_exist(
        self,
        test_context: OrcaTestContext,
        expected_next_method: str,
        expected_prev_method: str,
    ) -> None:
        """Test StructuralNavigator has navigation methods for each heading level."""

        essential_modules = test_context.setup_shared_dependencies(
            [
                "orca.keybindings",
                "orca.settings_manager",
                "orca.dbus_service",
                "orca.debug",
                "orca.focus_manager",
                "orca.AXObject",
                "orca.AXUtilities",
            ]
        )
        self._setup_mocks(test_context, essential_modules)

        from orca.structural_navigator import StructuralNavigator

        navigator = StructuralNavigator()
        assert hasattr(navigator, expected_next_method)
        assert hasattr(navigator, expected_prev_method)
        assert callable(getattr(navigator, expected_next_method))
        assert callable(getattr(navigator, expected_prev_method))

    @pytest.mark.parametrize(
        "mode_value",
        [
            pytest.param("OFF", id="off_mode"),
            pytest.param("DOCUMENT", id="document_mode"),
            pytest.param("GUI", id="gui_mode"),
        ],
    )
    def test_navigation_mode_values(
        self,
        test_context: OrcaTestContext,
        mode_value: str,
    ) -> None:
        """Test NavigationMode enum values."""

        essential_modules = test_context.setup_shared_dependencies(
            [
                "orca.keybindings",
                "orca.settings_manager",
                "orca.dbus_service",
                "orca.debug",
                "orca.focus_manager",
                "orca.AXObject",
                "orca.AXUtilities",
            ]
        )
        self._setup_mocks(test_context, essential_modules)

        from orca.structural_navigator import NavigationMode

        if mode_value == "OFF":
            assert NavigationMode.OFF.value == "OFF"
        elif mode_value == "DOCUMENT":
            assert NavigationMode.DOCUMENT.value == "DOCUMENT"
        elif mode_value == "GUI":
            assert NavigationMode.GUI.value == "GUI"

    def test_basic_structural_navigator_state(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator basic state management."""

        essential_modules = test_context.setup_shared_dependencies(
            [
                "orca.keybindings",
                "orca.settings_manager",
                "orca.dbus_service",
                "orca.debug",
                "orca.focus_manager",
                "orca.AXObject",
                "orca.AXUtilities",
            ]
        )
        self._setup_mocks(test_context, essential_modules)

        from orca.structural_navigator import StructuralNavigator

        navigator = StructuralNavigator()
        assert navigator._last_input_event is None
        assert navigator._suspended is False
        assert isinstance(navigator._mode_for_script, dict)

    def test_get_is_enabled(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_is_enabled returns setting value."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav.get_is_enabled()
        assert result is True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.assert_called_with("structuralNavigationEnabled")

    def test_set_is_enabled_no_change(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_is_enabled returns early if value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav.set_is_enabled(True)
        assert result is True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_setting.assert_not_called()

    def test_set_is_enabled_true_with_previous_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_is_enabled restores previous mode when enabling."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = False
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        nav._previous_mode_for_script[mock_script] = NavigationMode.DOCUMENT
        test_context.patch_object(nav, "_is_active_script", return_value=True)
        mock_refresh = test_context.Mock()
        test_context.patch_object(nav, "refresh_bindings_and_grabs", new=mock_refresh)

        result = nav.set_is_enabled(True)
        assert result is True
        assert nav._mode_for_script[mock_script] == NavigationMode.DOCUMENT
        mock_refresh.assert_called_once()

    def test_set_is_enabled_true_without_previous_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_is_enabled without previous mode when enabling."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = False
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        test_context.patch_object(nav, "_is_active_script", return_value=True)
        mock_refresh = test_context.Mock()
        test_context.patch_object(nav, "refresh_bindings_and_grabs", new=mock_refresh)

        result = nav.set_is_enabled(True)
        assert result is True
        mock_refresh.assert_called_once()

    def test_set_is_enabled_false_saves_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_is_enabled saves current mode when disabling."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        nav._mode_for_script[mock_script] = NavigationMode.DOCUMENT
        test_context.patch_object(nav, "_is_active_script", return_value=True)
        mock_refresh = test_context.Mock()
        test_context.patch_object(nav, "refresh_bindings_and_grabs", new=mock_refresh)

        result = nav.set_is_enabled(False)
        assert result is True
        assert nav._previous_mode_for_script[mock_script] == NavigationMode.DOCUMENT
        assert nav._mode_for_script[mock_script] == NavigationMode.OFF
        mock_refresh.assert_called_once()

    def test_set_is_enabled_false_already_off(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_is_enabled returns early if already OFF."""

        essential_modules = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        essential_modules[
            "orca.script_manager"
        ].get_manager.return_value.get_active_script.return_value = mock_script
        from orca.structural_navigator import get_navigator, NavigationMode

        nav = get_navigator()
        nav._mode_for_script[mock_script] = NavigationMode.OFF
        mock_refresh = test_context.Mock()
        test_context.patch_object(nav, "refresh_bindings_and_grabs", new=mock_refresh)

        result = nav.set_is_enabled(False)
        assert result is True
        mock_refresh.assert_not_called()

    def test_get_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.get_triggers_focus_mode returns setting value."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = False
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav.get_triggers_focus_mode()
        assert result is False
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.assert_called_with("structNavTriggersFocusMode")

    def test_set_triggers_focus_mode(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_triggers_focus_mode updates setting."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav.set_triggers_focus_mode(False)
        assert result is True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_setting.assert_called_with(
            "structNavTriggersFocusMode", False
        )

    def test_set_triggers_focus_mode_no_change(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.set_triggers_focus_mode returns early if unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        result = nav.set_triggers_focus_mode(True)
        assert result is True
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.set_setting.assert_not_called()

    def test_last_command_prevents_focus_mode_true(self, test_context: OrcaTestContext) -> None:
        """Test StructuralNavigator.last_command_prevents_focus_mode returns True."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = False
        essential_modules[
            "orca.input_event_manager"
        ].get_manager.return_value.last_event_equals_or_is_release_for_event.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_event = test_context.Mock()
        nav._last_input_event = mock_event
        result = nav.last_command_prevents_focus_mode()
        assert result is True

    def test_last_command_prevents_focus_mode_false_no_event(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test StructuralNavigator.last_command_prevents_focus_mode returns False if no event."""

        self._setup_dependencies(test_context)
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        nav._last_input_event = None
        result = nav.last_command_prevents_focus_mode()
        assert result is False

    def test_last_command_prevents_focus_mode_false_setting_true(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test StructuralNavigator.last_command_prevents_focus_mode returns False if setting True."""

        essential_modules = self._setup_dependencies(test_context)
        essential_modules[
            "orca.settings_manager"
        ].get_manager.return_value.get_setting.return_value = True
        from orca.structural_navigator import get_navigator

        nav = get_navigator()
        mock_event = test_context.Mock()
        nav._last_input_event = mock_event
        result = nav.last_command_prevents_focus_mode()
        assert result is False
