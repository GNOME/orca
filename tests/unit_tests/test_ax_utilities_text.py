# Unit tests for ax_utilities_text.py methods.
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

"""Unit tests for ax_utilities_text.py methods."""

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
class TestAXUtilitiesText:
    """Test AXUtilitiesText class methods."""

    @staticmethod
    def _setup_dependencies(test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_text dependencies."""

        additional_modules = [
            "orca.ax_component",
            "orca.ax_hypertext",
            "orca.ax_object",
            "orca.ax_text",
            "orca.ax_utilities_application",
            "orca.ax_utilities_hypertext",
            "orca.ax_utilities_object",
            "orca.ax_utilities_role",
        ]
        return test_context.setup_shared_dependencies(additional_modules)

    def test_equivalent_selection_positions_in_same_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test exact and newline-normalized offsets are equivalent."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_text import AXText, AXUtilitiesHypertext, AXUtilitiesText

        obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesHypertext,
            "compare_text_positions",
            side_effect=lambda _obj1, offset1, _obj2, offset2: offset1 - offset2,
        )
        get_substring = test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda _obj, start, end: "\n" if (start, end) == (6, 7) else "x",
        )

        assert AXUtilitiesText.text_selection_positions_are_equivalent(obj, 6, obj, 6)
        assert AXUtilitiesText.text_selection_positions_are_equivalent(obj, 6, obj, 7)
        assert not AXUtilitiesText.text_selection_positions_are_equivalent(obj, 5, obj, 7)
        assert get_substring.call_count == 2

    def test_equivalent_selection_positions_at_adjacent_object_boundary(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test the end of one object equals the start of its adjacent object."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_text import (
            AXText,
            AXUtilitiesHypertext,
            AXUtilitiesObject,
            AXUtilitiesText,
        )

        before = test_context.Mock(spec=Atspi.Accessible)
        after = test_context.Mock(spec=Atspi.Accessible)
        ancestor = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesHypertext, "compare_text_positions", return_value=-1)
        test_context.patch_object(AXText, "get_character_count", return_value=5)
        test_context.patch_object(
            AXUtilitiesObject,
            "get_common_ancestor",
            return_value=ancestor,
        )
        expand = test_context.patch_object(
            AXUtilitiesHypertext,
            "expand_eocs_in_range",
            return_value="",
        )

        assert AXUtilitiesText.text_selection_positions_are_equivalent(before, 5, after, 0)
        expand.assert_called_once_with(
            before,
            5,
            after,
            0,
            include_start=False,
            include_end=False,
        )
        assert not AXUtilitiesText.text_selection_positions_are_equivalent(before, 4, after, 0)

    def test_get_selection_anchor_offset_handles_both_sides_of_newline(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test either newline-adjacent focus representation preserves the opposite endpoint."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_text import AXText, AXUtilitiesHypertext, AXUtilitiesText

        obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesHypertext,
            "compare_text_positions",
            side_effect=lambda _obj1, offset1, _obj2, offset2: offset1 - offset2,
        )
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda _obj, start, end: (
                "\n" if (start, end) in {(2, 3), (6, 7)} else "selection"
            ),
        )

        assert AXUtilitiesText.get_selection_anchor_offset(obj, 7, 3, 6) == 3
        assert AXUtilitiesText.get_selection_anchor_offset(obj, 2, 3, 6) == 6

    def test_get_text_selection_endpoints_searches_once_when_nothing_is_selected(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test the search for the last selected position is skipped if there is no first one."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_text import AXObject, AXText, AXUtilitiesText

        root = test_context.Mock(spec=Atspi.Accessible)
        child = test_context.Mock(spec=Atspi.Accessible)
        get_selected_ranges = test_context.patch_object(
            AXText, "get_selected_ranges", return_value=[]
        )
        test_context.patch_object(
            AXObject, "get_child_count", side_effect=lambda obj: 1 if obj == root else 0
        )
        test_context.patch_object(AXObject, "get_child", return_value=child)

        assert AXUtilitiesText.get_text_selection_endpoints(root) == ((None, -1), (None, -1))
        assert get_selected_ranges.call_count == 2
