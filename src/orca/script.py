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

import core
import debug
import focus_tracking_presenter
import settings

# The default script - used when the app is unknown (i.e., None)
#
_default = None    


class Script:
    """Manages the specific focus tracking scripts for applications.
    """
    
    # The cache of the currently known scripts.  The key is the Python
    # Accessible application, and the value is the script for that app.
    #
    _cache = {} 


    def __init__(self, app):
        """Creates a script for the given application, if necessary.
        This method should not be called by anyone except the getScript
        method of Orca.  Callers wishing to obtain a script for an app
        should call script.getScript.

        Arguments:
        - app: the Python Accessible application to create a script for
        """

        if Script._cache.has_key(app):
            return

        self.app = app
        
        if app:
            self.name = self.app.name
        else:
            self.name = "default"
            
        self.listeners = {}
        self.keybindings = {}
        
        Script._cache[app] = self

        
    def processObjectEvent(self, event):
        """Processes all object events of interest to this script.  Note
        that this script may be passed events it doesn't care about, so
        it needs to react accordingly.

        Arguments:
        - event: the Event
        """

        # This calls the first listener it finds whose key *begins with*
        # or is the same as the event.type.
        #
        for key in self.listeners.keys():
            if event.type.startswith(key):
                try:
                    self.listeners[key](event)
                except:
                    debug.printException(debug.LEVEL_SEVERE)
            

    def processKeyEvent(self, keystring):
        """Processes the given keyboard event. This method is called
        synchronously from the at-spi registry and should be performant.  In
        addition, it must return True if it has consumed the event (and False
        if not).
    
        Arguments:
        - keystring: a keyboard event string

        Returns True if the event should be consumed.
        """

        if self.keybindings.has_key(keystring):
            try:
                return self.keybindings[keystring]()
            except:
                debug.printException(debug.LEVEL_SEVERE)
        return False
            

    def processBrailleEvent(self, command):
        """Called whenever a cursor key is pressed on the Braille display.
    
        Arguments:
        - command: the BrlAPI command for the key that was pressed.

        Returns True if the command was consumed; otherwise False
        """
        return False


def _registerEventListeners(script):
    """Tells the focus_tracking_presenter module to listen for all the event
    types of interest to the script.

    Arguments:
    - script: the script.
    """

    for eventType in script.listeners.keys():
        focus_tracking_presenter.registerEventListener(eventType)
            
def _unregisterEventListeners(script):
    """Tells the focus_tracking_presenter module to stop listening for all the
    event types of interest to the script.

    Arguments:
    - script: the script.
    """

    for eventType in script.listeners.keys():
        focus_tracking_presenter.unregisterEventListener(eventType)
            
    
def getScript(app):
    """Get a script for an app (and make it if necessary).  This is used
    instead of a simple calls to Script's constructor.

    Arguments:
    - app: the Python app

    Returns an instance of a Script.
    """

    import default
    
    global _default

    # We might not know what the app is.  In this case, just defer to the
    # default script for support.
    #
    if app is None:
        if _default is None:
            _default = default.getScript(None)
            _registerEventListeners(_default)
        return _default
    elif Script._cache.has_key(app):
        return Script._cache[app]
    elif settings.getSetting("useCustomScripts", True):
        try:
            module = __import__(app.name, globals(), locals(), [''])
            try:
                script = module.getScript(app)
                script.name = app.name + " (custom)"
            except:
                # We do not want the getScript method to fail.  If it does,
                # we want to let the scrip developer know what went wrong.
                #
                debug.printException(debug.LEVEL_SEVERE)
                script = default.getScript(app)                    
        except:
            # It's ok if a custom script doesn't exist.
            #
            script = default.getScript(app)
    else:
        script = default.getScript(app)

    Script._cache[app] = script
    _registerEventListeners(script)

    return script


def deleteScript(app):
    """Deletes a script for an app (if it exists).

    Arguments:
    - app: the Python app
    """

    if app:
        if Script._cache.has_key(app):
            script = Script._cache[app]
            _unregisterEventListeners(script)
            debug.println(debug.LEVEL_FINE, "DELETED SCRIPT: ", script.name)
            del Script._cache[app]
