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

import orca.debug as debug
import orca.script_utilities as script_utilities
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_utilities import AXUtilities


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        script_utilities.Utilities.__init__(self, script)
        self._isLayoutOnly = {}

    def clearCachedObjects(self):
        self._isLayoutOnly = {}

    def selectedChildren(self, obj):
        if AXObject.supports_selection(obj):
            return AXSelection.get_selected_children(obj)

        # This is a workaround for bgo#738705.
        if not AXUtilities.is_panel(obj):
            return []

        return AXUtilities.find_all_selected_objects(obj)

    def insertedText(self, event):
        if event.any_data:
            return event.any_data

        if event.detail1 == -1:
            msg = "GNOME SHELL: Broken text insertion event"
            debug.println(debug.LEVEL_INFO, msg, True)

            text = self.queryNonEmptyText(event.source)
            if text:
                string = text.getText(0, -1)
                if string:
                    tokens = ["HACK: Returning last char in '", string, "'"]
                    debug.printTokens(debug.LEVEL_INFO, tokens, True)
                    return string[-1]

            msg = "GNOME SHELL: Unable to correct broken text insertion event"
            debug.println(debug.LEVEL_INFO, msg, True)

        return ""

    def selectedText(self, obj):
        string, start, end = super().selectedText(obj)
        if -1 not in [start, end]:
            return string, start, end

        msg = "GNOME SHELL: Bogus selection range (%i, %i) for %s" % (start, end, obj)
        debug.println(debug.LEVEL_INFO, msg, True)

        text = self.queryNonEmptyText(obj)
        if text.getNSelections() > 0:
            string = text.getText(0, -1)
            start, end = 0, len(string)
            msg = "HACK: Returning '%s' (%i, %i) for %s" % (string, start, end, obj)
            debug.println(debug.LEVEL_INFO, msg, True)

        return string, start, end

    def unrelatedLabels(self, root, onlyShowing=True, minimumWords=3):
        if not root:
            return []

        def hasRole(x):
            return AXUtilities.is_dialog(x) \
                or AXUtilities.is_notification(x) \
                or AXUtilities.is_menu_item(x)

        if not hasRole(root) and AXObject.find_ancestor(root, hasRole) is None:
            tokens = ["GNOME SHELL: Not seeking unrelated labels for", root]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        return super().unrelatedLabels(root, onlyShowing, minimumWords)

    def isLayoutOnly(self, obj):
        rv = self._isLayoutOnly.get(hash(obj))
        if rv is not None:
            return rv

        rv = super().isLayoutOnly(obj)
        if not rv and AXUtilities.is_panel(obj) and AXObject.get_child_count(obj) == 1:
            child = AXObject.get_child(obj, 0)
            if self.displayedLabel(obj) == AXObject.get_name(child) \
               and not AXUtilities.is_label(child):
                rv = True
                tokens = ["GNOME SHELL:", obj, "is deemed to be layout only"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)

        self._isLayoutOnly[hash(obj)] = rv
        return rv


    def isBogusWindowFocusClaim(self, event):
        if event.type.startswith('object:state-changed:focused') and event.detail1 \
           and AXUtilities.is_window(event.source) \
           and not self.canBeActiveWindow(event.source):
            msg = "GNOME SHELL: Event is believed to be bogus window focus claim"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False
