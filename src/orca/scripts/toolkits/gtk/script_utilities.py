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
from orca.ax_utilities import AXUtilities


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._isComboBoxWithToggleDescendant = {}
        self._isToggleDescendantOfComboBox = {}
        self._isTypeahead = {}
        self._isUselessPanel = {}
        self._isLayoutOnly = {}

    def clearCachedObjects(self):
        self._isComboBoxWithToggleDescendant = {}
        self._isToggleDescendantOfComboBox = {}
        self._isTypeahead = {}
        self._isUselessPanel = {}
        self._isLayoutOnly = {}

    def infoBar(self, root):
        return AXObject.find_descendant(root, AXUtilities.is_info_bar)

    def isComboBoxWithToggleDescendant(self, obj):
        if not AXUtilities.is_combo_box(obj):
            return False

        rv = self._isComboBoxWithToggleDescendant.get(hash(obj))
        if rv is not None:
            return rv

        for child in AXObject.iter_children(obj):
            if not AXUtilities.is_filler(child):
                continue

            toggle = AXObject.find_descendant(child, AXUtilities.is_toggle_button)
            rv = toggle is not None
            if toggle:
                self._isToggleDescendantOfComboBox[hash(toggle)] = True
                break

        self._isComboBoxWithToggleDescendant[hash(obj)] = rv
        return rv

    def isLayoutOnly(self, obj):
        rv = self._isLayoutOnly.get(hash(obj))
        if rv is not None:
            if rv:
                tokens = ["GTK:", obj, "is deemed to be layout only"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return rv

        rv = super().isLayoutOnly(obj)
        self._isLayoutOnly[hash(obj)] = rv
        return rv

    def isToggleDescendantOfComboBox(self, obj):
        if not AXUtilities.is_toggle_button(obj):
            return False

        rv = self._isToggleDescendantOfComboBox.get(hash(obj))
        if rv is not None:
            return rv

        comboBox = AXObject.find_ancestor(obj, AXUtilities.is_combo_box)
        if comboBox:
            self._isComboBoxWithToggleDescendant[hash(comboBox)] = True

        rv = comboBox is not None
        self._isToggleDescendantOfComboBox[hash(obj)] = rv
        return rv

    def isTypeahead(self, obj):
        if not obj or self.isDead(obj):
            return False

        if not AXUtilities.is_text(obj):
            return False

        rv = self._isTypeahead.get(hash(obj))
        if rv is not None:
            return rv

        parent = AXObject.get_parent(obj)
        while parent and self.isLayoutOnly(parent):
            parent = AXObject.get_parent(parent)

        rv = AXUtilities.is_window(parent)
        self._isTypeahead[hash(obj)] = rv
        return rv

    def isSearchEntry(self, obj, focusedOnly=False):
        # Another example of why we need subrole support in ATK and AT-SPI2.
        if not (AXObject.get_name(obj) and AXUtilities.is_single_line(obj)):
            return False

        if focusedOnly and not AXUtilities.is_focused(obj):
            return False

        icons = [x for x in AXObject.iter_children(obj, AXUtilities.is_icon)]
        if icons:
            return True

        return False

    def isEntryCompletionPopupItem(self, obj):
        return AXUtilities.is_table_cell(obj) \
            and AXObject.find_ancestor(obj, AXUtilities.is_window) is not None

    def isPopOver(self, obj):
        return AXObject.has_relation(obj, Atspi.RelationType.POPUP_FOR)

    def isUselessPanel(self, obj):
        if not AXUtilities.is_panel(obj):
            return False

        rv = self._isUselessPanel.get(hash(obj))
        if rv is not None:
            return rv

        childCount = AXObject.get_child_count(obj)
        name = AXObject.get_name(obj)
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
        if rv and self.isLink(obj) and AXObject.get_index_in_parent(obj) == -1:
            msg = f'INFO: Hacking around bug 759736 for {obj}'
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return rv

    def eventIsCanvasNoise(self, event):
        if not AXUtilities.is_canvas(event.source):
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
        if not AXUtilities.is_single_line(obj) \
           or not AXObject.supports_editable_text(obj):
            return x, y

        text = self.queryNonEmptyText(obj)
        if not text:
            return x, y

        objBox = obj.queryComponent().getExtents(coordType)
        stringBox = text.getRangeExtents(0, text.characterCount, coordType)
        if self.intersection(objBox, stringBox) != (0, 0, 0, 0):
            return x, y

        tokens = ["ERROR: text bounds", stringBox, "not in obj bounds", objBox]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

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
