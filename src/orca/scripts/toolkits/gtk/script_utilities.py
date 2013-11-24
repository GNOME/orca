# Orca
#
# Copyright (C) 2013 Igalia, S.L.
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

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.script_utilities as script_utilities

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        script_utilities.Utilities.__init__(self, script)

    def displayedText(self, obj):
        displayedText = script_utilities.Utilities.displayedText(self, obj)
        if displayedText:
            return displayedText

        # Present GtkLabel children inside a GtkListBox row.
        if obj.parent and obj.parent.getRole() == pyatspi.ROLE_LIST_BOX:
            labels = self.unrelatedLabels(obj, onlyShowing=False)
            displayedText = " ".join(map(self.displayedText, labels))

        self._script.generatorCache[self.DISPLAYED_TEXT][obj] = displayedText
        return displayedText
