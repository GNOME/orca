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
    """Test Command class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for command_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        input_event_mock = essential_modules["orca.input_event"]
        input_event_mock.InputEventHandler = test_context.Mock

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.KeyBinding = test_context.Mock
        keybindings_mock.KeyBindings = test_context.Mock

        return essential_modules

    def _create_mock_handler(self, test_context: OrcaTestContext) -> Mock:
        """Creates a mock InputEventHandler."""

        handler = test_context.Mock()
        handler.function = test_context.Mock()
        handler.description = "Test handler description"
        handler.learn_mode_enabled = True
        return handler

    def _create_mock_keybinding(self, test_context: OrcaTestContext) -> Mock:
        """Creates a mock KeyBinding."""

        kb = test_context.Mock()
        kb.handler = self._create_mock_handler(test_context)
        return kb

    def test_init_minimal(self, test_context: OrcaTestContext) -> None:
        """Test Command.__init__ with minimal arguments."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        command = Command("testHandler", handler, "Test Group")

        assert command.get_handler_name() == "testHandler"
        assert command.get_handler() == handler
        assert command.get_group_label() == "Test Group"
        assert command.get_description() == ""
        assert command.get_keybinding() is None
        assert command.get_default_keybinding() is None
        assert command.get_learn_mode_enabled() is True

    def test_init_full(self, test_context: OrcaTestContext) -> None:
        """Test Command.__init__ with all arguments."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        keybinding = self._create_mock_keybinding(test_context)
        command = Command(
            "fullHandler",
            handler,
            "Full Group",
            "Full description",
            keybinding,
            False
        )

        assert command.get_handler_name() == "fullHandler"
        assert command.get_handler() == handler
        assert command.get_group_label() == "Full Group"
        assert command.get_description() == "Full description"
        assert command.get_keybinding() == keybinding
        assert command.get_default_keybinding() == keybinding
        assert command.get_learn_mode_enabled() is False

    def test_set_keybinding(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        command = Command("testHandler", handler, "Test Group")

        assert command.get_keybinding() is None

        new_kb = self._create_mock_keybinding(test_context)
        command.set_keybinding(new_kb)
        assert command.get_keybinding() == new_kb

        command.set_keybinding(None)
        assert command.get_keybinding() is None

    def test_set_default_keybinding(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_default_keybinding."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        command = Command("testHandler", handler, "Test Group")

        assert command.get_default_keybinding() is None

        default_kb = self._create_mock_keybinding(test_context)
        command.set_default_keybinding(default_kb)
        assert command.get_default_keybinding() == default_kb

    def test_set_group_label(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_group_label."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        command = Command("testHandler", handler, "Original Group")

        assert command.get_group_label() == "Original Group"

        command.set_group_label("New Group")
        assert command.get_group_label() == "New Group"

    def test_set_learn_mode_enabled(self, test_context: OrcaTestContext) -> None:
        """Test Command.set_learn_mode_enabled."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        command = Command("testHandler", handler, "Test Group")

        assert command.get_learn_mode_enabled() is True

        command.set_learn_mode_enabled(False)
        assert command.get_learn_mode_enabled() is False

        command.set_learn_mode_enabled(True)
        assert command.get_learn_mode_enabled() is True

    def test_keybinding_independence(self, test_context: OrcaTestContext) -> None:
        """Test that current and default keybindings are independent."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command

        handler = self._create_mock_handler(test_context)
        initial_kb = self._create_mock_keybinding(test_context)
        command = Command("testHandler", handler, "Test Group", "", initial_kb)

        assert command.get_keybinding() == initial_kb
        assert command.get_default_keybinding() == initial_kb

        new_kb = self._create_mock_keybinding(test_context)
        command.set_keybinding(new_kb)

        assert command.get_keybinding() == new_kb
        assert command.get_default_keybinding() == initial_kb


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

    def _create_mock_handler(
        self,
        test_context: OrcaTestContext,
        description: str = "Test handler",
        learn_mode: bool = True
    ) -> Mock:
        """Creates a mock InputEventHandler."""

        handler = test_context.Mock()
        handler.function = test_context.Mock()
        handler.description = description
        handler.learn_mode_enabled = learn_mode
        return handler

    def _create_mock_keybinding(
        self,
        test_context: OrcaTestContext,
        handler: Mock
    ) -> Mock:
        """Creates a mock KeyBinding for a handler."""

        kb = test_context.Mock()
        kb.handler = handler
        return kb

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.__init__."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()
        assert manager.get_all_commands() == ()

    def test_add_and_get_command(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.add_command and get_command."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()
        handler = self._create_mock_handler(test_context)
        command = Command("testHandler", handler, "Test Group")

        manager.add_command(command)

        retrieved = manager.get_command("testHandler")
        assert retrieved == command

        assert manager.get_command("nonexistent") is None

    def test_get_all_commands(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.get_all_commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler1 = self._create_mock_handler(test_context, "Handler 1")
        handler2 = self._create_mock_handler(test_context, "Handler 2")
        handler3 = self._create_mock_handler(test_context, "Handler 3")

        cmd1 = Command("handler1", handler1, "Group A")
        cmd2 = Command("handler2", handler2, "Group B")
        cmd3 = Command("handler3", handler3, "Group A")

        manager.add_command(cmd1)
        manager.add_command(cmd2)
        manager.add_command(cmd3)

        all_commands = manager.get_all_commands()
        assert len(all_commands) == 3
        assert cmd1 in all_commands
        assert cmd2 in all_commands
        assert cmd3 in all_commands

    def test_get_commands_by_group_label(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.get_commands_by_group_label."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler1 = self._create_mock_handler(test_context, "Handler 1")
        handler2 = self._create_mock_handler(test_context, "Handler 2")
        handler3 = self._create_mock_handler(test_context, "Handler 3")

        cmd1 = Command("handler1", handler1, "Group A")
        cmd2 = Command("handler2", handler2, "Group B")
        cmd3 = Command("handler3", handler3, "Group A")

        manager.add_command(cmd1)
        manager.add_command(cmd2)
        manager.add_command(cmd3)

        group_a = manager.get_commands_by_group_label("Group A")
        assert len(group_a) == 2
        assert cmd1 in group_a
        assert cmd3 in group_a
        assert cmd2 not in group_a

        group_b = manager.get_commands_by_group_label("Group B")
        assert len(group_b) == 1
        assert cmd2 in group_b

        empty_group = manager.get_commands_by_group_label("Nonexistent")
        assert len(empty_group) == 0

    def test_clear_commands(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.clear_commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        cmd = Command("testHandler", handler, "Test Group")
        manager.add_command(cmd)

        assert len(manager.get_all_commands()) == 1

        manager.clear_commands()
        assert len(manager.get_all_commands()) == 0
        assert manager.get_command("testHandler") is None

    def test_add_command_overwrites_existing(self, test_context: OrcaTestContext) -> None:
        """Test that adding a command with same name overwrites the existing one."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler1 = self._create_mock_handler(test_context, "Original")
        handler2 = self._create_mock_handler(test_context, "Replacement")

        cmd1 = Command("sameHandler", handler1, "Group A")
        cmd2 = Command("sameHandler", handler2, "Group B")

        manager.add_command(cmd1)
        assert manager.get_command("sameHandler").get_group_label() == "Group A"

        manager.add_command(cmd2)
        assert manager.get_command("sameHandler").get_group_label() == "Group B"
        assert len(manager.get_all_commands()) == 1

    def test_set_default_bindings_from_module(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.set_default_bindings_from_module."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler1 = self._create_mock_handler(test_context)
        handler2 = self._create_mock_handler(test_context)

        cmd1 = Command("handler1", handler1, "Test Group")
        cmd2 = Command("handler2", handler2, "Test Group")
        manager.add_command(cmd1)
        manager.add_command(cmd2)

        kb1 = self._create_mock_keybinding(test_context, handler1)
        kb2 = self._create_mock_keybinding(test_context, handler2)

        module_bindings = test_context.Mock()
        module_bindings.key_bindings = [kb1, kb2]

        handlers = {"handler1": handler1, "handler2": handler2}
        skip = frozenset()

        manager.set_default_bindings_from_module(handlers, module_bindings, skip)

        assert cmd1.get_default_keybinding() == kb1
        assert cmd2.get_default_keybinding() == kb2
        assert cmd1.get_keybinding() == kb1
        assert cmd2.get_keybinding() == kb2

    def test_set_default_bindings_skips_handlers(self, test_context: OrcaTestContext) -> None:
        """Test that set_default_bindings_from_module respects skip_handlers."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler1 = self._create_mock_handler(test_context)
        handler2 = self._create_mock_handler(test_context)

        cmd1 = Command("handler1", handler1, "Test Group")
        cmd2 = Command("handler2", handler2, "Test Group")
        manager.add_command(cmd1)
        manager.add_command(cmd2)

        kb1 = self._create_mock_keybinding(test_context, handler1)
        kb2 = self._create_mock_keybinding(test_context, handler2)

        module_bindings = test_context.Mock()
        module_bindings.key_bindings = [kb1, kb2]

        handlers = {"handler1": handler1, "handler2": handler2}
        skip = frozenset(["handler1"])

        manager.set_default_bindings_from_module(handlers, module_bindings, skip)

        assert cmd1.get_default_keybinding() is None
        assert cmd2.get_default_keybinding() == kb2

    def test_set_default_bindings_only_when_none(self, test_context: OrcaTestContext) -> None:
        """Test that set_default_bindings_from_module only sets if default is None."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        existing_kb = self._create_mock_keybinding(test_context, handler)
        cmd = Command("handler", handler, "Test Group", "", existing_kb)
        manager.add_command(cmd)

        new_kb = self._create_mock_keybinding(test_context, handler)
        module_bindings = test_context.Mock()
        module_bindings.key_bindings = [new_kb]

        handlers = {"handler": handler}
        skip = frozenset()

        manager.set_default_bindings_from_module(handlers, module_bindings, skip)

        assert cmd.get_default_keybinding() == existing_kb

    def test_clear_deleted_bindings(self, test_context: OrcaTestContext) -> None:
        """Test CommandManager.clear_deleted_bindings."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler1 = self._create_mock_handler(test_context)
        handler2 = self._create_mock_handler(test_context)

        kb1 = self._create_mock_keybinding(test_context, handler1)
        kb2 = self._create_mock_keybinding(test_context, handler2)

        cmd1 = Command("handler1", handler1, "Test Group", "", kb1)
        cmd2 = Command("handler2", handler2, "Test Group", "", kb2)
        manager.add_command(cmd1)
        manager.add_command(cmd2)

        handlers = {"handler1": handler1, "handler2": handler2}
        profile_keybindings = {"handler1": []}
        skip = frozenset()

        manager.clear_deleted_bindings(handlers, profile_keybindings, skip)

        assert cmd1.get_keybinding() is None
        assert cmd2.get_keybinding() == kb2

    def test_clear_deleted_bindings_skips_handlers(self, test_context: OrcaTestContext) -> None:
        """Test that clear_deleted_bindings respects skip_handlers."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        kb = self._create_mock_keybinding(test_context, handler)
        cmd = Command("handler", handler, "Test Group", "", kb)
        manager.add_command(cmd)

        handlers = {"handler": handler}
        profile_keybindings = {"handler": []}
        skip = frozenset(["handler"])

        manager.clear_deleted_bindings(handlers, profile_keybindings, skip)

        assert cmd.get_keybinding() == kb

    def test_apply_customized_bindings_updates_existing(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that apply_customized_bindings updates existing commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        cmd = Command("handler", handler, "Original Group")
        manager.add_command(cmd)

        new_kb = self._create_mock_keybinding(test_context, handler)
        customized = test_context.Mock()
        customized.key_bindings = [new_kb]

        handlers = {"handler": handler}
        skip = frozenset()

        manager.apply_customized_bindings(handlers, customized, "New Group", skip)

        assert cmd.get_keybinding() == new_kb
        assert cmd.get_group_label() == "New Group"

    def test_apply_customized_bindings_adds_new(self, test_context: OrcaTestContext) -> None:
        """Test that apply_customized_bindings adds new commands."""

        self._setup_dependencies(test_context)
        from orca.command_manager import CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        kb = self._create_mock_keybinding(test_context, handler)
        customized = test_context.Mock()
        customized.key_bindings = [kb]

        handlers = {"newHandler": handler}
        skip = frozenset()

        manager.apply_customized_bindings(handlers, customized, "New Group", skip)

        cmd = manager.get_command("newHandler")
        assert cmd is not None
        assert cmd.get_keybinding() == kb
        assert cmd.get_group_label() == "New Group"

    def test_apply_customized_bindings_no_group_update(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test apply_customized_bindings with update_group_label=False."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        cmd = Command("handler", handler, "Original Group")
        manager.add_command(cmd)

        new_kb = self._create_mock_keybinding(test_context, handler)
        customized = test_context.Mock()
        customized.key_bindings = [new_kb]

        handlers = {"handler": handler}
        skip = frozenset()

        manager.apply_customized_bindings(
            handlers, customized, "New Group", skip, update_group_label=False
        )

        assert cmd.get_keybinding() == new_kb
        assert cmd.get_group_label() == "Original Group"

    def test_apply_customized_bindings_skips_handlers(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that apply_customized_bindings respects skip_handlers."""

        self._setup_dependencies(test_context)
        from orca.command_manager import Command, CommandManager

        manager = CommandManager()

        handler = self._create_mock_handler(test_context)
        cmd = Command("handler", handler, "Original Group")
        manager.add_command(cmd)

        new_kb = self._create_mock_keybinding(test_context, handler)
        customized = test_context.Mock()
        customized.key_bindings = [new_kb]

        handlers = {"handler": handler}
        skip = frozenset(["handler"])

        manager.apply_customized_bindings(handlers, customized, "New Group", skip)

        assert cmd.get_keybinding() is None
        assert cmd.get_group_label() == "Original Group"


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
