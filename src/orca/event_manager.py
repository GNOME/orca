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
        debug.println(debug.LEVEL_INFO, 'Event manager initialized', True)

    def activate(self):
        """Called when this presentation manager is activated."""

        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Activating', True)
        self._registerListener("window:activate")
        self._registerListener("window:deactivate")
        self._registerListener("object:children-changed")
        self._registerListener("mouse:button")
        self.registerKeystrokeListener(self._processKeyboardEvent)
        self._active = True
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Activated', True)

    def deactivate(self):
        """Called when this event manager is deactivated."""

        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Dectivating', True)
        self._active = False
        for eventType in self._scriptListenerCounts.keys():
            self.registry.deregisterEventListener(self._enqueue, eventType)
        self._scriptListenerCounts = {}
        self.deregisterKeystrokeListener(self._processKeyboardEvent)
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivated', True)

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

        debug.println(debug.LEVEL_INFO, '')
        msg = 'EVENT MANAGER: %s for %s in %s (%s, %s, %s)' % \
              (event.type, event.source, event.host_application,
               event.detail1,event.detail2, event.any_data)
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

        script = orca_state.activeScript
        if event.type.startswith('object:children-changed:add'):
            if not script:
                msg = 'EVENT MANAGER: Ignoring because there is no active script'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if script.app != event.host_application:
                msg = 'EVENT MANAGER: Ignoring because event is not from active app'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        # This should ultimately be changed as there are valid reasons
        # to handle these events at the application level.
        if event.type.startswith('object:children-changed:remove') \
           and event.source != self._desktop:
            msg = 'EVENT MANAGER: Ignoring because event type is ignored'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if event.type.startswith('object:text-changed') and event.type.endswith('system'):
            # We should also get children-changed events telling us the same thing.
            # Getting a bunch of both can result in a flood that grinds us to a halt.
            if event.any_data == self.EMBEDDED_OBJECT_CHARACTER:
                msg = 'EVENT MANAGER: Ignoring because changed text is embedded object'
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
        if state.contains(pyatspi.STATE_DEFUNCT):
            msg = 'ERROR: Event is from defunct source'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if event.type.startswith('object:property-change:accessible-name'):
            if role in [pyatspi.ROLE_CANVAS,
                        pyatspi.ROLE_ICON,
                        pyatspi.ROLE_TABLE_ROW,  # Thunderbird spam
                        pyatspi.ROLE_TABLE_CELL, # Thunderbird spam
                        pyatspi.ROLE_MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:property-change:accessible-value'):
            if role == pyatspi.ROLE_SPLIT_PANE and not state.contains(pyatspi.STATE_FOCUSED):
                msg = 'EVENT MANAGER: Ignoring event type due to role and state'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:state-changed:sensitive'):
            if role in [pyatspi.ROLE_MENU_ITEM,
                        pyatspi.ROLE_FILLER,
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

        if event.type.startswith('object:children-changed:add') \
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
            try:
                childState = event.any_data.getState()
                childRole = event.any_data.getRole()
            except:
                msg = 'ERROR: Event any_data contains potentially-defunct child/descendant'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            if childState.contains(pyatspi.STATE_DEFUNCT):
                if state.contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
                   and event.source not in self._parentsOfDefunctDescendants:
                    self._parentsOfDefunctDescendants.append(event.source)

                msg = 'ERROR: Event any_data contains defunct child/descendant'
                debug.println(debug.LEVEL_INFO, msg, True)
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

        if isEnqueue:
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
            return True, "window:activate event"

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
            except (LookupError, RuntimeError):
                # If we got this error here, we'll get it again when we
                # attempt to get the state, catch it, and clean up.
                pass
            except:
                debug.printException(debug.LEVEL_WARNING)
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

        if eType.startswith('object:selection-changed') \
           and event.source in self._parentsOfDefunctDescendants:
            msg = 'EVENT MANAGER: Ignoring event from parent of defunct descendants'
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if not debug.eventDebugFilter or debug.eventDebugFilter.match(eType) \
           and not eType.startswith("mouse:"):
            debug.printDetails(debug.LEVEL_INFO, ' ' * 18, event.source)

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
