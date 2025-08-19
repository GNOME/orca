# Unit tests for action_presenter.py methods.
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

# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

"""Unit tests for action_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

LOCATION_NOT_FOUND_FULL_MSG = "Location not found (full)"
LOCATION_NOT_FOUND_BRIEF_MSG = "Location not found (brief)"
LOCATION_NOT_FOUND_MSG = "Location not found"
SHOW_ACTIONS_LIST_CMD = "showActionsList"

@pytest.mark.unit
class TestActionPresenter:
    """Test ActionPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns all dependencies needed for ActionPresenter testing."""

        additional_modules = ["orca.brltablenames", "orca.speech"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        essential_modules["orca.cmdnames"].SHOW_ACTIONS_LIST = SHOW_ACTIONS_LIST_CMD
        focus_manager_instance = test_context.Mock()
        focus_manager_instance.get_active_mode_and_object_of_interest = test_context.Mock(
            return_value=(None, None)
        )
        focus_manager_instance.get_locus_of_focus = test_context.Mock(return_value=None)
        focus_manager_instance.get_active_window = test_context.Mock(return_value=None)
        focus_manager_instance.clear_state = test_context.Mock()
        focus_manager_instance.set_active_window = test_context.Mock()
        focus_manager_instance.set_locus_of_focus = test_context.Mock()
        essential_modules["orca.focus_manager"].get_manager = test_context.Mock(
            return_value=focus_manager_instance
        )

        input_event_handler_mock = test_context.Mock()
        essential_modules["orca.input_event"].InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )
        essential_modules["orca.input_event"].InputEvent = test_context.mocker.MagicMock

        script_manager_instance = essential_modules["orca.script_manager"].get_manager()
        script_mock = script_manager_instance.get_active_script()
        script_mock.speech_generator.get_localized_role_name = test_context.Mock(
            return_value="button"
        )

        essential_modules["orca.messages"].LOCATION_NOT_FOUND_FULL = LOCATION_NOT_FOUND_FULL_MSG
        essential_modules["orca.messages"].LOCATION_NOT_FOUND_BRIEF = LOCATION_NOT_FOUND_BRIEF_MSG
        essential_modules["orca.messages"].NO_ACTIONS_FOUND_ON = "No actions found on %s"
        essential_modules["orca.guilabels"].ACTIONS_LIST = "Actions List"
        return essential_modules

    # pylint: disable-next=too-many-locals
    @pytest.mark.parametrize(
        "test_scenario,n_actions,action_descriptions,object_source,"
        "expected_message,expects_gui_creation",
        [
            pytest.param(
                "with_actions",
                2,
                ["Click button", "Activate button"],
                "locus_of_focus",
                None,
                True,
                id="actions_from_locus",
            ),
            pytest.param(
                "no_object",
                0,
                [],
                None,
                LOCATION_NOT_FOUND_FULL_MSG,
                False,
                id="no_object_available",
            ),
            pytest.param(
                "empty_descriptions",
                2,
                ["", ""],
                "locus_of_focus",
                None,
                True,
                id="empty_action_descriptions",
            ),
            pytest.param(
                "from_active_mode",
                2,
                ["Click button", "Activate button"],
                "active_mode",
                None,
                True,
                id="object_from_active_mode",
            ),
            pytest.param(
                "no_actions_found",
                0,
                [],
                "locus_of_focus",
                "No actions found on Test Button",
                False,
                id="object_has_no_actions",
            ),
        ],
    )
    def test_show_actions_list(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements
        self,
        test_context: OrcaTestContext,
        test_scenario: str,
        n_actions: int,
        action_descriptions: list[str],
        object_source: str | None,
        expected_message: str | None,
        expects_gui_creation: bool,
    ) -> None:
        """Test ActionPresenter.show_actions_list with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        if test_scenario != "no_object":
            ax_object_mock = test_context.Mock()
            ax_object_mock.get_n_actions = test_context.Mock(return_value=n_actions)
            ax_object_mock.get_action_name = test_context.Mock(
                side_effect=lambda obj, i: ["click", "activate"][i]
                if i < len(["click", "activate"])
                else f"action{i}"
            )
            ax_object_mock.get_action_description = test_context.Mock(
                side_effect=lambda obj, i: action_descriptions[i]
                if i < len(action_descriptions)
                else f"desc{i}"
            )
            ax_object_mock.get_name = test_context.Mock(return_value="Test Button")

            ax_utilities_mock = test_context.Mock()
            ax_utilities_mock.get_application = test_context.Mock(return_value=test_context.Mock())

            ax_object_module_mock = test_context.Mock()
            ax_object_module_mock.AXObject = ax_object_mock
            test_context.patch_module("orca.ax_object", ax_object_module_mock)
            ax_utilities_module_mock = test_context.Mock()
            ax_utilities_module_mock.AXUtilities = ax_utilities_mock
            test_context.patch_module("orca.ax_utilities", ax_utilities_module_mock)

        from orca.action_presenter import ActionPresenter

        presenter = ActionPresenter()
        mock_script = essential_modules["orca.script_manager"].get_manager().get_script()
        mock_event = test_context.Mock()
        focus_manager = essential_modules["orca.focus_manager"].get_manager()

        if object_source == "locus_of_focus":
            mock_accessible_object = test_context.Mock()
            mock_accessible_object.get_name = test_context.Mock(return_value="Test Button")
            focus_manager.get_active_mode_and_object_of_interest.return_value = (None, None)
            focus_manager.get_locus_of_focus.return_value = mock_accessible_object
        elif object_source == "active_mode":
            mock_accessible_object = test_context.Mock()
            mock_accessible_object.get_name = test_context.Mock(return_value="Test Button")
            focus_manager.get_active_mode_and_object_of_interest.return_value = (
                test_context.Mock(),
                mock_accessible_object,
            )
            focus_manager.get_locus_of_focus.return_value = None
        else:
            focus_manager.get_active_mode_and_object_of_interest.return_value = (None, None)
            focus_manager.get_locus_of_focus.return_value = None
            mock_accessible_object = None

        mock_action_list_class = None
        if expects_gui_creation:
            mock_window = test_context.Mock()
            focus_manager.get_active_window.return_value = mock_window
            mock_action_list = test_context.Mock()
            mock_action_list_class = test_context.patch(
                "orca.action_presenter.ActionList", return_value=mock_action_list
            )

        result = presenter.show_actions_list(mock_script, mock_event, True)
        assert result is True

        if expected_message:
            if LOCATION_NOT_FOUND_MSG in expected_message:
                mock_script.present_message.assert_called_once_with(
                    LOCATION_NOT_FOUND_FULL_MSG, LOCATION_NOT_FOUND_BRIEF_MSG
                )
            else:
                mock_script.present_message.assert_called_once_with(expected_message)

        if expects_gui_creation and n_actions > 0:
            assert mock_action_list_class is not None
            mock_action_list_class.assert_called_once()
            mock_action_list.show_gui.assert_called_once()
            assert presenter._obj == mock_accessible_object
            assert presenter._gui == mock_action_list

            if test_scenario == "empty_descriptions":
                call_args = mock_action_list_class.call_args[0][0]
                assert "click" in call_args
                assert call_args["click"] == "click"

    @pytest.mark.parametrize(
        "action_success,gui_state",
        [
            pytest.param(True, "present", id="successful_action"),
            pytest.param(False, "present", id="failed_action"),
            pytest.param(True, None, id="no_gui_early_return"),
        ],
    )
    def test_perform_action(
        self,
        test_context: OrcaTestContext,
        action_success: bool,
        gui_state: str | None,
    ) -> None:
        """Test ActionPresenter._perform_action with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.action_presenter import ActionPresenter

        presenter = ActionPresenter()
        mock_accessible_object = test_context.Mock()
        mock_accessible_object.get_name = test_context.Mock(return_value="Test Button")
        presenter._obj = mock_accessible_object

        if gui_state == "present":
            presenter._gui = test_context.Mock()
        else:
            presenter._gui = None

        mock_idle_add = test_context.patch("orca.action_presenter.GLib.idle_add")
        mock_debug_tokens = test_context.patch("orca.action_presenter.debug.print_tokens")
        mock_do_action = test_context.patch("orca.action_presenter.AXObject.do_named_action")
        mock_do_action.return_value = action_success

        presenter._perform_action("click")

        if gui_state is None:
            essential_modules["orca.debug"].print_message.assert_called()
            debug_call = essential_modules["orca.debug"].print_message.call_args[0][1]
            assert "_perform_action called when self._gui is None" in debug_call
            mock_do_action.assert_not_called()
        else:
            assert presenter._gui is not None
            presenter._gui.hide.assert_called_once()
            mock_do_action.assert_called_with(mock_accessible_object, "click")
            mock_idle_add.assert_called_with(presenter._gui.destroy)
            mock_debug_tokens.assert_called()

            if not action_success:
                debug_calls = mock_debug_tokens.call_args_list
                assert len(debug_calls) > 0

    def test_get_presenter_singleton(self, test_context: OrcaTestContext) -> None:
        """Test action_presenter.get_presenter singleton functionality."""

        self._setup_dependencies(test_context)
        from orca.action_presenter import get_presenter

        presenter1 = get_presenter()
        presenter2 = get_presenter()
        assert presenter1 is presenter2
        assert presenter1.__class__.__name__ == "ActionPresenter"

    @pytest.mark.parametrize(
        "method_name,refresh,mock_empty,expects_debug",
        [
            pytest.param("get_bindings", True, False, True, id="bindings_with_refresh"),
            pytest.param("get_bindings", False, True, False, id="bindings_empty_no_refresh"),
            pytest.param("get_handlers", True, False, True, id="handlers_with_refresh"),
        ],
    )
    def test_get_bindings_and_handlers(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        test_context: OrcaTestContext,
        method_name: str,
        refresh: bool,
        mock_empty: bool,
        expects_debug: bool,
    ) -> None:
        """Test ActionPresenter.get_bindings and get_handlers with various settings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.action_presenter import ActionPresenter

        presenter = ActionPresenter()

        if method_name == "get_bindings":
            mock_setup = test_context.patch_object(presenter, "_setup_bindings", return_value=None)

            if mock_empty:
                test_context.patch_object(
                    presenter._bindings, "is_empty", return_value=True
                )

            bindings_result = presenter.get_bindings(refresh=refresh, is_desktop=bool(refresh))
            assert bindings_result is presenter._bindings
        else:
            mock_setup = test_context.patch_object(presenter, "_setup_handlers", return_value=None)
            handlers_result = presenter.get_handlers(refresh=refresh)
            assert handlers_result is presenter._handlers

        mock_setup.assert_called_once()
        if expects_debug:
            essential_modules["orca.debug"].print_message.assert_called()

    def test_setup_bindings_creates_key_binding(self, test_context: OrcaTestContext) -> None:
        """Test ActionPresenter._setup_bindings creates proper key binding."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.action_presenter import ActionPresenter

        presenter = ActionPresenter()

        presenter._bindings = test_context.Mock()
        presenter._bindings.is_empty = test_context.Mock(return_value=True)

        mock_keybindings = test_context.Mock()
        mock_key_binding_class = test_context.Mock()
        mock_keybindings.KeyBindings = test_context.Mock()
        mock_keybindings.KeyBinding = mock_key_binding_class
        mock_keybindings.DEFAULT_MODIFIER_MASK = "DEFAULT_MODIFIER"
        mock_keybindings.ORCA_SHIFT_MODIFIER_MASK = "ORCA_SHIFT_MODIFIER"
        test_context.patch("orca.action_presenter.keybindings", new=mock_keybindings)

        presenter._setup_bindings()

        mock_key_binding_class.assert_called_once_with(
            "a", "DEFAULT_MODIFIER", "ORCA_SHIFT_MODIFIER", presenter._handlers["show_actions_list"]
        )
        essential_modules["orca.debug"].print_message.assert_called()

    def test_restore_focus_sets_script_and_focus(self, test_context: OrcaTestContext) -> None:
        """Test ActionPresenter._restore_focus properly restores script and focus."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.action_presenter import ActionPresenter

        presenter = ActionPresenter()
        mock_obj = test_context.Mock()
        mock_window = test_context.Mock()
        mock_app = test_context.Mock()
        mock_script = test_context.Mock()

        presenter._obj = mock_obj
        presenter._window = mock_window

        ax_utilities_mock = test_context.Mock()
        ax_utilities_mock.get_application = test_context.Mock(return_value=mock_app)
        test_context.patch("orca.action_presenter.AXUtilities", new=ax_utilities_mock)

        script_manager_instance = essential_modules["orca.script_manager"].get_manager()
        script_manager_instance.get_script.return_value = mock_script

        focus_manager_instance = essential_modules["orca.focus_manager"].get_manager()

        presenter._restore_focus()

        ax_utilities_mock.get_application.assert_called_once_with(mock_obj)
        script_manager_instance.get_script.assert_called_once_with(mock_app, mock_obj)
        script_manager_instance.set_active_script.assert_called_once_with(
            mock_script, "Action Presenter list is being destroyed"
        )
        focus_manager_instance.clear_state.assert_called_once_with(
            "Action Presenter list is being destroyed"
        )
        focus_manager_instance.set_active_window.assert_called_once_with(mock_window)
        focus_manager_instance.set_locus_of_focus.assert_called_once_with(None, mock_obj)

    def test_clear_gui_and_restore_focus(self, test_context: OrcaTestContext) -> None:
        """Test ActionPresenter._clear_gui_and_restore_focus clears gui and calls restore."""

        self._setup_dependencies(test_context)
        from orca.action_presenter import ActionPresenter

        presenter = ActionPresenter()
        presenter._gui = test_context.Mock()

        mock_restore_focus = test_context.patch_object(
            presenter, "_restore_focus", return_value=None
        )

        presenter._clear_gui_and_restore_focus()

        assert presenter._gui is None
        mock_restore_focus.assert_called_once()
