# Orca
#
# Copyright (C) 2014 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import orca.script_utilities as script_utilities

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        script_utilities.Utilities.__init__(self, script)

    def selectedChildren(self, obj):
        try:
            selection = obj.querySelection()
        except:
            # This is a workaround for bgo#738705.
            if obj.getRole() != pyatspi.ROLE_PANEL:
                return []

            isSelected = lambda x: x and x.getState().contains(pyatspi.STATE_SELECTED)
            children = pyatspi.findAllDescendants(obj, isSelected)
        else:
            children = []
            for x in range(selection.nSelectedChildren):
                children.append(selection.getSelectedChild(x))

        return children
