# Orca
#
# Copyright 2019 Igalia, S.L.
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

"""Custom script for basic switchers like Metacity."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2019 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import orca
from orca import orca_state
from orca.scripts import default

from .script_utilities import Utilities


class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""

        super().__init__(app)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def forceScriptActivation(self, event):
        """Allows scripts to insist that they should become active."""

        if self.utilities.isSwitcherSelectionChangeEventType(event):
            return True

        return super().forceScriptActivation(event)

    def _handleSwitcherEvent(self, event):
        """Presents the currently selected item, if appropriate."""

        if not self.utilities.isSwitcherContainer(event.source):
            msg = "SWITCHER: Event is not from switcher container"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.isSwitcherSelectionChangeEventType(event):
            msg = "SWITCHER: Not treating event as selection change."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "SWITCHER: Treating event as selection change"
        debug.println(debug.LEVEL_INFO, msg, True)

        self.presentationInterrupt()
        orca_state.activeWindow = self.utilities.topLevelObject(event.source)
        orca.setLocusOfFocus(event, event.source, False)
        self.presentMessage(self.utilities.getSelectionName(event.source), force=True)
        return True

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onFocusedChanged(event)

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self._handleSwitcherEvent(event):
            return

        super().onNameChanged(event)

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onSelectedChanged(event)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onSelectionChanged(event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onShowingChanged(event)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onCaretMoved(event)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onTextDeleted(event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().onTextInserted(event)
