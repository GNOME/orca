# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Provides a custom script for gcalctool."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.scripts.toolkits.gtk as gtk
import orca.messages as messages

########################################################################
#                                                                      #
# The GCalcTool script class.                                          #
#                                                                      #
########################################################################

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.

        Arguments:
        - app: the application to create a script for.
        """

        gtk.Script.__init__(self, app)

        self._resultsDisplay = None
        self._statusLine = None

    def onWindowActivated(self, event):
        """Called whenever one of gcalctool's toplevel windows is activated.

        Arguments:
        - event: the window activated Event
        """

        if self._resultsDisplay and self._statusLine:
            gtk.Script.onWindowActivated(self, event)
            return

        obj = event.source
        role = obj.getRole()
        if role != pyatspi.ROLE_FRAME:
            gtk.Script.onWindowActivated(self, event)
            return

        isEditbar = lambda x: x and x.getRole() == pyatspi.ROLE_EDITBAR
        self._resultsDisplay = pyatspi.findDescendant(obj, isEditbar)
        if not self._resultsDisplay:
            self.presentMessage(messages.CALCULATOR_DISPLAY_NOT_FOUND)

        isStatusLine = lambda x: x and x.getRole() == pyatspi.ROLE_TEXT \
                       and not x.getState().contains(pyatspi.STATE_EDITABLE)
        self._statusLine = pyatspi.findDescendant(obj, isStatusLine)

        gtk.Script.onWindowActivated(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into gcalctool's text display.

        Arguments:
        - event: the text inserted Event
        """

        if self.utilities.isSameObject(event.source, self._statusLine):
            self.presentMessage(self.utilities.displayedText(self._statusLine))
            return

        gtk.Script.onTextInserted(self, event)
