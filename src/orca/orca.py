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
import mag
import script
import kbd
import debug
from rolenames import getRoleName # localized role names
from orca_i18n import _ # for gettext support

# List of all the running apps we know about.  Each element is a Python
# Accessible instance.
#
apps = []

# If True, this module has been initialized.
#
initialized = False


def buildAppList ():
    """Retrieves the list of currently running apps for the desktop and
    populates the apps list attribute with these apps.
    """
    
    global apps

    apps = []

    i = core.desktop.childCount-1
    while i >= 0:
        acc = core.desktop.getChildAtIndex (i)
        app = a11y.makeAccessible(acc)
        if app != None:
            apps.insert (0, app)
        i = i-1


def activateApp (app):
    """Called when a top-level window is activated.  It reloads the
    script associated with the top-level window's application and
    activates the script's keybindings.

    Arguments:
    - app: the Python Accessible instance representing the application
    """
    
    speech.stop ("default")

    s = script.getScript (app)
    debug.println ("ACTIVATED SCRIPT: " + s.name)
    kbd.keybindings = s.keybindings
    brl.onBrlKey = s.onBrlKey    
    

# Track

def onChildrenChanged (e):
    """Tracks children-changed events on the desktop to determine when
    apps start and stop.

    Arguments:
    - e: at-spi event from the at-api registry
    """
    
    if e.source == core.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        #
        if core.desktop.childCount == 0:
            speech.say ("default", _("User logged out - shutting down."))
            shutdown ()
            return

        # Otherwise, an application has been created or removed.
        #
        if e.type == "object:children-changed:add":
            obj = core.desktop.getChildAtIndex (e.detail1)
            app = a11y.makeAccessible (obj)
        elif e.type == "object:children-changed:remove":
            try:
                # [[[TODO: WDW - understand why the e.detail1 app might
                # not always be in the apps list.]]]
                #
                app = apps[e.detail1]
                script.deleteScript (app)
            except:
                pass
            
        # [[[TODO: WDW - Note the call to buildAppList - that will update the
        # apps[] list.  If this logic is changed in the future, the apps list
        # will most likely needed to be updated here.]]]
        #
        buildAppList ()

    
def onWindowActivated (e):
    """When toplevel windows are activated, reload the script
    associated with the window's application and set the script's
    keybidings as the active bindings.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    acc = a11y.makeAccessible (e.source)
    activateApp (acc.app)


class Event:
   """Dummy class for converting the source of an event to an
   Accessible object.  We need this since the core.event object we
   get from the core is read-only.  So, we create this dummy event
   object to contain a copy of all the event members with the source
   converted to an Accessible.
   """

   pass


def processEvent (e):
    """Handles all events destined for scripts.  [[[TODO: WDW - the event
    type we received can be more specific than the event type we registered
    for.  We need to handle this.]]] [[[TODO: WDW - there may not be an
    active app.  We need to handle this.]]]

    Arguments:
    - e: an at-spi event.
    """
    
    # Create an Accessible for the source
    #
    source = a11y.makeAccessible (e.source)

    # Copy relevant details from the event.
    #
    event = Event ()
    event.type = e.type
    event.detail1 = e.detail1
    event.detail2 = e.detail2
    event.any_data = e.any_data
    event.source = source

    #debug.println ("Event: type=(" + event.type + ")")
    #debug.listDetails("       ", source)
                       
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
        if source.state.count (core.Accessibility.STATE_DEFUNCT) == 0:
            sys.stderr.write ("ERROR: app not found; source=(" + source.name 
                              + ") event = " + event.type + ").\n")

    s = script.getScript (source.app)

    found = False
    keys = s.listeners.keys()
    for key in s.listeners.keys():
        if e.type.startswith(key):
            func = s.listeners[key]
            found = True
            break

    if found == True:
        # We do not want orca to crash if an ill-behaved script causes
        # an exception.
        #
        try:
            func (event)
        except:
            debug.printException ()


def findActiveWindow ():
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
            if state.count (core.Accessibility.STATE_ACTIVE) > 0:
                return app.child(i)
            i = i+1

    return None



def init ():
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

    a11y.init ()
    kbd.init ()
    if getattr (settings, "useSpeech", True):
        speech.init ()
    
    # [[[TODO: WDW - do we need to register onBrlKey as a listener,
    # or....do we need to modify the brl module so that onBrlKey will
    # be called from the brl module?]]]
    #
    if getattr (settings, "useBraille", False):
        initialized = brl.init ()
        if initialized:
            debug.println ("Braille module has been initialized.")
        else:
            debug.println ("Braille module has NOT been initialized.")

    if getattr (settings, "useMagnifier", False):
        mag.init ()

    # Build list of accessible apps.
    #
    buildAppList ()

    # Create and load an app's script when it is added to the desktop
    #
    core.registerEventListener (onChildrenChanged, "object:children-changed:")

    # Reload a script's modules and activate it's keybindings when a
    # toplevel of the application is activated
    #
    core.registerEventListener (onWindowActivated, "window:activate")

    # Register for all the at-api events we may ever care about.
    #
    for type in a11y.dispatcher.values():
        core.registerEventListener (processEvent, type)

    initialized = True
    return True


def start ():
    """Starts orca and also the bonobo main loop.

    Returns False only if this module has not been initialized.
    """

    global initialized
    
    if not initialized:
        return False

    speech.say ("default", _("Welcome to Orca."))

    try:
        brl.clear ()
        brl.addRegion (_("Welcome to Orca."), 16, 0)
        brl.refresh ()
    except:
        debug.printException ()
    
    # Find the cusrrently active toplevel window and activate its script.
    #
    win = findActiveWindow ()
    if win:
        activateApp (win.app)

        # Generate a fake window activation event so the application
        # can tell the user about itself.
        #
        e = Event ()
        e.source = win
        e.type = "window:activate"
        e.detail1 = 0
        e.detail2 = 0
        e.any_data = None
    
        try:
            s = script.getScript (win.app)
            s.listeners["window:activate"] (e)
        except:
            debug.printException ()

    core.bonobo.main ()


def shutdown ():
    """Stop orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """
    
    global initialized
    global apps

    if not initialized:
        return False

    speech.say ("default", _("goodbye."))
    brl.clear ()
    brl.addRegion (_("Goodbye."), 8, 0)
    brl.refresh ()

    # Deregister our event listeners
    #
    core.unregisterEventListener (onChildrenChanged,
                                  "object:children-changed:")
    for key in a11y.dispatcher.keys():
        core.unregisterEventListener (processEvent, key)

    # Shutdown all the other support.
    #
    kbd.shutdown ()
    a11y.shutdown ()
    if getattr (settings, "useSpeech", True):
        speech.shutdown ()
    if getattr (settings, "useBraille", False):
        brl.shutdown ();
    if getattr (settings, "useMagnifier", False):
        mag.shutdown ();

    core.bonobo.main_quit ()

    initialized = False
    return True
