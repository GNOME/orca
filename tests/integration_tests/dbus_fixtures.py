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

# pylint: disable=invalid-name
# pylint: disable=unused-argument

"""D-Bus fixtures and helpers for integration tests."""

import os
import threading
import xml.etree.ElementTree as ET
from collections.abc import Callable
from typing import Any

import pytest
from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError

SERVICE_NAME = "org.gnome.Orca1.Service"
SERVICE_PATH = "/org/gnome/Orca1/Service"
PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
INTROSPECTABLE_INTERFACE = "org.freedesktop.DBus.Introspectable"


def module_object_path(module_name: str) -> str:
    """Returns the D-Bus object path for module_name."""

    return f"{SERVICE_PATH}/{module_name}"


def module_interface_name(module_name: str) -> str:
    """Returns the D-Bus interface name exposed by module_name."""

    return f"org.gnome.Orca1.{module_name}"


def list_module_names(bus: SessionMessageBus) -> list[str]:
    """Returns sorted module names registered under /org/gnome/Orca1/Service."""

    proxy = bus.get_proxy(SERVICE_NAME, SERVICE_PATH, interface_name=INTROSPECTABLE_INTERFACE)
    root = ET.fromstring(proxy.Introspect())
    return sorted(node.get("name") for node in root.findall("node") if node.get("name"))


def module_interface_xml(bus: SessionMessageBus, module_name: str) -> ET.Element | None:
    """Returns the <interface> element for the module's native interface, or None."""

    proxy = bus.get_proxy(
        SERVICE_NAME,
        module_object_path(module_name),
        interface_name=INTROSPECTABLE_INTERFACE,
    )
    root = ET.fromstring(proxy.Introspect())
    target = module_interface_name(module_name)
    for iface in root.findall("interface"):
        if iface.get("name") == target:
            return iface
    return None


def simple_command_names(iface_xml: ET.Element | None) -> list[str]:
    """Returns names of methods that take only notify_user (i.e., simple commands)."""

    if iface_xml is None:
        return []
    out = []
    for method in iface_xml.findall("method"):
        in_args = [a for a in method.findall("arg") if a.get("direction") == "in"]
        if len(in_args) == 1 and in_args[0].get("name") == "notify_user":
            out.append(method.get("name"))
    return out


def parameterized_command_names(iface_xml: ET.Element | None) -> list[str]:
    """Returns names of methods that take parameters beyond notify_user."""

    if iface_xml is None:
        return []
    out = []
    for method in iface_xml.findall("method"):
        in_args = [a for a in method.findall("arg") if a.get("direction") == "in"]
        if len(in_args) == 1 and in_args[0].get("name") == "notify_user":
            continue
        out.append(method.get("name"))
    return out


def property_names(iface_xml: ET.Element | None, *access_modes: str) -> list[str]:
    """Returns names of properties whose access attribute is in access_modes."""

    if iface_xml is None:
        return []
    return [
        prop.get("name")
        for prop in iface_xml.findall("property")
        if prop.get("access") in access_modes
    ]


def property_signature(iface_xml: ET.Element | None, property_name: str) -> str | None:
    """Returns the D-Bus signature for property_name, or None if not present."""

    if iface_xml is None:
        return None
    for prop in iface_xml.findall("property"):
        if prop.get("name") == property_name:
            return prop.get("type")
    return None


def command_signature(iface_xml: ET.Element | None, command_name: str) -> list[tuple[str, str]]:
    """Returns the input parameters of command_name as [(arg_name, dbus_type), ...]."""

    if iface_xml is None:
        return []
    method = next(
        (m for m in iface_xml.findall("method") if m.get("name") == command_name),
        None,
    )
    if method is None:
        return []
    return [
        (arg.get("name"), arg.get("type"))
        for arg in method.findall("arg")
        if arg.get("direction") == "in"
    ]


def get_property(bus: SessionMessageBus, module_name: str, property_name: str) -> Any:
    """Reads property_name via Properties.Get; returns the unpacked value."""

    proxy = bus.get_proxy(
        SERVICE_NAME,
        module_object_path(module_name),
        interface_name=PROPERTIES_INTERFACE,
    )
    result = proxy.Get(module_interface_name(module_name), property_name)
    return result.unpack() if hasattr(result, "unpack") else result


def set_property(bus: SessionMessageBus, module_name: str, property_name: str, value: Any) -> None:
    """Writes property_name via Properties.Set."""

    proxy = bus.get_proxy(
        SERVICE_NAME,
        module_object_path(module_name),
        interface_name=PROPERTIES_INTERFACE,
    )
    proxy.Set(module_interface_name(module_name), property_name, value)


@pytest.fixture(scope="session", name="bus")
def _bus(orca: Any) -> SessionMessageBus:
    """Returns a session-scoped bus connection. The orca fixture ensures Orca is up."""

    return SessionMessageBus()


@pytest.fixture(scope="session", name="dbus_service_proxy")
def _dbus_service_proxy(bus: SessionMessageBus) -> Any:
    """Returns a D-Bus proxy for the Orca service root."""

    proxy = bus.get_proxy(SERVICE_NAME, SERVICE_PATH)
    proxy.GetVersion()
    return proxy


@pytest.fixture(scope="session", name="module_proxy_factory")
def _module_proxy_factory(bus: SessionMessageBus) -> Callable[[str], Any]:
    """Factory returning native dasbus proxies; skips when a module is not registered."""

    def _create_proxy(module_name: str):
        target = module_interface_name(module_name)
        try:
            iface = module_interface_xml(bus, module_name)
        except (DBusError, AttributeError, TypeError) as error:
            pytest.skip(f"Could not introspect {module_name}: {error!s}")
            return None
        if iface is None:
            pytest.skip(f"Module {module_name} ({target}) is not registered on the bus")
            return None
        return bus.get_proxy(SERVICE_NAME, module_object_path(module_name))

    return _create_proxy


@pytest.fixture(name="dbus_timeout")
def dbus_timeout_fixture() -> int:
    """Default timeout for D-Bus operations (configurable via environment)."""

    return int(os.environ.get("ORCA_DBUS_TIMEOUT", "5"))


@pytest.fixture
def run_with_timeout(
    dbus_timeout: int,
) -> Callable[[Callable[[], Any], int | None], dict[str, Any]]:
    """Run a test function with timeout handling using threading (thread-safe)."""

    def _run_test(test_func: Callable[[], Any], timeout: int | None = None) -> dict[str, Any]:
        timeout_value = timeout if timeout is not None else dbus_timeout

        result_container = {}
        exception_container = {}

        def target():
            """Target function to run in the thread."""
            try:
                result = test_func()
                result_container["result"] = result
            except (DBusError, AttributeError, TypeError, ValueError) as error:
                exception_container["error"] = error

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_value if timeout_value > 0 else None)

        if thread.is_alive():
            return {
                "success": False,
                "result": None,
                "error": f"TIMEOUT: Test timed out after {timeout_value} seconds",
            }

        if "error" in exception_container:
            error = exception_container["error"]
            if isinstance(error, (DBusError, AttributeError, TypeError, ValueError)):
                return {"success": False, "result": None, "error": str(error)}
            raise error

        return {"success": True, "result": result_container.get("result"), "error": None}

    return _run_test
