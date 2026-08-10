# Unit tests for text_selection_manager.py methods.
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

"""Unit tests for text_selection_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestTextSelectionManager:
    """Test TextSelectionManager methods."""

    def test_get_all_selected_text_for_spreadsheet_cell(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test spreadsheet-cell selection does not traverse adjacent objects."""

        test_context.setup_shared_dependencies([])
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        cell = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=True)
        test_context.patch_object(
            AXUtilities, "get_selected_text", return_value=("cell text", 2, 11)
        )
        expand_selected_text = test_context.patch_object(
            AXUtilities, "expand_eocs_in_range", return_value="cell text"
        )

        assert manager.get_all_selected_text(script, cell) == "cell text"
        expand_selected_text.assert_called_once_with(
            cell, 2, cell, 11, include_start=True, include_end=False
        )
        script.utilities.find_previous_object.assert_not_called()
        script.utilities.find_next_object.assert_not_called()

    def test_get_all_selected_text_prefers_document_selection(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test document selections take precedence over per-object selections."""

        test_context.setup_shared_dependencies([])
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        obj = test_context.Mock(spec=Atspi.Accessible)
        document = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=False)
        test_context.patch_object(AXUtilities, "is_document", return_value=False)
        test_context.patch_object(AXUtilities, "find_ancestor", return_value=document)
        get_document_selected_texts = test_context.patch_object(
            AXUtilities,
            "get_document_selected_texts",
            return_value=(True, ["First selection", "Second selection"]),
        )
        get_selected_text = test_context.patch_object(AXUtilities, "get_selected_text")
        expand_selected_text = test_context.patch_object(AXUtilities, "expand_eocs_in_range")

        assert manager.get_all_selected_text(script, obj) == "First selection Second selection"
        get_document_selected_texts.assert_called_once_with(document)
        get_selected_text.assert_not_called()
        expand_selected_text.assert_not_called()
        script.utilities.find_previous_object.assert_not_called()
        script.utilities.find_next_object.assert_not_called()

    def test_get_all_selected_text_uses_adjacent_text_objects_as_fallback(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test failed document retrieval falls back to adjacent selected text objects."""

        test_context.setup_shared_dependencies([])
        from orca.text_selection_manager import AXUtilities, TextSelectionManager

        manager = TextSelectionManager()
        script = test_context.Mock()
        obj = test_context.Mock(spec=Atspi.Accessible)
        previous_obj = test_context.Mock(spec=Atspi.Accessible)
        next_obj = test_context.Mock(spec=Atspi.Accessible)
        document = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilities, "is_spreadsheet_cell", return_value=False)
        test_context.patch_object(AXUtilities, "is_document", return_value=False)
        test_context.patch_object(AXUtilities, "find_ancestor", return_value=document)
        test_context.patch_object(
            AXUtilities,
            "get_document_selected_texts",
            return_value=(False, []),
        )
        test_context.patch_object(
            AXUtilities,
            "get_selected_text",
            side_effect=[
                ("current text", 0, 12),
                ("previous text", 0, 13),
                ("next text", 0, 9),
            ],
        )
        test_context.patch_object(
            AXUtilities,
            "expand_eocs_in_range",
            side_effect=[
                "current text",
                "previous text",
                "next text",
            ],
        )
        script.utilities.find_previous_object.side_effect = [previous_obj, None]
        script.utilities.find_next_object.side_effect = [next_obj, None]

        assert manager.get_all_selected_text(script, obj) == (
            "previous text current text next text"
        )
