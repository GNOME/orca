# Unit tests for ax_selection.py methods.
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

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_selection.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXSelection:
    """Test AXSelection class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_selection dependencies."""

        essential_modules = test_context.setup_shared_dependencies()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject = test_context.Mock()
        ax_object_mock.AXObject.supports_selection = test_context.Mock(return_value=True)

        return essential_modules

    @pytest.mark.parametrize(
        "has_selection_support,side_effect,expected_result,expects_debug_call",
        [
            pytest.param(True, lambda obj: 3, 3, True, id="with_support"),
            pytest.param(False, None, 0, False, id="without_support"),
            pytest.param(
                True,
                lambda obj: (_ for _ in ()).throw(GLib.GError("Test error")),
                0,
                True,
                id="glib_error",
            ),
        ],
    )
    def test_get_selected_child_count_scenarios(
        self,
        test_context: OrcaTestContext,
        has_selection_support: bool,
        side_effect,
        expected_result: int,
        expects_debug_call: bool,
    ) -> None:
        """Test AXSelection.get_selected_child_count with various scenarios."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import debug
        from orca.ax_object import AXObject
        from orca.ax_selection import AXSelection

        test_context.patch_object(
            AXObject,
            "supports_selection",
            return_value=has_selection_support,
        )
        if side_effect:
            test_context.patch_object(
                Atspi.Selection,
                "get_n_selected_children",
                side_effect=side_effect,
            )
        test_context.patch_object(
            debug,
            "print_tokens",
            new=essential_modules["orca.debug"].print_tokens,
        )
        result = AXSelection.get_selected_child_count(mock_accessible)
        assert result == expected_result
        if expects_debug_call:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "selected_count, index, expected_child",
        [
            pytest.param(3, 0, "child_0", id="first_child"),
            pytest.param(3, 2, "child_2", id="last_child"),
            pytest.param(3, -1, "child_2", id="negative_index_last"),
            pytest.param(0, 0, None, id="no_selected_children"),
            pytest.param(3, 5, None, id="index_out_of_bounds"),
            pytest.param(3, -2, None, id="invalid_negative_index"),
        ],
    )
    def test_get_selected_child(self, test_context, selected_count, index, expected_child) -> None:
        """Test AXSelection.get_selected_child."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_selection import AXSelection

        mock_children = {i: f"child_{i}" for i in range(selected_count)}

        def mock_get_selected_child(_obj, idx):
            return mock_children.get(idx)

        test_context.patch_object(
            AXSelection,
            "get_selected_child_count",
            return_value=selected_count,
        )
        test_context.patch_object(
            Atspi.Selection,
            "get_selected_child",
            side_effect=mock_get_selected_child,
        )
        result = AXSelection.get_selected_child(mock_accessible, index)
        assert result == expected_child
        if expected_child is not None:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "error_scenario,expected_result,expects_debug_call",
        [
            pytest.param("returns_self", None, True, id="returns_self"),
            pytest.param("glib_error", None, True, id="glib_error"),
        ],
    )
    def test_get_selected_child_error_scenarios(
        self,
        test_context: OrcaTestContext,
        error_scenario: str,
        expected_result,
        expects_debug_call: bool,
    ) -> None:
        """Test AXSelection.get_selected_child error scenarios."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca import debug
        from orca.ax_selection import AXSelection

        test_context.patch_object(AXSelection, "get_selected_child_count", return_value=1)

        if error_scenario == "returns_self":
            test_context.patch_object(
                Atspi.Selection,
                "get_selected_child",
                return_value=mock_accessible,
            )
        elif error_scenario == "glib_error":

            def raise_glib_error(obj, idx):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Selection,
                "get_selected_child",
                side_effect=raise_glib_error,
            )

        test_context.patch_object(
            debug,
            "print_tokens",
            new=essential_modules["orca.debug"].print_tokens,
        )
        result = AXSelection.get_selected_child(mock_accessible, 0)
        assert result == expected_result
        if expects_debug_call:
            essential_modules["orca.debug"].print_tokens.assert_called()
