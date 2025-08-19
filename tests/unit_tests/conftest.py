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

"""Shared fixtures and configuration for unit tests."""

from __future__ import annotations

import os
import sys

import pytest

from .orca_test_fixtures import test_context  # noqa: F401  # pylint: disable=unused-import

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

def clean_all_orca_modules() -> None:
    """Aggressively clean all orca modules from sys.modules."""

    modules_to_remove = []
    for module_name in sys.modules:
        if module_name.startswith("orca.") or module_name == "orca":
            modules_to_remove.append(module_name)

    for module_name in modules_to_remove:
        sys.modules.pop(module_name, None)

def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""

    config.addinivalue_line("markers", "unit: marks tests as unit tests")

def pytest_runtest_setup(item: pytest.Item) -> None:  # pylint: disable=unused-argument
    """Clean module cache before each test to prevent cross-test contamination."""

    clean_all_orca_modules()
