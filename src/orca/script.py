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

# The EventListener class - Objects of this type are used by script
# objects to encapsulate the information containined by event listeners

# The script class

class script:

    # Script object constructor

    def __init__ (self, app):

        # Store a reference to the app

        self.app = app

        # Make an empty dictionary of event listeners

        self.listeners = {}

        # Setup empty keybindings

        self.keybindings = {}

    # Loads a script - Loads the app-specific script and keybindings
    # module.  It then searches the app-specific Python module for
    # event listener functions, and if it finds them, it registers
    # appropriate event listeners with the core module, and adds
    # references to the functions to th script object

    def load (self):

        # Load the default script and default keybindings

        self.default = __import__ ("default")
        self.default_bindings = __import__ ("default-keybindings")

        # Load app-specific script and keybindings

        try:
            self.mod = __import__ (self.app.name)
        except:
            self.mod = None
        try:
            bindingsname = self.app.name + "-keybindings"
            self.bindings_mod = __import__ (bindingsname)
        except:
            self.bindings_mod = None

        # If the app-specific Python module has a function called
        # onBrlKey, this function should be used to handle Braille
        # display callbacks

        try:
            func = getattr (self.mod, "onBrlKey")
        except:
            try:
                func = getattr (self.default,"onBrlKey")
            except:
                func = None
        if func:
            self.onBrlKey = func

        # Connect event dispatchers - a11y.py defines the names
        # of functions that may be in a script for responding to
        # various types of events, and their corresponding at-spi
        # event names.  We iterate through the list of known event
        # handler names, and check to see if our app-specific module
        # has a function with each name.  If it does not, we look in
        # the default module.  If we find an event handler, we add it
        # to the script.

        for key in a11y.dispatcher.keys ():
            try:
                func = getattr (self.mod, key)
            except:
                try:
                    func = getattr (self.default, key)
                except:
                    func = None

            # If we found a function, add it to this script's list of
            # event listeners

            if func:
                type = a11y.dispatcher[key]
                self.listeners[type] = func

        # Key binding sets are hash tables.  the keys are the string
        # names of key combinations, and the values are the names of
        # Python functions to call when the specified key is pressed.
        # first we connect all the default key bindings, and then we
        # iterate throuh the list of app-specific ones.  Any
        # app-specific keybinding that duplicates a default one
        # overrides it.

        for key in self.default_bindings.keybindings.keys ():
                funcname = self.default_bindings.keybindings[key]
                try:
                    func = getattr (self.mod, funcname)
                except:
                    try:
                        func = getattr (self.default, funcname)
                    except:
                        func = None
                if func:
                    self.keybindings[key] = func

        # Add app-specific keybindings - These override the defaults
        # if there are duplicates.

        if self.bindings_mod:
            for key in self.bindings_mod.keybindings.keys ():
                funcname = self.bindings_mod.keybindings[key]
                try:
                    func = getattr (self.mod, funcname)
                except:
                    try:
                        func = getattr (self.default, funcname)
                    except:
                        func = None
                    if func:
                        self.keybindings[key] = func

        return True

    # Reload the modules underlying a script

    def reload (self):

        # Reload the default module and keybindings

        reload (self.default)
        reload (self.default_bindings)

        # Try to reload the app-specific module and key bindings

        try:
            reload (self.mod)
        except:
            pass
        try:
            reload (self.bindings_mod)
        except:
            pass


