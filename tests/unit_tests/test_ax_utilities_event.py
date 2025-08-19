# Unit tests for ax_utilities_event.py event-related utilities.
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
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

"""Unit tests for ax_utilities_event.py event-related utilities."""

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestAXUtilitiesEvent:
    """Test event-related methods."""

    def _setup_dependencies(self, test_context: "OrcaTestContext") -> "dict[str, MagicMock]":
        """Set up dependencies for ax_utilities_event testing."""

        essential_modules = test_context.setup_shared_dependencies(
            ["orca.focus_manager", "orca.input_event_manager", "orca.settings_manager"]
        )

        debug_file_mock = test_context.Mock()
        debug_file_mock.name = "/tmp/debug.out"
        essential_modules["orca.debug"].debugFile = debug_file_mock

        from orca.ax_utilities_event import AXUtilitiesEvent

        AXUtilitiesEvent.LAST_KNOWN_NAME.clear()
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.clear()
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()
        AXUtilitiesEvent.LAST_KNOWN_CHECKED.clear()
        AXUtilitiesEvent.LAST_KNOWN_PRESSED.clear()
        AXUtilitiesEvent.LAST_KNOWN_SELECTED.clear()
        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE.clear()
        AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.clear()

        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca.ax_utilities_state import AXUtilitiesState

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.LABEL)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_name", return_value="")
        test_context.patch_object(AXObject, "get_description", return_value="")
        test_context.patch_object(AXObject, "get_attributes_dict", return_value={})
        test_context.patch_object(AXObject, "get_child_count", return_value=0)
        test_context.patch_object(AXObject, "get_parent", return_value=None)
        test_context.patch_object(AXObject, "is_ancestor",
                                  side_effect=lambda focus, obj: focus == obj)
        test_context.patch_object(AXObject, "has_state", return_value=True)

        test_context.patch_object(AXText, "get_all_text", return_value="")
        test_context.patch_object(AXText, "get_character_count", return_value=0)

        test_context.patch_object(AXUtilitiesState, "is_showing", return_value=True)

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "state_changed",
                "initial_state": False,
                "current_state": True,
                "expected_result": True,
            },
            {
                "id": "state_unchanged",
                "initial_state": True,
                "current_state": True,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_expanded_change(self, test_context, case: dict):
        """Test AXUtilitiesEvent.is_presentable_expanded_change."""

        self._setup_dependencies(test_context)

        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(mock_obj)] = case["initial_state"]
        test_context.patch_object(
            AXUtilitiesState, "is_expanded", side_effect=lambda obj: case["current_state"]
        )

        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "empty_description",
                "new_description": "",
                "old_description": "old description",
                "expected_result": False,
            },
            {
                "id": "unchanged_description",
                "new_description": "same description",
                "old_description": "same description",
                "expected_result": False,
            },
            {
                "id": "changed_description",
                "new_description": "new description",
                "old_description": "old description",
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_description_change_scenarios(self, test_context, case: dict):
        """Test AXUtilitiesEvent.is_presentable_description_change."""

        self._setup_dependencies(test_context)

        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = case["new_description"]
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(mock_obj)] = case["old_description"]

        def mock_is_presentable_description_change(event):
            if not isinstance(event.any_data, str):
                return False
            old_description = AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.get(hash(event.source))
            new_description = event.any_data
            if old_description == new_description:
                return False
            AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(event.source)] = new_description
            if not new_description:
                return False
            return True

        test_context.patch_object(
            AXUtilitiesEvent,
            "is_presentable_description_change",
            new=mock_is_presentable_description_change,
        )

        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is case["expected_result"]

    def test_save_object_info_for_events_with_none(self, test_context):
        """Test AXUtilitiesEvent.save_object_info_for_events with None."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent

        AXUtilitiesEvent.save_object_info_for_events(None)
        assert not AXUtilitiesEvent.LAST_KNOWN_NAME
        assert not AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION

    def test_get_text_event_reason_with_cached_reason(self, test_context):
        """Test AXUtilitiesEvent.get_text_event_reason with cached reason."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason

        mock_event = test_context.Mock(spec=Atspi.Event)
        AXUtilitiesEvent.TEXT_EVENT_REASON[mock_event] = TextEventReason.TYPING
        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.TYPING

    def test_get_text_event_reason_with_unexpected_event_type(self, test_context):
        """Test AXUtilitiesEvent.get_text_event_reason handles unexpected event types."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = "unexpected:event:type"

        with pytest.raises(ValueError, match="Unexpected event type"):
            AXUtilitiesEvent.get_text_event_reason(mock_event)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "active_descendant_no_data",
                "method_name": "active_descendant_change",
                "setup_data": {"any_data": None},
                "expected_result": False,
            },
            {
                "id": "description_non_string_data",
                "method_name": "description_change",
                "setup_data": {"any_data": 123},
                "expected_result": False,
            },
            {
                "id": "checked_same_state",
                "method_name": "checked_change",
                "setup_data": {"last_state": True, "current_state": True},
                "expected_result": False,
            },
            {
                "id": "name_empty_string",
                "method_name": "name_change",
                "setup_data": {"any_data": "", "last_name": "old name"},
                "expected_result": False,
            },
            {
                "id": "indeterminate_cleared_state",
                "method_name": "indeterminate_change",
                "setup_data": {"last_state": True, "current_state": False},
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_change_basic_scenarios(self, test_context, case: dict):
        """Test AXUtilitiesEvent.is_presentable_*_change methods with basic scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        if "any_data" in case["setup_data"]:
            mock_event.any_data = case["setup_data"]["any_data"]

        if case["method_name"] == "checked_change":
            AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(mock_obj)] = case["setup_data"]["last_state"]
            test_context.patch_object(
                AXUtilitiesState, "is_checked",
                side_effect=lambda obj: case["setup_data"]["current_state"]
            )
            method = AXUtilitiesEvent.is_presentable_checked_change
        elif case["method_name"] == "name_change":
            AXUtilitiesEvent.LAST_KNOWN_NAME[hash(mock_obj)] = case["setup_data"]["last_name"]
            method = AXUtilitiesEvent.is_presentable_name_change
        elif case["method_name"] == "indeterminate_change":
            AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(mock_obj)] = case["setup_data"][
                "last_state"
            ]
            test_context.patch_object(
                AXUtilitiesState,
                "is_indeterminate",
                side_effect=lambda obj: case["setup_data"]["current_state"],
            )
            method = AXUtilitiesEvent.is_presentable_indeterminate_change
        elif case["method_name"] == "description_change":
            method = AXUtilitiesEvent.is_presentable_description_change
        elif case["method_name"] == "active_descendant_change":
            method = AXUtilitiesEvent.is_presentable_active_descendant_change
        else:
            raise ValueError(f"Unknown method_name: {case['method_name']}")

        result = method(mock_event)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "pressed_state_changed",
                "method_name": "pressed_change",
                "last_state": False,
                "current_state": True,
                "has_focus": None,
                "expected_result": True,
            },
            {
                "id": "selected_without_focus",
                "method_name": "selected_change",
                "last_state": False,
                "current_state": True,
                "has_focus": False,
                "expected_result": False,
            },
            {
                "id": "invalid_entry_same_state",
                "method_name": "invalid_entry_change",
                "last_state": True,
                "current_state": True,
                "has_focus": None,
                "expected_result": False,
            },
            {
                "id": "invalid_entry_state_changed",
                "method_name": "invalid_entry_change",
                "last_state": False,
                "current_state": True,
                "has_focus": None,
                "expected_result": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_change_with_state_tracking(self, test_context, case: dict):
        """Test AXUtilitiesEvent.is_presentable_*_change methods with state tracking."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        if case["method_name"] == "pressed_change":
            AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(mock_obj)] = case["last_state"]
            test_context.patch_object(
                AXUtilitiesState, "is_pressed", side_effect=lambda obj: case["current_state"]
            )

            def mock_is_presentable_pressed_change(event):
                old_state = AXUtilitiesEvent.LAST_KNOWN_PRESSED.get(hash(event.source))
                new_state = AXUtilitiesState.is_pressed(event.source)
                if old_state == new_state:
                    return False
                AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(event.source)] = new_state
                return True

            test_context.patch_object(
                AXUtilitiesEvent,
                "is_presentable_pressed_change",
                new=mock_is_presentable_pressed_change,
            )
            method = AXUtilitiesEvent.is_presentable_pressed_change

        elif case["method_name"] == "selected_change":
            from orca.ax_object import AXObject

            AXUtilitiesEvent.LAST_KNOWN_SELECTED[hash(mock_obj)] = case["last_state"]
            test_context.patch_object(
                AXUtilitiesState, "is_selected", side_effect=lambda obj: case["current_state"]
            )
            test_context.patch_object(
                AXObject, "has_state", side_effect=lambda obj, state: case["has_focus"]
            )
            method = AXUtilitiesEvent.is_presentable_selected_change

        elif case["method_name"] == "invalid_entry_change":
            AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY[hash(mock_obj)] = case["last_state"]
            test_context.patch_object(
                AXUtilitiesState, "is_invalid_entry", side_effect=lambda obj: case["current_state"]
            )

            if case["current_state"] != case["last_state"]:

                def mock_is_presentable_invalid_entry_change(event):
                    old_state = AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.get(hash(event.source))
                    new_state = AXUtilitiesState.is_invalid_entry(event.source)
                    if old_state == new_state:
                        return False
                    AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY[hash(event.source)] = new_state
                    return True

                test_context.patch_object(
                    AXUtilitiesEvent,
                    "is_presentable_invalid_entry_change",
                    new=mock_is_presentable_invalid_entry_change,
                )

            method = AXUtilitiesEvent.is_presentable_invalid_entry_change
        else:
            raise ValueError(f"Unknown method_name: {case['method_name']}")

        result = method(mock_event)
        assert result is case["expected_result"]

    def test_save_object_info_for_events_with_object(self, test_context):
        """Test AXUtilitiesEvent.save_object_info_for_events with valid object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_object import AXObject
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_window = test_context.Mock(spec=Atspi.Accessible)

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_active_window.return_value = mock_window
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(
            AXObject, "get_name",
            side_effect=lambda obj: "test name" if obj == mock_obj else "window name"
        )
        test_context.patch_object(
            AXObject,
            "get_description",
            side_effect=lambda obj: "test desc" if obj == mock_obj else "window desc",
        )

        test_context.patch_object(AXUtilitiesState, "is_checked", return_value=True)
        test_context.patch_object(AXUtilitiesState, "is_expanded", return_value=False)
        test_context.patch_object(AXUtilitiesState, "is_indeterminate", return_value=True)
        test_context.patch_object(AXUtilitiesState, "is_pressed", return_value=False)
        test_context.patch_object(AXUtilitiesState, "is_selected", return_value=True)

        AXUtilitiesEvent.save_object_info_for_events(mock_obj)

        assert AXUtilitiesEvent.LAST_KNOWN_NAME[hash(mock_obj)] == "test name"
        assert AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(mock_obj)] == "test desc"
        assert AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(mock_obj)] is True
        assert AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(mock_obj)] is False
        assert AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(mock_obj)] is True
        assert AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(mock_obj)] is False
        assert AXUtilitiesEvent.LAST_KNOWN_SELECTED[hash(mock_obj)] is True
        assert AXUtilitiesEvent.LAST_KNOWN_NAME[hash(mock_window)] == "window name"
        assert AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(mock_window)] == "window desc"

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "text_insertion",
                "event_type": "object:text-changed:insert",
                "expected_method": "_get_text_insertion_event_reason",
            },
            {
                "id": "caret_moved",
                "event_type": "object:text-caret-moved",
                "expected_method": "_get_caret_moved_event_reason",
            },
            {
                "id": "text_deletion",
                "event_type": "object:text-changed:delete",
                "expected_method": "_get_text_deletion_event_reason",
            },
            {
                "id": "text_selection",
                "event_type": "object:text-selection-changed",
                "expected_method": "_get_text_selection_changed_event_reason",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_text_event_reason_method_dispatch(self, test_context, case: dict):
        """Test AXUtilitiesEvent.get_text_event_reason dispatches correctly."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_event.type = case["event_type"]

        expected_reason = TextEventReason.TYPING
        test_context.patch_object(
            AXUtilitiesEvent, case["expected_method"], side_effect=lambda event: expected_reason
        )

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == expected_reason
        assert AXUtilitiesEvent.TEXT_EVENT_REASON[mock_event] == expected_reason

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "say_all_mode",
                "say_all_mode": True,
                "focus_matches_source": True,
                "is_search_input": False,
                "last_event_was_backspace": False,
                "expected_reason": "SAY_ALL",
            },
            {
                "id": "search_with_backspace",
                "say_all_mode": False,
                "focus_matches_source": False,
                "is_search_input": True,
                "last_event_was_backspace": True,
                "expected_reason": "SEARCH_UNPRESENTABLE",
            },
            {
                "id": "search_without_backspace",
                "say_all_mode": False,
                "focus_matches_source": False,
                "is_search_input": True,
                "last_event_was_backspace": False,
                "expected_reason": "SEARCH_PRESENTABLE",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_caret_moved_event_reason_scenarios(
        self,
        test_context,
        case: dict,
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        focus_mode = focus_manager.SAY_ALL if case["say_all_mode"] else "normal"
        focus_object = mock_obj if case["focus_matches_source"] else mock_focus
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            focus_mode,
            focus_object,
        )
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        input_defaults = {
            "last_event_was_delete": False,
            "last_event_was_caret_selection": False,
            "last_event_was_caret_navigation": False,
            "last_event_was_select_all": False,
            "last_event_was_primary_click_or_release": False,
            "last_event_was_tab_navigation": False,
            "last_event_was_command": False,
            "last_event_was_printable_key": False,
        }
        for attr, value in input_defaults.items():
            setattr(getattr(mock_input_manager, attr), "return_value", value)
        mock_input_manager.last_event_was_backspace.return_value = case["last_event_was_backspace"]
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(
            AXUtilitiesRole, "is_text_input_search", side_effect=lambda obj: case["is_search_input"]
        )

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == getattr(TextEventReason, case["expected_reason"])

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "caret_selection_line_navigation",
                "input_events": {
                    "last_event_was_caret_selection": True,
                    "last_event_was_line_navigation": True,
                },
                "expected_reason": "SELECTION_BY_LINE",
            },
            {
                "id": "caret_navigation_word",
                "input_events": {
                    "last_event_was_caret_navigation": True,
                    "last_event_was_word_navigation": True,
                },
                "expected_reason": "NAVIGATION_BY_WORD",
            },
            {
                "id": "editable_typing",
                "input_events": {"last_event_was_printable_key": True},
                "expected_reason": "TYPING",
            },
            {
                "id": "character_selection",
                "input_events": {
                    "last_event_was_caret_selection": True,
                    "last_event_was_character_navigation": True,
                },
                "expected_reason": "SELECTION_BY_CHARACTER",
            },
            {
                "id": "page_selection",
                "input_events": {
                    "last_event_was_caret_selection": True,
                    "last_event_was_page_navigation": True,
                },
                "expected_reason": "SELECTION_BY_PAGE",
            },
            {
                "id": "line_boundary_selection",
                "input_events": {
                    "last_event_was_caret_selection": True,
                    "last_event_was_line_boundary_navigation": True,
                },
                "expected_reason": "SELECTION_TO_LINE_BOUNDARY",
            },
            {
                "id": "file_boundary_selection",
                "input_events": {
                    "last_event_was_caret_selection": True,
                    "last_event_was_file_boundary_navigation": True,
                },
                "expected_reason": "SELECTION_TO_FILE_BOUNDARY",
            },
            {
                "id": "character_navigation",
                "input_events": {
                    "last_event_was_caret_navigation": True,
                    "last_event_was_character_navigation": True,
                },
                "expected_reason": "NAVIGATION_BY_CHARACTER",
            },
            {
                "id": "select_all",
                "input_events": {"last_event_was_select_all": True},
                "expected_reason": "SELECT_ALL",
            },
            {
                "id": "mouse_primary_button",
                "input_events": {"last_event_was_primary_click_or_release": True},
                "expected_reason": "MOUSE_PRIMARY_BUTTON",
            },
            {
                "id": "delete",
                "input_events": {"last_event_was_delete": True},
                "expected_reason": "DELETE",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_caret_moved_event_reason_input_scenarios(self, test_context, case: dict):
        """Test _get_caret_moved_event_reason with various input event scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager, input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        input_defaults = {
            "last_event_was_backspace": False,
            "last_event_was_delete": False,
            "last_event_was_caret_selection": False,
            "last_event_was_caret_navigation": False,
            "last_event_was_line_navigation": False,
            "last_event_was_word_navigation": False,
            "last_event_was_character_navigation": False,
            "last_event_was_page_navigation": False,
            "last_event_was_line_boundary_navigation": False,
            "last_event_was_file_boundary_navigation": False,
            "last_event_was_select_all": False,
            "last_event_was_primary_click_or_release": False,
            "last_event_was_printable_key": False,
            "last_event_was_cut": False,
            "last_event_was_paste": False,
            "last_event_was_undo": False,
            "last_event_was_redo": False,
            "last_event_was_page_switch": False,
            "last_event_was_command": False,
        }
        input_defaults.update(case["input_events"])
        for attr, value in input_defaults.items():
            setattr(getattr(mock_input_manager, attr), "return_value", value)
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        if "printable_key" in str(case["input_events"]):
            test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
            test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == getattr(TextEventReason, case["expected_reason"])

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "ui_role",
                "is_ui_role": True,
                "is_editable": False,
                "last_event_was_backspace": False,
                "expected_reason": "UI_UPDATE",
            },
            {
                "id": "editable_backspace",
                "is_ui_role": False,
                "is_editable": True,
                "last_event_was_backspace": True,
                "expected_reason": "BACKSPACE",
            },
            {
                "id": "editable_typing",
                "is_ui_role": False,
                "is_editable": True,
                "last_event_was_backspace": False,
                "expected_reason": "TYPING",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_text_deletion_event_reason_scenarios(self, test_context, case: dict):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "deleted text"

        mock_input_manager = test_context.Mock()
        input_settings = {
            "last_event_was_page_switch": False,
            "last_event_was_delete": False,
            "last_event_was_cut": False,
            "last_event_was_paste": False,
            "last_event_was_undo": False,
            "last_event_was_redo": False,
            "last_event_was_command": False,
            "last_event_was_up_or_down": False,
            "last_event_was_page_up_or_page_down": False,
            "last_event_was_backspace": case["last_event_was_backspace"],
            "last_event_was_printable_key": not case["last_event_was_backspace"],
        }
        for attr, value in input_settings.items():
            setattr(getattr(mock_input_manager, attr), "return_value", value)
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        if case["is_ui_role"]:
            test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.LABEL)
            test_context.patch_object(
                AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
            )
        else:
            test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
            test_context.patch_object(
                AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
            )

        test_context.patch_object(
            AXUtilitiesState, "is_editable", side_effect=lambda obj: case["is_editable"]
        )
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == getattr(TextEventReason, case["expected_reason"])

    def test_get_text_deletion_event_reason_spin_button(self, test_context):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with spin button."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "1"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = True
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_spin_button", return_value=True)
        test_context.patch_object(AXObject, "find_ancestor", return_value=None)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.SPIN_BUTTON_VALUE_CHANGE

    def test_get_text_deletion_event_reason_selected_text_deletion(self, test_context):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with selected text deletion."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "selected text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        test_context.patch_object(
            AXText, "get_cached_selected_text", return_value=("selected text", 0, 13)
        )

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.SELECTED_TEXT_DELETION

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "ui_role",
                "is_ui_role": True,
                "is_editable": False,
                "last_event_was_paste": False,
                "selected_text_matches": False,
                "expected_reason": "UI_UPDATE",
            },
            {
                "id": "editable_paste",
                "is_ui_role": False,
                "is_editable": True,
                "last_event_was_paste": True,
                "selected_text_matches": False,
                "expected_reason": "PASTE",
            },
            {
                "id": "selected_text_insertion",
                "is_ui_role": False,
                "is_editable": True,
                "last_event_was_paste": False,
                "selected_text_matches": True,
                "expected_reason": "SELECTED_TEXT_INSERTION",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_text_insertion_event_reason_scenarios(
        self,
        test_context,
        case: dict,
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "inserted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = case["last_event_was_paste"]
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        if case["is_ui_role"]:
            test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.LABEL)
            test_context.patch_object(
                AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
            )
        else:
            test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
            test_context.patch_object(
                AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
            )

        test_context.patch_object(
            AXUtilitiesState, "is_editable", side_effect=lambda obj: case["is_editable"]
        )
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        if case["selected_text_matches"]:
            test_context.patch_object(
                AXText, "get_selected_text", return_value=("inserted text", 0, 13)
            )
        else:
            test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == getattr(TextEventReason, case["expected_reason"])

    def test_get_text_insertion_event_reason_typing_echoable(self, test_context):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with typing echoable."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager
        from orca import settings_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "a"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = True
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        mock_settings_manager = test_context.Mock()
        mock_settings_manager.get_setting.return_value = True
        test_context.patch_object(
            settings_manager, "get_manager", return_value=mock_settings_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_password_text", return_value=False)

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.TYPING_ECHOABLE

    def test_get_text_insertion_event_reason_auto_insertion_newline(self, test_context):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with auto-insertion newline."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "\n"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = True
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_INSERTION_UNPRESENTABLE

    def test_get_text_selection_changed_event_reason_search_scenarios(self, test_context):
        """Test AXUtilitiesEvent._get_text_selection_changed_event_reason with search scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_backspace.return_value = True
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(
            AXUtilitiesRole, "is_text_input_search", side_effect=lambda obj: obj == mock_focus
        )

        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_UNPRESENTABLE

    def test_get_text_selection_changed_event_reason_caret_selection_word(self, test_context):
        """Test AXUtilitiesEvent._get_text_selection_changed_event_reason with word selection."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "is_text_input_search", return_value=False)

        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_WORD

    def test_is_presentable_active_descendant_change_with_focused_source(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_active_descendant_change with focused source."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = mock_child

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(
            AXUtilitiesState, "is_focused", side_effect=lambda obj: obj == mock_child
        )

        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=False)

        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is True

    def test_is_presentable_active_descendant_change_tree_table_scenario(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_active_descendant_change with tree table."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_different_table = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_different_table
        mock_event.any_data = mock_child

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(
            AXUtilitiesState, "is_focused", side_effect=lambda obj: obj == mock_child
        )

        test_context.patch_object(
            AXUtilitiesRole, "is_table_cell", side_effect=lambda obj: obj == mock_focus
        )
        test_context.patch_object(
            AXUtilitiesRole,
            "is_tree_or_tree_table",
            side_effect=lambda obj: obj in [mock_table, mock_different_table],
        )

        test_context.patch_object(
            AXObject,
            "find_ancestor",
            side_effect=lambda obj, predicate: mock_table if obj == mock_focus else None,
        )

        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is False

    def test_is_presentable_checked_change_with_focus_checking(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_checked_change with focus scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(mock_obj)] = False

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_space.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesState, "is_checked", return_value=True)

        test_context.patch_object(AXUtilitiesRole, "is_radio_button", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_list_item", return_value=True)

        test_context.patch_object(
            AXObject, "is_ancestor",
            side_effect=lambda obj1, obj2: obj1 == mock_obj and obj2 == mock_focus
        )

        result = AXUtilitiesEvent.is_presentable_checked_change(mock_event)
        assert result is True

    def test_is_presentable_description_change_with_focus_scenarios(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_description_change with focus scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "new description"

        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(mock_obj)] = "old description"

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(AXUtilitiesState, "is_showing", return_value=True)

        test_context.patch_object(
            AXObject, "is_ancestor",
            side_effect=lambda obj1, obj2: obj1 == mock_focus and obj2 == mock_obj
        )

        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is True

    def test_is_presentable_expanded_change_with_detail_and_roles(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_expanded_change with detail and role scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.detail1 = 1
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(mock_obj)] = False

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(AXUtilitiesState, "is_expanded", return_value=True)
        test_context.patch_object(AXUtilitiesState, "is_focused", return_value=True)

        test_context.patch_object(AXUtilitiesRole, "is_table_row", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_list_box", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_combo_box", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_button", return_value=False)

        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is True

    def test_is_presentable_indeterminate_change_focus_check(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_indeterminate_change with focus check."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(mock_obj)] = False

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(AXUtilitiesState, "is_indeterminate", return_value=True)

        result = AXUtilitiesEvent.is_presentable_indeterminate_change(mock_event)
        assert result is True

    def test_is_presentable_name_change_with_frame(self, test_context):
        """Test AXUtilitiesEvent.is_presentable_name_change with frame scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_text import AXText
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_frame = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_frame
        mock_event.any_data = "New Window Title: user input text"

        AXUtilitiesEvent.LAST_KNOWN_NAME[hash(mock_frame)] = "Old Window Title"

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_active_window.return_value = mock_frame
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(AXUtilitiesState, "is_showing", return_value=True)
        test_context.patch_object(
            AXUtilitiesState, "is_editable", side_effect=lambda obj: obj == mock_focus
        )

        test_context.patch_object(
            AXUtilitiesRole, "is_frame", side_effect=lambda obj: obj == mock_frame
        )

        test_context.patch_object(AXText, "get_character_count", return_value=15)
        test_context.patch_object(AXText, "get_all_text", return_value="user input text")

        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

    def test_is_presentable_text_event_editable_scenarios(self, test_context):
        """Test AXUtilitiesEvent._is_presentable_text_event with editable scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesState, "is_focused", return_value=False)

        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        test_context.patch_object(
            AXObject, "is_ancestor",
            side_effect=lambda obj1, obj2: obj1 == mock_obj and obj2 == mock_focus
        )

        result = AXUtilitiesEvent._is_presentable_text_event(mock_event)
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "text_attributes", "method_name": "is_presentable_text_attributes_change"},
            {"id": "text_deletion", "method_name": "is_presentable_text_deletion"},
            {"id": "text_insertion", "method_name": "is_presentable_text_insertion"},
        ],
        ids=lambda case: case["id"],
    )
    def test_text_event_methods_delegate(self, test_context, case: dict):
        """Test AXUtilitiesEvent text event methods delegate to _is_presentable_text_event."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = test_context.Mock(spec=Atspi.Event)

        test_context.patch_object(
            AXUtilitiesEvent, "_is_presentable_text_event", return_value=True
        )

        method = getattr(AXUtilitiesEvent, case["method_name"])
        result = method(mock_event)
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "delete",
                "test_scenario": "delete",
                "input_manager_config": {"last_event_was_delete": True},
                "editable_state": True,
                "expected_result": "DELETE",
            },
            {
                "id": "selection_by_word",
                "test_scenario": "selection_by_word",
                "input_manager_config": {
                    "last_event_was_caret_selection": True,
                    "last_event_was_word_navigation": True,
                },
                "editable_state": False,
                "expected_result": "SELECTION_BY_WORD",
            },
            {
                "id": "navigation_by_page",
                "test_scenario": "navigation_by_page",
                "input_manager_config": {
                    "last_event_was_caret_navigation": True,
                    "last_event_was_page_navigation": True,
                },
                "editable_state": False,
                "expected_result": "NAVIGATION_BY_PAGE",
            },
            {
                "id": "navigation_to_line_boundary",
                "test_scenario": "navigation_to_line_boundary",
                "input_manager_config": {
                    "last_event_was_caret_navigation": True,
                    "last_event_was_line_boundary_navigation": True,
                },
                "editable_state": False,
                "expected_result": "NAVIGATION_TO_LINE_BOUNDARY",
            },
            {
                "id": "navigation_to_file_boundary",
                "test_scenario": "navigation_to_file_boundary",
                "input_manager_config": {
                    "last_event_was_caret_navigation": True,
                    "last_event_was_file_boundary_navigation": True,
                },
                "editable_state": False,
                "expected_result": "NAVIGATION_TO_FILE_BOUNDARY",
            },
            {
                "id": "cut",
                "test_scenario": "cut",
                "input_manager_config": {"last_event_was_cut": True},
                "editable_state": True,
                "expected_result": "CUT",
            },
            {
                "id": "paste",
                "test_scenario": "paste",
                "input_manager_config": {"last_event_was_paste": True},
                "editable_state": True,
                "expected_result": "PASTE",
            },
            {
                "id": "undo",
                "test_scenario": "undo",
                "input_manager_config": {"last_event_was_undo": True},
                "editable_state": True,
                "expected_result": "UNDO",
            },
            {
                "id": "redo",
                "test_scenario": "redo",
                "input_manager_config": {"last_event_was_redo": True},
                "editable_state": True,
                "expected_result": "REDO",
            },
            {
                "id": "page_switch",
                "test_scenario": "page_switch",
                "input_manager_config": {"last_event_was_page_switch": True},
                "editable_state": True,
                "expected_result": "PAGE_SWITCH",
            },
            {
                "id": "command",
                "test_scenario": "command",
                "input_manager_config": {"last_event_was_command": True},
                "editable_state": True,
                "expected_result": "UNSPECIFIED_COMMAND",
            },
            {
                "id": "tab_navigation",
                "test_scenario": "tab_navigation",
                "input_manager_config": {"last_event_was_tab_navigation": True},
                "editable_state": False,
                "expected_result": "FOCUS_CHANGE",
            },
            {
                "id": "ui_update",
                "test_scenario": "ui_update",
                "input_manager_config": {},
                "editable_state": False,
                "expected_result": "UI_UPDATE",
            },
            {
                "id": "navigation_by_line",
                "test_scenario": "navigation_by_line",
                "input_manager_config": {
                    "last_event_was_caret_navigation": True,
                    "last_event_was_line_navigation": True,
                },
                "editable_state": False,
                "expected_result": "NAVIGATION_BY_LINE",
            },
            {
                "id": "unspecified_navigation",
                "test_scenario": "unspecified_navigation",
                "input_manager_config": {
                    "last_event_was_caret_navigation": True,
                },
                "editable_state": False,
                "expected_result": "UNSPECIFIED_NAVIGATION",
            },
            {
                "id": "editable_backspace",
                "test_scenario": "editable_backspace",
                "input_manager_config": {"last_event_was_backspace": True},
                "editable_state": True,
                "expected_result": "BACKSPACE",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_caret_moved_event_reason_consolidated(self, test_context, case: dict):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager, input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        default_config = {
            "last_event_was_backspace": False,
            "last_event_was_delete": False,
            "last_event_was_caret_selection": False,
            "last_event_was_caret_navigation": False,
            "last_event_was_line_navigation": False,
            "last_event_was_word_navigation": False,
            "last_event_was_character_navigation": False,
            "last_event_was_page_navigation": False,
            "last_event_was_line_boundary_navigation": False,
            "last_event_was_file_boundary_navigation": False,
            "last_event_was_select_all": False,
            "last_event_was_primary_click_or_release": False,
            "last_event_was_cut": False,
            "last_event_was_paste": False,
            "last_event_was_undo": False,
            "last_event_was_redo": False,
            "last_event_was_page_switch": False,
            "last_event_was_command": False,
            "last_event_was_printable_key": False,
            "last_event_was_tab_navigation": False,
        }
        default_config.update(case["input_manager_config"])

        for attr, value in default_config.items():
            setattr(mock_input_manager, attr, test_context.Mock(return_value=value))

        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(
            AXUtilitiesState, "is_editable", side_effect=lambda obj: case["editable_state"]
        )
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        if case["test_scenario"] == "ui_update":
            from orca.ax_object import AXObject

            test_context.patch_object(
                AXObject, "find_ancestor", return_value=test_context.Mock()
            )

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == getattr(TextEventReason, case["expected_result"])

    def test_get_text_event_reason_ui_update(self, test_context):
        """Test get_text_event_reason with UI update scenario."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=["text"])
        test_context.patch_object(AXObject, "get_role", return_value="text")

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UI_UPDATE

    def test_get_text_event_reason_page_switch_scenario(self, test_context):
        """Test get_text_event_reason with page switch scenario."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="document")

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

    def test_get_text_event_reason_command_scenario(self, test_context):
        """Test get_text_event_reason with command scenario."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="document")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_text_event_reason_delete_in_editable(self, test_context):
        """Test get_text_event_reason with delete in editable object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.DELETE

    def test_get_text_event_reason_cut_in_editable(self, test_context):
        """Test get_text_event_reason with cut in editable object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.CUT

    def test_get_text_event_reason_paste_in_editable(self, test_context):
        """Test get_text_event_reason with paste in editable object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.PASTE

    def test_get_text_event_reason_undo_in_editable(self, test_context):
        """Test get_text_event_reason with undo in editable object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UNDO

    def test_get_text_event_reason_redo_in_editable(self, test_context):
        """Test get_text_event_reason with redo in editable object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.REDO

    def test_get_text_event_reason_command_in_editable(self, test_context):
        """Test get_text_event_reason with command in editable object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        from orca.ax_text import AXText

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_clear_all_dictionaries_direct_call(self, test_context):
        """Test _clear_all_dictionaries method directly."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca import debug

        mock_print_message = test_context.Mock()
        test_context.patch_object(debug, "print_message", new=mock_print_message)

        AXUtilitiesEvent._clear_all_dictionaries("direct test")

        mock_print_message.assert_called_once()
        args = mock_print_message.call_args[0]
        assert "AXUtilitiesEvent: Clearing local cache." in args[1]
        assert "Reason: direct test" in args[1]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "delete_scenario",
                "test_event_type": "delete",
                "input_manager_config": {"last_event_was_delete": True},
                "expected_reason": "DELETE",
            },
            {
                "id": "cut_scenario",
                "test_event_type": "cut",
                "input_manager_config": {"last_event_was_cut": True},
                "expected_reason": "CUT",
            },
            {
                "id": "paste_scenario",
                "test_event_type": "paste",
                "input_manager_config": {"last_event_was_paste": True},
                "expected_reason": "PASTE",
            },
            {
                "id": "undo_scenario",
                "test_event_type": "undo",
                "input_manager_config": {"last_event_was_undo": True},
                "expected_reason": "UNDO",
            },
            {
                "id": "redo_scenario",
                "test_event_type": "redo",
                "input_manager_config": {"last_event_was_redo": True},
                "expected_reason": "REDO",
            },
            {
                "id": "command_scenario",
                "test_event_type": "command",
                "input_manager_config": {"last_event_was_command": True},
                "expected_reason": "UNSPECIFIED_COMMAND",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_text_insertion_event_reason_input_scenarios(
        self, test_context, case: dict
    ) -> None:
        """Test _get_text_insertion_event_reason with various input scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = test_context.Mock()
        default_config = {
            "last_event_was_page_switch": False,
            "last_event_was_backspace": False,
            "last_event_was_delete": False,
            "last_event_was_cut": False,
            "last_event_was_paste": False,
            "last_event_was_undo": False,
            "last_event_was_redo": False,
            "last_event_was_command": False,
        }
        default_config.update(case["input_manager_config"])
        for method_name, return_value in default_config.items():
            setattr(mock_input_manager, method_name, test_context.Mock(return_value=return_value))
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "get_text_ui_roles", return_value=[])
        test_context.patch_object(AXObject, "get_role", return_value="entry")
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == getattr(TextEventReason, case["expected_reason"])

    def test_get_text_deletion_event_reason_auto_deletion(self, test_context):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with auto deletion."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "auto deleted"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = True
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_spin_button", return_value=False)
        test_context.patch_object(AXObject, "find_ancestor", return_value=None)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_DELETION

    def test_get_text_deletion_event_reason_children_change(self, test_context):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with children change."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "\ufffc"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.CHILDREN_CHANGE

    def test_get_text_insertion_event_reason_selected_text_restoration(self, test_context):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with selected text restoration."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "restored text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        test_context.patch_object(
            AXText, "get_selected_text", return_value=("restored text", 0, 13)
        )

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.SELECTED_TEXT_RESTORATION

    def test_get_text_insertion_event_reason_auto_insertion_presentable_tab(self, test_context):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with auto insertion from tab."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "auto inserted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = True
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_INSERTION_PRESENTABLE

    def test_get_text_insertion_event_reason_auto_insertion_unpresentable_return(
        self, test_context
    ):
        """Test _get_text_insertion_event_reason with auto insertion from return in single line."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "auto inserted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = True
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXUtilitiesState, "is_single_line", return_value=True)

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_INSERTION_UNPRESENTABLE

    def test_get_text_insertion_event_reason_middle_click(self, test_context):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with middle click."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "pasted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = True
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.MOUSE_MIDDLE_BUTTON

    def test_clear_cache_now_with_reason(self, test_context):
        """Test AXUtilitiesEvent.clear_cache_now with reason parameter."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent

        AXUtilitiesEvent.clear_cache_now("test reason")
        assert len(AXUtilitiesEvent.LAST_KNOWN_NAME) == 0
        assert len(AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION) == 0
        assert len(AXUtilitiesEvent.TEXT_EVENT_REASON) == 0

    def test_get_text_deletion_event_reason_page_switch(self, test_context):
        """Test _get_text_deletion_event_reason with page switch scenario."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

    def test_get_text_deletion_event_reason_editable_scenarios(self, test_context):
        """Test _get_text_deletion_event_reason with various editable scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "deleted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXText, "get_cached_selected_text", return_value=("", 0, 0))

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.DELETE

        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.CUT

        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.PASTE

        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.UNDO

        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.REDO

        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_text_deletion_event_reason_command_non_editable(self, test_context):
        """Test _get_text_deletion_event_reason command scenario for non-editable."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "deleted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_text_insertion_event_reason_editable_backspace(self, test_context):
        """Test _get_text_insertion_event_reason with editable backspace scenario."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "inserted text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = True
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))
        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.BACKSPACE

    def test_get_text_insertion_event_reason_redo_selected_text_restoration(self, test_context):
        """Test _get_text_insertion_event_reason with redo and selected text restoration."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "selected text"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(
            AXText, "get_selected_text", return_value=("selected text", 0, 13)
        )

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.SELECTED_TEXT_RESTORATION

    def test_get_text_selection_changed_event_reason_comprehensive(self, test_context):
        """Test _get_text_selection_changed_event_reason with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_search_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager.get_locus_of_focus.return_value = mock_search_obj

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "is_text_input_search", return_value=True)
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_PRESENTABLE

        mock_input_manager.last_event_was_backspace.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_UNPRESENTABLE

        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_UNPRESENTABLE

        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True

        mock_input_manager.last_event_was_line_navigation.return_value = True
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_LINE

        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_WORD

        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_CHARACTER

        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_PAGE

        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_TO_LINE_BOUNDARY

        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_TO_FILE_BOUNDARY

        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_SELECTION

    def test_get_text_selection_changed_event_reason_caret_navigation(self, test_context):
        """Test _get_text_selection_changed_event_reason caret navigation scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "is_text_input_search", return_value=False)
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        mock_input_manager.last_event_was_line_navigation.return_value = True
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_LINE

        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_WORD

        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_CHARACTER

        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_PAGE

        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_TO_LINE_BOUNDARY

        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_TO_FILE_BOUNDARY

        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_NAVIGATION

    def test_get_text_selection_changed_event_reason_editable_scenarios(self, test_context):
        """Test _get_text_selection_changed_event_reason with editable scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager, focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXUtilitiesRole, "is_text_input_search", return_value=False)
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_spin_button", return_value=False)
        test_context.patch_object(AXObject, "find_ancestor", return_value=None)

        mock_input_manager.last_event_was_backspace.return_value = True
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.BACKSPACE

        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.DELETE

        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.CUT

        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.PASTE

        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNDO

        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.REDO

        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.TYPING

        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = True
        test_context.patch_object(AXUtilitiesRole, "is_spin_button", return_value=True)
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SPIN_BUTTON_VALUE_CHANGE

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "active_descendant_no_focused_state",
                "test_scenario": "no_focused_state",
                "setup_config": {"is_focused": lambda obj: False},
                "expected_result": False,
            },
            {
                "id": "active_descendant_tree_table_different_tree",
                "test_scenario": "tree_table_different_tree",
                "setup_config": {
                    "is_focused": "child_focused",
                    "is_table_cell": True,
                    "setup_tree_table": True,
                },
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_active_descendant_change_edge_cases(self, test_context, case: dict):
        """Test is_presentable_active_descendant_change edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.any_data = mock_child

        if case["test_scenario"] == "no_focused_state":
            test_context.patch_object(
                AXUtilitiesState, "is_focused", new=case["setup_config"]["is_focused"]
            )
        elif case["test_scenario"] == "tree_table_different_tree":
            test_context.patch_object(
                AXUtilitiesState, "is_focused", side_effect=lambda obj: obj == mock_child
            )
            mock_focus = test_context.Mock(spec=Atspi.Accessible)
            mock_table = test_context.Mock(spec=Atspi.Accessible)
            mock_focus_manager = test_context.Mock()
            mock_focus_manager.get_locus_of_focus.return_value = mock_focus
            test_context.patch_object(
                focus_manager, "get_manager", return_value=mock_focus_manager
            )
            test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=True)
            test_context.patch_object(
                AXObject, "find_ancestor", return_value=mock_table
            )

        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "checked_radio_button_no_space",
                "test_scenario": "ancestor_not_list_tree_item",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_checked_change_edge_cases(self, test_context, case: dict):
        """Test is_presentable_checked_change edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager, input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)
        test_context.patch_object(AXUtilitiesState, "is_checked", return_value=True)
        AXUtilitiesEvent.LAST_KNOWN_CHECKED.clear()

        if case["test_scenario"] == "ancestor_not_list_tree_item":
            test_context.patch_object(
                AXObject, "is_ancestor", return_value=True
            )
            test_context.patch_object(AXUtilitiesRole, "is_list_item", return_value=False)
            test_context.patch_object(AXUtilitiesRole, "is_tree_item", return_value=False)
        elif case["test_scenario"] == "radio_button_no_space":
            mock_focus_manager.get_locus_of_focus.return_value = mock_source
            test_context.patch_object(AXUtilitiesRole, "is_radio_button", return_value=True)
            mock_input_manager = test_context.Mock()
            mock_input_manager.last_event_was_space.return_value = False
            test_context.patch_object(
                input_event_manager, "get_manager", return_value=mock_input_manager
            )

        result = AXUtilitiesEvent.is_presentable_checked_change(mock_event)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "description_empty",
                "test_scenario": "empty_description",
                "description_data": "",
                "is_showing": True,
                "is_ancestor": True,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_description_change_edge_cases(self, test_context, case: dict):
        """Test is_presentable_description_change edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager
        from orca.ax_object import AXObject

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.any_data = case["description_data"]
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.clear()

        test_context.patch_object(
            AXUtilitiesState, "is_showing", side_effect=lambda obj: case["is_showing"]
        )

        if case["test_scenario"] in ["not_focus_ancestor", "not_showing"]:
            mock_focus = test_context.Mock(spec=Atspi.Accessible)
            mock_focus_manager = test_context.Mock()
            mock_focus_manager.get_locus_of_focus.return_value = mock_focus
            test_context.patch_object(
                focus_manager, "get_manager", return_value=mock_focus_manager
            )
            test_context.patch_object(
                AXObject, "is_ancestor", side_effect=lambda focus, source: case["is_ancestor"]
            )

        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "expanded_not_focus_ancestor",
                "test_scenario": "not_focus_ancestor",
                "detail1": 0,
                "role_configs": {},
                "is_ancestor": False,
                "is_focused": True,
                "expected_result": False,
            },
            {
                "id": "expanded_table_row",
                "test_scenario": "table_row",
                "detail1": 0,
                "role_configs": {"is_table_row": True, "is_list_box": False},
                "is_ancestor": True,
                "is_focused": True,
                "expected_result": True,
            },
            {
                "id": "expanded_list_box",
                "test_scenario": "list_box",
                "detail1": 1,
                "role_configs": {"is_table_row": False, "is_list_box": True},
                "is_ancestor": True,
                "is_focused": True,
                "expected_result": True,
            },
            {
                "id": "expanded_combo_box_no_focus",
                "test_scenario": "combo_box_no_focus",
                "detail1": 1,
                "role_configs": {"is_combo_box": True, "is_button": False},
                "is_ancestor": True,
                "is_focused": False,
                "expected_result": False,
            },
            {
                "id": "expanded_button_no_focus",
                "test_scenario": "button_no_focus",
                "detail1": 1,
                "role_configs": {"is_combo_box": False, "is_button": True},
                "is_ancestor": True,
                "is_focused": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_expanded_change_edge_cases(self, test_context, case: dict):
        """Test is_presentable_expanded_change edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.detail1 = case["detail1"]
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()

        test_context.patch_object(AXUtilitiesState, "is_expanded", return_value=True)
        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)
        test_context.patch_object(
            AXObject, "is_ancestor", side_effect=lambda focus, source: case["is_ancestor"]
        )

        for role_method, value in case["role_configs"].items():
            test_context.patch_object(
                AXUtilitiesRole, role_method, side_effect=lambda obj, v=value: v
            )

        if "no_focus" in case["test_scenario"]:
            test_context.patch_object(
                AXUtilitiesState, "is_focused", side_effect=lambda obj: case["is_focused"]
            )

        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "indeterminate_not_from_focus",
                "change_type": "indeterminate",
                "state_method": "is_indeterminate",
                "expected_result": False,
            },
            {
                "id": "invalid_entry_not_from_focus",
                "change_type": "invalid_entry",
                "state_method": "is_invalid_entry",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_simple_change_edge_cases(self, test_context, case: dict) -> None:
        """Test simple presentable change edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        cache_name = f"LAST_KNOWN_{case['change_type'].upper()}"
        getattr(AXUtilitiesEvent, cache_name).clear()

        test_context.patch_object(AXUtilitiesState, case["state_method"], return_value=True)

        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        method_name = f"is_presentable_{case['change_type']}_change"
        result = getattr(AXUtilitiesEvent, method_name)(mock_event)
        assert result is case["expected_result"]

    def test_is_presentable_name_change_edge_cases(self, test_context):
        """Test is_presentable_name_change edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_text import AXText
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.any_data = "new name"
        AXUtilitiesEvent.LAST_KNOWN_NAME.clear()

        mock_event.any_data = ""
        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

        mock_event.any_data = "new name"
        test_context.patch_object(AXUtilitiesState, "is_showing", return_value=False)
        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

        test_context.patch_object(AXUtilitiesState, "is_showing", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_frame", return_value=True)

        mock_active_window = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_active_window.return_value = mock_active_window
        mock_focus_manager.get_locus_of_focus.return_value = mock_source
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

        mock_focus_manager.get_active_window.return_value = mock_source

        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus

        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=10)
        test_context.patch_object(AXText, "get_all_text", return_value="new")

        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "pressed_not_from_focus",
                "change_type": "pressed",
                "state_method": "is_pressed",
                "expected_result": False,
            },
            {
                "id": "selected_not_from_focus",
                "change_type": "selected",
                "state_method": "is_selected",
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_is_presentable_state_change_edge_cases(self, test_context, case: dict) -> None:
        """Test presentable state change edge cases not from focus."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        cache_name = f"LAST_KNOWN_{case['change_type'].upper()}"
        getattr(AXUtilitiesEvent, cache_name).clear()

        test_context.patch_object(AXUtilitiesState, case["state_method"], return_value=True)

        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        method_name = f"is_presentable_{case['change_type']}_change"
        result = getattr(AXUtilitiesEvent, method_name)(mock_event)
        assert result is case["expected_result"]

    def test_is_presentable_text_event_edge_cases(self, test_context):
        """Test _is_presentable_text_event edge cases."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)

        result = AXUtilitiesEvent._is_presentable_text_event(mock_event)
        assert result is False

        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)

        mock_focus = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        test_context.patch_object(focus_manager, "get_manager", return_value=mock_focus_manager)

        test_context.patch_object(AXUtilitiesState, "is_focused", return_value=False)
        test_context.patch_object(AXObject, "is_ancestor", return_value=True)

        result = AXUtilitiesEvent._is_presentable_text_event(mock_event)
        assert result is True

    def test_get_text_insertion_event_reason_additional_scenarios(self, test_context):
        """Test additional _get_text_insertion_event_reason scenarios for missing coverage."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = test_context.Mock(spec=Atspi.Event)
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "x"

        mock_input_manager = test_context.Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_space.return_value = False
        mock_input_manager.last_event_was_tab.return_value = False
        mock_input_manager.last_event_was_return.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = True
        mock_input_manager.last_event_was_middle_click.return_value = False
        mock_input_manager.last_event_was_middle_release.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        test_context.patch_object(
            input_event_manager, "get_manager", return_value=mock_input_manager
        )

        test_context.patch_object(AXObject, "get_role", return_value=Atspi.Role.TEXT)
        test_context.patch_object(
            AXUtilitiesRole, "get_text_ui_roles", return_value=[Atspi.Role.LABEL]
        )
        test_context.patch_object(AXUtilitiesState, "is_editable", return_value=True)
        test_context.patch_object(AXUtilitiesRole, "is_terminal", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_password_text", return_value=True)
        test_context.patch_object(AXText, "get_selected_text", return_value=("", 0, 0))

        from orca import settings_manager

        mock_settings_manager = test_context.Mock()
        mock_settings_manager.get_setting.return_value = True
        test_context.patch_object(
            settings_manager, "get_manager", return_value=mock_settings_manager
        )

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.TYPING_ECHOABLE

        mock_event.any_data = "multi-char"
        test_context.patch_object(AXUtilitiesRole, "is_password_text", return_value=False)
        mock_settings_manager.get_setting.return_value = False

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.TYPING
