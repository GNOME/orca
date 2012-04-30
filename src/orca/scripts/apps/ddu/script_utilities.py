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

    def _isBogusCellText(self, cell, string):
        """Attempts to identify text in a cell which the DDU is exposing
        to us, but which is not actually displayed to the user.

        Arguments:
        - cell: The cell we wish to examine.
        - string: The string we're considering for that cell

        Returns True if we think the string should not be presented to
        the user.
        """

        if string.isdigit() and self.cellIndex(cell) == 2 \
           and cell.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            try:
                table = cell.parent.parent.queryTable()
            except:
                pass
            else:
                index = self.cellIndex(cell.parent)
                col = table.getColumnAtIndex(index)
                if col == 0:
                    return True

        return False

    def realActiveDescendant(self, obj):
        """Given an object that should be a child of an object that
        manages its descendants, return the child that is the real
        active descendant carrying useful information.

        Arguments:
        - obj: an object that should be a child of an object that
        manages its descendants.
        """

        try:
            return self._script.\
                generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]
        except:
            if self.REAL_ACTIVE_DESCENDANT not in self._script.\
                    generatorCache:
                self._script.generatorCache[self.REAL_ACTIVE_DESCENDANT] = {}
            activeDescendant = None

        # If obj is a table cell and all of it's children are table cells
        # (probably cell renderers), then return the first child which has
        # a non zero length text string. If no such object is found, just
        # fall through and use the default approach below. See bug #376791
        # for more details.
        #
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL and obj.childCount:
            nonTableCellFound = False
            for child in obj:
                if child.getRole() != pyatspi.ROLE_TABLE_CELL:
                    nonTableCellFound = True
            if not nonTableCellFound:
                for child in obj:
                    string = self.substring(child, 0, -1)
                    # Here is where this method differs from the default
                    # scripts: We break once we find text, and we hack
                    # out the number in the first column.
                    #
                    if string:
                        if not self._isBogusCellText(child, string):
                            activeDescendant = child
                        break

        self._script.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj] = \
            activeDescendant or obj
        return self._script.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]

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
