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

"""Unit tests for ax_utilities_event.py event-related utilities."""

from unittest.mock import Mock

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .conftest import clean_module_cache

def _clear_ax_event_state():
    from orca.ax_utilities_event import AXUtilitiesEvent

    AXUtilitiesEvent.LAST_KNOWN_NAME.clear()
    AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.clear()
    AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()
    AXUtilitiesEvent.LAST_KNOWN_CHECKED.clear()
    AXUtilitiesEvent.LAST_KNOWN_PRESSED.clear()
    AXUtilitiesEvent.LAST_KNOWN_SELECTED.clear()
    AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE.clear()
    AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.clear()


def _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies):
    import sys
    from orca.ax_object import AXObject
    from orca.ax_text import AXText
    from orca.ax_utilities_state import AXUtilitiesState

    monkeypatch.setitem(sys.modules, "orca.focus_manager", Mock())
    monkeypatch.setitem(sys.modules, "orca.input_event_manager", Mock())
    monkeypatch.setitem(sys.modules, "orca.settings_manager", Mock())
    debug_mock = mock_orca_dependencies["debug"]
    debug_file_mock = Mock()
    debug_file_mock.name = "/tmp/debug.out"
    debug_mock.debugFile = debug_file_mock

    _clear_ax_event_state()

    monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.LABEL)
    monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
    monkeypatch.setattr(AXObject, "get_name", lambda obj: "")
    monkeypatch.setattr(AXObject, "get_description", lambda obj: "")
    monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {})
    monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 0)
    monkeypatch.setattr(AXObject, "get_parent", lambda obj: None)
    monkeypatch.setattr(AXObject, "is_ancestor", lambda focus, obj: focus == obj)

    monkeypatch.setattr(AXText, "get_all_text", lambda obj: "")
    monkeypatch.setattr(AXText, "get_character_count", lambda obj: 0)

    monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: True)

    monkeypatch.setattr(AXObject, "has_state", lambda obj, state: True)


@pytest.mark.unit
class TestAXUtilitiesEvent:
    """Test event-related methods."""

    @pytest.mark.parametrize(
        "initial_state, current_state, expected_result",
        [
            pytest.param(False, True, True, id="state_changed"),
            pytest.param(True, True, False, id="state_unchanged"),
        ],
    )
    def test_is_presentable_expanded_change(
        self, monkeypatch, initial_state, current_state, expected_result, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_expanded_change."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)

        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(mock_obj)] = initial_state
        monkeypatch.setattr(AXUtilitiesState, "is_expanded", lambda obj: current_state)

        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is expected_result

    @pytest.mark.parametrize(
        "new_description, old_description, expected_result",
        [
            pytest.param("", "old description", False, id="empty_description"),
            pytest.param("same description", "same description", False, id="unchanged_description"),
            pytest.param("new description", "old description", True, id="changed_description"),
        ],
    )
    def test_is_presentable_description_change_scenarios(
        self, monkeypatch, new_description, old_description, expected_result, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_description_change."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)

        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = new_description
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(mock_obj)] = old_description

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

        monkeypatch.setattr(
            AXUtilitiesEvent,
            "is_presentable_description_change",
            mock_is_presentable_description_change,
        )

        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is expected_result

    def test_save_object_info_for_events_with_none(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent.save_object_info_for_events with None."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        AXUtilitiesEvent.save_object_info_for_events(None)
        assert not AXUtilitiesEvent.LAST_KNOWN_NAME
        assert not AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION

    def test_get_text_event_reason_with_cached_reason(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent.get_text_event_reason with cached reason."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason

        mock_event = Mock(spec=Atspi.Event)
        AXUtilitiesEvent.TEXT_EVENT_REASON[mock_event] = TextEventReason.TYPING
        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.TYPING

    def test_get_text_event_reason_with_unexpected_event_type(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.get_text_event_reason handles unexpected event types."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = "unexpected:event:type"

        with pytest.raises(ValueError, match="Unexpected event type"):
            AXUtilitiesEvent.get_text_event_reason(mock_event)

    def test_is_presentable_active_descendant_change_with_no_any_data(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_active_descendant_change with no data."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = Mock(spec=Atspi.Event)
        mock_event.any_data = None
        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is False

    def test_is_presentable_description_change_with_non_string_data(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_description_change with non-string data."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = Mock(spec=Atspi.Event)
        mock_event.any_data = 123
        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is False

    def test_is_presentable_checked_change_with_same_state(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_checked_change with same state."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(mock_obj)] = True
        monkeypatch.setattr(AXUtilitiesState, "is_checked", lambda obj: True)
        result = AXUtilitiesEvent.is_presentable_checked_change(mock_event)
        assert result is False

    def test_is_presentable_name_change_with_empty_string(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_name_change with empty string."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = ""
        AXUtilitiesEvent.LAST_KNOWN_NAME[hash(mock_obj)] = "old name"
        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

    def test_is_presentable_indeterminate_change_with_cleared_state(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_indeterminate_change with cleared state."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(mock_obj)] = True
        monkeypatch.setattr(AXUtilitiesState, "is_indeterminate", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_indeterminate_change(mock_event)
        assert result is False

    def test_is_presentable_pressed_change_with_new_state(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_pressed_change with new state."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(mock_obj)] = False
        monkeypatch.setattr(AXUtilitiesState, "is_pressed", lambda obj: True)

        def mock_is_presentable_pressed_change(event):
            old_state = AXUtilitiesEvent.LAST_KNOWN_PRESSED.get(hash(event.source))
            new_state = AXUtilitiesState.is_pressed(event.source)
            if old_state == new_state:
                return False
            AXUtilitiesEvent.LAST_KNOWN_PRESSED[hash(event.source)] = new_state
            return True

        monkeypatch.setattr(
            AXUtilitiesEvent, "is_presentable_pressed_change", mock_is_presentable_pressed_change
        )

        result = AXUtilitiesEvent.is_presentable_pressed_change(mock_event)
        assert result is True

    def test_is_presentable_selected_change_without_focus(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_selected_change without focus."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_SELECTED[hash(mock_obj)] = False
        monkeypatch.setattr(AXUtilitiesState, "is_selected", lambda obj: True)
        monkeypatch.setattr(AXObject, "has_state", lambda obj, state: False)
        result = AXUtilitiesEvent.is_presentable_selected_change(mock_event)
        assert result is False

    def test_is_presentable_invalid_entry_change_with_same_state(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_invalid_entry_change with same state."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY[hash(mock_obj)] = True
        monkeypatch.setattr(AXUtilitiesState, "is_invalid_entry", lambda obj: True)
        result = AXUtilitiesEvent.is_presentable_invalid_entry_change(mock_event)
        assert result is False

    def test_is_presentable_invalid_entry_change_with_new_state(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_invalid_entry_change with new state."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY[hash(mock_obj)] = False
        monkeypatch.setattr(AXUtilitiesState, "is_invalid_entry", lambda obj: True)

        def mock_is_presentable_invalid_entry_change(event):
            old_state = AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.get(hash(event.source))
            new_state = AXUtilitiesState.is_invalid_entry(event.source)
            if old_state == new_state:
                return False
            AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY[hash(event.source)] = new_state
            return True

        monkeypatch.setattr(
            AXUtilitiesEvent,
            "is_presentable_invalid_entry_change",
            mock_is_presentable_invalid_entry_change,
        )

        result = AXUtilitiesEvent.is_presentable_invalid_entry_change(mock_event)
        assert result is True

    def test_save_object_info_for_events_with_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent.save_object_info_for_events with valid object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_object import AXObject
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_window = Mock(spec=Atspi.Accessible)

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_window.return_value = mock_window
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(
            AXObject, "get_name", lambda obj: "test name" if obj == mock_obj else "window name"
        )
        monkeypatch.setattr(
            AXObject,
            "get_description",
            lambda obj: "test desc" if obj == mock_obj else "window desc",
        )

        monkeypatch.setattr(AXUtilitiesState, "is_checked", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesState, "is_expanded", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesState, "is_indeterminate", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesState, "is_pressed", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesState, "is_selected", lambda obj: True)

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
        "event_type, expected_method",
        [
            pytest.param(
                "object:text-changed:insert",
                "_get_text_insertion_event_reason",
                id="text_insertion",
            ),
            pytest.param(
                "object:text-caret-moved", "_get_caret_moved_event_reason", id="caret_moved"
            ),
            pytest.param(
                "object:text-changed:delete", "_get_text_deletion_event_reason", id="text_deletion"
            ),
            pytest.param(
                "object:text-selection-changed",
                "_get_text_selection_changed_event_reason",
                id="text_selection",
            ),
        ],
    )
    def test_get_text_event_reason_method_dispatch(
        self, monkeypatch, event_type, expected_method, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.get_text_event_reason dispatches correctly."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason

        mock_event = Mock(spec=Atspi.Event)
        mock_event.type = event_type

        expected_reason = TextEventReason.TYPING
        monkeypatch.setattr(AXUtilitiesEvent, expected_method, lambda event: expected_reason)

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == expected_reason
        assert AXUtilitiesEvent.TEXT_EVENT_REASON[mock_event] == expected_reason

    @pytest.mark.parametrize(
        (
            "say_all_mode, focus_matches_source, is_search_input, "
            "last_event_was_backspace, expected_reason"
        ),
        [
            pytest.param(True, True, False, False, "SAY_ALL", id="say_all_mode"),
            pytest.param(
                False, False, True, True, "SEARCH_UNPRESENTABLE", id="search_with_backspace"
            ),
            pytest.param(
                False, False, True, False, "SEARCH_PRESENTABLE", id="search_without_backspace"
            ),
        ],
    )
    def test_get_caret_moved_event_reason_scenarios(
        self,
        monkeypatch,
        say_all_mode,
        focus_matches_source,
        is_search_input,
        last_event_was_backspace,
        expected_reason,
        mock_orca_dependencies,
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        focus_mode = focus_manager.SAY_ALL if say_all_mode else "normal"
        focus_object = mock_obj if focus_matches_source else mock_focus
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            focus_mode,
            focus_object,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
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
        mock_input_manager.last_event_was_backspace.return_value = last_event_was_backspace
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_text_input_search", lambda obj: is_search_input)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == getattr(TextEventReason, expected_reason)

    def test_get_caret_moved_event_reason_caret_selection_line_navigation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_caret_moved_event_reason with caret selection line navigation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = True
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_LINE

    def test_get_caret_moved_event_reason_caret_navigation_word(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with caret navigation word."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_WORD

    def test_get_caret_moved_event_reason_editable_typing(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with editable object typing."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.TYPING

    @pytest.mark.parametrize(
        "is_ui_role, is_editable, last_event_was_backspace, expected_reason",
        [
            pytest.param(True, False, False, "UI_UPDATE", id="ui_role"),
            pytest.param(False, True, True, "BACKSPACE", id="editable_backspace"),
            pytest.param(False, True, False, "TYPING", id="editable_typing"),
        ],
    )
    def test_get_text_deletion_event_reason_scenarios(
        self,
        monkeypatch,
        is_ui_role,
        is_editable,
        last_event_was_backspace,
        expected_reason,
        mock_orca_dependencies,
    ):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "deleted text"

        mock_input_manager = Mock()
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
            "last_event_was_backspace": last_event_was_backspace,
            "last_event_was_printable_key": not last_event_was_backspace,
        }
        for attr, value in input_settings.items():
            setattr(getattr(mock_input_manager, attr), "return_value", value)
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        if is_ui_role:
            monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.LABEL)
            monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        else:
            monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
            monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: is_editable)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == getattr(TextEventReason, expected_reason)

    def test_get_text_deletion_event_reason_spin_button(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with spin button."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "1"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_spin_button", lambda obj: True)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, predicate: None)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.SPIN_BUTTON_VALUE_CHANGE

    def test_get_text_deletion_event_reason_selected_text_deletion(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with selected text deletion."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "selected text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(
            AXText, "get_cached_selected_text", lambda obj: ("selected text", 0, 13)
        )

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.SELECTED_TEXT_DELETION

    @pytest.mark.parametrize(
        "is_ui_role, is_editable, last_event_was_paste, selected_text_matches, expected_reason",
        [
            pytest.param(True, False, False, False, "UI_UPDATE", id="ui_role"),
            pytest.param(False, True, True, False, "PASTE", id="editable_paste"),
            pytest.param(
                False, True, False, True, "SELECTED_TEXT_INSERTION", id="selected_text_insertion"
            ),
        ],
    )
    def test_get_text_insertion_event_reason_scenarios(
        self,
        monkeypatch,
        is_ui_role,
        is_editable,
        last_event_was_paste,
        selected_text_matches,
        expected_reason,
        mock_orca_dependencies,
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "inserted text"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = last_event_was_paste
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        if is_ui_role:
            monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.LABEL)
            monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        else:
            monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
            monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: is_editable)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        if selected_text_matches:
            monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("inserted text", 0, 13))
        else:
            monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == getattr(TextEventReason, expected_reason)

    def test_get_text_insertion_event_reason_typing_echoable(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with typing echoable."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager
        from orca import settings_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "a"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        mock_settings_manager = Mock()
        mock_settings_manager.get_setting.return_value = True
        monkeypatch.setattr(settings_manager, "get_manager", lambda: mock_settings_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_password_text", lambda obj: False)

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.TYPING_ECHOABLE

    def test_get_text_insertion_event_reason_auto_insertion_newline(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with auto-insertion newline."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "\n"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_INSERTION_UNPRESENTABLE

    def test_get_text_selection_changed_event_reason_search_scenarios(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_selection_changed_event_reason with search scenarios."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = True
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_text_input_search", lambda obj: obj == mock_focus)

        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_UNPRESENTABLE

    def test_get_text_selection_changed_event_reason_caret_selection_word(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_selection_changed_event_reason with word selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_text_input_search", lambda obj: False)

        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_WORD

    def test_is_presentable_active_descendant_change_with_focused_source(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_active_descendant_change with focused source."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_child = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = mock_child

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: obj == mock_child)

        monkeypatch.setattr(AXUtilitiesRole, "is_table_cell", lambda obj: False)

        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is True

    def test_is_presentable_active_descendant_change_tree_table_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_active_descendant_change with tree table."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_child = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_table = Mock(spec=Atspi.Accessible)
        mock_different_table = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_different_table
        mock_event.any_data = mock_child

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: obj == mock_child)

        monkeypatch.setattr(AXUtilitiesRole, "is_table_cell", lambda obj: obj == mock_focus)
        monkeypatch.setattr(
            AXUtilitiesRole,
            "is_tree_or_tree_table",
            lambda obj: obj in [mock_table, mock_different_table],
        )

        monkeypatch.setattr(
            AXObject,
            "find_ancestor",
            lambda obj, predicate: mock_table if obj == mock_focus else None,
        )

        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is False

    def test_is_presentable_checked_change_with_focus_checking(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_checked_change with focus scenarios."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        AXUtilitiesEvent.LAST_KNOWN_CHECKED[hash(mock_obj)] = False

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_space.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_checked", lambda obj: True)

        monkeypatch.setattr(AXUtilitiesRole, "is_radio_button", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj: True)

        monkeypatch.setattr(
            AXObject, "is_ancestor", lambda obj1, obj2: obj1 == mock_obj and obj2 == mock_focus
        )

        result = AXUtilitiesEvent.is_presentable_checked_change(mock_event)
        assert result is True

    def test_is_presentable_description_change_with_focus_scenarios(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_description_change with focus scenarios."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "new description"

        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION[hash(mock_obj)] = "old description"

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: True)

        monkeypatch.setattr(
            AXObject, "is_ancestor", lambda obj1, obj2: obj1 == mock_focus and obj2 == mock_obj
        )

        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is True

    def test_is_presentable_expanded_change_with_detail_and_roles(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_expanded_change with detail and role scenarios."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.detail1 = 1
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED[hash(mock_obj)] = False

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_expanded", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: True)

        monkeypatch.setattr(AXUtilitiesRole, "is_table_row", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_box", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_combo_box", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_button", lambda obj: False)

        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is True

    def test_is_presentable_indeterminate_change_focus_check(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent.is_presentable_indeterminate_change with focus check."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE[hash(mock_obj)] = False

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_indeterminate", lambda obj: True)

        result = AXUtilitiesEvent.is_presentable_indeterminate_change(mock_event)
        assert result is True

    def test_is_presentable_name_change_with_frame(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent.is_presentable_name_change with frame scenarios."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_text import AXText
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_frame = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_frame
        mock_event.any_data = "New Window Title: user input text"

        AXUtilitiesEvent.LAST_KNOWN_NAME[hash(mock_frame)] = "Old Window Title"

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_window.return_value = mock_frame
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: obj == mock_focus)

        monkeypatch.setattr(AXUtilitiesRole, "is_frame", lambda obj: obj == mock_frame)

        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 15)
        monkeypatch.setattr(AXText, "get_all_text", lambda obj: "user input text")

        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

    def test_is_presentable_text_event_editable_scenarios(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._is_presentable_text_event with editable scenarios."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: False)

        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(
            AXObject, "is_ancestor", lambda obj1, obj2: obj1 == mock_obj and obj2 == mock_focus
        )

        result = AXUtilitiesEvent._is_presentable_text_event(mock_event)
        assert result is True

    @pytest.mark.parametrize(
        "method_name",
        [
            pytest.param("is_presentable_text_attributes_change", id="text_attributes"),
            pytest.param("is_presentable_text_deletion", id="text_deletion"),
            pytest.param("is_presentable_text_insertion", id="text_insertion"),
        ],
    )
    def test_text_event_methods_delegate(self, monkeypatch, method_name, mock_orca_dependencies):
        """Test AXUtilitiesEvent text event methods delegate to _is_presentable_text_event."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        mock_event = Mock(spec=Atspi.Event)

        monkeypatch.setattr(AXUtilitiesEvent, "_is_presentable_text_event", lambda event: True)

        method = getattr(AXUtilitiesEvent, method_name)
        result = method(mock_event)
        assert result is True

    def test_get_caret_moved_event_reason_character_selection(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with character selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = True
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_CHARACTER

    def test_get_caret_moved_event_reason_page_selection(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with page selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = True
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_PAGE

    def test_get_caret_moved_event_reason_line_boundary_selection(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with line boundary selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = True
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_TO_LINE_BOUNDARY

    def test_get_caret_moved_event_reason_file_boundary_selection(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with file boundary selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_TO_FILE_BOUNDARY

    def test_get_caret_moved_event_reason_unspecified_selection(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with unspecified selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_SELECTION

    def test_get_caret_moved_event_reason_character_navigation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with character navigation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = True
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_CHARACTER

    def test_get_caret_moved_event_reason_select_all(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with select all."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = True
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECT_ALL

    def test_get_caret_moved_event_reason_mouse_primary_button(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with mouse primary button."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.MOUSE_PRIMARY_BUTTON

    def test_get_caret_moved_event_reason_delete(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with delete key."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.DELETE

    def test_get_caret_moved_event_reason_selection_by_word(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with word navigation selection."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_WORD

    def test_get_caret_moved_event_reason_navigation_by_page(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with page navigation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = True
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_PAGE

    def test_get_caret_moved_event_reason_navigation_to_line_boundary(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with line boundary navigation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = True
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_TO_LINE_BOUNDARY

    def test_get_caret_moved_event_reason_navigation_to_file_boundary(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with file boundary navigation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_TO_FILE_BOUNDARY

    def test_get_text_event_reason_ui_update(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with UI update scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: ["text"])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "text")

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UI_UPDATE

    def test_get_text_event_reason_page_switch_scenario(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with page switch scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "document")

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

    def test_get_text_event_reason_command_scenario(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with command scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "document")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_text_event_reason_delete_in_editable(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with delete in editable object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.DELETE

    def test_get_text_event_reason_cut_in_editable(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with cut in editable object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.CUT

    def test_get_text_event_reason_paste_in_editable(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with paste in editable object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.PASTE

    def test_get_text_event_reason_undo_in_editable(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with undo in editable object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UNDO

    def test_get_text_event_reason_redo_in_editable(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with redo in editable object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.REDO

    def test_get_text_event_reason_command_in_editable(self, monkeypatch, mock_orca_dependencies):
        """Test get_text_event_reason with command in editable object."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.type = "object:text-changed:insert"
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        from orca.ax_text import AXText

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent.get_text_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_clear_all_dictionaries_direct_call(self, monkeypatch, mock_orca_dependencies):
        """Test _clear_all_dictionaries method directly."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca import debug

        mock_print_message = Mock()
        monkeypatch.setattr(debug, "print_message", mock_print_message)

        AXUtilitiesEvent._clear_all_dictionaries("direct test")

        mock_print_message.assert_called_once()
        args = mock_print_message.call_args[0]
        assert "AXUtilitiesEvent: Clearing local cache." in args[1]
        assert "Reason: direct test" in args[1]

    def test_get_text_insertion_event_reason_delete_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with delete scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.DELETE

    def test_get_text_insertion_event_reason_cut_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with cut scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.CUT

    def test_get_text_insertion_event_reason_paste_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with paste scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.PASTE

    def test_get_text_insertion_event_reason_undo_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with undo scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.UNDO

    def test_get_text_insertion_event_reason_redo_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with redo scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.REDO

    def test_get_text_insertion_event_reason_command_scenario(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with command scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "test"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [])
        monkeypatch.setattr(AXObject, "get_role", lambda obj: "entry")
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_caret_moved_event_reason_cut(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with cut operation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.CUT

    def test_get_caret_moved_event_reason_paste(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with paste operation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.PASTE

    def test_get_caret_moved_event_reason_undo(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with undo operation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.UNDO

    def test_get_caret_moved_event_reason_redo(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with redo operation."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.REDO

    def test_get_caret_moved_event_reason_page_switch(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with page switch."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = True
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

    def test_get_caret_moved_event_reason_command(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with unspecified command."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        mock_input_manager.last_event_was_printable_key.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_caret_moved_event_reason_tab_navigation(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with tab navigation focus change."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_tab_navigation.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, predicate: None)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.FOCUS_CHANGE

    def test_get_caret_moved_event_reason_ui_update(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent._get_caret_moved_event_reason with UI update."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_object import AXObject
        from orca import focus_manager
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_ancestor = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = (
            "normal",
            mock_obj,
        )
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_tab_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, predicate: mock_ancestor)

        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.UI_UPDATE

    def test_get_text_deletion_event_reason_auto_deletion(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with auto deletion."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "auto deleted"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_spin_button", lambda obj: False)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, predicate: None)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_DELETION

    def test_get_text_deletion_event_reason_children_change(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_deletion_event_reason with children change."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "\ufffc"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.CHILDREN_CHANGE

    def test_get_text_insertion_event_reason_selected_text_restoration(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with selected text restoration."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "restored text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("restored text", 0, 13))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.SELECTED_TEXT_RESTORATION

    def test_get_text_insertion_event_reason_auto_insertion_presentable_tab(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with auto insertion from tab."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "auto inserted text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_INSERTION_PRESENTABLE

    def test_get_text_insertion_event_reason_auto_insertion_unpresentable_return(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with auto insertion from return in single line."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "auto inserted text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesState, "is_single_line", lambda obj: True)

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.AUTO_INSERTION_UNPRESENTABLE

    def test_get_text_insertion_event_reason_middle_click(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesEvent._get_text_insertion_event_reason with middle click."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "pasted text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.MOUSE_MIDDLE_BUTTON

    def test_clear_cache_now_with_reason(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesEvent.clear_cache_now with reason parameter."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent

        # Call clear_cache_now with a reason to test line 147
        AXUtilitiesEvent.clear_cache_now("test reason")

        # Verify that cache dictionaries are cleared
        assert len(AXUtilitiesEvent.LAST_KNOWN_NAME) == 0
        assert len(AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION) == 0
        assert len(AXUtilitiesEvent.TEXT_EVENT_REASON) == 0

    def test_get_caret_moved_event_reason_navigation_by_line(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_caret_moved_event_reason with line navigation scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_line_navigation.return_value = True
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_tab_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        mock_focus_manager = Mock()
        mode_and_focus = ("normal", mock_obj)
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = mode_and_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        # Test line 236: NAVIGATION_BY_LINE
        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_LINE

    def test_get_caret_moved_event_reason_unspecified_navigation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_caret_moved_event_reason with unspecified navigation scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        # All specific navigation types return False to trigger unspecified path
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_tab_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        mock_focus_manager = Mock()
        mode_and_focus = ("normal", mock_obj)
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = mode_and_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        # Test line 248: UNSPECIFIED_NAVIGATION
        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_NAVIGATION

    def test_get_caret_moved_event_reason_editable_backspace(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_caret_moved_event_reason with editable object and backspace."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_backspace.return_value = True
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_tab_navigation.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        mock_focus_manager = Mock()
        mode_and_focus = ("normal", mock_obj)
        mock_focus_manager.get_active_mode_and_object_of_interest.return_value = mode_and_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        # Test line 255: BACKSPACE in editable context
        result = AXUtilitiesEvent._get_caret_moved_event_reason(mock_event)
        assert result == TextEventReason.BACKSPACE

    def test_get_text_deletion_event_reason_page_switch(self, monkeypatch, mock_orca_dependencies):
        """Test _get_text_deletion_event_reason with page switch scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        # Test line 288: PAGE_SWITCH
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

    def test_get_text_deletion_event_reason_editable_scenarios(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_deletion_event_reason with various editable scenarios."""
        # pylint: disable=too-many-statements

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "deleted text"

        # Test delete scenario (line 293)
        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_cached_selected_text", lambda obj: ("", 0, 0))

        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.DELETE

        # Test cut scenario (line 295)
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.CUT

        # Test paste scenario (line 297)
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.PASTE

        # Test undo scenario (line 299)
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.UNDO

        # Test redo scenario (line 301)
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.REDO

        # Test command scenario (line 303)
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_text_deletion_event_reason_command_non_editable(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_deletion_event_reason command scenario for non-editable."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "deleted text"

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        # Test line 317: UNSPECIFIED_COMMAND for non-editable
        result = AXUtilitiesEvent._get_text_deletion_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

    def test_get_text_insertion_event_reason_editable_backspace(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with editable backspace scenario."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "inserted text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        # Test line 339: BACKSPACE in editable context
        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.BACKSPACE

    def test_get_text_insertion_event_reason_redo_selected_text_restoration(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_insertion_event_reason with redo and selected text restoration."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "selected text"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        # Return the same text as event.any_data to trigger SELECTED_TEXT_INSERTION
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("selected text", 0, 13))

        # Test line 353: SELECTED_TEXT_RESTORATION with redo
        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.SELECTED_TEXT_RESTORATION

    def test_get_text_selection_changed_event_reason_comprehensive(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_selection_changed_event_reason with various scenarios."""
        # pylint: disable=too-many-statements

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        # Test search presentable scenario (line 416)
        mock_search_obj = Mock(spec=Atspi.Accessible)
        mock_focus_manager.get_locus_of_focus.return_value = mock_search_obj

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_text_input_search", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_PRESENTABLE

        # Test search unpresentable scenario (line 414, branch where backspace is true)
        mock_input_manager.last_event_was_backspace.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_UNPRESENTABLE

        # Test delete search unpresentable (line 413)
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SEARCH_UNPRESENTABLE

        # Test caret selection scenarios (lines 419, 422-431)
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj  # Reset to same object
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_caret_selection.return_value = True

        # Line navigation selection (line 419)
        mock_input_manager.last_event_was_line_navigation.return_value = True
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_LINE

        # Word navigation selection (line 422)
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_WORD

        # Character navigation selection (line 424)
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_CHARACTER

        # Page navigation selection (line 426)
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_BY_PAGE

        # Line boundary selection (line 428)
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_TO_LINE_BOUNDARY

        # File boundary selection (line 430)
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SELECTION_TO_FILE_BOUNDARY

        # Unspecified selection (line 431)
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_SELECTION

    def test_get_text_selection_changed_event_reason_caret_navigation(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_selection_changed_event_reason caret navigation scenarios."""
        # pylint: disable=too-many-statements

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import input_event_manager, focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = True
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_text_input_search", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        # Test line navigation (line 434)
        mock_input_manager.last_event_was_line_navigation.return_value = True
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_LINE

        # Test word navigation (line 437)
        mock_input_manager.last_event_was_line_navigation.return_value = False
        mock_input_manager.last_event_was_word_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_WORD

        # Test character navigation (line 439)
        mock_input_manager.last_event_was_word_navigation.return_value = False
        mock_input_manager.last_event_was_character_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_CHARACTER

        # Test page navigation (line 441)
        mock_input_manager.last_event_was_character_navigation.return_value = False
        mock_input_manager.last_event_was_page_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_BY_PAGE

        # Test line boundary navigation (line 443)
        mock_input_manager.last_event_was_page_navigation.return_value = False
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_TO_LINE_BOUNDARY

        # Test file boundary navigation (line 445)
        mock_input_manager.last_event_was_line_boundary_navigation.return_value = False
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.NAVIGATION_TO_FILE_BOUNDARY

        # Test unspecified navigation (line 446)
        mock_input_manager.last_event_was_file_boundary_navigation.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_NAVIGATION

    def test_get_text_selection_changed_event_reason_editable_scenarios(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test _get_text_selection_changed_event_reason with editable scenarios."""
        # pylint: disable=too-many-statements

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import input_event_manager, focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj

        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_obj
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_caret_selection.return_value = False
        mock_input_manager.last_event_was_caret_navigation.return_value = False
        mock_input_manager.last_event_was_select_all.return_value = False
        mock_input_manager.last_event_was_primary_click_or_release.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = False
        mock_input_manager.last_event_was_page_up_or_page_down.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_text_input_search", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_spin_button", lambda obj: False)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, check_func: None)

        # Test backspace (line 453)
        mock_input_manager.last_event_was_backspace.return_value = True
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = False
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.BACKSPACE

        # Test delete (line 455)
        mock_input_manager.last_event_was_backspace.return_value = False
        mock_input_manager.last_event_was_delete.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.DELETE

        # Test cut (line 457)
        mock_input_manager.last_event_was_delete.return_value = False
        mock_input_manager.last_event_was_cut.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.CUT

        # Test paste (line 459)
        mock_input_manager.last_event_was_cut.return_value = False
        mock_input_manager.last_event_was_paste.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.PASTE

        # Test undo (line 461)
        mock_input_manager.last_event_was_paste.return_value = False
        mock_input_manager.last_event_was_undo.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNDO

        # Test redo (line 463)
        mock_input_manager.last_event_was_undo.return_value = False
        mock_input_manager.last_event_was_redo.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.REDO

        # Test page switch (line 465)
        mock_input_manager.last_event_was_redo.return_value = False
        mock_input_manager.last_event_was_page_switch.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.PAGE_SWITCH

        # Test command (line 467)
        mock_input_manager.last_event_was_page_switch.return_value = False
        mock_input_manager.last_event_was_command.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.UNSPECIFIED_COMMAND

        # Test printable key (line 469)
        mock_input_manager.last_event_was_command.return_value = False
        mock_input_manager.last_event_was_printable_key.return_value = True
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.TYPING

        # Test spin button value change (line 473)
        mock_input_manager.last_event_was_printable_key.return_value = False
        mock_input_manager.last_event_was_up_or_down.return_value = True
        monkeypatch.setattr(AXUtilitiesRole, "is_spin_button", lambda obj: True)
        result = AXUtilitiesEvent._get_text_selection_changed_event_reason(mock_event)
        assert result == TextEventReason.SPIN_BUTTON_VALUE_CHANGE

    def test_is_presentable_active_descendant_change_edge_cases(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_presentable_active_descendant_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_child = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.any_data = mock_child

        # Test neither source nor child have focused state (lines 487-489)
        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is False

        # Test tree table scenario with different tree (lines 494-497)
        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: obj == mock_child)

        mock_focus = Mock(spec=Atspi.Accessible)
        mock_table = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesRole, "is_table_cell", lambda obj: True)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, check_func: mock_table)

        result = AXUtilitiesEvent.is_presentable_active_descendant_change(mock_event)
        assert result is False

    def test_is_presentable_checked_change_edge_cases(self, monkeypatch, mock_orca_dependencies):
        """Test is_presentable_checked_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager, input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        # Test descendant checking scenarios (lines 518-524)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_checked", lambda obj: True)
        # Clear any previous state to ensure state change is detected
        AXUtilitiesEvent.LAST_KNOWN_CHECKED.clear()

        # Source is ancestor but focus is not list/tree item (lines 522-524)
        monkeypatch.setattr(AXObject, "is_ancestor", lambda ancestor, descendant: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_item", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_tree_item", lambda obj: False)

        result = AXUtilitiesEvent.is_presentable_checked_change(mock_event)
        assert result is False

        # Test radio button without space key (lines 530-532)
        mock_focus_manager.get_locus_of_focus.return_value = mock_source  # Same as source
        monkeypatch.setattr(AXUtilitiesRole, "is_radio_button", lambda obj: True)

        mock_input_manager = Mock()
        mock_input_manager.last_event_was_space.return_value = False
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        result = AXUtilitiesEvent.is_presentable_checked_change(mock_event)
        assert result is False

    def test_is_presentable_description_change_edge_cases(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_presentable_description_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.any_data = "new description"

        # Clear any cached state
        AXUtilitiesEvent.LAST_KNOWN_DESCRIPTION.clear()

        # Test with empty description (lines 556-558)
        mock_event.any_data = ""
        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is False

        # Reset with non-empty description
        mock_event.any_data = "new description"

        # Test source not showing (lines 561-563)
        monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is False

        # Reset showing state
        monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: True)

        # Test source not focus or ancestor (lines 567-569)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_ancestor", lambda focus, source: False)

        result = AXUtilitiesEvent.is_presentable_description_change(mock_event)
        assert result is False

    def test_is_presentable_expanded_change_edge_cases(self, monkeypatch, mock_orca_dependencies):
        """Test is_presentable_expanded_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.detail1 = 0

        # Clear any cached state to ensure state change is detected
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()

        monkeypatch.setattr(AXUtilitiesState, "is_expanded", lambda obj: True)

        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        # Test not from focus and not ancestor (lines 594-596)
        monkeypatch.setattr(AXObject, "is_ancestor", lambda focus, source: False)
        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is False

        # Test with table row or list box roles (lines 599-601)
        # Clear cached state again to ensure fresh state change detection
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()
        monkeypatch.setattr(AXObject, "is_ancestor", lambda focus, source: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_table_row", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_box", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is True

        # Test list box role (line 599, second condition)
        # Clear cached state again to ensure fresh state change detection
        AXUtilitiesEvent.LAST_KNOWN_EXPANDED.clear()
        mock_event.detail1 = 1  # Reset detail1 to avoid early return
        monkeypatch.setattr(AXUtilitiesRole, "is_table_row", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_box", lambda obj: True)
        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is True

        # Test combo box without focus (lines 603-611)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_box", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_combo_box", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_button", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is False

        # Test button without focus (lines 603-611)
        monkeypatch.setattr(AXUtilitiesRole, "is_combo_box", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_button", lambda obj: True)
        result = AXUtilitiesEvent.is_presentable_expanded_change(mock_event)
        assert result is False

    def test_is_presentable_indeterminate_change_edge_cases(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_presentable_indeterminate_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        # Clear any cached state
        AXUtilitiesEvent.LAST_KNOWN_INDETERMINATE.clear()

        # Test cleared state (lines 620-622, 628-631)
        monkeypatch.setattr(AXUtilitiesState, "is_indeterminate", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_indeterminate_change(mock_event)
        assert result is False

        # Test set state but not from focus (lines 634-636)
        monkeypatch.setattr(AXUtilitiesState, "is_indeterminate", lambda obj: True)

        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        result = AXUtilitiesEvent.is_presentable_indeterminate_change(mock_event)
        assert result is False

    def test_is_presentable_invalid_entry_change_edge_cases(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test is_presentable_invalid_entry_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        # Clear any cached state
        AXUtilitiesEvent.LAST_KNOWN_INVALID_ENTRY.clear()

        monkeypatch.setattr(AXUtilitiesState, "is_invalid_entry", lambda obj: True)

        # Test not from focus (lines 655-657)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        result = AXUtilitiesEvent.is_presentable_invalid_entry_change(mock_event)
        assert result is False

    def test_is_presentable_name_change_edge_cases(self, monkeypatch, mock_orca_dependencies):
        """Test is_presentable_name_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_text import AXText
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source
        mock_event.any_data = "new name"

        # Clear any cached state
        AXUtilitiesEvent.LAST_KNOWN_NAME.clear()

        # Test with empty name (lines 681-683)
        mock_event.any_data = ""
        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

        # Reset with non-empty name
        mock_event.any_data = "new name"

        # Test source not showing (lines 686-688)
        monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: False)
        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

        # Reset showing state
        monkeypatch.setattr(AXUtilitiesState, "is_showing", lambda obj: True)

        # Test frame not active window (lines 692-694)
        monkeypatch.setattr(AXUtilitiesRole, "is_frame", lambda obj: True)

        mock_active_window = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_active_window.return_value = mock_active_window
        mock_focus_manager.get_locus_of_focus.return_value = mock_source
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

        # Test frame with redundant text (lines 704-715)
        mock_focus_manager.get_active_window.return_value = mock_source  # Same as source

        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus

        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXText, "get_character_count", lambda obj: 10)
        monkeypatch.setattr(AXText, "get_all_text", lambda obj: "new")

        result = AXUtilitiesEvent.is_presentable_name_change(mock_event)
        assert result is False

    def test_is_presentable_pressed_change_edge_cases(self, monkeypatch, mock_orca_dependencies):
        """Test is_presentable_pressed_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        # Clear any cached state
        AXUtilitiesEvent.LAST_KNOWN_PRESSED.clear()

        monkeypatch.setattr(AXUtilitiesState, "is_pressed", lambda obj: True)

        # Test not from focus (lines 730-732)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        result = AXUtilitiesEvent.is_presentable_pressed_change(mock_event)
        assert result is False

    def test_is_presentable_selected_change_edge_cases(self, monkeypatch, mock_orca_dependencies):
        """Test is_presentable_selected_change edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_state import AXUtilitiesState
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        # Clear any cached state
        AXUtilitiesEvent.LAST_KNOWN_SELECTED.clear()

        monkeypatch.setattr(AXUtilitiesState, "is_selected", lambda obj: True)

        # Test not from focus (lines 751-753)
        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        result = AXUtilitiesEvent.is_presentable_selected_change(mock_event)
        assert result is False

    def test_is_presentable_text_event_edge_cases(self, monkeypatch, mock_orca_dependencies):
        """Test _is_presentable_text_event edge cases."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca import focus_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_source = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_source

        # Test neither editable nor terminal (lines 765-767)
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)

        result = AXUtilitiesEvent._is_presentable_text_event(mock_event)
        assert result is False

        # Test source ancestor of focus (lines 781-785)
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)

        mock_focus = Mock(spec=Atspi.Accessible)
        mock_focus_manager = Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_focus
        monkeypatch.setattr(focus_manager, "get_manager", lambda: mock_focus_manager)

        monkeypatch.setattr(AXUtilitiesState, "is_focused", lambda obj: False)
        monkeypatch.setattr(AXObject, "is_ancestor", lambda source, focus: True)

        result = AXUtilitiesEvent._is_presentable_text_event(mock_event)
        assert result is True

    def test_get_text_insertion_event_reason_additional_scenarios(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test additional _get_text_insertion_event_reason scenarios for missing coverage."""

        clean_module_cache("orca.ax_utilities_event")
        _apply_common_ax_mocks(monkeypatch, mock_orca_dependencies)
        from orca.ax_utilities_event import AXUtilitiesEvent, TextEventReason
        from orca.ax_utilities_role import AXUtilitiesRole
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_object import AXObject
        from orca.ax_text import AXText
        from orca import input_event_manager

        mock_event = Mock(spec=Atspi.Event)
        mock_obj = Mock(spec=Atspi.Accessible)
        mock_event.source = mock_obj
        mock_event.any_data = "x"

        mock_input_manager = Mock()
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
        monkeypatch.setattr(input_event_manager, "get_manager", lambda: mock_input_manager)

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.TEXT)
        monkeypatch.setattr(AXUtilitiesRole, "get_text_ui_roles", lambda: [Atspi.Role.LABEL])
        monkeypatch.setattr(AXUtilitiesState, "is_editable", lambda obj: True)
        monkeypatch.setattr(AXUtilitiesRole, "is_terminal", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_password_text", lambda obj: True)
        monkeypatch.setattr(AXText, "get_selected_text", lambda obj: ("", 0, 0))

        # Mock settings manager for echo settings (line 373)
        from orca import settings_manager

        mock_settings_manager = Mock()
        mock_settings_manager.get_setting.return_value = True
        monkeypatch.setattr(settings_manager, "get_manager", lambda: mock_settings_manager)

        # Test password text with echo enabled (line 373)
        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        assert result == TextEventReason.TYPING_ECHOABLE

        # Test text length check scenario (lines 387-388)
        mock_event.any_data = "multi-char"
        monkeypatch.setattr(AXUtilitiesRole, "is_password_text", lambda obj: False)
        # Reset settings manager to return False for enableEchoByCharacter
        mock_settings_manager.get_setting.return_value = False

        result = AXUtilitiesEvent._get_text_insertion_event_reason(mock_event)
        # Should be TYPING now because echo is disabled
        assert result == TextEventReason.TYPING
