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

import orca.scripts.default as default
import orca.input_event as input_event
import orca.orca_state as orca_state
import orca.speech as speech
import pyatspi

from .speech_generator import SpeechGenerator

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
        self._statusLine = None

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def onWindowActivated(self, event):
        """Called whenever one of gcalctool's toplevel windows is activated.

        Arguments:
        - event: the window activated Event
        """

        # Locate the results display and the status line if we've not yet
        # done so.
        #
        if not (self._resultsDisplay and self._statusLine) \
           and event.source.getRole() == pyatspi.ROLE_FRAME:
            objs = self.utilities.descendantsWithRole(
                event.source, pyatspi.ROLE_EDITBAR)
            if len(objs) == 0:
                # Translators: this is an indication that Orca is unable to
                # obtain the display of the gcalctool calculator, which is
                # the area where calculation results are presented.
                #
                contents = _("Unable to get calculator display")
                speech.speak(contents)
                self.displayBrailleMessage(contents)
            else:
                self._resultsDisplay = objs[0]
                contents = self.utilities.substring(self._resultsDisplay, 0, -1)
                self.displayBrailleMessage(contents)
                # The status line in gcalctool 5.29 is a sibling of the
                # edit bar.
                #
                objs = self.utilities.descendantsWithRole(
                    self._resultsDisplay.parent, pyatspi.ROLE_TEXT)
                for obj in objs:
                    if not obj.getState().contains(pyatspi.STATE_EDITABLE):
                        self._statusLine = obj
                        break
                else:
                    # The status line in gcalctool 5.28 is a label in the
                    # status bar in which text is inserted as need be.
                    #
                    statusBar = self.utilities.statusBar(event.source)
                    if statusBar:
                        objs = self.utilities.descendantsWithRole(
                            statusBar, pyatspi.ROLE_LABEL)
                        if len(objs):
                            self._statusLine = objs[0]

        default.Script.onWindowActivated(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into gcalctool's text display.

        Arguments:
        - event: the text inserted Event
        """

        # Always update the Braille display but only speak if the last
        # key pressed was Return, space, or equals.
        #
        if self.utilities.isSameObject(event.source, self._resultsDisplay):
            contents = self.utilities.substring(self._resultsDisplay, 0, -1)
            self.displayBrailleMessage(contents)
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey in ["space", "Return", "="]:
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

            if not lastKey:
                return

            self._lastProcessedKeyEvent = \
                input_event.KeyboardEvent(orca_state.lastNonModifierKeyEvent)

        elif self.utilities.isSameObject(event.source, self._statusLine):
            contents = self.utilities.substring(self._statusLine, 0, -1)
            speech.speak(contents)
            return
