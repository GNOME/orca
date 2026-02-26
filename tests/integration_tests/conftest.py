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

"""Shared fixtures and configuration for integration tests."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from .dbus_fixtures import (  # noqa: F401
    _dbus_service_proxy,
    _module_proxy_factory,
    dbus_timeout_fixture,
    run_with_timeout,
)
from .gsettings_fixtures import (  # noqa: F401
    _gsettings_handle,
    _gsettings_profile,
    _gsettings_registry,
)

if TYPE_CHECKING:
    import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""

    config.addinivalue_line("markers", "dbus: marks tests as D-Bus specific tests")
    config.addinivalue_line("markers", "gsettings: marks tests as GSettings integration tests")
