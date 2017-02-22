# Orca
#
# Copyright 2016 Igalia, S.L.
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

"""Custom script for SeaMonkey."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import cmdnames
from orca import debug
from orca import input_event
from orca import orca_state
from orca.scripts.toolkits import Gecko


class Script(Gecko.Script):

    def __init__(self, app):
        super().__init__(app)

    def setupInputEventHandlers(self):
        super().setupInputEventHandlers()

        self.inputEventHandlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.inputEventHandlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.inputEventHandlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyBrowseMode,
                cmdnames.SET_BROWSE_MODE_STICKY)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            msg = "SEAMONKEY: Ignoring, event source is content editable"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        table = self.utilities.getTable(orca_state.locusOfFocus)
        if table and not self.utilities.isTextDocumentTable(table):
            msg = "SEAMONKEY: Ignoring, locusOfFocus is %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().onBusyChanged(event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
            return

        try:
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            focusRole = None

        if focusRole != pyatspi.ROLE_ENTRY or not self.utilities.inDocumentContent():
            super().onFocus(event)
            return

        if event.source.getRole() == pyatspi.ROLE_MENU:
            msg = "SEAMONKEY: Non-document menu claimed focus from document entry"
            debug.println(debug.LEVEL_INFO, msg, True)

            if self.utilities.lastInputEventWasPrintableKey():
                msg = "SEAMONKEY: Ignoring, believed to be result of printable input"
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        super().onFocus(event)

    def useFocusMode(self, obj):
        if self.utilities.isEditableMessage(obj):
            msg = "SEAMONKEY: Using focus mode for editable message %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "SEAMONKEY: %s is not an editable message." % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return super().useFocusMode(obj)

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(orca_state.locusOfFocus):
            return

        super().enableStickyBrowseMode(inputEvent, forceMessage)

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(orca_state.locusOfFocus):
            return

        super().enableStickyFocusMode(inputEvent, forceMessage)

    def togglePresentationMode(self, inputEvent):
        if self._inFocusMode \
           and self.utilities.isEditableMessage(orca_state.locusOfFocus):
            return

        super().togglePresentationMode(inputEvent)

    def useStructuralNavigationModel(self):
        if self.utilities.isEditableMessage(orca_state.locusOfFocus):
            return False

        return super().useStructuralNavigationModel()
