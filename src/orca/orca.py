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

# List of running apps

apps = []
appnames = []

# Build the list of currently runing apps

def buildAppList ():
    global apps
    global appnames

    apps = []
    appnames = []

    i = core.desktop.childCount-1
    while i >= 0:
        app = core.desktop.getChildAtIndex (i)
        if app:
            apps.insert (0, app)
            appnames.insert (0, app.name)
        i = i-1

# Track children-changed events on the desktop to determine when apps
# start and stop

def onChildrenChanged (event):

    if event.source == core.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        
        if core.desktop.childCount == 0:
            speech.say ("default", _("User logged out - shutting down."))
            shutdown ()
            return

        if event.type == "object:children-changed:add":
            app = core.desktop.getChildAtIndex (event.detail1)
            script.load (app.name)
        if event.type == "object:children-changed:remove":
            if script.isLoaded (appnames[event.detail1]):
                script.unload (appnames[event.detail1])
        buildAppList ()
    
# Activate scripts when their apps' toplevel windows are activated

def onWindowActivated (event):

    # Clear the Braille display on Window Activations

    brl.clear ()
    app = event.source.parent
    script.activate (app.name)
    try:
        func = script.active.onWindowActivated
    except:
        func = None
    if func:
        func (event)

# Orca initialized

initialized = False

def init ():
    global initialized
    global appnames
    
    if initialized:
        return False

    # Initialize the core

    core.init ()

    # Initialize a11y support

    a11y.init ()

    # Initialize keyboard hooks

    kbd.init ()

    # Setup speakers

    speech.init ()

    # Initialize Braille support

    brl.init ()

    # Build list of accessible apps

    buildAppList ()

    core.registerEventListener (onChildrenChanged, "object:children-changed:")
    core.registerEventListener (onWindowActivated, "window:activate")

    # Load the default script

    script.load ("default")

    # Activate the default script

    script.activate ("default")

    # Attempt to load scripts for all currently running apps

    for name in appnames:
        script.load (name)

    initialized = True
    return True

# Start Orca - This starts the Bonobo main loop

def start ():
    global initialized

    if not initialized:
        return False
    core.bonobo.main ()


# Stop Orca - This cleans up resources and quits the Bonobo main loop

def shutdown ():
    global initialized
    global apps
    global appnames

    if not initialized:
        return False

    speech.say ("default", _("goodbye."))

    del apps
    del appnames

    # Deregister our event listeners

    core.unregisterEventListener (onChildrenChanged, "object:children-changed:")
    core.unregisterEventListener (onWindowActivated, "window:activate")

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

    # Shutdown the core

    core.shutdown ()

    initialized = False
    return True
