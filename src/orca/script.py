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

# General utility functions

import core
import a11y

# User settings

import settings

# Keyboard hooks

import kbd

# Braille support

if settings.useBraille:
    import brl

# Default event dispatcher names

import dispatcher

# The EventListener class - Objects of this type are used by script
# objects to encapsulate the information containined by event listeners

class EventListener:
    def __init__(self, type, func):
        self.type = type
        self.func = func

    # Register the listener with the core module

    def register (self):

        core.registerEventListener (self.func, self.type)

    # deregister the event listener with at-spi

    def deregister (self):

        core.unregisterEventListener (self.func, self.type)

# The script class

class script:

    # Script object constructor

    def __init__ (self, appname):

        self.appname = appname

        # The keybindings script file name takes the form
        # appname-keybindings.py

        self.bindingsname = appname+"-keybindings"
        self.listeners = []
        self.keybindings = {}

    # Loads a script - Loads the app-specific script and keybindings
    # module.  It then searches the app-specific Python module for
    # event listener functions, and if it finds them, it registers
    # appropriate event listeners with the core module, and adds
    # references to the functions to th script object

    def load (self):

        # Load the default script and default keybindings

        default = __import__ ("default")
        defbindings = __import__ ("default-keybindings")

        # Load app-specific script and keybindings

        try:
            mod = __import__ (self.appname)
        except:
            mod = None
        try:
            bindings = __import__ (self.bindingsname)
        except:
            bindings = None

        # If the app-specific Python module has a function called
        # onBrlKey, this function should be used to handle Braille
        # display callbacks

        try:
            func = getattr (mod, "onBrlKey")
        except:
            try:
                func = getattr (default,"onBrlKey")
            except:
                func = None
        if func:
            self.onBrlKey = func

        # Connect event dispatchers - dispatcher.py defines the names
        # of functions that may be in a script for responding to
        # various types of events, and their corresponding at-spi
        # event names.  We iterate through the list of known event
        # handler names, and check to see if our app-specific module
        # has a function with each name.  If it does not, we look in
        # the default module.  If we find an event handler, we add it
        # to the script.

        for key in dispatcher.event.keys ():
            try:
                func = getattr (mod, key)
            except:
                try:
                    func = getattr (default, key)
                except:
                    func = None
            if func:
                type = dispatcher.event[key]
                l = EventListener (type, func)
                self.listeners.append (l)

        # Key binding sets are hash tables.  the keys are the string
        # names of key combinations, and the values are the names of
        # Python functions to call when the specified key is pressed.
        # first we connect all the default key bindings, and then we
        # iterate throuh the list of app-specific ones.  Any
        # app-specific keybinding that duplicates a default one
        # overrides it.

        for key in defbindings.keybindings.keys ():
                funcname = defbindings.keybindings[key]
                try:
                    func = getattr (mod, funcname)
                except:
                    try:
                        func = getattr (default, funcname)
                    except:
                        func = None
                if func:
                    self.keybindings[key] = func

        # Add app-specific keybindings - These override the defaults
        # if there are duplicates.

        if bindings:
            for key in bindings.keybindings.keys ():
                funcname = bindings.keybindings[key]
                try:
                    func = getattr (mod, funcname)
                except:
                    try:
                        func = getattr (default, funcname)
                    except:
                        func = None
                    if func:
                        self.keybindings[key] = func

        return True

    # Activate the script - This function registers all the event
    # listeners and registers the appropriate keybindings

    def activate (self):

        # Register all the listeners

        for l in self.listeners:
            l.register ()

        # Activate the keybindings

        kbd.keybindings = self.keybindings

        # Activate the onBrlKey callback

        if settings.useBraille:
            brl.registerCallback (self.onBrlKey)
        
    # Deactivate the script - This deregisters all event listeners and
    # keybindings

    def deactivate (self):

        # Deregister all the listeners

        for l in self.listeners:
            l.deregister ()

        # Deactivate keybindings

        kbd.keybindings = None

        # Deactivate the onBrlKey callback

        if settings.useBraille:
            brl.unregisterCallback ()

# A dictionary of the currently loaded scripts

scripts = {}

# A reference to the currently active script

active = None

# Function to load a script

def load (name):
    global scripts

    try:
        s = scripts[name]
        return False
    except:
        pass
    s = script (name)
    s.load ()
    scripts[name] = s
    return True

# Function to unload a script

def unload (name):
    global scripts

    try:
        del scripts[name]
        return True
    except:
        return False

# Determine whether a script is loaded

def isLoaded (name):
    global scripts

    try:
        script = scripts[name]
        return True
    except:
        return False

# Activate a particular script

def activate (name):
    global scripts
    global active

    if active:
        if active.appname != name:
            active.deactivate ()
        else:
            return False
    try:
        active = scripts[name]
        active.activate ()
        return True
    except:
        return False

