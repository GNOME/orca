# Utilities for obtaining information about containers supporting selection
#
# Copyright 2023 Igalia, S.L.
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

"""Utilities for obtaining information about containers supporting selection."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from .ax_object import AXObject
from .ax_utilities_role import AXUtilitiesRole


class AXSelection:
    """Utilities for obtaining information about containers supporting selection."""

    @staticmethod
    def get_selected_child_count(obj: Atspi.Accessible) -> int:
        """Returns the selected child count of obj"""

        if not AXObject.supports_selection(obj):
            return 0

        try:
            count = Atspi.Selection.get_n_selected_children(obj)
        except GLib.GError as error:
            tokens = ["AXSelection: Exception in get_selected_child_count:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return 0

        tokens = ["AXSelection:", obj, "reports", count, "selected children"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_selected_child(obj: Atspi.Accessible, index: int) -> Atspi.Accessible | None:
        """Returns the nth selected child of obj."""

        n_children = AXSelection.get_selected_child_count(obj)
        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not 0 <= index < n_children:
            return None

        try:
            child = Atspi.Selection.get_selected_child(obj, index)
        except GLib.GError as error:
            tokens = ["AXSelection: Exception in get_selected_child:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if child == obj:
            tokens = ["AXSelection:", obj, "claims to be its own selected child"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = ["AXSelection:", child, "is selected child #", index, "of", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return child

    @staticmethod
    def get_selected_children(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of all the selected children of obj."""

        if obj is None:
            return []

        count = AXSelection.get_selected_child_count(obj)
        if not count and AXUtilitiesRole.is_combo_box(obj):
            container = AXObject.find_descendant(
                obj, lambda x: AXUtilitiesRole.is_menu(x) or AXUtilitiesRole.is_list_box(x))
            return AXSelection.get_selected_children(container)

        children = set()
        for i in range(count):
            try:
                child = Atspi.Selection.get_selected_child(obj, i)
            except GLib.GError as error:
                tokens = ["AXSelection: Exception in get_selected_children:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return []

            if child is not None:
                children.add(child)

        if obj in children:
            tokens = ["AXSelection:", obj, "claims to be its own selected child"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            children.remove(obj)

        result = list(children)
        if len(result) != count:
            tokens = ["AXSelection: Selected child count of", obj, f"is {count}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result
