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

"""Custom script for gaim.  This provides the ability for Orca to
monitor both the IM input and IM output text areas at the same
time.
"""

import orca.a11y as a11y
import orca.braille as braille
import orca.core as core
import orca.default as default
import orca.orca as orca
import orca.rolenames as rolenames
import orca.speech as speech

from orca.orca_i18n import _
from orca.rolenames import getRoleName

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

        self._output = None
        self._input = None
        

    def _setChat(self, obj):
        """If we've found a chat window, set a reference to it and read it.

        Arguments:
        - obj: the gaim frame
        """
    
        # The chat window has three text boxes in it (the chat topic, the
        # message log, and the text entry field).  find them all - they're
        # always returned in the same order
        #
        entries = a11y.findByRole(obj, rolenames.ROLE_TEXT)
        self._output = entries[1]
        self._input = entries[2]

        # Speak the title of the chat
        #
        label = obj.label
        text = label + _(" chat")
        braille.displayMessage(text)
        speech.speak(text)

        
    def _setIm(self, obj):
        """If we've found an IM window, set a reference to it and read it.

        Arguments:
        - obj: the gaim frame
        """

        # There are two text boxes in each IM window (the message log, and
        # the text entry field).  They are always returned in the same
        # order.   
        #
        entries = a11y.findByRole(obj, rolenames.ROLE_TEXT)
        self._output = entries[0]
        self._input = entries[1]

        # Speak the title of the IM
        #
        label = obj.label
        text = label + _(" instant message")
        braille.displayMessage(text)
        speech.speak(text)


    def onWindowActivated(self, event):
        """Called whenever one of Gaim's toplevel windows is activated.

        Arguments:
        - event: the window activated Event
        """
    
        # If it's not a standard window, do the normal behavior since it
        # won't have an IM or chat in it
        #
        if event.source.role != rolenames.ROLE_FRAME:
            self._output = None
            self._input = None
            return default.Script.onWindowActivated(self, event)

        # Frames with two text boxes are considered to be instant message
        # windows, and those with three are considered chats.  This works for
        # now, but we need a more robust way of doing this sort of thing for
        # the general case
        #
        entries = a11y.findByRole(event.source, rolenames.ROLE_TEXT)
    
        if len(entries) == 2:
            self._setIm(event.source)
        elif len(entries) == 3:
            self._setChat(event.source)
        else:
            self._output = None
            self._input = None

        return default.Script.onWindowActivated(self, event)


    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Gaim's text objects.
        If the object is an instant message or chat, speak the text If we're
        not watching anything, do the default behavior.

        Arguments:
        - event: the text inserted Event
        """

        # [[[TODO: WDW - HACK we seem to be getting object ids for the
        # same text area.  So, we do something a bit more creative here.]]]
        #
        #if (self._output == None) or (event.source != self._output):
        #    return default.Script.onTextInserted(self, event)

        # Do the default action for everything except the display that
        # is showing the chat.
        #
        if (event.source.role != rolenames.ROLE_TEXT):
            return default.Script.onTextInserted(self, event)

        if not event.source.state.count(core.Accessibility.STATE_FOCUSED):
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
        else:
            orca.setLocusOfFocus(event, event.source, False)
            return default.Script.onTextInserted(self, event)
            
        
    def onFocus(self, event):
        """Called when any object in Gaim gets the focus.

        Arguments:
        - event: the focus Event
        """

        # The text boxes in chat and IM windows have no names - so we give
        # them some here
        #
        if event.source == self._input:
            text = _("Input")
        elif event.source == self._output:
            text = _("Message Log")
        else:
            return default.Script.onFocus(self, event)

        text = text + " " + getRoleName(event.source)
        speech.speak(text)
