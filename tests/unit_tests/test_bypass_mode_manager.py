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

        additional_modules = ["orca.orca_modifier_manager"]
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
        orca_modifier_manager_mock.get_manager = test_context.Mock(
            return_value=modifier_manager_instance
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

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test BypassModeManager initialization."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        assert manager._is_active is False
        assert manager._handlers is not None
        assert manager._bindings is not None
        essential_modules["orca.keybindings"].KeyBindings.assert_called()

    @pytest.mark.parametrize(
        "method_name,is_desktop,expected_log_msg",
        [
            pytest.param(
                "get_bindings",
                True,
                "BYPASS MODE MANAGER: Refreshing bindings. Is desktop: True",
                id="bindings_desktop",
            ),
            pytest.param(
                "get_bindings",
                False,
                "BYPASS MODE MANAGER: Refreshing bindings. Is desktop: False",
                id="bindings_not_desktop",
            ),
            pytest.param(
                "get_handlers",
                None,
                "BYPASS MODE MANAGER: Refreshing handlers.",
                id="handlers_refresh",
            ),
        ],
    )
    def test_get_bindings_and_handlers_refresh(
        self,
        test_context: OrcaTestContext,
        method_name: str,
        is_desktop: bool | None,
        expected_log_msg: str,
    ) -> None:
        """Test get_bindings and get_handlers with refresh=True."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        essential_modules["orca.debug"].print_message.reset_mock()

        if method_name == "get_bindings":
            bindings_result = manager.get_bindings(refresh=True, is_desktop=is_desktop or False)
            assert bindings_result is not None
        else:
            handlers_result = manager.get_handlers(refresh=True)
            assert handlers_result is not None
        essential_modules["orca.debug"].print_message.assert_called_with(
            essential_modules["orca.debug"].LEVEL_INFO,
            expected_log_msg,
            True,
        )

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test _setup_handlers method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        manager._setup_handlers()
        assert "bypass_mode_toggle" in manager._handlers
        expected_handler = essential_modules["input_event_handler"]
        assert manager._handlers["bypass_mode_toggle"] == expected_handler
        input_event = essential_modules["orca.input_event"]
        input_event.InputEventHandler.assert_called_with(
            manager.toggle_enabled, "Toggle all Orca command keys"
        )

    @pytest.mark.parametrize(
        "default_mask,alt_mask",
        [
            pytest.param(1, 2, id="original_config"),
            pytest.param(8, 16, id="custom_config"),
        ],
    )
    def test_setup_bindings(
        self, test_context: OrcaTestContext, default_mask: int, alt_mask: int
    ) -> None:
        """Test _setup_bindings method with different key binding configurations."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.DEFAULT_MODIFIER_MASK = default_mask
        keybindings_mock.ALT_MODIFIER_MASK = alt_mask
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        keybindings_mock.KeyBinding.reset_mock()
        manager._setup_bindings()

        essential_modules["orca.keybindings"].KeyBinding.assert_called_with(
            "BackSpace",
            default_mask,
            alt_mask,
            manager._handlers["bypass_mode_toggle"],
            1,
            True,
        )

        key_bindings_instance = essential_modules["key_bindings_instance"]
        key_bindings_instance.add.assert_called()
        settings_manager_instance = essential_modules["settings_manager_instance"]
        settings_manager_instance.override_key_bindings.assert_called_with(
            manager._handlers, key_bindings_instance, False
        )

    @pytest.mark.parametrize(
        "initial_active,has_event,expected_active,expected_message,"
        "expected_grabs_call,expected_modifier_call",
        [
            (
                False,
                True,
                True,
                "Orca command keys off.",
                "remove_key_grabs",
                "unset_orca_modifiers",
            ),
            (
                False,
                False,
                True,
                None,
                "remove_key_grabs",
                "unset_orca_modifiers",
            ),
            (
                True,
                True,
                False,
                "Orca command keys on.",
                "add_key_grabs",
                "refresh_orca_modifiers",
            ),
            (
                True,
                False,
                False,
                None,
                "add_key_grabs",
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

        grabs_method = getattr(mock_script, expected_grabs_call)
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

        if not initial_active and key_bindings:
            mock_script.key_bindings.add.assert_any_call(key_bindings[0], include_grabs=True)
            mock_script.key_bindings.add.assert_any_call(key_bindings[1], include_grabs=True)

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

    def test_bindings_with_key_override(self, test_context: OrcaTestContext) -> None:
        """Test that bindings are properly configured with key overrides."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        mock_overridden_bindings = test_context.Mock()
        settings_manager_instance = essential_modules["settings_manager_instance"]
        settings_manager_instance.override_key_bindings.return_value = mock_overridden_bindings
        from orca.bypass_mode_manager import BypassModeManager

        manager = BypassModeManager()
        bindings = manager.get_bindings(refresh=True)
        assert bindings == mock_overridden_bindings

        key_bindings_instance = essential_modules["key_bindings_instance"]
        settings_manager_instance.override_key_bindings.assert_called_with(
            manager._handlers, key_bindings_instance, False
        )

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
