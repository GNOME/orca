# Unit tests for sleep_mode_manager.py methods.
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
# pylint: disable=too-many-locals

"""Unit tests for sleep_mode_manager.py methods."""

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
class TestSleepModeManager:
    """Test SleepModeManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for sleep_mode_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies([])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.debugFile = None
        debug_mock.LEVEL_INFO = 800

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.get_name = test_context.Mock(return_value="TestApp")

        braille_mock = essential_modules["orca.braille"]
        braille_mock.clear = test_context.Mock()

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.TOGGLE_SLEEP_MODE = "Toggle sleep mode for the current application"

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(
            return_value=controller_mock
        )
        dbus_service_mock.command = lambda func: func

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        keybindings_mock = essential_modules["orca.keybindings"]
        key_bindings_instance = test_context.Mock()
        key_bindings_instance.is_empty = test_context.Mock(return_value=False)
        key_bindings_instance.remove_key_grabs = test_context.Mock(return_value=None)
        key_bindings_instance.add = test_context.Mock(return_value=None)
        keybindings_mock.KeyBindings = test_context.Mock(return_value=key_bindings_instance)
        keybindings_mock.KeyBinding = test_context.Mock()
        keybindings_mock.DEFAULT_MODIFIER_MASK = 1
        keybindings_mock.SHIFT_ALT_CTRL_MODIFIER_MASK = 15

        messages_mock = essential_modules["orca.messages"]
        messages_mock.SLEEP_MODE_ENABLED_FOR = "Sleep mode enabled for %s."
        messages_mock.SLEEP_MODE_DISABLED_FOR = "Sleep mode disabled for %s."

        script_manager_mock = essential_modules["orca.script_manager"]
        script_manager_instance = test_context.Mock()
        script_manager_instance.get_or_create_sleep_mode_script = test_context.Mock()
        script_manager_instance.set_active_script = test_context.Mock()
        script_manager_instance.get_script = test_context.Mock()
        script_manager_mock.get_manager = test_context.Mock(
            return_value=script_manager_instance
        )

        essential_modules["controller"] = controller_mock
        essential_modules["input_event_handler"] = input_event_handler_mock
        essential_modules["key_bindings_instance"] = key_bindings_instance
        essential_modules["script_manager_instance"] = script_manager_instance

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager.__init__ with default parameters."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        assert manager._handlers is not None
        assert manager._bindings is not None
        assert not manager._apps
        essential_modules["orca.keybindings"].KeyBindings.assert_called()

        assert essential_modules["orca.dbus_service"] is not None
        assert essential_modules["controller"] is not None

    @pytest.mark.parametrize(
        "is_desktop",
        [
            pytest.param(True, id="desktop"),
            pytest.param(False, id="not_desktop"),
        ],
    )
    def test_get_bindings_refresh(self, test_context: OrcaTestContext, is_desktop: bool) -> None:
        """Test SleepModeManager.get_bindings with refresh=True and various desktop settings."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        bindings = manager.get_bindings(refresh=True, is_desktop=is_desktop)
        assert bindings is not None
        essential_modules["orca.debug"].print_message.assert_any_call(
            essential_modules["orca.debug"].LEVEL_INFO,
            f"SLEEP MODE MANAGER: Refreshing bindings. Is desktop: {is_desktop}",
            True,
        )

    def test_get_handlers_refresh_true(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager.get_handlers with refresh=True."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        handlers = manager.get_handlers(refresh=True)
        assert handlers is not None
        essential_modules["orca.debug"].print_message.assert_any_call(
            essential_modules["orca.debug"].LEVEL_INFO,
            "SLEEP MODE MANAGER: Refreshing handlers.",
            True,
        )

    def test_is_active_for_app_with_active_app(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager.is_active_for_app returns True for active app."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        app_hash = hash(mock_app)
        manager._apps.append(app_hash)

        essential_modules["orca.debug"].print_tokens.reset_mock()
        result = manager.is_active_for_app(mock_app)
        assert result is True
        essential_modules["orca.debug"].print_tokens.assert_called_with(
            essential_modules["orca.debug"].LEVEL_INFO,
            ["SLEEP MODE MANAGER: Is active for", mock_app],
            True,
        )

    def test_setup_handlers(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager._setup_handlers method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        manager._setup_handlers()
        assert "toggle_sleep_mode" in manager._handlers
        expected_handler = essential_modules["input_event_handler"]
        assert manager._handlers["toggle_sleep_mode"] == expected_handler
        input_event = essential_modules["orca.input_event"]
        input_event.InputEventHandler.assert_called_with(
            manager.toggle_sleep_mode, "Toggle sleep mode for the current application"
        )

    def test_setup_bindings(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager._setup_bindings method."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        manager._setup_bindings()

        essential_modules["orca.keybindings"].KeyBinding.assert_called_with(
            "q",
            1,  # DEFAULT_MODIFIER_MASK
            15,  # SHIFT_ALT_CTRL_MODIFIER_MASK
            manager._handlers["toggle_sleep_mode"],
        )

        key_bindings_instance = essential_modules["key_bindings_instance"]
        key_bindings_instance.add.assert_called()

    def test_toggle_sleep_mode_no_script(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager.toggle_sleep_mode with no script."""

        self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        result = manager.toggle_sleep_mode(None)
        assert result is True

    def test_toggle_sleep_mode_script_no_app(self, test_context: OrcaTestContext) -> None:
        """Test SleepModeManager.toggle_sleep_mode with script but no app."""

        self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        mock_script = test_context.Mock()
        mock_script.app = None
        result = manager.toggle_sleep_mode(mock_script)
        assert result is True

    @pytest.mark.parametrize(
        "initially_active,notify_user,expected_message_contains",
        [
            pytest.param(False, True, "Sleep mode enabled for", id="enable_with_notification"),
            pytest.param(False, False, None, id="enable_without_notification"),
            pytest.param(True, True, "Sleep mode disabled for", id="disable_with_notification"),
            pytest.param(True, False, None, id="disable_without_notification"),
        ],
    )
    def test_toggle_sleep_mode_with_script_and_app(  # pylint: disable=too-many-branches
        self,
        test_context: OrcaTestContext,
        initially_active: bool,
        notify_user: bool,
        expected_message_contains: str | None,
    ) -> None:
        """Test SleepModeManager.toggle_sleep_mode with various scenarios."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.sleep_mode_manager import SleepModeManager

        manager = SleepModeManager()
        mock_script = test_context.Mock()
        mock_app = test_context.Mock()
        mock_script.app = mock_app
        mock_event = test_context.Mock()
        app_hash = hash(mock_app)

        if initially_active:
            manager._apps.append(app_hash)

        script_manager_instance = essential_modules["script_manager_instance"]

        if initially_active:
            new_script = test_context.Mock()
            script_manager_instance.get_script = test_context.Mock(return_value=new_script)
        else:
            sleep_script = test_context.Mock()
            script_manager_instance.get_or_create_sleep_mode_script = test_context.Mock(
                return_value=sleep_script
            )

        test_context.patch(
            "orca.sleep_mode_manager.script_manager.get_manager",
            return_value=script_manager_instance
        )

        result = manager.toggle_sleep_mode(mock_script, mock_event, notify_user=notify_user)
        assert result is True

        if initially_active:
            assert app_hash not in manager._apps
        else:
            assert app_hash in manager._apps

        if not initially_active:
            essential_modules["orca.braille"].clear.assert_called()

        if notify_user and expected_message_contains:
            if initially_active:
                new_script.present_message.assert_called_once()
                call_args = new_script.present_message.call_args[0][0]
            else:
                mock_script.present_message.assert_called_once()
                call_args = mock_script.present_message.call_args[0][0]
            assert expected_message_contains in call_args
        else:
            if initially_active:
                new_script.present_message.assert_not_called()
            else:
                mock_script.present_message.assert_not_called()

        if initially_active:
            script_manager_instance.get_script.assert_called_with(mock_app)
            script_manager_instance.set_active_script.assert_called_with(
                new_script, "Sleep mode toggled off"
            )
        else:
            script_manager_instance.get_or_create_sleep_mode_script.assert_called_with(mock_app)
            script_manager_instance.set_active_script.assert_called_with(
                sleep_script, "Sleep mode toggled on"
            )
