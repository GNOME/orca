# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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

import a11y
import braille
import kbd
import rolenames
import speech
import orca

from default import Default

########################################################################
#                                                                      #
# The factory method for this module.  All Scripts are expected to     #
# have this method, and it is the sole way that instances of scripts   #
# should be created.                                                   #
#                                                                      #
########################################################################

def getScript(app):
    """Factory method to create a new Default script for the given
    application.  This method should be used for creating all
    instances of this script class.

    Arguments:
    - app: the application to create a script for (should be gcalctool)
    """

    return GCalcTool(app)


########################################################################
#                                                                      #
# The GCalcTool script class.                                          #
#                                                                      #
########################################################################

class GCalcTool(Default):

    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.
        
        Arguments:
        - app: the application to create a script for.
        """
        
        Default.__init__(self, app)

        self._display = None
        self._display_txt = None

        
    def onWindowActivated(self, event):
        """Called whenever one of gcalctool's toplevel windows is activated.

        Arguments:
        - event: the window activated Event
        """

        # If we haven't found the display, and this is a toplevel window,
        # look for the display in this window
        #
        if (self._display is None) \
               and (event.source.role == rolenames.ROLE_FRAME):

            # It's the only text object in GCalctool's main window
            #
            d = a11y.findByRole(event.source, rolenames.ROLE_TEXT)
            self._display = d[0]
            self._display_txt = self._display.text
            contents = self._display_txt.getText(0, -1)
            braille.displayMessage(contents)

            # Call the default onWindowActivated function
            #
            Default.onWindowActivated(self, event)


    def onTextInserted(self, event):
        """Called whenever text is inserted into gcalctool's text display.
        If the object is an instant message or chat, speak the text If we're
        not watching anything, do the default behavior.

        Arguments:
        - event: the text inserted Event
        """

        # This is an attempt to only read the display when enter or equals is
        # pressed - so when we get text insertions to the display, speak
        # them if the last key pressed was enter or equals.
        #
        # Always update the Braille display but only speak if the last
        # key pressed was enter or equals
        #
        if event.source == self._display:
            contents = self._display_txt.getText(0, -1)
            braille.displayMessage(contents)
            if orca.lastKey == "Return" or orca.lastKey == "=":
                speech.say("default", contents)
