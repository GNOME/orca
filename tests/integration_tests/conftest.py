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

# pylint: disable=unused-argument

"""Shared fixtures and configuration for integration tests."""

import os
import threading
from typing import Any, Callable

import pytest
from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError


@pytest.fixture(scope="session", name="dbus_service_proxy")
def _dbus_service_proxy() -> Any:
    """Get a dasbus proxy for the main Orca service."""

    try:
        bus = SessionMessageBus()
        proxy = bus.get_proxy("org.gnome.Orca.Service", "/org/gnome/Orca/Service")
        proxy.GetVersion()
        return proxy
    except (DBusError, AttributeError, TypeError) as error:
        pytest.skip(f"Orca D-Bus service not available: {str(error)}")
        return None

@pytest.fixture(scope="session", name="module_proxy_factory")
def _module_proxy_factory(dbus_service_proxy: Any) -> Callable[[str], Any]:
    """Factory for creating module-specific D-Bus proxies."""

    def _create_proxy(module_name: str):
        # If we got here, dbus_service_proxy succeeded, so Orca is running
        try:
            bus = SessionMessageBus()
            return bus.get_proxy(
                "org.gnome.Orca.Service",
                f"/org/gnome/Orca/Service/{module_name}"
            )
        except (DBusError, AttributeError, TypeError) as error:
            pytest.skip(f"Could not create proxy for {module_name}: {str(error)}")
            return None

    return _create_proxy

@pytest.fixture(name="dbus_timeout")
def dbus_timeout_fixture() -> int:
    """Default timeout for D-Bus operations (configurable via environment)."""

    return int(os.environ.get("ORCA_DBUS_TIMEOUT", "5"))

@pytest.fixture
def run_with_timeout(
    dbus_timeout: int
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
        thread.daemon = True  # Allow program to exit even if thread is still running
        thread.start()
        thread.join(timeout_value if timeout_value > 0 else None)

        if thread.is_alive():
            # Thread is still running, so it timed out
            return {
                "success": False,
                "result": None,
                "error": f"TIMEOUT: Test timed out after {timeout_value} seconds"
            }

        if "error" in exception_container:
            error = exception_container["error"]
            if isinstance(error, (DBusError, AttributeError, TypeError, ValueError)):
                return {"success": False, "result": None, "error": str(error)}
            # Re-raise unexpected exceptions
            raise error

        return {"success": True, "result": result_container.get("result"), "error": None}

    return _run_test

def pytest_configure(config: Any) -> None:
    """Register custom markers."""

    config.addinivalue_line("markers", "dbus: marks tests as D-Bus specific tests")
