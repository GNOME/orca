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
import queue
import threading
import time

from . import debug
from . import focus_manager
from . import input_event
from . import orca_state
from . import script_manager
from . import settings
from .ax_object import AXObject
from .ax_utilities import AXUtilities


class EventManager:

    def __init__(self):
        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Initializing', True)
        self._scriptListenerCounts = {}
        self._active = False
        self._paused = False
        self._eventQueue     = queue.Queue(0)
        self._gidleId        = 0
        self._gidleLock      = threading.Lock()
        self._listener = Atspi.EventListener.new(self._enqueue_object_event)
        orca_state.device = None
        debug.printMessage(debug.LEVEL_INFO, 'Event manager initialized', True)

    def activate(self):
        """Called when this event manager is activated."""

        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Activating', True)
        orca_state.device = Atspi.Device.new()
        orca_state.device.event_count = 0
        orca_state.device.key_watcher = \
            orca_state.device.add_key_watcher(self._processKeyboardEvent)

        self._active = True
        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Activated', True)

    def deactivate(self):
        """Called when this event manager is deactivated."""

        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivating', True)
        self._active = False
        self._eventQueue = queue.Queue(0)
        self._scriptListenerCounts = {}
        orca_state.device = None
        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivated', True)

    def pauseQueuing(self, pause=True, clearQueue=False, reason=""):
        """Pauses/unpauses event queuing."""

        msg = f"EVENT MANAGER: Pause queueing: {pause}. Clear queue: {clearQueue}. {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._paused = pause
        if clearQueue:
            self._eventQueue = queue.Queue(0)

    def _isObsoletedBy(self, event):
        """Returns the event which renders this one no longer worthy of being processed."""

        def isSame(x):
            return x.type == event.type \
                and x.source == event.source \
                and x.detail1 == event.detail1 \
                and x.detail2 == event.detail2 \
                and x.any_data == event.any_data

        def obsoletesIfSameTypeAndObject(x):
            skippable = {
                "document:page-changed",
                "object:active-descendant-changed",
                "object:children-changed",
                "object:property-change",
                "object:state-changed",
                "object:selection-changed",
                "object:text-caret-moved",
                "object:text-selection-changed",
                "window",
            }
            if not any(x.type.startswith(etype) for etype in skippable):
                return False
            return x.source == event.source and x.type == event.type

        def obsoletesIfSameTypeInSibling(x):
            if x.type != event.type or x.detail1 != event.detail1 or x.detail2 != event.detail2 \
               or x.any_data != event.any_data:
                return False

            skippable = {
                "focus",
                "object:state-changed:focused",
            }
            if not any(x.type.startswith(etype) for etype in skippable):
                return False
            return AXObject.get_parent(x.source) == AXObject.get_parent(event.source)

        def obsoletesWindowEvent(x):
            skippable = {
                "window:activate",
                "window:deactivate",
            }
            if not any(x.type.startswith(etype) for etype in skippable):
                return False
            if not any(event.type.startswith(etype) for etype in skippable):
                return False
            if x.source == event.source:
                return True
            return False

        self._eventQueue.mutex.acquire()
        try:
            events = list(reversed(self._eventQueue.queue))
        except Exception as error:
            msg = f"EVENT MANAGER: Exception in _isObsoletedBy: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            events = []
        finally:
            self._eventQueue.mutex.release()

        for e in events:
            if e == event:
                return None
            if isSame(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent duplicate"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletesIfSameTypeAndObject(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent event of same type for same object"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletesIfSameTypeInSibling(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent event of same type from sibling"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletesWindowEvent(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent window (de)activation event"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e

        tokens = ["EVENT MANAGER:", event, "is not obsoleted"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return None

    def _ignore(self, event):
        """Returns True if this event should be ignored."""

        debug.printMessage(debug.LEVEL_INFO, '')
        tokens = ["EVENT MANAGER:", event]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not self._active or self._paused:
            msg = 'EVENT MANAGER: Ignoring because manager is not active or queueing is paused'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        event_type = event.type
        if event_type.startswith('window') or event_type.startswith('mouse:button'):
            return False

        if self._inDeluge() and self._ignoreDuringDeluge(event):
            msg = 'EVENT MANAGER: Ignoring event type due to deluge'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        # Keep these checks early in the process so we can assume them throughout
        # the rest of our checks.
        focus = focus_manager.getManager().get_locus_of_focus()
        if focus == event.source or AXUtilities.is_focused(event.source):
            return False
        if focus == event.any_data:
            return False

        if event_type.startswith("object:children-changed"):
            child = event.any_data
            if child is None:
                msg = 'EVENT_MANAGER: Ignoring due to lack of event.any_data'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if "remove" in event_type and AXObject.is_dead(focus):
                return False
            if AXObject.is_dead(child):
                msg = 'EVENT_MANAGER: Ignoring due to dead event.any_data'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if AXUtilities.is_menu_related(child) or AXUtilities.is_image(child):
                msg = 'EVENT_MANAGER: Ignoring due to role of event.any_data'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            app = AXObject.get_application(event.source)
            if "remove" in event_type and AXObject.get_name(app).lower() == "gnome-shell":
                msg = "EVENT MANAGER: Ignoring event based on type and app"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            script = script_manager.getManager().getActiveScript()
            if script is None:
                msg = "EVENT MANAGER: Ignoring because there is no active script"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if script.app != AXObject.get_application(event.source):
                msg = "EVENT MANAGER: Ignoring because event is not from active app"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

        if event_type.startswith("object:property-change"):
            role = AXObject.get_role(event.source)
            if "name" in event_type:
                if role in [Atspi.Role.CANVAS,
                            Atspi.Role.CHECK_BOX,    # TeamTalk5 spam
                            Atspi.Role.ICON,
                            Atspi.Role.IMAGE,        # Thunderbird spam
                            Atspi.Role.LIST,         # Web app spam
                            Atspi.Role.LIST_ITEM,    # Web app spam
                            Atspi.Role.MENU,
                            Atspi.Role.MENU_ITEM,
                            Atspi.Role.PANEL,        # TeamTalk5 spam
                            Atspi.Role.RADIO_BUTTON, # TeamTalk5 spam
                            Atspi.Role.SECTION,      # Web app spam
                            Atspi.Role.TABLE_ROW,    # Thunderbird spam
                            Atspi.Role.TABLE_CELL,   # Thunderbird spam
                            Atspi.Role.TREE_ITEM]:   # Thunderbird spam
                    msg = "EVENT MANAGER: Ignoring event type due to role of unfocused source"
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
                return False
            if "value" in event_type:
                if role in [Atspi.Role.SPLIT_PANE, Atspi.Role.SCROLL_BAR]:
                    msg = "EVENT MANAGER: Ignoring event type due to role of unfocused source"
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
                return False

        if event_type.startswith('object:selection-changed'):
            if AXObject.is_dead(event.source):
                msg = "EVENT MANAGER: Ignoring event from dead source"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            return False

        if event_type.startswith("object:state-changed"):
            role = AXObject.get_role(event.source)
            if event_type.endswith("system"):
                # Thunderbird spams us with these when a message list thread is expanded/collapsed.
                if role in [Atspi.Role.TABLE,
                            Atspi.Role.TABLE_CELL,
                            Atspi.Role.TABLE_ROW,
                            Atspi.Role.TREE,
                            Atspi.Role.TREE_ITEM,
                            Atspi.Role.TREE_TABLE]:
                    msg = 'EVENT MANAGER: Ignoring system event based on role'
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
            if "checked" in event_type:
                # Gtk 3 apps. See https://gitlab.gnome.org/GNOME/gtk/-/issues/6449
                if not AXUtilities.is_showing(event.source):
                    msg = "EVENT MANAGER: Ignoring event type of unfocused, non-showing source"
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
                return False
            if "selected" in event_type:
                if not event.detail1 and role in [Atspi.Role.PUSH_BUTTON]:
                    msg = "EVENT MANAGER: Ignoring event type due to role of source and detail1"
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
                return False
            if "sensitive" in event_type:
                # The Gedit and Thunderbird scripts pay attention to this event for spellcheck.
                if role not in [Atspi.Role.TEXT, Atspi.Role.ENTRY]:
                    msg = "EVENT MANAGER: Ignoring event type due to role of unfocused source"
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
                return False
            if "showing" in event_type:
                if role not in [Atspi.Role.ALERT,
                                Atspi.Role.ANIMATION,
                                Atspi.Role.DIALOG,
                                Atspi.Role.INFO_BAR,
                                Atspi.Role.MENU,
                                Atspi.Role.NOTIFICATION,
                                Atspi.Role.STATUS_BAR,
                                Atspi.Role.TOOL_TIP]:
                    msg = "EVENT MANAGER: Ignoring event type due to role"
                    debug.printMessage(debug.LEVEL_INFO, msg, True)
                    return True
                return False

        if event_type.startswith('object:text-caret-moved'):
            role = AXObject.get_role(event.source)
            if role in [Atspi.Role.LABEL]:
                msg = "EVENT MANAGER: Ignoring event type due to role of unfocused source"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            return False

        if event_type.startswith('object:text-changed'):
            if "\ufffc" in event.any_data and not event.any_data.replace("\ufffc", ""):
                msg = "EVENT MANAGER: Ignoring because changed text is only embedded objects"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if "insert" in event_type and event.detail2 > 1000:
                msg = "EVENT MANAGER: Ignoring because inserted text has more than 1000 chars"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if event_type.endswith("system") and AXUtilities.is_selectable(focus):
                # Thunderbird spams us with text changes every time the selected item changes.
                msg = "EVENT MANAGER: Ignoring because event is suspected spam"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            return False

        return False

    def _queuePrintln(self, e, isEnqueue=True, isPrune=None):
        """Convenience method to output queue-related debugging info."""

        if debug.LEVEL_INFO < debug.debugLevel:
            return

        tokens = []
        if isinstance(e, input_event.KeyboardEvent):
            tokens.extend([e.event_string, e.hw_code])
        elif isinstance(e, input_event.BrailleEvent):
            tokens.append(e.event)
        elif not debug.eventDebugFilter or debug.eventDebugFilter.match(e.type):
            tokens.append(e)
        else:
            return

        if isPrune:
            tokens[0:0] = ["EVENT MANAGER: Pruning"]
        elif isPrune is not None:
            tokens[0:0] = ["EVENT MANAGER: Not pruning"]
        elif isEnqueue:
            tokens[0:0] = ["EVENT MANAGER: Queueing"]
        else:
            tokens[0:0] = ["EVENT MANAGER: Dequeued"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    def _enqueue_object_event(self, e):
        """Callback for Atspi object events."""

        if self._ignore(e):
            return

        self._queuePrintln(e)

        if self._inFlood() and self._prioritizeDuringFlood(e):
            msg = 'EVENT MANAGER: Pruning event queue due to flood.'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._pruneEventsDuringFlood()

        app = AXObject.get_application(e.source)
        tokens = ["EVENT MANAGER: App for event source is", app]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.getManager().getScript(app, e.source)
        script.eventCache[e.type] = (e, time.time())

        self._gidleLock.acquire()
        self._eventQueue.put(e)
        if not self._gidleId:
            self._gidleId = GLib.idle_add(self._dequeue_object_event)
        self._gidleLock.release()

    def _onNoFocus(self):
        if focus_manager.getManager().focus_and_window_are_unknown():
            return False

        if script_manager.getManager().getActiveScript() is None:
            defaultScript = script_manager.getManager().getDefaultScript()
            script_manager.getManager().setActiveScript(defaultScript, 'No focus')
            defaultScript.idleMessage()

        return False

    def _dequeue_object_event(self):
        """Handles all object events destined for scripts."""

        rerun = True
        try:
            event = self._eventQueue.get_nowait()
            self._queuePrintln(event, isEnqueue=False)
            debug.objEvent = event
            debugging = not debug.eventDebugFilter \
                        or debug.eventDebugFilter.match(event.type)
            if debugging:
                startTime = time.time()
                msg = (
                    f"\nvvvvv PROCESS OBJECT EVENT {event.type} "
                    f"(queue size: {self._eventQueue.qsize()}) vvvvv"
                )
                debug.printMessage(debug.eventDebugLevel, msg, False)
            self._processObjectEvent(event)
            if debugging:
                msg = (
                    f"TOTAL PROCESSING TIME: {time.time() - startTime:.4f}"
                    f"\n^^^^^ PROCESS OBJECT EVENT {event.type} ^^^^^\n"
                )
                debug.printMessage(debug.eventDebugLevel, msg, False)

            debug.objEvent = None

            self._gidleLock.acquire()
            if self._eventQueue.empty():
                GLib.timeout_add(2500, self._onNoFocus)
                self._gidleId = 0
                rerun = False # destroy and don't call again
            self._gidleLock.release()
        except queue.Empty:
            msg = 'EVENT MANAGER: Attempted dequeue, but the event queue is empty'
            debug.printMessage(debug.LEVEL_SEVERE, msg, True)
            self._gidleId = 0
            rerun = False # destroy and don't call again
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)

        return rerun

    def registerListener(self, eventType):
        """Tells this module to listen for the given event type.

        Arguments:
        - eventType: the event type.
        """

        msg = f'EVENT MANAGER: registering listener for: {eventType}'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

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
        debug.printMessage(debug.LEVEL_INFO, msg, True)

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

        tokens = ["EVENT MANAGER: Registering listeners for:", script]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        for eventType in script.listeners.keys():
            self.registerListener(eventType)

    def deregisterScriptListeners(self, script):
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        tokens = ["EVENT MANAGER: De-registering listeners for:", script]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        for eventType in script.listeners.keys():
            self.deregisterListener(eventType)

    @staticmethod
    def _getScriptForEvent(event):
        """Returns the script associated with event."""

        if event.type.startswith("mouse:"):
            mouseEvent = input_event.MouseButtonEvent(event)
            script = script_manager.getManager().getScript(mouseEvent.app, mouseEvent.window, False)
            tokens = ["EVENT MANAGER: Script for event is", script]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return script

        script = None
        app = AXObject.get_application(event.source)
        if AXUtilities.is_defunct(app):
            tokens = ["EVENT MANAGER:", app, "is defunct. Cannot get script for event."]
            debug.printTokens(debug.LEVEL_WARNING, tokens, True)
            return None

        skipCheck = {
            "object:children-changed",
            "object:column-reordered",
            "object:row-reordered",
            "object:property-change",
            "object:selection-changed",
            "object:state-changed:checked",
            "object:state-changed:expanded",
            "object:state-changed:indeterminate",
            "object:state-changed:pressed",
            "object:state-changed:selected",
            "object:state-changed:sensitive",
            "object:state-changed:showing",
            "object:text-changed",
        }

        check = not any(event.type.startswith(x) for x in skipCheck)
        tokens = ["EVENT MANAGER: Getting script for event for", app, "check:", check]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.getManager().getScript(app, event.source, sanityCheck=check)
        tokens = ["EVENT MANAGER: Script for event is", script]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
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

        if script == script_manager.getManager().getActiveScript():
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
            if event.source != focus_manager.getManager().get_active_window():
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
            tokens = ["EVENT MANAGER: source of", event.type, "is dead"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
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

        return event.source != focus_manager.getManager().get_locus_of_focus()

    def _inDeluge(self):
        size = self._eventQueue.qsize()
        if size > 100:
            msg = f"EVENT MANAGER: DELUGE! Queue size is {size}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _processDuringFlood(self, event, focus=None):
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

        focus = focus or focus_manager.getManager().get_locus_of_focus()
        return event.source == focus

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
        focus = focus_manager.getManager().get_locus_of_focus()
        while not self._eventQueue.empty():
            try:
                event = self._eventQueue.get()
            except Exception as error:
                msg = f"EVENT MANAGER: Exception pruning events: {error}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            else:
                if self._processDuringFlood(event, focus):
                    newQueue.put(event)
                    self._queuePrintln(event, isPrune=False)
            finally:
                if not self._eventQueue.empty():
                    self._eventQueue.task_done()

        self._eventQueue = newQueue
        newSize = self._eventQueue.qsize()

        msg = f"EVENT MANAGER: {oldSize - newSize} events pruned. New size: {newSize}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _inFlood(self):
        size = self._eventQueue.qsize()
        if size > 50:
            msg = f"EVENT MANAGER: FLOOD? Queue size is {size}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _shouldProcessEvent(self, event, eventScript, activeScript):
        if eventScript == activeScript:
            msg = f"EVENT MANAGER: Processing {event.type}: script for event is active"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if eventScript.presentIfInactive:
            msg = f"EVENT MANAGER: Processing {event.type}: script handles events when inactive"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_progress_bar(event.source) \
           and settings.progressBarVerbosity == settings.PROGRESS_BAR_ALL:
            msg = f"EVENT MANAGER: Processing {event.type}: progress bar verbosity is 'all'"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = f"EVENT MANAGER: Not processing {event.type} due to lack of reason"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return False

    def _processObjectEvent(self, event):
        """Handles all object events destined for scripts.

        Arguments:
        - e: an at-spi event.
        """

        if self._isObsoletedBy(event):
            return

        eType = event.type
        if eType.startswith("object:children-changed:remove") \
           and event.source == AXUtilities.get_desktop():
            script_manager.getManager().reclaimScripts()
            return

        if AXObject.is_dead(event.source) or AXUtilities.is_defunct(event.source):
            tokens = ["EVENT MANAGER: Ignoring defunct object:", event.source]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

            if eType.startswith("window:deactivate") or eType.startswith("window:destroy") \
               and focus_manager.getManager().get_active_window() == event.source:
                focus_manager.getManager().clear_state("Active window is dead or defunct")
                script_manager.getManager().setActiveScript(
                    None, "Active window is dead or defunct")
            return

        if eType.startswith("window:") and not eType.endswith("create"):
            script_manager.getManager().reclaimScripts()
        elif eType.startswith("object:state-changed:active") \
           and AXUtilities.is_frame(event.source):
            script_manager.getManager().reclaimScripts()

        if AXUtilities.is_iconified(event.source):
            tokens = ["EVENT MANAGER: Ignoring iconified object:", event.source]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        if self._inFlood():
            if not self._processDuringFlood(event):
                msg = 'EVENT MANAGER: Not processing this event due to flood.'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return
            if self._prioritizeDuringFlood(event):
                msg = 'EVENT MANAGER: Pruning event queue due to flood.'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self._pruneEventsDuringFlood()

        debug.printObjectEvent(debug.LEVEL_INFO, event, timestamp=True)
        if not debug.eventDebugFilter or debug.eventDebugFilter.match(eType) \
           and not eType.startswith("mouse:"):
            indent = " " * 32
            debug.printDetails(debug.LEVEL_INFO, indent, event.source)
            if isinstance(event.any_data, Atspi.Accessible):
                debug.printMessage(debug.LEVEL_INFO, f"{indent}ANY DATA:")
                debug.printDetails(debug.LEVEL_INFO, indent, event.any_data, includeApp=False)

        script = self._getScriptForEvent(event)
        if not script:
            msg = "ERROR: Could not get script for event"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        setNewActiveScript, reason = self._isActivatableEvent(event, script)
        msg = f'EVENT MANAGER: Change active script: {setNewActiveScript} ({reason})'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if setNewActiveScript:
            try:
                script_manager.getManager().setActiveScript(script, reason)
            except Exception as error:
                tokens = ["EVENT MANAGER: Exception setting active script for",
                          event.source, ":", error]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return

        activeScript = script_manager.getManager().getActiveScript()
        if not self._shouldProcessEvent(event, script, activeScript):
            return

        try:
            script.processObjectEvent(event)
        except Exception as error:
            msg = f"EVENT MANAGER: Exception processing {event.type}: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            debug.printException(debug.LEVEL_INFO)

        if debug.LEVEL_INFO >= debug.debugLevel and script:
            attributes = script.getTransferableAttributes()
            for key, value in attributes.items():
                msg = f"EVENT MANAGER: {key}: {value}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _processKeyboardEvent(self, device, pressed, keycode, keysym, state, text):
        keyboardEvent = input_event.KeyboardEvent(pressed, keycode, keysym, state, text)
        keyboardEvent.process()

    def process_braille_event(self, event):
        """Processes this BrailleEvent."""

        braille_event = input_event.BrailleEvent(event)
        return braille_event.process()

_manager = EventManager()

def getManager():
    return _manager
