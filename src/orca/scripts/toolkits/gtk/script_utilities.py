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
        if not obj or AXObject.is_dead(obj):
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

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False,
                     ignoreDescriptions=True):
        return super().isSameObject(obj1, obj2, comparePaths, ignoreNames, False)

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

    def eventIsCanvasNoise(self, event):
        if not AXUtilities.is_canvas(event.source):
            return False

        if not self.topLevelObjectIsActiveWindow(event.source):
            msg = "GTK: Event is believed to be canvas noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False
