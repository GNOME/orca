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

"""Defines the Script class."""

import a11y


class Script:
    """Manages the event handling logic of orca.  Instances of this
    class create the function tables named "listeners" and "keybindings."

    Each instance creates "listeners" table (actually a dictionary) that
    it first populates with the module for the application associated with
    the script instance (the name of the module must match the name
    of the application [[[TODO: WDW - this probably needs to be fixed
    if applications are going to have different names for different
    locales.]]]), if it exists.  The script then looks to the default.py
    module and adds listeners from that module only if they do not already
    exist in the "listeners" table.

    Each instance also creates a "keybindings" table that is managed
    in a similar way as the "listeners" table, except the names of
    the modules to be loaded include the "-keybindings" suffix.
    """
    
    def __init__ (self, app):
        """Creates an empty script.  The load() method does the
        actual work of populating the "listeners" and "keybindings"
        tables.

        Arguments:
        - app: the Python Accessible application to create a script for
        """
        
        self.app = app
        self.listeners = {}
        self.keybindings = {}


    def load (self):
        """Loads a script.

        Populates the "listeners" table using the module for the
        application associated with the script instance (the name of the
        module must match the name of the application [[[TODO: WDW - this
        probably needs to be fixed if applications are going to have
        different names for different locales.]]]), if it exists.  The
        script then looks to the default.py module and adds listeners
        from that module only if they do not already exist in the
        "listeners" table.

        Also populates the "keybindings" table in a similar way as the
        "listeners" table, except the names of the modules to be loaded
        include the "-keybindings" suffix.

        Returns True.
        """
        
        # Load the default script and default keybindings.  
        #
        self.default = __import__ ("default")
        self.default_bindings = __import__ ("default-keybindings")

        # Load app-specific script and keybindings
        #
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
        # display callbacks.  [[[TODO: WDW - probably should look
        # to handle Braille key events much like we handle keyboard
        # events.]]]
        #
        try:
            func = getattr (self.mod, "onBrlKey")
        except:
            try:
                func = getattr (self.default,"onBrlKey")
            except:
                func = None
        if func:
            self.onBrlKey = func

        # Populate the "listeners" table - a11y.py defines the names
        # of functions allowed in a script for responding to various
        # types of events, and their corresponding at-spi event names.
        # We iterate through the list of allowed event handler names,
        # and check to see if our app-specific module has a function
        # with each name.  If it does not, we look in the default
        # module.  If we find an event handler, we add it to the
        # "listeners" dictionary.
        #
        for key in a11y.dispatcher.keys ():
            try:
                func = getattr (self.mod, key)
            except:
                try:
                    func = getattr (self.default, key)
                except:
                    func = None
            if func:
                type = a11y.dispatcher[key]
                self.listeners[type] = func

        # Populate the "keybindings" table.  The keys are the string
        # names of key combinations, and the values are the names of
        # Python functions to call when the specified key is pressed.
        # first we connect all the default key bindings, and then we
        # iterate throuh the list of app-specific ones.  App-specific
        # keybindings always replace default ones for the same key
        # combinations.
        #
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


    def reload (self):
        """Reloads the default and app-specific modules for the script.
        
        [[[TODO: WDW - not sure this really repopulates the listeners and
        keybindings tables, should the module files have changed on disk.
        Probably should also try to handle the case where a reload occurs
        after an app-script has been added to the file system sometime
        between the load and the reload.]]]
        """

        reload (self.default)
        reload (self.default_bindings)

        try:
            reload (self.mod)
        except:
            pass
        try:
            reload (self.bindings_mod)
        except:
            pass


