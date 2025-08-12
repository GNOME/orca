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

"""Shared fixtures and configuration for unit tests."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest
from dasbus.error import DBusError

if TYPE_CHECKING:
    from collections.abc import Generator
    from types import ModuleType

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))


@pytest.fixture(name="mock_dbus_service")
def _mock_dbus_service() -> Generator[ModuleType, None, None]:
    """Mock dbus_service dependencies but allow actual implementation to work."""

    class MockVariant:
        """Mock GLib.Variant for testing."""

        def __init__(self, type_string: str, value: Any):
            self._type_string = type_string
            self._value = value

        def get_type_string(self) -> str:
            """Return the variant type string."""
            return self._type_string

        def unpack(self) -> Any:
            """Return the variant value."""
            return self._value

    def mock_variant_constructor(type_string: str, value: Any) -> MockVariant:
        """Create a MockVariant instance."""
        return MockVariant(type_string, value)

    mock_glib = Mock()
    mock_glib.Variant = mock_variant_constructor

    def dbus_interface_decorator(_interface_name):
        def decorator(cls):
            return cls

        return decorator

    mock_dasbus_interface = Mock()
    mock_dasbus_interface.dbus_interface = dbus_interface_decorator

    mock_dasbus_publishable = Mock()
    mock_dasbus_publishable.Publishable = Mock

    mock_gi_repository = Mock()
    mock_gi_repository.GLib = mock_glib

    mock_gi = Mock()
    mock_gi.repository = mock_gi_repository

    # Create mock dasbus.error module that provides real DBusError
    mock_dasbus_error = Mock()
    mock_dasbus_error.DBusError = DBusError

    with patch.dict(
        sys.modules,
        {
            "gi": mock_gi,
            "gi.repository": mock_gi_repository,
            "gi.repository.GLib": mock_glib,
            "dasbus": Mock(),
            "dasbus.connection": Mock(),
            "dasbus.error": mock_dasbus_error,
            "dasbus.loop": Mock(),
            "dasbus.server": Mock(),
            "dasbus.server.interface": mock_dasbus_interface,
            "dasbus.server.publishable": mock_dasbus_publishable,
            "orca.debug": Mock(),
            "orca.input_event": Mock(),
            "orca.orca_platform": Mock(),
            "orca.script_manager": Mock(),
            "orca.orca_i18n": Mock(),
            "orca.messages": Mock(),
            "orca.settings": Mock(),
            "orca.braille": Mock(),
            "orca.ax_object": Mock(),
            "orca.ax_utilities": Mock(),
            "orca.ax_utilities_role": Mock(),
            "orca.ax_component": Mock(),
            "orca.ax_table": Mock(),
            "orca.focus_manager": Mock(),
            "orca.input_event_manager": Mock(),
        },
    ):
        from orca import dbus_service  # pylint: disable=import-outside-toplevel

        yield dbus_service


class OrcaMocks:
    """Container for organized access to Orca dependency mocks."""

    def __init__(self, mocks: dict[str, Mock]):
        """Initialize with mock dictionary."""
        self._mocks = mocks
        # Provide attribute access for better ergonomics
        for name, mock_obj in mocks.items():
            setattr(self, name.replace("-", "_"), mock_obj)

    def __getitem__(self, key: str) -> Mock:
        """Support dictionary-style access for backward compatibility."""
        return self._mocks[key]


@pytest.fixture(name="mock_orca_dependencies")
def _mock_orca_dependencies_fixture(monkeypatch) -> OrcaMocks:
    """Shared fixture for mocking common Orca dependencies.

    Returns an OrcaMocks container with both attribute and dictionary access
    to mocked modules. This centralizes the common mocking logic and reduces
    code duplication.
    """

    # Create commonly used mocks
    debug_mock = Mock()
    debug_mock.print_message = Mock()
    debug_mock.print_tokens = Mock()
    debug_mock.LEVEL_INFO = 1

    # Mock modules that are frequently used across tests
    mocks = {
        "debug": debug_mock,
        "ax_object": Mock(),
        "ax_utilities_role": Mock(),
        "ax_utilities_state": Mock(),
        "ax_utilities_application": Mock(),
        "ax_utilities_relation": Mock(),
        "ax_utilities_event": Mock(),
        "keynames": Mock(),
        # Additional mocks for more complex test files
        "colornames": Mock(
            rgb_string_to_color_name=Mock(return_value="red"),
            normalize_rgb_string=Mock(return_value="#ff0000"),
        ),
        "messages": Mock(
            pixel_count=Mock(return_value="5 pixels"),
            CURRENT_DATE="Current date",
            CURRENT_TIME="Current time",
            CURRENT_LOCATION="Current location",
            CURRENT_PAGE="Current page",
            CURRENT_STEP="Current step",
            CURRENT_ITEM="Current item",
        ),
        "settings": Mock(useColorNames=True),
        "text_attribute_names": Mock(
            attribute_names={"bg-color": "Background Color"},
            attribute_values={"bold": "Bold", "fill": "fill"},
        ),
        # Advanced mocks for complex dependencies
        "orca_i18n": Mock(
            _=lambda x: x, C_=lambda c, x: x, ngettext=lambda s, p, n: s if n == 1 else p
        ),
        "orca_platform": Mock(version="1.0.0"),
        "ax_collection": Mock(),
        "ax_component": Mock(),
        "ax_utilities": Mock(),
    }

    # Apply all mocks to sys.modules
    for module_name, mock_obj in mocks.items():
        monkeypatch.setitem(sys.modules, f"orca.{module_name}", mock_obj)

    return OrcaMocks(mocks)


def clean_module_cache(module_name: str) -> None:
    """Clean a specific module from sys.modules cache."""

    if module_name in sys.modules:
        del sys.modules[module_name]


def pytest_configure(config: Any) -> None:
    """Register custom markers."""

    config.addinivalue_line("markers", "unit: marks tests as unit tests")
