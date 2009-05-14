# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Custom formatting for planner."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.formatting as defaultFormatting

scriptFormatting = {
    'speech': {
        pyatspi.ROLE_TOGGLE_BUTTON: {
            'unfocused': '(isDesiredFocusedItem and _("Display more options") + labelAndName + allTextSelection + roleName + toggleState + availability) or label'
            'focused': '(isDesiredFocusedItem and toggleState) or label'
            },
    }
}

class Formatting(defaultFormatting.Formatting):

    def __init__(self, script):
        defaultFormatting.Formatting.__init__(self, script)
        self.update(scriptFormatting)

