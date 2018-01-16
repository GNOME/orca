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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013-2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import time

import orca.debug as debug
import orca.orca as orca
import orca.orca_state as orca_state
import orca.scripts.default as default

from .script_utilities import Utilities

class Script(default.Script):

    def __init__(self, app):
        default.Script.__init__(self, app)

    def getUtilities(self):
        return Utilities(self)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if self.utilities.isInOpenMenuBarMenu(newFocus):
            window = self.utilities.topLevelObject(newFocus)
            windowChanged = window and orca_state.activeWindow != window
            if windowChanged:
                orca_state.activeWindow = window
                self.windowActivateTime = time.time()

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not self.utilities.isTypeahead(orca_state.locusOfFocus):
            super().onActiveDescendantChanged(event)
            return

        msg = "GAIL: locusOfFocus believed to be typeahead. Presenting change."
        debug.println(debug.LEVEL_INFO, msg, True)
        self.presentObject(event.any_data)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # that fail to reliably emit object:state-changed:focused events.
        if self.utilities.isLayoutOnly(event.source):
            return

        if self.utilities.isTypeahead(orca_state.locusOfFocus) \
           and "Table" in pyatspi.listInterfaces(event.source) \
           and not event.source.getState().contains(pyatspi.STATE_FOCUSED):
            return

        ancestor = pyatspi.findAncestor(orca_state.locusOfFocus, lambda x: x == event.source)
        if not ancestor:
            orca.setLocusOfFocus(event, event.source)
            return

        if ancestor and "Table" in pyatspi.listInterfaces(ancestor):
            return

        isMenu = lambda x: x and x.getRole() == pyatspi.ROLE_MENU
        if isMenu(ancestor) and not pyatspi.findAncestor(ancestor, isMenu):
            return

        orca.setLocusOfFocus(event, event.source)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        isFocused = event.source.getState().contains(pyatspi.STATE_FOCUSED)
        role = event.source.getRole()

        if not isFocused and self.utilities.isTypeahead(orca_state.locusOfFocus):
            msg = "GAIL: locusOfFocus believed to be typeahead. Presenting change."
            debug.println(debug.LEVEL_INFO, msg, True)

            selectedChildren = self.utilities.selectedChildren(event.source)
            for child in selectedChildren:
                if not self.utilities.isLayoutOnly(child):
                    self.presentObject(child)
            return

        if role == pyatspi.ROLE_LAYERED_PANE \
           and self.utilities.selectedChildCount(event.source) > 1:
            return

        super().onSelectionChanged(event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        default.Script.onTextSelectionChanged(self, event)
