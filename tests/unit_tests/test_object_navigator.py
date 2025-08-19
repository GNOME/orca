# Unit tests for object_navigator.py methods.
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
# pylint: disable=too-many-locals

"""Unit tests for object_navigator.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestObjectNavigator:
    """Test ObjectNavigator class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for object_navigator dependencies."""

        import sys

        essential_modules = test_context._setup_essential_modules(
            [
                "gi",
                "gi.repository",
                "gi.repository.Atspi",
                "orca.cmdnames",
                "orca.dbus_service",
                "orca.debug",
                "orca.focus_manager",
                "orca.input_event",
                "orca.keybindings",
                "orca.messages",
                "orca.ax_event_synthesizer",
                "orca.ax_object",
                "orca.ax_utilities",
            ]
        )

        atspi_mock = essential_modules["gi.repository.Atspi"]
        atspi_accessible_mock = test_context.Mock()
        atspi_accessible_mock.get_parent = test_context.Mock(return_value=None)
        atspi_accessible_mock.get_child_count = test_context.Mock(return_value=0)
        atspi_accessible_mock.get_child_at_index = test_context.Mock(return_value=None)
        atspi_mock.Accessible = atspi_accessible_mock

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        controller_mock.reset_mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(return_value=controller_mock)

        def mock_command_decorator(func):
            return func

        dbus_service_mock.command = mock_command_decorator

        if "orca.object_navigator" in sys.modules:
            object_navigator_module = sys.modules["orca.object_navigator"]
            if not hasattr(object_navigator_module, "_original_navigator"):
                setattr(
                    object_navigator_module,
                    "_original_navigator",
                    getattr(object_navigator_module, "_navigator", None),
                )
            setattr(object_navigator_module, "_navigator", test_context.Mock())

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_instance_mock = test_context.Mock()
        keybindings_instance_mock.is_empty = test_context.Mock(return_value=True)
        keybindings_instance_mock.remove_key_grabs = test_context.Mock()
        keybindings_mock.KeyBindings = test_context.Mock(return_value=keybindings_instance_mock)

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject = test_context.Mock()
        ax_object_mock.AXObject.get_parent = test_context.Mock(return_value=None)
        ax_object_mock.AXObject.get_child_count = test_context.Mock(return_value=0)
        ax_object_mock.AXObject.iter_children = test_context.Mock(return_value=[])

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.AXUtilities = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_focused = test_context.Mock(return_value=False)
        ax_utilities_mock.AXUtilities.is_paragraph = test_context.Mock(return_value=True)
        ax_utilities_mock.AXUtilities.is_layout_only = test_context.Mock(return_value=False)

        focus_manager_mock = essential_modules["orca.focus_manager"]
        focus_manager_mock.get_manager = test_context.Mock()
        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_locus_of_focus = test_context.Mock(return_value=None)
        focus_manager_instance.get_active_mode_and_object_of_interest = test_context.Mock(
            return_value=("default", None)
        )
        focus_manager_mock.get_manager.return_value = focus_manager_instance

        ax_event_synthesizer_mock = essential_modules["orca.ax_event_synthesizer"]
        ax_event_synthesizer_mock.AXEventSynthesizer = test_context.Mock()
        ax_event_synthesizer_mock.AXEventSynthesizer.try_all_clickable_actions = test_context.Mock(
            return_value=False
        )
        ax_event_synthesizer_mock.AXEventSynthesizer.click_object = test_context.Mock()

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.OBJECT_NAVIGATOR_PARENT = "objectNavigatorParent"
        cmdnames_mock.OBJECT_NAVIGATOR_FIRST_CHILD = "objectNavigatorFirstChild"
        cmdnames_mock.OBJECT_NAVIGATOR_NEXT_SIBLING = "objectNavigatorNextSibling"
        cmdnames_mock.OBJECT_NAVIGATOR_PREVIOUS_SIBLING = "objectNavigatorPreviousSibling"
        cmdnames_mock.OBJECT_NAVIGATOR_TOGGLE_SIMPLIFY = "objectNavigatorToggleSimplify"
        cmdnames_mock.OBJECT_NAVIGATOR_PERFORM_ACTION = "objectNavigatorPerformAction"

        messages_mock = essential_modules["orca.messages"]
        messages_mock.OBJECT_NAVIGATOR_NO_PARENT = "No parent"
        messages_mock.OBJECT_NAVIGATOR_NO_CHILD = "No child"
        messages_mock.OBJECT_NAVIGATOR_NO_SIBLING = "No sibling"
        messages_mock.OBJECT_NAVIGATOR_SIMPLIFY_ON = "Simplify navigation on"
        messages_mock.OBJECT_NAVIGATOR_SIMPLIFY_OFF = "Simplify navigation off"

        atspi_mock.ModifierType = test_context.Mock()
        atspi_mock.ModifierType.ALT = 3
        atspi_mock.ModifierType.CONTROL = 2
        atspi_mock.ModifierType.SHIFT = 0

        return essential_modules

    def test_init_creates_navigator_with_defaults(self, test_context: OrcaTestContext) -> None:
        """Test ObjectNavigator initialization with default settings."""

        self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator: ObjectNavigator = ObjectNavigator()
        assert navigator._navigator_focus is None
        assert navigator._last_navigator_focus is None
        assert navigator._last_locus_of_focus is None
        assert navigator._simplify is True
        assert navigator._handlers is not None
        assert navigator._bindings is not None

    def test_init_registers_dbus_commands(self, test_context: OrcaTestContext) -> None:
        """Test ObjectNavigator registers D-Bus commands during initialization."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        dbus_service = essential_modules["orca.dbus_service"]
        controller = dbus_service.get_remote_controller.return_value
        controller.register_decorated_module.reset_mock()
        navigator = ObjectNavigator()
        controller.register_decorated_module.assert_called_once_with("ObjectNavigator", navigator)

    def test_get_bindings_returns_existing_when_not_empty(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_bindings returns existing bindings when not empty."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        keybindings_instance = essential_modules["orca.keybindings"].KeyBindings.return_value
        keybindings_instance.is_empty.return_value = False
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        bindings = navigator.get_bindings()
        assert bindings is not None
        assert bindings == navigator._bindings

    def test_get_bindings_creates_new_when_empty(self, test_context: OrcaTestContext) -> None:
        """Test get_bindings creates new bindings when current bindings are empty."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        bindings = navigator.get_bindings()
        assert bindings is not None
        assert essential_modules["orca.keybindings"].KeyBindings.call_count >= 2

    def test_get_bindings_refresh_removes_grabs_and_recreates(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_bindings with refresh removes key grabs and recreates bindings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        keybindings_mock = essential_modules["orca.keybindings"].KeyBindings.return_value
        bindings = navigator.get_bindings(refresh=True)
        keybindings_mock.remove_key_grabs.assert_called_once()
        assert bindings is not None

    @pytest.mark.parametrize(
        "refresh",
        [
            pytest.param(False, id="no_refresh"),
            pytest.param(True, id="refresh"),
        ],
    )
    def test_get_handlers(self, test_context: OrcaTestContext, refresh: bool) -> None:
        """Test get_handlers with refresh parameter."""

        self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        original_handlers = navigator._handlers if not refresh else None
        handlers = navigator.get_handlers(refresh=refresh)
        assert handlers is not None
        assert isinstance(handlers, dict)

        if not refresh:
            assert handlers == original_handlers

    def test_include_in_simple_navigation_basic_object(self, test_context: OrcaTestContext) -> None:
        """Test _include_in_simple_navigation with basic accessible object."""

        self._setup_dependencies(test_context)
        mock_obj = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        result = navigator._include_in_simple_navigation(mock_obj)
        assert result is True

    def test_exclude_from_simple_navigation_with_script(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _exclude_from_simple_navigation with script parameter."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        result = navigator._exclude_from_simple_navigation(mock_script, mock_obj)
        assert result is False

    def test_children_returns_list_for_object_with_children(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _children returns list of child objects."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_child = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_child_count.return_value = 1
        ax_object.iter_children.return_value = [mock_child]
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        children = navigator._children(mock_script, mock_obj)
        assert isinstance(children, list)
        assert len(children) == 1
        assert children[0] == mock_child

    def test_children_returns_empty_list_for_object_without_children(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _children returns empty list for object with no children."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_child_count.return_value = 0
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        children = navigator._children(mock_script, mock_obj)
        assert isinstance(children, list)
        assert len(children) == 0

    def test_parent_returns_parent_object(self, test_context: OrcaTestContext) -> None:
        """Test _parent returns parent of accessible object."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        mock_parent = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_parent.return_value = mock_parent
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        parent = navigator._parent(mock_script, mock_obj)
        assert parent == mock_parent
        ax_object.get_parent.assert_called_once_with(mock_obj)

    def test_parent_returns_none_when_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test _parent returns None when object has no parent."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_parent.return_value = None
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        parent = navigator._parent(mock_script, mock_obj)
        assert parent is None

    def test_set_navigator_focus_updates_focus_tracking(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _set_navigator_focus properly tracks focus changes."""

        self._setup_dependencies(test_context)
        mock_obj = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._set_navigator_focus(mock_obj)
        assert navigator._navigator_focus == mock_obj

    def test_set_navigator_focus_tracks_previous_focus(self, test_context: OrcaTestContext) -> None:
        """Test _set_navigator_focus tracks previous focus object."""

        self._setup_dependencies(test_context)
        mock_obj1 = test_context.Mock()
        mock_obj2 = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._set_navigator_focus(mock_obj1)
        navigator._set_navigator_focus(mock_obj2)
        assert navigator._navigator_focus == mock_obj2
        assert navigator._last_navigator_focus == mock_obj1

    def test_update_tracks_locus_of_focus(self, test_context: OrcaTestContext) -> None:
        """Test _update tracks the current locus of focus."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_focus_obj = test_context.Mock()
        focus_manager = essential_modules["orca.focus_manager"].get_manager.return_value
        focus_manager.get_locus_of_focus.return_value = mock_focus_obj
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._update()
        assert navigator._last_locus_of_focus == mock_focus_obj

    def test_present_calls_script_presentation_method(self, test_context: OrcaTestContext) -> None:
        """Test _present calls appropriate script method for object presentation."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = test_context.Mock()
        navigator._present(mock_script)
        mock_script.present_object.assert_called_once()

    @pytest.mark.parametrize(
        "notify_user",
        [
            pytest.param(True, id="notify_user_true"),
            pytest.param(False, id="notify_user_false"),
        ],
    )
    def test_present_respects_notify_user_parameter(
        self, test_context: OrcaTestContext, notify_user
    ) -> None:
        """Test _present respects the notify_user parameter."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = test_context.Mock()
        navigator._present(mock_script, notify_user=notify_user)
        if notify_user:
            mock_script.present_object.assert_called_once()
        else:
            mock_script.present_object.assert_not_called()

    @pytest.mark.parametrize(
        "has_parent",
        [
            pytest.param(True, id="success"),
            pytest.param(False, id="no_parent"),
        ],
    )
    def test_move_to_parent_scenarios(
        self, test_context: OrcaTestContext, has_parent: bool
    ) -> None:
        """Test move_to_parent with various parent availability scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        mock_current = test_context.Mock()

        if has_parent:
            mock_parent = test_context.Mock()
            ax_object = essential_modules["orca.ax_object"].AXObject
            ax_object.get_parent.return_value = mock_parent
            expected_focus = mock_parent
        else:
            ax_object = essential_modules["orca.ax_object"].AXObject
            ax_object.get_parent.return_value = None
            expected_focus = mock_current

        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = mock_current
        result = navigator.move_to_parent(mock_script)
        assert result is True
        assert navigator._navigator_focus == expected_focus

    @pytest.mark.parametrize(
        "has_children, child_count",
        [
            pytest.param(True, 1, id="success"),
            pytest.param(False, 0, id="no_children"),
        ],
    )
    def test_move_to_first_child_scenarios(
        self, test_context: OrcaTestContext, has_children: bool, child_count: int
    ) -> None:
        """Test move_to_first_child with various child availability scenarios."""
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        mock_current = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_child_count.return_value = child_count

        if has_children:
            mock_child = test_context.Mock()
            ax_object.iter_children.return_value = [mock_child]
            expected_focus = mock_child
        else:
            expected_focus = mock_current

        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = mock_current
        result = navigator.move_to_first_child(mock_script)
        assert result is True
        assert navigator._navigator_focus == expected_focus

    def test_move_to_next_sibling_success(self, test_context: OrcaTestContext) -> None:
        """Test move_to_next_sibling successfully navigates to next sibling."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        mock_current = test_context.Mock()
        mock_parent = test_context.Mock()
        mock_sibling = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_parent.return_value = mock_parent
        ax_object.get_child_count.return_value = 2
        ax_object.iter_children.return_value = [mock_current, mock_sibling]
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = mock_current
        result = navigator.move_to_next_sibling(mock_script)
        assert result is True
        assert navigator._navigator_focus == mock_sibling

    def test_move_to_previous_sibling_success(self, test_context: OrcaTestContext) -> None:
        """Test move_to_previous_sibling successfully navigates to previous sibling."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_object = test_context.Mock()
        mock_current = test_context.Mock()
        mock_parent = test_context.Mock()
        mock_sibling = test_context.Mock()
        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.get_parent.return_value = mock_parent
        ax_object.get_child_count.return_value = 2
        ax_object.iter_children.return_value = [mock_sibling, mock_current]
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = mock_current
        result = navigator.move_to_previous_sibling(mock_script)
        assert result is True
        assert navigator._navigator_focus == mock_sibling

    def test_toggle_simplify_changes_simplify_state(self, test_context: OrcaTestContext) -> None:
        """Test toggle_simplify changes the simplification state."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        original_state = navigator._simplify
        result = navigator.toggle_simplify(mock_script)
        assert result is True
        assert navigator._simplify != original_state

    def test_toggle_simplify_announces_state_change(self, test_context: OrcaTestContext) -> None:
        """Test toggle_simplify announces the state change to user."""

        self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator.toggle_simplify(mock_script)
        mock_script.present_message.assert_called_once()

    def test_perform_action_calls_synthesizer(self, test_context: OrcaTestContext) -> None:
        """Test perform_action uses AXEventSynthesizer for action execution."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        ax_event_synthesizer = essential_modules["orca.ax_event_synthesizer"].AXEventSynthesizer
        ax_event_synthesizer.try_all_clickable_actions = test_context.Mock(return_value=False)
        ax_event_synthesizer.click_object = test_context.Mock(return_value=True)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = mock_obj
        result = navigator.perform_action(mock_script)
        assert result is True
        ax_event_synthesizer.click_object.assert_called_once_with(mock_obj, 1)

    def test_children_with_null_object(self, test_context: OrcaTestContext) -> None:
        """Test _children handles None object gracefully."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        mock_script = test_context.Mock()
        children = navigator._children(mock_script, None)
        assert isinstance(children, list)
        assert len(children) == 0
        essential_modules["orca.debug"].print_message.assert_called()

    def test_parent_with_null_object_returns_none(self, test_context: OrcaTestContext) -> None:
        """Test _parent returns None when given None object."""

        self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        mock_script = test_context.Mock()
        parent = navigator._parent(mock_script, None)
        assert parent is None

    def test_move_to_parent_with_null_navigator_focus(self, test_context: OrcaTestContext) -> None:
        """Test move_to_parent handles None navigator focus gracefully."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = None
        mock_script = test_context.Mock()
        result = navigator.move_to_parent(mock_script)
        assert result is True
        essential_modules["orca.debug"].print_message.assert_called()

    def test_move_to_first_child_with_dead_object(self, test_context: OrcaTestContext) -> None:
        """Test move_to_first_child handles dead AT-SPI objects."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        mock_script = test_context.Mock()
        mock_obj = test_context.Mock()
        navigator._navigator_focus = mock_obj

        ax_object = essential_modules["orca.ax_object"].AXObject
        ax_object.is_dead.return_value = True

        result = navigator.move_to_first_child(mock_script)
        assert result is True
        essential_modules["orca.debug"].print_message.assert_called()

    def test_perform_action_with_null_focus_logs_debug_info(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test perform_action logs debug information with None navigator focus."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._navigator_focus = None
        mock_script = test_context.Mock()

        result = navigator.perform_action(mock_script)
        assert result is True
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_toggle_simplify_announces_on_state(self, test_context: OrcaTestContext) -> None:
        """Test toggle_simplify announces state change correctly."""

        self._setup_dependencies(test_context)
        from orca.object_navigator import ObjectNavigator  # pylint: disable=import-outside-toplevel

        navigator = ObjectNavigator()
        navigator._simplify = False
        mock_script = test_context.Mock()
        mock_script.present_message = test_context.Mock()

        navigator.toggle_simplify(mock_script)

        mock_script.present_message.assert_called_once()
        assert navigator._simplify is True

    def test_get_navigator_returns_singleton_instance(self, test_context: OrcaTestContext) -> None:
        """Test get_navigator function returns singleton ObjectNavigator instance."""

        self._setup_dependencies(test_context)
        from orca.object_navigator import get_navigator  # pylint: disable=import-outside-toplevel

        navigator1 = get_navigator()
        navigator2 = get_navigator()
        assert navigator1 is navigator2
        assert navigator1.__class__.__name__ == "ObjectNavigator"
