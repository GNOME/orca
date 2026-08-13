# Orca
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

"""Manages accessible text selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class TextSelectionManager:
    """Provides high-level text-selection operations independent of navigation modality."""

    @staticmethod
    def _get_selected_text_with_eocs_expanded(obj: Atspi.Accessible) -> str:
        """Returns the selected text with embedded object characters expanded."""

        string, start_offset, end_offset = AXUtilities.get_selected_text(obj)
        if not string:
            return ""

        return AXUtilities.expand_eocs_in_range(
            obj,
            start_offset,
            obj,
            end_offset,
            include_start=True,
            include_end=False,
        )

    def get_all_selected_text(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> str:
        """Returns all text in the logical selection containing obj."""

        if AXUtilities.is_spreadsheet_cell(obj):
            return self._get_selected_text_with_eocs_expanded(obj)

        document = (
            obj
            if AXUtilities.is_document(obj)
            else AXUtilities.find_ancestor(obj, AXUtilities.is_document)
        )
        if document is not None:
            success, strings = AXUtilities.get_document_selected_texts(document)
            if success:
                return " ".join(strings)

            start, end = AXUtilities.get_document_text_selection_endpoints(None, document)
            start_obj, start_offset = start
            end_obj, end_offset = end
            if start_obj is not None and end_obj is not None:
                expanded = AXUtilities.expand_eocs_in_range(
                    start_obj,
                    start_offset,
                    end_obj,
                    end_offset,
                    include_start=True,
                    include_end=False,
                )
                if expanded:
                    return expanded

        strings = []
        current = self._get_selected_text_with_eocs_expanded(obj)
        if current:
            strings.append(current)

        preceding_strings: list[str] = []
        previous_obj = script.utilities.find_previous_object(obj)
        while previous_obj is not None:
            selection = self._get_selected_text_with_eocs_expanded(previous_obj)
            if not selection:
                break
            preceding_strings.insert(0, selection)
            previous_obj = script.utilities.find_previous_object(previous_obj)

        next_obj = script.utilities.find_next_object(obj)
        while next_obj is not None:
            selection = self._get_selected_text_with_eocs_expanded(next_obj)
            if not selection:
                break
            strings.append(selection)
            next_obj = script.utilities.find_next_object(next_obj)

        return " ".join(preceding_strings + strings)


_manager = TextSelectionManager()


def get_manager() -> TextSelectionManager:
    """Returns the singleton text selection manager."""

    return _manager
