# Orca
#
# Copyright 2011. Orca Team.
# Author: Joanmarie Diggs <joanmarie.diggs@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011. Orca Team."
__license__   = "LGPL"

from gi.repository import GLib
import pyatspi
import queue
import threading
import time

from . import debug
from . import input_event
from . import messages
from . import orca_state
from . import script_manager
from . import settings

_scriptManager = script_manager.getManager()

class EventManager:

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'

    def __init__(self, asyncMode=True):
        debug.println(debug.LEVEL_FINEST, 'INFO: Initializing event manager')
        debug.println(debug.LEVEL_FINEST, 'INFO: Async Mode is %s' % asyncMode)
        self._asyncMode = asyncMode
        self._scriptListenerCounts = {}
        self.registry = pyatspi.Registry
        self._active = False
        self._enqueueCount = 0
        self._dequeueCount = 0
        self._eventQueue     = queue.Queue(0)
        self._gidleId        = 0
        self._gidleLock      = threading.Lock()
        self._gilSleepTime = 0.00001
        self._synchronousToolkits = ['VCL']
        self._ignoredEvents = ['object:bounds-changed',
                               'object:state-changed:defunct',
                               'object:property-change:accessible-parent']
        debug.println(debug.LEVEL_FINEST, 'INFO: Event manager initialized')

    def activate(self):
        """Called when this presentation manager is activated."""

        debug.println(debug.LEVEL_FINEST, 'INFO: Activating event manager')
        self._registerListener("window:activate")
        self._registerListener("window:deactivate")
        self._registerListener("object:children-changed")
        self._registerListener("mouse:button")
        self._active = True
        debug.println(debug.LEVEL_FINEST, 'INFO: Event manager activated')

    def deactivate(self):
        """Called when this event manager is deactivated."""

        debug.println(debug.LEVEL_FINEST, 'INFO: Dectivating event manager')
        self._active = False
        for eventType in list(self._scriptListenerCounts.keys()):
            self.registry.deregisterEventListener(self._enqueue, eventType)
        self._scriptListenerCounts = {}
        debug.println(debug.LEVEL_FINEST, 'INFO: Event manager deactivated')

    def ignoreEventTypes(self, eventTypeList):
        for eventType in eventTypeList:
            if not eventType in self._ignoredEvents:
                self._ignoredEvents.append(eventType)

    def unignoreEventTypes(self, eventTypeList):
        for eventType in eventTypeList:
            if eventType in self._ignoredEvents:
                self._ignoredEvents.remove(eventType)

    def _ignore(self, event):
        """Returns True if this event should be ignored."""

        msg = '\nINFO: %s for %s in %s' % (event.type, event.source, event.host_application)
        debug.println(debug.LEVEL_INFO, msg)

        if not self._active:
            msg = 'INFO: Ignoring because event manager is not active'
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if list(filter(event.type.startswith, self._ignoredEvents)):
            msg = 'INFO: Ignoring because event type is ignored'
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if event.type.startswith('window'):
            msg = 'INFO: Not ignoring because event type is never ignored'
            debug.println(debug.LEVEL_INFO, msg)
            return False

        # This should ultimately be changed as there are valid reasons
        # to handle these events at the application level.
        if event.type.startswith('object:children-changed:remove') \
           and event.source != self.registry.getDesktop(0):
            msg = 'INFO: Ignoring because event type is ignored'
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if event.type.startswith('object:text-changed') and event.type.endswith('system'):
            # We should also get children-changed events telling us the same thing.
            # Getting a bunch of both can result in a flood that grinds us to a halt.
            if event.any_data == self.EMBEDDED_OBJECT_CHARACTER:
                msg = 'INFO: Text changed event for embedded object. Who cares?'
                debug.println(debug.LEVEL_INFO, msg)
                return True

        try:
            # TODO - JD: For now we won't ask for the name. Simply asking for the name should
            # not break anything, and should be a reliable way to quickly identify defunct
            # objects. But apparently the mere act of asking for the name causes Orca to stop
            # presenting Eclipse (and possibly other) applications. This might be an AT-SPI2
            # issue, but until we know for certain....
            #name = event.source.name
            state = event.source.getState()
        except:
            msg = 'ERROR: %s from potentially-defunct source %s in app %s (%s, %s, %s)' % \
                  (event.type, event.source, event.host_application, event.detail1,
                   event.detail2, event.any_data)
            debug.println(debug.LEVEL_INFO, msg)
            return True
        if state.contains(pyatspi.STATE_DEFUNCT):
            msg = 'ERROR: %s from defunct source %s in app %s (%s, %s, %s)' % \
                  (event.type, event.source, event.host_application, event.detail1,
                   event.detail2, event.any_data)
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if event.type.startswith('object:state-changed:showing'):
            try:
                role = event.source.getRole()
            except:
                role = None
            if role in [pyatspi.ROLE_IMAGE, pyatspi.ROLE_MENU_ITEM, pyatspi.ROLE_PARAGRAPH]:
                msg = 'INFO: %s for %s in app %s. Who cares?' % \
                      (event.type, event.source, event.host_application)
                debug.println(debug.LEVEL_INFO, msg)
                return True

        if event.type.startswith('object:children-changed:add'):
            if not event.any_data:
                msg = 'ERROR: %s without child from source %s in app %s' % \
                      (event.type, event.source, event.host_application)
                debug.println(debug.LEVEL_INFO, msg)
                return True
            try:
                state = event.any_data.getState()
                role = event.any_data.getRole()
            except:
                msg = 'ERROR: %s with potentially-defunct child %s from source %s in app %s' % \
                      (event.type, event.any_data, event.source, event.host_application)
                debug.println(debug.LEVEL_INFO, msg)
                return True
            if state.contains(pyatspi.STATE_DEFUNCT):
                msg = 'ERROR: %s with defunct child %s from source %s in app %s' % \
                      (event.type, event.any_data, event.source, event.host_application)
                debug.println(debug.LEVEL_INFO, msg)
                return True

            # This should be safe. We do not have a reason to present a newly-added,
            # but not focused image. We do not need to update live regions for images.
            # This is very likely a completely and utterly useless event for us. The
            # reason for ignoring it here rather than quickly processing it is the
            # potential for event floods like we're seeing from matrix.org.
            if role == pyatspi.ROLE_IMAGE:
                msg = 'INFO: %s for child image %s from source %s in app %s. Who cares?' % \
                      (event.type, event.any_data, event.source, event.host_application)
                debug.println(debug.LEVEL_INFO, msg)
                return True

        msg = 'INFO: Not ignoring due to lack of cause'
        debug.println(debug.LEVEL_INFO, msg)
        return False

    def _addToQueue(self, event, asyncMode):
        debugging = debug.debugEventQueue
        if debugging:
            debug.println(debug.LEVEL_ALL, "           acquiring lock...")
        self._gidleLock.acquire()

        if debugging:
            debug.println(debug.LEVEL_ALL, "           ...acquired")
            debug.println(debug.LEVEL_ALL, "           calling queue.put...")
            debug.println(debug.LEVEL_ALL, "           (full=%s)" \
                          % self._eventQueue.full())

        self._eventQueue.put(event)
        if debugging:
            debug.println(debug.LEVEL_ALL, "           ...put complete")

        if asyncMode and not self._gidleId:
            if self._gilSleepTime:
                time.sleep(self._gilSleepTime)
            self._gidleId = GLib.idle_add(self._dequeue)

        if debugging:
            debug.println(debug.LEVEL_ALL, "           releasing lock...")
        self._gidleLock.release()
        if debug.debugEventQueue:
            debug.println(debug.LEVEL_ALL, "           ...released")

    def _queuePrintln(self, e, isEnqueue=True):
        """Convenience method to output queue-related debugging info."""

        if isinstance(e, input_event.KeyboardEvent):
            data = "'%s' (%d)" % (e.event_string, e.hw_code)
        elif isinstance(e, input_event.BrailleEvent):
            data = "'%s'" % repr(e.event)
        elif not debug.eventDebugFilter or debug.eventDebugFilter.match(e.type):
            data = "%s (%s,%s,%s) from %s" % \
                   (e.source, e.detail1, e.detail2, e.any_data, e.host_application)
        else:
            return

        eType = str(e.type).upper()
        if isEnqueue:
            string = "----------> QUEUEING %s %s" % (eType, data.upper())
        else:
            string = "DEQUEUED %s %s <----------" % (eType, data.upper())

        debug.println(debug.LEVEL_ALL, string)

    def _enqueue(self, e):
        """Handles the enqueueing of all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        if debug.debugEventQueue:
            if self._enqueueCount:
                msg = "_enqueue entered before exiting (count = %d)" \
                    % self._enqueueCount
                debug.println(debug.LEVEL_ALL, msg)
            self._enqueueCount += 1

        inputEvents = (input_event.KeyboardEvent, input_event.BrailleEvent)
        isObjectEvent = not isinstance(e, inputEvents)

        try:
            ignore = isObjectEvent and self._ignore(e)
        except:
            msg = 'ERROR: Exception evaluating event: %s' % e
            debug.println(debug.LEVEL_INFO, msg)
            ignore = True
        if ignore:
            if debug.debugEventQueue:
                self._enqueueCount -= 1
            return

        self._queuePrintln(e)

        asyncMode = self._asyncMode
        if isObjectEvent:
            app = e.source.getApplication()
            try:
                toolkitName = app.toolkitName
            except:
                toolkitName = None
            if toolkitName in self._synchronousToolkits:
                asyncMode = False
            script = _scriptManager.getScript(app, e.source)
            script.eventCache[e.type] = (e, time.time())

        self._addToQueue(e, asyncMode)
        if not asyncMode:
            self._dequeue()

        if debug.debugEventQueue:
            self._enqueueCount -= 1

    def _dequeue(self):
        """Handles all events destined for scripts. Called by the GTK
        idle thread."""

        rerun = True

        if debug.debugEventQueue:
            debug.println(debug.LEVEL_ALL,
                          "event_manager._dequeue %d" % self._dequeueCount)
            self._dequeueCount += 1

        try:
            event = self._eventQueue.get_nowait()
            self._queuePrintln(event, isEnqueue=False)
            inputEvents = (input_event.KeyboardEvent, input_event.BrailleEvent)
            if isinstance(event, inputEvents):
                self._processInputEvent(event)
            else:
                debug.objEvent = event
                debugging = not debug.eventDebugFilter \
                            or debug.eventDebugFilter.match(event.type)
                if debugging:
                    startTime = time.time()
                    debug.println(debug.eventDebugLevel,
                                  "\nvvvvv PROCESS OBJECT EVENT %s vvvvv" \
                                  % event.type)
                self._processObjectEvent(event)
                if debugging:
                    debug.println(debug.eventDebugLevel,
                                  "TOTAL PROCESSING TIME: %.4f" \
                                  % (time.time() - startTime))
                    debug.println(debug.eventDebugLevel,
                                  "^^^^^ PROCESS OBJECT EVENT %s ^^^^^\n" \
                                  % event.type)
                debug.objEvent = None

            # [[[TODO: HACK - it would seem logical to only do this if we
            # discover the queue is empty, but this inroduces a hang for
            # some reason if done inside an acquire/release block for a
            # lock.  So...we do it here.]]]
            #
            try:
                noFocus = not (orca_state.activeScript or orca_state.locusOfFocus)
            except:
                noFocus = True

            self._gidleLock.acquire()
            if self._eventQueue.empty():
                if noFocus:
                    if self._gilSleepTime:
                        time.sleep(self._gilSleepTime)
                    fullMessage = messages.NO_FOCUS
                    defaultScript = _scriptManager.getDefaultScript()
                    defaultScript.presentMessage(fullMessage, '')
                self._gidleId = 0
                rerun = False # destroy and don't call again
            self._gidleLock.release()
        except queue.Empty:
            debug.println(debug.LEVEL_SEVERE,
                          "event_manager._dequeue: the event queue is empty!")
            self._gidleId = 0
            rerun = False # destroy and don't call again
        except:
            debug.printException(debug.LEVEL_SEVERE)

        if debug.debugEventQueue:
            self._dequeueCount -= 1
            debug.println(debug.LEVEL_ALL,
                          "Leaving _dequeue. Count: %d" % self._dequeueCount)

        return rerun

    def _registerListener(self, eventType):
        """Tells this module to listen for the given event type.

        Arguments:
        - eventType: the event type.
        """

        debug.println(debug.LEVEL_FINEST,
                      'INFO: Event manager registering listener for: %s' \
                       % eventType)

        if eventType in self._scriptListenerCounts:
            self._scriptListenerCounts[eventType] += 1
        else:
            self.registry.registerEventListener(self._enqueue, eventType)
            self._scriptListenerCounts[eventType] = 1

    def _deregisterListener(self, eventType):
        """Tells this module to stop listening for the given event type.

        Arguments:
        - eventType: the event type.
        """

        debug.println(debug.LEVEL_FINEST,
                      'INFO: Event manager deregistering listener for: %s' \
                       % eventType)

        if not eventType in self._scriptListenerCounts:
            return

        self._scriptListenerCounts[eventType] -= 1
        if self._scriptListenerCounts[eventType] == 0:
            self.registry.deregisterEventListener(self._enqueue, eventType)
            del self._scriptListenerCounts[eventType]

    def registerScriptListeners(self, script):
        """Tells the event manager to start listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        debug.println(debug.LEVEL_FINEST,
                      'INFO: Event manager registering listeners for: %s' \
                       % script)

        for eventType in list(script.listeners.keys()):
            self._registerListener(eventType)

    def deregisterScriptListeners(self, script):
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        debug.println(debug.LEVEL_FINEST,
                      'INFO: Event manager deregistering listeners for: %s' \
                       % script)

        for eventType in list(script.listeners.keys()):
            self._deregisterListener(eventType)

    def registerModuleListeners(self, listeners):
        """Register the listeners on behalf of the caller."""

        for eventType, function in list(listeners.items()):
            self.registry.registerEventListener(function, eventType)

    def deregisterModuleListeners(self, listeners):
        """Deegister the listeners on behalf of the caller."""

        for eventType, function in list(listeners.items()):
            self.registry.deregisterEventListener(function, eventType)

    def registerKeystrokeListener(self, function, mask=None, kind=None):
        """Register the keystroke listener on behalf of the caller."""

        debug.println(
            debug.LEVEL_FINEST,
            'INFO: Event manager registering keystroke listener function: %s' \
             % function)

        if mask == None:
            mask = list(range(256))

        if kind == None:
            kind = (pyatspi.KEY_PRESSED_EVENT, pyatspi.KEY_RELEASED_EVENT)

        self.registry.registerKeystrokeListener(function, mask=mask, kind=kind)

    def deregisterKeystrokeListener(self, function, mask=None, kind=None):
        """Deregister the keystroke listener on behalf of the caller."""

        debug.println(
            debug.LEVEL_FINEST,
            'INFO: Event manager deregistering keystroke listener function: %s'\
             % function)

        if mask == None:
            mask = list(range(256))

        if kind == None:
            kind = (pyatspi.KEY_PRESSED_EVENT, pyatspi.KEY_RELEASED_EVENT)

        self.registry.deregisterKeystrokeListener(
            function, mask=mask, kind=kind)

    def _processInputEvent(self, event):
        """Processes the given input event based on the keybinding from the
        currently-active script.

        Arguments:
        - event: an instance of BrailleEvent or a KeyboardEvent
        """

        if not orca_state.activeScript:
            return

        if isinstance(event, input_event.KeyboardEvent):
            function = orca_state.activeScript.processKeyboardEvent
            data = "'%s' (%d)" % (event.event_string, event.hw_code)
        elif isinstance(event, input_event.BrailleEvent):
            function = orca_state.activeScript.processBrailleEvent
            data = "'%s'" % repr(event.event)
        else:
            return

        eType = str(event.type).upper()
        startTime = time.time()
        debug.println(debug.eventDebugLevel,
                      "\nvvvvv PROCESS %s %s vvvvv" % (eType, data))
        try:
            function(event)
        except:
            debug.printException(debug.LEVEL_WARNING)
            debug.printStack(debug.LEVEL_WARNING)
        debug.println(debug.eventDebugLevel,
                      "TOTAL PROCESSING TIME: %.4f" \
                      % (time.time() - startTime))
        debug.println(debug.eventDebugLevel,
                      "^^^^^ PROCESS %s %s ^^^^^\n" % (eType, data))

    @staticmethod
    def _getScriptForEvent(event):
        """Returns the script associated with event."""

        if event.type.startswith("mouse:"):
            return orca_state.activeScript

        script = None
        app = None
        try:
            app = event.host_application or event.source.getApplication()
            if app and app.getState().contains(pyatspi.STATE_DEFUNCT):
                msg = 'WARNING: App is defunct. Cannot get script for event.'
                debug.println(debug.LEVEL_WARNING, msg)
                return None
        except:
            msg = 'WARNING: Exception when getting script for event.'
            debug.println(debug.LEVEL_WARNING, msg)
        else:
            msg = 'INFO: Getting script for %s from %s' % (event.type, app)
            debug.println(debug.LEVEL_INFO, msg)
            script = _scriptManager.getScript(app, event.source)

        msg = 'INFO: Script for %s from %s is %s' % (event.type, app, script)
        debug.println(debug.LEVEL_INFO, msg)
        return script

    def _isActivatableEvent(self, event, script=None):
        """Determines if the event is one which should cause us to
        change which script is currently active.

        Returns a (boolean, string) tuple indicating whether or not
        this is an activatable event, and our reason (for the purpose
        of debugging).
        """

        if not event.source:
            return False, "event.source? What event.source??"

        role = state = None
        try:
            role = event.source.getRole()
        except (LookupError, RuntimeError):
            return False, "Error getting event.source's role"
        try:
            state = event.source.getState()
        except (LookupError, RuntimeError):
            return False, "Error getting event.source's state"
        
        if not script:
            script = self._getScriptForEvent(event)

        if not script:
            return False, "There is no script for this event."

        if script == orca_state.activeScript:
            return False, "The script for this event is already active."

        if not script.isActivatableEvent(event):
            return False, "The script says not to activate for this event."

        eType = event.type
        if eType.startswith('window:activate'):
            return True, "window:activate event"

        if eType.startswith('focus') \
           or (eType.startswith('object:state-changed:focused')
               and event.detail1):
            return True, "Event source claimed focus."

        # This condition appears with gnome-screensave-dialog.
        # See bug 530368.
        if eType.startswith('object:state-changed:showing') \
           and role == pyatspi.ROLE_PANEL \
           and state.contains(pyatspi.STATE_MODAL):
            return True, "Modal panel is showing."

        return False, "No reason found to activate a different script."

    def _processObjectEvent(self, event):
        """Handles all object events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        debug.printObjectEvent(debug.LEVEL_FINEST, event)
        eType = event.type

        if eType.startswith("object:children-changed:remove"):
            try:
                if event.source == self.registry.getDesktop(0):
                    _scriptManager.reclaimScripts()
                    return
            except (LookupError, RuntimeError):
                # If we got this error here, we'll get it again when we
                # attempt to get the state, catch it, and clean up.
                pass
            except:
                debug.printException(debug.LEVEL_WARNING)
                return

        # Clean up any flat review context so that Orca does not get
        # confused (see bgo#609633)
        #
        if eType.startswith("window:deactivate") \
           and orca_state.activeScript \
           and orca_state.activeScript.flatReviewContext \
           and orca_state.activeScript.app == event.host_application:
            orca_state.activeScript.flatReviewContext = None

        try:
            state = event.source.getState()
        except (LookupError, RuntimeError):
            debug.println(debug.LEVEL_WARNING,
                          "Error while processing event: %s" % eType)
            if eType.startswith("window:deactivate"):
                orca_state.locusOfFocus = None
                orca_state.activeWindow = None
            return
        except:
            return

        if state and state.contains(pyatspi.STATE_DEFUNCT):
            debug.println(debug.LEVEL_FINEST, "IGNORING DEFUNCT OBJECT")
            if eType.startswith("window:deactivate"):
                orca_state.locusOfFocus = None
                orca_state.activeWindow = None
            return

        if state and state.contains(pyatspi.STATE_ICONIFIED):
            debug.println(debug.LEVEL_FINEST, "IGNORING ICONIFIED OBJECT")
            return

        if not debug.eventDebugFilter or debug.eventDebugFilter.match(eType) \
           and not eType.startswith("mouse:"):
            debug.printDetails(debug.LEVEL_FINEST, "    ", event.source)

        script = self._getScriptForEvent(event)
        if not script:
            msg = 'ERROR: Could not get script for %s' % event
            debug.println(debug.LEVEL_INFO, msg)
            return

        setNewActiveScript, reason = self._isActivatableEvent(event, script)
        if setNewActiveScript:
            try:
                app = event.host_application or event.source.getApplication()
            except:
                msg = 'ERROR: Could not get application for %s' % event.source
                debug.println(debug.LEVEL_INFO, msg)
                return
            try:
                _scriptManager.setActiveScript(script, reason)
            except:
                msg = 'ERROR: Could not set active script for %s' % event.source
                debug.println(debug.LEVEL_INFO, msg)
                return

        try:
            script.processObjectEvent(event)
        except:
            msg = 'ERROR: Could not process %s' % event.type
            debug.println(debug.LEVEL_INFO, msg)

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event based on the keybinding from the
        currently active script. This method is called synchronously from the
        at-spi registry and should be performant.  In addition, it must return
        True if it has consumed the event (and False if not).

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event should be consumed.
        """

        consume = False
        if orca_state.activeScript \
           and orca_state.activeScript.consumesKeyboardEvent(keyboardEvent):
            consume = not orca_state.bypassNextCommand
            if consume:
                self._enqueue(keyboardEvent)

        return consume

    def processBrailleEvent(self, brailleEvent):
        """Called whenever a cursor key is pressed on the Braille display.

        Arguments:
        - brailleEvent: an instance of input_event.BrailleEvent

        Returns True if the command was consumed; otherwise False
        """

        if orca_state.activeScript \
           and orca_state.activeScript.consumesBrailleEvent(brailleEvent):
            self._enqueue(brailleEvent)
            return True
        else:
            return False

_manager = EventManager()

def getManager():
    return _manager
