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

    processKeyboardEvent - handles all keyboard events
    processBrailleEvent  - handles all Braille input events
    locusOfFocusChanged  - notified when orca's locusOfFocus changes
    activate             - called when this manager is enabled
    deactivate           - called when this manager is disabled

This module uses the script module to maintain a set of scripts for all
running applications, and also keeps the notion of an activeScript.  All
object events are passed to the associated script for that application,
regardless if the application has keyboard focus or not.  All keyboard events
are passed to the active script only if it has indicated interest in the
event.
"""

import a11y
import default
import core
import debug
import orca
import settings
import speech

from orca_i18n import _ # for gettext support

import CORBA


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
_knownScripts = {} 


# The default script - used when the app is unknown (i.e., None)
#
_default = None    


# The currently active script - this script will get all keyboard
# and Braille events.
#
_activeScript = None


def _createScript(app):
    """For the given application name, create a new script instance.
    We'll first see if a mapping from appName to module name exists.
    If it does, we use that.  If it doesn't, we try the app name.
    If all else fails, we fall back to the default script.
    """

    script = None

    if settings.getSetting(settings.USE_CUSTOM_SCRIPTS, True):
        # Look for custom scripts first.  
        #
        # We'll use the LEVEL_FINEST level for debug output here as
        # it really isn't an error if the script cannot be found.
        # But, sometimes a script cannot be "found" because it has
        # a syntax error in it, so we want to give script writers
        # a vehicle for debugging these types of things.
        #
        scriptPackages = settings.getSetting(settings.SCRIPT_PACKAGES,
                                             ["orca-scripts", "scripts"])

        moduleName = settings.getScriptModuleName(app)
        module = None

        for package in scriptPackages:
            if len(package):
                name = package + "." + moduleName
            else:
                name = moduleName
                
            try:
                module = __import__(name, 
                                    globals(), 
                                    locals(), 
                                    [''])
                debug.println(debug.LEVEL_FINER,
                              "Using custom script module: %s" % name)
                break
            except:
                debug.printException(debug.LEVEL_FINEST)

        if module:
            try:
                script = module.Script(app)
            except:
                # We do not want the getScript method to fail.  If it does,
                # we want to let the script developer know what went wrong,
                # but we also want to move along without crashing Orca.
                #
                debug.printException(debug.LEVEL_SEVERE)

    if script is None:
        script = default.Script(app)

    return script


def _getScript(app):
    """Get a script for an app (and make it if necessary).  This is used
    instead of a simple calls to Script's constructor.

    Arguments:
    - app: the Python app

    Returns an instance of a Script.
    """

    global _default

    # We might not know what the app is.  In this case, just defer to the
    # default script for support.  Note the hack to check for Orca - this
    # will occur if Orca pops up its own windows.  We work to make Orca
    # windows work well with the default script so it will not need a
    # custom script.
    #
    if app is None:
        if _default is None:
            _default = default.Script(None)
            _registerEventListeners(_default)
        script = _default
    elif _knownScripts.has_key(app):
        script = _knownScripts[app]
    else:
	script = _createScript(app)
    	_knownScripts[app] = script
    	_registerEventListeners(script)

    return script


def _reclaimScripts():
    """Compares the list of known scripts to the list of known apps,
    deleting any scripts as necessary.
    """

    apps = []
    
    for i in range(0, core.desktop.childCount):
        acc = core.desktop.getChildAtIndex(i)
        try:
            app = a11y.makeAccessible(acc)
            if app:
                apps.insert(0, app)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    for app in _knownScripts.keys():
        if apps.count(app) == 0:
            script = _knownScripts[app]
            _unregisterEventListeners(script)
            debug.println(debug.LEVEL_FINE, "DELETED SCRIPT: " + script.name)
            del _knownScripts[app]


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
   def __init__(self, e=None):
       if e:
           self.source   = a11y.makeAccessible(e.source)
           self.type     = e.type
           self.detail1  = e.detail1
           self.detail2  = e.detail2
           self.any_data = e.any_data
       else:
           self.source   = None
           self.type     = None
           self.detail1  = None
           self.detail2  = None
           self.any_data = None


def processObjectEvent(e):
    """Handles all events destined for scripts.

    Arguments:
    - e: an at-spi event.
    """

    global _activeScript

    debug.printObjectEvent(debug.LEVEL_FINEST, e)

    # Reclaim (delete) any scripts when desktop children go away.
    # The idea here is that a desktop child is an app.  We also
    # generally do not like object:children-changed:remove or
    # object:property-change:accessible-parent events because they
    # indicate something is now whacked with the hierarchy, so we
    # just ignore them.
    #
    if e.type == "object:children-changed:remove":
        if e.source == core.desktop:
            _reclaimScripts()
        return
    if e.type == "object:property-change:accessible-parent":
        return
    
    # We ignore defunct objects and let the a11y module take care of them
    # for us.
    #
    if (e.type == "object:state-changed:defunct"):
        return

    # [[[TODO: WDW - HACK because tickling gedit when it is starting can
    # cause gedit to issue the following message:
    #
    # (gedit:31434): GLib-GObject-WARNING **: invalid cast from `SpiAccessible' to `BonoboControlAccessible'
    #
    # It seems as though whenever this message is issued, gedit will hang
    # when you try to exit it.  Debugging has shown that the iconfied state
    # in particular seems to indicate that an object is telling all
    # assistive technologies to just leave it alone or it will pull the
    # trigger on the application.]]]
    #
    if (e.type == "object:state-changed:iconified"):
        return

    # Convert the AT-SPI event into a Python Event that we can annotate.
    # Copy relevant details from the event.
    #
    try:
        event = Event(e)
        debug.printDetails(debug.LEVEL_FINEST, "    ", event.source)
    except CORBA.COMM_FAILURE:
        debug.printException(debug.LEVEL_SEVERE)
        debug.println(debug.LEVEL_SEVERE,
                      "COMM_FAILURE above while processing event: " + e.type)
	a11y.deleteAccessible(e.source)
	return
    except:
        debug.printException(debug.LEVEL_SEVERE)
        return

    if event.source is None:
        debug.println(debug.LEVEL_SEVERE,
                      "ERROR: received an event with no source.")
        return

    # [[[TODO: WDW - might want to consider re-introducing the reload
    # feature of scripts somewhere around here.  I pulled it out as
    # part of the big refactor to make scripts object-oriented. Logged
    # as bugzilla bug 319777.]]]
    #
    try:
        if event.type == "window:activate":
            speech.stop()
            _activeScript = _getScript(event.source.app)
            debug.println(debug.LEVEL_FINE, "ACTIVE SCRIPT: " \
                          + _activeScript.name)
        s = _getScript(event.source.app)
        s.processObjectEvent(event)
    except CORBA.COMM_FAILURE:
        debug.printException(debug.LEVEL_SEVERE)
        debug.println(debug.LEVEL_SEVERE,
                      "COMM_FAILURE above while processing event: " + e.type)
	a11y.deleteAccessible(e.source)        
    except:
        debug.printException(debug.LEVEL_SEVERE)


def processKeyboardEvent(keyboardEvent):
    """Processes the given keyboard event based on the keybinding from the
    currently active script. This method is called synchronously from the
    at-spi registry and should be performant.  In addition, it must return
    True if it has consumed the event (and False if not).
    
    Arguments:
    - keyboardEvent: an instance of input_event.KeyboardEvent

    Returns True if the event should be consumed.
    """

    if _activeScript:
        return _activeScript.processKeyboardEvent(keyboardEvent)
    else:
        return False


def processBrailleEvent(brailleEvent):
    """Called whenever a cursor key is pressed on the Braille display.
    
    Arguments:
    - brailleEvent: an instance of input_event.BrailleEvent

    Returns True if the command was consumed; otherwise False
    """

    if _activeScript:
        return _activeScript.processBrailleEvent(brailleEvent)
    else:
        return False


def locusOfFocusChanged(event, oldLocusOfFocus, newLocusOfFocus):
    """Called when the visual object with focus changes.

    Arguments:
    - event: if not None, the Event that caused the change
    - oldLocusOfFocus: Accessible that is the old locus of focus
    - newLocusOfFocus: Accessible that is the new locus of focus
    """

    if _activeScript:
        _activeScript.locusOfFocusChanged(event,
                                          oldLocusOfFocus,
                                          newLocusOfFocus)
            

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
    
    if _activeScript:
        _activeScript.visualAppearanceChanged(event, obj)
            

def activate():
    """Called when this presentation manager is activated."""

    speech.speak(_("Switching to focus tracking mode."))

    _registerEventListener("window:activate")
    _registerEventListener("window:deactivate")
    _registerEventListener("object:children-changed:remove")

    win = orca.findActiveWindow()
    if win:
        # Generate a fake window activation event so the application
        # can tell the user about itself.
        #
        e = Event()
        e.source = win._acc
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
