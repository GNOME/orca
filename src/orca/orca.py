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
import script
import kbd
from orca_i18n import _ # for gettext support

# Dictionary that maintains all the scripts known to orca.  The keys
# are the Accessible.app attributes, which are Accessibility_Application
# instances.  The values are Script instances.  [[[TODO: WDW - I have been
# told there are bugs in apps at-spi implementations that prevent us from
# getting an app from an accessible.  This could cause issues with finding
# scripts.
#
scripts = {}

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
        try:
            app = a11y.makeAccessible(acc)
            if app != None:
                apps.insert (0, app)
        except:
            pass
        i = i-1


def activateApp (app):
    """Called when a top-level window is activate.  It reloads the
    script associated with the top-level window's application and
    activates the script's keybindings.

    Arguments:
    - app: the Python Accessible instance representing the application
    """
    
    global scripts

    speech.stop ("default")

    try:
        s = scripts[app]
    except:
        sys.stderr.write ("No script found for " + app.name + ".\n")
        return

    s.reload ()

    # Make this scripts keybindings active
    #
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
            s = script.Script (app)
            s.load ()
            scripts[app] = s
        elif e.type == "object:children-changed:remove":
            app = apps[e.detail1]
            del scripts[app]
            
        # [[[WDW - Note the call to buildAppList - that will update
        # the apps[] list.  If this logic is changed in the future,
        # the apps list will most likely needed to be updated here.
        #
        buildAppList ()

    
def onWindowActivated (e):
    """When toplevel windows are activated, reload the script
    associated with the window's application and set the script's
    keybidings as the active bindings.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    activateApp (a11y.makeAccessible(e.source).app)


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
    
    global scripts
    
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

    # See if we have a script for this event.  [[[TODO: WDW - probably
    # should take into account if the app is active or not.  Perhaps the
    # script for the app should do this as it might be the best one to
    # determine if it should speak or not.]]]
    #
    if source.app is None:
        sys.stderr.write ("App not found for " + source.name
                          + " (event.type = " + e.type + ").\n")
    else:
        try:
            s = scripts[source.app]
            func = s.listeners[e.type]
            func (event)
        except:
            pass
    

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
    if settings.useSpeech:  speech.init ()
    
    # [[[TODO: WDW - do we need to register onBrlKey as a listener,
    # or....do we need to modify the brl module so that onBrlKey will
    # be called from the brl module?]]]
    #
    if settings.useBraille: brl.init ()
    
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

    # Attempt to load scripts for all currently running apps
    #
    for app in apps:
        s = script.Script (app)
        scripts[app] = s
        s.load ()

    initialized = True
    return True


def start ():
    """Starts orca and also the bonobo main loop.

    Returns False only if this module has not been initialized.
    """

    global initialized
    global scripts
    
    if not initialized:
        return False

    speech.say ("default", _("Welcome to Orca."))

    # Find the currently active toplevel window and activate its script.
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
            s = scripts[win.app]
            s.listeners["window:activate"](e)
        except:
            pass

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
    if settings.useSpeech:  speech.shutdown ()
    if settings.useBraille: brl.shutdown ();

    core.bonobo.main_quit ()

    initialized = False
    return True
