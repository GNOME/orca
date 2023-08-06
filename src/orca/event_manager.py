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

import gi
gi.require_version('Atspi', '2.0') 
from gi.repository import Atspi
from gi.repository import GLib
import pyatspi
import queue
import threading
import time

from . import debug
from . import input_event
from . import orca_state
from . import script_manager
from . import settings
from .ax_object import AXObject
from .ax_utilities import AXUtilities

_scriptManager = script_manager.getManager()

class EventManager:

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'

    def __init__(self, asyncMode=True):
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Initializing', True)
        debug.println(debug.LEVEL_INFO, f'EVENT MANAGER: Async Mode is {asyncMode}', True)
        self._asyncMode = asyncMode
        self._scriptListenerCounts = {}
        self._active = False
        self._enqueueCount = 0
        self._dequeueCount = 0
        self._eventQueue     = queue.Queue(0)
        self._gidleId        = 0
        self._gidleLock      = threading.Lock()
        self._gilSleepTime = 0.00001
        self._synchronousToolkits = ['VCL']
        self._eventsSuspended = False
        self._listener = Atspi.EventListener.new(self._enqueue)

        # Note: These must match what the scripts registered for, otherwise
        # Atspi might segfault.
        #
        # Events we don't want to suspend include:
        # object:text-changed:insert - marco
        self._suspendableEvents = ['object:children-changed:add',
                                   'object:children-changed:remove',
                                   'object:property-change:accessible-name',
                                   'object:state-changed:sensitive',
                                   'object:state-changed:showing',
                                   'object:text-changed:delete']
        self._eventsTriggeringSuspension = []
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
            except Exception:
                self.forceLegacyKeyHandling = True
                self.activateLegacyKeyHandling()
                return
            orca_state.device.key_watcher = orca_state.device.add_key_watcher(
                self._processNewKeyboardEvent)
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

        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivating', True)
        self._active = False
        self._eventQueue = queue.Queue(0)
        self._scriptListenerCounts = {}
        self.deactivateLegacyKeyHandling()
        debug.println(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivated', True)

    def deactivateNewKeyHandling(self):
        if self.newKeyHandlingActive:
            orca_state.device = None
            self.newKeyHandlingActive = False

    def deactivateLegacyKeyHandling(self):
        if self.legacyKeyHandlingActive:
            self.deregisterKeystrokeListener(self._processKeyboardEvent)
            self.legacyKeyHandlingActive = False

    def ignoreEventTypes(self, eventTypeList):
        for eventType in eventTypeList:
            if eventType not in self._ignoredEvents:
                self._ignoredEvents.append(eventType)

    def unignoreEventTypes(self, eventTypeList):
        for eventType in eventTypeList:
            if eventType in self._ignoredEvents:
                self._ignoredEvents.remove(eventType)

    def _isDuplicateEvent(self, event):
        """Returns True if this event is already in the event queue."""

        def isSame(x):
            return x.type == event.type \
                and x.source == event.source \
                and x.detail1 == event.detail1 \
                and x.detail2 == event.detail2 \
                and x.any_data == event.any_data

        for e in self._eventQueue.queue:
            if isSame(e):
                return True

        return False

    def _ignore(self, event):
        """Returns True if this event should be ignored."""

        anydata = event.any_data
        if isinstance(anydata, str) and len(anydata) > 100:
            anydata = f"{anydata[0:100]} (...)"

        source = str(event.source)
        if len(source) > 100:
            source = f"{source[0:100]} (...) ]"

        app = AXObject.get_application(event.source)

        debug.println(debug.LEVEL_INFO, '')
        if self._eventsSuspended:
            msg = f"EVENT MANAGER: Suspended events: {', '.join(self._suspendableEvents)}"
            debug.println(debug.LEVEL_INFO, msg, True)

        msg = 'EVENT MANAGER: %s for %s in %s (%s, %s, %s)' % \
              (event.type, source, app, event.detail1,event.detail2, anydata)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not self._active:
            msg = 'EVENT MANAGER: Ignoring because event manager is not active'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if list(filter(event.type.startswith, self._ignoredEvents)):
            msg = 'EVENT MANAGER: Ignoring because event type is ignored'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if AXObject.get_name(app) == 'gnome-shell':
            if event.type.startswith('object:children-changed:remove'):
                msg = 'EVENT MANAGER: Ignoring event based on type and app'
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

        if self._isDuplicateEvent(event):
            msg = 'EVENT MANAGER: Ignoring duplicate event'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        # Thunderbird spams us with these when a message list thread is expanded or collapsed.
        if event.type.endswith('system') \
           and AXObject.get_name(app).lower().startswith('thunderbird'):
            if AXUtilities.is_table_related(event.source) \
              or AXUtilities.is_tree_related(event.source) \
              or AXUtilities.is_section(event.source):
                msg = 'EVENT MANAGER: Ignoring system event based on role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        if self._inDeluge() and self._ignoreDuringDeluge(event):
            msg = 'EVENT MANAGER: Ignoring event type due to deluge'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        script = orca_state.activeScript
        if event.type.startswith('object:children-changed') \
           or event.type.startswith('object:state-changed:sensitive'):
            if not script:
                msg = 'EVENT MANAGER: Ignoring because there is no active script'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if script.app != app:
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

        # TODO - JD: For now we won't ask for the name. Simply asking for the name should
        # not break anything, and should be a reliable way to quickly identify defunct
        # objects. But apparently the mere act of asking for the name causes Orca to stop
        # presenting Eclipse (and possibly other) applications. This might be an AT-SPI2
        # issue, but until we know for certain....
        #name = Atspi.Accessible.get_name(event.source)

        if AXUtilities.has_no_state(event.source):
            msg = 'EVENT MANAGER: Ignoring event due to empty state set'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_defunct(event.source):
            msg = 'EVENT MANAGER: Ignoreing event from defunct source'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        role = AXObject.get_role(event.source)
        if event.type.startswith('object:property-change:accessible-name'):
            if role in [Atspi.Role.CANVAS,
                        Atspi.Role.ICON,
                        Atspi.Role.LABEL,      # gnome-shell spam
                        Atspi.Role.LIST_ITEM,  # Web app spam
                        Atspi.Role.LIST,       # Web app spam
                        Atspi.Role.SECTION,    # Web app spam
                        Atspi.Role.TABLE_ROW,  # Thunderbird spam
                        Atspi.Role.TABLE_CELL, # Thunderbird spam
                        Atspi.Role.TREE_ITEM,  # Thunderbird spam
                        Atspi.Role.IMAGE,      # Thunderbird spam
                        Atspi.Role.MENU,
                        Atspi.Role.MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:property-change:accessible-value'):
            if role == Atspi.Role.SPLIT_PANE and not AXUtilities.is_focused(event.source):
                msg = 'EVENT MANAGER: Ignoring event type due to role and state'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:text-changed:insert') and event.detail2 > 1000 \
             and role in [Atspi.Role.TEXT, Atspi.Role.STATIC]:
            msg = 'EVENT MANAGER: Ignoring because inserted text has more than 1000 chars'
            debug.println(debug.LEVEL_INFO, msg, True)
            return True
        elif event.type.startswith('object:state-changed:sensitive'):
            if role in [Atspi.Role.MENU_ITEM,
                        Atspi.Role.MENU,
                        Atspi.Role.FILLER,
                        Atspi.Role.PANEL,
                        Atspi.Role.CHECK_MENU_ITEM,
                        Atspi.Role.RADIO_MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:state-changed:selected'):
            if not event.detail1 and role in [Atspi.Role.PUSH_BUTTON]:
                msg = 'EVENT MANAGER: Ignoring event type due to role and detail1'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        elif event.type.startswith('object:state-changed:showing'):
            if role not in [Atspi.Role.ALERT,
                            Atspi.Role.ANIMATION,
                            Atspi.Role.INFO_BAR,
                            Atspi.Role.MENU,
                            Atspi.Role.NOTIFICATION,
                            Atspi.Role.DIALOG,
                            Atspi.Role.PANEL,
                            Atspi.Role.STATUS_BAR,
                            Atspi.Role.TOOL_TIP]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if role == Atspi.Role.PANEL:
                if not event.detail1:
                    msg = 'EVENT MANAGER: Ignoring event type due to role and detail1'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return True
                if AXObject.is_dead(event.source):
                    msg = 'EVENT MANAGER: Ignoring event from dead source'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return True
                if not AXObject.get_name(event.source):
                    msg = 'EVENT MANAGER: Ignoring event type due to role and lack of name'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return True

        elif event.type.startswith('object:text-caret-moved'):
            if role in [Atspi.Role.LABEL] and not AXUtilities.is_focused(event.source):
                msg = 'EVENT MANAGER: Ignoring event type due to role and state'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        elif event.type.startswith('object:selection-changed'):
            if event.source in self._parentsOfDefunctDescendants:
                msg = 'EVENT MANAGER: Ignoring event from parent of defunct descendants'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            if AXObject.is_dead(event.source):
                msg = 'EVENT MANAGER: Ignoring event from dead source'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        if event.type.startswith('object:children-changed') \
           or event.type.startswith('object:active-descendant-changed'):
            if role in [Atspi.Role.MENU,
                        Atspi.Role.LAYERED_PANE,
                        Atspi.Role.MENU_ITEM]:
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if event.any_data is None:
                msg = 'EVENT_MANAGER: Ignoring due to lack of event.any_data'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if event.type.endswith('remove'):
                if event.any_data == orca_state.locusOfFocus:
                    msg = 'EVENT MANAGER: Locus of focus is being destroyed'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return False

                if AXObject.is_dead(orca_state.locusOfFocus):
                    msg = 'EVENT MANAGER: Locus of focus is dead.'
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return False

                msg = f'EVENT MANAGER: Locus of focus: {orca_state.locusOfFocus}'
                debug.println(debug.LEVEL_INFO, msg, True)

            defunct = AXObject.is_dead(event.any_data) or AXUtilities.is_defunct(event.any_data)
            if defunct:
                msg = 'EVENT MANAGER: Ignoring event for potentially-defunct child/descendant'
                debug.println(debug.LEVEL_INFO, msg, True)
                if AXUtilities.manages_descendants(event.source) \
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
            if AXUtilities.is_image(event.any_data):
                msg = 'EVENT MANAGER: Ignoring event type due to role'
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            # In normal apps we would have caught this from the parent role.
            # But gnome-shell has panel parents adding/removing menu items.
            if event.type.startswith('object:children-changed'):
                if AXUtilities.is_menu_item(event.any_data):
                    msg = 'EVENT MANAGER: Ignoring event type due to child role'
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
            data = f"'{repr(e.event)}'"
        elif not debug.eventDebugFilter or debug.eventDebugFilter.match(e.type):
            app = AXObject.get_application(e.source)
            anydata = e.any_data
            if isinstance(anydata, str) and len(anydata) > 100:
                anydata = f"{anydata[0:100]} (...)"
            data = f"{e.source} ({e.detail1},{e.detail2},{anydata}) from {app}"
        else:
            return

        if isPrune:
            string = f"EVENT MANAGER: Pruning {e.type} {data}"
        elif isPrune is not None:
            string = f"EVENT MANAGER: Not pruning {e.type} {data}"
        elif isEnqueue:
            string = f"EVENT MANAGER: Queueing {e.type} {data}"
        else:
            string = f"EVENT MANAGER: Dequeued {e.type} {data}"

        debug.println(debug.LEVEL_INFO, string, True)

    def _suspendEvents(self, triggeringEvent):
        self._eventsTriggeringSuspension.append(triggeringEvent)

        if self._eventsSuspended:
            msg = "EVENT MANAGER: Events already suspended."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        msg = "EVENT MANAGER: Suspending events."
        debug.println(debug.LEVEL_INFO, msg, True)

        for event in self._suspendableEvents:
            self.deregisterListener(event)

        self._eventsSuspended = True

    def _unsuspendEvents(self, triggeringEvent):
        if triggeringEvent in self._eventsTriggeringSuspension:
            self._eventsTriggeringSuspension.remove(triggeringEvent)

        if not self._eventsSuspended:
            msg = "EVENT MANAGER: Events already unsuspended."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if self._eventsTriggeringSuspension:
            msg = "EVENT MANAGER: Events are suspended for another event."
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        msg = "EVENT MANAGER: Unsuspending events."
        debug.println(debug.LEVEL_INFO, msg, True)

        for event in self._suspendableEvents:
            self.registerListener(event)

        self._eventsSuspended = False

    def _shouldSuspendEventsFor(self, event):
        if AXUtilities.is_frame(event.source) or AXUtilities.is_window(event.source):
            if event.type.startswith("window"):
                msg = "EVENT MANAGER: Should suspend events for window event."
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
            if event.type.endswith("active"):
                msg = "EVENT MANAGER: Should suspend events for active event on window."
                debug.println(debug.LEVEL_INFO, msg, True)
                return True
        if AXUtilities.is_document(event.source):
            if event.type.endswith("busy"):
                msg = "EVENT MANAGER: Should suspend events for busy event on document."
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        return False

    def _didSuspendEventsFor(self, event):
        return event in self._eventsTriggeringSuspension

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
        except Exception:
            msg = f'ERROR: Exception evaluating event: {e}'
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

        if isObjectEvent and self._shouldSuspendEventsFor(e):
            self._suspendEvents(e)

        asyncMode = self._asyncMode
        if isObjectEvent:
            if isinstance(e, input_event.MouseButtonEvent):
                asyncMode = True
            elif AXObject.get_application_toolkit_name(e.source) in self._synchronousToolkits:
                asyncMode = False
            elif e.type.startswith("object:children-changed"):
                asyncMode = AXUtilities.is_table(e.source)
            elif AXUtilities.is_notification(e.source):
                # To decrease the likelihood that the popup will be destroyed before we
                # have its contents.
                asyncMode = False
            script = _scriptManager.getScript(AXObject.get_application(e.source), e.source)
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
                                  "\nvvvvv PROCESS OBJECT EVENT %s (queue size: %i) vvvvv" \
                                  % (event.type, self._eventQueue.qsize()))
                self._processObjectEvent(event)
                if self._didSuspendEventsFor(event):
                    self._unsuspendEvents(event)

                if debugging:
                    debug.println(debug.eventDebugLevel,
                                  "TOTAL PROCESSING TIME: %.4f" \
                                  % (time.time() - startTime))
                    debug.println(debug.eventDebugLevel,
                                  f"^^^^^ PROCESS OBJECT EVENT {event.type} ^^^^^\n")
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
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)

        if debug.debugEventQueue:
            self._dequeueCount -= 1
            msg = 'EVENT MANAGER: Leaving _dequeue. Count: %d' % self._dequeueCount
            debug.println(debug.LEVEL_ALL, msg, True)

        return rerun

    def registerListener(self, eventType):
        """Tells this module to listen for the given event type.

        Arguments:
        - eventType: the event type.
        """

        msg = f'EVENT MANAGER: registering listener for: {eventType}'
        debug.println(debug.LEVEL_INFO, msg, True)

        if eventType in self._scriptListenerCounts:
            self._scriptListenerCounts[eventType] += 1
        else:
            self._listener.register(eventType)
            self._scriptListenerCounts[eventType] = 1

    def deregisterListener(self, eventType):
        """Tells this module to stop listening for the given event type.

        Arguments:
        - eventType: the event type.
        """

        msg = f'EVENT MANAGER: deregistering listener for: {eventType}'
        debug.println(debug.LEVEL_INFO, msg, True)

        if eventType not in self._scriptListenerCounts:
            return

        self._scriptListenerCounts[eventType] -= 1
        if self._scriptListenerCounts[eventType] == 0:
            self._listener.deregister(eventType)
            del self._scriptListenerCounts[eventType]

    def registerScriptListeners(self, script):
        """Tells the event manager to start listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        msg = f'EVENT MANAGER: registering listeners for: {script}'
        debug.println(debug.LEVEL_INFO, msg, True)

        for eventType in script.listeners.keys():
            self.registerListener(eventType)

    def deregisterScriptListeners(self, script):
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        msg = f'EVENT MANAGER: deregistering listeners for: {script}'
        debug.println(debug.LEVEL_INFO, msg, True)

        for eventType in script.listeners.keys():
            self.deregisterListener(eventType)

    def registerKeystrokeListener(self, function, mask=None, kind=None):
        """Register the keystroke listener on behalf of the caller."""

        msg = f'EVENT MANAGER: registering keystroke listener function: {function}'
        debug.println(debug.LEVEL_INFO, msg, True)

        if mask is None:
            mask = list(range(256))

        if kind is None:
            kind = (Atspi.EventType.KEY_PRESSED_EVENT, Atspi.EventType.KEY_RELEASED_EVENT)

        pyatspi.Registry.registerKeystrokeListener(function, mask=mask, kind=kind)

    def deregisterKeystrokeListener(self, function, mask=None, kind=None):
        """Deregister the keystroke listener on behalf of the caller."""

        msg = f'EVENT MANAGER: deregistering keystroke listener function: {function}'
        debug.println(debug.LEVEL_INFO, msg, True)

        if mask is None:
            mask = list(range(256))

        if kind is None:
            kind = (Atspi.EventType.KEY_PRESSED_EVENT, Atspi.EventType.KEY_RELEASED_EVENT)

        pyatspi.Registry.deregisterKeystrokeListener(function, mask=mask, kind=kind)

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
            data = f"'{repr(event.event)}'"
        else:
            return

        eType = str(event.type).upper()
        startTime = time.time()
        debug.println(debug.eventDebugLevel,
                      f"\nvvvvv PROCESS {eType} {data} vvvvv")
        try:
            function(event)
        except Exception:
            debug.printException(debug.LEVEL_WARNING)
            debug.printStack(debug.LEVEL_WARNING)
        debug.println(debug.eventDebugLevel,
                      f"TOTAL PROCESSING TIME: {time.time() - startTime:.4f}")
        debug.println(debug.eventDebugLevel,
                      f"^^^^^ PROCESS {eType} {data} ^^^^^\n")

    @staticmethod
    def _getScriptForEvent(event):
        """Returns the script associated with event."""

        if event.type.startswith("mouse:"):
            return _scriptManager.getScriptForMouseButtonEvent(event)

        script = None
        app = AXObject.get_application(event.source)
        if AXUtilities.is_defunct(app):
            msg = f'WARNING: {app} is defunct. Cannot get script for event.'
            debug.println(debug.LEVEL_WARNING, msg, True)
            return None

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
        msg = f'EVENT MANAGER: Getting script for {app} (check: {check})'
        debug.println(debug.LEVEL_INFO, msg, True)
        script = _scriptManager.getScript(app, event.source, sanityCheck=check)

        msg = f'EVENT MANAGER: Script is {script}'
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
                and event.detail1 and AXUtilities.is_frame(event.source)

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
           and AXUtilities.is_menu(event.source) and AXUtilities.is_focusable(event.source):
            return True, "Selection change in focused menu"

        # This condition appears with gnome-screensaver-dialog.
        # See bug 530368.
        if eType.startswith('object:state-changed:showing') \
           and AXUtilities.is_panel(event.source) and AXUtilities.is_modal(event.source):
            return True, "Modal panel is showing."

        return False, "No reason found to activate a different script."

    def _eventSourceIsDead(self, event):
        if AXObject.is_dead(event.source):
            msg = f"EVENT MANAGER: source of {event.type} is dead"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _ignoreDuringDeluge(self, event):
        """Returns true if this event should be ignored during a deluge."""

        if self._eventSourceIsDead(event):
            return True

        ignore = ["object:text-changed:delete",
                  "object:text-changed:insert",
                  "object:text-changed:delete:system",
                  "object:text-changed:insert:system",
                  "object:text-attributes-changed",
                  "object:text-caret-moved",
                  "object:children-changed:add",
                  "object:children-changed:add:system",
                  "object:children-changed:remove",
                  "object:children-changed:remove:system",
                  "object:property-change:accessible-name",
                  "object:property-change:accessible-description",
                  "object:selection-changed",
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

        if self._eventSourceIsDead(event):
            return False

        ignore = ["object:text-changed:delete",
                  "object:text-changed:insert",
                  "object:text-changed:delete:system",
                  "object:text-changed:insert:system",
                  "object:text-attributes-changed",
                  "object:text-caret-moved",
                  "object:children-changed:add",
                  "object:children-changed:add:system",
                  "object:children-changed:remove",
                  "object:children-changed:remove:system",
                  "object:property-change:accessible-name",
                  "object:property-change:accessible-description",
                  "object:selection-changed",
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
            return AXUtilities.is_frame(event.source) or AXUtilities.is_window(event.source)

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
            except Exception:
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

        if eType.startswith("object:children-changed:remove") \
           and event.source == AXUtilities.get_desktop():
            _scriptManager.reclaimScripts()
            return

        if eType.startswith("window:") and not eType.endswith("create"):
            _scriptManager.reclaimScripts()
        elif eType.startswith("object:state-changed:active") \
           and AXUtilities.is_frame(event.source):
            _scriptManager.reclaimScripts()

        if AXObject.is_dead(event.source) or AXUtilities.is_defunct(event.source):
            msg = f'EVENT MANAGER: Ignoring defunct object: {event.source}'
            debug.println(debug.LEVEL_INFO, msg, True)
            if eType.startswith("window:deactivate") or eType.startswith("window:destroy") \
               and orca_state.activeWindow == event.source:
                msg = 'EVENT MANAGER: Clearing active window, script, and locus of focus'
                debug.println(debug.LEVEL_INFO, msg, True)
                orca_state.locusOfFocus = None
                orca_state.activeWindow = None
                _scriptManager.setActiveScript(None, "Active window is dead or defunct")
            return

        if AXUtilities.is_iconified(event.source):
            msg = f'EVENT MANAGER: Ignoring iconified object: {event.source}'
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
            if isinstance(event.any_data, Atspi.Accessible):
                debug.println(debug.LEVEL_INFO, f'{indent}ANY DATA:')
                debug.printDetails(debug.LEVEL_INFO, indent, event.any_data, includeApp=False)

        script = self._getScriptForEvent(event)
        if not script:
            msg = f'ERROR: Could not get script for {event}'
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        setNewActiveScript, reason = self._isActivatableEvent(event, script)
        msg = f'EVENT MANAGER: Change active script: {setNewActiveScript} ({reason})'
        debug.println(debug.LEVEL_INFO, msg, True)

        if setNewActiveScript:
            try:
                _scriptManager.setActiveScript(script, reason)
            except Exception:
                msg = f'ERROR: Could not set active script for {event.source}'
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        try:
            script.processObjectEvent(event)
        except Exception:
            msg = f'ERROR: Could not process {event.type}'
            debug.println(debug.LEVEL_INFO, msg, True)
            debug.printException(debug.LEVEL_INFO)

        msg = 'EVENT MANAGER: locusOfFocus: %s activeScript: %s' % \
              (orca_state.locusOfFocus, orca_state.activeScript)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not orca_state.activeScript:
            return

        attributes = orca_state.activeScript.getTransferableAttributes()
        for key, value in attributes.items():
            msg = f'EVENT MANAGER: {key}: {value}'
            debug.println(debug.LEVEL_INFO, msg, True)

    def _processNewKeyboardEvent(self, device, pressed, keycode, keysym, state, text):
        event = Atspi.DeviceEvent()
        if pressed:
            event.type = Atspi.EventType.KEY_PRESSED_EVENT
        else:
            event.type = Atspi.EventType.KEY_RELEASED_EVENT
        event.hw_code = keycode
        event.id = keysym
        event.modifiers = state
        event.event_string = text
        if event.event_string is None:
            event.event_string = ""
        event.timestamp = time.time()

        if not pressed and text == "Num_Lock" and "KP_Insert" in settings.orcaModifierKeys \
            and orca_state.activeScript is not None:
            orca_state.activeScript.refreshKeyGrabs()

        if pressed:
            orca_state.openingDialog = (text == "space" \
                                         and (state & ~(1 << Atspi.ModifierType.NUMLOCK)))

        self._processKeyboardEvent(event)

    def _processKeyboardEvent(self, event):
        keyboardEvent = input_event.KeyboardEvent(event)
        if not keyboardEvent.is_duplicate:
            debug.println(debug.LEVEL_INFO, f"\n{keyboardEvent}")

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
