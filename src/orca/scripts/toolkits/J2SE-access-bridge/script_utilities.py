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

from orca import script_utilities
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

class Utilities(script_utilities.Utilities):

    def nodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        newObj = obj
        if newObj and not AXObject.is_valid(newObj):
            newObj = self.findReplicant(AXObject.get_parent(obj), obj)

        if not newObj:
            return script_utilities.Utilities.nodeLevel(self, obj)

        count = 0
        while newObj:
            if AXUtilities.is_expandable(newObj) or AXUtilities.is_collapsed(newObj):
                if AXUtilities.is_visible(newObj):
                    count += 1
                newObj = AXObject.get_parent(newObj)
            else:
                break

        return count - 1
