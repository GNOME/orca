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
from gi.repository import Atspi
from gi.repository import GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXSelection:
    """Test AXSelection class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_selection dependencies."""

        additional_modules = ["orca.ax_utilities_role"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.AXObject = test_context.Mock()
        ax_object_mock.AXObject.supports_selection = test_context.Mock(return_value=True)
        ax_object_mock.AXObject.find_descendant = test_context.Mock()

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"]
        ax_utilities_role_mock.AXUtilitiesRole = test_context.Mock()
        ax_utilities_role_mock.AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        ax_utilities_role_mock.AXUtilitiesRole.is_menu = test_context.Mock(return_value=False)
        ax_utilities_role_mock.AXUtilitiesRole.is_list_box = test_context.Mock(return_value=False)

        return essential_modules

    def _setup_combo_box_selection_mocks(self, test_context, accessible, container, child):
        """Set up common mocks for combo box selection testing."""

        from orca.ax_selection import AXSelection
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        def mock_get_selected_child_count(obj):
            if obj == accessible:
                return 0
            if obj == container:
                return 1
            return 0

        def mock_get_selected_child(obj, idx):
            if obj == container and idx == 0:
                return child
            return None

        test_context.patch_object(
            AXSelection, "get_selected_child_count", side_effect=mock_get_selected_child_count
        )
        test_context.patch_object(
            AXUtilitiesRole, "is_combo_box", side_effect=lambda obj: obj == accessible
        )
        test_context.patch_object(AXUtilitiesRole, "is_menu", return_value=False)
        test_context.patch_object(
            AXUtilitiesRole, "is_list_box", side_effect=lambda obj: obj == container
        )
        test_context.patch_object(AXObject, "find_descendant", return_value=container)
        test_context.patch_object(
            Atspi.Selection, "get_selected_child", side_effect=mock_get_selected_child
        )

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
        from orca.ax_selection import AXSelection
        from orca.ax_object import AXObject
        from orca import debug

        test_context.patch_object(
            AXObject, "supports_selection", return_value=has_selection_support
        )
        if side_effect:
            test_context.patch_object(
                Atspi.Selection, "get_n_selected_children", side_effect=side_effect
            )
        test_context.patch_object(
            debug, "print_tokens", new=essential_modules["orca.debug"].print_tokens
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
            AXSelection, "get_selected_child_count", return_value=selected_count
        )
        test_context.patch_object(
            Atspi.Selection, "get_selected_child", side_effect=mock_get_selected_child
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
        from orca.ax_selection import AXSelection
        from orca import debug

        test_context.patch_object(AXSelection, "get_selected_child_count", return_value=1)

        if error_scenario == "returns_self":
            test_context.patch_object(
                Atspi.Selection, "get_selected_child", return_value=mock_accessible
            )
        elif error_scenario == "glib_error":

            def raise_glib_error(obj, idx):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Selection, "get_selected_child", side_effect=raise_glib_error
            )

        test_context.patch_object(
            debug, "print_tokens", new=essential_modules["orca.debug"].print_tokens
        )
        result = AXSelection.get_selected_child(mock_accessible, 0)
        assert result == expected_result
        if expects_debug_call:
            essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "test_scenario,child_count,expected_length,child_setup",
        [
            pytest.param("none_object", 0, 0, None, id="none_object"),
            pytest.param("multiple_children", 2, 2, "normal", id="multiple_children"),
        ],
    )
    def test_get_selected_children_basic_scenarios(
        self,
        test_context: OrcaTestContext,
        test_scenario: str,
        child_count: int,
        expected_length: int,
        child_setup: str | None,
    ) -> None:
        """Test AXSelection.get_selected_children basic scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_selection import AXSelection

        if test_scenario == "none_object":
            result = AXSelection.get_selected_children(None)
            assert result == []
            return

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        if child_setup == "normal":
            mock_children = [test_context.Mock(spec=Atspi.Accessible) for _ in range(child_count)]

            def mock_get_selected_child(_obj, idx):
                return mock_children[idx] if idx < len(mock_children) else None

            test_context.patch_object(
                AXSelection, "get_selected_child_count", return_value=child_count
            )
            test_context.patch_object(
                Atspi.Selection, "get_selected_child", side_effect=mock_get_selected_child
            )

        result = AXSelection.get_selected_children(mock_accessible)
        assert len(result) == expected_length
        if child_setup == "normal" and child_count > 0:
            for child in mock_children:
                assert child in result

    def test_get_selected_children_combo_box_fallback(self, test_context: OrcaTestContext) -> None:
        """Test AXSelection.get_selected_children with combo box fallback."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_selection import AXSelection

        mock_container = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)

        self._setup_combo_box_selection_mocks(
            test_context, mock_accessible, mock_container, mock_child
        )
        result = AXSelection.get_selected_children(mock_accessible)
        assert result == [mock_child]

    @pytest.mark.parametrize(
        "special_scenario,child_count,expected_length,expects_debug_call",
        [
            pytest.param("removes_self", 2, 1, True, id="removes_self_reference"),
            pytest.param("glib_error", 1, 0, True, id="glib_error"),
            pytest.param("duplicates", 3, 1, False, id="duplicate_children"),
            pytest.param("none_children", 2, 0, False, id="none_children"),
        ],
    )
    def test_get_selected_children_special_scenarios(
        self,
        test_context: OrcaTestContext,
        special_scenario: str,
        child_count: int,
        expected_length: int,
        expects_debug_call: bool,
    ) -> None:
        """Test AXSelection.get_selected_children special scenarios."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_selection import AXSelection
        from orca import debug

        test_context.patch_object(
            AXSelection, "get_selected_child_count", return_value=child_count
        )
        test_context.patch_object(
            debug, "print_tokens", new=essential_modules["orca.debug"].print_tokens
        )

        if special_scenario == "removes_self":
            mock_child = test_context.Mock(spec=Atspi.Accessible)

            def mock_get_selected_child(_obj, idx):
                return mock_accessible if idx == 0 else mock_child if idx == 1 else None

            test_context.patch_object(
                Atspi.Selection, "get_selected_child", side_effect=mock_get_selected_child
            )
            result = AXSelection.get_selected_children(mock_accessible)
            assert mock_child in result
            assert mock_accessible not in result
        elif special_scenario == "glib_error":

            def raise_glib_error(obj, idx):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Selection, "get_selected_child", side_effect=raise_glib_error
            )
        elif special_scenario == "duplicates":
            mock_child = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                Atspi.Selection, "get_selected_child", return_value=mock_child
            )
            result = AXSelection.get_selected_children(mock_accessible)
            assert mock_child in result
        elif special_scenario == "none_children":
            test_context.patch_object(
                Atspi.Selection, "get_selected_child", return_value=None
            )

        if special_scenario not in ["removes_self", "duplicates"]:
            result = AXSelection.get_selected_children(mock_accessible)

        assert len(result) == expected_length
        if expects_debug_call:
            essential_modules["orca.debug"].print_tokens.assert_called()
