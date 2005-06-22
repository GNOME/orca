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

"""Defines the Script class.  The main entry point into this class
is the getScript factory method, to which one passes an application.
This class maintains a set of known script instances and will only
create a new script for an application if necessary.  To tell the
factory a script is no longer needed, use the deleteScript method.

Each script maintains a set of keybindings and listeners as well
as an onBrlKey field.  The keybindings field is a dictionary
where the keys are keystrings and the values are function pointers.
The listeners field is also a dictionary where the keys are
at-spi event names and the values are function pointers.  The
onBrlKey field is a function pointer."""

import settings
import orca

# The default script - used when the app is unknown (i.e., None)
#
_default = None    

# This dictionary maps at-spi event names to Python function names
# which are to be used in scripts.  For example, it maps "focus:"
# events to call a script function called onFocus and
# "window:activate" to onWindowActivated.  [[[TODO: WDW - might
# consider moving this to the script module at some point.]]]
#
EVENT_MAP = {}
EVENT_MAP["onNameChanged"]             = "object:property-change:accessible-name"
EVENT_MAP["onTextSelectionChanged"]    = "object:text-selection-changed"
EVENT_MAP["onTextInserted"]            = "object:text-changed:insert"
EVENT_MAP["onTextDeleted"]             = "object:text-changed:delete"
EVENT_MAP["onStateChanged"]            = "object:state-changed:"
EVENT_MAP["onValueChanged"]            = "object:value-changed:"
EVENT_MAP["onSelectionChanged"]        = "object:selection-changed"
EVENT_MAP["onCaretMoved"]              = "object:text-caret-moved"
EVENT_MAP["onLinkSelected"]            = "object:link-selected"
EVENT_MAP["onPropertyChanged"]         = "object:property-change:"
EVENT_MAP["onSelectionChanged"]        = "object:selection-changed"
EVENT_MAP["onActiveDescendantChanged"] = "object:active-descendant-changed"
EVENT_MAP["onVisibleDataChanged"]      = "object:visible-changed"
EVENT_MAP["onChildrenChanged"]         = "object:children-changed:"
EVENT_MAP["onWindowActivated"]         = "window:activate"
EVENT_MAP["onWindowCreated"]           = "window:create"
EVENT_MAP["onWindowDeactivated"]       = "window:deactivate"
EVENT_MAP["onWindowDestroyed"]         = "window:destroy"
EVENT_MAP["onWindowDeactivated"]       = "window:deactivated"
EVENT_MAP["onWindowMaximized"]         = "window:maximize"
EVENT_MAP["onWindowMinimized"]         = "window:minimize"
EVENT_MAP["onWindowRenamed"]           = "window:rename"
EVENT_MAP["onWindowRestored"]          = "window:restore"
EVENT_MAP["onWindowSwitched"]          = "window:switch"
EVENT_MAP["onWindowTitlelized"]        = "window:titlelize"
EVENT_MAP["onFocus"]                   = "focus:"


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
    
    # The cache of the currently known scripts.  The key is the Python
    # Accessible application, and the value is the script for that app.
    #
    _cache = {} 


    def __init__(self, app):

        """Creates a script.  Populates the "listeners" table using the module
        for the application associated with the script instance (the name of
        the module must match the name of the application [[[TODO: WDW - this
        probably needs to be fixed if applications are going to have different
        names for different locales.]]]), if it exists.  The script then looks
        to the default.py module and adds listeners from that module only if
        they do not already exist in the "listeners" table.

        Also populates the "keybindings" table in a similar way as the
        "listeners" table, except the names of the modules to be loaded
        include the "-keybindings" suffix.

        Arguments:
        - app: the Python Accessible application to create a script for
        """

        global EVENT_MAP
        
        if Script._cache.has_key(app):
            return

        self.app = app
        
        if app:
            self.name = self.app.name
        else:
            self.name = "default"
            
        self.listeners = {}
        self.keybindings = {}
        
        # Load the default script and default keybindings.  
        #
        self._default = \
            __import__("default",
                       globals(),
                       locals(),
                       [''])
        self._default_bindings = \
            __import__("default-keybindings",
                       globals(),
                       locals(),
                       [''])
        
        # Load app-specific script and keybindings
        #
        if settings.getSetting("useCustomScripts", True):
            try:
                self._custom = __import__(self.app.name)
                self.name = self.app.name + " (custom)"
            except:
                self._custom = None
            try:
                bindingsname = self.app.name + "-keybindings"
                self._custom_bindings = __import__(bindingsname)
            except:
                self._custom_bindings = None
        else:
            self._custom = None
            self._custom_bindings = None                
            
        # If the app-specific Python module has a function called
        # onBrlKey, this function should be used to handle Braille
        # display callbacks.  [[[TODO: WDW - probably should look
        # to handle Braille key events much like we handle keyboard
        # events.]]]
        #
        func = getattr(self._custom, "onBrlKey", None)
        if func is None:
            func = getattr(self._default,"onBrlKey", None)
        if func:
            self.onBrlKey = func

        # Populate the "listeners" table - orca.py defines the names
        # of functions allowed in a script for responding to various
        # types of events, and their corresponding at-spi event names.
        # We iterate through the list of allowed event handler names,
        # and check to see if our app-specific module has a function
        # with each name.  If it does not, we look in the default
        # module.  If we find an event handler, we add it to the
        # "listeners" dictionary.
        #
        for key in EVENT_MAP.keys():
            func = getattr(self._custom, key, None)
            if func is None:
                func = getattr(self._default, key, None)
            if func:
                type = EVENT_MAP[key]
                self.listeners[type] = func

        # Populate the "keybindings" table.  The keys are the string
        # names of key combinations, and the values are the names of
        # Python functions to call when the specified key is pressed.
        # first we connect all the default key bindings, and then we
        # iterate throuh the list of app-specific ones.  App-specific
        # keybindings always replace default ones for the same key
        # combinations.
        #
        for key in self._default_bindings.keybindings.keys():
            funcname = self._default_bindings.keybindings[key]
            func = getattr(self._custom, funcname, None)
            if func is None:
                func = getattr(self._default, funcname, None)
            if func:
                self.keybindings[key] = func

        if self._custom_bindings:
            for key in self._custom_bindings.keybindings.keys():
                funcname = self._custom_bindings.keybindings[key]
                func = getattr(self._custom, funcname, None)
                if func is None:
                    func = getattr(self._default, funcname, None)
                if func:
                    self.keybindings[key] = func

        Script._cache[app] = self

        
    def reload(self):
        """Reloads the default and app-specific modules for the script.
        
        [[[TODO: WDW - not sure this really repopulates the listeners and
        keybindings tables, should the module files have changed on disk.
        Probably should also try to handle the case where a reload occurs
        after an app-script has been added to the file system sometime
        between the load and the reload.]]]
        """

        reload(self._default)
        reload(self._default_bindings)

        try:
            reload(self._custom)
        except:
            pass
        try:
            reload(self._custom_bindings)
        except:
            pass


def getScript(app):
    """Get a script for an app (and make it if necessary).  This is used
    instead of a simple calls to Script's constructor.

    Arguments:
    - app: the Python app

    Returns an instance of a Script.
    """

    global _default

    # We might not know what the app is.  In this case, just defer to the
    # default script for support.
    #
    if app is None:
        if _default is None:
            _default = Script(None)
        return _default
    
    try:
        script = Script._cache[app]
    except:
        script = Script(app)
        
    return script


def deleteScript(app):
    """Deletes a script for an app (if it exists).

    Arguments:
    - app: the Python app
    """

    if app is None:
        pass
    else:
        del Script._cache[app]
    
