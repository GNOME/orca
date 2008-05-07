# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom script for gnome-search-tool"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.debug as debug
import orca.default as default
import orca.speech as speech

from orca.orca_i18n import _        # for gettext support
from orca.orca_i18n import ngettext # for gettext support

import pyatspi
import time
import gobject
gobject.threads_init()


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

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # The table of files found.
        #
        self.fileTable = None

        # Set to true if we are doing a search.
        #
        self.searching = False

        # Time value using by the interval timer.
        #
        self.startTime = None

        # Interval in seconds, between utterances of "Searching" when a
        # search is in progress.
        #
        self.searchInterval = 5.0

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:state-changed:showing"]           = \
            self.onStateChanged

        return listeners

    def _speakSearching(self):
        """If we are still searching, let the user know. Then start another
        timer to go off again and repeat this process.
        """

        if not self.searching:
            return False

        currentTime = time.time()
        if not self.startTime or \
           (currentTime > (self.startTime + self.searchInterval)):
            speech.speak(_("Searching."))
            self.startTime = time.time()

        return True

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               debug.getAccessibleDetails(event.source))

        # self.printAncestry(event.source)

        rolesList = [pyatspi.ROLE_PUSH_BUTTON, \
                    pyatspi.ROLE_FILLER, \
                    pyatspi.ROLE_FILLER, \
                    pyatspi.ROLE_FILLER, \
                    pyatspi.ROLE_FRAME, \
                    pyatspi.ROLE_APPLICATION]
        visible = event.source.getState().contains(pyatspi.STATE_VISIBLE)

        # Check to see if we have just had an "object:state-changed:showing"
        # event for the Stop button. If the name is "Stop", and one of its
        # states is VISIBLE, that means we have started a search. As the
        # search progresses, regularly inform the user of this by speaking
        # "Searching" (assuming the search tool has focus).
        #
        # Translators: the "Stop" string must match what gnome-search-tool
        # is using.  We hate keying off stuff like this, but we're forced
        # to do so in this case.
        #
        if self.isDesiredFocusedItem(event.source, rolesList) and \
           event.source.name == _("Stop") and visible:
            debug.println(self.debugLevel,
                          "gnome-search-tool.onNameChanged - " \
                          + "search started.")

            self.searching = True

            # If we don't already have a handle to the table containing the
            # list of files found, then get it now.
            #
            if not self.fileTable:
                frame = self.getTopLevel(event.source)
                allTables = self.findByRole(frame, pyatspi.ROLE_TABLE)
                self.fileTable = allTables[0]

            gobject.idle_add(self._speakSearching)

        # Check to see if we have just had an "object:state-changed:showing"
        # event for the Find button. If the name is "Find", and one of its
        # states is VISIBLE and we are currently searching, that means we
        # have just stopped a search. Inform the user that the search is
        # complete and tell them how many files were found.
        #
        # Translators: the "Find" string must match what gnome-search-tool
        # is using.  We hate keying off stuff like this, but we're forced
        # to do so in this case.
        #
        if self.isDesiredFocusedItem(event.source, rolesList) and \
           event.source.name == _("Find") and visible and self.searching:
            debug.println(self.debugLevel,
                          "gnome-search-tool.onNameChanged - " \
                          + "search completed.")

            self.searching = False
            speech.speak(_("Search complete."))
            sensitive = self.fileTable.getState().contains( \
                                                pyatspi.STATE_SENSITIVE)
            if sensitive:
                try:
                    fileCount = self.fileTable.queryTable().nRows
                except NotImplementedError:
                    fileCount = 0
                noFilesString = ngettext("%d file found",
                                         "%d files found",
                                         fileCount) % fileCount
                speech.speak(noFilesString)
            else:
                speech.speak(_("No files found."))

        # Pass the event onto the parent class to be handled in the default way.
        #
        default.Script.onStateChanged(self, event)
