# Unit tests for ax_selection.py selection-related methods.
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
# pylint: disable=unused-argument

"""Unit tests for ax_selection.py selection-related methods."""

from unittest.mock import Mock

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from .conftest import clean_module_cache


@pytest.mark.unit
class TestAXSelection:
    """Test selection-related methods."""

    @pytest.fixture
    def mock_accessible(self):
        """Create a mock Atspi.Accessible object."""

        return Mock(spec=Atspi.Accessible)

    def test_get_selected_child_count_with_selection_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_child_count with selection support."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_selection", lambda obj: True)
        monkeypatch.setattr(Atspi.Selection, "get_n_selected_children", lambda obj: 3)

        result = AXSelection.get_selected_child_count(mock_accessible)
        assert result == 3
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_child_count_without_selection_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_child_count without selection support."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_selection", lambda obj: False)

        result = AXSelection.get_selected_child_count(mock_accessible)
        assert result == 0

    def test_get_selected_child_count_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_child_count handles GLib.GError."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca.ax_object import AXObject
        from orca import debug

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "supports_selection", lambda obj: True)
        monkeypatch.setattr(Atspi.Selection, "get_n_selected_children", raise_glib_error)
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)

        result = AXSelection.get_selected_child_count(mock_accessible)
        assert result == 0
        mock_orca_dependencies["debug"].print_tokens.assert_called()

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
    def test_get_selected_child(
        self,
        monkeypatch,
        mock_accessible,
        selected_count,
        index,
        expected_child,
        mock_orca_dependencies,
    ):
        """Test AXSelection.get_selected_child."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection

        mock_children = {i: f"child_{i}" for i in range(selected_count)}

        def mock_get_selected_child(obj, idx):
            return mock_children.get(idx)

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: selected_count)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", mock_get_selected_child)

        result = AXSelection.get_selected_child(mock_accessible, index)
        assert result == expected_child

        if expected_child is not None:
            mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_child_returns_self(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_child when object returns itself."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca import debug

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 1)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", lambda obj, idx: mock_accessible)
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)

        result = AXSelection.get_selected_child(mock_accessible, 0)
        assert result is None
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_child_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_child handles GLib.GError."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca import debug

        def raise_glib_error(obj, idx):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 1)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", raise_glib_error)
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)

        result = AXSelection.get_selected_child(mock_accessible, 0)
        assert result is None
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_children_with_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXSelection.get_selected_children with None object."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection

        result = AXSelection.get_selected_children(None)
        assert result == []

    def test_get_selected_children_with_multiple_children(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_children with multiple children."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection

        mock_child1 = Mock(spec=Atspi.Accessible)
        mock_child2 = Mock(spec=Atspi.Accessible)
        mock_children = [mock_child1, mock_child2]

        def mock_get_selected_child(obj, idx):
            return mock_children[idx] if idx < len(mock_children) else None

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 2)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", mock_get_selected_child)

        result = AXSelection.get_selected_children(mock_accessible)
        assert len(result) == 2
        assert mock_child1 in result
        assert mock_child2 in result

    def test_get_selected_children_combo_box_fallback(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_children with combo box fallback."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca.ax_object import AXObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_container = Mock(spec=Atspi.Accessible)
        mock_child = Mock(spec=Atspi.Accessible)

        def mock_get_selected_child_count(obj):
            if obj == mock_accessible:
                return 0
            if obj == mock_container:
                return 1
            return 0

        def mock_get_selected_child(obj, idx):
            if obj == mock_container and idx == 0:
                return mock_child
            return None

        monkeypatch.setattr(AXSelection, "get_selected_child_count", mock_get_selected_child_count)
        monkeypatch.setattr(AXUtilitiesRole, "is_combo_box", lambda obj: obj == mock_accessible)
        monkeypatch.setattr(AXUtilitiesRole, "is_menu", lambda obj: False)
        monkeypatch.setattr(AXUtilitiesRole, "is_list_box", lambda obj: obj == mock_container)
        monkeypatch.setattr(AXObject, "find_descendant", lambda obj, func: mock_container)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", mock_get_selected_child)

        result = AXSelection.get_selected_children(mock_accessible)
        assert result == [mock_child]

    def test_get_selected_children_removes_self_reference(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_children removes self-reference."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca import debug

        mock_child = Mock(spec=Atspi.Accessible)

        def mock_get_selected_child(obj, idx):
            if idx == 0:
                return mock_accessible
            if idx == 1:
                return mock_child
            return None

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 2)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", mock_get_selected_child)
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)

        result = AXSelection.get_selected_children(mock_accessible)
        assert len(result) == 1
        assert mock_child in result
        assert mock_accessible not in result
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_children_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_children handles GLib.GError."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection
        from orca import debug

        def raise_glib_error(obj, idx):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 1)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", raise_glib_error)
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)

        result = AXSelection.get_selected_children(mock_accessible)
        assert result == []
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_selected_children_with_duplicates(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_children handles duplicate children."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection

        mock_child = Mock(spec=Atspi.Accessible)

        def mock_get_selected_child(obj, idx):
            return mock_child

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 3)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", mock_get_selected_child)

        result = AXSelection.get_selected_children(mock_accessible)
        assert len(result) == 1
        assert mock_child in result

    def test_get_selected_children_with_none_children(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXSelection.get_selected_children with None children returned."""

        clean_module_cache("orca.ax_selection")
        from orca.ax_selection import AXSelection

        def mock_get_selected_child(obj, idx):
            return None

        monkeypatch.setattr(AXSelection, "get_selected_child_count", lambda obj: 2)
        monkeypatch.setattr(Atspi.Selection, "get_selected_child", mock_get_selected_child)

        result = AXSelection.get_selected_children(mock_accessible)
        assert result == []
