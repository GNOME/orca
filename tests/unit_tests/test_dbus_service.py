# Unit tests for dbus_service.py methods.
#
# Copyright 2025 Valve Corporation
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-lines

"""Unit tests for D-Bus functionality."""

from __future__ import annotations

import sys
import types
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


class _MockDBusError(Exception):
    def __init__(self, message="DBus error"):
        super().__init__(message)
        self.message = message


@pytest.mark.unit
class TestDBusService:
    """Test D-Bus service functionality."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for dbus_service dependencies."""

        external_modules = [
            "gi",
            "gi.repository",
            "dasbus",
            "dasbus.connection",
            "dasbus.error",
            "dasbus.loop",
            "dasbus.server.interface",
            "dasbus.server.publishable",
            "dasbus.typing",
        ]

        internal_modules = [
            "orca.debug",
            "orca.input_event",
            "orca.input_event_manager",
            "orca.orca_platform",
            "orca.script_manager",
            "orca.braille_presenter",
            "orca.presentation_manager",
        ]

        all_modules = external_modules + internal_modules
        essential_modules = test_context._setup_essential_modules(all_modules)

        class MockGLibVariant:
            """Mock GLib.Variant for D-Bus type handling."""

            def __init__(self, type_string: str, value):
                self._type_string = type_string
                self._value = value

            def get_type_string(self) -> str:
                """Return the GLib type string."""
                return self._type_string

            def unpack(self):
                """Unpack the variant value."""
                return self._value

        essential_modules["gi.repository"].GLib = test_context.Mock()
        essential_modules["gi.repository"].GLib.Variant = MockGLibVariant

        class MockPublishable:
            """Mock Publishable base class for inheritance."""

            def __init__(self, *args, **kwargs):
                pass

        essential_modules["dasbus.server.publishable"].Publishable = MockPublishable

        essential_modules["dasbus.error"].DBusError = _MockDBusError

        def mock_dbus_interface(_interface_name):
            def decorator(cls):
                return cls

            return decorator

        essential_modules["dasbus.server.interface"].dbus_interface = mock_dbus_interface

        essential_modules["orca.debug"].LEVEL_INFO = 800
        essential_modules["orca.debug"].println = test_context.Mock()

        essential_modules["orca.orca_platform"].version = "test-version"

        return essential_modules

    def _get_mock_dbus_error(self) -> type[Exception]:
        return _MockDBusError

    def test_command_decorator(self, test_context: OrcaTestContext) -> None:
        """Test command decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.command
        def test_function(script=None, event=None, notify_user=False) -> bool:  # pylint: disable=unused-argument
            """Test command function."""

            return True

        assert hasattr(test_function, "dbus_command_description")
        assert test_function.dbus_command_description == "Test command function."

    def test_command_decorator_without_docstring(self, test_context: OrcaTestContext) -> None:
        """Test command decorator without docstring."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.command
        def test_function_no_doc(script=None, event=None, notify_user=False) -> bool:  # pylint: disable=unused-argument
            return True

        assert hasattr(test_function_no_doc, "dbus_command_description")
        assert (
            test_function_no_doc.dbus_command_description == "D-Bus command: test_function_no_doc"
        )

    def test_parameterized_command_decorator(self, test_context: OrcaTestContext) -> None:
        """Test parameterized_command decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.parameterized_command
        def test_function(
            script=None,  # pylint: disable=unused-argument
            event=None,  # pylint: disable=unused-argument
            language="",  # pylint: disable=unused-argument
            variant="",  # pylint: disable=unused-argument
            notify_user=False,  # pylint: disable=unused-argument
        ) -> list[tuple[str, str, str]]:
            """Get voices for language."""

            return [("voice1", language, variant)]

        assert hasattr(test_function, "dbus_parameterized_command_description")
        assert test_function.dbus_parameterized_command_description == "Get voices for language."

    def test_getter_decorator(self, test_context: OrcaTestContext) -> None:
        """Test getter decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.getter
        def get_rate() -> int:
            """Returns the current speech rate."""

            return 50

        assert hasattr(get_rate, "dbus_getter_description")
        assert get_rate.dbus_getter_description == "Returns the current speech rate."

    def test_setter_decorator(self, test_context: OrcaTestContext) -> None:
        """Test setter decorator."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.setter
        def set_rate(_value) -> bool:
            """Sets the current speech rate."""

            return True

        assert hasattr(set_rate, "dbus_setter_description")
        assert set_rate.dbus_setter_description == "Sets the current speech rate."

    def test_multiple_decorators_on_module(self, test_context: OrcaTestContext) -> None:
        """Test multiple decorators on module."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class MockModule:
            """Mock module for testing multiple decorators."""

            @dbus_service.command
            def toggle_speech(self, notify_user=False) -> bool:  # pylint: disable=unused-argument
                """Toggle speech on/off."""

                return True

            @dbus_service.parameterized_command
            def get_voices_for_language(
                self,
                language="",  # pylint: disable=unused-argument
                variant="",  # pylint: disable=unused-argument
                notify_user=False,  # pylint: disable=unused-argument
            ) -> list:
                """Get voices for language."""

                return []

            @dbus_service.getter
            def get_rate(self) -> int:
                """Get speech rate."""

                return 50

            @dbus_service.setter
            def set_rate(self, _value) -> bool:
                """Set speech rate."""

                return True

        mock_module = MockModule()
        assert hasattr(mock_module.toggle_speech, "dbus_command_description")
        assert hasattr(
            mock_module.get_voices_for_language,
            "dbus_parameterized_command_description",
        )
        assert hasattr(mock_module.get_rate, "dbus_getter_description")
        assert hasattr(mock_module.set_rate, "dbus_setter_description")

    def test_decorated_functions_remain_callable(self, test_context: OrcaTestContext) -> None:
        """Test decorated functions remain callable."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.parameterized_command
        def test_command(param1="default", notify_user=False) -> str:
            """Test parameterized command."""

            return f"param1={param1}, notify_user={notify_user}"

        assert hasattr(test_command, "dbus_parameterized_command_description")
        result = test_command(param1="test_value", notify_user=True)
        assert "param1=test_value" in result
        assert "notify_user=True" in result

    def test_show_preferences_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ShowPreferences success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_script = test_context.Mock()
        mock_script.show_preferences_gui.return_value = None
        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = mock_script
        test_context.patch("orca.script_manager.get_manager", return_value=mock_manager)
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.ShowPreferences()
        assert result is True
        mock_script.show_preferences_gui.assert_called_once()

    def test_show_preferences_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ShowPreferences no active script."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_script = test_context.Mock()
        mock_script.show_preferences_gui.return_value = None
        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = None
        mock_manager.get_default_script.return_value = mock_script
        test_context.patch("orca.script_manager.get_manager", return_value=mock_manager)
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.ShowPreferences()
        assert result is True
        mock_script.show_preferences_gui.assert_called_once()

    def test_show_preferences_no_script(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.ShowPreferences no script."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = None
        mock_manager.get_default_script.return_value = None
        test_context.patch("orca.script_manager.get_manager", return_value=mock_manager)
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.ShowPreferences()
        assert result is False

    def test_present_message_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.PresentMessage success."""

        essential_modules = self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_script = test_context.Mock()
        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = mock_script
        test_context.patch("orca.script_manager.get_manager", return_value=mock_manager)
        service = dbus_service.OrcaDBusServiceInterface()
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        result = service.PresentMessage("Test message")
        assert result is True
        pres_manager.present_message.assert_called_once_with("Test message")

    def test_present_message_no_script(self, test_context: OrcaTestContext) -> None:
        """Test OrcaDBusServiceInterface.PresentMessage works without active script."""

        essential_modules = self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_manager = test_context.Mock()
        mock_manager.get_active_script.return_value = None
        mock_manager.get_default_script.return_value = None
        test_context.patch("orca.script_manager.get_manager", return_value=mock_manager)
        pres_manager = essential_modules["orca.presentation_manager"].get_manager()
        pres_manager.present_message.reset_mock()
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.PresentMessage("Test message")
        # presentation_manager works without a script now
        assert result is True
        pres_manager.present_message.assert_called_once_with("Test message")

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "with_revision",
                "version": "2.0.0",
                "revision": "abcd1234",
                "expected_result": "2.0.0 (rev abcd1234)",
            },
            {"id": "no_revision", "version": "2.0.0", "revision": "", "expected_result": "2.0.0"},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_version_scenarios(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test OrcaDBusServiceInterface.GetVersion with and without revision."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        version = case["version"]
        revision = case["revision"]
        expected_result = case["expected_result"]

        test_context.patch_object(dbus_service.orca_platform, "version", new=version)
        test_context.patch_object(dbus_service.orca_platform, "revision", new=revision)
        service = dbus_service.OrcaDBusServiceInterface()
        result = service.GetVersion()
        assert result == expected_result

    def test_orca_remote_controller_constructor(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController constructor."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        assert controller._dbus_service_interface is None
        assert controller._is_running is False
        assert controller._bus is None
        assert not controller._pending_registrations

    def test_start_already_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start already running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        result = controller.start()
        assert result is True

    def test_start_bus_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start bus error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_dbus_error = self._get_mock_dbus_error()

        def mock_session_bus() -> None:
            raise mock_dbus_error("Bus connection failed")

        test_context.patch_object(dbus_service, "SessionMessageBus", new=mock_session_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        assert controller._bus is None
        assert controller._is_running is False

    def test_start_publish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start publish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_dbus_error = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        mock_bus.publish_object.side_effect = mock_dbus_error("Publish failed")
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        assert controller._bus is None
        assert controller._dbus_service_interface is None
        assert controller._is_running is False

    def test_start_publish_error_with_cleanup(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start publish error with cleanup."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_dbus_error = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        mock_bus.register_service.side_effect = mock_dbus_error("Register failed")
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        mock_bus.unpublish_object.assert_called_once()

    def test_start_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.start success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)
        controller = dbus_service.OrcaRemoteController()
        mock_process = test_context.Mock()
        mock_print = test_context.Mock()
        test_context.patch_object(controller, "_process_pending_registrations", new=mock_process)
        test_context.patch_object(controller, "_print_registration_summary", new=mock_print)
        result = controller.start()
        assert result is True
        assert controller._is_running is True
        assert controller._bus is mock_bus
        assert controller._dbus_service_interface is not None
        mock_bus.publish_object.assert_called_once()
        mock_bus.register_service.assert_called_once()
        mock_process.assert_called_once()
        mock_print.assert_called_once()

    def test_shutdown_not_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown not running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller.shutdown()

    def test_shutdown_success(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown success."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_bus = test_context.Mock()
        mock_service = test_context.Mock()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._bus = mock_bus
        controller._dbus_service_interface = mock_service
        controller._pending_registrations = {"test": "module"}
        controller.shutdown()
        assert controller._is_running is False
        assert controller._bus is None
        assert controller._dbus_service_interface is None
        assert not controller._pending_registrations
        mock_bus.unpublish_object.assert_called_once()
        mock_bus.unregister_service.assert_called_once()
        mock_bus.disconnect.assert_called_once()

    def test_shutdown_unpublish_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown unpublish error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_dbus_error = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unpublish_object.side_effect = mock_dbus_error("Unpublish failed")
        mock_service = test_context.Mock()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._bus = mock_bus
        controller._dbus_service_interface = mock_service

        controller.shutdown()
        assert controller._is_running is False
        mock_bus.unregister_service.assert_called_once()
        mock_bus.disconnect.assert_called_once()

    def test_shutdown_unregister_error(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.shutdown unregister error."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_dbus_error = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.unregister_service.side_effect = mock_dbus_error("Unregister failed")
        mock_service = test_context.Mock()
        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._bus = mock_bus
        controller._dbus_service_interface = mock_service

        controller.shutdown()
        assert controller._is_running is False
        mock_bus.disconnect.assert_called_once()

    def test_register_decorated_module_not_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.register_decorated_module not running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        mock_module = test_context.Mock()
        controller.register_decorated_module("TestModule", mock_module)
        assert "TestModule" in controller._pending_registrations
        assert controller._pending_registrations["TestModule"] is mock_module

    def test_register_decorated_module_running(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController.register_decorated_module running."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._is_running = True
        controller._dbus_service_interface = test_context.Mock()
        controller._bus = test_context.Mock()
        mock_publish = test_context.Mock()
        test_context.patch_object(controller, "_publish_module", new=mock_publish)
        mock_module = test_context.Mock()
        controller.register_decorated_module("TestModule", mock_module)
        mock_publish.assert_called_once_with("TestModule", mock_module)

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "pending",
                "is_running": False,
                "has_pending": True,
                "unpublish_returns": None,
                "expected_result": True,
                "expects_unpublish_call": False,
            },
            {
                "id": "not_registered",
                "is_running": False,
                "has_pending": False,
                "unpublish_returns": None,
                "expected_result": False,
                "expects_unpublish_call": False,
            },
            {
                "id": "running",
                "is_running": True,
                "has_pending": False,
                "unpublish_returns": True,
                "expected_result": True,
                "expects_unpublish_call": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_deregister_module_commands_scenarios(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test OrcaRemoteController.deregister_module_commands with various scenarios."""
        self._setup_dependencies(test_context)
        from orca import dbus_service

        is_running = case["is_running"]
        has_pending = case["has_pending"]
        unpublish_returns = case["unpublish_returns"]
        expected_result = case["expected_result"]
        expects_unpublish_call = case["expects_unpublish_call"]

        controller = dbus_service.OrcaRemoteController()

        if has_pending:
            controller._pending_registrations["TestModule"] = test_context.Mock()

        mock_unpublish = test_context.Mock(return_value=unpublish_returns)
        test_context.patch_object(controller, "_unpublish_module", new=mock_unpublish)

        if is_running:
            controller._is_running = True
            controller._dbus_service_interface = test_context.Mock()
            controller._bus = test_context.Mock()
            controller._registered["TestModule"] = test_context.Mock()

        result = controller.deregister_module_commands("TestModule")
        assert result is expected_result

        if has_pending:
            assert "TestModule" not in controller._pending_registrations

        if expects_unpublish_call:
            mock_unpublish.assert_called_once_with("TestModule")

    def test_process_pending_registrations_empty(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController._process_pending_registrations empty."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        controller._process_pending_registrations()

    def test_process_pending_registrations_with_modules(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test OrcaRemoteController._process_pending_registrations with modules."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        mock_publish = test_context.Mock()
        test_context.patch_object(controller, "_publish_module", new=mock_publish)
        mock_module1 = test_context.Mock()
        mock_module2 = test_context.Mock()
        controller._pending_registrations = {"Module1": mock_module1, "Module2": mock_module2}
        controller._process_pending_registrations()
        assert not controller._pending_registrations
        assert mock_publish.call_count == 2
        mock_publish.assert_any_call("Module1", mock_module1)
        mock_publish.assert_any_call("Module2", mock_module2)

    def test_print_registration_summary(self, test_context: OrcaTestContext) -> None:
        """Test OrcaRemoteController._print_registration_summary."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()
        mock_registration = test_context.Mock()
        mock_registration.get_commands.return_value = {"DoX": object(), "DoY": object()}
        mock_registration.get_parameterized_commands.return_value = {"DoZ": object()}
        mock_registration.get_getters.return_value = {"Rate": object()}
        mock_registration.get_setters.return_value = {"Rate": object()}
        controller._registered = {"FakeManager": mock_registration}
        # Should not raise; the assertions confirm the expected lookups happened.
        controller._print_registration_summary()
        mock_registration.get_commands.assert_called()
        mock_registration.get_parameterized_commands.assert_called()
        mock_registration.get_getters.assert_called()
        mock_registration.get_setters.assert_called()

    def test_get_remote_controller(self, test_context: OrcaTestContext) -> None:
        """Test get_remote_controller function."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        controller = dbus_service.get_remote_controller()
        assert isinstance(controller, dbus_service.OrcaRemoteController)

    def test_start_unpublish_object_error_during_cleanup(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test OrcaRemoteController.start unpublish object error during cleanup."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        mock_dbus_error = self._get_mock_dbus_error()
        mock_bus = test_context.Mock()
        mock_bus.connection.get_unique_name.return_value = "test_name"
        mock_bus.register_service.side_effect = mock_dbus_error("Register failed")
        mock_bus.unpublish_object.side_effect = mock_dbus_error("Unpublish failed")
        test_context.patch_object(dbus_service, "SessionMessageBus", return_value=mock_bus)

        controller = dbus_service.OrcaRemoteController()
        result = controller.start()
        assert result is False
        assert controller._bus is None
        assert controller._dbus_service_interface is None

    def test_module_registration_classify_recognizes_each_kind(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that _classify_method returns each _Kind and description."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        @dbus_service.command
        def cmd():
            """A command."""

        @dbus_service.parameterized_command
        def pcmd():
            """A parameterized command."""

        @dbus_service.getter
        def get_thing():
            """A getter."""

        @dbus_service.setter
        def set_thing(_value):
            """A setter."""

        classify = dbus_service._ModuleRegistration._classify_method
        assert classify(cmd) == (dbus_service._Kind.COMMAND, "A command.")
        assert classify(pcmd) == (dbus_service._Kind.PARAMETERIZED, "A parameterized command.")
        assert classify(get_thing) == (dbus_service._Kind.GETTER, "A getter.")
        assert classify(set_thing) == (dbus_service._Kind.SETTER, "A setter.")

    def test_module_registration_classify_undecorated_returns_none(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that _classify_method returns (None, '') for undecorated methods."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        def plain():
            return None

        assert dbus_service._ModuleRegistration._classify_method(plain) == (None, "")

    @pytest.mark.parametrize(
        ("snake", "kind_attr", "expected"),
        [
            ("toggle_speech", "COMMAND", "ToggleSpeech"),
            ("get_voices_for_language", "PARAMETERIZED", "GetVoicesForLanguage"),
            ("get_rate", "GETTER", "Rate"),
            ("set_rate", "SETTER", "Rate"),
            ("rate", "GETTER", "Rate"),
        ],
    )
    def test_module_registration_dbus_name_for(
        self, test_context: OrcaTestContext, snake: str, kind_attr: str, expected: str
    ) -> None:
        """Test that _dbus_name_for camelizes and strips get_/set_ for property kinds only."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        kind = getattr(dbus_service._Kind, kind_attr)
        assert dbus_service._ModuleRegistration._dbus_name_for(snake, kind) == expected

    def test_module_registration_from_module_instance_groups_members(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test that from_module_instance walks an instance and groups members by kind."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class FakeManager:
            """Fake manager exposing one of each decorator kind."""

            @dbus_service.command
            def toggle_speech(self) -> bool:
                """Toggles speech."""

                return True

            @dbus_service.parameterized_command
            def get_voices_for_language(self, _language) -> list:
                """Returns voices."""

                return []

            @dbus_service.getter
            def get_rate(self) -> float:
                """Returns rate."""

                return 1.0

            @dbus_service.setter
            def set_rate(self, _value) -> bool:
                """Sets rate."""

                return True

            def undecorated(self) -> None:
                """Should be ignored."""

        registration = dbus_service._ModuleRegistration.from_module_instance(
            "FakeManager", FakeManager()
        )
        assert set(registration.get_commands()) == {"ToggleSpeech"}
        assert set(registration.get_parameterized_commands()) == {"GetVoicesForLanguage"}
        assert set(registration.get_getters()) == {"Rate"}
        assert set(registration.get_setters()) == {"Rate"}
        assert registration.get_module_name() == "FakeManager"
        assert registration.total_member_count() == 4
        assert not registration.is_empty()

    def test_module_registration_setter_description_preferred_over_getter(
        self, test_context: OrcaTestContext
    ) -> None:
        """When a property has both, the setter description wins (it usually documents inputs)."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class FakeManager:
            """Fake manager with paired getter/setter."""

            @dbus_service.getter
            def get_rate(self) -> float:
                """Returns rate."""

                return 1.0

            @dbus_service.setter
            def set_rate(self, _value) -> bool:
                """Sets rate."""

                return True

        registration = dbus_service._ModuleRegistration.from_module_instance(
            "FakeManager", FakeManager()
        )
        assert registration.get_descriptions()["Rate"] == "Sets rate."

    def test_module_registration_find_helpers(self, test_context: OrcaTestContext) -> None:
        """Test find_command/find_getter/find_setter return registered methods or None."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        class FakeManager:
            """Fake manager."""

            @dbus_service.command
            def toggle_speech(self) -> bool:
                """Toggles speech."""

                return True

            @dbus_service.parameterized_command
            def query(self, _topic) -> bool:
                """Queries."""

                return True

            @dbus_service.getter
            def get_rate(self) -> float:
                """Returns rate."""

                return 1.0

            @dbus_service.setter
            def set_rate(self, _value) -> bool:
                """Sets rate."""

                return True

        instance = FakeManager()
        registration = dbus_service._ModuleRegistration.from_module_instance(
            "FakeManager", instance
        )
        # Bound methods are fresh objects each access, so compare with == not is.
        assert registration.find_command("ToggleSpeech") == instance.toggle_speech
        assert registration.find_command("Query") == instance.query
        assert registration.find_command("Nope") is None
        assert registration.find_getter("Rate") == instance.get_rate
        assert registration.find_setter("Rate") == instance.set_rate
        assert registration.find_getter("Nope") is None
        assert registration.find_setter("Nope") is None

    def test_module_registration_empty(self, test_context: OrcaTestContext) -> None:
        """A new registration is empty until members are added."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        registration = dbus_service._ModuleRegistration("Empty")
        assert registration.is_empty()
        assert registration.total_member_count() == 0

    def test_module_registration_object_path_and_dbus_object(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_object_path/set_dbus_object round-trip cleanly."""

        self._setup_dependencies(test_context)
        from orca import dbus_service

        registration = dbus_service._ModuleRegistration("FakeManager")
        assert registration.get_object_path() == ""
        assert registration.get_dbus_object() is None

        registration.set_object_path("/org/gnome/Orca1/Service/FakeManager")
        sentinel = object()
        registration.set_dbus_object(sentinel)
        assert registration.get_object_path() == "/org/gnome/Orca1/Service/FakeManager"
        assert registration.get_dbus_object() is sentinel


def _stub_orca_internals(test_context: OrcaTestContext) -> dict[str, object]:
    """Installs orca-internal stubs while leaving dasbus and gi real."""

    # _InterfaceBuilder relies on real dasbus introspection to build interface classes
    # from type annotations, so dasbus and gi must NOT be mocked here. Only orca.*
    # modules that the synthesized wrappers lazily import need stubbing.
    class _RemoteControllerEvent:
        pass

    class _StubInputEventManager:
        def __init__(self) -> None:
            self.last_event: object | None = None

        def process_remote_controller_event(self, event: object) -> None:
            self.last_event = event

    class _StubScriptManager:
        def get_active_script(self) -> object:
            return "active-script"

        def get_default_script(self) -> object:
            return "default-script"

    iem_instance = _StubInputEventManager()
    sm_instance = _StubScriptManager()

    platform_mod = types.ModuleType("orca.orca_platform")
    platform_mod.version = "test-version"
    platform_mod.revision = ""

    debug_mod = types.ModuleType("orca.debug")
    debug_mod.LEVEL_INFO = 800
    debug_mod.LEVEL_WARNING = 900
    debug_mod.LEVEL_SEVERE = 1000
    debug_mod.print_message = lambda *_args, **_kwargs: None
    debug_mod.print_tokens = lambda *_args, **_kwargs: None

    input_event_mod = types.ModuleType("orca.input_event")
    input_event_mod.RemoteControllerEvent = _RemoteControllerEvent

    iem_mod = types.ModuleType("orca.input_event_manager")
    iem_mod.get_manager = lambda: iem_instance

    sm_mod = types.ModuleType("orca.script_manager")
    sm_mod.get_manager = lambda: sm_instance

    stubs = {
        "orca.orca_platform": platform_mod,
        "orca.debug": debug_mod,
        "orca.input_event": input_event_mod,
        "orca.input_event_manager": iem_mod,
        "orca.script_manager": sm_mod,
    }
    test_context.patch_modules(stubs)

    sys.modules.pop("orca.dbus_service", None)
    return stubs


@pytest.mark.unit
class TestInterfaceBuilder:
    """Tests for _InterfaceBuilder: builds D-Bus interface classes from a registration."""

    def _build(self, ds):
        """Builds the FakeManager interface class used by these tests."""

        class FakeManager:
            """Fake manager exposing one of each decorator kind."""

            @ds.command
            def toggle_speech(self, script=None, event=None, notify_user=True) -> bool:
                """Toggles speech."""
                return True

            @ds.parameterized_command
            def get_voices_for_language(
                self,
                language: str,
                variant: str = "",
                script=None,
                event=None,
                notify_user: bool = False,
            ) -> list[tuple[str, str, str]]:
                """Returns voices."""
                return [("v", language, variant)]

            @ds.getter
            def get_rate(self) -> float:
                """Returns rate."""
                return 1.0

            @ds.setter
            def set_rate(self, value: float) -> bool:
                """Sets rate."""
                return True

            @ds.setter
            def set_locking_keys_presented(self, value: bool | None) -> bool:
                """Sets locking-keys presentation."""
                return True

        registration = ds._ModuleRegistration.from_module_instance("FakeManager", FakeManager())
        return ds._InterfaceBuilder.build(registration)

    def _interface_xml(self, cls):
        """Returns the <interface> element with our DBus name."""

        root = ET.fromstring(cls.__dbus_xml__)
        for iface in root.findall("interface"):
            if iface.get("name") == "org.gnome.Orca1.FakeManager":
                return iface
        return None

    def test_simple_command_method_signature(self, test_context: OrcaTestContext) -> None:
        """A simple @command becomes a method taking only notify_user, returning bool."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        cls = self._build(dbus_service)
        iface = self._interface_xml(cls)
        method = next(m for m in iface.findall("method") if m.get("name") == "ToggleSpeech")
        in_args = [a for a in method.findall("arg") if a.get("direction") == "in"]
        out_args = [a for a in method.findall("arg") if a.get("direction") == "out"]
        assert [a.get("name") for a in in_args] == ["notify_user"]
        assert [a.get("type") for a in in_args] == ["b"]
        assert [a.get("type") for a in out_args] == ["b"]

    def test_parameterized_command_preserves_signature(self, test_context: OrcaTestContext) -> None:
        """Parameterized commands carry user parameters plus a trailing notify_user."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        cls = self._build(dbus_service)
        iface = self._interface_xml(cls)
        method = next(m for m in iface.findall("method") if m.get("name") == "GetVoicesForLanguage")
        in_args = [
            (a.get("name"), a.get("type"))
            for a in method.findall("arg")
            if a.get("direction") == "in"
        ]
        out_args = [a.get("type") for a in method.findall("arg") if a.get("direction") == "out"]
        assert in_args == [("language", "s"), ("variant", "s"), ("notify_user", "b")]
        assert out_args == ["a(sss)"]

    def test_property_access_modes(self, test_context: OrcaTestContext) -> None:
        """A getter+setter pair is read/write; a setter alone is write-only."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        cls = self._build(dbus_service)
        iface = self._interface_xml(cls)
        properties = {p.get("name"): p for p in iface.findall("property")}
        assert properties["Rate"].get("type") == "d"
        assert properties["Rate"].get("access") == "readwrite"
        assert properties["LockingKeysPresented"].get("type") == "b"
        assert properties["LockingKeysPresented"].get("access") == "write"

    def test_uint32_annotation_produces_unsigned_signature(
        self, test_context: OrcaTestContext
    ) -> None:
        """A UInt32-typed property is exposed with the unsigned-int D-Bus signature 'u'."""

        _stub_orca_internals(test_context)
        from orca import dbus_service
        from orca.dbus_service import UInt32

        class FakeManager:
            @dbus_service.getter
            def get_volume(self) -> UInt32:
                """Returns volume."""
                return UInt32(50)

            @dbus_service.setter
            def set_volume(self, value: UInt32) -> bool:
                """Sets volume."""
                return True

        registration = dbus_service._ModuleRegistration.from_module_instance(
            "FakeManager", FakeManager()
        )
        cls = dbus_service._InterfaceBuilder.build(registration)
        root = ET.fromstring(cls.__dbus_xml__)
        iface = next(
            i for i in root.findall("interface") if i.get("name") == "org.gnome.Orca1.FakeManager"
        )
        volume = next(p for p in iface.findall("property") if p.get("name") == "Volume")
        assert volume.get("type") == "u"
        assert volume.get("access") == "readwrite"

    def test_user_params_resolved_when_reserved_param_unresolvable(
        self, test_context: OrcaTestContext
    ) -> None:
        """A TYPE_CHECKING-only annotation on a reserved param must not poison user params.

        Real Orca modules type script as default.Script (a TYPE_CHECKING import).
        Combined with from __future__ import annotations, that turns every annotation
        into a string. Per-annotation parsing must recover the user-facing parameter and
        return types that D-Bus actually marshals over the wire.
        """

        _stub_orca_internals(test_context)
        from orca import dbus_service

        class TypeCheckingOnly:
            """Mirrors a real Orca presenter that types script as a TYPE_CHECKING-only ref."""

            @dbus_service.parameterized_command
            def get_voices_for_language(
                self,
                language: str,
                variant: str = "",
                script: ThisIsNotImportedAtRuntime = None,  # type: ignore[name-defined]  # noqa: F821
                event: NeitherIsThis = None,  # type: ignore[name-defined]  # noqa: F821
                notify_user: bool = False,
            ) -> list[tuple[str, str, str]]:
                """Returns voices."""
                return [("v", language, variant)]

        registration = dbus_service._ModuleRegistration.from_module_instance(
            "FakeManager", TypeCheckingOnly()
        )
        cls = dbus_service._InterfaceBuilder.build(registration)

        root = ET.fromstring(cls.__dbus_xml__)
        iface = next(
            i for i in root.findall("interface") if i.get("name") == "org.gnome.Orca1.FakeManager"
        )
        method = next(m for m in iface.findall("method") if m.get("name") == "GetVoicesForLanguage")
        in_args = [
            (a.get("name"), a.get("type"))
            for a in method.findall("arg")
            if a.get("direction") == "in"
        ]
        out_args = [a.get("type") for a in method.findall("arg") if a.get("direction") == "out"]
        assert in_args == [("language", "s"), ("variant", "s"), ("notify_user", "b")]
        assert out_args == ["a(sss)"]

    def test_command_wrapper_synthesizes_event_and_script(
        self, test_context: OrcaTestContext
    ) -> None:
        """Calling the synthesized D-Bus method routes through the @command wrapper."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        calls: list[tuple] = []

        class Tracker:
            """Records calls so the test can verify what the wrapper passed through."""

            @dbus_service.command
            def toggle_speech(self, script=None, event=None, notify_user=True) -> bool:
                """Toggles."""
                calls.append(("cmd", script, type(event).__name__, notify_user))
                return True

        registration = dbus_service._ModuleRegistration.from_module_instance("Tracker", Tracker())
        cls = dbus_service._InterfaceBuilder.build(registration)
        instance = cls()

        result = instance.ToggleSpeech(False)
        assert result is True
        kind, script, event_type, notify = calls[-1]
        assert kind == "cmd"
        assert script == "active-script"
        assert event_type == "_RemoteControllerEvent"
        assert notify is False

    def test_property_descriptors_route_to_underlying_methods(
        self, test_context: OrcaTestContext
    ) -> None:
        """Reading and writing the synthesized property invokes the underlying methods."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        calls: list[tuple] = []

        class Tracker:
            """Records setter calls so the test can verify routing."""

            @dbus_service.getter
            def get_rate(self) -> float:
                """Rate."""
                return 7.5

            @dbus_service.setter
            def set_rate(self, value: float) -> bool:
                """Set rate."""
                calls.append(("set_rate", value))
                return True

        registration = dbus_service._ModuleRegistration.from_module_instance("Tracker", Tracker())
        cls = dbus_service._InterfaceBuilder.build(registration)
        instance = cls()

        assert instance.Rate == 7.5
        instance.Rate = 11.0
        assert calls[-1] == ("set_rate", 11.0)


@pytest.mark.unit
class TestRemoteControllerInternalAPIs:
    """Internal-call APIs that extension code uses to bypass the bus."""

    def _registered_controller(self, dbus_service, calls):
        """Returns a controller with one FakeManager registered, ready for in-process use."""

        class FakeManager:
            @dbus_service.command
            def toggle_speech(self, script=None, event=None, notify_user=True) -> bool:
                """Toggles."""
                calls.append(("cmd", notify_user))
                return True

            @dbus_service.getter
            def get_rate(self) -> float:
                """Rate."""
                return 3.14

            @dbus_service.setter
            def set_rate(self, value: float) -> bool:
                """Set rate."""
                calls.append(("set_rate", value))
                return True

        registration = dbus_service._ModuleRegistration.from_module_instance(
            "FakeManager", FakeManager()
        )
        controller = dbus_service.OrcaRemoteController()
        controller._registered["FakeManager"] = registration
        return controller

    def test_execute_command_internal_routes_to_method(self, test_context: OrcaTestContext) -> None:
        """execute_command_internal runs the command and returns its bool result."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        calls: list[tuple] = []
        controller = self._registered_controller(dbus_service, calls)

        assert controller.execute_command_internal("FakeManager", "ToggleSpeech", False) is True
        assert calls[-1] == ("cmd", False)

    def test_execute_command_internal_unknown_returns_false(
        self, test_context: OrcaTestContext
    ) -> None:
        """An unknown module or command yields False without raising."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        controller = self._registered_controller(dbus_service, [])
        assert controller.execute_command_internal("NoSuch", "Foo") is False
        assert controller.execute_command_internal("FakeManager", "NoSuch") is False

    def test_get_and_set_value_internal_round_trip(self, test_context: OrcaTestContext) -> None:
        """get_value_internal reads via the getter; set_value_internal writes via setter."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        calls: list[tuple] = []
        controller = self._registered_controller(dbus_service, calls)

        assert controller.get_value_internal("FakeManager", "Rate") == 3.14
        assert controller.set_value_internal("FakeManager", "Rate", 9.0) is True
        assert calls[-1] == ("set_rate", 9.0)

    def test_unknown_property_returns_safe_default(self, test_context: OrcaTestContext) -> None:
        """Unknown getters return None; unknown setters return False."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        controller = self._registered_controller(dbus_service, [])
        assert controller.get_value_internal("FakeManager", "Bogus") is None
        assert controller.set_value_internal("FakeManager", "Bogus", 1) is False


@pytest.mark.unit
class TestRemoteControllerLifecycle:
    """Controller queues registrations until the bus is up."""

    def test_pending_registrations_replay_on_start(self, test_context: OrcaTestContext) -> None:
        """A module registered before start() is published when the service comes up."""

        _stub_orca_internals(test_context)
        from orca import dbus_service

        controller = dbus_service.OrcaRemoteController()

        class FakeManager:
            @dbus_service.command
            def toggle_speech(self, script=None, event=None, notify_user=True) -> bool:
                """Toggles."""
                return True

        instance = FakeManager()
        controller.register_decorated_module("FakeManager", instance)
        assert "FakeManager" in controller._pending_registrations

        published: list[tuple[str, object]] = []
        controller._is_running = True
        controller._bus = types.SimpleNamespace(
            publish_object=lambda path, obj: published.append((path, obj)),
            unpublish_object=lambda path: None,
        )
        controller._process_pending_registrations()

        assert "FakeManager" in controller._registered
        assert not controller._pending_registrations
        assert published, "module should have been published once the bus came up"
        assert published[0][0].endswith("/FakeManager")
