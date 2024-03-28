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

# For the "AXUtilities has no ... member"
# pylint: disable=E1101

"""Custom script for SeaMonkey."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

from orca import cmdnames
from orca import debug
from orca import focus_manager
from orca import input_event
from orca import input_event_manager
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import Gecko


class Script(Gecko.Script):

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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        table = AXTable.get_table(focus_manager.getManager().get_locus_of_focus())
        if table and not self.utilities.isTextDocumentTable(table):
            msg = "SEAMONKEY: Ignoring, table is not text-document table"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        super().onBusyChanged(event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
            return

        focus = focus_manager.getManager().get_locus_of_focus()
        if not AXUtilities.is_entry(focus) or not self.utilities.inDocumentContent():
            super().onFocus(event)
            return

        if AXUtilities.is_menu(event.source):
            msg = "SEAMONKEY: Non-document menu claimed focus from document entry"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            if input_event_manager.getManager().last_event_was_printable_key():
                msg = "SEAMONKEY: Ignoring, believed to be result of printable input"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return

        super().onFocus(event)

    def useFocusMode(self, obj, prevObj=None):
        if self.utilities.isEditableMessage(obj):
            tokens = ["SEAMONKEY: Using focus mode for editable message", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["SEAMONKEY:", obj, "is not an editable message."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return super().useFocusMode(obj, prevObj)

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.getManager().get_locus_of_focus()):
            return

        super().enableStickyBrowseMode(inputEvent, forceMessage)

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.getManager().get_locus_of_focus()):
            return

        super().enableStickyFocusMode(inputEvent, forceMessage)

    def togglePresentationMode(self, inputEvent, documentFrame=None):
        if self._inFocusMode \
           and self.utilities.isEditableMessage(focus_manager.getManager().get_locus_of_focus()):
            return

        super().togglePresentationMode(inputEvent, documentFrame)
