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

"""Provides a custom script for gcalctool."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.braille as braille
import orca.default as default
import orca.input_event as input_event
import orca.orca_state as orca_state
import orca.speech as speech
import pyatspi

from speech_generator import SpeechGenerator

from orca.orca_i18n import _ # for gettext support

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

        self._lastProcessedKeyEvent = None
        self._lastSpokenContents = None
        self._resultsDisplay = None

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
                # Translators: this is an indication that Orca is unable to
                # obtain the display of the gcalctool calculator, which is
                # the area where calculation results are presented.
                #
                contents = _("Unable to get calculator display")
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

        Arguments:
        - event: the text inserted Event
        """

        # Always update the Braille display but only speak if the last
        # key pressed was Return, space, or equals.
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

                # gcalctool issues several identical text inserted events
                # for a single press of keys such as enter, space, or equals.
                # In fact, it's usually about 4, but we cannot depend upon
                # that.  In addition, keyboard events are decoupled from
                # text insertion events, so we may get key press/release
                # events before an insertion occurs, or we might get a 
                # press, an insertion, and then a release.
                #
                # So, what we do is try to infer that an insertion event
                # was the cause of a single key event.
                #
                speakIt = True
                if self._lastProcessedKeyEvent:
                    # This catches text insertion events where the last
                    # keyboard event we looked at was the key release event.
                    #
                    if self._lastProcessedKeyEvent.timestamp \
                       == orca_state.lastNonModifierKeyEvent.timestamp:
                        speakIt = False
                    # This catches text insertion events where the last
                    # keyboard event we looked at was the key press event,
                    # but the current one is now the associated key release
                    # event.  We infer they are the same by looking at the
                    # hardware code, the time delta between the press and
                    # the release, and that we are on the verge of repeating
                    # something we just spoke.
                    #
                    # It would be tempting to look at just the contents that
                    # we previous spoke, but a use case we need to handle is
                    # when the user enters a number (e.g., "666") and then
                    # presses Return several times.  In this case, we get
                    # the text insertion events and they are all "666".
                    #
                    elif (self._lastProcessedKeyEvent.type \
                          == pyatspi.KEY_PRESSED_EVENT) \
                          and (orca_state.lastNonModifierKeyEvent.type \
                               == pyatspi.KEY_RELEASED_EVENT) \
                          and (orca_state.lastNonModifierKeyEvent.hw_code \
                               == self._lastProcessedKeyEvent.hw_code) \
                          and (orca_state.lastNonModifierKeyEvent.timestamp \
                               - self._lastProcessedKeyEvent.timestamp) < 1000 \
                          and (contents == self._lastSpokenContents):
                        speakIt = False
                if speakIt:
                    speech.speak(contents)
                    self._lastSpokenContents = contents

        self._lastProcessedKeyEvent = \
            input_event.KeyboardEvent(orca_state.lastNonModifierKeyEvent)
