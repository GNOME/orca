# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom script for rhythmbox."""

__id__ = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.braillegenerator as braillegenerator

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Overrides _getBrailleRegionsForTableCell to correctly handle 
    the table cells in the Library table.
    """

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)

    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a single table cell

        Arguments:
        - obj: the table

        Returns a list where the first element is a list of Regions to 
        display and the second element is the Region which should get focus.
        """

        # Check to see if this is a table cell from the Library table.
        # If so, it'll have five children and we are interested in the
        # penultimate one. See bug #512639 for more details.
        #
        if obj.childCount == 5:
            obj = obj[3]

        return braillegenerator.BrailleGenerator.\
                    _getBrailleRegionsForTableCell(self, obj)
