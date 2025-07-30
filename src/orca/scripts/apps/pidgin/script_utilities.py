# Orca
#
# Copyright 2010 Joanmarie Diggs.
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


"""Custom script utilities for pidgin."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import script_utilities
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(script_utilities.Utilities):
    """Custom script utilities for pidgin."""

    def get_expander_cell_for(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the cell that is expandable in the row with obj."""

        if not self._script.chat.isInBuddyList(obj):
            return None

        if AXUtilities.is_expandable(obj):
            return obj

        if not AXUtilities.is_table_cell(obj):
            return None

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_table_cell(parent):
            obj = parent

        candidate = AXObject.get_previous_sibling(obj)
        if AXUtilities.is_expandable(candidate):
            return candidate

        return None

    def child_nodes(self, obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Gets all of the objects that have RELATION_NODE_CHILD_OF pointing to this cell."""

        if not self._script.chat.isInBuddyList(obj):
            return super().child_nodes(obj)

        if not AXUtilities.is_expanded(obj):
            return []

        parent = AXTable.get_table(obj)
        if parent is None:
            return []

        nodes = []
        row, col = AXTable.get_cell_coordinates(obj)

        # increment the column because the expander cell is hidden.
        col += 1
        node_level = self.node_level(obj)

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        for i in range(row + 1, AXTable.get_row_count(parent, prefer_attribute=False)):
            cell = AXTable.get_cell_at(parent, i, col)
            node_cell = AXObject.get_previous_sibling(cell)
            targets = AXUtilities.get_is_node_child_of(node_cell)
            if not targets:
                continue

            node_of = targets[0]
            if obj == node_of:
                nodes.append(cell)
            elif self.node_level(node_of) <= node_level:
                break

        return nodes

    def node_level(self, obj: Atspi.Accessible) -> int:
        if not self._script.chat.isInBuddyList(obj):
            return super().node_level(obj)

        return super().node_level(AXObject.get_previous_sibling(obj))
