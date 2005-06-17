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
import brl
import default
import kbd
import rolenames
import speech

# A reference to the display

display = None

# A reference to the accessible text interface of the display

display_txt = None



# This function is run whenever a toplevel window in gcalctool is
# activated

def onWindowActivated(event):
    global display
    global display_txt


    # If we haven't found the display, and this is a toplevel window,
    # look for the display in this window

    if display is None and event.source.role == rolenames.ROLE_TEXT:

        # It's the only text object in GCalctool's main window

        d = a11y.findByRole(event.source, rolenames.ROLE_TEXT)
        display = d[0]
        display_txt = a11y.getText(display)
        contents = display_txt.getText(0, -1)
        brl.writeText(0, contents)

    # Call the default onWindowActivated function

    default.onWindowActivated(event)


# This is an attempt to only read the display when enter or equals is
# pressed - so when we get text insertions to the display, speak
# them if the last key pressed was enter or equals

def onTextInserted(event):
    global display
    global display_txt

    if event.source == display:

        # Always update the Braille display but only speak if the last
        # key pressed was enter or equals

        contents = display_txt.getText(0, -1)
        brl.writeText(0, contents)
        if orca.lastKey == "Return" or orca.lastKey == "=":
            speech.say("default", contents)
            
        
        
