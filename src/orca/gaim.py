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

import a11y
import braille
import rolenames
import speech

from orca_i18n import _
from rolenames import getRoleName

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
    - app: the application to create a script for (should be gaim)
    """
    
    return Gaim(app)


########################################################################
#                                                                      #
# The Gaim script class.                                               #
#                                                                      #
########################################################################

class Gaim(Default):

    def __init__(self, app):
        """Creates a new script for the given application.  Callers
        should use the getScript factory method instead of calling
        this constructor directly.
        
        Arguments:
        - app: the application to create a script for.
        """

        Default.__init__(self, app)

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
        speech.say("default", text)

        
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
        speech.say("default", text)


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
            return Default.onWindowActivated(self, event)

        # Frames with two text boxes are considered to be instant message
        # windows, and those with three are considered chats.  This works for
        # now, but we need a more robust way of doing this sort of thing for
        # the general case
        #
        entries = a11y.findByRole(event.source, rolenames.ROLE_TEXT)
    
        if len(entries) == 2:
            self._setIm(self, event.source)
        elif len(entries) == 3:
            self._setChat(self, event.source)
        else:
            self._output = None
            self._input = None
            
        return Default.onWindowActivated(self, event)


    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Gaim's text objects.
        If the object is an instant message or chat, speak the text If we're
        not watching anything, do the default behavior.

        Arguments:
        - event: the text inserted Event
        """

        if (self._output == None) or (event.source != self._output):
            return Default.onTextInserted(self, event)

        txt = event.source.text
        text = txt.getText(event.detail1, event.detail1 + event.detail2)
        speech.say("default", text)


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
        elif event.source == _self.output:
            text = _("Message Log")
        else:
            return Default.onFocus(self, event)
    
        text = text + " " + getRoleName(event.source)
        speech.say("default", text)
