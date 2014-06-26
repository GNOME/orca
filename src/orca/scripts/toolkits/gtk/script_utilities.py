# Orca
#
# Copyright (C) 2013-2014 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2013-2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import re

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

    def isSearchEntry(self, obj, focusedOnly=False):
        # Another example of why we need subrole support in ATK and AT-SPI2.
        try:
            name = obj.name
            state = obj.getState()
        except:
            return False

        if not (name and state.contains(pyatspi.STATE_SINGLE_LINE)):
            return False

        if focusedOnly and not state.contains(pyatspi.STATE_FOCUSED):
            return False

        isIcon = lambda x: x and x.getRole() == pyatspi.ROLE_ICON
        icons = list(filter(isIcon, [x for x in obj]))
        if icons:
            return True

        return False

    def _isNonModalPopOver(self, obj):
        try:
            state = obj.getState()
        except:
            return False

        if state.contains(pyatspi.STATE_MODAL):
            return False

        try:
            relations = obj.getRelationSet()
        except:
            return False

        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_POPUP_FOR:
                return True

        return False

    def rgbFromString(self, attributeValue):
        regex = re.compile("rgb|[^\w,]", re.IGNORECASE)
        string = re.sub(regex, "", attributeValue)
        red, green, blue = string.split(",")

        return int(red) >> 8, int(green) >> 8, int(blue) >> 8
