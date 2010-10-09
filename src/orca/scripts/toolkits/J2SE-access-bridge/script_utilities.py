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

import pyatspi

import orca.script_utilities as script_utilities

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

    def isSameObject(self, obj1, obj2):
        """Compares two objects to determine if they are functionally
        the same object. This is needed because some applications and
        toolkits kill and replace accessibles."""

        if (obj1 == obj2):
            return True
        elif (not obj1) or (not obj2):
            return False
        elif (obj1.name != obj2.name) or (obj1.childCount != obj2.childCount):
            return False

        # This is to handle labels in trees. In some cases the default
        # script's method gives us false positives; other times false
        # negatives.
        #
        if obj1.getRole() == obj2.getRole() == pyatspi.ROLE_LABEL:
            try:
                ext1 = obj1.queryComponent().getExtents(0)
                ext2 = obj2.queryComponent().getExtents(0)
            except:
                pass
            else:
                if ext1.x == ext2.x and ext1.y == ext2.y \
                   and ext1.width == ext2.width and ext1.height == ext2.height:
                    return True

        return script_utilities.Utilities.isSameObject(self, obj1, obj2)

    def nodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        newObj = self.validObj(self._script.lastDescendantChangedSource, obj)
        if not newObj:
            return script_utilities.Utilities.nodeLevel(self, obj)

        count = 0
        while newObj:
            state = newObj.getState()
            if state.contains(pyatspi.STATE_EXPANDABLE) \
               or state.contains(pyatspi.STATE_COLLAPSED):
                if state.contains(pyatspi.STATE_VISIBLE):
                    count += 1
                newObj = newObj.parent
            else:
                break

        return count - 1

    def validObj(self, rootObj, obj, onlyShowing=True):
        """Attempts to convert an older copy of an accessible into the
        current, active version. We need to do this in order to ascend
        the hierarchy.

        Arguments:
        - rootObj: the top-most ancestor of interest
        - obj: the old object we're attempting to replace
        - onlyShowing: whether or not we should limit matches to those
          which have STATE_SHOWING

         Returns an accessible replacement for obj if one can be found;
         otherwise, None.
         """

        if not (obj and rootObj):
            return None

        items = self.descendantsWithRole(rootObj, obj.getRole(), onlyShowing)
        for item in items:
            if item.name == obj.name \
               and self.isSameObject(item, obj):
                return item

        return None

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
