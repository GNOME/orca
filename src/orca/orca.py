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

# Accessibility support

import a11y
import core

# Import user settings

import settings

# Speech support

import speech

# Braille support

import brl

# Script management

import script

# Keyboard hooks

import kbd

# Orca i18n

from orca_i18n import _

# This dictionary contains references to all the loded scripts

scripts = {}

# List of running apps

apps = []

# Build the list of currently runing apps

def buildAppList ():
    global apps

    apps = []

    i = core.desktop.childCount-1
    while i >= 0:
        acc = core.desktop.getChildAtIndex (i)
        try:
            app = a11y.Accessible.cache[acc]
        except:
            if acc == None:
                app = None
            else:
                app = a11y.Accessible (acc)
        if app != None:
            apps.insert (0, app)
        i = i-1

# This function is called when a toplevel window is activated -- it
# reloads the script associated with the toplevel window's
# application, and activates the script's keybindings

def activateApp (app):
    global scripts

    # Stop speech when a new window is activated

    speech.stop ("default")

    # Find the script for this app

    try:
        s = scripts[app]
    except:
        print "no script found for " + app.name
        return

    # Reload the script

    s.reload ()

    # Make this scripts keybindings active

    kbd.keybindings = s.keybindings
    brl.onBrlKey = s.onBrlKey
    

# Track children-changed events on the desktop to determine when apps
# start and stop

def onChildrenChanged (e):

    if e.source == core.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        
        if core.desktop.childCount == 0:
            speech.say ("default", _("User logged out - shutting down."))
            shutdown ()
            return

        if e.type == "object:children-changed:add":
            obj = core.desktop.getChildAtIndex (e.detail1)
            app = a11y.makeAccessible (obj)
            s = script.script (app)
            s.load ()
            scripts[app] = s
        elif e.type == "object:children-changed:remove":
            app = apps[e.detail1]
            del scripts[app]
        buildAppList ()
    
# When toplevel windows are activated, reload the script associated
# with the window's application and set the script's keybidings as the
# active bindings

def onWindowActivated (e):
    activateApp (a11y.makeAccessible(e.source).app)

# Dummy class for converting the source of an event to an Accessible
# object -- we need this since the core.event object we get from the
# core is read-only-- so we create this dummy event object to contain
# a copy of all the event members with the source converted to an
# Accessible

class Event:
    pass

# This function process *all* events destined for scripts

def processEvent (e):
    global scripts
    
    # Create an Accessible for the source

    source = a11y.makeAccessible (e.source)

    # Convert the event source to an Accessible

    event = Event ()
    event.type = e.type
    event.detail1 = e.detail1
    event.detail2 = e.detail2
    event.any_data = e.any_data
    event.source = source

    # See if we have a script for this event

    if source.app is None:
        print "app not found"
    else:
        try:
            s = scripts[source.app]
        except:
            s = None
        if s is not None:
            try:
                func = s.listeners[e.type]
            except:
                func = None
            if func is not None:
                func (event)
    
# Find the currently active toplevel window

def findActiveWindow ():
    global apps
    
    # Travers through the list of known apps

    for app in apps:
        
        # Traverse through all the toplevels of each app, looking for one with state active

        i = 0
        while i < app.childCount:
            state = app.child(i).state
            if state.count (core.Accessibility.STATE_ACTIVE) > 0:
                return app.child(i)
            i = i+1
    return None

# Orca initialized

initialized = False

def init ():
    global initialized
    global apps
    
    if initialized:
        return False

    # Initialize a11y support

    a11y.init ()

    # Initialize keyboard hooks

    kbd.init ()

    # Setup speakers

    speech.init ()

    # Initialize Braille support

    if settings.useBraille:
        brl.init ()

    # Build list of accessible apps

    buildAppList ()

    # Create and load an app's script when it is added to the desktop

    core.registerEventListener (onChildrenChanged, "object:children-changed:")

    # Reload a script's modules and activate it's keybindings when a toplevel of the application is activated

    core.registerEventListener (onWindowActivated, "window:activate")

    # a11y.dispatcher has a list of all the listeners we should register

    for type in a11y.dispatcher.values():
        core.registerEventListener (processEvent, type)

    # Attempt to load scripts for all currently running apps

    for app in apps:

        # Create a script for this application and add it to our list of scripts

        s = script.script (app)
        scripts[app] = s

        # Load the script

        s.load ()

    initialized = True
    return True

# Start Orca - This starts the Bonobo main loop

def start ():
    global initialized
    global scripts
    

    if not initialized:
        return False

    speech.say ("default", _("Welcome to Orca."))

    # Find the currently active toplevel window

    win = findActiveWindow ()

    if win:


        # Active the script for this window

        activateApp (win.app)

        # Find the script for this app

        s = scripts[win.app]

        # Generate a fake window activation event so we get some feedback
        # as to what window is active

        e = Event ()
        e.source = win
        e.type = "window:activate"
        e.detail1 = 0
        e.detail2 = 0
        e.any_data = None
    
        # Send our fake event to the script -- this may fail if for some
        # reason the script doesn't have an onWindowActivated function

        try:
            s.listeners["window:activate"](e)
        except:
            pass

    core.bonobo.main ()


# Stop Orca - This cleans up resources and quits the Bonobo main loop

def shutdown ():
    global initialized
    global apps

    if not initialized:
        return False

    speech.say ("default", _("goodbye."))

    # Deregister our event listeners

    core.unregisterEventListener (onChildrenChanged, "object:children-changed:")

    # a11y.dispatcher has a list of all the listeners we should unregister

    for key in a11y.dispatcher.keys():
        core.unregisterEventListener (processEvent, key)

    # Shutdown the keyboard support

    kbd.shutdown ()

    # Shutdown accessibility utility functions

    a11y.shutdown ()

    # Shutdown Braille support

    brl.shutdown ();

    # Shutdown speech support

    speech.shutdown ()

    # Shutdown Bonobo

    core.bonobo.main_quit ()

    initialized = False
    return True
