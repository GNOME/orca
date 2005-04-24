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

import sys
import a11y
import core
import settings  # user settings
import speech
import brl
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import script
import kbd
import debug
from rolenames import getRoleName # localized role names
from orca_i18n import _ # for gettext support


# List of all the running apps we know about.  Each element is a Python
# Accessible instance.
#
apps = []


# The Accessible that currently has keyboard focus
#
focusedObject = None


# The Accessible application whose window currently has focus
#
focusedApp = None


# If True, this module has been initialized.
#
initialized = False


def buildAppList():
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


def activateApp(app):
    """Called when a top-level window is activated.  It reloads the
    script associated with the top-level window's application and
    activates the script's keybindings.

    Arguments:
    - app: the Python Accessible instance representing the application
    """
    
    speech.stop("default")

    s = script.getScript(app)
    debug.println(debug.LEVEL_FINE, "ACTIVATED SCRIPT: " + s.name)
    kbd.keybindings = s.keybindings
    brl.onBrlKey = s.onBrlKey    
    

# Track

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

        # Otherwise, an application has been created or removed.
        #
        if e.type == "object:children-changed:add":
            obj = core.desktop.getChildAtIndex(e.detail1)
            app = a11y.makeAccessible(obj)
        elif e.type == "object:children-changed:remove":
            try:
                # [[[TODO: WDW - understand why the e.detail1 app might
                # not always be in the apps list.]]]
                #
                app = apps[e.detail1]
                script.deleteScript(app)
            except:
                pass
            
        # [[[TODO: WDW - Note the call to buildAppList - that will update the
        # apps[] list.  If this logic is changed in the future, the apps list
        # will most likely needed to be updated here.]]]
        #
        buildAppList()

    
def onWindowActivated(e):
    """When toplevel windows are activated, reload the script
    associated with the window's application and set the script's
    keybidings as the active bindings.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    global focusedApp
    
    acc = a11y.makeAccessible(e.source)
    focusedApp = acc.app
    activateApp(focusedApp)


def onFocus(e):
    """Core module event listener called when focus changes.  Saves
    away the associated application in the focusedApp attribute and the
    associated object in the focusedObject attribute.

    Arguments:
    - e: at-spi event from the at-api registry
    """
    
    global focusedObject
    global focusedApp

    focusedObject = a11y.makeAccessible(e.source)

    # We need this hack fo the time being due to a bug in Nautilus,
    # which makes it impossible to traverse to the application from
    # some objects within Nautilus.  [[[TODO: WDW - removed this because
    # it was causing a very odd interaction with Mozilla.]]]
    #
    #focusedObject.app = focusedApp


class Event:
   """Dummy class for converting the source of an event to an
   Accessible object.  We need this since the core.event object we
   get from the core is read-only.  So, we create this dummy event
   object to contain a copy of all the event members with the source
   converted to an Accessible.
   """

   pass


def processEvent(e):
    """Handles all events destined for scripts.  [[[TODO: WDW - the event
    type we received can be more specific than the event type we registered
    for.  We need to handle this.]]] [[[TODO: WDW - there may not be an
    active app.  We need to handle this.]]]

    Arguments:
    - e: an at-spi event.
    """
    
    # Create an Accessible for the source
    #
    source = a11y.makeAccessible(e.source)

    # Copy relevant details from the event.
    #
    event = Event()
    event.type = e.type
    event.detail1 = e.detail1
    event.detail2 = e.detail2
    event.any_data = e.any_data
    event.source = source

    debug.println(debug.LEVEL_FINEST, "EVENT: type=(" + event.type + ")")
    debug.listDetails(debug.LEVEL_FINEST, "       ", source)
                       
    # See if we have a script for this event.  Note that the event type in the
    # listeners dictionary may not be as specific as the event type we
    # received (e.g., the listeners dictionary might contain the key
    # "object:state-changed:" and the event.type might be
    # "object:state-changed:focused" So, we find the listener whose event type
    # begins with this event's type.  [[[TODO: WDW - the order of the
    # a11y.dispatcher table should reflect this; that is, it should be ordered
    # in terms of most specific type to most generic type.]]]  [[[TODO: WDW -
    # probably should take into account if the app is active or not.  Perhaps
    # the script for the app should do this as it might be the best one to
    # determine if it should speak or not.]]]
    #
    if source.app is None:
        set = source.state
        if source.state.count(core.Accessibility.STATE_DEFUNCT) == 0:
            sys.stderr.write("ERROR: app not found; source=(" + source.name 
                             + ") event = " + event.type + ").\n")
        
    s = script.getScript(source.app)

    found = False
    keys = s.listeners.keys()
    for key in s.listeners.keys():
        if e.type.startswith(key):
            func = s.listeners[key]
            found = True
            break

    if found:
        # We do not want orca to crash if an ill-behaved script causes
        # an exception.
        #
        try:
            debug.println(debug.LEVEL_FINE, \
                          "orca.processEvent: " \
                          + "source: name=(" + source.name + ") " \
                          + "role=(" + source.role + ")\n" \
                          + "                   " \
                          + "func:   (" + func.func_name + ")\n" \
                          + "                   " \
                          + "script: (" + s.name + ")")
            func(event)
        except:
            debug.printException(debug.LEVEL_SEVERE)


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


# This dictionary maps at-spi event names to Python function names
# which are to be used in scripts.  For example, it maps "focus:"
# events to call a script function called onFocus and
# "window:activate" to onWindowActivated.  [[[TODO: WDW - might
# consider moving this to the script module at some point.]]]
#
dispatcher = {}
dispatcher["onNameChanged"]             = "object:property-change:accessible-name"
dispatcher["onTextSelectionChanged"]    = "object:text-selection-changed"
dispatcher["onTextInserted"]            = "object:text-changed:insert"
dispatcher["onTextDeleted"]             = "object:text-changed:delete"
dispatcher["onStateChanged"]            = "object:state-changed:"
dispatcher["onValueChanged"]            = "object:value-changed:"
dispatcher["onSelectionChanged"]        = "object:selection-changed"
dispatcher["onCaretMoved"]              = "object:text-caret-moved"
dispatcher["onLinkSelected"]            = "object:link-selected"
dispatcher["onPropertyChanged"]         = "object:property-change:"
dispatcher["onSelectionChanged"]        = "object:selection-changed"
dispatcher["onActiveDescendantChanged"] = "object:active-descendant-changed"
dispatcher["onVisibleDataChanged"]      = "object:visible-changed"
dispatcher["onChildrenChanged"]         = "object:children-changed:"
dispatcher["onWindowActivated"]         = "window:activate"
dispatcher["onWindowCreated"]           = "window:create"
dispatcher["onWindowDeactivated"]       = "window:deactivate"
dispatcher["onWindowDestroyed"]         = "window:destroy"
dispatcher["onWindowDeactivated"]       = "window:deactivated"
dispatcher["onWindowMaximized"]         = "window:maximize"
dispatcher["onWindowMinimized"]         = "window:minimize"
dispatcher["onWindowRenamed"]           = "window:rename"
dispatcher["onWindowRestored"]          = "window:restore"
dispatcher["onWindowSwitched"]          = "window:switch"
dispatcher["onWindowTitlelized"]        = "window:titlelize"
dispatcher["onFocus"]                   = "focus:"


def init():
    """Initialize the orca module, which initializes a11y, kbd, speech,
    and braille modules.  Also builds up the application list, registers
    for at-spi events, and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """
    
    global initialized
    global apps
    
    if initialized:
        return False

    a11y.init()
    kbd.init()
    if getattr(settings, "useSpeech", True):
        speech.init()
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has been initialized.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")
        
    # [[[TODO: WDW - do we need to register onBrlKey as a listener,
    # or....do we need to modify the brl module so that onBrlKey will
    # be called from the brl module?]]]
    #
    if getattr(settings, "useBraille", False):
        initialized = brl.init()
        if initialized:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Braille module has been initialized.")
        else:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Braille module has NOT been initialized.")

    if getattr(settings, "useMagnifier", False):
        mag.init()
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has been initialized.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has NOT been initialized.")

    # Build list of accessible apps.
    #
    buildAppList()

    # Create and load an app's script when it is added to the desktop
    #
    core.registerEventListener(onChildrenChanged, "object:children-changed:")

    # Reload a script's modules and activate it's keybindings when a
    # toplevel of the application is activated.  Also keep track of
    # the application with focus.
    #
    core.registerEventListener(onWindowActivated, "window:activate")

    # Keep track of the object with focus.
    #
    core.registerEventListener(onFocus, "focus:")
    
    # Register for all the at-api events we may ever care about.
    #
    for type in dispatcher.values():
        core.registerEventListener(processEvent, type)

    initialized = True
    return True


def start():
    """Starts orca and also the bonobo main loop.

    Returns False only if this module has not been initialized.
    """

    global initialized
    
    if not initialized:
        return False

    try:
        speech.say("default", _("Welcome to Orca."))
        brl.clear()
        brl.addRegion(_("Welcome to Orca."), 16, 0)
        brl.refresh()
    except:
        debug.printException(debug.LEVEL_SEVERE)
    
    # Find the cusrrently active toplevel window and activate its script.
    #
    win = findActiveWindow()
    if win:
        activateApp(win.app)

        # Generate a fake window activation event so the application
        # can tell the user about itself.
        #
        e = Event()
        e.source = win
        e.type = "window:activate"
        e.detail1 = 0
        e.detail2 = 0
        e.any_data = None
    
        try:
            s = script.getScript(win.app)
            s.listeners["window:activate"](e)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    core.bonobo.main()


def shutdown():
    """Stop orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """
    
    global initialized
    global apps

    if not initialized:
        return False

    speech.say("default", _("goodbye."))
    brl.clear()
    brl.addRegion(_("Goodbye."), 8, 0)
    brl.refresh()

    # Deregister our event listeners
    #
    core.unregisterEventListener(onChildrenChanged,
                                 "object:children-changed:")
    for key in dispatcher.keys():
        core.unregisterEventListener(processEvent, key)

    # Shutdown all the other support.
    #
    kbd.shutdown()
    a11y.shutdown()
    if getattr(settings, "useSpeech", True):
        speech.shutdown()
    if getattr(settings, "useBraille", False):
        brl.shutdown();
    if getattr(settings, "useMagnifier", False):
        mag.shutdown();

    core.bonobo.main_quit()

    initialized = False
    return True
