# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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

"""Custom script for gaim.  This provides the ability for Orca to
monitor both the IM input and IM output text areas at the same
time.
"""

import orca.atspi as atspi
import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.orca as orca
import orca.rolenames as rolenames
import orca.speech as speech

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The Gaim script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.
        
        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Gaim's text
        objects.  If the object is an instant message or chat, speak
        the text. If we're not watching anything, do the default
        behavior.

        Arguments:
        - event: the text inserted Event
        """

        # Do the default action for everything except the display that
        # is showing the chat.
        #
        if (event.source.role != rolenames.ROLE_TEXT):
            return default.Script.onTextInserted(self, event)

        if not event.source.state.count(atspi.Accessibility.STATE_FOCUSED):
            # We always automatically go back to focus tracking mode when
            # someone sends us a message.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()

            txt = event.source.text
            text = txt.getText(event.detail1, event.detail1 + event.detail2)
            
            # A new message inserts a carriage return at the end of the
            # previous line rather than adding to the end of the current
            # line (I think).  So...remove the darn thing.
            #
            if text[0] == "\n":
                text = text[1:]
                braille.displayMessage(text)
                speech.speak(text)
                return
            else:
                # [[[TODO: WDW - HACK to handle the case where the
                # area where the user types loses focus and never
                # regains it with respect to the AT-SPI regardless if
                # it really gets it with respect to the toolkit.  The
                # way we are guessing we are really in the area where
                # you type is because the text does not end in a
                # "\n".  This is related to bug
                # http://bugzilla.gnome.org/show_bug.cgi?id=325917]]]
                #
                debug.println(debug.LEVEL_WARNING,
                              "WARNING in gaim.py: "
                              + "the text area has not regained focus")
                orca.setLocusOfFocus(event, event.source, False)
                return default.Script.onTextInserted(self, event)
        else:
            orca.setLocusOfFocus(event, event.source, False)
            return default.Script.onTextInserted(self, event)
