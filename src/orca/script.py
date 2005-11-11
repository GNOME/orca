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

"""Each script maintains a set of key bindings, braille bindings, and
AT-SPI event listeners.  The key bindings are an instance of
KeyBindings.  The braille bindings are also a dictionary where the
keys are BrlTTY command integers and the values are instances of
InputEventHandler.  The listeners field is a dictionary where the keys
are AT-SPI event names and the values are function pointers.

Instances of scripts are intended to be created solely by the
focus_tracking_presenter, which will call the main entry points of a
script instance: processObjectEvent, processKeyboardEvent, and
processBrailleEvent, locusOfFocusChanged, and visualAppearanceChanged.

This Script class is not intended to be instantiated directly.
Instead, it is expected that subclasses of the Script class will be
created in their own module.  The module defining the Script subclass
is also required to have a 'getScript(app)' method that returns an
instance of the Script subclass.  See default.py for an example."""

import debug
import keybindings
import settings

class Script:
    """The specific focus tracking scripts for applications.
    """
    
    def __init__(self, app):
        """Creates a script for the given application, if necessary.
        This method should not be called by anyone except the
        focus_tracking_presenter.  The main responsibilities of
        this constructor are as follows:

          1) Set the app field of the instance to the app object that
             was passed in.  It is OK to have a None app.
             
          2) Set the name field of the instance to a meaningful name
             (e.g., the name of the app if app is not None).  This
             name field is useful primarily for debugging purposes.

          3) Set up with listeners field, which is a dictionary where
             the keys are AT-SPI event type strings (e.g., 'focus:')
             and the values are methods whose parameters are
             (self,event).

          4) Set up the braillebindings field, which is a dictionary
             where the keys are BrlTTY commands (e.g.,
             braille.CMD_FWINLT]) and the values are InputEventHandler
             instances (see input_event.py).

          5) Set up the keybindings field, which is an instance of
             a KeyBindings class (see keybindings.py).  Scripts will
             add keybindings to the keybindings field by using its
             'add' method to add an instance of a KeyBinding (see also
             keybindings.py).

        See default.py for an example.
        
        Arguments:
        - app: the Python Accessible application to create a script for
        """

        self.app = app
        
        if app:
            self.name = self.app.name
        else:
            self.name = "default"

        self.name += " (module=" + self.__module__ + ")"
        
        self.listeners = {}
        self.braillebindings = {}
        self.keybindings = keybindings.KeyBindings()
        
        
    def processObjectEvent(self, event):
        """Processes all AT-SPI object events of interest to this
        script.  The interest in events is specified via the
        'listeners' field that was defined during the construction of
        this script.

        In general, the primary purpose of handling object events is to
        keep track of changes to the locus of focus and notify the
        orca module of these changes via orca.setLocusOfFocus and
        orca.visualAppearanceChanged.

        Note that this script may be passed events it doesn't care
        about, so it needs to react accordingly.

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
        # different here.  Logged as bugzilla bug 319781.]]]
        #
        for key in self.listeners.keys():
            if event.type.startswith(key):
                self.listeners[key](event)

            
    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event. This method is called
        synchronously from the AT-SPI registry and should be
        performant.  In addition, it must return True if it has
        consumed the event (and False if not).

        This method will primarily use the keybindings field of this
        script instance see if this script has an interest in the
        event.

        NOTE: there is latent, but unsupported, logic for allowing
        the user's user-settings.py file to extend and/or override
        the keybindings for a script.
        
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
        user_bindings = None

        user_bindings_map = settings.getSetting("keybindings_map",{})
        if user_bindings_map.has_key(self.name):
            user_bindings = user_bindings_map[self.name]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        consumed = False
        if user_bindings:
            consumed = user_bindings.consumeKeyboardEvent(keyboardEvent)
        if not consumed:
            consumed = self.keybindings.consumeKeyboardEvent(keyboardEvent)

        return consumed
        

    def processBrailleEvent(self, brailleEvent):
        """Called whenever a key is pressed on the Braille display.
    
        This method will primarily use the braillebindings field of
        this script instance see if this script has an interest in the
        event.

        NOTE: there is latent, but unsupported, logic for allowing
        the user's user-settings.py file to extend and/or override
        the braillebindings for a script.
        
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
            handler = user_bindings[command]
            consumed = handler.processInputEvent(brailleEvent)
                
        if (not consumed) and self.braillebindings.has_key(command):
            handler = self.braillebindings[command]
            consumed = handler.processInputEvent(brailleEvent)

        return consumed


    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        The primary purpose of this method is to present locus of focus
        information to the user.
        
        NOTE: scripts should not call this method directly.  Instead,
        a script should call orca.setLocusOfFocus, which will eventually
        result in this method being called.  

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        pass


    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.
        This method should not be called for objects whose visual
        appearance changes solely because of focus -- setLocusOfFocus
        is used for that.  Instead, it is intended mostly for objects
        whose notional 'value' has changed, such as a checkbox
        changing state, a progress bar advancing, a slider moving,
        text inserted, caret moved, etc.

        The primary purpose of this method is to present the changed
        information to the user.
        
        NOTE: scripts should not call this method directly.  Instead,
        a script should call orca.visualAppearanceChanged, which will
        eventually result in this method being called.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """
        pass
