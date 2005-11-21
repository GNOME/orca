# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

import orca.atspi as atspi
import orca.braille as braille
import orca.default as default
import orca.input_event as input_event
import orca.rolenames as rolenames
import orca.speech as speech
import orca.orca as orca

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
            #
            d = atspi.findByRole(event.source, rolenames.ROLE_TEXT)
            if len(d) == 0:
                d = atspi.findByRole(event.source, rolenames.ROLE_EDITBAR)

            # If d is an empty list at this point, we're unable to get the
            # gcalctool display. Inform the user.
            #
            if len(d) == 0:
                contents = "Unable to get calculator display"
                speech.speak(contents)
                braille.displayMessage(contents)
            else:
                self._display = d[0]
                self._display_txt = self._display.text
                contents = self._display_txt.getText(0, -1)
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
        if event.source == self._display:
            contents = self._display_txt.getText(0, -1)
            braille.displayMessage(contents)

            if (orca.lastInputEvent is None) \
                   or \
                   (not isinstance(orca.lastInputEvent,
                                   input_event.KeyboardEvent)):
                return

            if (orca.lastInputEvent.event_string == "Return") \
                   or (orca.lastInputEvent.event_string == "="):
                speech.speak(contents)
