# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

""" Custom script for gnome-panel
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.default as default
import orca.debug as debug
import orca.braille as braille
import orca.speech as speech
import pyatspi

########################################################################
#                                                                      #
# The gnome-panel script class.                                        #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for gnome-panel

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        self._debug("__init__")
        default.Script.__init__(self, app)

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "gnome-panel.py: "+msg)

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)
        
        listeners["object:state-changed:focused"]           = \
            self.onStateChanged
        listeners["object:state-changed:showing"]           = \
            self.onStateChanged
        
        return listeners

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """
        obj = event.source

        self._debug("onStateChanged: '%s' %s (%d, %d)" % \
                    (obj.name, event.type, event.detail1, event.detail2))

        # Handle tooltip popups.
        #
        if obj.getRole() == pyatspi.ROLE_TOOL_TIP:
            if event.type.startswith("object:state-changed:showing") and \
               event.detail1 == 1:
                braille.displayMessage(obj.name)
                utterances = self.speechGenerator.generateSpeech(obj)
                speech.speak(utterances)

        # If focus moves to something within a panel and focus was not
        # already in the containing panel, the panel will issue its
        # own state-changed:focused event with detail1 == 1 after the
        # event for the item with focus.  The panel is not focused,
        # plus the extraneous event results in unnecessary chattiness
        # and updates the braille display to "panel."
        #
        elif obj.getRole() == pyatspi.ROLE_PANEL and \
             event.type.startswith("object:state-changed:focused") and \
             event.detail1 == 1 and not \
             event.source.getState().contains(pyatspi.STATE_FOCUSED):
            return

        else:
            default.Script.onStateChanged(self, event)
