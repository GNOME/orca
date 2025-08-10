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

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements

"""Provides a D-Bus interface for remotely controlling Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2025 Valve Corporation."
__license__   = "LGPL"

import enum
import inspect
from typing import Callable

from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError
from dasbus.loop import EventLoop
from dasbus.server.interface import dbus_interface
from dasbus.server.publishable import Publishable
from gi.repository import GLib

from . import debug
from . import input_event
from . import input_event_manager
from . import orca_platform # pylint: disable=no-name-in-module
from . import script_manager

class HandlerType(enum.Enum):
    """Enumeration of handler types for D-Bus methods."""

    COMMAND = enum.auto()
    PARAMETERIZED_COMMAND = enum.auto()
    GETTER = enum.auto()
    SETTER = enum.auto()

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

def parameterized_command(func):
    """Decorator to mark a method as a D-Bus parameterized command using its docstring.

    Usage:
        @parameterized_command
        def get_voices_for_language(
            self,
            language,
            variant='',
            script=None,
            event=None,
            notify_user=False
        ):
            '''Returns a list of available voices for the specified language.'''
            # method implementation
    """
    description = func.__doc__ or f"D-Bus parameterized command: {func.__name__}"
    func.dbus_parameterized_command_description = description
    return func

def getter(func):
    """Decorator to mark a method as a D-Bus getter using its docstring.

    Usage:
        @getter
        def get_rate(self):
            '''Returns the current speech rate.'''
            # method implementation
    """
    description = func.__doc__ or f"D-Bus getter: {func.__name__}"
    func.dbus_getter_description = description
    return func

def setter(func):
    """Decorator to mark a method as a D-Bus setter using its docstring.

    Usage:
        @setter
        def set_rate(self, value):
            '''Sets the current speech rate.'''
            # method implementation
    """
    description = func.__doc__ or f"D-Bus setter: {func.__name__}"
    func.dbus_setter_description = description
    return func


def _extract_function_parameters(func: Callable) -> list[tuple[str, str]]:
    """Extract parameter names and types from a function signature."""

    sig = inspect.signature(func)
    parameters = []

    skip_params = {"self", "script", "event"}
    for param_name, param in sig.parameters.items():
        if param_name in skip_params:
            continue

        if param.annotation != inspect.Parameter.empty:
            if hasattr(param.annotation, "__name__"):
                type_str = param.annotation.__name__
            else:
                type_str = str(param.annotation).replace("typing.", "")
        else:
            type_str = "Any"
        parameters.append((param_name, type_str))

    return parameters


class _HandlerInfo:
    """Stores processed information about a function exposed via D-Bus."""

    def __init__(
        self,
        python_function_name: str,
        description: str,
        action: Callable[..., bool],
        handler_type: HandlerType = HandlerType.COMMAND,
        parameters: list[tuple[str, str]] | None = None
    ):
        self.python_function_name: str = python_function_name
        self.description: str = description
        self.action: Callable[..., bool] = action
        self.handler_type: HandlerType = handler_type
        self.parameters: list[tuple[str, str]] = parameters or []


@dbus_interface("org.gnome.Orca.Module")
class OrcaModuleDBusInterface(Publishable):
    """A D-Bus interface representing a specific Orca module (e.g., a manager)."""

    def __init__(self,
                 module_name: str,
                 handlers_info: list[_HandlerInfo]):
        super().__init__()
        self._module_name = module_name
        self._commands: dict[str, _HandlerInfo] = {}
        self._parameterized_commands: dict[str, _HandlerInfo] = {}
        self._getters: dict[str, _HandlerInfo] = {}
        self._setters: dict[str, _HandlerInfo] = {}

        for info in handlers_info:
            handler_type = getattr(info, "handler_type", HandlerType.COMMAND)
            normalized_name = self._normalize_handler_name(info.python_function_name, handler_type)
            if handler_type == HandlerType.GETTER:
                self._getters[normalized_name] = info
            elif handler_type == HandlerType.SETTER:
                self._setters[normalized_name] = info
            elif handler_type == HandlerType.PARAMETERIZED_COMMAND:
                self._parameterized_commands[normalized_name] = info
            else:
                self._commands[normalized_name] = info

        msg = (
            f"DBUS SERVICE: OrcaModuleDBusInterface for {module_name} initialized "
            f"with {len(self._commands)} command(s), "
            f"{len(self._parameterized_commands)} parameterized command(s), "
            f"{len(self._getters)} getter(s), {len(self._setters)} setter(s)."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def ExecuteRuntimeGetter(self, getter_name: str) -> GLib.Variant: # pylint: disable=invalid-name
        """Executes the named getter returning the value as a GLib.Variant for D-Bus marshalling."""

        handler_info = self._getters.get(getter_name)
        if not handler_info:
            msg = f"DBUS SERVICE: Unknown getter '{getter_name}' for '{self._module_name}'."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return GLib.Variant("v", GLib.Variant("s", ""))

        result = handler_info.action()
        msg = f"DBUS SERVICE: Getter '{getter_name}' returned: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._to_variant(result)

    def ExecuteRuntimeSetter(self, setter_name: str, value: GLib.Variant) -> bool: # pylint: disable=invalid-name
        """Executes the named setter, returning True if succeeded."""

        handler_info = self._setters.get(setter_name)
        if handler_info is None:
            msg = f"DBUS SERVICE: Unknown setter '{setter_name}' for '{self._module_name}'."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        unpacked = value.unpack()
        result = handler_info.action(unpacked)
        msg = f"DBUS SERVICE: Setter '{setter_name}' with value '{unpacked}' returned: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def ListCommands(self) -> list[tuple[str, str]]: # pylint: disable=invalid-name
        """Returns a list of (command_name, description) for this module (commands only)."""

        command_list = []
        for camel_case_name, info in self._commands.items():
            command_list.append((camel_case_name, info.description))
        return command_list

    def ListParameterizedCommands(  # pylint: disable=invalid-name
        self,
    ) -> list[tuple[str, str, list[tuple[str, str]]]]:
        """Returns a list of (command_name, description, parameters) for this module."""

        command_list = []
        for camel_case_name, info in self._parameterized_commands.items():
            command_list.append((camel_case_name, info.description, info.parameters))
        return command_list

    def ListRuntimeGetters(self) -> list[tuple[str, str]]: # pylint: disable=invalid-name
        """Returns a list of (getter_name, description) for this module."""

        getter_list = []
        for camel_case_name, info in self._getters.items():
            getter_list.append((camel_case_name, info.description))
        return getter_list

    def ListRuntimeSetters(self) -> list[tuple[str, str]]: # pylint: disable=invalid-name
        """Returns a list of (setter_name, description) for this module."""

        setter_list = []
        for camel_case_name, info in self._setters.items():
            setter_list.append((camel_case_name, info.description))
        return setter_list

    def ExecuteCommand(self, command_name: str, notify_user: bool) -> bool: # pylint: disable=invalid-name
        """Executes the named command and returns True if the command succeeded."""

        if command_name not in self._commands:
            msg = f"DBUS SERVICE: Unknown command '{command_name}' for '{self._module_name}'."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        handler_info = self._commands[command_name]
        msg = f"DBUS SERVICE: About to execute '{command_name}' in '{self._module_name}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        result = handler_info.action(notify_user)
        msg = (
            f"DBUS SERVICE: '{command_name}' in '{self._module_name}' executed. "
            f"Result: {result}, notify_user: {notify_user}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def ExecuteParameterizedCommand( # pylint: disable=invalid-name
        self,
        command_name: str,
        parameters: dict[str, GLib.Variant],
        notify_user: bool
    ) -> GLib.Variant:
        """Executes the named command with parameters and returns the result."""

        handler_info = self._parameterized_commands.get(command_name)
        if not handler_info:
            msg = (
                f"DBUS SERVICE: Unknown parameterized command '{command_name}' for "
                f"'{self._module_name}'."
            )
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return GLib.Variant("b", False)

        kwargs = {name: variant.unpack() for name, variant in parameters.items()}
        kwargs["notify_user"] = notify_user
        msg = f"DBUS SERVICE: About to execute '{command_name}' in '{self._module_name}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        result = handler_info.action(**kwargs)
        msg = f"DBUS SERVICE: '{command_name}' in '{self._module_name}' executed."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._to_variant(result)

    def for_publication(self):
        """Returns the D-Bus interface XML for publication."""

        return self.__dbus_xml__ # pylint: disable=no-member

    @staticmethod
    def _normalize_handler_name(
        function_name: str,
        handler_type: HandlerType = HandlerType.COMMAND
    ) -> str:
        """Normalizes a Python function name for D-Bus exposure (getter/setter/command)."""

        # Only strip prefixes for getters and setters, not for commands
        if handler_type in (HandlerType.GETTER, HandlerType.SETTER):
            if function_name.startswith("get_") or function_name.startswith("set_"):
                function_name = function_name[4:]
        return "".join(word.capitalize() for word in function_name.split("_"))

    @staticmethod
    def _to_variant(result):
        """Converts a Python value to a correctly-typed GLib.Variant for D-Bus marshalling."""

        if isinstance(result, bool):
            return GLib.Variant("b", result)
        if isinstance(result, int):
            return GLib.Variant("i", result)
        if isinstance(result, float):
            return GLib.Variant("d", result)
        if isinstance(result, str):
            return GLib.Variant("s", result)
        if isinstance(result, dict):
            return GLib.Variant(
                "a{sv}", {str(k): GLib.Variant("v", v) for k, v in result.items()})
        if isinstance(result, (list, tuple)):
            if all(isinstance(x, str) for x in result):
                return GLib.Variant("as", list(result))
            if all(isinstance(x, bool) for x in result):
                return GLib.Variant("ab", list(result))
            if all(isinstance(x, int) for x in result):
                return GLib.Variant("ax", list(result))
            if all(isinstance(x, (list, tuple)) for x in result):
                if not result:
                    return GLib.Variant("av", [])
                first_len = len(result[0])
                converted = [tuple(str(item or "") for item in x) for x in result]
                signature = "(" + "s" * first_len + ")"
                return GLib.Variant(f"a{signature}", converted)
            return GLib.Variant("av", [GLib.Variant("v", x) for x in result])
        if result is None:
            return GLib.Variant("v", GLib.Variant("s", ""))
        return GLib.Variant("s", str(result))


@dbus_interface("org.gnome.Orca.Service")
class OrcaDBusServiceInterface(Publishable):
    """Internal D-Bus service object that handles D-Bus specifics."""

    def __init__(self) -> None:
        super().__init__()
        self._registered_modules: set[str] = set()

    def for_publication(self):
        """Returns the D-Bus interface XML for publication."""

        return self.__dbus_xml__  # pylint: disable=no-member

    def add_module_interface(
        self,
        module_name: str,
        handlers_info: list[_HandlerInfo],
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
            if not attr_name.startswith("_") and attr_name[0].isupper():
                attr = getattr(self, attr_name)
                if callable(attr) and hasattr(attr, "__doc__"):
                    description = (attr.__doc__.strip() if attr.__doc__
                                 else f"Service command: {attr_name}")
                    commands.append((attr_name, description))

        return sorted(commands)

    def ShowPreferences(self) -> bool: # pylint: disable=invalid-name
        """Shows Orca's preferences GUI."""

        msg = "DBUS SERVICE: ShowPreferences called."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        manager = script_manager.get_manager()
        script = manager.get_active_script() or manager.get_default_script()
        if script is None:
            msg = "DBUS SERVICE: No script available"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        script.show_preferences_gui()
        return True

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

        script.present_message(message)
        return True

    def GetVersion(self) -> str: # pylint: disable=invalid-name
        """Returns Orca's version and revision if available."""

        result = orca_platform.version
        if orca_platform.revision:
            result += f" (rev {orca_platform.revision})"

        msg = f"DBUS SERVICE: GetVersion called, returning: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def Quit(self) -> bool: # pylint: disable=invalid-name
        """Quits Orca. Returns True if the quit request was accepted."""

        msg = "DBUS SERVICE: Quit called."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        from . import orca  # pylint: disable=import-outside-toplevel

        # orca.shutdown() shuts down the dbus service, so send the response immediately and then
        # do the actual shutdown after a brief delay.
        def _delayed_shutdown():
            orca.shutdown()
            return False

        GLib.timeout_add(100, _delayed_shutdown)
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
        self._total_commands: int = 0
        self._total_getters: int = 0
        self._total_setters: int = 0
        self._total_modules: int = 0

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
        self._print_registration_summary()
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
        commands_count = 0
        getters_count = 0
        setters_count = 0

        for attr_name in dir(module_instance):
            attr = getattr(module_instance, attr_name)
            # Command
            if callable(attr) and hasattr(attr, "dbus_command_description"):
                description = attr.dbus_command_description
                def _create_wrapper(method=attr):
                    def _wrapper(notify_user):
                        event = input_event.RemoteControllerEvent()
                        script = script_manager.get_manager().get_active_script()
                        if script is None:
                            script = script_manager.get_manager().get_default_script()
                        rv = method(script=script, event=event, notify_user=notify_user)
                        # TODO - JD: It probably makes sense to fully process these input
                        # events just like any others, rather than have the caller here.
                        input_event_manager.get_manager().process_remote_controller_event(event)
                        return rv
                    return _wrapper
                handler_info = _HandlerInfo(
                    python_function_name=attr_name,
                    description=description,
                    action=_create_wrapper(),
                    handler_type=HandlerType.COMMAND
                )
                handlers_info.append(handler_info)
                commands_count += 1
            # Parameterized Command
            elif callable(attr) and hasattr(attr, "dbus_parameterized_command_description"):
                description = attr.dbus_parameterized_command_description
                def _create_parameterized_wrapper(method=attr):
                    def _wrapper(**kwargs):
                        event = input_event.RemoteControllerEvent()
                        script = script_manager.get_manager().get_active_script()
                        if script is None:
                            script = script_manager.get_manager().get_default_script()
                        rv = method(script=script, event=event, **kwargs)
                        # TODO - JD: It probably makes sense to fully process these input
                        # events just like any others, rather than have the caller here.
                        input_event_manager.get_manager().process_remote_controller_event(event)
                        return rv
                    return _wrapper
                handler_info = _HandlerInfo(
                    python_function_name=attr_name,
                    description=description,
                    action=_create_parameterized_wrapper(),
                    handler_type=HandlerType.PARAMETERIZED_COMMAND,
                    parameters=_extract_function_parameters(attr)
                )
                handlers_info.append(handler_info)
                commands_count += 1
            # Getter
            elif callable(attr) and hasattr(attr, "dbus_getter_description"):
                description = attr.dbus_getter_description
                def _create_getter_wrapper(method=attr):
                    def _wrapper(_notify_user=None):
                        return method()
                    return _wrapper
                handler_info = _HandlerInfo(
                    python_function_name=attr_name,
                    description=description,
                    action=_create_getter_wrapper(),
                    handler_type=HandlerType.GETTER
                )
                handlers_info.append(handler_info)
                getters_count += 1
            # Setter
            elif callable(attr) and hasattr(attr, "dbus_setter_description"):
                description = attr.dbus_setter_description
                def _create_setter_wrapper(method=attr):
                    def _wrapper(value):
                        return method(value)
                    return _wrapper
                handler_info = _HandlerInfo(
                    python_function_name=attr_name,
                    description=description,
                    action=_create_setter_wrapper(),
                    handler_type=HandlerType.SETTER
                )
                handlers_info.append(handler_info)
                setters_count += 1

        if not handlers_info:
            return

        self._total_commands += commands_count
        self._total_getters += getters_count
        self._total_setters += setters_count
        self._total_modules += 1

        self._dbus_service_interface.add_module_interface(
            module_name, handlers_info, self._bus, self.OBJECT_PATH)
        msg = (
            f"REMOTE CONTROLLER: Successfully registered {len(handlers_info)} "
            f"commands/getters/setters for module {module_name}."
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
        self._total_commands = 0
        self._total_getters = 0
        self._total_setters = 0
        self._total_modules = 0

    def is_running(self) -> bool:
        """Checks if the D-Bus service is currently running."""

        return self._is_running

    def _count_system_commands(self) -> int:
        """Counts the system-wide D-Bus commands available on the main service interface."""

        if not self._dbus_service_interface:
            return 0

        system_commands = 0
        for attr_name in dir(self._dbus_service_interface):
            if not attr_name.startswith("_") and attr_name[0].isupper():
                attr = getattr(self._dbus_service_interface, attr_name)
                if callable(attr) and hasattr(attr, "__doc__"):
                    system_commands += 1
        return system_commands

    def _print_registration_summary(self) -> None:
        """Prints a summary of all registered D-Bus handlers."""

        system_commands_count = self._count_system_commands()
        total_handlers = self._total_commands + self._total_getters + self._total_setters
        msg = (
            f"REMOTE CONTROLLER: Registration complete. Summary: "
            f"{self._total_modules} modules, "
            f"{self._total_commands} module commands, "
            f"{self._total_getters} module getters, "
            f"{self._total_setters} module setters, "
            f"{system_commands_count} system commands. "
            f"Total handlers: {total_handlers + system_commands_count}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

_remote_controller: OrcaRemoteController = OrcaRemoteController()

def get_remote_controller() -> OrcaRemoteController:
    """Returns the OrcaRemoteController singleton."""

    return _remote_controller
