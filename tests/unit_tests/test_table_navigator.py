# Unit tests for table_navigator.py methods.
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

"""Unit tests for table_navigator.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestTableNavigator:
    """Test TableNavigator class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up dependencies for table_navigator module testing."""

        additional_modules = ["orca.input_event_manager"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)
        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.__init__ creates instance with correct default values."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        assert navigator._previous_reported_row is None
        assert navigator._previous_reported_col is None
        assert navigator._last_input_event is None
        assert navigator._enabled is True
        assert navigator._suspended is False
        assert navigator._handlers is not None
        assert navigator._bindings == mock_keybindings_instance
        mock_controller.register_decorated_module.assert_called_with("TableNavigator", navigator)

    @pytest.mark.parametrize(
        "refresh, expects_remove_grabs, expects_is_empty_check",
        [
            pytest.param(False, False, True, id="first_time"),
            pytest.param(True, True, False, id="refresh"),
        ],
    )
    def test_get_bindings_scenarios(
        self, test_context: OrcaTestContext, refresh, expects_remove_grabs, expects_is_empty_check
    ) -> None:
        """Test TableNavigator.get_bindings various scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        if expects_is_empty_check:
            mock_keybindings_instance.is_empty.return_value = True
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.override_key_bindings.return_value = mock_keybindings_instance
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        if refresh:
            result = navigator.get_bindings(refresh=True)
        else:
            result = navigator.get_bindings()
        assert result == mock_keybindings_instance

        if expects_remove_grabs:
            mock_keybindings_instance.remove_key_grabs.assert_called_once()
        if expects_is_empty_check:
            mock_keybindings_instance.is_empty.assert_called()

    def test_get_handlers_first_time(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.get_handlers returns dictionary with all expected handlers."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator.get_handlers()
        assert isinstance(result, dict)
        expected_handlers = [
            "table_navigator_toggle_enabled",
            "table_cell_left",
            "table_cell_right",
            "table_cell_up",
            "table_cell_down",
            "table_cell_first",
            "table_cell_last",
            "table_cell_beginning_of_row",
            "table_cell_end_of_row",
            "table_cell_top_of_column",
            "table_cell_bottom_of_column",
            "set_dynamic_column_headers_row",
            "clear_dynamic_column_headers_row",
            "set_dynamic_row_headers_column",
            "clear_dynamic_row_headers_column",
        ]
        for handler_name in expected_handlers:
            assert handler_name in result

    def test_get_handlers_refresh(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.get_handlers prints debug message when refresh=True."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator.get_handlers(refresh=True)
        assert isinstance(result, dict)
        essential_modules["orca.debug"].print_message.assert_called()

    def test_is_enabled_default_true(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.is_enabled returns True by default."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        assert navigator.is_enabled() is True

    def test_is_enabled_after_disable(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.is_enabled returns False when disabled."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._enabled = False
        assert navigator.is_enabled() is False

    def test_last_input_event_was_navigation_command_none(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test last_input_event_was_navigation_command with None event returns False."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_manager = test_context.Mock()
        essential_modules["orca.input_event_manager"].get_manager.return_value = mock_manager
        mock_manager.last_event_equals_or_is_release_for_event.return_value = False
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator.last_input_event_was_navigation_command()
        assert result is False
        mock_manager.last_event_equals_or_is_release_for_event.assert_not_called()

    def test_last_input_event_was_navigation_command_with_event(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test last_input_event_was_navigation_command with event returns True when matching."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_manager = test_context.Mock()
        essential_modules["orca.input_event_manager"].get_manager.return_value = mock_manager
        mock_manager.last_event_equals_or_is_release_for_event.return_value = True
        mock_event = test_context.Mock()
        mock_event.as_single_line_string.return_value = "test_event"
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._last_input_event = mock_event
        result = navigator.last_input_event_was_navigation_command()
        assert result is True
        mock_manager.last_event_equals_or_is_release_for_event.assert_called_once_with(mock_event)

    @pytest.mark.parametrize(
        "enabled, suspended, expected_enabled_state",
        [
            pytest.param(True, False, True, id="enabled_not_suspended"),
            pytest.param(True, True, False, id="enabled_but_suspended"),
            pytest.param(False, False, False, id="disabled_not_suspended"),
            pytest.param(False, True, False, id="disabled_and_suspended"),
        ],
    )
    def test_setup_bindings_enabled_states(
        self, test_context, enabled, suspended, expected_enabled_state
    ) -> None:
        """Test TableNavigator._setup_bindings creates KeyBindings with correct enabled state."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_keybinding_class = test_context.Mock()
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBinding", new=mock_keybinding_class
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.override_key_bindings.return_value = mock_keybindings_instance
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._enabled = enabled
        navigator._suspended = suspended
        navigator._setup_bindings()
        calls = mock_keybinding_class.call_args_list
        navigation_calls = [call for call in calls if len(call[0]) >= 6]
        if navigation_calls:
            for call in navigation_calls[1:]:
                assert call[0][5] == expected_enabled_state

    @pytest.mark.parametrize(
        "initial_enabled,expected_enabled,expected_message_attr",
        [
            (False, True, "TABLE_NAVIGATION_ENABLED"),
            (True, False, "TABLE_NAVIGATION_DISABLED"),
        ],
    )
    def test_toggle_enabled(
        self,
        test_context: OrcaTestContext,
        initial_enabled: bool,
        expected_enabled: bool,
        expected_message_attr: str,
    ) -> None:
        """Test TableNavigator.toggle_enabled toggles state and presents appropriate message."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._enabled = initial_enabled
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_event = test_context.Mock()
        mock_refresh = test_context.Mock()
        setattr(navigator, "refresh_bindings_and_grabs", mock_refresh)
        result = navigator.toggle_enabled(mock_script, mock_event, notify_user=True)
        assert result is True
        assert navigator._enabled is expected_enabled
        assert navigator._last_input_event is None
        expected_message = getattr(essential_modules["orca.messages"], expected_message_attr)
        mock_script.present_message.assert_called_once_with(expected_message)
        mock_refresh.assert_called_once_with(mock_script, "toggling table navigation")

    def test_toggle_enabled_no_notify(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.toggle_enabled does not present message when notify_user=False."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._enabled = False
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_event = test_context.Mock()
        setattr(navigator, "refresh_bindings_and_grabs", test_context.Mock())
        result = navigator.toggle_enabled(mock_script, mock_event, notify_user=False)
        assert result is True
        assert navigator._enabled is True
        mock_script.present_message.assert_not_called()

    @pytest.mark.parametrize(
        "initial_suspended,new_suspended,should_refresh",
        [
            (False, True, True),
            (True, False, True),
            (False, False, False),
            (True, True, False),
        ],
    )
    def test_suspend_commands(
        self,
        test_context: OrcaTestContext,
        initial_suspended: bool,
        new_suspended: bool,
        should_refresh: bool,
    ) -> None:
        """Test TableNavigator.suspend_commands handles state changes appropriately."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._suspended = initial_suspended
        mock_script = test_context.Mock()
        mock_refresh = test_context.Mock()
        setattr(navigator, "refresh_bindings_and_grabs", mock_refresh)
        reason = "test reason" if new_suspended else ""
        navigator.suspend_commands(mock_script, new_suspended, reason)
        assert navigator._suspended is new_suspended
        if should_refresh:
            mock_refresh.assert_called_once_with(
                mock_script, f"Suspended changed to {new_suspended}"
            )
        else:
            mock_refresh.assert_not_called()

    @pytest.mark.parametrize(
        "is_focusable, has_name, has_children, is_whitespace, expected_result",
        [
            pytest.param(True, False, False, True, False, id="focusable_object"),
            pytest.param(False, True, False, True, False, id="object_with_name"),
            pytest.param(False, False, True, True, False, id="object_with_non_blank_children"),
            pytest.param(False, False, False, False, False, id="object_with_text"),
            pytest.param(False, False, False, True, True, id="blank_object"),
            pytest.param(False, False, True, True, True, id="object_with_only_blank_children"),
        ],
    )
    def test_is_blank(
        self, test_context, is_focusable, has_name, has_children, is_whitespace, expected_result
    ) -> None:
        """Test _is_blank correctly identifies blank objects based on various criteria."""

        essential_modules = self._setup_dependencies(test_context)
        test_context.patch(
            "orca.table_navigator.AXUtilities.is_focusable", return_value=is_focusable
        )
        test_context.patch(
            "orca.table_navigator.AXObject.get_name", return_value="name" if has_name else ""
        )
        test_context.patch(
            "orca.table_navigator.AXObject.get_child_count", return_value=1 if has_children else 0
        )
        test_context.patch(
            "orca.table_navigator.AXText.is_whitespace_or_empty", return_value=is_whitespace
        )
        if has_children:
            mock_child = test_context.Mock()
            test_context.patch(
                "orca.table_navigator.AXObject.iter_children", return_value=[mock_child]
            )
            # For the recursive call on child, configure mock to handle both expected cases
            if expected_result and not is_focusable and not has_name:
                # Child should also be blank - override child-specific mocking
                test_context.patch(
                    "orca.table_navigator.AXUtilities.is_focusable",
                    side_effect=lambda obj: False if obj == mock_child else is_focusable,
                )
                test_context.patch(
                    "orca.table_navigator.AXObject.get_name",
                    side_effect=lambda obj: (
                        "" if obj == mock_child else ("name" if has_name else "")
                    ),
                )
                test_context.patch(
                    "orca.table_navigator.AXObject.get_child_count",
                    side_effect=lambda obj: 0 if obj == mock_child else (1 if has_children else 0),
                )
                test_context.patch(
                    "orca.table_navigator.AXText.is_whitespace_or_empty",
                    side_effect=lambda obj: True if obj == mock_child else is_whitespace,
                )
            else:
                # Child should not be blank - make it focusable to stop recursion
                test_context.patch(
                    "orca.table_navigator.AXUtilities.is_focusable",
                    side_effect=lambda obj: True if obj == mock_child else is_focusable,
                )
        else:
            test_context.patch(
                "orca.table_navigator.AXObject.iter_children", return_value=[]
            )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        result = navigator._is_blank(mock_obj)
        assert result == expected_result

    def test_get_current_cell_basic(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator._get_current_cell returns focus manager's locus when it is a cell."""

        essential_modules = self._setup_dependencies(test_context)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_cell
        test_context.patch(
            "orca.table_navigator.focus_manager.get_manager", return_value=mock_focus_manager
        )
        test_context.patch(
            "orca.table_navigator.AXObject.get_parent", return_value=None
        )

        def mock_is_cell_or_header(obj):
            return obj == mock_cell

        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", new=mock_is_cell_or_header
        )
        test_context.patch(
            "orca.table_navigator.AXObject.find_ancestor", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.debug.print_tokens", return_value=None
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator._get_current_cell()
        assert result == mock_cell

    def test_get_current_cell_nested(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator._get_current_cell returns parent when it is also a table cell."""

        essential_modules = self._setup_dependencies(test_context)
        mock_focus_manager = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager.return_value = mock_focus_manager
        mock_inner_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_parent_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager.get_locus_of_focus.return_value = mock_inner_cell
        test_context.patch(
            "orca.table_navigator.AXObject.get_parent",
            side_effect=lambda obj: mock_parent_cell if obj == mock_inner_cell else None,
        )

        def mock_is_table_cell(obj):
            return obj in [mock_inner_cell, mock_parent_cell]

        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", new=mock_is_table_cell
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator._get_current_cell()
        assert result == mock_parent_cell

    def test_get_cell_coordinates_basic(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator._get_cell_coordinates returns coordinates from AXTable."""

        essential_modules = self._setup_dependencies(test_context)
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates",
            return_value=(2, 3),
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        result = navigator._get_cell_coordinates(mock_cell)
        assert result == (2, 3)

    def test_get_cell_coordinates_with_previous(self, test_context: OrcaTestContext) -> None:
        """Test _get_cell_coordinates returns previous coordinates when cell matches."""

        essential_modules = self._setup_dependencies(test_context)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates",
            return_value=(2, 3),
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_at", return_value=mock_cell
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._previous_reported_row = 1
        navigator._previous_reported_col = 2
        result = navigator._get_cell_coordinates(mock_cell)
        assert result == (1, 2)

    @pytest.mark.parametrize(
        "direction, boundary_check, boundary_message, get_next_cell_method",
        [
            pytest.param(
                "left", "is_start_of_row", "TABLE_ROW_BEGINNING", "get_cell_on_left", id="move_left"
            ),
            pytest.param(
                "right", "is_end_of_row", "TABLE_ROW_END", "get_cell_on_right", id="move_right"
            ),
            pytest.param(
                "up", "is_top_of_column", "TABLE_COLUMN_TOP", "get_cell_above", id="move_up"
            ),
            pytest.param(
                "down",
                "is_bottom_of_column",
                "TABLE_COLUMN_BOTTOM",
                "get_cell_below",
                id="move_down",
            ),
        ],
    )
    def test_move_direction_scenarios(
        self,
        test_context: OrcaTestContext,
        direction: str,
        boundary_check: str,
        boundary_message: str,
        get_next_cell_method: str,
    ) -> None:
        """Test TableNavigator move methods for various scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        move_method = getattr(navigator, f"move_{direction}")

        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        result = move_method(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )
        assert navigator._last_input_event == mock_event

        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            f"orca.table_navigator.AXTable.{boundary_check}", return_value=True
        )
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_cell))
        mock_script.reset_mock()
        result = move_method(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_with(
            getattr(essential_modules["orca.messages"], boundary_message)
        )

        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_next_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            f"orca.table_navigator.AXTable.{boundary_check}", return_value=False
        )
        test_context.patch(
            f"orca.table_navigator.AXTable.{get_next_cell_method}", return_value=mock_next_cell
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        setattr(navigator, "_get_cell_coordinates", test_context.Mock(return_value=(1, 2)))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script.reset_mock()
        result = move_method(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once()
        call_args = mock_present_cell.call_args[0]
        assert call_args[0] == mock_script
        assert call_args[1] == mock_next_cell
        assert call_args[4] == mock_current_cell
        assert call_args[5] is True

    def test_move_left_successful(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_left successfully moves to left cell and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_left_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_start_of_row", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_on_left", return_value=mock_left_cell
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        setattr(navigator, "_get_cell_coordinates", test_context.Mock(return_value=(1, 2)))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_left(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_left_cell, 1, 1, mock_current_cell, True
        )

    def test_move_right_successful(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_right successfully moves to right cell and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_right_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_end_of_row", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_on_right", return_value=mock_right_cell
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        setattr(navigator, "_get_cell_coordinates", test_context.Mock(return_value=(1, 2)))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_right(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_right_cell, 1, 3, mock_current_cell, True
        )

    def test_move_up_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_up presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_up(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )
        assert navigator._last_input_event == mock_event

    def test_move_up_at_top_of_column(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_up presents column top message when at top of column."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_top_of_column", return_value=True
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_up(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_COLUMN_TOP
        )

    def test_move_up_successful(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_up successfully moves to cell above and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_up_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_top_of_column", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_above", return_value=mock_up_cell
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        setattr(navigator, "_get_cell_coordinates", test_context.Mock(return_value=(2, 1)))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_up(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_up_cell, 1, 1, mock_current_cell, True
        )

    def test_move_down_successful(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_down successfully moves to cell below and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_down_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_bottom_of_column", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_below", return_value=mock_down_cell
        )
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        setattr(navigator, "_get_cell_coordinates", test_context.Mock(return_value=(1, 1)))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_down(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_down_cell, 2, 1, mock_current_cell, True
        )

    def test_move_to_first_cell_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test move_to_first_cell presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_first_cell(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_move_to_first_cell_successful(self, test_context: OrcaTestContext) -> None:
        """Test move_to_first_cell successfully moves to first cell and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_first_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_first_cell", return_value=mock_first_cell
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_first_cell(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_first_cell, 0, 0, mock_current_cell, True
        )

    def test_present_cell_not_cell_or_header(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator._present_cell returns early when object is not a cell or header."""

        essential_modules = self._setup_dependencies(test_context)
        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", return_value=False
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_script = test_context.Mock()
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_previous_cell = test_context.Mock(spec=Atspi.Accessible)
        navigator._present_cell(mock_script, mock_cell, 1, 2, mock_previous_cell)
        assert navigator._previous_reported_row != 1
        assert navigator._previous_reported_col != 2

    def test_present_cell_successful(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator._present_cell sets focus, coordinates, and presents cell."""

        essential_modules = self._setup_dependencies(test_context)
        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", return_value=True
        )
        test_context.patch(
            "orca.table_navigator.AXObject.grab_focus", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXObject.find_descendant", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXObject.supports_text", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_spans", return_value=(1, 1)
        )
        mock_focus_manager = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager.return_value = mock_focus_manager
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_script = test_context.Mock()
        mock_script.utilities.grab_focus_when_setting_caret.return_value = False
        mock_script.utilities.is_gui_cell.return_value = False
        mock_script.present_object = test_context.Mock()
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_previous_cell = test_context.Mock(spec=Atspi.Accessible)
        navigator._present_cell(mock_script, mock_cell, 1, 2, mock_previous_cell)
        assert navigator._previous_reported_row == 1
        assert navigator._previous_reported_col == 2
        mock_focus_manager.set_locus_of_focus.assert_called()
        mock_script.present_object.assert_called_once_with(
            mock_cell, offset=0, priorObj=mock_previous_cell, interrupt=True
        )

    def test_get_navigator(self, test_context: OrcaTestContext) -> None:
        """Test table_navigator.get_navigator returns singleton TableNavigator instance."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca import table_navigator

        navigator1 = table_navigator.get_navigator()
        navigator2 = table_navigator.get_navigator()
        assert navigator1 is navigator2
        assert isinstance(navigator1, table_navigator.TableNavigator)

    def test_get_current_cell_needs_ancestor_search(self, test_context: OrcaTestContext) -> None:
        """Test _get_current_cell when cell is not table cell and needs ancestor search."""

        essential_modules = self._setup_dependencies(test_context)
        mock_initial_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_initial_cell
        test_context.patch(
            "orca.table_navigator.focus_manager.get_manager", return_value=mock_focus_manager
        )
        test_context.patch(
            "orca.table_navigator.AXObject.get_parent", return_value=None
        )

        def mock_is_cell_or_header(obj):
            return obj == mock_ancestor_cell

        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", new=mock_is_cell_or_header
        )
        test_context.patch(
            "orca.table_navigator.AXObject.find_ancestor", return_value=mock_ancestor_cell
        )
        test_context.patch(
            "orca.table_navigator.debug.print_tokens", return_value=None
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator._get_current_cell()
        assert result == mock_ancestor_cell

    def test_move_left_skip_blank_cells(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_left skipping blank cells when setting is enabled."""

        essential_modules = self._setup_dependencies(test_context)
        mock_settings_manager = test_context.Mock()
        mock_settings_manager.get_setting.return_value = True  # skipBlankCells = True
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_script = test_context.Mock()
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_blank_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_final_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates", return_value=(1, 1)
        )
        test_context.patch(
            "orca.table_navigator.AXTable.is_start_of_row",
            side_effect=lambda cell: cell == mock_final_cell,
        )
        cell_sequence = [mock_blank_cell, mock_final_cell]
        call_count = [0]

        def mock_get_cell_on_left(_cell):
            if call_count[0] < len(cell_sequence):
                result = cell_sequence[call_count[0]]
                call_count[0] += 1
                return result
            return None

        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_on_left", new=mock_get_cell_on_left
        )

        def mock_is_blank(cell):
            return cell == mock_blank_cell

        test_context.patch(
            "orca.table_navigator.debug.print_tokens", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.TableNavigator._present_cell", return_value=None
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_is_blank", mock_is_blank)
        result = navigator.move_left(mock_script, mock_current_cell)
        assert result is True

    def test_move_right_at_end_of_row(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_right when at end of row returns True and notifies user."""

        essential_modules = self._setup_dependencies(test_context)
        mock_settings_manager = test_context.Mock()
        mock_settings_manager.get_setting.return_value = False  # skipBlankCells = False
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_script = test_context.Mock()
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates", return_value=(1, 5)
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_on_right", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXTable.is_end_of_row", return_value=True
        )
        test_context.patch(
            "orca.table_navigator.debug.print_tokens", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.TableNavigator._present_cell", return_value=None
        )
        mock_focus_manager = test_context.Mock()
        mock_focus_manager.get_locus_of_focus.return_value = mock_current_cell
        test_context.patch(
            "orca.table_navigator.focus_manager.get_manager", return_value=mock_focus_manager
        )
        test_context.patch(
            "orca.table_navigator.AXObject.get_parent", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", return_value=True
        )
        test_context.patch(
            "orca.table_navigator.AXObject.find_ancestor", return_value=None
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        result = navigator.move_right(mock_script)
        # move_right returns True even at end of row, but presents a message
        assert result is True
        mock_script.present_message.assert_called_once()

    def test_refresh_bindings_and_grabs(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.refresh_bindings_and_grabs removes old bindings and adds new ones."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        mock_binding = test_context.Mock()
        mock_keybindings_instance.key_bindings = [mock_binding]
        mock_new_bindings = test_context.Mock()
        mock_new_bindings.key_bindings = [mock_binding]
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "get_handlers", test_context.Mock(return_value={}))
        setattr(navigator, "get_bindings", test_context.Mock(return_value=mock_new_bindings))
        mock_script = test_context.Mock()
        navigator.refresh_bindings_and_grabs(mock_script, "test reason")
        mock_script.key_bindings.remove.assert_called_with(mock_binding, include_grabs=True)
        mock_script.key_bindings.add.assert_called()
        essential_modules["orca.debug"].print_message.assert_called()

    def test_move_to_last_cell_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test move_to_last_cell presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_last_cell(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )
        assert navigator._last_input_event == mock_event

    def test_move_to_last_cell_successful(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.move_to_last_cell successfully moves to last cell and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_last_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_last_cell", return_value=mock_last_cell
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_row_count", return_value=5
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_column_count", return_value=3
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_last_cell(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_last_cell, 5, 3, mock_current_cell, True
        )

    def test_move_to_top_of_column_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test move_to_top_of_column presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_top_of_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_move_to_top_of_column_already_at_top(self, test_context: OrcaTestContext) -> None:
        """Test move_to_top_of_column presents column top message when already at top."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_top_of_column", return_value=True
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_top_of_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_COLUMN_TOP
        )

    def test_move_to_top_of_column_successful(self, test_context: OrcaTestContext) -> None:
        """Test move_to_top_of_column successfully moves to top of column and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_top_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_top_of_column", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_top_of_column", return_value=mock_top_cell
        )

        def mock_get_cell_coordinates(cell, prefer_attribute=False):  # pylint: disable=unused-argument
            if cell == mock_current_cell:
                return (3, 1)
            if cell == mock_top_cell:
                return (0, 1)
            return (0, 0)

        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates", new=mock_get_cell_coordinates
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_top_of_column(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_top_cell, 3, 1, mock_current_cell, True
        )

    def test_move_to_bottom_of_column_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test move_to_bottom_of_column presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_bottom_of_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_move_to_bottom_of_column_already_at_bottom(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test move_to_bottom_of_column presents column bottom message when already at bottom."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_bottom_of_column", return_value=True
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_bottom_of_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_COLUMN_BOTTOM
        )

    def test_move_to_bottom_of_column_successful(self, test_context: OrcaTestContext) -> None:
        """Test move_to_bottom_of_column successfully moves to bottom of column and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_bottom_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_bottom_of_column", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_bottom_of_column", return_value=mock_bottom_cell
        )

        def mock_get_cell_coordinates(cell, prefer_attribute=False):  # pylint: disable=unused-argument
            if cell == mock_current_cell:
                return (1, 2)
            if cell == mock_bottom_cell:
                return (4, 2)
            return (0, 0)

        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates", new=mock_get_cell_coordinates
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_bottom_of_column(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_bottom_cell, 1, 2, mock_current_cell, True
        )

    def test_move_to_beginning_of_row_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test move_to_beginning_of_row presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_beginning_of_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_move_to_beginning_of_row_already_at_start(self, test_context: OrcaTestContext) -> None:
        """Test move_to_beginning_of_row presents row beginning message when already at start."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_start_of_row", return_value=True
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_beginning_of_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_ROW_BEGINNING
        )

    def test_move_to_beginning_of_row_successful(self, test_context: OrcaTestContext) -> None:
        """Test move_to_beginning_of_row successfully moves to beginning of row and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_start_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_start_of_row", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_start_of_row", return_value=mock_start_cell
        )

        def mock_get_cell_coordinates(cell, prefer_attribute=False):  # pylint: disable=unused-argument
            if cell == mock_start_cell:
                return (2, 0)
            return (2, 3)

        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates", new=mock_get_cell_coordinates
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_beginning_of_row(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_start_cell, 2, 0, mock_current_cell, True
        )

    def test_move_to_end_of_row_not_in_table(self, test_context: OrcaTestContext) -> None:
        """Test move_to_end_of_row presents not in table message when current cell is None."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_end_of_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_move_to_end_of_row_already_at_end(self, test_context: OrcaTestContext) -> None:
        """Test move_to_end_of_row presents row end message when already at end."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_end_of_row", return_value=True
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_end_of_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_ROW_END
        )

    def test_move_to_end_of_row_successful(self, test_context: OrcaTestContext) -> None:
        """Test move_to_end_of_row successfully moves to end of row and presents it."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_end_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.is_end_of_row", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_end_of_row", return_value=mock_end_cell
        )

        def mock_get_cell_coordinates(cell, prefer_attribute=False):  # pylint: disable=unused-argument
            if cell == mock_end_cell:
                return (2, 4)
            return (2, 1)

        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates", new=mock_get_cell_coordinates
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_present_cell = test_context.Mock()
        setattr(navigator, "_present_cell", mock_present_cell)
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.move_to_end_of_row(mock_script, mock_event)
        assert result is True
        mock_present_cell.assert_called_once_with(
            mock_script, mock_end_cell, 2, 4, mock_current_cell, True
        )

    def test_set_dynamic_column_headers_row_not_in_table(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_dynamic_column_headers_row presents not in table message.

        Test case when current cell is None.
        """

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.set_dynamic_column_headers_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_set_dynamic_column_headers_row_successful(self, test_context: OrcaTestContext) -> None:
        """Test set_dynamic_column_headers_row successfully sets column headers row."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates",
            return_value=(1, 2),
        )
        test_context.patch(
            "orca.table_navigator.AXTable.set_dynamic_column_headers_row", return_value=None
        )
        essential_modules["orca.messages"].DYNAMIC_COLUMN_HEADER_SET = "Column header row set to %d"
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.set_dynamic_column_headers_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with("Column header row set to 2")

    def test_clear_dynamic_column_headers_row_not_in_table(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test clear_dynamic_column_headers_row presents not in table message.

        Test case when current cell is None.
        """

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.clear_dynamic_column_headers_row(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_clear_dynamic_column_headers_row_successful(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test clear_dynamic_column_headers_row successfully clears column headers row."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager.return_value = mock_focus_manager
        mock_focus_manager.get_locus_of_focus.return_value = mock_current_cell
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.clear_dynamic_column_headers_row", return_value=None
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.clear_dynamic_column_headers_row(mock_script, mock_event)
        assert result is True
        mock_script.interrupt_presentation.assert_called_once()
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].DYNAMIC_COLUMN_HEADER_CLEARED
        )

    def test_set_dynamic_row_headers_column_not_in_table(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_dynamic_row_headers_column presents not in table message.

        Test case when current cell is None.
        """

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.set_dynamic_row_headers_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_set_dynamic_row_headers_column_successful(self, test_context: OrcaTestContext) -> None:
        """Test set_dynamic_row_headers_column successfully sets row headers column."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates",
            return_value=(2, 1),
        )
        test_context.patch(
            "orca.table_navigator.AXTable.set_dynamic_row_headers_column",
            return_value=None,
        )
        essential_modules["orca.messages"].DYNAMIC_ROW_HEADER_SET = "Row header column set to %s"
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_script = test_context.Mock()
        mock_script.utilities.convert_column_to_string.return_value = "B"
        mock_event = test_context.Mock()
        result = navigator.set_dynamic_row_headers_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with("Row header column set to B")

    def test_clear_dynamic_row_headers_column_not_in_table(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test clear_dynamic_row_headers_column presents not in table message.

        Test case when current cell is None.
        """

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=None))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.clear_dynamic_row_headers_column(mock_script, mock_event)
        assert result is True
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].TABLE_NOT_IN_A
        )

    def test_clear_dynamic_row_headers_column_successful(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test clear_dynamic_row_headers_column successfully clears row headers column."""

        essential_modules = self._setup_dependencies(test_context)
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        mock_current_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_focus_manager = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager.return_value = mock_focus_manager
        mock_focus_manager.get_locus_of_focus.return_value = mock_current_cell
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.clear_dynamic_row_headers_column", return_value=None
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        setattr(navigator, "_get_current_cell", test_context.Mock(return_value=mock_current_cell))
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()
        result = navigator.clear_dynamic_row_headers_column(mock_script, mock_event)
        assert result is True
        mock_script.interrupt_presentation.assert_called_once()
        mock_script.present_message.assert_called_once_with(
            essential_modules["orca.messages"].DYNAMIC_ROW_HEADER_CLEARED
        )

    def test_get_cell_coordinates_with_different_previous_cell(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _get_cell_coordinates returns actual coordinates when previous cell differs."""

        essential_modules = self._setup_dependencies(test_context)
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_table = test_context.Mock(spec=Atspi.Accessible)
        mock_different_cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_coordinates",
            return_value=(2, 3),
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_table", return_value=mock_table
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_at", return_value=mock_different_cell
        )
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        navigator._previous_reported_row = 1
        navigator._previous_reported_col = 2
        result = navigator._get_cell_coordinates(mock_cell)
        assert result == (2, 3)

    def test_present_cell_with_settings_enabled(self, test_context: OrcaTestContext) -> None:
        """Test _present_cell with speakCellCoordinates and speakCellSpan enabled."""

        essential_modules = self._setup_dependencies(test_context)
        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", return_value=True
        )
        test_context.patch(
            "orca.table_navigator.AXObject.grab_focus", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXObject.find_descendant", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXObject.supports_text", return_value=False
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_spans", return_value=(2, 3)
        )
        mock_focus_manager = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager.return_value = mock_focus_manager
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager

        def mock_get_setting(setting):
            if setting == "speakCellCoordinates":
                return True
            if setting == "speakCellSpan":
                return True
            return False

        mock_settings_manager.get_setting.side_effect = mock_get_setting
        essential_modules["orca.messages"].TABLE_CELL_COORDINATES = "Row %(row)s, column %(column)s"
        essential_modules["orca.messages"].cell_span.return_value = "spans 2 rows and 3 columns"
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_script = test_context.Mock()
        mock_script.utilities.grab_focus_when_setting_caret.return_value = False
        mock_script.utilities.is_gui_cell.return_value = False
        mock_script.present_object = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_previous_cell = test_context.Mock(spec=Atspi.Accessible)
        navigator._present_cell(mock_script, mock_cell, 1, 2, mock_previous_cell)
        assert navigator._previous_reported_row == 1
        assert navigator._previous_reported_col == 2
        mock_focus_manager.set_locus_of_focus.assert_called()
        mock_script.present_object.assert_called_once_with(
            mock_cell, offset=0, priorObj=mock_previous_cell, interrupt=True
        )
        assert mock_script.present_message.call_count == 2

    def test_present_cell_with_text_descendant_and_gui_cell(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _present_cell when cell has text descendant and is gui cell."""

        essential_modules = self._setup_dependencies(test_context)
        mock_text_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch(
            "orca.table_navigator.AXUtilities.is_table_cell_or_header", return_value=True
        )
        test_context.patch(
            "orca.table_navigator.AXObject.grab_focus", return_value=None
        )
        test_context.patch(
            "orca.table_navigator.AXObject.find_descendant", return_value=mock_text_obj
        )
        test_context.patch(
            "orca.table_navigator.AXObject.supports_text",
            side_effect=lambda obj: obj == mock_text_obj,
        )
        test_context.patch(
            "orca.table_navigator.AXTable.get_cell_spans", return_value=(1, 1)
        )
        mock_focus_manager = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager.return_value = mock_focus_manager
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        mock_controller = test_context.Mock()
        essential_modules["orca.dbus_service"].get_remote_controller.return_value = mock_controller
        mock_keybindings_class = test_context.Mock()
        mock_keybindings_instance = test_context.Mock()
        mock_keybindings_class.return_value = mock_keybindings_instance
        test_context.patch(
            "orca.table_navigator.keybindings.KeyBindings", new=mock_keybindings_class
        )
        from orca.table_navigator import TableNavigator

        navigator = TableNavigator()
        mock_script = test_context.Mock()
        mock_script.utilities.grab_focus_when_setting_caret.return_value = True
        mock_script.utilities.is_gui_cell.return_value = True
        mock_script.utilities.set_caret_position = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        mock_cell = test_context.Mock(spec=Atspi.Accessible)
        mock_previous_cell = test_context.Mock(spec=Atspi.Accessible)
        navigator._present_cell(mock_script, mock_cell, 1, 2, mock_previous_cell)
        mock_focus_manager.set_locus_of_focus.assert_called_with(None, mock_text_obj, False)
        assert navigator._previous_reported_row == 1
        assert navigator._previous_reported_col == 2

    def test_get_skip_blank_cells(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.get_skip_blank_cells returns setting value."""

        essential_modules = self._setup_dependencies(test_context)
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = True
        from orca.table_navigator import get_navigator

        nav = get_navigator()
        result = nav.get_skip_blank_cells()
        assert result is True
        mock_settings_manager.get_setting.assert_called_with("skipBlankCells")

    def test_set_skip_blank_cells(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.set_skip_blank_cells updates setting."""

        essential_modules = self._setup_dependencies(test_context)
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = False
        from orca.table_navigator import get_navigator

        nav = get_navigator()
        result = nav.set_skip_blank_cells(True)
        assert result is True
        mock_settings_manager.set_setting.assert_called_with("skipBlankCells", True)

    def test_set_skip_blank_cells_no_change(self, test_context: OrcaTestContext) -> None:
        """Test TableNavigator.set_skip_blank_cells returns early if value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        mock_settings_manager = test_context.Mock()
        essential_modules["orca.settings_manager"].get_manager.return_value = mock_settings_manager
        mock_settings_manager.get_setting.return_value = True
        from orca.table_navigator import get_navigator

        nav = get_navigator()
        result = nav.set_skip_blank_cells(True)
        assert result is True
        mock_settings_manager.set_setting.assert_not_called()
