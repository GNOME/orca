# Unit tests for bypass_mode_manager.py methods.
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
# pylint: disable=too-many-locals
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=no-member

"""Unit tests for bypass_mode_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestBypassModeManager:
    """Test BypassModeManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for bypass_mode_manager module testing."""

        additional_modules = ["orca.orca_modifier_manager", "orca.command_manager"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.BYPASS_MODE_TOGGLE = "Toggle all Orca command keys"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        keybindings_mock = essential_modules["orca.keybindings"]
        key_bindings_instance = test_context.Mock()
        key_bindings_instance.is_empty = test_context.Mock(return_value=False)
        key_bindings_instance.key_bindings = []
        key_bindings_instance.add = test_context.Mock(return_value=None)
        keybindings_mock.KeyBindings = test_context.Mock(return_value=key_bindings_instance)
        keybindings_mock.KeyBinding = test_context.Mock()
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.ALT_MODIFIER_MASK = 2

        messages_mock = essential_modules["orca.messages"]
        messages_mock.BYPASS_MODE_ENABLED = "Orca command keys off."
        messages_mock.BYPASS_MODE_DISABLED = "Orca command keys on."

        orca_modifier_manager_mock = essential_modules["orca.orca_modifier_manager"]
        modifier_manager_instance = test_context.Mock()
        modifier_manager_instance.unset_orca_modifiers = test_context.Mock()
        modifier_manager_instance.refresh_orca_modifiers = test_context.Mock()
        modifier_manager_instance.add_grabs_for_orca_modifiers = test_context.Mock()
        modifier_manager_instance.remove_grabs_for_orca_modifiers = test_context.Mock()
        orca_modifier_manager_mock.get_manager = test_context.Mock(
            return_value=modifier_manager_instance
        )

        command_manager_mock = essential_modules["orca.command_manager"]
        command_manager_instance = test_context.Mock()
        command_manager_instance.add_all_grabs = test_context.Mock()
        command_manager_instance.remove_all_grabs = test_context.Mock()
        command_manager_instance.add_grabs_for_command = test_context.Mock()
        command_manager_mock.get_manager = test_context.Mock(
            return_value=command_manager_instance
        )

        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        override_method = test_context.Mock(return_value=key_bindings_instance)
        settings_manager_instance.override_key_bindings = override_method
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        essential_modules["input_event_handler"] = input_event_handler_mock
        essential_modules["key_bindings_instance"] = key_bindings_instance
        essential_modules["modifier_manager_instance"] = modifier_manager_instance
        essential_modules["settings_manager_instance"] = settings_manager_instance
        essential_modules["command_manager_instance"] = command_manager_instance

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test BypassModeManager initialization."""

        self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager
        from orca import command_manager

        manager = BypassModeManager()
        assert manager._is_active is False
        # Commands are registered during setup(), not __init__()
        manager.set_up_commands()
        cmd_manager = command_manager.get_manager()
        assert cmd_manager.get_keyboard_command("bypass_mode_toggle") is not None

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test that commands are registered with CommandManager during setup."""

        self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager
        from orca import command_manager

        manager = BypassModeManager()
        manager.set_up_commands()
        # Commands are now registered with CommandManager during setup()
        cmd_manager = command_manager.get_manager()
        cmd = cmd_manager.get_keyboard_command("bypass_mode_toggle")
        assert cmd is not None

    def test_setup_bindings(self, test_context: OrcaTestContext) -> None:
        """Test that keybindings are created via Command.set_keybinding."""

        self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager
        from orca import command_manager

        manager = BypassModeManager()
        manager.set_up_commands()
        # Verify the command has a keybinding
        cmd_manager = command_manager.get_manager()
        cmd = cmd_manager.get_keyboard_command("bypass_mode_toggle")
        assert cmd is not None
        keybinding = cmd.get_keybinding()
        assert keybinding is not None

    @pytest.mark.parametrize(
        "initial_active,has_event,expected_active,expected_message,"
        "expected_grabs_call,expected_modifier_call",
        [
            (
                False,
                True,
                True,
                "Orca command keys off.",
                "remove_all_grabs",
                "unset_orca_modifiers",
            ),
            (
                False,
                False,
                True,
                None,
                "remove_all_grabs",
                "unset_orca_modifiers",
            ),
            (
                True,
                True,
                False,
                "Orca command keys on.",
                "add_all_grabs",
                "refresh_orca_modifiers",
            ),
            (
                True,
                False,
                False,
                None,
                "add_all_grabs",
                "refresh_orca_modifiers",
            ),
        ],
    )
    def test_toggle_enabled(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        test_context: OrcaTestContext,
        initial_active: bool,
        has_event: bool,
        expected_active: bool,
        expected_message: str | None,
        expected_grabs_call: str,
        expected_modifier_call: str,
    ) -> None:
        """Test toggle_enabled with various initial states and event conditions."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        if not initial_active:
            mock_binding1 = test_context.Mock()
            mock_binding2 = test_context.Mock()
            key_bindings = [mock_binding1, mock_binding2]
        else:
            key_bindings = []

        key_bindings_instance = essential_modules["key_bindings_instance"]
        key_bindings_instance.key_bindings = key_bindings
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._is_active = initial_active
        mock_script = test_context.Mock()
        mock_event = test_context.Mock() if has_event else None

        result = manager.toggle_enabled(mock_script, mock_event)
        assert result is True
        assert manager._is_active is expected_active

        if expected_message:
            mock_script.present_message.assert_called_with(expected_message)
        else:
            mock_script.present_message.assert_not_called()

        cmd_manager = essential_modules["command_manager_instance"]
        grabs_method = getattr(cmd_manager, expected_grabs_call)
        if expected_active:
            grabs_method.assert_called_with("bypass mode enabled")
        else:
            grabs_method.assert_called_with("bypass mode disabled")

        modifier_manager = essential_modules["modifier_manager_instance"]
        modifier_method = getattr(modifier_manager, expected_modifier_call)
        if expected_active:
            modifier_method.assert_called_with("bypass mode enabled")
        else:
            modifier_method.assert_called_with("bypass mode disabled")

    def test_toggle_enabled_multiple_times(self, test_context: OrcaTestContext) -> None:
        """Test toggle_enabled works correctly when called multiple times."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        key_bindings_instance = essential_modules["key_bindings_instance"]
        key_bindings_instance.key_bindings = []
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        mock_script = test_context.Mock()

        assert manager.is_active() is False

        result1 = manager.toggle_enabled(mock_script, None)
        assert result1 is True
        assert manager.is_active() is True

        result2 = manager.toggle_enabled(mock_script, None)
        assert result2 is True
        assert manager.is_active() is False

        result3 = manager.toggle_enabled(mock_script, None)
        assert result3 is True
        assert manager.is_active() is True

    def test_bindings_created_correctly(self, test_context: OrcaTestContext) -> None:
        """Test that bindings are properly configured from commands."""

        self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager
        from orca import command_manager

        manager = BypassModeManager()
        manager.set_up_commands()
        # Verify bypass_mode_toggle command has keybinding set
        cmd = command_manager.get_manager().get_keyboard_command("bypass_mode_toggle")
        assert cmd is not None
        assert cmd.get_keybinding() is not None

    def test_toggle_enabled_with_minimal_script_interface(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test toggle_enabled method with script that has minimal interface."""

        self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        mock_script = test_context.Mock(spec=[])
        mock_script.add_key_grabs = test_context.Mock()
        mock_script.remove_key_grabs = test_context.Mock()
        mock_script.present_message = test_context.Mock()
        mock_script.key_bindings = test_context.Mock()
        mock_script.key_bindings.add = test_context.Mock()

        result = manager.toggle_enabled(mock_script)
        assert result is True
        assert manager.is_active() is True
