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
import orca.script_utilities as script_utilities
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def childNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell. Overridden here because the object
        which contains the relation is in a hidden column and thus doesn't
        have a column number (necessary for using getAccessibleAt()).

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

        if not self._script.chat.isInBuddyList(obj):
            return script_utilities.Utilities.childNodes(self, obj)

        parent = AXObject.get_parent(obj)
        try:
            table = parent.queryTable()
        except Exception:
            return []
        else:
            if not AXUtilities.is_expanded(obj):
                return []

        nodes = []
        index = self.cellIndex(obj)
        row = table.getRowAtIndex(index)
        col = table.getColumnAtIndex(index + 1)
        nodeLevel = self.nodeLevel(obj)

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        for i in range(row+1, table.nRows):
            cell = table.getAccessibleAt(i, col)
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
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned. Overridden
        here because the accessible we need is in a hidden column.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return -1

        if not self._script.chat.isInBuddyList(obj):
            return script_utilities.Utilities.nodeLevel(self, obj)

        obj = AXObject.get_previous_sibling(obj)
        parent = AXObject.get_parent(obj)
        try:
            parent.queryTable()
        except Exception:
            return -1

        nodes = []
        node = obj
        done = False
        while not done:
            relation = AXObject.get_relation(node, Atspi.RelationType.NODE_CHILD_OF)
            node = None
            if relation:
                node = relation.get_target(0)

            # We want to avoid situations where something gives us an
            # infinite cycle of nodes.  Bon Echo has been seen to do
            # this (see bug 351847).
            #
            if (len(nodes) > 100) or nodes.count(node):
                debug.println(debug.LEVEL_WARNING,
                              "pidgin.nodeLevel detected a cycle!!!")
                done = True
            elif node:
                nodes.append(node)
                debug.println(debug.LEVEL_FINEST,
                              f"pidgin.nodeLevel {len(nodes)}")
            else:
                done = True

        return len(nodes) - 1

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################



    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################

    def isZombie(self, obj):
        if not super().isZombie(obj):
            return False

        if AXObject.get_role(obj) != Atspi.Role.TOGGLE_BUTTON:
            return True

        msg = f'INFO: Hacking around broken index in parent for {obj}'
        debug.println(debug.LEVEL_INFO, msg, True)
        return AXObject.get_index_in_parent(obj) != -1
