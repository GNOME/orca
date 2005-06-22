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

"""Provides the focus tracking presentation manager for Orca.  The main
entry points into this module are for the presentation manager contract:

    processObjectEvent  - handles all object events
    processKeyEvent     - handles all keyboard events
    processBrailleEvent - handles all Braille input events
    activate            - called when this manager is enabled
    deactivate          - called when this manager is disabled

This module uses the script module to maintain a set of scripts for all
running applications, and also keeps the notion of an activeScript.  All
object events are passed to the associated script for that application,
regardless if the application has keyboard focus or not.  All keyboard events
are passed to the active script only if it has indicated interest in the
event.
"""

import sys

import a11y
import core
import debug
#import mag - [[[TODO: WDW - disable until I can figure out how
#             to resolve the GNOME reference in mag.py.]]]
import orca
import script
import speech

from orca_i18n import _ # for gettext support


# The currently active script - this script will get all keyboard
# and Braille events.
#
_activeScript = None


def activateScript(app):
    """Called when a top-level window is activated.  It reloads the
    script associated with the top-level window's application and
    activates the script's keybindings.

    Arguments:
    - app: the Python Accessible instance representing the application
    """

    global _activeScript
    
    speech.stop("default")

    _activeScript = script.getScript(app)
    _activeScript.reload()
    debug.println(debug.LEVEL_FINE, "ACTIVATED SCRIPT: " + _activeScript.name)

def processObjectEvent(event):
    """Handles all events destined for scripts.  [[[TODO: WDW - the event
    type we received can be more specific than the event type we registered
    for.  We need to handle this.]]] [[[TODO: WDW - there may not be an
    active app.  We need to handle this.]]]

    Arguments:
    - event: a Python Event (the one created from an at-spi event).
    """

    if event.type == "window:activate":
        activateScript(event.source.app)
    elif (event.source == core.desktop) \
             and (event.type == "object:children-changed:remove"):
        try:
            script.deleteScript(event.source.app)
            return
        except:
            return

    if event.source is None:
        sys.stderr.write("ERROR: received an event with no source.\n")
        
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
    if event.source.app is None:
        set = event.source.state
        if event.source.state.count(core.Accessibility.STATE_DEFUNCT) > 0:
            return
        
    s = script.getScript(event.source.app)

    found = False
    keys = s.listeners.keys()
    for key in s.listeners.keys():
        if event.type.startswith(key):
            func = s.listeners[key]
            found = True
            break

    if found:
        # We do not want orca to crash if an ill-behaved script causes
        # an exception.
        #
        try:
            debug.println(debug.LEVEL_FINE, \
                          "focus-tracking-presenter.processEvent: " \
                          + "source: name=(" + event.source.name + ") " \
                          + "role=(" + event.source.role + ")\n" \
                          + "                   " \
                          + "func:   (" + func.func_name + ")\n" \
                          + "                   " \
                          + "script: (" + s.name + ")")
            func(event)
        except:
            debug.printException(debug.LEVEL_SEVERE)


def processKeyEvent(keystring):
    """Processes the given keyboard event based on the keybinding from the
    currently active script. This method is called synchronously from the
    at-spi registry and should be performant.  In addition, it must return
    True if it has consumed the event (and False if not).
    
    Arguments:
    - keystring: a keyboard event string from kbd.py

    Returns True if the event should be consumed.
    """

    if _activeScript and _activeScript.keybindings.has_key(keystring):
        try:
            func = _activeScript.keybindings[keystring]
            return func()
        except:
            debug.printException(debug.LEVEL_SEVERE)
            
    return False


def processBrailleEvent(command):
    """Called whenever a cursor key is pressed on the Braille display.
    
    Arguments:
    - command: the BrlAPI command for the key that was pressed.
    """

    try:
        _activeScript.onBrlKey(command)
    except:
        pass
        

def activate():
    """Called when this presentation manager is activated."""

    speech.say("default", _("Switching to focus tracking mode."))
        
    win = orca.findActiveWindow()
    if win:
        # Generate a fake window activation event so the application
        # can tell the user about itself.
        #
        e = orca.Event()
        e.source = win
        e.type = "window:activate"
        e.detail1 = 0
        e.detail2 = 0
        e.any_data = None    
        processObjectEvent(e)


def deactivate():
    """Called when this presentation manager is deactivated."""
    pass
