# Orca
#
# Copyright 2023-2026 Igalia, S.L.
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

"""Utilities for obtaining selection-related information about accessible objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_table import AXTable
from .ax_utilities_collection import AXUtilitiesCollection
from .ax_utilities_object import AXUtilitiesObject
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState
from .ax_utilities_table import AXUtilitiesTable

if TYPE_CHECKING:
    from typing import ClassVar


class AXUtilitiesSelection:
    """Utilities for obtaining selection-related information about accessible objects."""

    _all_items_selected: ClassVar[dict[int, bool]] = {}

    @staticmethod
    def clear_cache_now(reason: str = "") -> None:
        """Clears all cached selection state."""

        AXUtilitiesSelection._all_items_selected.clear()

    @staticmethod
    def get_all_items_selected_state(obj: Atspi.Accessible) -> bool:
        """Returns the cached all-items-selected state for obj."""

        return AXUtilitiesSelection._all_items_selected.get(hash(obj), False)

    @staticmethod
    def set_all_items_selected_state(obj: Atspi.Accessible, selected: bool) -> None:
        """Sets the cached all-items-selected state for obj."""

        AXUtilitiesSelection._all_items_selected[hash(obj)] = selected

    @staticmethod
    def get_selected_children(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of all the selected children of obj."""

        if obj is None:
            return []

        count = AXSelection.get_selected_child_count(obj)
        if not count and AXUtilitiesRole.is_combo_box(obj):
            if AXObject.supports_collection(obj):
                container = AXUtilitiesCollection.find_first_with_role(
                    obj, [Atspi.Role.MENU, Atspi.Role.LIST_BOX]
                )
            else:
                container = AXUtilitiesObject.find_descendant(
                    obj,
                    lambda x: AXUtilitiesRole.is_menu(x) or AXUtilitiesRole.is_list_box(x),
                )
            return AXUtilitiesSelection.get_selected_children(container)

        children = set()
        for i in range(count):
            child = AXSelection.get_selected_child(obj, i)
            if child is not None:
                children.add(child)

        if obj in children:
            tokens = ["AXUtilitiesSelection:", obj, "claims to be its own selected child"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            children.remove(obj)

        result = list(children)
        if len(result) != count:
            tokens = ["AXUtilitiesSelection: Selected child count of", obj, f"is {count}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    @staticmethod
    def selected_children(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of selected children in obj."""

        if AXUtilitiesTable.is_spreadsheet_table(obj):
            return []

        return AXUtilitiesSelection.get_selected_children(obj)

    @staticmethod
    def get_selection_container(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the selection container for obj."""

        if not obj:
            return None

        if AXUtilitiesRole.is_paragraph(obj) or AXUtilitiesState.is_editable(obj):
            return None

        if AXObject.supports_selection(obj):
            return obj

        rolemap = {
            Atspi.Role.CANVAS: [Atspi.Role.LAYERED_PANE],
            Atspi.Role.ICON: [Atspi.Role.LAYERED_PANE],
            Atspi.Role.LIST_ITEM: [Atspi.Role.LIST_BOX],
            Atspi.Role.TREE_ITEM: [Atspi.Role.TREE, Atspi.Role.TREE_TABLE],
            Atspi.Role.TABLE_CELL: [Atspi.Role.TABLE, Atspi.Role.TREE_TABLE],
            Atspi.Role.TABLE_ROW: [Atspi.Role.TABLE, Atspi.Role.TREE_TABLE],
        }

        matching_roles = rolemap.get(AXObject.get_role(obj))

        def is_match(x: Atspi.Accessible) -> bool:
            if matching_roles and AXObject.get_role(x) not in matching_roles:
                return False
            return AXObject.supports_selection(x)

        return AXUtilitiesObject.find_ancestor(obj, is_match)

    @staticmethod
    def selectable_child_count(obj: Atspi.Accessible) -> int:
        """Returns the number of selectable children in obj."""

        if not AXObject.supports_selection(obj):
            return 0

        if AXObject.supports_table(obj):
            rows = AXTable.get_row_count(obj)
            return max(0, rows)

        rolemap = {
            Atspi.Role.LIST_BOX: [Atspi.Role.LIST_ITEM],
            Atspi.Role.TREE: [Atspi.Role.TREE_ITEM],
        }

        role = AXObject.get_role(obj)
        if role not in rolemap:
            return AXObject.get_child_count(obj)

        def is_match(x: Atspi.Accessible) -> bool:
            return AXObject.get_role(x) in rolemap[role]

        return len(AXUtilitiesObject.find_all_descendants(obj, is_match))

    @staticmethod
    def selected_child_count(obj: Atspi.Accessible) -> int:
        """Returns the number of selected children in obj."""

        if AXObject.supports_table(obj):
            return AXTable.get_selected_row_count(obj)
        return AXSelection.get_selected_child_count(obj)

    @staticmethod
    def all_items_selected(obj: Atspi.Accessible) -> bool:
        """Returns True if all items in obj are selected."""

        if not AXObject.supports_selection(obj):
            return False

        if AXUtilitiesState.is_expandable(obj) and not AXUtilitiesState.is_expanded(obj):
            return False

        if AXUtilitiesRole.is_combo_box(obj) or AXUtilitiesRole.is_menu(obj):
            return False

        child_count = AXObject.get_child_count(obj)
        if child_count == AXSelection.get_selected_child_count(obj):
            child = AXSelection.get_selected_child(obj, 0)
            if AXObject.get_parent(child) != obj:
                return False

            tokens = ["AXUtilitiesSelection: All", child_count, "children believed to be selected"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return AXUtilitiesTable.all_cells_are_selected(obj)
