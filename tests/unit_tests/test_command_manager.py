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
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

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
            "fullCommand", function, "Full Group", "Full description", enabled=False, suspended=True
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
            "fullCommand",
            function,
            "Full Group",
            "Full description",
            desktop_keybinding=desktop_kb,
            laptop_keybinding=laptop_kb,
        )

        assert command.get_name() == "fullCommand"
        assert command.get_default_keybinding(is_desktop=True) == desktop_kb
        assert command.get_default_keybinding(is_desktop=False) == laptop_kb

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
            "testCommand", function, "Test Group", desktop_keybinding=keybinding
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
            "testCommand", function, "Test Group", desktop_keybinding=keybinding, enabled=False
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
            "testCommand", function, "Test Group", desktop_keybinding=keybinding, suspended=True
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
            "testCommand", function, "Test Group", "Test description", braille_bindings=(1, 2, 3)
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

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

        return essential_modules

    def _create_mock_function(
        self,
        test_context: OrcaTestContext,
        _description: str = "Test function",
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
        kb.keysymstring = "a"
        return kb

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.__init__."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        assert not manager.get_all_keyboard_commands()
        assert not manager.get_all_braille_commands()

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
        event.is_keypad_key_with_numlock_on.return_value = False

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
        event.is_keypad_key_with_numlock_on.return_value = False

        result = manager.get_command_for_event(event, active_only=False)
        assert result == cmd

    def test_get_command_for_braille_event_finds_match(self, test_context: OrcaTestContext) -> None:
        """Test get_command_for_braille_event returns matching command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import BrailleCommand, CommandManager

        manager = CommandManager()

        function = self._create_mock_function(test_context)
        cmd = BrailleCommand("cmd", function, "Test Group", braille_bindings=(100, 200, 300))
        manager.add_command(cmd)

        result = manager.get_command_for_braille_event(200)
        assert result == cmd

    def test_get_command_for_braille_event_no_match(self, test_context: OrcaTestContext) -> None:
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
        event.is_keypad_key_with_numlock_on.return_value = False

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
        event.is_keypad_key_with_numlock_on.return_value = False

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

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

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


@pytest.mark.unit
class TestDiffBasedGrabUpdates:
    """Test diff-based grab updates in CommandManager."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies(["orca.orca_modifier_manager"])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        orca_modifier_manager_mock = essential_modules["orca.orca_modifier_manager"]
        modifier_manager_instance = test_context.Mock()
        modifier_manager_instance.refresh_orca_modifiers = test_context.Mock()
        orca_modifier_manager_mock.get_manager = test_context.Mock(
            return_value=modifier_manager_instance
        )

        # Mock settings_manager for apply_user_overrides
        settings_manager_mock = essential_modules["orca.settings_manager"]
        settings_manager_instance = test_context.Mock()
        settings_manager_instance.get_active_keybindings = test_context.Mock(return_value={})
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=settings_manager_instance
        )

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

        essential_modules["modifier_manager_instance"] = modifier_manager_instance
        essential_modules["settings_manager_instance"] = settings_manager_instance
        return essential_modules

    def _create_mock_function(self, test_context: OrcaTestContext) -> Mock:
        """Creates a mock function for a Command."""

        function = test_context.Mock()
        function.return_value = True
        return function

    def _create_mock_keybinding(
        self,
        test_context: OrcaTestContext,
        keysymstring: str = "a",
        modifiers: int = 0,
        click_count: int = 1,
        keyval: int = 65,
        keycode: int = 38,
    ) -> Mock:
        """Creates a mock KeyBinding with specified properties."""

        kb = test_context.Mock()
        kb.keysymstring = keysymstring
        kb.modifiers = modifiers
        kb.click_count = click_count
        kb.keyval = keyval
        kb.keycode = keycode
        kb.has_grabs = test_context.Mock(return_value=False)
        kb.add_grabs = test_context.Mock()
        kb.remove_grabs = test_context.Mock()
        kb.get_grab_ids = test_context.Mock(return_value=[])
        kb.set_grab_ids = test_context.Mock()
        return kb

    def test_binding_key_returns_tuple(self, test_context: OrcaTestContext) -> None:
        """Test _binding_key returns correct tuple."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        kb = self._create_mock_keybinding(
            test_context, keysymstring="h", modifiers=256, click_count=2
        )

        result = manager._binding_key(kb)
        assert result == ("h", 256, 2)

    def test_binding_key_returns_none_for_none(self, test_context: OrcaTestContext) -> None:
        """Test _binding_key returns None for None keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        assert manager._binding_key(None) is None

    def test_binding_key_returns_none_for_empty_keysymstring(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _binding_key returns None when keysymstring is empty."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        kb = self._create_mock_keybinding(test_context, keysymstring="")
        assert manager._binding_key(kb) is None

    def test_diff_transfers_grab_ids_for_matching_bindings(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that grab IDs are transferred when bindings match."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Old command with grabs
        old_kb = self._create_mock_keybinding(test_context, keysymstring="h", modifiers=256)
        old_kb.has_grabs.return_value = True
        old_kb.get_grab_ids.return_value = [42, 43]
        old_cmd = KeyboardCommand("cmd", function, "Group", desktop_keybinding=old_kb)
        old_cmd.set_keybinding(old_kb)
        old_commands = {"cmd": old_cmd}

        # New command with same binding but no grabs yet
        new_kb = self._create_mock_keybinding(test_context, keysymstring="h", modifiers=256)
        new_kb.has_grabs.return_value = False
        new_cmd = KeyboardCommand("cmd", function, "Group", desktop_keybinding=new_kb)
        new_cmd.set_keybinding(new_kb)
        new_commands = {"cmd": new_cmd}

        manager._keyboard_commands = old_commands
        manager._diff_and_update_grabs(new_commands, "test")

        # Verify grab IDs were transferred
        new_kb.set_grab_ids.assert_called_once_with([42, 43])
        old_kb.set_grab_ids.assert_called_once_with([])
        # Neither add nor remove should be called
        new_kb.add_grabs.assert_not_called()
        old_kb.remove_grabs.assert_not_called()

    def test_diff_removes_grabs_for_old_only_bindings(self, test_context: OrcaTestContext) -> None:
        """Test that grabs are removed for bindings only in old commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Old command with grabs
        old_kb = self._create_mock_keybinding(test_context, keysymstring="h", modifiers=256)
        old_kb.has_grabs.return_value = True
        old_cmd = KeyboardCommand("old_cmd", function, "Group", desktop_keybinding=old_kb)
        old_cmd.set_keybinding(old_kb)
        old_commands = {"old_cmd": old_cmd}

        # Empty new commands
        new_commands: dict = {}

        manager._keyboard_commands = old_commands
        manager._diff_and_update_grabs(new_commands, "test")

        # Verify grabs were removed
        old_kb.remove_grabs.assert_called_once()

    def test_diff_adds_grabs_for_new_only_bindings(self, test_context: OrcaTestContext) -> None:
        """Test that grabs are added for bindings only in new commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Empty old commands
        old_commands: dict = {}

        # New command without grabs
        new_kb = self._create_mock_keybinding(test_context, keysymstring="h", modifiers=256)
        new_kb.has_grabs.return_value = False
        new_cmd = KeyboardCommand("new_cmd", function, "Group", desktop_keybinding=new_kb)
        new_cmd.set_keybinding(new_kb)
        new_commands = {"new_cmd": new_cmd}

        manager._keyboard_commands = old_commands
        manager._diff_and_update_grabs(new_commands, "test")

        # Verify grabs were added
        new_kb.add_grabs.assert_called_once()

    def test_set_active_commands_uses_diff(self, test_context: OrcaTestContext) -> None:
        """Test set_active_commands uses diff-based updates."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Add initial command with grabs
        old_kb = self._create_mock_keybinding(test_context, keysymstring="a")
        old_kb.has_grabs.return_value = True
        old_cmd = KeyboardCommand("old_cmd", function, "Group", desktop_keybinding=old_kb)
        old_cmd.set_keybinding(old_kb)
        manager.add_command(old_cmd)

        # Set new commands
        new_kb = self._create_mock_keybinding(test_context, keysymstring="b")
        new_kb.has_grabs.return_value = False
        new_cmd = KeyboardCommand("new_cmd", function, "Group", desktop_keybinding=new_kb)
        new_cmd.set_keybinding(new_kb)

        manager.set_active_commands({"new_cmd": new_cmd}, "test")

        # Old binding should have grabs removed, new binding should have grabs added
        old_kb.remove_grabs.assert_called_once()
        new_kb.add_grabs.assert_called_once()

    def test_activate_commands_applies_overrides(self, test_context: OrcaTestContext) -> None:
        """Test activate_commands applies user overrides."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Add a command
        kb = self._create_mock_keybinding(test_context, keysymstring="a")
        cmd = KeyboardCommand("test_cmd", function, "Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Activate commands should apply user overrides
        settings_manager = essential_modules["settings_manager_instance"]
        settings_manager.get_active_keybindings.return_value = {}

        manager.activate_commands("test")

        # Should call get_active_keybindings to apply overrides
        settings_manager.get_active_keybindings.assert_called()

    def test_diff_skips_inactive_commands(self, test_context: OrcaTestContext) -> None:
        """Test that diff skips inactive commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Old command that is disabled (inactive)
        old_kb = self._create_mock_keybinding(test_context, keysymstring="h")
        old_kb.has_grabs.return_value = True
        old_cmd = KeyboardCommand(
            "cmd", function, "Group", desktop_keybinding=old_kb, enabled=False
        )
        old_cmd.set_keybinding(old_kb)
        old_commands = {"cmd": old_cmd}

        # New command that is also disabled
        new_kb = self._create_mock_keybinding(test_context, keysymstring="h")
        new_cmd = KeyboardCommand(
            "cmd", function, "Group", desktop_keybinding=new_kb, enabled=False
        )
        new_cmd.set_keybinding(new_kb)
        new_commands = {"cmd": new_cmd}

        manager._keyboard_commands = old_commands
        manager._diff_and_update_grabs(new_commands, "test")

        # Neither should have grabs modified since both are inactive
        old_kb.remove_grabs.assert_not_called()
        new_kb.add_grabs.assert_not_called()
        new_kb.set_grab_ids.assert_not_called()

    def test_set_group_suspended_removes_grabs_when_suspending(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_group_suspended removes grabs when suspending active commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Active command with grabs
        kb = self._create_mock_keybinding(test_context, keysymstring="h")
        kb.has_grabs.return_value = True
        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Suspend the group
        manager.set_group_suspended("Test Group", True)

        # Grabs should be removed
        kb.remove_grabs.assert_called_once()
        kb.add_grabs.assert_not_called()

    def test_set_group_suspended_adds_grabs_when_unsuspending(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_group_suspended adds grabs when unsuspending commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Suspended command without grabs
        kb = self._create_mock_keybinding(test_context, keysymstring="h")
        kb.has_grabs.return_value = False
        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb, suspended=True)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Unsuspend the group
        manager.set_group_suspended("Test Group", False)

        # Grabs should be added
        kb.add_grabs.assert_called_once()
        kb.remove_grabs.assert_not_called()

    def test_set_group_suspended_no_change_when_already_in_state(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_group_suspended does nothing when commands already in desired state."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Already suspended command
        kb = self._create_mock_keybinding(test_context, keysymstring="h")
        kb.has_grabs.return_value = False
        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb, suspended=True)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Suspend again (no change)
        manager.set_group_suspended("Test Group", True)

        # No grabs should be modified
        kb.add_grabs.assert_not_called()
        kb.remove_grabs.assert_not_called()

    def test_set_group_enabled_removes_grabs_when_disabling(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_group_enabled removes grabs when disabling active commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Active command with grabs
        kb = self._create_mock_keybinding(test_context, keysymstring="h")
        kb.has_grabs.return_value = True
        cmd = KeyboardCommand("cmd", function, "Test Group", desktop_keybinding=kb)
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Disable the group
        manager.set_group_enabled("Test Group", False)

        # Grabs should be removed
        kb.remove_grabs.assert_called_once()
        kb.add_grabs.assert_not_called()

    def test_set_group_enabled_skips_group_toggle_commands(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_group_enabled skips group toggle commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import KeyboardCommand, CommandManager

        manager = CommandManager()
        function = self._create_mock_function(test_context)

        # Group toggle command with grabs
        kb = self._create_mock_keybinding(test_context, keysymstring="z")
        kb.has_grabs.return_value = True
        cmd = KeyboardCommand(
            "toggle_cmd", function, "Test Group", desktop_keybinding=kb, is_group_toggle=True
        )
        cmd.set_keybinding(kb)
        manager.add_command(cmd)

        # Disable the group
        manager.set_group_enabled("Test Group", False)

        # Group toggle should not have grabs removed (it stays active)
        kb.remove_grabs.assert_not_called()
        # Command should still be enabled
        assert cmd.is_enabled() is True
