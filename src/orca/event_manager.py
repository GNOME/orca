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

from gi.repository import GObject
import pyatspi
import Queue
import threading
import time

from . import debug
from . import input_event
from . import orca_state
from . import script_manager
from . import settings

from .orca_i18n import _

_scriptManager = script_manager.getManager()

class EventManager:

    def __init__(self):
        debug.println(debug.LEVEL_FINEST, 'INFO: Initializing event manager')
        self._scriptListenerCounts = {}
        self.registry = pyatspi.Registry
        self._enqueueCount = 0
        self._dequeueCount = 0
        self._eventQueue     = Queue.Queue(0)
        self._gidleId        = 0
        self._gidleLock      = threading.Lock()
        self.noFocusTimestamp = 0.0
        debug.println(debug.LEVEL_FINEST, 'INFO: Event manager initialized')

    def activate(self):
        """Called when this presentation manager is activated."""

        debug.println(debug.LEVEL_FINEST, 'INFO: Activating event manager')
        self._registerListener("window:activate")
        self._registerListener("window:deactivate")
        self._registerListener("object:children-changed")
        self._registerListener("mouse:button")
        debug.println(debug.LEVEL_FINEST, 'INFO: Event manager activated')

    def deactivate(self):
        """Called when this event manager is deactivated."""

        debug.println(debug.LEVEL_FINEST, 'INFO: Dectivating event manager')
        for eventType in list(self._scriptListenerCounts.keys()):
            self.registry.deregisterEventListener(self._enqueue, eventType)
        self._scriptListenerCounts = {}
        debug.println(debug.LEVEL_FINEST, 'INFO: Event manager deactivated')

    def _ignore(self, event):
        """Returns True if this event should be ignored."""

        if not event or not event.source:
            return True

        ignoredList = ['object:state-changed:defunct',
                       'object:property-change:accessible-parent']
        ignoredList.extend(settings.ignoredEventsList)
        if list(filter(event.type.startswith, ignoredList)):
            return True

        # This should ultimately be changed as there are valid reasons
        # to handle these events at the application level.
        if event.type.startswith('object:children-changed:remove') \
           and event.source != self.registry.getDesktop(0):
            return True

        return False

    def _addToQueue(self, event, asyncMode):
        debugging = settings.debugEventQueue
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
            if settings.gilSleepTime:
                time.sleep(settings.gilSleepTime)
            self._gidleId = GObject.idle_add(self._dequeue)

        if debugging:
            debug.println(debug.LEVEL_ALL, "           releasing lock...")
        self._gidleLock.release()
        if settings.debugEventQueue:
            debug.println(debug.LEVEL_ALL, "           ...released")

    def _queuePrintln(self, e, isEnqueue=True):
        """Convenience method to output queue-related debugging info."""

        if isinstance(e, input_event.KeyboardEvent):
            data = "'%s' (%d)" % (e.event_string, e.hw_code)
        elif isinstance(e, input_event.BrailleEvent):
            data = "'%s'" % repr(e.event)
        elif not debug.eventDebugFilter or debug.eventDebugFilter.match(e.type):
            data = ""
        else:
            return

        eType = str(e.type).upper()
        if isEnqueue:
            string = "----------> QUEUEING %s %s" % (eType, data)
        else:
            string = "DEQUEUED %s %s <----------" % (eType, data)

        debug.println(debug.LEVEL_ALL, string)

    def _enqueue(self, e):
        """Handles the enqueueing of all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        if settings.debugEventQueue:
            if self._enqueueCount:
                msg = "_enqueue entered before exiting (count = %d)" \
                    % self._enqueueCount
                debug.println(debug.LEVEL_ALL, msg)
            self._enqueueCount += 1

        inputEvents = (input_event.KeyboardEvent, input_event.BrailleEvent)
        isObjectEvent = not isinstance(e, inputEvents)
        if isObjectEvent and self._ignore(e):
            if settings.debugEventQueue:
                self._enqueueCount -= 1
            return

        self._queuePrintln(e)

        asyncMode = settings.asyncMode
        if isObjectEvent:
            app = e.source.getApplication()
            try:
                toolkitName = app.toolkitName
            except:
                toolkitName = None
            if toolkitName in settings.synchronousToolkits:
                asyncMode = False
            script = _scriptManager.getScript(app, e.source)
            script.eventCache[e.type] = (e, time.time())

        self._addToQueue(e, asyncMode)
        if not asyncMode:
            self._dequeue()

        if settings.debugEventQueue:
            self._enqueueCount -= 1

    def _dequeue(self):
        """Handles all events destined for scripts. Called by the GTK
        idle thread."""

        rerun = True

        if settings.debugEventQueue:
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
                orca_state.currentObjectEvent = event
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
                orca_state.currentObjectEvent = None

            # [[[TODO: HACK - it would seem logical to only do this if we
            # discover the queue is empty, but this inroduces a hang for
            # some reason if done inside an acquire/release block for a
            # lock.  So...we do it here.]]]
            #
            noFocus = \
                not orca_state.activeScript \
                or (not orca_state.locusOfFocus \
                    and self.noFocusTimestamp != orca_state.noFocusTimestamp)

            self._gidleLock.acquire()
            if self._eventQueue.empty():
                if noFocus:
                    if settings.gilSleepTime:
                        time.sleep(settings.gilSleepTime)
                    # Translators: this is intended to be a short phrase to
                    # speak and braille to tell the user that no component
                    # has keyboard focus.
                    #
                    fullMessage = _("No focus")
                    defaultScript = _scriptManager.getDefaultScript()
                    defaultScript.presentMessage(fullMessage, '')
                    self.noFocusTimestamp = orca_state.noFocusTimestamp
                self._gidleId = 0
                rerun = False # destroy and don't call again
            self._gidleLock.release()
        except Queue.Empty:
            debug.println(debug.LEVEL_SEVERE,
                          "event_manager._dequeue: the event queue is empty!")
            self._gidleId = 0
            rerun = False # destroy and don't call again
        except:
            debug.printException(debug.LEVEL_SEVERE)

        if settings.debugEventQueue:
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
        debug.println(debug.eventDebugLevel,
                      "\nvvvvv PROCESS %s %s vvvvv" % (eType, data))
        try:
            function(event)
        except:
            debug.printException(debug.LEVEL_WARNING)
            debug.printStack(debug.LEVEL_WARNING)
        debug.println(debug.eventDebugLevel,
                      "^^^^^ PROCESS %s %s ^^^^^\n" % (eType, data))

    @staticmethod
    def _getScriptForEvent(event):
        """Returns the script associated with event."""

        if event.type.startswith("mouse:"):
            return orca_state.activeScript

        script = None
        try:
            app = event.host_application or event.source.getApplication()
            if app and app.getState().contains(pyatspi.STATE_DEFUNCT):
                msg = 'WARNING: App is defunct. Cannot get script for event.'
                debug.println(debug.LEVEL_WARNING, msg)
                return None
        except:
            debug.printException(debug.LEVEL_WARNING)
        else:
            script = _scriptManager.getScript(app, event.source)

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
            orca_state.activeScript.drawOutline(-1, 0, 0, 0)
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
            debug.printException(debug.LEVEL_WARNING)
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
            return

        debug.println(debug.LEVEL_FINEST, "Script for event: %s" % script.name)
        setNewActiveScript, reason = self._isActivatableEvent(event, script)
        if setNewActiveScript:
            app = event.host_application or event.source.getApplication()
            _scriptManager.setActiveScript(script, reason)

        script.processObjectEvent(event)

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
