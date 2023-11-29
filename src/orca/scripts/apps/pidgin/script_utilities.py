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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.debug as debug
import orca.scripts.toolkits.gtk as gtk
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities

class Utilities(gtk.Utilities):

    def getExpanderCellFor(self, obj):
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

    def childNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell. Overridden here because the object
        which contains the relation is in a hidden column and thus doesn't
        have a column number.

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

        if not self._script.chat.isInBuddyList(obj):
            return super().childNodes(obj)

        if not AXUtilities.is_expanded(obj):
            return []

        parent = AXTable.get_table(obj)
        if parent is None:
            return []

        nodes = []
        row, col = AXTable.get_cell_coordinates(obj)

        # increment the column because the expander cell is hidden.
        col += 1
        nodeLevel = self.nodeLevel(obj)

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        for i in range(row + 1, AXTable.get_row_count(parent, prefer_attribute=False)):
            cell = AXTable.get_cell_at(parent, i, col)
            nodeCell = AXObject.get_previous_sibling(cell)
            relation = AXObject.get_relation(nodeCell, Atspi.RelationType.NODE_CHILD_OF)
            if not relation:
                continue

            nodeOf = relation.getTarget(0)
            if self.isSameObject(obj, nodeOf):
                nodes.append(cell)
            elif self.nodeLevel(nodeOf) <= nodeLevel:
                break

        return nodes

    def nodeLevel(self, obj):
        if not self._script.chat.isInBuddyList(obj):
            return super().nodeLevel(obj)

        return super().nodeLevel(AXObject.get_previous_sibling(obj))

    def isZombie(self, obj):
        if not super().isZombie(obj):
            return False

        if AXObject.get_role(obj) != Atspi.Role.TOGGLE_BUTTON:
            return True

        tokens = ["PIDGIN: Hacking around broken index in parent for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return AXObject.get_index_in_parent(obj) != -1
