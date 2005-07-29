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

    processKeyEvent     - handles all keyboard events
    processBrailleEvent - handles all Braille input events
    locusOfFocusChanged - notified when orca's locusOfFocus changes
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
import default
import core
import debug
#import mag - [[[TODO: WDW - disable until I can figure out how
#             to resolve the GNOME reference in mag.py.]]]
import orca
import script
import settings
import speech

from orca_i18n import _ # for gettext support


########################################################################
#                                                                      #
# METHODS FOR KEEPING TRACK OF LISTENERS REGISTERED WITH CORE          #
#                                                                      #
########################################################################

# Dictionary that keeps count of event listeners by type.  This is a bit
# convoluted for now, but what happens is that scripts tell the
# focus_tracking_presenter to listen for object events based on what they
# want, and the focus_tracking_presenter then eventually passes them to the
# script.  Because both the focus_tracking_presenter and scripts are
# interested in object events, and the focus_tracking_presenter is what delves
# them out, we keep at most one listener to avoid receiving the same event
# twice in a row.
#
_listenerCounts = {}

def _registerEventListener(eventType):
    """Tells this module to listen for the given event type.

    Arguments:
    - eventType: the event type.
    """

    global _listenerCounts
    
    if _listenerCounts.has_key(eventType):
        _listenerCounts[eventType] = _listenerCounts[eventType] + 1
    else:
        core.registerEventListener(processObjectEvent, eventType)
        _listenerCounts[eventType] = 1
            
def _unregisterEventListener(eventType):
    """Tells this module to stop listening for the given event type.

    Arguments:
    - eventType: the event type.
    """

    global _listenerCounts
    
    _listenerCounts[eventType] = _listenerCounts[eventType] - 1
    if _listenerCounts[eventType] == 0:
        core.unregisterEventListener(processObjectEvent, eventType)
        del _listenerCounts[eventType]

def _registerEventListeners(script):
    """Tells the focus_tracking_presenter module to listen for all the event
    types of interest to the script.

    Arguments:
    - script: the script.
    """

    for eventType in script.listeners.keys():
        _registerEventListener(eventType)

            
def _unregisterEventListeners(script):
    """Tells the focus_tracking_presenter module to stop listening for all the
    event types of interest to the script.

    Arguments:
    - script: the script.
    """

    for eventType in script.listeners.keys():
        _unregisterEventListener(eventType)
            
########################################################################
#                                                                      #
# METHODS FOR KEEPING TRACK OF KNOWN SCRIPTS.                          #
#                                                                      #
########################################################################

# The cache of the currently known scripts.  The key is the Python
# Accessible application, and the value is the script for that app.
#
_known_scripts = {} 


# The default script - used when the app is unknown (i.e., None)
#
_default = None    


# The currently active script - this script will get all keyboard
# and Braille events.
#
_activeScript = None


def _getScript(app):
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
            _default = default.getScript(None)
            _registerEventListeners(_default)
        return _default
    elif _known_scripts.has_key(app):
        return _known_scripts[app]
    elif settings.getSetting("useCustomScripts", True):
        try:
            module = __import__(app.name, globals(), locals(), [''])
            try:
                script = module.getScript(app)
            except:
                # We do not want the getScript method to fail.  If it does,
                # we want to let the script developer know what went wrong,
                # but wee also want to move along without crashing Orca.
                #
                debug.printException(debug.LEVEL_SEVERE)
                script = default.getScript(app)                    
        except:
            # It's ok if a custom script doesn't exist.
            #
            script = default.getScript(app)
    else:
        script = default.getScript(app)

    _known_scripts[app] = script
    _registerEventListeners(script)

    return script


def _deleteScript(app):
    """Deletes a script for an app (if it exists).

    Arguments:
    - app: the Python app
    """

    if app:
        if _known_scripts.has_key(app):
            script = _known_scripts[app]
            _unregisterEventListeners(script)
            debug.println(debug.LEVEL_FINE, "DELETED SCRIPT: ", script.name)
            del _known_scripts[app]


########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING AT-SPI OBJECT EVENTS        #
#                                                                      #
# AT-SPI events are receieved here and converted into a Python object  #
# for processing by the rest of Orca.                                  #
#                                                                      #
########################################################################

class Event:
   """Dummy class for converting the source of an event to an
   Accessible object.  We need this since the core.event object we
   get from the core is read-only.  So, we create this dummy event
   object to contain a copy of all the event members with the source
   converted to an Accessible.  It is perfectly OK for event handlers
   to annotate this object with their own attributes.
   """
   pass


def processObjectEvent(e):
    """Handles all events destined for scripts.

    Arguments:
    - e: an at-spi event.
    """

    global _activeScript

    # We ignore defunct objects and let the a11y module take care of them
    # for us.
    #
    if (e.type == "object:state-changed:defunct") \
        or a11y.isDefunct(e.source):
        return

    # Convert the AT-SPI event into a Python Event that we can annotate.
    # Copy relevant details from the event.
    #
    event = Event()
    event.type = e.type
    event.detail1 = e.detail1
    event.detail2 = e.detail2
    event.any_data = e.any_data
    event.source = a11y.makeAccessible(e.source)

    debug.printObjectEvent(debug.LEVEL_FINEST,
                           event,
                           a11y.accessibleToString("                ",
                                                   event.source))

    if event.source is None:
        sys.stderr.write("ERROR: received an event with no source.\n")
        return

    # [[[TODO: WDW - might want to consider re-introducing the reload
    # feature of scripts somewhere around here.  I pulled it out as
    # part of the big refactor to make scripts object-oriented.]]]
    #
    if event.type == "window:activate":
        speech.stop("default")
        _activeScript = _getScript(event.source.app)
        debug.println(debug.LEVEL_FINE, "ACTIVATED SCRIPT: " \
                      + _activeScript.name)
    elif event.type == "object:children-changed:remove":
        # [[[TODO: WDW - something is severely broken.  We are not deleting
        # scripts here.
        #
        if e.source == core.desktop:
            try:
                _deleteScript(event.source.app)
                return
            except:
                debug.printException(debug.LEVEL_SEVERE)
                return

    s = _getScript(event.source.app)

    try:
        s.processObjectEvent(event)
    except:
        debug.printException(debug.LEVEL_SEVERE)


def processKeyEvent(keyboardEvent):
    """Processes the given keyboard event based on the keybinding from the
    currently active script. This method is called synchronously from the
    at-spi registry and should be performant.  In addition, it must return
    True if it has consumed the event (and False if not).
    
    Arguments:
    - keyboardEvent: an instance of input_event.KeyboardEvent

    Returns True if the event should be consumed.
    """

    global _activeScript
    
    if _activeScript:
        try:
            return _activeScript.processKeyEvent(keyboardEvent)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            
    return False


def processBrailleEvent(brailleEvent):
    """Called whenever a cursor key is pressed on the Braille display.
    
    Arguments:
    - brailleEvent: an instance of input_event.BrailleEvent

    Returns True if the command was consumed; otherwise False
    """

    if _activeScript:
        try:
            return _activeScript.processBrailleEvent(brailleEvent)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    return False


def locusOfFocusChanged(event, oldLocusOfFocus, newLocusOfFocus):
    """Called when the visual object with focus changes.

    Arguments:
    - event: if not None, the Event that caused the change
    - oldLocusOfFocus: Accessible that is the old locus of focus
    - newLocusOfFocus: Accessible that is the new locus of focus
    """

    global _activeScript
    
    if _activeScript:
        try:
            _activeScript.locusOfFocusChanged(event,
                                              oldLocusOfFocus,
                                              newLocusOfFocus)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            

def visualAppearanceChanged(event, obj):
    """Called when the visual appearance of an object changes.  This method
    should not be called for objects whose visual appearance changes solely
    because of focus -- setLocusOfFocus is used for that.  Instead, it is
    intended mostly for objects whose notional 'value' has changed, such as a
    checkbox changing state, a progress bar advancing, a slider moving, text
    inserted, caret moved, etc.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible whose visual appearance changed.
    """
    

    global _activeScript
    
    if _activeScript:
        try:
            _activeScript.visualAppearanceChanged(event, obj)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            

def activate():
    """Called when this presentation manager is activated."""

    speech.say("default", _("Switching to focus tracking mode."))

    _registerEventListener("window:activate")
    _registerEventListener("window:deactivate")
    _registerEventListener("object:children-changed:remove")

    win = orca.findActiveWindow()
    if win:
        # Generate a fake window activation event so the application
        # can tell the user about itself.
        #
        e = Event()
        e.source = win.acc
        e.type = "window:activate"
        e.detail1 = 0
        e.detail2 = 0
        e.any_data = None    

        processObjectEvent(e)


def deactivate():
    """Called when this presentation manager is deactivated."""

    global _listenerCounts
    
    for key in _listenerCounts.keys():
        core.unregisterEventListener(processObjectEvent, key)
    _listenerCounts = {}
