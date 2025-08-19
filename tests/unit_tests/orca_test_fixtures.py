# Orca Test Fixtures - Pytest Integration
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

"""Pytest fixtures for Orca screen reader tests.

This module provides pytest fixtures that integrate the OrcaTestContext
with pytest's fixture system, providing clean, isolated test environments.

The fixtures are designed to be simple to use while providing complete
test isolation and preventing cross-test contamination.

Usage:
    def test_presenter(orca_test):
        orca_test.setup_where_am_i_presenter_dependencies()
        from orca.where_am_i_presenter import WhereAmIPresenter

        presenter = WhereAmIPresenter()
        result = presenter.some_method()
        assert result is True
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import pytest

from .orca_test_context import OrcaTestContext

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

@pytest.fixture
def test_context(mocker: MockerFixture, monkeypatch) -> Generator[OrcaTestContext, None, None]:
    """Provides clean, isolated Orca test environment.

    This is the primary fixture for Orca tests. It provides a complete
    test isolation context that prevents cross-test contamination.

    Usage:
        class TestMyModule:
            def _setup_dependencies(self, orca_test):
                # Set up only what your module needs
                return orca_test.setup_shared_dependencies(["orca.debug"])

            def test_my_functionality(self, orca_test):
                self._setup_dependencies(orca_test)
                from orca.my_module import MyClass

                # Your test code here
                instance = MyClass()
                result = instance.some_method()

                assert result is True

    Args:
        mocker: pytest-mock mocker fixture (automatically injected)
        monkeypatch: pytest monkeypatch fixture (automatically injected)

    Yields:
        OrcaTestContext instance with clean isolation
    """

    with OrcaTestContext(mocker, monkeypatch) as context:
        yield context
