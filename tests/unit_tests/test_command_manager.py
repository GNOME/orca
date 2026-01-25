# Unit tests for command_manager.py methods.
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
# pylint: disable=protected-access

"""Unit tests for command_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import Mock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestCommand:
    """Test Command base class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        return essential_modules

    def _create_mock_function(self, test_context: OrcaTestContext) -> Mock:
        """Creates a mock function for a Command."""

        function = test_context.Mock()
        function.return_value = True
        return function

    def test_init_minimal(self, test_context: OrcaTestContext) -> None:
        """Test Command.__init__ with minimal arguments."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command("testCommand", function, "Test Group")

        assert command.get_name() == "testCommand"
        assert command.get_function() == function
        assert command.get_group_label() == "Test Group"
        assert command.get_description() == ""

    def test_init_full(self, test_context: OrcaTestContext) -> None:
        """Test Command.__init__ with all arguments."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command(
            "fullCommand", function, "Full Group", "Full description",
            enabled=False, suspended=True
        )

        assert command.get_name() == "fullCommand"
        assert command.get_function() == function
        assert command.get_group_label() == "Full Group"
        assert command.get_description() == "Full description"
        assert command.is_enabled() is False
        assert command.is_suspended() is True

    def test_set_group_label(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_group_label."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command("testCommand", function, "Original Group")

        assert command.get_group_label() == "Original Group"

        command.set_group_label("New Group")
        assert command.get_group_label() == "New Group"

    def test_init_enabled_suspended_defaults(self, test_context: OrcaTestContext) -> None:
        """Test that enabled defaults to True and suspended defaults to False."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command("testCommand", function, "Test Group")

        assert command.is_enabled() is True
        assert command.is_suspended() is False

    def test_init_enabled_suspended_explicit(self, test_context: OrcaTestContext) -> None:
        """Test Command.__init__ with explicit enabled and suspended values."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command("testCommand", function, "Test Group", enabled=False, suspended=True)

        assert command.is_enabled() is False
        assert command.is_suspended() is True

    def test_set_enabled(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_enabled."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command("testCommand", function, "Test Group")

        assert command.is_enabled() is True

        command.set_enabled(False)
        assert command.is_enabled() is False

        command.set_enabled(True)
        assert command.is_enabled() is True

    def test_set_suspended(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_suspended."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        command = Command("testCommand", function, "Test Group")

        assert command.is_suspended() is False

        command.set_suspended(True)
        assert command.is_suspended() is True

        command.set_suspended(False)
        assert command.is_suspended() is False

    def test_execute_calls_function(self, test_context: OrcaTestContext) -> None:
        """Test that execute calls the command's function."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        function.return_value = True
        command = Command("testCommand", function, "Test Group")

        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        result = command.execute(mock_script, mock_event)

        function.assert_called_once_with(mock_script, mock_event)
        assert result is True

    def test_execute_returns_function_result(self, test_context: OrcaTestContext) -> None:
        """Test that execute returns the function's return value."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        function = self._create_mock_function(test_context)
        function.return_value = False
        command = Command("testCommand", function, "Test Group")

        mock_script = test_context.Mock()

        result = command.execute(mock_script, None)

        assert result is False


@pytest.mark.unit
class TestKeyboardCommand:
    """Test KeyboardCommand class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        return essential_modules

    def _create_mock_function(self, test_context: OrcaTestContext) -> Mock:
        """Creates a mock function for a Command."""

        function = test_context.Mock()
        function.return_value = True
        return function

    def _create_mock_keybinding(
        self, test_context: OrcaTestContext, keyval: int = 65, keycode: int = 38
    ) -> Mock:
        """Creates a mock KeyBinding with default keyval/keycode for indexing."""

        kb = test_context.Mock()
        kb.keyval = keyval
        kb.keycode = keycode
        return kb

    def test_init_minimal(self, test_context: OrcaTestContext) -> None:
        """Test KeyboardCommand.__init__ with minimal arguments."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        command = KeyboardCommand("testCommand", function, "Test Group")

        assert command.get_name() == "testCommand"
        assert command.get_function() == function
        assert command.get_group_label() == "Test Group"
        assert command.get_description() == ""
        assert command.get_keybinding() is None

    def test_init_with_keybindings(self, test_context: OrcaTestContext) -> None:
        """Test KeyboardCommand.__init__ with keybindings."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        desktop_kb = self._create_mock_keybinding(test_context)
        laptop_kb = self._create_mock_keybinding(test_context)

        command = KeyboardCommand(
            "fullCommand", function, "Full Group", "Full description",
            desktop_keybinding=desktop_kb, laptop_keybinding=laptop_kb
        )

        assert command.get_name() == "fullCommand"
        assert command.get_desktop_keybinding() == desktop_kb
        assert command.get_laptop_keybinding() == laptop_kb

    def test_set_keybinding(self, test_context: OrcaTestContext) -> None:
        """Test KeyboardCommand.set_keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        command = KeyboardCommand("testCommand", function, "Test Group")

        assert command.get_keybinding() is None

        new_kb = self._create_mock_keybinding(test_context)
        command.set_keybinding(new_kb)
        assert command.get_keybinding() == new_kb

        command.set_keybinding(None)
        assert command.get_keybinding() is None

    def test_is_active_enabled_not_suspended_with_keybinding(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test is_active returns True when enabled, not suspended, and has keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        keybinding = self._create_mock_keybinding(test_context)
        command = KeyboardCommand(
            "testCommand", function, "Test Group",
            desktop_keybinding=keybinding
        )
        command.set_keybinding(keybinding)

        assert command.is_active() is True

    def test_is_active_disabled(self, test_context: OrcaTestContext) -> None:
        """Test is_active returns False when disabled."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        keybinding = self._create_mock_keybinding(test_context)
        command = KeyboardCommand(
            "testCommand", function, "Test Group",
            desktop_keybinding=keybinding, enabled=False
        )
        command.set_keybinding(keybinding)

        assert command.is_active() is False

    def test_is_active_suspended(self, test_context: OrcaTestContext) -> None:
        """Test is_active returns False when suspended."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        keybinding = self._create_mock_keybinding(test_context)
        command = KeyboardCommand(
            "testCommand", function, "Test Group",
            desktop_keybinding=keybinding, suspended=True
        )
        command.set_keybinding(keybinding)

        assert command.is_active() is False

    def test_is_active_no_keybinding(self, test_context: OrcaTestContext) -> None:
        """Test is_active returns False when no keybinding is assigned."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)
        command = KeyboardCommand("testCommand", function, "Test Group")

        assert command.is_active() is False

    def test_is_group_toggle_init(self, test_context: OrcaTestContext) -> None:
        """Test KeyboardCommand initializes is_group_toggle correctly."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand

        function = self._create_mock_function(test_context)

        # Default is False
        cmd_default = KeyboardCommand("cmd1", function, "Test Group")
        assert cmd_default.is_group_toggle() is False

        # Explicit True
        cmd_toggle = KeyboardCommand("cmd2", function, "Test Group", is_group_toggle=True)
        assert cmd_toggle.is_group_toggle() is True


@pytest.mark.unit
class TestBrailleCommand:
    """Test BrailleCommand class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        return essential_modules

    def _create_mock_function(self, test_context: OrcaTestContext) -> Mock:
        """Creates a mock function for a Command."""

        function = test_context.Mock()
        function.return_value = True
        return function

    def test_braille_bindings_default_empty(self, test_context: OrcaTestContext) -> None:
        """Test that braille bindings default to empty tuple."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand

        function = self._create_mock_function(test_context)
        command = BrailleCommand("testCommand", function, "Test Group")

        assert command.get_braille_bindings() == ()

    def test_init_with_braille_bindings(self, test_context: OrcaTestContext) -> None:
        """Test BrailleCommand.__init__ with braille bindings."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand

        function = self._create_mock_function(test_context)
        command = BrailleCommand(
            "testCommand", function, "Test Group", "Test description",
            braille_bindings=(1, 2, 3)
        )

        assert command.get_braille_bindings() == (1, 2, 3)


@pytest.mark.unit
class TestCommandManager:
    """Test CommandManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        return essential_modules

    def _create_mock_function(
        self,
        test_context: OrcaTestContext,
        description: str = "Test function",
    ) -> Mock:
        """Creates a mock function for a Command."""

        function = test_context.Mock()
        function.return_value = True
        return function

    def _create_mock_keybinding(
        self, test_context: OrcaTestContext, keyval: int = 65, keycode: int = 38
    ) -> Mock:
        """Creates a mock KeyBinding with default keyval/keycode for indexing."""

        kb = test_context.Mock()
        kb.keyval = keyval
        kb.keycode = keycode
        return kb

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.__init__."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        assert manager.get_all_keyboard_commands() == ()
        assert manager.get_all_braille_commands() == ()

    def test_add_and_get_keyboard_command(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.add_command and get_keyboard_command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)
        command = KeyboardCommand("testCommand", function, "Test Group")

        manager.add_command(command)

        retrieved = manager.get_keyboard_command("testCommand")
        assert retrieved == command

        assert manager.get_keyboard_command("nonexistent") is None

    def test_add_and_get_braille_command(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.add_command and get_braille_command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)
        command = BrailleCommand("testCommand", function, "Test Group",
                                  braille_bindings=(100, 200))

        manager.add_command(command)

        retrieved = manager.get_braille_command("testCommand")
        assert retrieved == command

        assert manager.get_braille_command("nonexistent") is None

    def test_get_all_keyboard_commands(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.get_all_keyboard_commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function1 = self._create_mock_function(test_context)
        function2 = self._create_mock_function(test_context)
        function3 = self._create_mock_function(test_context)

        cmd1 = KeyboardCommand("cmd1", function1, "Group A")
        cmd2 = KeyboardCommand("cmd2", function2, "Group B")
        cmd3 = KeyboardCommand("cmd3", function3, "Group A")

        manager.add_command(cmd1)
        manager.add_command(cmd2)
        manager.add_command(cmd3)

        all_commands = manager.get_all_keyboard_commands()
        assert len(all_commands) == 3
        assert cmd1 in all_commands
        assert cmd2 in all_commands
        assert cmd3 in all_commands

    def test_clear_commands(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.clear_commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, BrailleCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb_cmd = KeyboardCommand("kbCommand", function, "Test Group")
        br_cmd = BrailleCommand("brCommand", function, "Test Group", braille_bindings=(100,))
        manager.add_command(kb_cmd)
        manager.add_command(br_cmd)

        assert len(manager.get_all_keyboard_commands()) == 1
        assert len(manager.get_all_braille_commands()) == 1

        manager.clear_commands()
        assert len(manager.get_all_keyboard_commands()) == 0
        assert len(manager.get_all_braille_commands()) == 0

    def test_get_command_for_event_finds_match(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_event returns matching command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb = self._create_mock_keybinding(test_context)
        kb.matches.return_value = True
        kb.modifiers = 4
        kb.click_count = 1

        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        event = test_context.Mock()
        event.get_click_count.return_value = 1
        event.id = 65
        event.hw_code = 38
        event.modifiers = 4

        result = manager.get_command_for_event(event)
        assert result == cmd

    def test_get_command_for_event_no_match(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_event returns None when no match."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb = self._create_mock_keybinding(test_context)
        kb.matches.return_value = False

        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        event = test_context.Mock()
        event.get_click_count.return_value = 1
        event.id = 65
        event.hw_code = 38
        event.modifiers = 4

        result = manager.get_command_for_event(event)
        assert result is None

    def test_get_command_for_event_skips_inactive(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_event skips inactive commands by default."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb = self._create_mock_keybinding(test_context)
        kb.matches.return_value = True
        kb.modifiers = 4
        kb.click_count = 1

        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb, suspended=True)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        event = test_context.Mock()
        event.get_click_count.return_value = 1
        event.id = 65
        event.hw_code = 38
        event.modifiers = 4

        result = manager.get_command_for_event(event)
        assert result is None

    def test_get_command_for_event_includes_inactive(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_event can include inactive commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb = self._create_mock_keybinding(test_context)
        kb.matches.return_value = True
        kb.modifiers = 4
        kb.click_count = 1

        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb, suspended=True)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        event = test_context.Mock()
        event.get_click_count.return_value = 1
        event.id = 65
        event.hw_code = 38
        event.modifiers = 4

        result = manager.get_command_for_event(event, active_only=False)
        assert result == cmd

    def test_get_command_for_braille_event_finds_match(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_command_for_braille_event returns matching command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        cmd = BrailleCommand("cmd", function, "Test Group", braille_bindings=(100, 200, 300))
        manager.add_command(cmd)

        result = manager.get_command_for_braille_event(200)
        assert result == cmd

    def test_get_command_for_braille_event_no_match(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_command_for_braille_event returns None when no match."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        cmd = BrailleCommand("cmd", function, "Test Group", braille_bindings=(100, 200, 300))
        manager.add_command(cmd)

        result = manager.get_command_for_braille_event(999)
        assert result is None

    def test_get_command_for_braille_event_empty_bindings(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_command_for_braille_event returns None when command has no braille bindings."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        cmd = BrailleCommand("cmd", function, "Test Group")
        manager.add_command(cmd)

        result = manager.get_command_for_braille_event(100)
        assert result is None

    def test_set_group_enabled(self, test_context: OrcaTestContext) -> None:
        """Test set_group_enabled sets enabled state for all commands in group."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function1 = self._create_mock_function(test_context)
        function2 = self._create_mock_function(test_context)
        function3 = self._create_mock_function(test_context)

        cmd1 = KeyboardCommand("cmd1", function1, "Group A")
        cmd2 = KeyboardCommand("cmd2", function2, "Group A")
        cmd3 = KeyboardCommand("cmd3", function3, "Group B")

        manager.add_command(cmd1)
        manager.add_command(cmd2)
        manager.add_command(cmd3)

        manager.set_group_enabled("Group A", False)

        assert cmd1.is_enabled() is False
        assert cmd2.is_enabled() is False
        assert cmd3.is_enabled() is True

    def test_set_group_suspended(self, test_context: OrcaTestContext) -> None:
        """Test set_group_suspended sets suspended state for all commands in group."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function1 = self._create_mock_function(test_context)
        function2 = self._create_mock_function(test_context)
        function3 = self._create_mock_function(test_context)

        cmd1 = KeyboardCommand("cmd1", function1, "Group A")
        cmd2 = KeyboardCommand("cmd2", function2, "Group A")
        cmd3 = KeyboardCommand("cmd3", function3, "Group B")

        manager.add_command(cmd1)
        manager.add_command(cmd2)
        manager.add_command(cmd3)

        manager.set_group_suspended("Group A", True)

        assert cmd1.is_suspended() is True
        assert cmd2.is_suspended() is True
        assert cmd3.is_suspended() is False

    def test_add_grabs_for_command(self, test_context: OrcaTestContext) -> None:
        """Test add_grabs_for_command calls add_grabs on keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb = self._create_mock_keybinding(test_context)
        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        manager.add_grabs_for_command("cmd")

        kb.add_grabs.assert_called_once()

    def test_add_grabs_for_command_no_op_when_not_found(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test add_grabs_for_command is no-op for unknown command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        manager.add_grabs_for_command("nonexistent")

    def test_add_grabs_for_command_no_op_when_no_keybinding(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test add_grabs_for_command is no-op if no keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        cmd = KeyboardCommand("cmd", function, "Test Group")
        manager.add_command(cmd)

        manager.add_grabs_for_command("cmd")

    def test_remove_grabs_for_command(self, test_context: OrcaTestContext) -> None:
        """Test remove_grabs_for_command calls remove_grabs on keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        kb = self._create_mock_keybinding(test_context)
        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        manager.remove_grabs_for_command("cmd")

        kb.remove_grabs.assert_called_once()

    def test_remove_grabs_for_command_no_op_when_not_found(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test remove_grabs_for_command is no-op for unknown command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        manager.remove_grabs_for_command("nonexistent")

    def test_has_multi_click_bindings_true(self, test_context: OrcaTestContext) -> None:
        """Test has_multi_click_bindings returns True when multi-click binding exists."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)

        # Single-click binding (KP_Up keyval = 65431, keycode = 80)
        kb1 = self._create_mock_keybinding(test_context, keyval=65431, keycode=80)
        kb1.matches.return_value = True
        kb1.click_count = 1
        cmd1 = KeyboardCommand("readLine", function, "Flat Review", desktop_keybinding=kb1)
        cmd1.set_keybinding(kb1)
        manager.add_command(cmd1)

        # Double-click binding for same key
        kb2 = self._create_mock_keybinding(test_context, keyval=65431, keycode=80)
        kb2.matches.return_value = True
        kb2.click_count = 2
        cmd2 = KeyboardCommand("spellLine", function, "Flat Review", desktop_keybinding=kb2)
        cmd2.set_keybinding(kb2)
        manager.add_command(cmd2)

        assert manager.has_multi_click_bindings(65431, 80, 0) is True

    def test_has_multi_click_bindings_false_single_only(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test has_multi_click_bindings returns False when only single-click binding exists."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)

        # Only single-click binding (KP_Home keyval = 65429, keycode = 79)
        kb = self._create_mock_keybinding(test_context, keyval=65429, keycode=79)
        kb.matches.return_value = True
        kb.click_count = 1
        cmd = KeyboardCommand("previousLine", function, "Flat Review", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        assert manager.has_multi_click_bindings(65429, 79, 0) is False

    def test_has_multi_click_bindings_false_no_bindings(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test has_multi_click_bindings returns False when no bindings exist for key."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()

        # KP_Home keyval = 65429, keycode = 79
        assert manager.has_multi_click_bindings(65429, 79, 0) is False

    def test_has_multi_click_bindings_respects_modifiers(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test has_multi_click_bindings distinguishes by modifiers."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)

        # Double-click binding with Orca modifier (KP_Up keyval = 65431, keycode = 80)
        kb = self._create_mock_keybinding(test_context, keyval=65431, keycode=80)
        # matches() returns True only when modifiers=256
        kb.matches.side_effect = lambda kv, kc, mods: mods == 256
        kb.click_count = 2
        cmd = KeyboardCommand("someCommand", function, "Test", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # With modifier: has multi-click
        assert manager.has_multi_click_bindings(65431, 80, 256) is True
        # Without modifier: no multi-click bindings
        assert manager.has_multi_click_bindings(65431, 80, 0) is False

    def test_get_command_for_event_shifted_key(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_event finds command via keycode when keyval differs (shifted)."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        # Command bound to 'h' (keyval=104, keycode=38)
        kb = self._create_mock_keybinding(test_context, keyval=104, keycode=38)
        kb.matches.return_value = True
        kb.click_count = 1
        cmd = KeyboardCommand("prevHeading", function, "Structural Nav", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Event has 'H' keyval (72) due to Shift, but same keycode (38)
        event = test_context.Mock()
        event.get_click_count.return_value = 1
        event.id = 72  # 'H' keyval (shifted)
        event.hw_code = 38  # Same keycode as 'h'
        event.modifiers = 1  # Shift

        result = manager.get_command_for_event(event)
        assert result == cmd

    def test_get_command_for_event_unshifted_key(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_event finds command via keyval for unshifted key."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        # Command bound to 'h' (keyval=104, keycode=38)
        kb = self._create_mock_keybinding(test_context, keyval=104, keycode=38)
        kb.matches.return_value = True
        kb.click_count = 1
        cmd = KeyboardCommand("nextHeading", function, "Structural Nav", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Event has 'h' keyval (104), no shift
        event = test_context.Mock()
        event.get_click_count.return_value = 1
        event.id = 104  # 'h' keyval (unshifted)
        event.hw_code = 38
        event.modifiers = 0

        result = manager.get_command_for_event(event)
        assert result == cmd

    def test_has_multi_click_bindings_shifted_key(self, test_context: OrcaTestContext) -> None:
        """Test has_multi_click_bindings finds binding via keycode when keyval differs."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        # Single-click binding for 'h' (keyval=104, keycode=38)
        kb1 = self._create_mock_keybinding(test_context, keyval=104, keycode=38)
        kb1.matches.return_value = True
        kb1.click_count = 1
        cmd1 = KeyboardCommand("nextHeading", function, "Structural Nav", desktop_keybinding=kb1)
        cmd1.set_keybinding(kb1)
        manager.add_command(cmd1)

        # Double-click binding for same key
        kb2 = self._create_mock_keybinding(test_context, keyval=104, keycode=38)
        kb2.matches.return_value = True
        kb2.click_count = 2
        cmd2 = KeyboardCommand("listHeadings", function, "Structural Nav", desktop_keybinding=kb2)
        cmd2.set_keybinding(kb2)
        manager.add_command(cmd2)

        # Query with 'H' keyval (72) due to Shift, but same keycode (38)
        # Should find multi-click binding via keycode
        assert manager.has_multi_click_bindings(72, 38, 1) is True

    def test_has_multi_click_bindings_unshifted_key(self, test_context: OrcaTestContext) -> None:
        """Test has_multi_click_bindings finds binding via keyval for unshifted key."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        # Single-click binding for 'h' (keyval=104, keycode=38)
        kb1 = self._create_mock_keybinding(test_context, keyval=104, keycode=38)
        kb1.matches.return_value = True
        kb1.click_count = 1
        cmd1 = KeyboardCommand("nextHeading", function, "Structural Nav", desktop_keybinding=kb1)
        cmd1.set_keybinding(kb1)
        manager.add_command(cmd1)

        # Double-click binding for same key
        kb2 = self._create_mock_keybinding(test_context, keyval=104, keycode=38)
        kb2.matches.return_value = True
        kb2.click_count = 2
        cmd2 = KeyboardCommand("listHeadings", function, "Structural Nav", desktop_keybinding=kb2)
        cmd2.set_keybinding(kb2)
        manager.add_command(cmd2)

        # Query with 'h' keyval (104), unshifted - should find via keyval
        assert manager.has_multi_click_bindings(104, 38, 0) is True


@pytest.mark.unit
class TestGetManager:
    """Test the get_manager singleton function."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        return essential_modules

    def test_get_manager_returns_singleton(self, test_context: OrcaTestContext) -> None:
        """Test that get_manager returns the same instance."""

        self._setup_dependencies(test_context)
        from orca.command_manager import get_manager

        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2

    def test_get_manager_returns_command_manager(self, test_context: OrcaTestContext) -> None:
        """Test that get_manager returns a CommandManager instance."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager, get_manager

        manager = get_manager()
        assert isinstance(manager, CommandManager)
