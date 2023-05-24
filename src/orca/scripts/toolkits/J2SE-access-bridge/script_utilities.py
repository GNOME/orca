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

import orca.script_utilities as script_utilities
from orca.ax_object import AXObject

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

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False):
        """Compares two objects to determine if they are functionally
        the same object. This is needed because some applications and
        toolkits kill and replace accessibles."""

        if (obj1 == obj2):
            return True
        elif (not obj1) or (not obj2):
            return False
        elif (AXObject.get_name(obj1) != AXObject.get_name(obj2)) \
              or (AXObject.get_child_count(obj1) != AXObject.get_child_count(obj2)):
            return False

        # This is to handle labels in trees. In some cases the default
        # script's method gives us false positives; other times false
        # negatives.
        #
        if AXObject.get_role(obj1) == AXObject.get_role(obj2) == Atspi.Role.LABEL:
            try:
                ext1 = obj1.queryComponent().getExtents(0)
                ext2 = obj2.queryComponent().getExtents(0)
            except:
                pass
            else:
                if ext1.x == ext2.x and ext1.y == ext2.y \
                   and ext1.width == ext2.width and ext1.height == ext2.height:
                    return True

        # In java applications, TRANSIENT state is missing for tree items
        # (fix for bug #352250)
        #
        try:
            parent1 = obj1
            parent2 = obj2
            while parent1 and parent2 and \
                    AXObject.get_role(parent1) == Atspi.Role.LABEL and \
                    AXObject.get_role(parent2) == Atspi.Role.LABEL:
                if AXObject.get_index_in_parent(parent1) != AXObject.get_index_in_parent(parent2):
                    return False
                parent1 = AXObject.get_parent(parent1)
                parent2 = AXObject.get_parent(parent2)
            if parent1 and parent2 and parent1 == parent2:
                return True
        except:
            pass

        return script_utilities.Utilities.isSameObject(self, obj1, obj2, comparePaths, ignoreNames)

    def nodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        newObj = obj
        if newObj and self.isZombie(newObj):
            newObj = self.findReplicant(self._script.lastDescendantChangedSource, obj)

        if not newObj:
            return script_utilities.Utilities.nodeLevel(self, obj)

        count = 0
        while newObj:
            state = AXObject.get_state_set(newObj)
            if state.contains(Atspi.StateType.EXPANDABLE) \
               or state.contains(Atspi.StateType.COLLAPSED):
                if state.contains(Atspi.StateType.VISIBLE):
                    count += 1
                newObj = AXObject.get_parent(newObj)
            else:
                break

        return count - 1
