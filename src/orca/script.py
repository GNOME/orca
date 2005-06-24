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

"""Each script maintains a set of keybindings and listeners.  The keybindings
field is a dictionary where the keys are keystrings and the values are
function pointers.  The listeners field is also a dictionary where the keys
are AT-SPI event names and the values are function pointers."""

import debug
import settings

class Script:
    """Manages the specific focus tracking scripts for applications.
    """
    
    def __init__(self, app):
        """Creates a script for the given application, if necessary.
        This method should not be called by anyone except the
        focus_tracking_presenter.

        Arguments:
        - app: the Python Accessible application to create a script for
        """

        self.app = app
        
        if app:
            self.name = self.app.name
        else:
            self.name = "default"
            
        self.listeners = {}
        self.keybindings = {}
        
        
    def processObjectEvent(self, event):
        """Processes all object events of interest to this script.  Note
        that this script may be passed events it doesn't care about, so
        it needs to react accordingly.

        Arguments:
        - event: the Event
        """

        # This calls the first listener it finds whose key *begins with* or is
        # the same as the event.type.  The reason we do this is that the event
        # type in the listeners dictionary may not be as specific as the event
        # type we received (e.g., the listeners dictionary might contain the
        # key "object:state-changed:" and the event.type might be
        # "object:state-changed:focused".  [[[TODO: WDW - the order of the
        # keys is *not* deterministic, and is not guaranteed to be related
        # to the order in which they were added.  So...we need to do something
        # different here.]]]
        #
        for key in self.listeners.keys():
            if event.type.startswith(key):
                try:
                    self.listeners[key](event)
                except:
                    debug.printException(debug.LEVEL_SEVERE)
            

    def processKeyEvent(self, keystring):
        """Processes the given keyboard event. This method is called
        synchronously from the at-spi registry and should be performant.  In
        addition, it must return True if it has consumed the event (and False
        if not).
    
        Arguments:
        - keystring: a keyboard event string

        Returns True if the event should be consumed.
        """

        consumed = False
        user_keybindings = None

        # We'll let the user keybindings take precedence.  First, we'll
        # check to see if they have keybindings specific for the particular
        # application, then we'll check to see if they have any default
        # bindings to use.
        #
        user_keybindings_map = settings.getSetting("keybindings_map",{})
        if user_keybindings_map.has_key(self.name):
            user_keybindings = user_keybindings_map[self.name]
        elif user_keybindings_map.has_key("default"):
            user_keybindings = user_keybindings_map["default"]

        if user_keybindings and user_keybindings.has_key(keystring):
            try:
                consumed = user_keybindings[keystring](keystring, self)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                
        if (not consumed) and self.keybindings.has_key(keystring):
            try:
                consumed = self.keybindings[keystring](keystring, self)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed
        

    def processBrailleEvent(self, command):
        """Called whenever a cursor key is pressed on the Braille display.
    
        Arguments:
        - command: the BrlAPI command for the key that was pressed.

        Returns True if the command was consumed; otherwise False
        """
        return False
