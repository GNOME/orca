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

# pylint: disable=duplicate-code

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
from orca.ax_table import AXTable
from orca.scripts.toolkits import Gecko


class Script(Gecko.Script):
    """Custom script for SeaMonkey."""

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()

        self.input_event_handlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.input_event_handlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.input_event_handlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyBrowseMode,
                cmdnames.SET_BROWSE_MODE_STICKY)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            msg = "SEAMONKEY: Ignoring, event source is content editable"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table and not self.utilities.isTextDocumentTable(table):
            msg = "SEAMONKEY: Ignoring, table is not text-document table"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        super().on_busy_changed(event)

    def useFocusMode(self, obj, prevObj=None):
        if self.utilities.isEditableMessage(obj):
            tokens = ["SEAMONKEY: Using focus mode for editable message", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["SEAMONKEY:", obj, "is not an editable message."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return super().useFocusMode(obj, prevObj)

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.get_manager().get_locus_of_focus()):
            return

        super().enableStickyBrowseMode(inputEvent, forceMessage)

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if self.utilities.isEditableMessage(focus_manager.get_manager().get_locus_of_focus()):
            return

        super().enableStickyFocusMode(inputEvent, forceMessage)

    def togglePresentationMode(self, inputEvent, documentFrame=None):
        if self._inFocusMode \
           and self.utilities.isEditableMessage(focus_manager.get_manager().get_locus_of_focus()):
            return

        super().togglePresentationMode(inputEvent, documentFrame)
