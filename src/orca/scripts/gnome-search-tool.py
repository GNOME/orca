# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Custom script for gnome-search-tool"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.debug as debug
import orca.default as default
import orca.atspi as atspi
import orca.rolenames as rolenames
import orca.orca as orca
import orca.braille as braille
import orca.speech as speech
import orca.settings as settings
import orca.util as util

from orca.orca_i18n import _ # for gettext support

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
        self.searchInterval = 3.0

    def _speakSearching(self):
        """If we are still searching, let the user know. Then start another
        timer to go off again and repeat this process.
        """

        if self.searching == False:
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
                               event.source.toString())

        # util.printAncestry(event.source)

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_FILLER, \
                    rolenames.ROLE_FRAME, \
                    rolenames.ROLE_APPLICATION]
        visible = event.source.state.count( \
                               atspi.Accessibility.STATE_VISIBLE)

        # Check to see if we have just had an "object:state-changed:showing"
        # event for the Stop button. If the name is "Stop", and one of its
        # states is VISIBLE, that means we have started a search. As the
        # search progresses, regularly inform the user of this by speaking
        # "Searching" (assuming the search tool has focus).
        #
        if util.isDesiredFocusedItem(event.source, rolesList) and \
           event.source.name == _("Stop") and visible:
            debug.println(self.debugLevel,
                          "gnome-search-tool.onNameChanged - " \
                          + "search started.")

            self.searching = True

            # If we don't already have a handle to the table containing the
            # list of files found, then get it now.
            #
            if not self.fileTable:
                frame = util.getTopLevel(event.source)
                allTables = util.findByRole(frame, rolenames.ROLE_TABLE)
                self.fileTable = allTables[0]

            gobject.idle_add(self._speakSearching)

        # Check to see if we have just had an "object:state-changed:showing"
        # event for the Find button. If the name is "Find", and one of its
        # states is VISIBLE and we are currently searching, that means we
        # have just stopped a search. Inform the user that the search is
        # complete and tell them how many files were found.
        #
        if util.isDesiredFocusedItem(event.source, rolesList) and \
           event.source.name == _("Find") and visible and self.searching:
            debug.println(self.debugLevel,
                          "gnome-search-tool.onNameChanged - " \
                          + "search completed.")

            self.searching = False
            speech.speak(_("Search complete."))
            sensitive = self.fileTable.state.count( \
                               atspi.Accessibility.STATE_SENSITIVE)
            if sensitive:
                fileCount = self.fileTable.table.nRows
                speech.speak(str(fileCount) + _(" files found"))
            else:
                speech.speak(_("No files found."))

        # Pass the event onto the parent class to be handled in the default way.
        #
        default.Script.onStateChanged(self, event)
