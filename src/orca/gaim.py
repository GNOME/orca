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

import core
import script
import a11y
import speech
import brl
import default
from rolenames import getRoleName

# Orca i18n

from orca_i18n import _

# If we've found a chat window, set a global reference to it and read
# it

def setChat (obj):

    # The chat window has threee text boxes in it (the chat topic, the
    # message log, and the text entry field).  find them all - they're
    # always returned in the same order

    entries = a11y.findByRole (obj, "text")

    # The second entry is the output log - Due to current
    # architectural limitations, the only way to refer to the current
    # script object is through the script.active reference - global
    # variables to this module may be shared across multiple scripts
    # (although it's unlikely in this case) - the only practical case
    # where module-level variables actually are shared across multiple
    # applications is in the default script.  but since these scripts
    # serve as example code, the technically proper way to store
    # variables is in the script object, referenced by script.active

    script.active.output = entries[1]
    script.active.input = entries[2]

    # Speak the title of the chat

    label = a11y.getLabel (obj)
    text = label + _(" chat")
    brl.writeMessage (text)
    speech.say ("default", text)
    

# When we've found an instant mesage window, keep a reference to it

def setIm (obj):

    # There are two text boxes in each IM window (the message log, and
    # the text entry field).  They are always returned in the same
    # order
    

    entries = a11y.findByRole (obj, "text")

    # The first entry is the output log

    script.active.output = entries[0]
    script.active.input = entries[1]

    # Speak the title of the IM
    label = a11y.getLabel (obj)
    text = label + _(" instant message")
    brl.writeMessage (text)
    speech.say ("default", text)

# This function is called whenever one of Gaim's toplevel windows is
# activated

def onWindowActivated (event):

    # If it's not a standard window, do the normal behavior since it
    # won't have an IM or chat in it

    if event.source.getRoleName () != "frame":
        script.active.output = None
        script.active.input = None
        return default.onWindowActivated (event)


    # Frames with two text boxes are considered to be instant message
    # dinwos, and those with three are considered chats.  This works for
    # now, but we need a more robust way of doing this sort of thing for
    # the general case

    entries = a11y.findByRole (event.source, "text")
    if len(entries) == 2:
        setIm (event.source)
    elif len(entries) == 3:
        setChat (event.source)
    else:
        script.active.output = None
        script.active.input = None
        return default.onWindowActivated (event)

# This function is called whenever text is inserted into one of Gaim's
# text objects.  If the object is an instant message or chat, speak
# the text

def onTextInserted (event):

    # If we're not watching anything, do the default behavior

    if script.active.output == None or event.source != script.active.output:
        return default.onTextInserted (event)

    txt = a11y.getText (event.source)
    text = txt.getText (event.detail1, event.detail1+event.detail2)
    speech.say ("default", text)

# this function is called when any object in Gaim gets the focus

def onFocus (event):

    # The text boxes in chat and IM windows have no names - so we give
    # them some here

    if event.source == script.active.input:
        text = _("Input")
    elif event.source == script.active.output:
        text = _("Message Log")
    else:
        return default.onFocus (event)
    text = text + " " + getRoleName (event.source)
    speech.say ("default", text)
