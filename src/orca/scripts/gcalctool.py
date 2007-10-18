# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

"""Provides a custom script for gcalctool."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.braille as braille
import orca.default as default
import orca.input_event as input_event
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.where_am_I as where_am_I
import pyatspi

class WhereAmI(where_am_I.WhereAmI):

    def __init__(self, script):
        """Create a new WhereAmI that will be used to speak information
        about the current object of interest.
        """

        where_am_I.WhereAmI.__init__(self, script)

    def _speakStatusBar(self):
        """Speaks the status bar."""

        if not self._statusBar:
            return

        utterances = []
        text = self._getObjLabelAndName(self._statusBar)
        utterances.append(text)
        speech.speakUtterances(utterances)

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForPushButton to handle 'unspeakable'
    button labels displayed on the screen.
    """
    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForObjectName(self, obj):
        """Gives preference to the object name versus what is being
        displayed on the screen.  This helps accomodate the naming
        hints being given to us by gcalctool for it's mathematical
        operator buttons."""

        if obj.getRole() != pyatspi.ROLE_PUSH_BUTTON:
            return speechgenerator.SpeechGenerator._getSpeechForObjectName(\
                self, obj)

        if obj.name:
            name = obj.name
        else:
            name = self._script.getDisplayedText(obj)

        if name:
            return [name]
        elif obj.description:
            return [obj.description]
        else:
            return []

########################################################################
#                                                                      #
# The GCalcTool script class.                                          #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        self._resultsDisplay = None

    def getWhereAmI(self):
        """Returns the "where am I" class for this script.
        """

        return WhereAmI(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def onWindowActivated(self, event):
        """Called whenever one of gcalctool's toplevel windows is activated.

        Arguments:
        - event: the window activated Event
        """

        # If we haven't found the display, and this is a toplevel window,
        # look for the display in this window
        #
        if (self._resultsDisplay is None) \
               and (event.source.getRole() == pyatspi.ROLE_FRAME):

            # The widget hierarchy for gcalctool differs depending upon the
            # version.
            #
            # In GNOME 2.6 (gcalctool version 4.3.51 for example), the
            # display area was a text_view widget. This can be found by
            # looking for an accessible object with a role of ROLE_TEXT.
            #
            # For GNOME 2.10 and 2.12 there is a scrolled_window containing
            # the text_view display. This can be found by looking for an
            # accessible object with a role of ROLE_EDITBAR.
            #
            d = self.findByRole(event.source, pyatspi.ROLE_TEXT)
            if len(d) == 0:
                d = self.findByRole(event.source, pyatspi.ROLE_EDITBAR)

            # If d is an empty list at this point, we're unable to get the
            # gcalctool display. Inform the user.
            #
            if len(d) == 0:
                contents = "Unable to get calculator display"
                speech.speak(contents)
                braille.displayMessage(contents)
            else:
                self._resultsDisplay = d[0]
                contents = self.getText(self._resultsDisplay, 0, -1)
                braille.displayMessage(contents)

            # Call the default onWindowActivated function
            #
            default.Script.onWindowActivated(self, event)

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
        if event.source == self._resultsDisplay:
            contents = self.getText(self._resultsDisplay, 0, -1)
            braille.displayMessage(contents)

            if (orca_state.lastInputEvent is None) \
                   or \
                   (not isinstance(orca_state.lastInputEvent,
                                   input_event.KeyboardEvent)):
                return

            if (orca_state.lastNonModifierKeyEvent.event_string == "space") \
                   or (orca_state.lastNonModifierKeyEvent.event_string \
                       == "Return") \
                   or (orca_state.lastNonModifierKeyEvent.event_string == "="):
                speech.speak(contents)
