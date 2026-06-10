# Unit tests for ax_utilities_selection.py methods.
#
# Copyright 2026 Igalia, S.L.
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
# pylint: disable=protected-access

"""Unit tests for ax_utilities_selection.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXUtilitiesSelectionCache:
    """Tests the manager-backed selection utility cache."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_selection dependencies."""

        return test_context.setup_shared_dependencies(
            [
                "orca.ax_selection",
                "orca.ax_table",
                "orca.ax_utilities_collection",
                "orca.ax_utilities_object",
                "orca.ax_utilities_role",
                "orca.ax_utilities_state",
                "orca.ax_utilities_table",
            ]
        )

    def test_import_registers_selection_cache_namespace(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test importing selection utilities registers its cache namespace."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager

        manager = ax_cache_manager.get_manager()
        register = test_context.patch_object(
            manager,
            "register_cache",
            wraps=manager.register_cache,
        )

        from orca.ax_utilities_selection import AXUtilitiesSelection

        register.assert_called_once_with(
            AXUtilitiesSelection._CACHE,
            AXUtilitiesSelection._CACHE.IS_ALL_ITEMS_SELECTED,
            lifetime=ax_cache_manager.Lifetime.PROCESS,
            clear_interval_seconds=None,
        )

    def test_manager_clear_cache_now_clears_selected_all_state(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test routine manager clearing removes selected-all states."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager
        from orca.ax_utilities_selection import AXUtilitiesSelection

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        AXUtilitiesSelection.set_all_items_selected_state(mock_obj, True)

        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert AXUtilitiesSelection.get_all_items_selected_state(mock_obj) is False
