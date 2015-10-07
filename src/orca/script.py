# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Each script maintains a set of key bindings, braille bindings, and
AT-SPI event listeners.  The key bindings are an instance of
KeyBindings.  The braille bindings are also a dictionary where the
keys are BrlTTY command integers and the values are instances of
InputEventHandler.  The listeners field is a dictionary where the keys
are AT-SPI event names and the values are function pointers.

Instances of scripts are intended to be created solely by the
script manager.

This Script class is not intended to be instantiated directly.
Instead, it is expected that subclasses of the Script class will be
created in their own module.  The module defining the Script subclass
is also required to have a 'getScript(app)' method that returns an
instance of the Script subclass.  See default.py for an example."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

from . import braille_generator
from . import debug
from . import event_manager
from . import flat_review
from . import formatting
from . import label_inference
from . import keybindings
from . import orca_state
from . import script_manager
from . import script_utilities
from . import settings
from . import settings_manager
from . import speech_generator
from . import structural_navigation
from . import where_am_I
from . import bookmarks
from . import tutorialgenerator

_eventManager = event_manager.getManager()
_scriptManager = script_manager.getManager()
_settingsManager = settings_manager.getManager()

class Script:
    """The specific focus tracking scripts for applications.
    """

    def __init__(self, app):
        """Creates a script for the given application, if necessary.
        This method should not be called by anyone except the
        script manager.

        Arguments:
        - app: the Python Accessible application to create a script for
        """
        self.app = app

        if app:
            try:
                self.name = self.app.name
            except (LookupError, RuntimeError):
                msg = 'script.__init__: Error trying to get app.name'
                debug.println(debug.LEVEL_FINE, msg)
                self.name = "default"
        else:
            self.name = "default"

        self.name += " (module=" + self.__module__ + ")"

        self.listeners = self.getListeners()

        # By default, handle events for non-active applications.
        #
        self.presentIfInactive = True

        self.utilities = self.getUtilities()
        self.labelInference = self.getLabelInference()
        self.structuralNavigation = self.getStructuralNavigation()
        self.caretNavigation = self.getCaretNavigation()
        self.bookmarks = self.getBookmarks()
        self.liveRegionManager = self.getLiveRegionManager()

        self.chat = self.getChat()
        self.inputEventHandlers = {}
        self.pointOfReference = {}
        self.setupInputEventHandlers()
        self.keyBindings = self.getKeyBindings()
        self.brailleBindings = self.getBrailleBindings()

        self.formatting = self.getFormatting()
        self.brailleGenerator = self.getBrailleGenerator()
        self.speechGenerator = self.getSpeechGenerator()
        self.generatorCache = {}
        self.eventCache = {}
        self.whereAmI = self.getWhereAmI()
        self.spellcheck = self.getSpellCheck()
        self.voices = settings.voices
        self.tutorialGenerator = self.getTutorialGenerator()

        self.flatReviewContextClass = flat_review.Context

        self.findCommandRun = False
        self._lastCommandWasStructNav = False

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

    def getToolkitKeyBindings(self):
        """Returns the toolkit-specific keybindings for this script."""

        return keybindings.KeyBindings()

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        return keybindings.KeyBindings()

    def getKeyBindingsForInputHandler(self, inputEventHandler):
        """ Returns a KeyBindings object with the list of KeyBindings that
        matche the passed inputEventHandler as argument (at least the
        inputEventHandler that has the same handler function)

        Arguments:
        - inputEventHandler: an instance of input_event.InputEventHandler

        Returns an instance of keybindings.KeyBindings populated with
        keybindings.KeyBinding instances that match the inputEventHandler.
        """
        matches = keybindings.KeyBindings()

        for binding in self.keyBindings.keyBindings:
            if inputEventHandler == binding.handler:
                matches.add(binding)

        return matches

    def getBrailleBindings(self):
        """Defines the braille bindings for this script.

        Returns a dictionary where the keys are BrlTTY commands and the
        values are InputEventHandler instances.
        """
        return {}

    def getBrailleCommandsForInputHandler(self, inputEventHandler):
        """Returns a list of BrlTTY commands (they're in braille.py) that
        match the given inputEventHandler passed as argument.

        Arguments:
        - inputEventHandler: an instance of input_event.InputEventHandler

        Returns a list (possibly empty) of BrlTTY commands (they're in
        braille.py) that match the given inputEventHandler passed.
        """
        return [command
                for command, handler in list(self.brailleBindings.items())
                if inputEventHandler == handler]

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return formatting.Formatting(self)

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return braille_generator.BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return speech_generator.SpeechGenerator(self)

    def getTutorialGenerator(self):
        """Returns the tutorial generator for this script.
        """
        return tutorialgenerator.TutorialGenerator(self)

    def getChat(self):
        """Returns the 'chat' class for this script.
        """
        return None

    def getSpellCheck(self):
        """Returns the spellcheck support for this script."""
        return None

    def getCaretNavigation(self):
        """Returns the caret navigation support for this script."""
        return None

    def getUtilities(self):
        """Returns the utilites for this script.
        """
        return script_utilities.Utilities(self)

    def getLabelInference(self):
        """Returns the label inference functionality for this script."""
        return label_inference.LabelInference(self)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script.
        """
        return []

    def getStructuralNavigation(self):
        """Returns the 'structural navigation' class for this script."""
        types = self.getEnabledStructuralNavigationTypes()
        enable = _settingsManager.getSetting('structuralNavigationEnabled')
        return structural_navigation.StructuralNavigation(self, types, enable)

    def getLiveRegionManager(self):
        """Returns the live region support for this script."""
        return None

    def useStructuralNavigationModel(self):
        """Returns True if we should use structural navigation. Most
        scripts will have no need to override this.  Gecko does however
        because within an HTML document there are times when we do want
        to use it and times when we don't even though it is enabled,
        e.g. in a form field.
        """
        return self.structuralNavigation.enabled

    def getWhereAmI(self):
        """Returns the "where am I" class for this script.
        """
        return where_am_I.WhereAmI(self)

    def getBookmarks(self):
        """Returns the "bookmarks" class for this script.
        """
        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = bookmarks.Bookmarks(self)
            return self.bookmarks

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application.
        """
        return None

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        return {}

    def registerEventListeners(self):
        """Tells the event manager to start listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        _eventManager.registerScriptListeners(self)

    def deregisterEventListeners(self):
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        _eventManager.deregisterScriptListeners(self)

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

        Note that this script may be passed events it doesn't care
        about, so it needs to react accordingly.

        Arguments:
        - event: the Event
        """

        try:
            role = event.source.getRole()
        except (LookupError, RuntimeError):
            msg = 'script.processObjectEvent: Error getting role'
            debug.println(debug.LEVEL_FINE, msg)
            return

        # Check to see if we really want to process this event.
        #
        processEvent = (orca_state.activeScript == self \
                        or self.presentIfInactive)
        if role == pyatspi.ROLE_PROGRESS_BAR \
           and not processEvent \
           and settings.progressBarVerbosity == settings.PROGRESS_BAR_ALL:
            processEvent = True

        if not processEvent:
            return

        if self.skipObjectEvent(event):
            return

        # Clear the generator cache for each event.
        #
        self.generatorCache = {}

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
        for key in list(self.listeners.keys()):
            if event.type.startswith(key):
                self.listeners[key](event)

    def skipObjectEvent(self, event):
        """Gives us, and scripts, the ability to decide an event isn't
        worth taking the time to process under the current circumstances.

        Arguments:
        - event: the Event

        Returns True if we shouldn't bother processing this object event.
        """

        cachedEvent, eventTime = self.eventCache.get(event.type, [None, 0])
        if not cachedEvent or cachedEvent == event:
            return False

        focus    = ["object:state-changed:focused"]
        typing   = ["object:text-changed:insert", "object:text-changed:delete"]
        arrowing = ["object:text-caret-moved", "object:text-selection-changed",
                    "object:selection-changed", "object:active-descendant-changed"]

        skip = False
        if (event.type in arrowing or event.type in typing) \
           and event.source == cachedEvent.source:
            skip = True
            reason = "more recent event of the same type in the same object"
        elif event.type in focus and event.source != cachedEvent.source \
             and event.type == cachedEvent.type \
             and event.detail1 == cachedEvent.detail1:
            skip = True
            reason = "more recent event of the same type in a different object"
        elif event.type.endswith("system") and event.source == cachedEvent.source:
            skip = True
            reason = "more recent system event in the same object"
        elif event.type.startswith("object:state-changed") \
             and event.type == cachedEvent.type \
             and event.source == cachedEvent.source \
             and event.detail1 == cachedEvent.detail1:
            skip = True
            reason = "appears to be duplicate state-changed event"

        if skip:
            debug.println(debug.LEVEL_FINE,
                          "script.skipObjectEvent: skipped due to %s:" \
                          % reason)
            debug.println(debug.LEVEL_FINE,
                          "\tType: %s\n\tSource: %s\n\tDetail1: %s"
                          % (cachedEvent.type, cachedEvent.source, cachedEvent.detail1))
        return skip

    def checkKeyboardEventData(self, keyboardEvent):
        """Checks the data on the keyboard event.

        Some toolkits don't fill all the key event fields, and/or fills
        them out with unexpected data. This method tries to fill in the
        missing fields and validate/standardize the data we've been given.
        While any script can override this method, it is expected that
        this will only be done at the toolkit script level.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        try:
            from gi.repository import Gdk
            keyboardEvent.keyval_name = Gdk.keyval_name(keyboardEvent.id)
        except:
            debug.println(debug.LEVEL_FINE,
                          "Could not obtain keyval_name for id: %d" \
                          % keyboardEvent.id)

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """

        user_bindings = None
        user_bindings_map = settings.keyBindingsMap
        if self.__module__ in user_bindings_map:
            user_bindings = user_bindings_map[self.__module__]
        elif "default" in user_bindings_map:
            user_bindings = user_bindings_map["default"]

        consumes = False
        self._lastCommandWasStructNav = False
        if user_bindings:
            handler = user_bindings.getInputHandler(keyboardEvent)
            if handler \
                 and handler.function in self.structuralNavigation.functions:
                consumes = self.useStructuralNavigationModel()
                if consumes:
                    self._lastCommandWasStructNav = True
            else:
                consumes = handler != None
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler \
                 and handler.function in self.structuralNavigation.functions:
                consumes = self.useStructuralNavigationModel()
                if consumes:
                    self._lastCommandWasStructNav = True
            else:
                consumes = handler != None
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
        if self.__module__ in user_bindings_map:
            user_bindings = user_bindings_map[self.__module__]
        elif "default" in user_bindings_map:
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
        if self.__module__ in user_bindings_map:
            user_bindings = user_bindings_map[self.__module__]
        elif "default" in user_bindings_map:
            user_bindings = user_bindings_map["default"]

        command = brailleEvent.event["command"]
        consumes = False
        if user_bindings:
            consumes = command in user_bindings
        if not consumes:
            consumes = command in self.brailleBindings
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
        command = brailleEvent.event["command"]

        user_bindings_map = settings.brailleBindingsMap
        if self.name in user_bindings_map:
            user_bindings = user_bindings_map[self.name]
        elif "default" in user_bindings_map:
            user_bindings = user_bindings_map["default"]

        if user_bindings and command in user_bindings:
            handler = user_bindings[command]
            consumed = handler.processInputEvent(self, brailleEvent)

        if (not consumed) and command in self.brailleBindings:
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

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """
        pass

    def isActivatableEvent(self, event):
        """Returns True if the given event is one that should cause this
        script to become the active script.  This is only a hint to
        the focus tracking manager and it is not guaranteed this
        request will be honored.  Note that by the time the focus
        tracking manager calls this method, it thinks the script
        should become active.  This is an opportunity for the script
        to say it shouldn't.
        """
        return True

    def activate(self):
        """Called when this script is activated."""
        pass

    def deactivate(self):
        """Called when this script is deactivated."""
        pass
