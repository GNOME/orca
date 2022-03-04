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
import gi
gi.require_version('Atspi', '2.0') 
from gi.repository import Atspi
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
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Initializing', True)
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Async Mode is %s' % asyncMode, True)
        self._asyncMode = asyncMode
        self._scriptListenerCounts = {}
        self.registry = pyatspi.Registry
        self._desktop = pyatspi.Registry.getDesktop(0)
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
        self._parentsOfDefunctDescendants = []

        orca_state.device = None
        self.newKeyHandlingActive = False
        self.legacyKeyHandlingActive = False
        self.forceLegacyKeyHandling = False

        debug.println(debug.LEVEL_INFO, 'Event manager initialized', True)

    def activate(self):
        """Called when this event manager is activated."""

        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Activating', True)
        self.setKeyHandling(False)

        self._active = True
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Activated', True)

    def activateNewKeyHandling(self):
        if not self.newKeyHandlingActive:
            try:
                orca_state.device = Atspi.Device.new()
            except:
                self.forceLegacyKeyHandling = True
                self.activateLegacyKeyHandling()
                return
            orca_state.device.event_count = 0
            orca_state.device.key_watcher = orca_state.device.add_key_watcher(self._processNewKeyboardEvent)
            self.newKeyHandlingActive = True

    def activateLegacyKeyHandling(self):
        if not self.legacyKeyHandlingActive:
            self.registerKeystrokeListener(self._processKeyboardEvent)
            self.legacyKeyHandlingActive = True

    def setKeyHandling(self, new):
        if new and not self.forceLegacyKeyHandling:
            self.deactivateLegacyKeyHandling()
            self.activateNewKeyHandling()
        else:
            self.deactivateNewKeyHandling()
            self.activateLegacyKeyHandling()

    def deactivate(self):
        """Called when this event manager is deactivated."""

        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Dectivating', True)
        self._active = False
        for eventType in self._scriptListenerCounts.keys():
            self.registry.deregisterEventListener(self._enqueue, eventType)
        self._scriptListenerCounts = {}
        self.deactivateLegacyKeyHandling()
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivated', True)

    def deactivateNewKeyHandling(self):
        if self.newKeyHandlingActive:
            orca_state.device = None
            self.newKeyHandlingActive = False;

    def deactivateLegacyKeyHandling(self):
        if self.legacyKeyHandlingActive:
            self.deregisterKeystrokeListener(self._processKeyboardEvent)
            self.legacyKeyHandlingActive = False;

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

        anydata = event.any_data
        if isinstance(anydata, str) and len(anydata) > 100:
            anydata = "%s (...)" % anydata[0:100]

        source = str(event.source)
        if len(source) > 100:
            source = "%s (...) ]" % source[0:100]

        debug.println(debug.LEVEL_INFO, '')
        msg = 'EVENT MANAGER: %s for %s in %s (%s, %s, %s)' % \
              (event.type, source, event.host_application,
               event.detail1,event.detail2, anydata)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not self._active:
            msg = 'EVENT MANAGER: Ignoring because event manager is not active'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if list(filter(event.type.startswith, self._ignoredEvents)):
            msg = 'EVENT MANAGER: Ignoring because event type is ignored'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if event.type.startswith('window'):
            msg = 'EVENT MANAGER: Not ignoring because event type is never ignored'
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if event.type.startswith('mouse:button'):
            msg = 'EVENT MANAGER: Not ignoring because event type is never ignored'
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self._inDeluge() and self._ignoreDuringDeluge(event):
            msg = 'EVENT MANAGER: Ignoring event type due to deluge'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        script = orca_state.activeScript
        if event.type.startswith('object:children-changed'):
            if not script:
                msg = 'EVENT MANAGER: Ignoring because there is no active script'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if script.app != event.host_application:
                msg = 'EVENT MANAGER: Ignoring because event is not from active app'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        if event.type.startswith('object:text-changed') \
           and self.EMBEDDED_OBJECT_CHARACTER in event.any_data \
           and not event.any_data.replace(self.EMBEDDED_OBJECT_CHARACTER, ""):
            # We should also get children-changed events telling us the same thing.
            # Getting a bunch of both can result in a flood that grinds us to a halt.
            msg = 'EVENT MANAGER: Ignoring because changed text is only embedded objects'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        try:
            # TODO - JD: For now we won't ask for the name. Simply asking for the name should
            # not break anything, and should be a reliable way to quickly identify defunct
            # objects. But apparently the mere act of asking for the name causes Orca to stop
            # presenting Eclipse (and possibly other) applications. This might be an AT-SPI2
            # issue, but until we know for certain....
            #name = event.source.name
            state = event.source.getState()
            role = event.source.getRole()
        except:
            msg = 'ERROR: Event is from potentially-defunct source'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if state.isEmpty():
            msg = 'EVENT MANAGER: Ignoring event due to empty state set'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if state.contains(pyatspi.STATE_DEFUNCT):
            msg = 'ERROR: Event is from defunct source'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if event.type.startswith('object:property-change:accessible-name'):
            if role in [pyatspi.ROLE_CANVAS,
                        pyatspi.ROLE_ICON,
                        pyatspi.ROLE_LABEL,      # gnome-shell spam
                        pyatspi.ROLE_LIST_ITEM,  # Web app spam
                        pyatspi.ROLE_LIST,       # Web app spam
                        pyatspi.ROLE_SECTION,    # Web app spam
                        pyatspi.ROLE_TABLE_ROW,  # Thunderbird spam
                        pyatspi.ROLE_TABLE_CELL, # Thunderbird spam
                        pyatspi.ROLE_MENU,
                        pyatspi.ROLE_MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:property-change:accessible-value'):
            if role == pyatspi.ROLE_SPLIT_PANE and not state.contains(pyatspi.STATE_FOCUSED):
                msg = 'EVENT MANAGER: Ignoring event type due to role and state'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:text-changed:insert') and event.detail2 > 1000 \
             and role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_STATIC]:
            msg = 'EVENT MANAGER: Ignoring because inserted text has more than 1000 chars'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True
        elif event.type.startswith('object:state-changed:sensitive'):
            if role in [pyatspi.ROLE_MENU_ITEM,
                        pyatspi.ROLE_MENU,
                        pyatspi.ROLE_FILLER,
                        pyatspi.ROLE_PANEL,
                        pyatspi.ROLE_CHECK_MENU_ITEM,
                        pyatspi.ROLE_RADIO_MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:state-changed:showing'):
            if role not in [pyatspi.ROLE_ALERT,
                            pyatspi.ROLE_ANIMATION,
                            pyatspi.ROLE_INFO_BAR,
                            pyatspi.ROLE_MENU,
                            pyatspi.ROLE_NOTIFICATION,
                            pyatspi.ROLE_DIALOG,
                            pyatspi.ROLE_PANEL,
                            pyatspi.ROLE_STATUS_BAR,
                            pyatspi.ROLE_TOOL_TIP]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:selection-changed'):
            if event.source in self._parentsOfDefunctDescendants:
                msg = 'EVENT MANAGER: Ignoring event from parent of defunct descendants'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            try:
                _name = event.source.name
            except:
                msg = 'EVENT MANAGER: Ignoring event from dead source'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        if event.type.startswith('object:children-changed') \
           or event.type.startswith('object:active-descendant-changed'):
            if role in [pyatspi.ROLE_MENU,
                        pyatspi.ROLE_LAYERED_PANE,
                        pyatspi.ROLE_MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if not event.any_data:
                msg = 'ERROR: Event any_data lacks child/descendant'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if event.type.endswith('remove'):
                if event.any_data == orca_state.locusOfFocus:
                    msg = 'EVENT MANAGER: Locus of focus is being destroyed'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return False

                try:
                    _name = orca_state.locusOfFocus.name
                except:
                    msg = 'EVENT MANAGER: Locus of focus is dead.'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return False
                else:
                    msg = 'EVENT MANAGER: Locus of focus: %s' % orca_state.locusOfFocus
                    debug.println(debug.LEVEL_INFO, msg, True)

            try:
                childState = event.any_data.getState()
                childRole = event.any_data.getRole()
                name = event.any_data.name
                defunct = False
            except:
                msg = 'ERROR: Event any_data contains potentially-defunct child/descendant'
                debug.println(debug.LEVEL_INFO, msg, True)
                defunct = True
            else:
                defunct = childState.contains(pyatspi.STATE_DEFUNCT)
                if defunct:
                    msg = 'ERROR: Event any_data contains defunct child/descendant'
                    debug.println(debug.LEVEL_INFO, msg, True)

            if defunct:
                if state.contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
                   and event.source not in self._parentsOfDefunctDescendants:
                    self._parentsOfDefunctDescendants.append(event.source)
                return True

            if event.source in self._parentsOfDefunctDescendants:
                self._parentsOfDefunctDescendants.remove(event.source)

            # This should be safe. We do not have a reason to present a newly-added,
            # but not focused image. We do not need to update live regions for images.
            # This is very likely a completely and utterly useless event for us. The
            # reason for ignoring it here rather than quickly processing it is the
            # potential for event floods like we're seeing from matrix.org.
            if childRole == pyatspi.ROLE_IMAGE:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        msg = 'EVENT MANAGER: Not ignoring due to lack of cause'
        debug.println(debug.LEVEL_INFO, msg, True)
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

    def _queuePrintln(self, e, isEnqueue=True, isPrune=None):
        """Convenience method to output queue-related debugging info."""

        if isinstance(e, input_event.KeyboardEvent):
            data = "'%s' (%d)" % (e.event_string, e.hw_code)
        elif isinstance(e, input_event.BrailleEvent):
            data = "'%s'" % repr(e.event)
        elif not debug.eventDebugFilter or debug.eventDebugFilter.match(e.type):
            anydata = e.any_data
            if isinstance(anydata, str) and len(anydata) > 100:
                anydata = "%s (...)" % anydata[0:100]
            data = "%s (%s,%s,%s) from %s" % \
                   (e.source, e.detail1, e.detail2, anydata, e.host_application)
        else:
            return

        if isPrune:
            string = "EVENT MANAGER: Pruning %s %s" % (e.type, data)
        elif isPrune is not None:
            string = "EVENT MANAGER: Not pruning %s %s" % (e.type, data)
        elif isEnqueue:
            string = "EVENT MANAGER: Queueing %s %s" % (e.type, data)
        else:
            string = "EVENT MANAGER: Dequeued %s %s" % (e.type, data)

        debug.println(debug.LEVEL_INFO, string, True)

    def _enqueue(self, e):
        """Handles the enqueueing of all events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        if debug.debugEventQueue:
            if self._enqueueCount:
                msg = "EVENT MANAGER: _enqueue entered before exiting (count = %d)" \
                    % self._enqueueCount
                debug.println(debug.LEVEL_ALL, msg, True)
            self._enqueueCount += 1

        inputEvents = (input_event.KeyboardEvent, input_event.BrailleEvent)
        isObjectEvent = not isinstance(e, inputEvents)

        try:
            ignore = isObjectEvent and self._ignore(e)
        except:
            msg = 'ERROR: Exception evaluating event: %s' % e
            debug.println(debug.LEVEL_INFO, msg, True)
            ignore = True
        if ignore:
            if debug.debugEventQueue:
                self._enqueueCount -= 1
            return

        self._queuePrintln(e)

        if self._inFlood() and self._prioritizeDuringFlood(e):
            msg = 'EVENT MANAGER: Pruning event queue due to flood.'
            debug.println(debug.LEVEL_INFO, msg, True)
            self._pruneEventsDuringFlood()

        asyncMode = self._asyncMode
        if isObjectEvent:
            app = e.source.getApplication()
            try:
                toolkitName = app.toolkitName
            except:
                toolkitName = None
            if toolkitName in self._synchronousToolkits \
               or isinstance(e, input_event.MouseButtonEvent):
                asyncMode = False
            elif e.type.startswith("object:children-changed"):
                try:
                    asyncMode = e.source.getRole() == pyatspi.ROLE_TABLE
                except:
                    asyncMode = True
            script = _scriptManager.getScript(app, e.source)
            script.eventCache[e.type] = (e, time.time())

        self._addToQueue(e, asyncMode)
        if not asyncMode:
            self._dequeue()

        if debug.debugEventQueue:
            self._enqueueCount -= 1

    def _isNoFocus(self):
        if orca_state.locusOfFocus or orca_state.activeWindow or orca_state.activeScript:
            return False

        msg = 'EVENT MANAGER: No focus'
        debug.println(debug.LEVEL_SEVERE, msg, True)
        return True

    def _onNoFocus(self):
        if not self._isNoFocus():
            return False

        defaultScript = _scriptManager.getDefaultScript()
        _scriptManager.setActiveScript(defaultScript, 'No focus')
        defaultScript.idleMessage()
        return False

    def _dequeue(self):
        """Handles all events destined for scripts. Called by the GTK
        idle thread."""

        rerun = True

        if debug.debugEventQueue:
            msg = 'EVENT MANAGER: Dequeue %d' % self._dequeueCount
            debug.println(debug.LEVEL_ALL, msg, True)
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

            self._gidleLock.acquire()
            if self._eventQueue.empty():
                GLib.timeout_add(2500, self._onNoFocus)
                self._gidleId = 0
                rerun = False # destroy and don't call again
            self._gidleLock.release()
        except queue.Empty:
            msg = 'EVENT MANAGER: Attempted dequeue, but the event queue is empty'
            debug.println(debug.LEVEL_SEVERE, msg, True)
            self._gidleId = 0
            rerun = False # destroy and don't call again
        except:
            debug.printException(debug.LEVEL_SEVERE)

        if debug.debugEventQueue:
            self._dequeueCount -= 1
            msg = 'EVENT MANAGER: Leaving _dequeue. Count: %d' % self._dequeueCount
            debug.println(debug.LEVEL_ALL, msg, True)

        return rerun

    def _registerListener(self, eventType):
        """Tells this module to listen for the given event type.

        Arguments:
        - eventType: the event type.
        """

        msg = 'EVENT MANAGER: registering listener for: %s' % eventType
        debug.println(debug.LEVEL_INFO, msg, True)

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

        msg = 'EVENT MANAGER: deregistering listener for: %s' % eventType
        debug.println(debug.LEVEL_INFO, msg, True)

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

        msg = 'EVENT MANAGER: registering listeners for: %s' % script
        debug.println(debug.LEVEL_INFO, msg, True)

        for eventType in script.listeners.keys():
            self._registerListener(eventType)

    def deregisterScriptListeners(self, script):
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        msg = 'EVENT MANAGER: deregistering listeners for: %s' % script
        debug.println(debug.LEVEL_INFO, msg, True)

        for eventType in script.listeners.keys():
            self._deregisterListener(eventType)

    def registerModuleListeners(self, listeners):
        """Register the listeners on behalf of the caller."""

        for eventType, function in listeners.items():
            self.registry.registerEventListener(function, eventType)

    def deregisterModuleListeners(self, listeners):
        """Deegister the listeners on behalf of the caller."""

        for eventType, function in listeners.items():
            self.registry.deregisterEventListener(function, eventType)

    def registerKeystrokeListener(self, function, mask=None, kind=None):
        """Register the keystroke listener on behalf of the caller."""

        msg = 'EVENT MANAGER: registering keystroke listener function: %s' % function
        debug.println(debug.LEVEL_INFO, msg, True)

        if mask is None:
            mask = list(range(256))

        if kind is None:
            kind = (pyatspi.KEY_PRESSED_EVENT, pyatspi.KEY_RELEASED_EVENT)

        self.registry.registerKeystrokeListener(function, mask=mask, kind=kind)

    def deregisterKeystrokeListener(self, function, mask=None, kind=None):
        """Deregister the keystroke listener on behalf of the caller."""

        msg = 'EVENT MANAGER: deregistering keystroke listener function: %s' % function
        debug.println(debug.LEVEL_INFO, msg, True)

        if mask is None:
            mask = list(range(256))

        if kind is None:
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

        if isinstance(event, input_event.BrailleEvent):
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
                debug.println(debug.LEVEL_WARNING, msg, True)
                return None
        except:
            msg = 'WARNING: Exception when getting script for event.'
            debug.println(debug.LEVEL_WARNING, msg, True)
        else:
            skipCheck = [
                "object:children-changed",
                "object:column-reordered",
                "object:row-reordered",
                "object:property-change",
                "object:selection-changed"
                "object:state-changed:checked",
                "object:state-changed:expanded",
                "object:state-changed:indeterminate",
                "object:state-changed:pressed",
                "object:state-changed:selected",
                "object:state-changed:sensitive",
                "object:state-changed:showing",
                "object:text-changed",
            ]
            check = not list(filter(lambda x: event.type.startswith(x), skipCheck))
            msg = 'EVENT MANAGER: Getting script for %s (check: %s)' % (app, check)
            debug.println(debug.LEVEL_INFO, msg, True)
            script = _scriptManager.getScript(app, event.source, sanityCheck=check)

        msg = 'EVENT MANAGER: Script is %s' % script
        debug.println(debug.LEVEL_INFO, msg, True)
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

        if script.forceScriptActivation(event):
            return True, "The script insists it should be activated for this event."

        eType = event.type

        if eType.startswith('window:activate'):
            windowActivation = True
        else:
            windowActivation = eType.startswith('object:state-changed:active') \
                and event.detail1 and role == pyatspi.ROLE_FRAME

        if windowActivation:
            if event.source != orca_state.activeWindow:
                return True, "Window activation"
            else:
                return False, "Window activation for already-active window"

        if eType.startswith('focus') \
           or (eType.startswith('object:state-changed:focused')
               and event.detail1):
            return True, "Event source claimed focus."

        if eType.startswith('object:state-changed:selected') and event.detail1 \
           and role == pyatspi.ROLE_MENU and state.contains(pyatspi.STATE_FOCUSED):
            return True, "Selection change in focused menu"

        # This condition appears with gnome-screensave-dialog.
        # See bug 530368.
        if eType.startswith('object:state-changed:showing') \
           and role == pyatspi.ROLE_PANEL \
           and state.contains(pyatspi.STATE_MODAL):
            return True, "Modal panel is showing."

        return False, "No reason found to activate a different script."

    def _ignoreDuringDeluge(self, event):
        """Returns true if this event should be ignored during a deluge."""

        ignore = ["object:text-changed:delete",
                  "object:text-changed:insert",
                  "object:text-changed:delete:system",
                  "object:text-changed:insert:system",
                  "object:text-attributes-changed",
                  "object:children-changed:add",
                  "object:children-changed:add:system",
                  "object:property-change:accessible-name",
                  "object:property-change:accessible-description",
                  "object:state-changed:showing",
                  "object:state-changed:sensitive"]

        if event.type not in ignore:
            return False

        return event.source != orca_state.locusOfFocus

    def _inDeluge(self):
        size = self._eventQueue.qsize()
        if size > 100:
            msg = 'EVENT MANAGER: DELUGE! Queue size is %i' % size
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _processDuringFlood(self, event):
        """Returns true if this event should be processed during a flood."""

        ignore = ["object:text-changed:delete",
                  "object:text-changed:insert",
                  "object:text-changed:delete:system",
                  "object:text-changed:insert:system",
                  "object:text-attributes-changed",
                  "object:children-changed:add",
                  "object:children-changed:add:system",
                  "object:property-change:accessible-name",
                  "object:property-change:accessible-description",
                  "object:state-changed:showing",
                  "object:state-changed:sensitive"]

        if event.type not in ignore:
            return True

        return event.source == orca_state.locusOfFocus

    def _prioritizeDuringFlood(self, event):
        """Returns true if this event should be prioritized during a flood."""

        if event.type.startswith("object:state-changed:focused"):
            return event.detail1

        if event.type.startswith("object:state-changed:selected"):
            return event.detail1

        if event.type.startswith("object:text-selection-changed"):
            return True

        if event.type.startswith("window:activate"):
            return True

        if event.type.startswith("window:deactivate"):
            return True

        if event.type.startswith("object:state-changed:active"):
            return event.source.getRole() in [pyatspi.ROLE_FRAME, pyatspi.ROLE_WINDOW]

        if event.type.startswith("document:load-complete"):
            return True

        if event.type.startswith("object:state-changed:busy"):
            return True

        return False

    def _pruneEventsDuringFlood(self):
        """Gets rid of events we don't care about during a flood."""

        oldSize = self._eventQueue.qsize()

        newQueue = queue.Queue(0)
        while not self._eventQueue.empty():
            try:
                event = self._eventQueue.get()
            except Empty:
                continue

            if self._processDuringFlood(event):
                newQueue.put(event)
                self._queuePrintln(event, isPrune=False)
            self._eventQueue.task_done()

        self._eventQueue = newQueue
        newSize = self._eventQueue.qsize()

        msg = 'EVENT MANAGER: %i events pruned. New size: %i' % ((oldSize - newSize), newSize)
        debug.println(debug.LEVEL_INFO, msg, True)

    def _inFlood(self):
        size = self._eventQueue.qsize()
        if size > 50:
            msg = 'EVENT MANAGER: FLOOD? Queue size is %i' % size
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _processObjectEvent(self, event):
        """Handles all object events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        debug.printObjectEvent(debug.LEVEL_INFO, event, timestamp=True)
        eType = event.type

        if eType.startswith("object:children-changed:remove"):
            try:
                if event.source == self._desktop:
                    _scriptManager.reclaimScripts()
                    return
            except:
                return

        if eType.startswith("window:") and not eType.endswith("create"):
            _scriptManager.reclaimScripts()

        if eType.startswith("object:state-changed:active"):
            try:
                role = event.source.getRole()
            except:
                pass
            else:
                if role == pyatspi.ROLE_FRAME:
                    _scriptManager.reclaimScripts()

        try:
            state = event.source.getState()
        except:
            isDefunct = True
            msg = 'ERROR: Exception getting state for event source'
            debug.println(debug.LEVEL_WARNING, msg, True)
        else:
            isDefunct = state.contains(pyatspi.STATE_DEFUNCT)

        if isDefunct:
            msg = 'EVENT MANAGER: Ignoring defunct object: %s' % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            if eType.startswith("window:deactivate") or eType.startswith("window:destroy") \
               and orca_state.activeWindow == event.source:
                msg = 'EVENT MANAGER: Clearing active window, script, and locus of focus'
                debug.println(debug.LEVEL_INFO, msg, True)
                orca_state.locusOfFocus = None
                orca_state.activeWindow = None
                orca_state.activeScript = None
            return

        if state and state.contains(pyatspi.STATE_ICONIFIED):
            msg = 'EVENT MANAGER: Ignoring iconified object: %s' % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if self._inFlood():
            if not self._processDuringFlood(event):
                msg = 'EVENT MANAGER: Not processing this event due to flood.'
                debug.println(debug.LEVEL_INFO, msg, True)
                return
            if self._prioritizeDuringFlood(event):
                msg = 'EVENT MANAGER: Pruning event queue due to flood.'
                debug.println(debug.LEVEL_INFO, msg, True)
                self._pruneEventsDuringFlood()

        if eType.startswith('object:selection-changed') \
           and event.source in self._parentsOfDefunctDescendants:
            msg = 'EVENT MANAGER: Ignoring event from parent of defunct descendants'
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if not debug.eventDebugFilter or debug.eventDebugFilter.match(eType) \
           and not eType.startswith("mouse:"):
            indent = " " * 32
            debug.printDetails(debug.LEVEL_INFO, indent, event.source)
            if isinstance(event.any_data, pyatspi.Accessible):
                debug.println(debug.LEVEL_INFO, '%sANY DATA:' % indent)
                debug.printDetails(debug.LEVEL_INFO, indent, event.any_data, includeApp=False)

        script = self._getScriptForEvent(event)
        if not script:
            msg = 'ERROR: Could not get script for %s' % event
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        setNewActiveScript, reason = self._isActivatableEvent(event, script)
        msg = 'EVENT MANAGER: Change active script: %s (%s)' % (setNewActiveScript, reason)
        debug.println(debug.LEVEL_INFO, msg, True)

        if setNewActiveScript:
            try:
                app = event.host_application or event.source.getApplication()
            except:
                msg = 'ERROR: Could not get application for %s' % event.source
                debug.println(debug.LEVEL_INFO, msg, True)
                return
            try:
                _scriptManager.setActiveScript(script, reason)
            except:
                msg = 'ERROR: Could not set active script for %s' % event.source
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        try:
            script.processObjectEvent(event)
        except:
            msg = 'ERROR: Could not process %s' % event.type
            debug.println(debug.LEVEL_INFO, msg, True)
            debug.printException(debug.LEVEL_INFO)

        msg = 'EVENT MANAGER: locusOfFocus: %s activeScript: %s' % \
              (orca_state.locusOfFocus, orca_state.activeScript)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not orca_state.activeScript:
            return

        attributes = orca_state.activeScript.getTransferableAttributes()
        for key, value in attributes.items():
            msg = 'EVENT MANAGER: %s: %s' % (key, value)
            debug.println(debug.LEVEL_INFO, msg, True)

    def _processNewKeyboardEvent(self, device, pressed, keycode, keysym, state, text):
        event = Atspi.DeviceEvent()
        if pressed:
            event.type = pyatspi.KEY_PRESSED_EVENT
        else:
            event.type = pyatspi.KEY_RELEASED_EVENT
        event.hw_code = keycode
        event.id = keysym
        event.modifiers = state
        event.event_string = text
        if event.event_string is None:
            event.event_string = ""
        event.timestamp = device.event_count
        device.event_count = device.event_count + 1

        if not pressed and text == "Num_Lock" and "KP_Insert" in settings.orcaModifierKeys and orca_state.activeSWcript is not None:
            orca_state.activeScript.refreshKeyGrabs()

        if pressed:
            orca_state.openingDialog = (text == "space" and (state & ~(1 << pyatspi.MODIFIER_NUMLOCK)))

        self._processKeyboardEvent(event)

    def _processKeyboardEvent(self, event):
        keyboardEvent = input_event.KeyboardEvent(event)
        if not keyboardEvent.is_duplicate:
            debug.println(debug.LEVEL_INFO, "\n%s" % keyboardEvent)

        rv = keyboardEvent.process()

        # Do any needed xmodmap crap. Hopefully this can die soon.
        from orca import orca
        orca.updateKeyMap(keyboardEvent)

        return rv

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
