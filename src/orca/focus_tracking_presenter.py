# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import gobject
import Queue
#import threading
import time

import atspi
import braille
import default
import debug
import input_event
import orca
import presentation_manager
import settings
import speech
import util

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
        self.registry      = atspi.Registry()
        self._knownScripts = {}
        self._eventQueue   = Queue.Queue(0)
        self._gidle_id     = 0
        self.lastNoFocusTime = 0.0

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
            self.registry.registerEventListener(self._enqueueEvent,
                                                eventType)
            self._listenerCounts[eventType] = 1

    def _deregisterEventListener(self, eventType):
        """Tells this module to stop listening for the given event type.

        Arguments:
        - eventType: the event type.
        """

        self._listenerCounts[eventType] -= 1
        if self._listenerCounts[eventType] == 0:
            self.registry.deregisterEventListener(self._enqueueEvent,
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

        if settings.enableCustomScripts:
            # Look for custom scripts first.
            #
            # We'll use the LEVEL_FINEST level for debug output here as
            # it really isn't an error if the script cannot be found.
            # But, sometimes a script cannot be "found" because it has
            # a syntax error in it, so we want to give script writers
            # a vehicle for debugging these types of things.
            #
            scriptPackages = settings.scriptPackages

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
                        debug.printException(debug.LEVEL_ALL)
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

        # If there is no custom script for an application, try seeing if
        # there is a script for the toolkit of the application.  If there
        # is, then try to use it.  If there isn't, then fall back to the
        # default script. Note that this search is restricted to the "orca"
        # package for now.
        #
        if (not script) \
            and app \
            and app.__dict__.has_key("toolkitName") \
            and app.toolkitName:

            try:
                debug.println(
                    debug.LEVEL_FINE,
                    "Looking for toolkit script %s.py..." % app.toolkitName)
                module = __import__(app.toolkitName,
                                    globals(),
                                    locals(),
                                    [''])
                script = module.Script(app)
                debug.println(debug.LEVEL_FINE,
                              "...found %s.py" % name)
            except ImportError:
                debug.printException(debug.LEVEL_ALL)
                debug.println(
                    debug.LEVEL_FINE,
                    "...could not find %s.py" % app.toolkitName)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                debug.println(
                    debug.LEVEL_SEVERE,
                    "While attempting to import %s" % app.toolkitName)

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

        # We might not know what the app is.  In this case, just defer
        # to the default script for support.
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

        # Sometimes the desktop can become unavailable.  This happens
        # often when synaptic is used to load new modules (see the bug
        # report http://bugzilla.gnome.org/show_bug.cgi?id=342022).
        # So...if this happens, we'll just move along.  The next
        # successful call to _reclaimScripts will reclaim anything we
        # didn't reclaim this time.
        #
        try:
            apps = []
            desktop = self.registry.desktop
            for i in range(0, desktop.childCount):
                acc = desktop.getChildAtIndex(i)
                app = atspi.Accessible.makeAccessible(acc)
                if app:
                    apps.insert(0, app)

            for app in self._knownScripts.keys():
                if apps.count(app) == 0:
                    script = self._knownScripts[app]
                    self._deregisterEventListeners(script)
                    del self._knownScripts[app]
                    del script
        except:
            debug.printException(debug.LEVEL_FINEST)

    ########################################################################
    #                                                                      #
    # METHODS FOR PRE-PROCESSING AND MASSAGING AT-SPI OBJECT EVENTS        #
    # for processing by the rest of Orca.                                  #
    #                                                                      #
    ########################################################################

    def _processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event based on the keybinding from the
        currently active script.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """
        if self._activeScript:
            try:
                self._activeScript.processKeyboardEvent(keyboardEvent)
            except:
                debug.printException(debug.LEVEL_WARNING)
                debug.printStack(debug.LEVEL_WARNING)

    def _processBrailleEvent(self, brailleEvent):
        """Called whenever a cursor key is pressed on the Braille display.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent
        """
        if self._activeScript:
            try:
                self._activeScript.processBrailleEvent(brailleEvent)
            except:
                debug.printException(debug.LEVEL_WARNING)
                debug.printStack(debug.LEVEL_WARNING)

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
            if event.source == atspi.Accessible.makeAccessible(
                                   self.registry.desktop):
                self._reclaimScripts()
                #import gc
                #gc.collect()
                #print "In process, garbage:", gc.garbage
                #for obj in gc.garbage:
                #    print "   referrers:", obj, gc.get_referrers(obj)
            return

        try:
            debug.printDetails(debug.LEVEL_FINEST, "    ", event.source)
        except CORBA.COMM_FAILURE:
            debug.printException(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_FINEST,
                          "COMM_FAILURE above while processing event: " \
                          + event.type)
        except CORBA.OBJECT_NOT_EXIST:
            debug.printException(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "OBJECT_NOT_EXIST above while processing event: " \
                          + event.type)
            atspi.Accessible.deleteAccessible(event.source)
            return
        except:
            debug.printException(debug.LEVEL_WARNING)
            return

        if not event.source:
            debug.println(debug.LEVEL_WARNING,
                          "ERROR: received an event with no source.")
            return

        # We can sometimes get COMM_FAILURES even if the object has not
        # gone away.  This happens a lot with the Java access bridge.
        # So...we will try a few times before giving up.
        #
        # [[[TODO: WDW - might want to consider re-introducing the reload
        # feature of scripts somewhere around here.  I pulled it out as
        # part of the big refactor to make scripts object-oriented. Logged
        # as bugzilla bug 319777.]]]
        #
        retryCount = 0
        oldLocusOfFocus = orca.locusOfFocus
        while retryCount <= settings.commFailureAttemptLimit:
            try:
                if event.type == "window:activate":
                    # We'll let someone else decide if it's important
                    # to stop speech or not.
                    #speech.stop()
                    self._activeScript = self._getScript(event.source.app)
                    debug.println(debug.LEVEL_FINE, "ACTIVE SCRIPT: " \
                                  + self._activeScript.name)
                s = self._getScript(event.source.app)
                s.processObjectEvent(event)
                if retryCount:
                    debug.println(debug.LEVEL_WARNING,
                                  "  SUCCEEDED AFTER %d TRIES" % retryCount)
                break
            except CORBA.COMM_FAILURE:
                debug.printException(debug.LEVEL_WARNING)
                debug.println(debug.LEVEL_WARNING,
                              "COMM_FAILURE above while processing: " \
                              + event.type)
                retryCount += 1
                if retryCount <= settings.commFailureAttemptLimit:
                    # We want the old locus of focus to be reset so
                    # the proper stuff will be spoken if the locus
                    # of focus changed during our last attempt at
                    # handling this event.
                    #
                    orca.locusOfFocus = oldLocusOfFocus
                    debug.println(debug.LEVEL_WARNING,
                                  "  TRYING AGAIN (%d)" % retryCount)
                    time.sleep(settings.commFailureWaitTime)
                else:
                    debug.println(debug.LEVEL_WARNING,
                                  "  GIVING UP AFTER %d TRIES" \
                                  % (retryCount - 1))
                    atspi.Accessible.deleteAccessible(event.source)
            except:
                debug.printException(debug.LEVEL_WARNING)
                break

    def _enqueueEvent(self, e):
        """Handles all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        # Uncomment these lines if you want to see what it's like without
        # the queue.
        #
        #if isinstance(e, input_event.KeyboardEvent):
        #    self._processKeyboardEvent(e)
        #elif isinstance(e, input_event.BrailleEvent):
        #    self._processBrailleEvent(e)
        #else:
        #    self._processObjectEvent(atspi.Event(e))
        #return

        event = None
        if isinstance(e, input_event.KeyboardEvent):
            if e.type == atspi.Accessibility.KEY_PRESSED_EVENT:
                debug.println(debug.LEVEL_FINEST,
                              "----------> QUEUEING KEYPRESS '%s' (%d)"
                              % (e.event_string, e.hw_code))
            elif e.type == atspi.Accessibility.KEY_RELEASED_EVENT:
                debug.println(debug.LEVEL_FINEST,
                              "----------> QUEUEING KEYRELEASE '%s' (%d)"
                              % (e.event_string, e.hw_code))
            event = e
        elif isinstance(e, input_event.BrailleEvent):
            debug.println(debug.LEVEL_FINEST,
                          "----------> QUEUEING BRAILLE COMMAND %d" % e.event)
            event = e
        else:
            # We ignore defunct objects and let the atspi module take
            # care of them for us.
            #
            if (e.type == "object:state-changed:defunct"):
                return

            # We also generally do not like
            # object:property-change:accessible-parent events because
            # they indicate something is now whacked with the
            # hierarchy, so we just ignore them and let the atspi
            # module take care of it for us.
            #
            if e.type == "object:property-change:accessible-parent":
                return

            # At this point in time, we only care when objects are
            # removed from the desktop.
            #
            if (e.type == "object:children-changed:remove") \
                and (e.source != self.registry.desktop):
                return

            # We create the event here because it will ref everything
            # we want it to ref, thus allowing things to survive until
            # they are processed on the gidle thread.
            #
            debug.println(debug.LEVEL_FINEST,
                          "---------> QUEUEING EVENT %s" % e.type)
            event = atspi.Event(e)

        if event:
            self._eventQueue.put(event)
            if not self._gidle_id:
                self._gidle_id = gobject.idle_add(self._dequeueEvent)

    def _timeout(self):
        """Timer that will be called if we time out while trying to perform
        an operation."""
        debug.println(debug.LEVEL_SEVERE,
                      "TIMEOUT: Looks like something has hung. Quitting Orca.")
        orca.shutdown()

    def _dequeueEvent(self):
        """Handles all events destined for scripts.  Called by the GTK
        idle thread.
        """

        event = self._eventQueue.get()

        if isinstance(event, input_event.KeyboardEvent):
            if event.type == atspi.Accessibility.KEY_PRESSED_EVENT:
                debug.println(debug.LEVEL_FINEST,
                              "DEQUEUED KEYPRESS '%s' (%d) <----------" \
                              % (event.event_string, event.hw_code))
                pressRelease = "PRESS"
            elif event.type == atspi.Accessibility.KEY_RELEASED_EVENT:
                debug.println(debug.LEVEL_FINEST,
                              "DEQUEUED KEYRELEASE '%s' (%d) <----------" \
                              % (event.event_string, event.hw_code))
                pressRelease = "RELEASE"
            debug.println(debug.eventDebugLevel,
                          "\nvvvvv PROCESS KEY %s EVENT %s vvvvv"\
                          % (pressRelease, event.event_string))
            self._processKeyboardEvent(event)
            debug.println(debug.eventDebugLevel,
                          "\n^^^^^ PROCESS KEY %s EVENT %s ^^^^^"\
                          % (pressRelease, event.event_string))
        elif isinstance(event, input_event.BrailleEvent):
            debug.println(debug.LEVEL_FINEST,
                          "DEQUEUED BRAILLE COMMAND %d <----------" \
                          % event.event)
            debug.println(debug.eventDebugLevel,
                          "\nvvvvv PROCESS BRAILLE EVENT %d vvvvv"\
                          % event.event)
            self._processBrailleEvent(event)
            debug.println(debug.eventDebugLevel,
                          "\n^^^^^ PROCESS BRAILLE EVENT %d ^^^^^"\
                          % event.event)
        else:
            debug.println(debug.LEVEL_FINEST, "DEQUEUED EVENT %s <----------" \
                          % event.type)

            # [[[TODO: WDW - the timer stuff is an experiment to see if
            # we can recover from hangs.  It's only experimental, so it's
            # commented out for now.]]]
            #
            #timer = threading.Timer(5.0, self._timeout)
            #timer.start()

            if debug.eventDebugFilter \
                and debug.eventDebugFilter.match(event.type):
                debug.println(debug.eventDebugLevel,
                              "\nvvvvv PROCESS OBJECT EVENT %s vvvvv" \
                              % event.type)
            self._processObjectEvent(event)
            if debug.eventDebugFilter \
                and debug.eventDebugFilter.match(event.type):
                debug.println(debug.eventDebugLevel,
                              "^^^^^ PROCESS OBJECT EVENT %s ^^^^^\n" \
                              % event.type)

            #timer.cancel()
            #del timer

        if self._eventQueue.empty():
            if not orca.locusOfFocus \
                or (orca.locusOfFocus.state.count(\
                    atspi.Accessibility.STATE_SENSITIVE) == 0):
                delta = time.time() - self.lastNoFocusTime
                if delta > settings.noFocusWaitTime:
                    message = _("No focus")
                    braille.displayMessage(message)
                    speech.speak(message)
                    self.lastNoFocusTime = time.time()

            self._gidle_id = 0
            return False # destroy and don't call again
        else:
            return True  # call again at next idle

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event based on the keybinding from the
        currently active script. This method is called synchronously from the
        at-spi registry and should be performant.  In addition, it must return
        True if it has consumed the event (and False if not).

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event should be consumed.
        """

        if self._activeScript \
           and self._activeScript.consumesKeyboardEvent(keyboardEvent):
            self._enqueueEvent(keyboardEvent)
            return True
        else:
            return False

    def processBrailleEvent(self, brailleEvent):
        """Called whenever a cursor key is pressed on the Braille display.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent

        Returns True if the command was consumed; otherwise False
        """

        if self._activeScript \
           and self._activeScript.consumesBrailleEvent(brailleEvent):
            self._enqueueEvent(brailleEvent)
            return True
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
        self._activeScript   = self._getScript(None)

        self._registerEventListener("window:activate")
        self._registerEventListener("window:deactivate")
        self._registerEventListener("object:children-changed:remove")

        win = util.findActiveWindow()
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
            self._enqueueEvent(e)

    def deactivate(self):
        """Called when this presentation manager is deactivated."""

        for eventType in self._listenerCounts.keys():
            self.registry.deregisterEventListener(self._enqueueEvent,
                                                  eventType)
        self._listenerCounts = {}
        self._knownScripts   = {}
        self._defaultScript  = None
        self._activeScript   = None
