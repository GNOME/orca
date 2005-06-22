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

import gtk
import pygtk
import sys

import a11y
import braille
import core
import debug
import focus_tracking_presenter
import hierarchical_presenter
import kbd
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import script
import settings
import speech

from rolenames import getRoleName # localized role names
from orca_i18n import _           # for gettext support


# If True, this module has been initialized.
#
_initialized = False


# The known presentation managers.
#
_PRESENTATION_MANAGERS = [focus_tracking_presenter,
                          hierarchical_presenter]

# The current presentation manager, which is an index into the
# _PRESENTATION_MANAGERS list.
#
_currentPresentationManager = -1


def _switchToPresentationManager(index):
    """Switches to the given presentation manager.

    Arguments:
    - index: an index into _PRESENTATION_MANAGERS
    """

    global _currentPresentationManager
    
    if _currentPresentationManager > 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()

    _currentPresentationManager = index

    # Wrap the presenter index around.
    #
    if _currentPresentationManager >= len(_PRESENTATION_MANAGERS):
        _currentPresentationManager = 0
    elif _currentPresentationManager < 0:
        _currentPresentationManager = len(_PRESENTATION_MANAGERS) - 1
        
    _PRESENTATION_MANAGERS[_currentPresentationManager].activate()


def _switchToNextPresentationManager():
    """Switches to the next presentation manager."""

    global _currentPresentationManager
    
    _switchToPresentationManager(_currentPresentationManager + 1)

    
########################################################################
#                                                                      #
# METHODS TO HANDLE APPLICATION LIST AND FOCUSED OBJECTS               #
#                                                                      #
########################################################################

# List of all the running apps we know about.  Each element is a Python
# Accessible instance.
#
apps = []


# The Accessible application whose window currently has focus
#
focusedApp = None


# The Accessible that currently has keyboard focus
#
focusedObject = None


def _buildAppList():
    """Retrieves the list of currently running apps for the desktop and
    populates the apps list attribute with these apps.
    """
    
    global apps

    apps = []

    i = core.desktop.childCount-1
    while i >= 0:
        acc = core.desktop.getChildAtIndex(i)
        app = a11y.makeAccessible(acc)
        if app != None:
            apps.insert(0, app)
        i = i-1


def findActiveWindow():
    """Traverses the list of known apps looking for one who has an
    immediate child (i.e., a window) whose state includes the active state.

    Returns the Python Accessible of the window that's active or None if
    no windows are active.
    """
    
    global apps
    
    for app in apps:
        i = 0
        while i < app.childCount:
            state = app.child(i).state
            if state.count(core.Accessibility.STATE_ACTIVE) > 0:
                return app.child(i)
            i = i+1

    return None


def onChildrenChanged(e):
    """Tracks children-changed events on the desktop to determine when
    apps start and stop.

    Arguments:
    - e: at-spi event from the at-api registry
    """
    
    if e.source == core.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        #
        if core.desktop.childCount == 0:
            speech.say("default", _("User logged out - shutting down."))
            shutdown()
            return

        # [[[TODO: WDW - Note the call to _buildAppList - that will update the
        # apps[] list.  If this logic is changed in the future, the apps list
        # will most likely needed to be updated here.]]]
        #
        _buildAppList()

    
def onWindowActivated(e):
    """Keeps track of the application whose window has focus.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    global focusedApp
    
    acc = a11y.makeAccessible(e.source)
    focusedApp = acc.app


def onFocus(e):
    """Keeps track of object and application with focus.

    Arguments:
    - e: at-spi event from the at-api registry
    """
    
    global focusedObject
    global focusedApp

    focusedObject = a11y.makeAccessible(e.source)
    focusedApp = focusedObject.app


########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING AT-SPI OBJECT EVENTS        #
#                                                                      #
# AT-SPI events are receieved here and converted into a Python object  #
# for processing by the rest of Orca.  [[[TODO: WDW - this might be a  #
# spot to coalesce and massage AT-SPI events into events useful to a   #
# screen reader.]]]                                                    #
#                                                                      #
########################################################################

class Event:
   """Dummy class for converting the source of an event to an
   Accessible object.  We need this since the core.event object we
   get from the core is read-only.  So, we create this dummy event
   object to contain a copy of all the event members with the source
   converted to an Accessible.
   """
   pass


def processObjectEvent(e):
    """Handles all events destined for scripts.  [[[TODO: WDW - the event
    type we received can be more specific than the event type we registered
    for.  We need to handle this.]]] [[[TODO: WDW - there may not be an
    active app.  We need to handle this.]]]

    Arguments:
    - e: an at-spi event.
    """
    
    global _currentPresentationManager
    
    # Create an Accessible for the source
    #
    if e.type == "object:state-changed:defunct":
        source = None
    else:
        source = a11y.makeAccessible(e.source)

    # Copy relevant details from the event.
    #
    event = Event()
    event.type = e.type
    event.detail1 = e.detail1
    event.detail2 = e.detail2
    event.any_data = e.any_data
    event.source = source

    debug.printObjectEvent(debug.LEVEL_FINEST, event)
    debug.listDetails(debug.LEVEL_FINEST, "       ", source)

    # [[[TODO: WDW - probably should check for index out of bounds.]]]
    #
    _PRESENTATION_MANAGERS[_currentPresentationManager].processObjectEvent(\
        event)


########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################

def debugListApps():
    """Prints a list of all known applications to stdout if debug
    is enabled."""

    debug.listApps(debug.LEVEL_OFF)
    return True 

def debugListActiveApp():
    """Prints details about the currently active application."""

    debug.listActiveApp(debug.LEVEL_OFF)
    return True 


########################################################################
#                                                                      #
# METHODS FOR HANDLING THE INITIALIZATION, SHUTDOWN, AND USE.          #
#                                                                      #
########################################################################

def init():
    """Initialize the orca module, which initializes a11y, kbd, speech,
    and braille modules.  Also builds up the application list, registers
    for at-spi events, and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """
    
    global _initialized
    global apps
    
    if _initialized:
        return False

    a11y.init()
    kbd.init(processKeyEvent)
    if settings.getSetting("useSpeech", True):
        speech.init()
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has been initialized.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")
        
    if settings.getSetting("useBraille", False):
        braille.init(7)

    if settings.getSetting("useMagnifier", False):
        mag.init()
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has been initialized.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has NOT been initialized.")

    # Build list of accessible apps.
    #
    _buildAppList()

    # Create and load an app's script when it is added to the desktop
    #
    core.registerEventListener(onChildrenChanged, "object:children-changed:")

    # Keep track of the application with focus.
    #
    core.registerEventListener(onWindowActivated, "window:activate")

    # Keep track of the object with focus.
    #
    core.registerEventListener(onFocus, "focus:")
    
    # Register for all the at-api events we may ever care about.
    # [[[TODO: WDW - this probably should be stuffed in the
    # focus_tracking_presenter?]]]]
    #
    for type in script.EVENT_MAP.values():
        core.registerEventListener(processObjectEvent, type)

    _initialized = True
    return True


def start():
    """Starts orca and also the bonobo main loop.

    Returns False only if this module has not been initialized.
    """

    global _initialized
    
    if not _initialized:
        return False

    try:
        speech.say("default", _("Welcome to Orca."))
        braille.displayMessage(_("Welcome to Orca."))
    except:
        debug.printException(debug.LEVEL_SEVERE)
    
    # Find the cusrrently active toplevel window and activate its script.
    #
    win = findActiveWindow()
    if win:
        focusedApp = win.app

    _switchToPresentationManager(0) # focus_tracking_presenter

    core.bonobo.main()


def shutdown():
    """Stop orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """
    
    global _initialized
    global apps

    if not _initialized:
        return False

    speech.say("default", _("goodbye."))
    braille.displayMessage(_("Goodbye."))

    # Deregister our event listeners
    #
    core.unregisterEventListener(onChildrenChanged,
                                 "object:children-changed:")
    core.unregisterEventListener(onWindowActivated,
                                 "window:activate")
    core.unregisterEventListener(onFocus,
                                 "focus:")
    for key in script.EVENT_MAP.keys():
        core.unregisterEventListener(processObjectEvent, key)

    # Shutdown all the other support.
    #
    kbd.shutdown() # automatically unregisters processKeyEvent
    a11y.shutdown()
    if settings.getSetting("useSpeech", True):
        speech.shutdown()
    if settings.getSetting("useBraille", False):
        braille.shutdown();
    if settings.getSetting("useMagnifier", False):
        mag.shutdown();

    core.bonobo.main_quit()

    _initialized = False
    return True


########################################################################
#                                                                      #
# METHODS FOR DRAWING RECTANGLES AROUND OBJECTS ON THE SCREEN          #
#                                                                      #
########################################################################

# The last drawn rectangle.  This is used for remembering what we
# need to erase on the screen.
#
_visibleRectangle = None

def outlineAccessible(accessible):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    global _visibleRectangle

    display = None
    
    try:
        display = gtk.gdk.display_get_default()
    except:
        display = gtk.gdk.display(":0")

    if display is None:
        debug.println(debug.LEVEL_SEVERE,
                      "orca.outlineAccessible could not open display.")
        return
    
    screen = display.get_default_screen()
    root_window = screen.get_root_window()
    graphics_context = root_window.new_gc()
    graphics_context.set_subwindow(gtk.gdk.INCLUDE_INFERIORS)
    graphics_context.set_function(gtk.gdk.INVERT)
    graphics_context.set_line_attributes(3,                  # width
                                         gtk.gdk.LINE_SOLID, # style
                                         gtk.gdk.CAP_BUTT,   # end style
                                         gtk.gdk.JOIN_MITER) # join style

    # Erase the old rectangle.
    #
    if _visibleRectangle:
        root_window.draw_rectangle(graphics_context,
                                   False,                    # Fill
                                   _visibleRectangle.x,
                                   _visibleRectangle.y,
                                   _visibleRectangle.width,
                                   _visibleRectangle.height)
        _visibleRectangle = None

    if accessible:
        component = a11y.getComponent(accessible)
        if component:
            _visibleRectangle = component.getExtents(0) # coord type = screen
            root_window.draw_rectangle(graphics_context,
                                       False,                  # Fill
                                       _visibleRectangle.x,
                                       _visibleRectangle.y,
                                       _visibleRectangle.width,
                                       _visibleRectangle.height)

    
########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING KEYBOARD EVENTS.            #
#                                                                      #
# All keyboard events are funnelled through here first.  Orca itself   #
# might have global keybindings (e.g., to switch between presenters),  #
# but it will typically pass the event onto the currently active       #
# active presentation manager.                                         #
#                                                                      #
########################################################################

# Keybindings that Orca itself cares about.
#
_keybindings = {}
_keybindings["F12"] = shutdown
_keybindings["F5"]  = debugListApps
_keybindings["F6"]  = debugListActiveApp
_keybindings["F8"]  = _switchToNextPresentationManager

# The string representing the last key pressed.
#
lastKey = None


def _getModifierString(modifier):
    """Converts a set of modifer states into a text string

    Arguments:
    - modifer: the modifiers field from an at-spi DeviceEvent

    Returns a string consisting of modifier names separated by "+"'s.
    """
    
    s = ""
    l = []

    # [[[TODO: WDW - need to consider all modifiers: SHIFT, SHIFTLOCK,
    # NUMLOCK, META, META2, META3.  Some of these may be handled via the
    # actual key symbol (e.g., upper or lower case), but others may not.]]]
    #
    if modifier & (1 << core.Accessibility.MODIFIER_CONTROL):
        l.append("control")
    if modifier & (1 << core.Accessibility.MODIFIER_ALT):
        l.append("alt")
    if modifier & (1 << core.Accessibility.MODIFIER_META):
        l.append("meta")
    if modifier & (1 << core.Accessibility.MODIFIER_META2):
        l.append("meta2")
    if modifier & (1 << core.Accessibility.MODIFIER_META3):
        l.append("meta3")
    for mod in l:
        if s == "":
            s = mod
        else:
            s = s + "+" + mod
    return s


def _keyEcho(key):
    """If the keyEcho setting is enabled, echoes the key via speech.
    Uppercase keys will be spoken using the "uppercase" voice style,
    whereas lowercase keys will be spoken using the "default" voice style.

    Arguments:
    - key: a string representing the key name to echo.
    """
    
    if not settings.getSetting("keyEcho", False):
        return
    if key.isupper():
        speech.say("uppercase", key)
    else:
        speech.say("default", key)


def processKeyEvent(event):
    """The primary key event handler for Orca.  Keeps track of various
    attributes, such as the lastKey and insertPressed.  Also calls
    keyEcho as well as any function that may exist in the _keybindings
    dictionary for the key event.  This method is called synchronously
    from the at-spi registry and should be performant.  In addition, it
    must return True if it has consumed the event (and False if not).
    
    Arguments:
    - event: an at-spi DeviceEvent

    Returns True if the event should be consumed.
    """
    
    global lastKey
    global _currentPresentationManager

    keystring = ""

    #print "KEYEVENT: type=%d" % event.type
    #print "          hw_code=%d" % event.hw_code
    #print "          modifiers=%d" % event.modifiers
    #print "          event_string=(%s)" % event.event_string, len(event.event_string)
    #print "          is_text=", event.is_text

    event_string = event.event_string
    if event.type == core.Accessibility.KEY_PRESSED_EVENT:
        # The control characters come through as control characters, so we
        # just turn them into their ASCII equivalent.  NOTE that the upper
        # case ASCII characters will be used (e.g., ctrl+a will be turned into
        # the string "control+A").  All these checks here are to just do some
        # sanity checking before doing the conversion. [[[TODO: WDW - this is
        # making assumptions about mapping ASCII control characters to to
        # UTF-8, I think.]]]
        #
        if (event.modifiers & (1 << core.Accessibility.MODIFIER_CONTROL)) \
           and (not event.is_text) and (len(event.event_string) == 1):
            value = ord(event.event_string[0])
            if value < 32:
                event_string = chr(value + 0x40)

        mods = _getModifierString(event.modifiers)

        if mods:
            keystring = mods + "+" + event_string
        else:
            keystring = event_string

        # Key presses always interrupt speech - If say all mode is
        # enabled, a key press stops it
        #
        if speech.sayAllEnabled:
            speech.stopSayAll()
        else:
            speech.stop("default")
            
    if keystring:
        lastKey = keystring
        debug.printKeyEvent(debug.LEVEL_FINE, keystring)
        _keyEcho(keystring)

        # Orca gets first stab at the event.  Then, the presenter gets
        # a shot.
        #
        if _keybindings.has_key(keystring):
            try:
                func = _keybindings[keystring]
                return func()
            except:
                debug.printException(debug.LEVEL_SEVERE)
                return False
        else:
            return _PRESENTATION_MANAGERS[_currentPresentationManager].\
                   processKeyEvent(keystring)

    return False
