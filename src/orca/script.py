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

"""Each script maintains a set of key bindings, braille bindings, and
AT-SPI event listeners.  The key bindings are an instance of
KeyBindings.  The braille bindings are also a dictionary where the
keys are BrlTTY command integers and the values are instances of
InputEventHandler.  The listeners field is a dictionary where the keys
are AT-SPI event names and the values are function pointers.

Instances of scripts are intended to be created solely by the
focus_tracking_presenter.

This Script class is not intended to be instantiated directly.
Instead, it is expected that subclasses of the Script class will be
created in their own module.  The module defining the Script subclass
is also required to have a 'getScript(app)' method that returns an
instance of the Script subclass.  See default.py for an example."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import braillegenerator
import debug
import keybindings
import settings
import speechgenerator

class Script:
    """The specific focus tracking scripts for applications.
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

        self.name += " (module=" + self.__module__ + ")"

        self.listeners = self.getListeners()

        self.inputEventHandlers = {}
        self.setupInputEventHandlers()
        self.keyBindings = self.getKeyBindings()
        self.brailleBindings = self.getBrailleBindings()

        self.brailleGenerator = self.getBrailleGenerator()
        self.speechGenerator = self.getSpeechGenerator()
        self.voices = settings.voices

        debug.println(debug.LEVEL_FINE, "NEW SCRIPT: %s" % self.name)

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.

        Returns a dictionary where the keys are AT-SPI event names
        and the values are script methods.
        """
        return {}

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""
        pass

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """
        return keybindings.KeyBindings()

    def getBrailleBindings(self):
        """Defines the braille bindings for this script.

        Returns a dictionary where the keys are BrlTTY commands and the
        values are InputEventHandler instances.
        """
        return {}

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return braillegenerator.BrailleGenerator()

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return speechgenerator.SpeechGenerator()

    # [[[WDW - There is a circular reference going on somewhere (see
    # bug 333168).  In the presence of this reference, the existence
    # of a __del__ method prevents the garbage collector from
    # collecting this object. So, we will not define a __del__ method
    # until we understand where the circular reference is coming from.
    #
    #def __del__(self):
    #    debug.println(debug.LEVEL_FINE, "DELETE SCRIPT: %s" % self.name)

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

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """
        user_bindings = None
        user_bindings_map = settings.keyBindingsMap
        if user_bindings_map.has_key(self.__module__):
            user_bindings = user_bindings_map[self.__module__]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        consumes = False
        if user_bindings:
            consumes = user_bindings.getInputHandler(keyboardEvent) != None
        if not consumes:
            consumes = self.keyBindings.getInputHandler(keyboardEvent) != None
        return consumes

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event.

        This method will primarily use the keybindings field of this
        script instance see if this script has an interest in the
        event.

        NOTE: there is latent, but unsupported, logic for allowing
        the user's user-settings.py file to extend and/or override
        the keybindings for a script.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
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

        user_bindings_map = settings.keyBindingsMap
        if user_bindings_map.has_key(self.__module__):
            user_bindings = user_bindings_map[self.__module__]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        consumed = False
        if user_bindings:
            consumed = user_bindings.consumeKeyboardEvent(self,
                                                          keyboardEvent)
        if not consumed:
            consumed = self.keyBindings.consumeKeyboardEvent(self,
                                                             keyboardEvent)
        return consumed

    def consumesBrailleEvent(self, brailleEvent):
        """Called when a key is pressed on the braille display.

        Arguments:
        - brailleEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """
        user_bindings = None
        user_bindings_map = settings.brailleBindingsMap
        if user_bindings_map.has_key(self.__module__):
            user_bindings = user_bindings_map[self.__module__]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        command = brailleEvent.event
        consumes = False
        if user_bindings:
            consumes = user_bindings.has_key(command)
        if not consumes:
            consumes = self.brailleBindings.has_key(command)
        return consumes

    def processBrailleEvent(self, brailleEvent):
        """Called whenever a key is pressed on the Braille display.

        This method will primarily use the brailleBindings field of
        this script instance see if this script has an interest in the
        event.

        NOTE: there is latent, but unsupported, logic for allowing
        the user's user-settings.py file to extend and/or override
        the brailleBindings for a script.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent
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

        user_bindings_map = settings.brailleBindingsMap
        if user_bindings_map.has_key(self.name):
            user_bindings = user_bindings_map[self.name]
        elif user_bindings_map.has_key("default"):
            user_bindings = user_bindings_map["default"]

        if user_bindings and user_bindings.has_key(command):
            handler = user_bindings[command]
            consumed = handler.processInputEvent(self, brailleEvent)

        if (not consumed) and self.brailleBindings.has_key(command):
            handler = self.brailleBindings[command]
            consumed = handler.processInputEvent(self, brailleEvent)

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
