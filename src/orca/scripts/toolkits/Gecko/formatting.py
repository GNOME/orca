# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Custom formatting for Gecko."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import copy
import pyatspi

import orca.formatting

# pylint: disable-msg=C0301

formatting = {
    'speech': {
        'suffix': {
            'focused': '[]',
            'unfocused': 'newNodeLevel + unselectedCell + clickable + hasLongDesc + ' + orca.formatting.TUTORIAL + ' + description ',
            'basicWhereAmI': orca.formatting.TUTORIAL + ' + clickable + hasLongDesc + description + liveRegionDescription',
            'detailedWhereAmI' : '[]'
            },
        'default': {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + ' + orca.formatting.MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + roleName',
            'detailedWhereAmI' : 'pageSummary'
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': 'expandedEOCs or (labelAndName + unrelatedLabels)'
            },
        pyatspi.ROLE_DIALOG: {
            'unfocused': 'expandedEOCs or (labelAndName + unrelatedLabels)'
            },
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'unfocused': 'name + roleName'
            },
        # [[[TODO: JD - We should decide if we want to provide
        # information about the table dimensions, whether or not
        # this is a layout table versus a data table, etc.  For now,
        # however, if it's in HTML content let's ignore it so that
        # SayAll by sentence works. :-) ]]]
        #
        pyatspi.ROLE_TABLE: {
            'unfocused': '[]'
            },
    },
}

class Formatting(orca.formatting.Formatting):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
