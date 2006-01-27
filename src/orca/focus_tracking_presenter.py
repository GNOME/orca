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

"""Provides the FocusTrackingPresenter for Orca."""

import gobject
import Queue

import atspi
import default
import debug
import orca
import presentation_manager
import settings
import speech

from orca_i18n import _ # for gettext support

import CORBA

class FocusTrackingPresenter(presentation_manager.PresentationManager):
    """Maintain a set of scripts for all running applications, and
    also keeps the notion of an activeScript.  All object events are
    passed to the associated script for that application, regardless if
    the application has keyboard focus or not.  All keyboard events are
    passed to the active script only if it has indicated interest in the
    event."""

    def __init__(self):

        # Dictionary that keeps count of event listeners by type.
        # This is a bit convoluted for now, but what happens is that
        # scripts tell the FocusTrackingPresenter to listen for
        # object events based on what they want, and the
        # FocusTrackingPresenter then eventually passes them to the
        # script.  Because both the FocusTrackingPresenter and scripts
        # are interested in object events, and the FocusTrackingPresenter
	# is what delves them out, we keep at most one listener to avoid
        # receiving the same event twice in a row.
        #
	self.registry = atspi.Registry()
	self._knownScripts = {}
	self._eventQueue   = Queue.Queue(0)
	self._gidle_id     = 0

    ########################################################################
    #                                                                      #
    # METHODS FOR KEEPING TRACK OF LISTENERS REGISTERED WITH ATSPI         #
    #                                                                      #
    ########################################################################

    def _registerEventListener(self, eventType):
        """Tells this module to listen for the given event type.

        Arguments:
        - eventType: the event type.
        """

        if self._listenerCounts.has_key(eventType):
            self._listenerCounts[eventType] += 1
        else:
            self.registry.registerEventListener(self._enqueueObjectEvent,
						eventType)
            self._listenerCounts[eventType] = 1

    def _deregisterEventListener(self, eventType):
        """Tells this module to stop listening for the given event type.

        Arguments:
        - eventType: the event type.
        """

        self._listenerCounts[eventType] -= 1
        if self._listenerCounts[eventType] == 0:
            self.registry.deregisterEventListener(self._enqueueObjectEvent,
						  eventType)
            del self._listenerCounts[eventType]

    def _registerEventListeners(self, script):
        """Tells the FocusTrackingPresenter to listen for all
	the event types of interest to the script.

        Arguments:
        - script: the script.
        """

        for eventType in script.listeners.keys():
            self._registerEventListener(eventType)

    def _deregisterEventListeners(self, script):
        """Tells the FocusTrackingPresenter to stop listening for all the
        event types of interest to the script.

        Arguments:
        - script: the script.
        """

        for eventType in script.listeners.keys():
            self._deregisterEventListener(eventType)

    ########################################################################
    #                                                                      #
    # METHODS FOR KEEPING TRACK OF KNOWN SCRIPTS.                          #
    #                                                                      #
    ########################################################################

    # The cache of the currently known scripts.  The key is the Python
    # Accessible application, and the value is the script for that app.
    #

    def _createScript(self, app):
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

            if moduleName and len(moduleName):
                for package in scriptPackages:
                    if len(package):
                        name = package + "." + moduleName
                    else:
                        name = moduleName
                    try:
                        debug.println(debug.LEVEL_FINEST,
                                      "Looking for script at %s.py..." % name)
                        module = __import__(name,
                                            globals(),
                                            locals(),
                                            [''])
                        debug.println(debug.LEVEL_FINEST,
                                      "...found %s.py" % name)
                        break
                    except ImportError:
                        debug.println(debug.LEVEL_FINEST,
                                      "...could not find %s.py" % name)
                    except:
                        debug.printException(debug.LEVEL_SEVERE)
                        debug.println(debug.LEVEL_SEVERE,
                                      "While attempting to import %s" % name)
            if module:
                try:
                    script = module.Script(app)
                except:
                    # We do not want the getScript method to fail.  If it does,
                    # we want to let the script developer know what went wrong,
                    # but we also want to move along without crashing Orca.
                    #
                    debug.printException(debug.LEVEL_SEVERE)

        if not script:
            script = default.Script(app)

        return script

    def _getScript(self, app):
        """Get a script for an app (and make it if necessary).  This is used
        instead of a simple calls to Script's constructor.

        Arguments:
        - app: the Python app

        Returns an instance of a Script.
        """

        # We might not know what the app is.  In this case, just defer to the
        # default script for support.  Note the hack to check for Orca - this
        # will occur if Orca pops up its own windows.  We work to make Orca
        # windows work well with the default script so it will not need a
        # custom script.
        #
        if not app:
            if not self._defaultScript:
                self._defaultScript = default.Script(None)
                self._registerEventListeners(self._defaultScript)
            script = self._defaultScript
        elif self._knownScripts.has_key(app):
            script = self._knownScripts[app]
        else:
    	    script = self._createScript(app)
       	    self._knownScripts[app] = script
            self._registerEventListeners(script)

        return script

    def _reclaimScripts(self):
        """Compares the list of known scripts to the list of known apps,
        deleting any scripts as necessary.
        """

        apps = []

        desktop = self.registry.desktop
        for i in range(0, desktop.childCount):
            acc = desktop.getChildAtIndex(i)
            try:
                app = atspi.Accessible.makeAccessible(acc)
                if app:
                    apps.insert(0, app)
            except:
                debug.printException(debug.LEVEL_SEVERE)

        for app in self._knownScripts.keys():
            if apps.count(app) == 0:
                script = self._knownScripts[app]
                self._deregisterEventListeners(script)
                del self._knownScripts[app]
                break

    ########################################################################
    #                                                                      #
    # METHODS FOR PRE-PROCESSING AND MASSAGING AT-SPI OBJECT EVENTS        #
    # for processing by the rest of Orca.                                  #
    #                                                                      #
    ########################################################################

    def _enqueueObjectEvent(self, e):
        """Handles all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        # Uncomment these lines if you want to see what it's like without
        # the queue.
        #
        #self._processObjectEvent(atspi.Event(e))
        #return
    
        # We ignore defunct objects and let the atspi module take care of them
        # for us.
        #
        if (e.type == "object:state-changed:defunct"):
            return

        # We also generally do not like
        # object:property-change:accessible-parent events because they
        # indicate something is now whacked with the hierarchy, so we
        # just ignore them and let the atspi module take care of it for
        # us.
        #
        if e.type == "object:property-change:accessible-parent":
            return

        # We create the event here because it will ref everything we
        # want it to ref, thus allowing things to survive until they
        # are processed on the gidle thread.
        #
	debug.println(debug.LEVEL_FINEST, "Queueing event %s" % e.type)
        try:
            self._eventQueue.put(atspi.Event(e))
            if not self._gidle_id:
                self._gidle_id = gobject.idle_add(self._dequeueObjectEvent)
	except:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "Exception above while processing event: " + e.type)
        
    def _dequeueObjectEvent(self):
        """Handles all events destined for scripts.  Called by the GTK
	idle thread.
        """

	event = self._eventQueue.get()
	debug.println(debug.LEVEL_FINEST, "Dequeued event %s" % event.type)
	self._processObjectEvent(event)
	if self._eventQueue.empty():
	    self._gidle_id = 0
	    return False
	else:
	    return True
	
    def _processObjectEvent(self, event):
        """Handles all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        debug.printObjectEvent(debug.LEVEL_FINEST, event)

        # Reclaim (delete) any scripts when desktop children go away.
        # The idea here is that a desktop child is an app. We also
        # generally do not like object:children-changed:remove events,
        # either.
        #
        if event.type == "object:children-changed:remove":
            if event.source == self.registry.desktop:
                self._reclaimScripts()
            return

        try:
            debug.printDetails(debug.LEVEL_FINEST, "    ", event.source)
        except CORBA.COMM_FAILURE:
            debug.printException(debug.LEVEL_FINEST)
            debug.println(debug.LEVEL_FINEST,
                          "COMM_FAILURE above while processing event: " \
                          + event.type)
            atspi.Accessible.deleteAccessible(event.source)
            return
        except CORBA.OBJECT_NOT_EXIST:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "OBJECT_NOT_EXIST above while processing event: " \
                          + event.type)
            atspi.Accessible.deleteAccessible(event.source)
            return
        except:
            debug.printException(debug.LEVEL_SEVERE)
            return

        if not event.source:
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
                self._activeScript = self._getScript(event.source.app)
                debug.println(debug.LEVEL_FINE, "ACTIVE SCRIPT: " \
                              + self._activeScript.name)
            s = self._getScript(event.source.app)
            s.processObjectEvent(event)
        except CORBA.COMM_FAILURE:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "COMM_FAILURE above while processing event: " \
                          + event.type)
            atspi.Accessible.deleteAccessible(event.source)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event based on the keybinding from the
        currently active script. This method is called synchronously from the
        at-spi registry and should be performant.  In addition, it must return
        True if it has consumed the event (and False if not).

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event should be consumed.
        """

        if self._activeScript:
            return self._activeScript.processKeyboardEvent(keyboardEvent)
        else:
            return False

    def processBrailleEvent(self, brailleEvent):
        """Called whenever a cursor key is pressed on the Braille display.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent

        Returns True if the command was consumed; otherwise False
        """

        if self._activeScript:
            return self._activeScript.processBrailleEvent(brailleEvent)
        else:
            return False

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        if self._activeScript:
            self._activeScript.locusOfFocusChanged(event,
                                                   oldLocusOfFocus,
                                                   newLocusOfFocus)

    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.
        This method should not be called for objects whose visual
        appearance changes solely because of focus -- locusOfFocusChanged
        is used for that.  Instead, it is intended mostly for objects
        whose notional 'value' has changed, such as a checkbox changing
        state, a progress bar advancing, a slider moving, text inserted,
        caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        if self._activeScript:
            self._activeScript.visualAppearanceChanged(event, obj)

    def activate(self):
        """Called when this presentation manager is activated."""

        speech.speak(_("Switching to focus tracking mode."))

    	self._listenerCounts = {}
	self._knownScripts   = {}
        self._defaultScript  = None
    	self._activeScript   = None

        self._registerEventListener("window:activate")
        self._registerEventListener("window:deactivate")
        self._registerEventListener("object:children-changed:remove")

        win = orca.findActiveWindow()
        if win:
            # Generate a fake window activation event so the application
            # can tell the user about itself.
            #
            e = atspi.Event()
            e.source   = win._acc
            e.type     = "window:activate"
            e.detail1  = 0
            e.detail2  = 0
            e.any_data = None
            self._enqueueObjectEvent(e)

    def deactivate(self):
        """Called when this presentation manager is deactivated."""

        for eventType in self._listenerCounts.keys():
            self.registry.deregisterEventListener(self._enqueueObjectEvent,
						  eventType)
    	self._listenerCounts = {}
	self._knownScripts   = {}
        self._defaultScript  = None
    	self._activeScript   = None
