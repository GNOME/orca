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

import orca.debug as debug
import orca.script_utilities as script_utilities
import orca.orca_state as orca_state

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._isComboBoxWithToggleDescendant = {}
        self._isToggleDescendantOfComboBox = {}

    def clearCachedObjects(self):
        self._isComboBoxWithToggleDescendant = {}
        self._isToggleDescendantOfComboBox = {}

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

    def isComboBoxWithToggleDescendant(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_COMBO_BOX):
            return False

        rv = self._isComboBoxWithToggleDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isToggle = lambda x: x and x.getRole() == pyatspi.ROLE_TOGGLE_BUTTON

        for child in obj:
            if child.getRole() != pyatspi.ROLE_FILLER:
                continue

            toggle = pyatspi.findDescendant(child, isToggle)
            rv = toggle is not None
            if toggle:
                self._isToggleDescendantOfComboBox[hash(toggle)] = True
                break

        self._isComboBoxWithToggleDescendant[hash(obj)] = rv
        return rv

    def isToggleDescendantOfComboBox(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TOGGLE_BUTTON):
            return False

        rv = self._isToggleDescendantOfComboBox.get(hash(obj))
        if rv is not None:
            return rv

        isComboBox = lambda x: x and x.getRole() == pyatspi.ROLE_COMBO_BOX
        comboBox = pyatspi.findAncestor(obj, isComboBox)
        if comboBox:
            self._isComboBoxWithToggleDescendant[hash(comboBox)] = True

        rv = comboBox is not None
        self._isToggleDescendantOfComboBox[hash(obj)] = rv
        return rv

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

    def isEntryCompletionPopupItem(self, obj):
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            isWindow = lambda x: x and x.getRole() == pyatspi.ROLE_WINDOW
            window = pyatspi.findAncestor(obj, isWindow)
            if window:
                return True

        return False

    def isPopOver(self, obj):
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

    def isZombie(self, obj):
        rv = super().isZombie(obj)
        if rv and self.isLink(obj) and obj.getIndexInParent() == -1:
            msg = 'INFO: Hacking around bug 759736 for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return rv

    def eventIsCanvasNoise(self, event):
        if event.source.getRole() != pyatspi.ROLE_CANVAS:
            return False

        if not orca_state.activeWindow:
            msg = 'INFO: No active window'
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        topLevel = self.topLevelObject(event.source)
        if not self.isSameObject(topLevel, orca_state.activeWindow):
            msg = 'INFO: Event is believed to be canvas noise'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False
