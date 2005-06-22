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
import default
import rolenames
import speech

from orca_i18n import _
from rolenames import getRoleName

# References to the text input and output areas
#
_input = None
_output = None

def _setChat(obj):
    """If we've found a chat window, set a global reference to it and read it.
    """
    
    global _input
    global _output

    # The chat window has threee text boxes in it (the chat topic, the
    # message log, and the text entry field).  find them all - they're
    # always returned in the same order
    #
    entries = a11y.findByRole(obj, rolenames.ROLE_TEXT)
    _output = entries[1]
    _input = entries[2]

    # Speak the title of the chat
    #
    label = a11y.getLabel(obj)
    text = label + _(" chat")
    braille.displayMessage(text)
    speech.say("default", text)
        
    
def _setIm(obj):
    """If we've found an IM window, set a global reference to it and read it.
    """

    global _input
    global _output
    
    # There are two text boxes in each IM window (the message log, and
    # the text entry field).  They are always returned in the same
    # order.   
    #
    entries = a11y.findByRole(obj, rolenames.ROLE_TEXT)
    _output = entries[0]
    _input = entries[1]

    # Speak the title of the IM
    #
    label = a11y.getLabel(obj)
    text = label + _(" instant message")
    braille.displayMessage(text)
    speech.say("default", text)


def onWindowActivated(event):
    """Called whenever one of Gaim's toplevel windows is activated.
    """

    global _input
    global _output
    
    # If it's not a standard window, do the normal behavior since it
    # won't have an IM or chat in it
    #
    if event.source.role != rolenames.ROLE_FRAME:
        _output = None
        _input = None
        return default.onWindowActivated(event)


    # Frames with two text boxes are considered to be instant message
    # windows, and those with three are considered chats.  This works for
    # now, but we need a more robust way of doing this sort of thing for
    # the general case
    #
    entries = a11y.findByRole(event.source, rolenames.ROLE_TEXT)
    
    if len(entries) == 2:
        _setIm(event.source)
    elif len(entries) == 3:
        _setChat(event.source)
    else:
        _output = None
        _input = None
        return default.onWindowActivated(event)


def onTextInserted(event):
    """Called whenever text is inserted into one of Gaim's text objects.  If
    the object is an instant message or chat, speak the text If we're not
    watching anything, do the default behavior.
    """

    global _output

    if (_output == None) or (event.source != _output):
        return default.onTextInserted(event)

    txt = a11y.getText(event.source)
    text = txt.getText(event.detail1, event.detail1 + event.detail2)
    speech.say("default", text)


def onFocus(event):
    """Called when any object in Gaim gets the focus.
    """

    # The text boxes in chat and IM windows have no names - so we give
    # them some here
    #
    if event.source == _input:
        text = _("Input")
    elif event.source == _output:
        text = _("Message Log")
    else:
        return default.onFocus(event)
    
    text = text + " " + getRoleName(event.source)
    speech.say("default", text)
