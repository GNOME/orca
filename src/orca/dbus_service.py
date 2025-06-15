# Orca
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

"""Provides a D-Bus interface for remotely controlling Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2025 Valve Corporation."
__license__   = "LGPL"

from typing import Callable
from dasbus.connection import SessionMessageBus
from dasbus.server.interface import dbus_interface
from dasbus.server.publishable import Publishable
from dasbus.loop import EventLoop
from dasbus.error import DBusError

from . import debug
from . import input_event
from . import script_manager

def command(func):
    """Decorator to mark a method as a D-Bus command using its docstring.

    Usage:
        @command
        def toggle_speech(self, script=None, event=None):
            '''Toggles speech on and off.'''
            # method implementation
    """
    description = func.__doc__ or f"D-Bus command: {func.__name__}"
    func.dbus_command_description = description
    return func

class InputEventHandlerInfo:
    """Stores processed information about an input event handler for D-Bus exposure."""

    def __init__(self, python_function_name: str, description: str, action: Callable[..., bool]):
        self.python_function_name: str = python_function_name
        self.description: str = description
        self.action: Callable[..., bool] = action

@dbus_interface("org.gnome.Orca.Module")
class OrcaModuleDBusInterface(Publishable):
    """A D-Bus interface representing a specific Orca module (e.g., a manager)."""

    def __init__(self,
                 module_name: str,
                 handlers_info: list[InputEventHandlerInfo]):
        super().__init__()
        self._module_name = module_name
        self._commands: dict[str, InputEventHandlerInfo] = {}

        for info in handlers_info:
            camel_case_name = self._to_camel_case(info.python_function_name)
            self._commands[camel_case_name] = info

        msg = (
            f"DBUS SERVICE: OrcaModuleDBusInterface for {module_name} initialized "
            f"with {len(self._commands)} commands."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def for_publication(self):
        """Returns the D-Bus interface XML for publication."""

        return self.__dbus_xml__ # pylint: disable=no-member

    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        parts = snake_str.split("_")
        return "".join(word.capitalize() if word else "" for word in parts)

    def ListCommands(self) -> list[tuple[str, str]]: # pylint: disable=invalid-name
        """Returns a list of (command_name, description) for this module."""

        command_list = []
        for camel_case_name, info in self._commands.items():
            command_list.append((camel_case_name, info.description))
        return command_list

    def ExecuteCommand(self, command_name: str, notify_user: bool) -> bool: # pylint: disable=invalid-name
        """Executes the named command and returns True if the command succeeded."""

        if command_name not in self._commands:
            msg = f"DBUS SERVICE: Unknown command '{command_name}' for '{self._module_name}'."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        handler_info = self._commands[command_name]
        result = handler_info.action(notify_user)
        msg = (
            f"DBUS SERVICE: '{command_name}' in '{self._module_name}' executed. "
            f"Result: {result}, notify_user: {notify_user}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

@dbus_interface("org.gnome.Orca.Service")
class OrcaDBusServiceInterface(Publishable):
    """Internal D-Bus service object that handles D-Bus specifics."""

    def __init__(self) -> None:
        super().__init__()
        self._registered_modules: set[str] = set()
        msg = "DBUS SERVICE: OrcaDBusServiceInterface initialized."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def for_publication(self):
        """Returns the D-Bus interface XML for publication."""

        return self.__dbus_xml__  # pylint: disable=no-member

    def add_module_interface(
        self,
        module_name: str,
        handlers_info: list[InputEventHandlerInfo],
        bus: SessionMessageBus,
        object_path_base: str
    ) -> None:
        """Creates and prepares a D-Bus interface for an Orca module."""

        object_path = f"{object_path_base}/{module_name}"
        if module_name in self._registered_modules:
            msg = f"DBUS SERVICE: Interface {module_name} already registered. Replacing."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            try:
                bus.unpublish_object(object_path)
            except DBusError as e:
                msg = f"DBUS SERVICE: Error unpublishing old interface for {module_name}: {e}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            self._registered_modules.discard(module_name)
        try:
            module_iface = OrcaModuleDBusInterface(module_name, handlers_info)
            bus.publish_object(object_path, module_iface)
            self._registered_modules.add(module_name)
            msg = f"DBUS SERVICE: Successfully published {module_name} at {object_path}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        except DBusError as e:
            msg = (
                f"DBUS SERVICE: Failed to create or publish D-Bus interface for "
                f"module {module_name} at {object_path}: {e}"
            )
            debug.print_message(debug.LEVEL_SEVERE, msg, True)

    def remove_module_interface(
        self,
        module_name: str,
        bus: SessionMessageBus,
        object_path_base: str
    ) -> bool:
        """Removes and unpublishes a D-Bus interface for an Orca module."""

        if module_name not in self._registered_modules:
            msg = f"DBUS SERVICE: Module {module_name} is not registered."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        object_path = f"{object_path_base}/{module_name}"
        try:
            bus.unpublish_object(object_path)
            self._registered_modules.discard(module_name)
            msg = f"DBUS SERVICE: Successfully removed {module_name} from {object_path}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        except DBusError as e:
            msg = f"DBUS SERVICE: Error removing interface for {module_name}: {e}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

    def ListModules(self) -> list[str]: # pylint: disable=invalid-name
        """Returns a list of registered module names."""

        return list(self._registered_modules)

    def ListCommands(self) -> list[tuple[str, str]]: # pylint: disable=invalid-name
        """Returns available commands on the main service interface."""

        commands = []
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name[0].isupper():
                attr = getattr(self, attr_name)
                if callable(attr) and hasattr(attr, '__doc__'):
                    description = (attr.__doc__.strip() if attr.__doc__
                                 else f"Service command: {attr_name}")
                    commands.append((attr_name, description))

        return sorted(commands)

    def PresentMessage(self, message: str) -> bool: # pylint: disable=invalid-name
        """Presents message to the user."""

        msg = f"DBUS SERVICE: PresentMessage called with: '{message}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        manager = script_manager.get_manager()
        script = manager.get_active_script() or manager.get_default_script()
        if script is None:
            msg = "DBUS SERVICE: No script available"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        script.presentMessage(message)
        return True

    def shutdown_service(self, bus: SessionMessageBus, object_path_base: str) -> None:
        """Releases D-Bus resources held by this service and its modules."""

        msg = "DBUS SERVICE: Releasing D-Bus resources for service."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for module_name in list(self._registered_modules):
            module_object_path = f"{object_path_base}/{module_name}"
            msg = (
                f"DBUS SERVICE: Shutting down and unpublishing module {module_name} "
                f"from main service."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            try:
                bus.unpublish_object(module_object_path)
            except DBusError as e:
                msg = f"DBUS SERVICE: Error unpublishing interface for {module_name}: {e}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
        self._registered_modules.clear()

class OrcaRemoteController:
    """Manages Orca's D-Bus service for remote control."""

    SERVICE_NAME = "org.gnome.Orca.Service"
    OBJECT_PATH = "/org/gnome/Orca/Service"

    def __init__(self) -> None:
        self._dbus_service_interface: OrcaDBusServiceInterface | None = None
        self._is_running: bool = False
        self._bus: SessionMessageBus | None = None
        self._event_loop: EventLoop | None = None
        self._pending_registrations: dict[str, object] = {}

    def start(self) -> bool:
        """Starts the D-Bus service."""

        if self._is_running:
            msg = "REMOTE CONTROLLER: Start called but service is already running."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "REMOTE CONTROLLER: Attempting to start D-Bus service."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        try:
            self._bus = SessionMessageBus()
            msg = (
                f"REMOTE CONTROLLER: SessionMessageBus acquired: "
                f"{self._bus.connection.get_unique_name()}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
        except DBusError as e:
            self._bus = None
            msg = f"REMOTE CONTROLLER: Failed to acquire D-Bus session bus: {e}"
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            return False

        self._dbus_service_interface = OrcaDBusServiceInterface()
        try:
            self._bus.publish_object(self.OBJECT_PATH, self._dbus_service_interface)
            self._bus.register_service(self.SERVICE_NAME)
        except DBusError as e:
            msg = f"REMOTE CONTROLLER: Failed to publish service or request name: {e}"
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            if self._dbus_service_interface and self._bus:
                try:
                    self._bus.unpublish_object(self.OBJECT_PATH)
                except DBusError:
                    pass
            self._dbus_service_interface = None
            self._bus = None
            return False

        self._is_running = True
        msg = (
            f"REMOTE CONTROLLER: Service started name={self.SERVICE_NAME} "
            f"path={self.OBJECT_PATH}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._process_pending_registrations()
        return True

    def _process_pending_registrations(self) -> None:
        """Processes any module registrations that were queued before the service was ready."""

        if not self._pending_registrations:
            return

        msg = (
            f"REMOTE CONTROLLER: Processing {len(self._pending_registrations)} "
            f"pending module registrations."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        for module_name, module_instance in self._pending_registrations.items():
            msg = f"REMOTE CONTROLLER: Processing pending registration for {module_name}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._register_decorated_commands_internal(module_name, module_instance)

        self._pending_registrations.clear()

    def register_decorated_module(self, module_name: str, module_instance) -> None:
        """Registers a module's decorated D-Bus commands."""

        if not self._is_running or not self._dbus_service_interface or not self._bus:
            msg = (
                f"REMOTE CONTROLLER: Service not ready; queuing decorated registration "
                f"for {module_name}."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._pending_registrations[module_name] = module_instance
            return

        self._register_decorated_commands_internal(module_name, module_instance)

    def _register_decorated_commands_internal(self, module_name: str, module_instance) -> None:
        """Internal method that registers decorated commands from a module instance."""

        if not self._is_running or not self._dbus_service_interface or not self._bus:
            msg = (
                f"REMOTE CONTROLLER: Internal error - _register_decorated_commands_internal "
                f"called for {module_name} but service is not ready."
            )
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            return

        handlers_info = []
        for attr_name in dir(module_instance):
            attr = getattr(module_instance, attr_name)
            if callable(attr) and hasattr(attr, "dbus_command_description"):
                description = attr.dbus_command_description
                def _create_wrapper(method=attr):
                    def _wrapper(notify_user):
                        event = input_event.RemoteControllerEvent()
                        script = script_manager.get_manager().get_active_script()
                        return method(script=script, event=event, notify_user=notify_user)
                    return _wrapper

                handler_info = InputEventHandlerInfo(
                    python_function_name=attr_name,
                    description=description,
                    action=_create_wrapper()
                )
                handlers_info.append(handler_info)

                msg = f"REMOTE CONTROLLER: Found decorated method '{attr_name}': {description}"
                debug.print_message(debug.LEVEL_INFO, msg, True)

        if not handlers_info:
            return

        self._dbus_service_interface.add_module_interface(
            module_name, handlers_info, self._bus, self.OBJECT_PATH)
        msg = (
            f"REMOTE CONTROLLER: Successfully registered {len(handlers_info)} "
            f"decorated commands for module {module_name}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def deregister_module_commands(self, module_name: str) -> bool:
        """Deregisters D-Bus commands for an Orca module."""

        if module_name in self._pending_registrations:
            msg = f"REMOTE CONTROLLER: Removing pending registration for {module_name}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            del self._pending_registrations[module_name]
            return True

        if not self._is_running or not self._dbus_service_interface or not self._bus:
            msg = (
                f"REMOTE CONTROLLER: Cannot deregister commands for {module_name}; "
                "service not running or bus not available."
            )
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        return self._dbus_service_interface.remove_module_interface(
            module_name, self._bus, self.OBJECT_PATH)

    def shutdown(self) -> None:
        """Shuts down the D-Bus service."""

        if not self._is_running:
            msg = "REMOTE CONTROLLER: Shutdown called but service is not running."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "REMOTE CONTROLLER: Attempting to shut down D-Bus service."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if self._dbus_service_interface and self._bus:
            self._dbus_service_interface.shutdown_service(self._bus, self.OBJECT_PATH)
            try:
                self._bus.unpublish_object(self.OBJECT_PATH)
            except DBusError as e:
                msg = f"REMOTE CONTROLLER: Error unpublishing main service object: {e}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            self._dbus_service_interface = None

        if self._bus:
            try:
                self._bus.unregister_service(self.SERVICE_NAME)
            except DBusError as e:
                msg = f"REMOTE CONTROLLER: Error releasing bus name: {e}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bus.disconnect()
            self._bus = None

        self._is_running = False
        msg = "REMOTE CONTROLLER: D-Bus service shut down."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._pending_registrations.clear()

    def is_running(self) -> bool:
        """Checks if the D-Bus service is currently running."""

        return self._is_running

_remote_controller: OrcaRemoteController = OrcaRemoteController()

def get_remote_controller() -> OrcaRemoteController:
    """Returns the OrcaRemoteController singleton."""

    return _remote_controller
