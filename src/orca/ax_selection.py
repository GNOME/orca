# Orca
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

"""Wrapper for the Atspi.Selection interface."""

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug
from .ax_object import AXObject


class AXSelection:
    """Wrapper for the Atspi.Selection interface."""

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
