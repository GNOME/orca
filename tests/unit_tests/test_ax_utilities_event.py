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

"""Unit tests for ax_utilities_event.py event-related utilities."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi



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

    # Apply additional mocks that this specific test needs
    monkeypatch.setitem(sys.modules, "orca.focus_manager", Mock())
    monkeypatch.setitem(sys.modules, "orca.input_event_manager", Mock())
    monkeypatch.setitem(sys.modules, "orca.settings_manager", Mock())
    # Fix debug mock to have proper debugFile attribute
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

        monkeypatch.setattr(AXUtilitiesEvent, "is_presentable_description_change",
                           mock_is_presentable_description_change)

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

        monkeypatch.setattr(AXUtilitiesEvent, "is_presentable_pressed_change",
                           mock_is_presentable_pressed_change)

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

        monkeypatch.setattr(AXUtilitiesEvent, "is_presentable_invalid_entry_change",
                           mock_is_presentable_invalid_entry_change)

        result = AXUtilitiesEvent.is_presentable_invalid_entry_change(mock_event)
        assert result is True
