# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
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

"""Custom formatting for evolution."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

# pylint: disable-msg=C0301

import copy

import orca.formatting

formatting = {
    'speech': {
        'ALTERNATIVE_REAL_ROLE_TABLE_CELL': {
            # the real cell information
            # note that pyatspi.ROLE_TABLE_CELL is used to work out if we need to
            # read a whole row. It calls REAL_ROLE_TABLE_CELL internally.
            #
            'focused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + (expandableState and expandableState ) + required',
            'unfocused': '(tableCell2ChildLabel + tableCell2ChildToggle) or cellCheckedState + (realActiveDescendantDisplayedText or imageDescription + image) + (expandableState and expandableState ) + required',
            },
    }
}

class Formatting(orca.formatting.Formatting):
    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
