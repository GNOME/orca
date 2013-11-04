# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Custom script for gnome-search-tool"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import time
from gi.repository import GLib

import orca.messages as messages
import orca.scripts.default as default

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The gnome-search-tool script class.                                  #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self.fileTable = None
        self.searching = False
        self.startTime = None
        self.searchInterval = 5.0

    def _speakSearching(self):
        """If we are still searching, let the user know. Then start another
        timer to go off again and repeat this process.
        """

        if not self.searching:
            return False

        currentTime = time.time()
        if not self.startTime or \
           (currentTime > (self.startTime + self.searchInterval)):
            self.presentMessage(messages.SEARCHING)
            self.startTime = time.time()

        return True

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        obj = event.source
        if obj.getRole() != pyatspi.ROLE_PUSH_BUTTON \
           or not obj.getState().contains(pyatspi.STATE_VISIBLE):
            return default.Script.onShowingChanged(self, event)

        # Translators: the "Stop" string must match what gnome-search-tool
        # is using.  We hate keying off stuff like this, but we're forced
        # to do so in this case.
        if obj.name == _("Stop"):
            self.searching = True
            if not self.fileTable:
                frame = self.utilities.topLevelObject(obj)
                allTables = self.utilities.descendantsWithRole(
                    frame, pyatspi.ROLE_TABLE)
                self.fileTable = allTables[0]

            GLib.idle_add(self._speakSearching)
            return

        # Translators: the "Find" string must match what gnome-search-tool
        # is using.  We hate keying off stuff like this, but we're forced
        # to do so in this case.
        if obj.name == _("Find") and self.searching:
            self.searching = False
            self.presentMessage(messages.SEARCH_COMPLETE)
            if self.fileTable.getState().contains(pyatspi.STATE_SENSITIVE):
                try:
                    fileCount = self.fileTable.queryTable().nRows
                    self.presentMessage(messages.filesFound(fileCount))
                except NotImplementedError:
                    self.presentMessage(messages.FILES_NOT_FOUND)
            return

        default.Script.onShowingChanged(self, event)
