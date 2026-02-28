# Unit tests for ax_utilities_object.py methods.
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

# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods

"""Unit tests for ax_utilities_object.py methods."""

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
class TestAXUtilitiesObject:
    """Test AXUtilitiesObject class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_object dependencies."""

        core_modules = [
            "orca.debug",
            "orca.messages",
            "orca.input_event",
            "orca.keybindings",
            "orca.cmdnames",
            "orca.dbus_service",
            "orca.script_manager",
            "orca.orca_i18n",
            "orca.guilabels",
            "orca.text_attribute_names",
            "orca.focus_manager",
            "orca.braille",
            "orca.keynames",
        ]

        essential_modules = {}
        for module_name in core_modules:
            mock_module = test_context.Mock()
            test_context.patch_module(module_name, mock_module)
            essential_modules[module_name] = mock_module

        test_context.configure_shared_module_behaviors(essential_modules)
        keynames_mock = essential_modules["orca.keynames"]
        keynames_mock.KEY_BACKSPACE = "BackSpace"
        keynames_mock.KEY_DELETE = "Delete"
        keynames_mock.KEY_TAB = "Tab"
        keynames_mock.KEY_RETURN = "Return"
        keynames_mock.KEY_ESCAPE = "Escape"

        return essential_modules

    def test_is_ancestor_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.is_ancestor with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject,
            "is_valid",
            side_effect=lambda obj: obj == mock_accessible,
        )
        result = AXUtilitiesObject.is_ancestor(None, mock_accessible)
        assert result is False

    def test_is_ancestor_invalid_ancestor(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.is_ancestor with invalid ancestor."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXObject,
            "is_valid",
            side_effect=lambda obj: obj == mock_accessible,
        )
        result = AXUtilitiesObject.is_ancestor(mock_accessible, None)
        assert result is False

    def test_is_ancestor_same_object_inclusive(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.is_ancestor with same object and inclusive=True."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        result = AXUtilitiesObject.is_ancestor(mock_accessible, mock_accessible, inclusive=True)
        assert result is True

    def test_is_ancestor_same_object_not_inclusive(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.is_ancestor with same object and inclusive=False."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_parent_checked", return_value=None)
        result = AXUtilitiesObject.is_ancestor(mock_accessible, mock_accessible, inclusive=False)
        assert result is False

    def test_is_ancestor_found(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.is_ancestor when ancestor is found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_parent_checked", return_value=mock_ancestor)
        result = AXUtilitiesObject.is_ancestor(mock_accessible, mock_ancestor)
        assert result is True

    def test_is_ancestor_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.is_ancestor when ancestor is not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_parent_checked", return_value=None)
        result = AXUtilitiesObject.is_ancestor(mock_accessible, mock_ancestor)
        assert result is False

    def test_find_descendant_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject._find_descendant with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)

        def always_true(_obj) -> bool:
            return True

        result = AXUtilitiesObject._find_descendant(mock_accessible, always_true)
        assert result is None

    def test_find_descendant_no_children(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject._find_descendant with no children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=0)

        def always_true(_obj) -> bool:
            return True

        result = AXUtilitiesObject._find_descendant(mock_accessible, always_true)
        assert result is None

    def test_find_descendant_found_direct_child(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject._find_descendant with direct child match."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=1)
        test_context.patch_object(AXObject, "get_child_checked", return_value=mock_child)

        def match_child(obj) -> bool:
            return obj == mock_child

        result = AXUtilitiesObject._find_descendant(mock_accessible, match_child)
        assert result == mock_child

    def test_find_descendant_found_in_grandchild(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject._find_descendant with grandchild match."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_grandchild = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 1
            if obj == mock_child:
                return 1
            return 0

        def mock_get_child_checked(obj, idx) -> object:
            if obj == mock_accessible and idx == 0:
                return mock_child
            if obj == mock_child and idx == 0:
                return mock_grandchild
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child_checked", new=mock_get_child_checked)

        def match_grandchild(obj) -> bool:
            return obj == mock_grandchild

        result = AXUtilitiesObject._find_descendant(mock_accessible, match_grandchild)
        assert result == mock_grandchild

    def test_find_deepest_descendant_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_deepest_descendant with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXUtilitiesObject.find_deepest_descendant(mock_accessible)
        assert result is None

    def test_find_deepest_descendant_no_children(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_deepest_descendant with no children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_child_count", return_value=0)
        test_context.patch_object(AXObject, "get_child", return_value=None)
        result = AXUtilitiesObject.find_deepest_descendant(mock_accessible)
        assert result == mock_accessible

    def test_find_deepest_descendant_with_children(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_deepest_descendant with nested children."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        mock_grandchild = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 2
            if obj == mock_child:
                return 1
            return 0

        def mock_get_child(obj, index) -> object:
            if obj == mock_accessible and index == 1:
                return mock_child
            if obj == mock_child and index == 0:
                return mock_grandchild
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)
        result = AXUtilitiesObject.find_deepest_descendant(mock_accessible)
        assert result == mock_grandchild

    def test_find_all_descendants_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject._find_all_descendants with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        matches: list[Atspi.Accessible] = []
        AXUtilitiesObject._find_all_descendants(mock_accessible, None, None, matches)
        assert not matches

    def test_find_all_descendants_with_include_filter(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesObject._find_all_descendants with include filter."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child1 = test_context.Mock(spec=Atspi.Accessible)
        mock_child2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 2
            return 0

        def mock_get_child(obj, idx) -> object:
            if obj == mock_accessible:
                if idx == 0:
                    return mock_child1
                if idx == 1:
                    return mock_child2
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)

        def include_child1(obj) -> bool:
            return obj == mock_child1

        matches: list[Atspi.Accessible] = []
        AXUtilitiesObject._find_all_descendants(mock_accessible, include_child1, None, matches)
        assert matches == [mock_child1]

    def test_find_all_descendants_with_exclude_filter(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesObject._find_all_descendants with exclude filter."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child1 = test_context.Mock(spec=Atspi.Accessible)
        mock_child2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_child_count(obj) -> int:
            if obj == mock_accessible:
                return 2
            return 0

        def mock_get_child(obj, idx) -> object:
            if obj == mock_accessible:
                if idx == 0:
                    return mock_child1
                if idx == 1:
                    return mock_child2
            return None

        test_context.patch_object(AXObject, "get_child_count", new=mock_get_child_count)
        test_context.patch_object(AXObject, "get_child", new=mock_get_child)

        def include_all(_obj) -> bool:
            return True

        def exclude_child1(obj) -> bool:
            return obj == mock_child1

        matches: list[Atspi.Accessible] = []
        AXUtilitiesObject._find_all_descendants(
            mock_accessible,
            include_all,
            exclude_child1,
            matches,
        )
        assert matches == [mock_child2]

    def test_get_common_ancestor_with_none_objects(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.get_common_ancestor with None objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_object import AXUtilitiesObject

        result = AXUtilitiesObject.get_common_ancestor(None, None)
        assert result is None

    def test_get_common_ancestor_same_objects(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.get_common_ancestor with same objects."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        result = AXUtilitiesObject.get_common_ancestor(mock_accessible, mock_accessible)
        assert result == mock_accessible

    def test_find_ancestor_found_in_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_ancestor found in parent."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_parent_checked(obj) -> object:
            if obj == mock_accessible:
                return mock_parent
            return None

        test_context.patch_object(AXObject, "get_parent_checked", new=mock_get_parent_checked)

        def match_parent(obj) -> bool:
            return obj == mock_parent

        result = AXUtilitiesObject.find_ancestor(mock_accessible, match_parent)
        assert result == mock_parent

    def test_find_ancestor_found_in_grandparent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_ancestor found in grandparent."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_grandparent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_parent_checked(obj) -> object:
            if obj == mock_accessible:
                return mock_parent
            if obj == mock_parent:
                return mock_grandparent
            return None

        test_context.patch_object(AXObject, "get_parent_checked", new=mock_get_parent_checked)

        def match_grandparent(obj) -> bool:
            return obj == mock_grandparent

        result = AXUtilitiesObject.find_ancestor(mock_accessible, match_grandparent)
        assert result == mock_grandparent

    def test_find_ancestor_not_found(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_ancestor not found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)

        def mock_get_parent_checked(obj) -> object:
            if obj == mock_accessible:
                return mock_parent
            return None

        test_context.patch_object(AXObject, "get_parent_checked", new=mock_get_parent_checked)

        def never_match(_obj) -> bool:
            return False

        result = AXUtilitiesObject.find_ancestor(mock_accessible, never_match)
        assert result is None

    def test_find_ancestor_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesObject.find_ancestor with no parent."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "get_parent_checked", return_value=None)

        def always_true(_obj) -> bool:
            return True

        result = AXUtilitiesObject.find_ancestor(mock_accessible, always_true)
        assert result is None

    def test_active_descendant_dead_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.active_descendant with dead obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_dead", return_value=True)
        result = AXUtilities.active_descendant(mock_accessible)
        assert result is None

    def test_active_descendant_non_table_cell(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.active_descendant with non-table-cell."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_dead", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=False)
        result = AXUtilities.active_descendant(mock_accessible)
        assert result == mock_accessible

    def test_active_descendant_table_cell_with_name(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.active_descendant with named table cell."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_dead", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=True)
        test_context.patch_object(AXObject, "get_name", return_value="Cell A1")
        result = AXUtilities.active_descendant(mock_accessible)
        assert result == mock_accessible

    def test_active_descendant_table_cell_with_descendant(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilities.active_descendant with table cell having a named descendant."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_object import AXUtilitiesObject
        from orca.ax_utilities_role import AXUtilitiesRole

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_dead", return_value=False)
        test_context.patch_object(AXUtilitiesRole, "is_table_cell", return_value=True)
        test_context.patch_object(
            AXObject,
            "get_name",
            side_effect=lambda obj: "child_name" if obj == mock_child else "",
        )
        test_context.patch_object(AXUtilitiesObject, "find_descendant", return_value=mock_child)
        result = AXUtilities.active_descendant(mock_accessible)
        assert result == mock_child

    def test_find_previous_object_no_restriction(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.find_previous_object without restriction."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_previous = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilities,
            "_get_previous_object",
            return_value=mock_previous,
        )
        result = AXUtilities.find_previous_object(mock_accessible)
        assert result == mock_previous

    def test_find_previous_object_with_restriction(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.find_previous_object with restriction."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_previous = test_context.Mock(spec=Atspi.Accessible)
        mock_restrict = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilities,
            "_get_previous_object",
            return_value=mock_previous,
        )
        test_context.patch_object(AXUtilitiesObject, "is_ancestor", return_value=False)
        result = AXUtilities.find_previous_object(mock_accessible, mock_restrict)
        assert result is None

    def test_find_next_object_no_restriction(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.find_next_object without restriction."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "_get_next_object", return_value=mock_next)
        result = AXUtilities.find_next_object(mock_accessible)
        assert result == mock_next

    def test_find_next_object_with_restriction(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities.find_next_object with restriction."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_object import AXUtilitiesObject

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        mock_restrict = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "_get_next_object", return_value=mock_next)
        test_context.patch_object(AXUtilitiesObject, "is_ancestor", return_value=False)
        result = AXUtilities.find_next_object(mock_accessible, mock_restrict)
        assert result is None

    def test_get_next_object_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_next_object with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXUtilities._get_next_object(mock_accessible)
        assert result is None

    def test_get_next_object_with_flows_to_relation(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_next_object with flows-to relation."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_target = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "is_dead", return_value=False)
        test_context.patch_object(
            AXUtilitiesRelation,
            "get_flows_to",
            return_value=[mock_target],
        )
        result = AXUtilities._get_next_object(mock_obj)
        assert result == mock_target

    def test_get_next_object_with_dead_flows_to_targets(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilities._get_next_object filters out dead flows-to targets."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_target = test_context.Mock(spec=Atspi.Accessible)
        mock_live_target = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject,
            "is_dead",
            side_effect=lambda obj: obj == mock_dead_target,
        )
        test_context.patch_object(
            AXUtilitiesRelation,
            "get_flows_to",
            return_value=[mock_dead_target, mock_live_target],
        )
        result = AXUtilities._get_next_object(mock_obj)
        assert result == mock_live_target

    def test_get_next_object_with_all_dead_flows_to_targets(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilities._get_next_object falls back when all flows-to are dead."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_target1 = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_target2 = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "is_dead", return_value=True)
        test_context.patch_object(AXObject, "get_index_in_parent", return_value=0)
        test_context.patch_object(AXObject, "get_parent", return_value=mock_parent)
        test_context.patch_object(AXObject, "get_child_count", return_value=2)
        test_context.patch_object(AXObject, "get_child", return_value=mock_next)
        test_context.patch_object(
            AXUtilitiesRelation,
            "get_flows_to",
            return_value=[mock_dead_target1, mock_dead_target2],
        )
        result = AXUtilities._get_next_object(mock_obj)
        assert result == mock_next

    def test_get_next_object_normal_traversal(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_next_object with normal parent-child traversal."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_next = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXUtilitiesRelation, "get_flows_to", return_value=[])
        test_context.patch_object(AXObject, "get_index_in_parent", return_value=0)
        test_context.patch_object(AXObject, "get_parent", return_value=mock_parent)
        test_context.patch_object(AXObject, "get_child_count", return_value=3)
        test_context.patch_object(AXObject, "get_child", return_value=mock_next)
        result = AXUtilities._get_next_object(mock_obj)
        assert result == mock_next

    def test_get_next_object_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_next_object when no parent is found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXUtilitiesRelation, "get_flows_to", return_value=[])
        test_context.patch_object(AXObject, "get_index_in_parent", return_value=2)
        test_context.patch_object(AXObject, "get_parent", return_value=None)
        result = AXUtilities._get_next_object(mock_obj)
        assert result is None

    def test_get_previous_object_invalid_obj(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_previous_object with invalid obj."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=False)
        result = AXUtilities._get_previous_object(mock_accessible)
        assert result is None

    def test_get_previous_object_with_flows_from_relation(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilities._get_previous_object with flows-from relation."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_source = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "is_dead", return_value=False)
        test_context.patch_object(
            AXUtilitiesRelation,
            "get_flows_from",
            return_value=[mock_source],
        )
        result = AXUtilities._get_previous_object(mock_obj)
        assert result == mock_source

    def test_get_previous_object_with_dead_flows_from_targets(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilities._get_previous_object filters out dead flows-from targets."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_source = test_context.Mock(spec=Atspi.Accessible)
        mock_live_source = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(
            AXObject,
            "is_dead",
            side_effect=lambda obj: obj == mock_dead_source,
        )
        test_context.patch_object(
            AXUtilitiesRelation,
            "get_flows_from",
            return_value=[mock_dead_source, mock_live_source],
        )
        result = AXUtilities._get_previous_object(mock_obj)
        assert result == mock_live_source

    def test_get_previous_object_with_all_dead_flows_from_targets(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilities._get_previous_object falls back when all flows-from are dead."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_source1 = test_context.Mock(spec=Atspi.Accessible)
        mock_dead_source2 = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        mock_previous = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXObject, "is_dead", return_value=True)
        test_context.patch_object(AXObject, "get_index_in_parent", return_value=1)
        test_context.patch_object(AXObject, "get_parent", return_value=mock_parent)
        test_context.patch_object(AXObject, "get_child_count", return_value=2)
        test_context.patch_object(AXObject, "get_child", return_value=mock_previous)
        test_context.patch_object(
            AXUtilitiesRelation,
            "get_flows_from",
            return_value=[mock_dead_source1, mock_dead_source2],
        )
        result = AXUtilities._get_previous_object(mock_obj)
        assert result == mock_previous

    def test_get_previous_object_no_parent(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilities._get_previous_object when no parent is found."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities import AXUtilities
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "is_valid", return_value=True)
        test_context.patch_object(AXUtilitiesRelation, "get_flows_from", return_value=[])
        test_context.patch_object(AXObject, "get_index_in_parent", return_value=0)
        test_context.patch_object(AXObject, "get_parent", return_value=None)
        result = AXUtilities._get_previous_object(mock_obj)
        assert result is None
