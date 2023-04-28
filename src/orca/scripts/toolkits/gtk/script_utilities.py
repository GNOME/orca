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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
import re

import orca.debug as debug
import orca.script_utilities as script_utilities
import orca.orca_state as orca_state
from orca.ax_object import AXObject


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._isComboBoxWithToggleDescendant = {}
        self._isToggleDescendantOfComboBox = {}
        self._isTypeahead = {}
        self._isUselessPanel = {}

    def clearCachedObjects(self):
        self._isComboBoxWithToggleDescendant = {}
        self._isToggleDescendantOfComboBox = {}
        self._isTypeahead = {}
        self._isUselessPanel = {}

    def infoBar(self, root):
        isInfoBar = lambda x: x and x.getRole() == Atspi.Role.INFO_BAR
        return AXObject.find_descendant(root, isInfoBar)

    def isComboBoxWithToggleDescendant(self, obj):
        if not (obj and obj.getRole() == Atspi.Role.COMBO_BOX):
            return False

        rv = self._isComboBoxWithToggleDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isToggle = lambda x: x and x.getRole() == Atspi.Role.TOGGLE_BUTTON

        for child in obj:
            if child.getRole() != Atspi.Role.FILLER:
                continue

            toggle = AXObject.find_descendant(child, isToggle)
            rv = toggle is not None
            if toggle:
                self._isToggleDescendantOfComboBox[hash(toggle)] = True
                break

        self._isComboBoxWithToggleDescendant[hash(obj)] = rv
        return rv

    def isToggleDescendantOfComboBox(self, obj):
        if not (obj and obj.getRole() == Atspi.Role.TOGGLE_BUTTON):
            return False

        rv = self._isToggleDescendantOfComboBox.get(hash(obj))
        if rv is not None:
            return rv

        isComboBox = lambda x: x and x.getRole() == Atspi.Role.COMBO_BOX
        comboBox = AXObject.find_ancestor(obj, isComboBox)
        if comboBox:
            self._isComboBoxWithToggleDescendant[hash(comboBox)] = True

        rv = comboBox is not None
        self._isToggleDescendantOfComboBox[hash(obj)] = rv
        return rv

    def isTypeahead(self, obj):
        if not obj or self.isDead(obj):
            return False

        if obj.getRole() != Atspi.Role.TEXT:
            return False

        rv = self._isTypeahead.get(hash(obj))
        if rv is not None:
            return rv

        parent = obj.parent
        while parent and self.isLayoutOnly(parent):
            parent = parent.parent

        rv = parent and parent.getRole() == Atspi.Role.WINDOW
        self._isTypeahead[hash(obj)] = rv
        return rv

    def isSearchEntry(self, obj, focusedOnly=False):
        # Another example of why we need subrole support in ATK and AT-SPI2.
        try:
            name = obj.name
            state = obj.getState()
        except:
            return False

        if not (name and state.contains(Atspi.StateType.SINGLE_LINE)):
            return False

        if focusedOnly and not state.contains(Atspi.StateType.FOCUSED):
            return False

        isIcon = lambda x: x and x.getRole() == Atspi.Role.ICON
        icons = list(filter(isIcon, [x for x in obj]))
        if icons:
            return True

        return False

    def isEntryCompletionPopupItem(self, obj):
        if obj.getRole() == Atspi.Role.TABLE_CELL:
            isWindow = lambda x: x and x.getRole() == Atspi.Role.WINDOW
            window = AXObject.find_ancestor(obj, isWindow)
            if window:
                return True

        return False

    def isPopOver(self, obj):
        try:
            relations = obj.getRelationSet()
        except:
            return False

        for relation in relations:
            if relation.getRelationType() == Atspi.RelationType.POPUP_FOR:
                return True

        return False

    def isUselessPanel(self, obj):
        if not (obj and obj.getRole() == Atspi.Role.PANEL):
            return False

        rv = self._isUselessPanel.get(hash(obj))
        if rv is not None:
            return rv

        try:
            name = obj.name
            childCount = obj.childCount
        except:
            rv = True
        else:
            rv = not (name or childCount or AXObject.supports_text(obj))

        self._isUselessPanel[hash(obj)] = rv
        return rv

    def rgbFromString(self, attributeValue):
        regex = re.compile(r"rgb|[^\w,]", re.IGNORECASE)
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
        if event.source.getRole() != Atspi.Role.CANVAS:
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

    def _adjustPointForObj(self, obj, x, y, coordType):
        try:
            singleLine = obj.getState().contains(Atspi.StateType.SINGLE_LINE)
        except:
            singleLine = False

        if not singleLine or not AXObject.supports_editable_text(obj):
            return x, y

        text = self.queryNonEmptyText(obj)
        if not text:
            return x, y

        objBox = obj.queryComponent().getExtents(coordType)
        stringBox = text.getRangeExtents(0, text.characterCount, coordType)
        if self.intersection(objBox, stringBox) != (0, 0, 0, 0):
            return x, y

        msg = "ERROR: text bounds %s not in obj bounds %s" % (stringBox, objBox)
        debug.println(debug.LEVEL_INFO, msg, True)

        # This is where the string starts; not the widget.
        boxX, boxY = stringBox[0], stringBox[1]

        # Window Coordinates should be relative to the window; not the widget.
        # But broken interface is broken, and this appears to be what is being
        # exposed. And we need this information to get the widget's x and y.
        charExtents = text.getCharacterExtents(0, Atspi.CoordType.WINDOW)
        if 0 < charExtents[0] < charExtents[2]:
            boxX -= charExtents[0]
        if 0 < charExtents[1] < charExtents[3]:
            boxY -= charExtents[1]

        # The point relative to the widget:
        relX = x - objBox[0]
        relY = y - objBox[1]

        # The point relative to our adjusted bounding box:
        newX = boxX + relX
        newY = boxY + relY

        msg = "INFO: Adjusted (%i, %i) to (%i, %i)" % (x, y, newX, newY)
        debug.println(debug.LEVEL_INFO, msg, True)
        return newX, newY
