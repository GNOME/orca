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

import ast
import contextlib
import enum
import inspect
import types
import typing
import xml.etree.ElementTree as ET
from collections.abc import Callable

from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError
from dasbus.server.interface import dbus_interface
from dasbus.server.publishable import Publishable
from dasbus.typing import UInt32 as UInt32  # noqa: PLC0414  (re-export)
from gi.repository import GLib

from . import (  # pylint: disable=no-name-in-module
    debug,
    orca_platform,
)


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


class _Kind(enum.Enum):
    """Decorated-method kinds detected during module registration."""

    COMMAND = enum.auto()
    PARAMETERIZED = enum.auto()
    GETTER = enum.auto()
    SETTER = enum.auto()


class _ModuleRegistration:  # pylint: disable=too-many-instance-attributes
    """Tracks a module's decorated methods and its published D-Bus interface."""

    def __init__(self, module_name: str) -> None:
        self._module_name: str = module_name
        self._commands: dict[str, Callable] = {}
        self._parameterized_commands: dict[str, Callable] = {}
        self._getters: dict[str, Callable] = {}
        self._setters: dict[str, Callable] = {}
        self._descriptions: dict[str, str] = {}
        self._dbus_object: object | None = None
        self._object_path: str = ""

    def get_module_name(self) -> str:
        """Returns the module name."""

        return self._module_name

    def get_commands(self) -> dict[str, Callable]:
        """Returns the simple (non-parameterized) commands."""

        return self._commands

    def get_parameterized_commands(self) -> dict[str, Callable]:
        """Returns the parameterized commands."""

        return self._parameterized_commands

    def get_getters(self) -> dict[str, Callable]:
        """Returns the property getters."""

        return self._getters

    def get_setters(self) -> dict[str, Callable]:
        """Returns the property setters."""

        return self._setters

    def get_descriptions(self) -> dict[str, str]:
        """Returns the description for each exposed CamelCase member name."""

        return self._descriptions

    def get_object_path(self) -> str:
        """Returns the D-Bus object path under which the module is published."""

        return self._object_path

    def set_object_path(self, path: str) -> None:
        """Stores the D-Bus object path under which the module was published."""

        self._object_path = path

    def get_dbus_object(self) -> object | None:
        """Returns the published D-Bus interface instance, or None if not published."""

        return self._dbus_object

    def set_dbus_object(self, obj: object) -> None:
        """Stores the published D-Bus interface instance."""

        self._dbus_object = obj

    def is_empty(self) -> bool:
        """Returns True if the registration has no decorated members."""

        return not (
            self._commands or self._parameterized_commands or self._getters or self._setters
        )

    def total_member_count(self) -> int:
        """Returns the total number of exposed members (commands + properties)."""

        return (
            len(self._commands)
            + len(self._parameterized_commands)
            + len(self._getters)
            + len(self._setters)
        )

    def find_command(self, command_name: str) -> Callable | None:
        """Returns the original command method for the given CamelCase name, or None."""

        return self._commands.get(command_name) or self._parameterized_commands.get(command_name)

    def find_getter(self, property_name: str) -> Callable | None:
        """Returns the original getter for the given CamelCase property name, or None."""

        return self._getters.get(property_name)

    def find_setter(self, property_name: str) -> Callable | None:
        """Returns the original setter for the given CamelCase property name, or None."""

        return self._setters.get(property_name)

    def add_decorated_member(
        self, kind: _Kind, attr_name: str, method: Callable, description: str
    ) -> None:
        """Records a decorated method under its DBus member name."""

        dbus_name = self._dbus_name_for(attr_name, kind)
        if kind is _Kind.COMMAND:
            self._commands[dbus_name] = method
            self._descriptions[dbus_name] = description
        elif kind is _Kind.PARAMETERIZED:
            self._parameterized_commands[dbus_name] = method
            self._descriptions[dbus_name] = description
        elif kind is _Kind.GETTER:
            self._getters[dbus_name] = method
            if dbus_name not in self._descriptions:
                self._descriptions[dbus_name] = description
        elif kind is _Kind.SETTER:
            self._setters[dbus_name] = method
            self._descriptions[dbus_name] = description

    @staticmethod
    def _dbus_name_for(attr_name: str, kind: _Kind) -> str:
        """Returns the CamelCase D-Bus name for a Python attribute name and decorator kind."""

        if kind in (_Kind.GETTER, _Kind.SETTER) and attr_name.startswith(("get_", "set_")):
            attr_name = attr_name[4:]
        return "".join(word.capitalize() for word in attr_name.split("_"))

    @classmethod
    def from_module_instance(
        cls, module_name: str, module_instance: object
    ) -> "_ModuleRegistration":
        """Walks module_instance and groups its decorated members by kind."""

        registration = cls(module_name)
        for attr_name in dir(module_instance):
            method = getattr(module_instance, attr_name, None)
            if not callable(method):
                continue
            kind, description = cls._classify_method(method)
            if kind is None:
                continue
            registration.add_decorated_member(kind, attr_name, method, description)
        return registration

    @staticmethod
    def _classify_method(method: Callable) -> tuple[_Kind | None, str]:
        """Returns (kind, description) for a decorated method, or (None, '') if undecorated."""

        description = getattr(method, "dbus_command_description", None)
        if description is not None:
            return _Kind.COMMAND, description

        description = getattr(method, "dbus_parameterized_command_description", None)
        if description is not None:
            return _Kind.PARAMETERIZED, description

        description = getattr(method, "dbus_getter_description", None)
        if description is not None:
            return _Kind.GETTER, description

        description = getattr(method, "dbus_setter_description", None)
        if description is not None:
            return _Kind.SETTER, description

        return None, ""


class _InterfaceBuilder:
    """Builds an introspectable D-Bus interface class from a _ModuleRegistration."""

    _RESERVED_PARAMS = frozenset({"self", "script", "event", "notify_user"})
    _BUILTIN_TYPES: typing.ClassVar[dict[str, object]] = {
        "bool": bool,
        "int": int,
        "UInt32": UInt32,
        "float": float,
        "str": str,
        "list": list,
        "tuple": tuple,
        "dict": dict,
        "None": type(None),
    }

    @classmethod
    def build(cls, registration: _ModuleRegistration) -> type:
        """Dynamically constructs a D-Bus interface class for the registered module."""

        def for_publication(self):
            """Returns the D-Bus interface XML for publication."""

            return self.__dbus_xml__  # pylint: disable=no-member

        namespace: dict[str, object] = {"for_publication": for_publication}
        for cname, method in registration.get_commands().items():
            namespace[cname] = cls._make_command_method(method)
        for cname, method in registration.get_parameterized_commands().items():
            namespace[cname] = cls._make_parameterized_command_method(method)
        getters = registration.get_getters()
        setters = registration.get_setters()
        for cname in set(getters) | set(setters):
            namespace[cname] = cls._make_property(getters.get(cname), setters.get(cname))

        module_name = registration.get_module_name()
        new_cls = type(f"{module_name}DBusInterface", (Publishable,), namespace)
        interface_name = f"org.gnome.Orca1.{module_name}"
        new_cls = dbus_interface(interface_name)(new_cls)
        new_cls.__dbus_xml__ = cls._inject_docstrings(
            new_cls.__dbus_xml__, registration.get_descriptions()
        )
        return new_cls

    @staticmethod
    def _inject_docstrings(xml_text: str, descriptions: dict[str, str]) -> str:
        """Adds org.gtk.GDBus.DocString annotations to methods and properties in the XML."""

        if not descriptions:
            return xml_text
        # XML is generated in-process by dasbus, not untrusted input.
        root = ET.fromstring(xml_text)  # noqa: S314
        for iface in root.findall("interface"):
            for element in list(iface.findall("method")) + list(iface.findall("property")):
                name = element.get("name")
                description = descriptions.get(name) if name else None
                if not description:
                    continue
                annotation = ET.Element(
                    "annotation",
                    {"name": "org.gtk.GDBus.DocString", "value": description},
                )
                element.insert(0, annotation)
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def _strip_optional(annotation):
        """Returns the non-None branch of Optional[T] / T | None, else the annotation unchanged."""

        origin = typing.get_origin(annotation)
        if origin in (typing.Union, types.UnionType):
            non_none = tuple(arg for arg in typing.get_args(annotation) if arg is not type(None))
            if len(non_none) == 1:
                return non_none[0]
        return annotation

    @classmethod
    def _resolve_annotation(cls, annotation):
        """Resolves annotation to a real type, or returns the original string."""

        # Resolve each annotation independently. typing.get_type_hints is all-or-nothing:
        # a single TYPE_CHECKING-only name on a sibling parameter (e.g. `script: default.Script`)
        # makes it raise NameError and lose every annotation in the function. Walking the AST
        # per-annotation lets the resolvable ones — like `language: str` — survive.
        if not isinstance(annotation, str):
            return annotation
        try:
            tree = ast.parse(annotation, mode="eval")
        except SyntaxError:
            return annotation
        try:
            return cls._type_from_node(tree.body)
        except (KeyError, AttributeError, TypeError):
            return annotation

    @classmethod
    def _type_from_node(cls, node: ast.AST):
        """Reconstructs a type from an AST node using a fixed builtin whitelist."""

        if isinstance(node, ast.Name):
            return cls._BUILTIN_TYPES[node.id]
        if isinstance(node, ast.Constant):
            if node.value is None:
                return type(None)
            raise KeyError(node.value)
        if isinstance(node, ast.Subscript):
            base = cls._type_from_node(node.value)
            slice_node = node.slice
            if isinstance(slice_node, ast.Tuple):
                args = tuple(cls._type_from_node(elt) for elt in slice_node.elts)
                return base[args]
            return base[cls._type_from_node(slice_node)]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return cls._type_from_node(node.left) | cls._type_from_node(node.right)
        raise KeyError(ast.dump(node))

    @classmethod
    def _resolved_signature(cls, method: Callable) -> inspect.Signature:
        """Returns method's signature with string annotations resolved per-parameter."""

        sig = inspect.signature(method)
        new_params = [
            param.replace(annotation=cls._resolve_annotation(param.annotation))
            for param in sig.parameters.values()
        ]
        return sig.replace(
            parameters=new_params,
            return_annotation=cls._resolve_annotation(sig.return_annotation),
        )

    @staticmethod
    def _make_command_method(method: Callable) -> Callable:
        """Builds a D-Bus method (notify_user) -> bool wrapping an @command method."""

        def Method(_self, notify_user: bool = True) -> bool:  # pylint: disable=invalid-name
            # Local imports break a circular import: dbus_service is imported by speech_manager,
            # and script_manager (transitively) imports speech_manager.
            from . import (  # pylint: disable=import-outside-toplevel
                input_event,
                input_event_manager,
                script_manager,
            )

            event = input_event.RemoteControllerEvent()
            manager = script_manager.get_manager()
            script = manager.get_active_script() or manager.get_default_script()
            result = method(script=script, event=event, notify_user=notify_user)
            input_event_manager.get_manager().process_remote_controller_event(event)
            return bool(result)

        return Method

    @classmethod
    def _make_parameterized_command_method(cls, method: Callable) -> Callable:
        """Builds a D-Bus method mirroring a @parameterized_command's user-facing signature."""

        original_sig = cls._resolved_signature(method)
        user_params = [
            (name, param)
            for name, param in original_sig.parameters.items()
            if name not in cls._RESERVED_PARAMS
        ]

        needs_notify_user = "notify_user" in original_sig.parameters

        new_params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        annotations: dict[str, object] = {}
        for name, param in user_params:
            annotation = cls._strip_optional(param.annotation)
            new_params.append(
                inspect.Parameter(
                    name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=param.default,
                    annotation=annotation,
                )
            )
            annotations[name] = annotation

        if needs_notify_user:
            new_params.append(
                inspect.Parameter(
                    "notify_user",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=True,
                    annotation=bool,
                )
            )
            annotations["notify_user"] = bool

        return_annotation = original_sig.return_annotation
        if return_annotation is inspect.Signature.empty:
            return_annotation = bool
        annotations["return"] = return_annotation

        new_sig = inspect.Signature(new_params, return_annotation=return_annotation)

        def Method(_self, *args, **kwargs):  # pylint: disable=invalid-name
            from . import (  # pylint: disable=import-outside-toplevel
                input_event,
                input_event_manager,
                script_manager,
            )

            bound = new_sig.bind(_self, *args, **kwargs)
            bound.apply_defaults()
            bound.arguments.pop("self", None)

            event = input_event.RemoteControllerEvent()
            manager = script_manager.get_manager()
            script = manager.get_active_script() or manager.get_default_script()
            bound.arguments["script"] = script
            bound.arguments["event"] = event
            result = method(**bound.arguments)
            input_event_manager.get_manager().process_remote_controller_event(event)
            return result

        Method.__signature__ = new_sig  # type: ignore[attr-defined]
        Method.__annotations__ = annotations
        return Method

    @classmethod
    def _make_property(cls, get_method: Callable | None, set_method: Callable | None) -> property:
        """Builds a D-Bus property from a getter and/or setter pair."""

        read = cls._make_property_getter(get_method) if get_method is not None else None
        write = cls._make_property_setter(set_method) if set_method is not None else None
        return property(read, write)

    @classmethod
    def _make_property_getter(cls, get_method: Callable) -> Callable:
        """Builds the read accessor for a D-Bus property, wrapping the original @getter method."""

        return_annotation = cls._resolved_signature(get_method).return_annotation
        if return_annotation is inspect.Signature.empty:
            return_annotation = bool

        def read(_self, _original=get_method):
            return _original()

        read.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
            [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)],
            return_annotation=return_annotation,
        )
        read.__annotations__ = {"return": return_annotation}
        return read

    @classmethod
    def _make_property_setter(cls, set_method: Callable) -> Callable:
        """Builds the write accessor for a D-Bus property, wrapping the original @setter method."""

        set_sig = cls._resolved_signature(set_method)
        value_param = next(param for name, param in set_sig.parameters.items() if name != "self")
        value_type = cls._strip_optional(value_param.annotation)
        if value_type is inspect.Signature.empty:
            value_type = bool

        def write(_self, value, _original=set_method):
            _original(value)

        write.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
            [
                inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),
                inspect.Parameter(
                    "value",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=value_type,
                ),
            ]
        )
        write.__annotations__ = {"value": value_type}
        return write


@dbus_interface("org.gnome.Orca1.Service")
class OrcaDBusServiceInterface(Publishable):
    """Internal D-Bus service object that handles D-Bus specifics."""

    def for_publication(self):
        """Returns the D-Bus interface XML for publication."""

        return self.__dbus_xml__  # pylint: disable=no-member

    def ShowPreferences(self) -> bool:  # pylint: disable=invalid-name
        """Shows Orca's preferences GUI."""

        from . import script_manager  # pylint: disable=import-outside-toplevel

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

    def PresentMessage(self, message: str) -> bool:  # pylint: disable=invalid-name
        """Presents message to the user."""

        from . import presentation_manager  # pylint: disable=import-outside-toplevel

        msg = f"DBUS SERVICE: PresentMessage called with: '{message}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        presentation_manager.get_manager().present_message(message)
        return True

    def GetVersion(self) -> str:  # pylint: disable=invalid-name
        """Returns Orca's version and revision if available."""

        result = orca_platform.version
        if orca_platform.revision:
            result += f" (rev {orca_platform.revision})"
        msg = f"DBUS SERVICE: GetVersion called, returning: {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def Quit(self) -> bool:  # pylint: disable=invalid-name
        """Quits Orca."""

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


class OrcaRemoteController:
    """Manages Orca's D-Bus service for remote control."""

    SERVICE_NAME = "org.gnome.Orca1.Service"
    OBJECT_PATH = "/org/gnome/Orca1/Service"

    def __init__(self) -> None:
        self._dbus_service_interface: OrcaDBusServiceInterface | None = None
        self._is_running: bool = False
        self._bus: SessionMessageBus | None = None
        self._registered: dict[str, _ModuleRegistration] = {}
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
                with contextlib.suppress(DBusError):
                    self._bus.unpublish_object(self.OBJECT_PATH)
            self._dbus_service_interface = None
            self._bus = None
            return False

        self._is_running = True
        msg = (
            f"REMOTE CONTROLLER: Service started name={self.SERVICE_NAME} path={self.OBJECT_PATH}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._process_pending_registrations()
        self._print_registration_summary()
        return True

    def shutdown(self) -> None:
        """Shuts down the D-Bus service."""

        if not self._is_running:
            msg = "REMOTE CONTROLLER: Shutdown called but service is not running."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = "REMOTE CONTROLLER: Attempting to shut down D-Bus service."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for module_name in list(self._registered):
            self._unpublish_module(module_name)

        if self._dbus_service_interface is not None and self._bus is not None:
            with contextlib.suppress(DBusError):
                self._bus.unpublish_object(self.OBJECT_PATH)
            self._dbus_service_interface = None

        if self._bus is not None:
            with contextlib.suppress(DBusError):
                self._bus.unregister_service(self.SERVICE_NAME)
            self._bus.disconnect()
            self._bus = None

        self._is_running = False
        msg = "REMOTE CONTROLLER: D-Bus service shut down."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._pending_registrations.clear()

    def register_decorated_module(self, module_name: str, module_instance: object) -> None:
        """Registers a module's decorated D-Bus methods, getters, and setters."""

        if not self._is_running or self._bus is None:
            msg = f"REMOTE CONTROLLER: Service not ready; queuing registration for {module_name}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._pending_registrations[module_name] = module_instance
            return
        self._publish_module(module_name, module_instance)

    def deregister_module_commands(self, module_name: str) -> bool:
        """Deregisters a previously-registered module."""

        if module_name in self._pending_registrations:
            del self._pending_registrations[module_name]
            msg = f"REMOTE CONTROLLER: Removed pending registration for {module_name}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if module_name not in self._registered:
            msg = f"REMOTE CONTROLLER: Module '{module_name}' is not registered."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        return self._unpublish_module(module_name)

    def present_message_internal(self, message: str) -> bool:
        """Presents a message via speech and/or braille without a D-Bus round-trip."""

        if self._dbus_service_interface is None:
            msg = "REMOTE CONTROLLER: Cannot present message; service not started."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        return self._dbus_service_interface.PresentMessage(message)

    def execute_command_internal(
        self,
        module_name: str,
        command_name: str,
        notify_user: bool = True,
    ) -> bool:
        """Executes a module command without a D-Bus round-trip."""

        registration = self._registered.get(module_name)
        if registration is None:
            msg = f"REMOTE CONTROLLER: Module '{module_name}' not found."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        method = registration.find_command(command_name)
        if method is None:
            msg = f"REMOTE CONTROLLER: Unknown command '{command_name}' in '{module_name}'."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        from . import (  # pylint: disable=import-outside-toplevel
            input_event,
            input_event_manager,
            script_manager,
        )

        event = input_event.RemoteControllerEvent()
        manager = script_manager.get_manager()
        script = manager.get_active_script() or manager.get_default_script()
        result = method(script=script, event=event, notify_user=notify_user)
        input_event_manager.get_manager().process_remote_controller_event(event)
        return bool(result)

    def get_value_internal(self, module_name: str, property_name: str) -> object:
        """Gets a runtime value from a module without a D-Bus round-trip."""

        registration = self._registered.get(module_name)
        if registration is None:
            msg = f"REMOTE CONTROLLER: Module '{module_name}' not found."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        method = registration.find_getter(property_name)
        if method is None:
            msg = f"REMOTE CONTROLLER: Unknown getter '{property_name}' in '{module_name}'."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        return method()

    def set_value_internal(self, module_name: str, property_name: str, value: object) -> bool:
        """Sets a runtime value on a module without a D-Bus round-trip."""

        registration = self._registered.get(module_name)
        if registration is None:
            msg = f"REMOTE CONTROLLER: Module '{module_name}' not found."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        method = registration.find_setter(property_name)
        if method is None:
            msg = f"REMOTE CONTROLLER: Unknown setter '{property_name}' in '{module_name}'."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        result = method(value)
        if result is None:
            return True
        return bool(result)

    def _publish_module(self, module_name: str, module_instance: object) -> None:
        """Builds the per-module D-Bus interface and publishes it on the bus."""

        if self._bus is None:
            return

        if module_name in self._registered:
            msg = f"REMOTE CONTROLLER: Module {module_name} already registered. Replacing."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._unpublish_module(module_name)

        registration = _ModuleRegistration.from_module_instance(module_name, module_instance)
        if registration.is_empty():
            return

        try:
            interface_class = _InterfaceBuilder.build(registration)
            # for_publication is supplied to the namespace, so the class isn't actually
            # abstract; pylint can't statically infer that.
            dbus_object = interface_class()  # pylint: disable=abstract-class-instantiated
            object_path = f"{self.OBJECT_PATH}/{module_name}"
            self._bus.publish_object(object_path, dbus_object)
        except DBusError as e:
            msg = f"REMOTE CONTROLLER: Failed to publish module {module_name}: {e}"
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            return

        registration.set_dbus_object(dbus_object)
        registration.set_object_path(object_path)
        self._registered[module_name] = registration

        msg = (
            f"REMOTE CONTROLLER: Registered {registration.total_member_count()} member(s) "
            f"for {module_name} at {object_path}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _unpublish_module(self, module_name: str) -> bool:
        """Removes a module's D-Bus interface from the bus."""

        registration = self._registered.get(module_name)
        if registration is None or self._bus is None:
            return False
        try:
            self._bus.unpublish_object(registration.get_object_path())
        except DBusError as e:
            msg = f"REMOTE CONTROLLER: Error unpublishing {module_name}: {e}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False
        del self._registered[module_name]
        msg = f"REMOTE CONTROLLER: Unpublished {module_name}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def _process_pending_registrations(self) -> None:
        """Publishes any modules that registered before the service was ready."""

        if not self._pending_registrations:
            return
        msg = (
            f"REMOTE CONTROLLER: Processing {len(self._pending_registrations)} pending "
            f"module registrations."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        for module_name, module_instance in list(self._pending_registrations.items()):
            self._publish_module(module_name, module_instance)
        self._pending_registrations.clear()

    def _print_registration_summary(self) -> None:
        """Logs a summary of the registered modules and their member counts."""

        modules = len(self._registered)
        commands = sum(
            len(reg.get_commands()) + len(reg.get_parameterized_commands())
            for reg in self._registered.values()
        )
        getters = sum(len(reg.get_getters()) for reg in self._registered.values())
        setters = sum(len(reg.get_setters()) for reg in self._registered.values())
        msg = (
            f"REMOTE CONTROLLER: Registration summary: {modules} modules, "
            f"{commands} commands, {getters} getters, {setters} setters."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)


_remote_controller: OrcaRemoteController = OrcaRemoteController()


def get_remote_controller() -> OrcaRemoteController:
    """Returns the OrcaRemoteController singleton."""

    return _remote_controller
