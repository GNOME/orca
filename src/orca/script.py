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

"""Each script maintains a set of key bindings, braille bindings, and AT-SPI
event listeners.  The key bindings are a dictionary where the keys are
keystrings and the values are instances of InputEventHandler.  The braille
bindings are also a dictionary where the keys are BrlTTY command integers and
the values are instances of InputEventHandler.  The listeners field is a
dictionary where the keys are AT-SPI event names and the values are function
pointers.

Instances of scripts are intended to be created solely by the
focus_tracking_presenter, which will call the three main entry points of a
script instance: processObjectEvent, processKeyEvent, and processBrailleEvent.
"""

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
        self.braillebindings = {}
        
        
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
            

    def processKeyEvent(self, keyboardEvent):
        """Processes the given keyboard event. This method is called
        synchronously from the at-spi registry and should be performant.  In
        addition, it must return True if it has consumed the event (and False
        if not).
        
        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        
        Returns True if the event was consumed; otherwise False
        """

        # We'll annotate the event with a reference to this script.
        # This will allow external scripts to muck with the script
        # instance if they wish.
        #
        keyboardEvent.script = self
        
        # We'll let the user keybindings take precedence.  First, we'll
        # check to see if they have keybindings specific for the particular
        # application, then we'll check to see if they have any default
        # bindings to use.
        #
        # [[[TODO: WDW - for performance, these bindings should probably
        # be conflated at initialization time.]]]
        #
        consumed = False
        user_bindings = None
        keystring = keyboardEvent.event

        user_bindings_map = settings.getSetting("keybindings_map",{})
        if user_bindings_map.has_key(self.name):
            user_bindings = user_bindings_map[self.name]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        if user_bindings and user_bindings.has_key(keystring):
            try:
                handler = user_bindings[keystring]
                consumed = handler.processInputEvent(keyboardEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                
        if (not consumed) and self.keybindings.has_key(keystring):
            try:
                handler = self.keybindings[keystring]
                consumed = handler.processInputEvent(keyboardEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed
        

    def processBrailleEvent(self, brailleEvent):
        """Called whenever a key is pressed on the Braille display.
    
        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent
        
        Returns True if the event was consumed; otherwise False
        """

        # We'll annotate the event with a reference to this script.
        # This will allow external scripts to muck with the script
        # instance if they wish.
        #
        brailleEvent.script = self

        # We'll let the user bindings take precedence.  First, we'll
        # check to see if they have bindings specific for the particular
        # application, then we'll check to see if they have any default
        # bindings to use.
        #
        # [[[TODO: WDW - for performance, these bindings should probably
        # be conflated at initialization time.]]]
        #
        consumed = False
        user_bindings = None
        command = brailleEvent.event
        
        user_bindings_map = settings.getSetting("braillebindings_map",{})
        if user_bindings_map.has_key(self.name):
            user_bindings = user_bindings_map[self.name]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        if user_bindings and user_bindings.has_key(command):
            try:
                handler = user_bindings[command]
                consumed = handler.processInputEvent(brailleEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                
        if (not consumed) and self.braillebindings.has_key(command):
            try:
                handler = self.braillebindings[command]
                consumed = handler.processInputEvent(brailleEvent)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        return consumed


    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        pass


    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.  This
        method should not be called for objects whose visual appearance
        changes solely because of focus -- setLocusOfFocus is used for that.
        Instead, it is intended mostly for objects whose notional 'value' has
        changed, such as a checkbox changing state, a progress bar advancing,
        a slider moving, text inserted, caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """
        pass
