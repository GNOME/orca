# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

__id__  = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import gobject
import Queue
import threading
import time

import pyatspi
import braille
import default
import debug
import input_event
import orca_state
import presentation_manager
import settings
import speech

from orca_i18n import _ # for gettext support

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
        self.registry        = pyatspi.Registry
        self._knownScripts   = {}
        self._knownAppSettings = {}
        self._oldAppSettings = None
        self._eventQueue     = Queue.Queue(0)
        self._gidleId        = 0
        self._gidleLock      = threading.Lock()
        self.noFocusTimestamp = 0.0

        self.setActiveScript(None)

        if settings.debugEventQueue:
            self._enqueueEventCount = 0
            self._dequeueEventCount = 0

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
        if (not script) and app and getattr(app, "toolkitName", None):
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

    def setActiveScript(self, newScript):
        """Set the new active script.

        Arguments:
        - newScript: the new script to be made active.
        """

        try:
            # If old ("factory") settings don't exist yet, save
            # a set, else restore the old application settings.
            #
            if not self._oldAppSettings:
                self._oldAppSettings = \
                    orca_state.activeScript.saveOldAppSettings()
            else:
                orca_state.activeScript.restoreOldAppSettings( \
                    self._oldAppSettings)

            orca_state.activeScript.deactivate()
        except:
            pass

        orca_state.activeScript = newScript

        try:
            orca_state.activeScript.activate()
        except:
            pass

    def _cleanupCache(self):
        """Looks for defunct accessible objects in the cache and removes them.
        """

        objectsRemoved = 0
        debug.println(debug.LEVEL_FINEST,
                      "_cleanupCache: %d objects removed." % objectsRemoved)

    def _cleanupGarbage(self):
        """Cleans up garbage on the heap."""
        import gc
        gc.collect()
        for obj in gc.garbage:
            try:
                if isinstance(obj, pyatspi.Accessibility.Accessible):
                    gc.garbage.remove(obj)
                    obj.__del__()
            except:
                pass

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
            desktop = self.registry.getDesktop(0)

            for app in self._knownScripts.keys():
                if app not in desktop:
                    script = self._knownScripts[app]
                    self._deregisterEventListeners(script)

                    # Provide a bunch of hints to the garbage collector
                    # that we just don't care about this stuff any longer.
                    # Note the "app.app = None" - that helps remove a
                    # cycle of the application referring to itself.
                    #
                    del self._knownScripts[app]
                    del app
                    del script
        except:
            debug.printException(debug.LEVEL_FINEST)

    ########################################################################
    #                                                                      #
    # METHODS FOR KEEPING TRACK OF APPLICATION SETTINGS.                   #
    #                                                                      #
    ########################################################################

    def loadAppSettings(self, script):
        """Load the users application specific settings for an app.

        Arguments:
        - script: the current active script.
        """

        app = script.app
        settingsPackages = settings.settingsPackages
        moduleName = settings.getScriptModuleName(app)

        if moduleName and len(moduleName):
            for package in settingsPackages:
                if len(package):
                    name = package + "." + moduleName
                else:
                    name = moduleName
                try:
                    debug.println(debug.LEVEL_FINEST,
                                  "Looking for settings at %s.py..." % name)
                    if not self._knownAppSettings.has_key(name):
                        self._knownAppSettings[name] = \
                            __import__(name, globals(), locals(), [''])
                    reload(self._knownAppSettings[name])
                    debug.println(debug.LEVEL_FINEST,
                                  "...found %s.py" % name)

                    # Setup the user's application specific key bindings.
                    # (if any).
                    #
                    if hasattr(self._knownAppSettings[name],
                               "overrideAppKeyBindings"):
                        script.overrideAppKeyBindings = \
                            self._knownAppSettings[name].overrideAppKeyBindings
                        script.keyBindings = \
                         self._knownAppSettings[name].overrideAppKeyBindings( \
                            script, script.keyBindings)

                    # Setup the user's application specific pronunciations
                    # (if any).
                    #
                    if hasattr(self._knownAppSettings[name],
                               "overridePronunciations"):
                        script.overridePronunciations = \
                            self._knownAppSettings[name].overridePronunciations
                        script.app_pronunciation_dict = \
                         self._knownAppSettings[name].overridePronunciations( \
                            script, script.app_pronunciation_dict)

                    break
                except ImportError:
                    debug.println(debug.LEVEL_FINEST,
                                  "...could not find %s.py" % name)

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
        if orca_state.activeScript:
            try:
                orca_state.activeScript.processKeyboardEvent(keyboardEvent)
            except:
                debug.printException(debug.LEVEL_WARNING)
                debug.printStack(debug.LEVEL_WARNING)

    def _processBrailleEvent(self, brailleEvent):
        """Called whenever a cursor key is pressed on the Braille display.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent
        """
        if orca_state.activeScript:
            try:
                orca_state.activeScript.processBrailleEvent(brailleEvent)
            except:
                debug.printException(debug.LEVEL_WARNING)
                debug.printStack(debug.LEVEL_WARNING)

    def _processObjectEvent(self, event):
        """Handles all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        debug.printObjectEvent(debug.LEVEL_FINEST, event)

        # [[[TODO: WDW - HACK to prevent gnome-panel from killing
        # itself.  It seems to do so after it issues some tool tip
        # events and Orca attempts to process them.  We're not really
        # doing anything with tool tips right now, so we just ignore
        # them.  Note that this is just a bandaid to the problem.  We
        # should do something better.  Please refer to bug 368626
        # http://bugzilla.gnome.org/show_bug.cgi?id=368626 to follow
        # this problem.]]]
        #
        try:
            if event.source.getRole() == pyatspi.ROLE_TOOL_TIP:
                # Check that it's okay to present tool tips. Always present
                # tooltips initiated by the user pressing Control-F1 on the
                # keyboard.
                #
                if isinstance(orca_state.lastInputEvent, \
                              input_event.KeyboardEvent):
                    if not orca_state.lastNonModifierKeyEvent.event_string \
                                                                     == "F1":
                        return

                    # Mouse move events don't update orca_state.lastInputEvent
                    # so it's possible the user accidentally nudged the
                    # mouse and generated another tooltip event. If the
                    # current time minus the last keyboard event time is
                    # greater than 0.2 seconds, than just ignore this tooltip
                    # event.
                    #
                    currentTime =  time.time()
                    if (currentTime - orca_state.lastInputEvent.time) > 0.2:
                        return
                elif not settings.presentToolTips:
                    return
        except:
            pass

        # Reclaim (delete) any scripts when desktop children go away.
        # The idea here is that a desktop child is an app. We also
        # generally do not like object:children-changed:remove events,
        # either.
        #
        if event.type.startswith("object:children-changed:remove"):
            if event.source == self.registry.getDesktop(0):
                self._reclaimScripts()
                self._cleanupCache()
                if settings.debugMemoryUsage:
                    self._cleanupGarbage()
            return

        try:
            # We don't want to touch a defunct object.  It's useless and it
            # can cause hangs.
            #
            if event.source:
                state = event.source.getState()
                if state.contains(pyatspi.STATE_DEFUNCT):
                    debug.println(debug.LEVEL_FINEST,
                                  "IGNORING DEFUNCT OBJECT")
                    return

            if (not debug.eventDebugFilter) \
                or (debug.eventDebugFilter \
                    and debug.eventDebugFilter.match(event.type)):
                if not event.type.startswith("mouse:"):
                    debug.printDetails(debug.LEVEL_FINEST, "    ", event.source)

        except LookupError:
            debug.printException(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "LookupError above while processing event: %s" %\
                          event.type)
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
        oldLocusOfFocus = orca_state.locusOfFocus
        try:
            # If we've received a mouse event, then don't try to get
            # event.source.getApplication() because the top most parent
            # is of role unknown, which will cause an ERROR message to be
            # displayed. See Orca bug #409731 for more details.
            #
            if not event.type.startswith("mouse:"):
                s = self._getScript(event.source.getApplication())
            else:
                s = orca_state.activeScript
            if not s:
                return
        except:
            s = None
            debug.printException(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "ERROR: received an event, but Script is None")

        while s and retryCount <= s.commFailureAttemptLimit:
            try:
                state = event.source.getState()
                if not state.contains(pyatspi.STATE_ICONIFIED):

                    # [[[TODO: WDW - HACK we look for frame that get
                    # focus: as a means to detect active scripts
                    # because yelp does this.  Actually, yelp is a bit
                    # odd in that it calls itself 'yelp' then changes
                    # its application name and id to the Gecko toolkit
                    # in use, and then issues a focus: event on the
                    # main window, which is a frame.]]]
                    #
                    if (event.type == "window:activate") \
                       or ((event.type.startswith("focus")) 
                           and (event.source.getRole() == pyatspi.ROLE_FRAME)):
                        # We'll let someone else decide if it's important
                        # to stop speech or not.
                        #speech.stop()
                        debug.println(debug.LEVEL_FINE, "ACTIVE SCRIPT: " \
                                      + orca_state.activeScript.name)

                        self.setActiveScript(
                            self._getScript(event.source.getApplication()))

                        # Load in the application specific settings for the
                        # app for this event (if found).
                        #
                        self.loadAppSettings(orca_state.activeScript)

                        # Tell BrlTTY which commands we care about.
                        #
                        braille.setupKeyRanges(\
                            orca_state.activeScript.brailleBindings.keys())
                    s.processObjectEvent(event)
                    if retryCount:
                        debug.println(debug.LEVEL_WARNING,
                                      "  SUCCEEDED AFTER %d TRIES" % retryCount)
                break
            except LookupError:
                debug.printException(debug.LEVEL_WARNING)
                debug.println(debug.LEVEL_WARNING,
                              "LookupError above while processing: %s" % \
                              event.type)
                retryCount += 1
                if retryCount <= s.commFailureAttemptLimit:
                    # We want the old locus of focus to be reset so
                    # the proper stuff will be spoken if the locus
                    # of focus changed during our last attempt at
                    # handling this event.
                    #
                    orca_state.locusOfFocus = oldLocusOfFocus
                    debug.println(debug.LEVEL_WARNING,
                                  "  TRYING AGAIN (%d)" % retryCount)
                    time.sleep(s.commFailureWaitTime)
                else:
                    debug.println(debug.LEVEL_WARNING,
                                  "  GIVING UP AFTER %d TRIES" \
                                  % (retryCount - 1))
            except:
                debug.printException(debug.LEVEL_WARNING)
                break

    def _enqueueEvent(self, e):
        """Handles all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        if settings.debugEventQueue:
            if self._enqueueEventCount:
                debug.println(debug.LEVEL_ALL,
                              "focus_tracking_presenter._enqueueEvent has " \
                              "been entered before exiting (count = %d)" \
                              % self._enqueueEventCount)
            self._enqueueEventCount += 1

        event = None
        if isinstance(e, input_event.KeyboardEvent):
            if e.type == pyatspi.KEY_PRESSED_EVENT:
                debug.println(debug.LEVEL_ALL,
                              "----------> QUEUEING KEYPRESS '%s' (%d)"
                              % (e.event_string, e.hw_code))
            elif e.type == pyatspi.KEY_RELEASED_EVENT:
                debug.println(debug.LEVEL_ALL,
                              "----------> QUEUEING KEYRELEASE '%s' (%d)"
                              % (e.event_string, e.hw_code))
            event = e
        elif isinstance(e, input_event.BrailleEvent):
            debug.println(debug.LEVEL_ALL,
                          "----------> QUEUEING BRAILLE COMMAND %d" % e.event)
            event = e
        else:
            # We ignore defunct objects.
            #
            if e.type.startswith("object:state-changed:defunct"):
                if settings.debugEventQueue:
                    self._enqueueEventCount -= 1
                return

            # We also generally do not like
            # object:property-change:accessible-parent events because
            # they indicate something is now whacked with the
            # hierarchy.
            #
            if e.type.startswith("object:property-change:accessible-parent"):
                if settings.debugEventQueue:
                    self._enqueueEventCount -= 1
                return

            # At this point in time, we only care when objects are
            # removed from the desktop.
            #
            if e.type.startswith("object:children-changed:remove") \
                and (e.source != self.registry.getDesktop(0)):
                if settings.debugEventQueue:
                    self._enqueueEventCount -= 1
                return

            # If the event doesn't have a source or that source is not marked
            # valid, then we don't care about this event. Just return.
            #
            
            event = e
            if not event.source:
                debug.println(debug.LEVEL_FINEST,
                      "---------> IGNORING INVALID EVENT %s" % e.type)
                if settings.debugEventQueue:
                    self._enqueueEventCount -= 1
                return

            if (not debug.eventDebugFilter) \
                or (debug.eventDebugFilter \
                    and debug.eventDebugFilter.match(e.type)):
                debug.println(debug.LEVEL_ALL,
                              "---------> QUEUEING EVENT %s" % e.type)

        if event:
            if settings.debugEventQueue:
                debug.println(debug.LEVEL_ALL,
                              "           acquiring lock...")
            self._gidleLock.acquire()
            if settings.debugEventQueue:
                debug.println(debug.LEVEL_ALL,
                              "           ...acquired")
                debug.println(debug.LEVEL_ALL,
                              "           calling queue.put...")
                debug.println(debug.LEVEL_ALL,
                              "           (full=%s)" % self._eventQueue.full())
            self._eventQueue.put(event)
            if settings.debugEventQueue:
                debug.println(debug.LEVEL_ALL,
                              "           ...put complete")
            if settings.asyncMode and (not self._gidleId):
                if settings.gilSleepTime:
                    time.sleep(settings.gilSleepTime)
                self._gidleId = gobject.idle_add(self._dequeueEvent)

            if settings.debugEventQueue:
                debug.println(debug.LEVEL_ALL,
                              "           releasing lock...")
            self._gidleLock.release()
            if settings.debugEventQueue:
                debug.println(debug.LEVEL_ALL,
                              "           ...released")

            if not settings.asyncMode:
                self._dequeueEvent()

        if settings.debugEventQueue:
            self._enqueueEventCount -= 1

        # [[[TODO: HACK - on some hangs, we see the event queue growing,
        # but the thread to take the events off is hung.  We might be
        # able to 'recover' by quitting when we see this happen.]]]
        #
        #if self._eventQueue.qsize() > 500:
        #    print "Looks like something has hung.  Here's the threads:"
        #    for someThread in threading.enumerate():
        #        print someThread.getName(), someThread.isAlive()
        #    print "Quitting Orca."
        #    orca.shutdown()

    def _dequeueEvent(self):
        """Handles all events destined for scripts.  Called by the GTK
        idle thread.
        """

        rerun = True

        if settings.debugEventQueue:
            debug.println(debug.LEVEL_ALL,
                          "Entering focus_tracking_presenter._dequeueEvent" \
                          + " %d" % self._dequeueEventCount)
            self._dequeueEventCount += 1

        try:
            event = self._eventQueue.get_nowait()

            if isinstance(event, input_event.KeyboardEvent):
                if event.type == pyatspi.KEY_PRESSED_EVENT:
                    debug.println(debug.LEVEL_ALL,
                                  "DEQUEUED KEYPRESS '%s' (%d) <----------" \
                                  % (event.event_string, event.hw_code))
                    pressRelease = "PRESS"
                elif event.type == pyatspi.KEY_RELEASED_EVENT:
                    debug.println(debug.LEVEL_ALL,
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
                debug.println(debug.LEVEL_ALL,
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
                if (not debug.eventDebugFilter) \
                    or (debug.eventDebugFilter \
                        and debug.eventDebugFilter.match(event.type)):
                    debug.println(debug.LEVEL_ALL,
                                  "DEQUEUED EVENT %s <----------" \
                                  % event.type)
                    debug.println(debug.eventDebugLevel,
                                  "\nvvvvv PROCESS OBJECT EVENT %s vvvvv" \
                                  % event.type)
                self._processObjectEvent(event)
                if (not debug.eventDebugFilter) \
                    or (debug.eventDebugFilter \
                        and debug.eventDebugFilter.match(event.type)):
                    debug.println(debug.eventDebugLevel,
                                  "^^^^^ PROCESS OBJECT EVENT %s ^^^^^\n" \
                                  % event.type)

            # [[[TODO: HACK - it would seem logical to only do this if we
            # discover the queue is empty, but this inroduces a hang for
            # some reason if done inside an acquire/release block for a
            # lock.  So...we do it here.]]]
            #
            noFocus = (not orca_state.activeScript) \
                      or ((not orca_state.locusOfFocus) \
                          and (self.noFocusTimestamp \
                               != orca_state.noFocusTimestamp))

            self._gidleLock.acquire()
            if self._eventQueue.empty():
                if noFocus:
                    if settings.gilSleepTime:
                        time.sleep(settings.gilSleepTime)
                    # Translators: this is intended to be a short phrase to
                    # speak and braille to tell the user that no component
                    # has keyboard focus.
                    #
                    message = _("No focus")
                    if settings.brailleVerbosityLevel == \
                        settings.VERBOSITY_LEVEL_VERBOSE:
                        braille.displayMessage(message)
                    if settings.speechVerbosityLevel == \
                        settings.VERBOSITY_LEVEL_VERBOSE:
                        speech.speak(message)
                    self.noFocusTimestamp = orca_state.noFocusTimestamp
                self._gidleId = 0
                rerun = False # destroy and don't call again
            self._gidleLock.release()
        except Queue.Empty:
            debug.println(debug.LEVEL_SEVERE,
                          "focus_tracking_presenter:_dequeueEvent: " \
                          + " the event queue is empty!")
        except:
            debug.printException(debug.LEVEL_SEVERE)

        if settings.debugEventQueue:
            self._dequeueEventCount -= 1
            debug.println(debug.LEVEL_ALL,
                          "Leaving focus_tracking_presenter._dequeueEvent" \
                          + " %d" % self._dequeueEventCount)

        return rerun

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event based on the keybinding from the
        currently active script. This method is called synchronously from the
        at-spi registry and should be performant.  In addition, it must return
        True if it has consumed the event (and False if not).

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event should be consumed.
        """

        if orca_state.activeScript \
           and orca_state.activeScript.consumesKeyboardEvent(keyboardEvent):
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

        if orca_state.activeScript \
           and orca_state.activeScript.consumesBrailleEvent(brailleEvent):
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

        if orca_state.activeScript:
            orca_state.activeScript.locusOfFocusChanged(event,
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

        if orca_state.activeScript:
            orca_state.activeScript.visualAppearanceChanged(event, obj)

    def _saveAppStates(self):
        """Saves script and application state information."""
        self._appStateInfo = []
        for script in self._knownScripts.values():
            self._appStateInfo.append([script.app, script.getAppState()])

    def _restoreAppStates(self):
        """Restores script and application state information."""
        try:
            for [app, appState] in self._appStateInfo:
                script = self._getScript(app)
                script.setAppState(appState)
        except:
            pass

        self._appStateInfo = None

    def activate(self):
        """Called when this presentation manager is activated."""

        self._listenerCounts = {}
        self._knownScripts   = {}
        self._knownAppSettings = {}
        self._oldAppSettings = None
        self._defaultScript  = None

        self._restoreAppStates()

        self.setActiveScript(self._getScript(None))

        # Tell BrlTTY which commands we care about.
        #
        braille.setupKeyRanges(orca_state.activeScript.brailleBindings.keys())

        self._registerEventListener("window:activate")
        self._registerEventListener("window:deactivate")
        self._registerEventListener("object:children-changed:remove")

        win = orca_state.activeScript.findActiveWindow()
        if win:
            # Generate a fake window activation event so the application
            # can tell the user about itself.
            #
            class _FakeEvent:
                pass
            class _FakeData:
                def value(self):
                    return None
            fe = _FakeEvent()
            fe.source   = win
            fe.type     = "window:activate"
            fe.detail1  = 0
            fe.detail2  = 0
            fe.any_data = _FakeData()
            e = pyatspi.event.Event(fe)
            self._enqueueEvent(e)

    def deactivate(self):
        """Called when this presentation manager is deactivated."""

        self._saveAppStates()

        for eventType in self._listenerCounts.keys():
            self.registry.deregisterEventListener(self._enqueueEvent,
                                                  eventType)
        self._listenerCounts = {}
        self._knownScripts   = {}
        self._knownAppSettings = {}
        self._oldAppSettings = None
        self._defaultScript  = None

        self.setActiveScript(None)
