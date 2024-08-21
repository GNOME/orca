# Orca
#
# Copyright 2011-2024 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position

"""Manager for accessible object events."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011-2024 Igalia, S.L."
__license__   = "LGPL"

import queue
import threading
import time

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from . import focus_manager
from . import input_event
from . import input_event_manager
from . import script_manager
from . import settings
from .ax_object import AXObject
from .ax_utilities import AXUtilities


class EventManager:
    """Manager for accessible object events."""

    def __init__(self):
        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Initializing', True)
        self._script_listener_counts = {}
        self._active = False
        self._paused = False
        self._event_queue     = queue.Queue(0)
        self._gidle_id        = 0
        self._gidle_lock      = threading.Lock()
        self._listener = Atspi.EventListener.new(self._enqueue_object_event)
        debug.printMessage(debug.LEVEL_INFO, 'Event manager initialized', True)

    def activate(self):
        """Called when this event manager is activated."""

        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Activating', True)
        input_event_manager.get_manager().start_key_watcher()
        self._active = True
        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Activated', True)

    def deactivate(self):
        """Called when this event manager is deactivated."""

        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivating', True)
        input_event_manager.get_manager().stop_key_watcher()
        self._active = False
        self._event_queue = queue.Queue(0)
        self._script_listener_counts = {}
        debug.printMessage(debug.LEVEL_INFO, 'EVENT MANAGER: Deactivated', True)

    def pause_queuing(self, pause=True, clear_queue=False, reason=""):
        """Pauses/unpauses event queuing."""

        msg = f"EVENT MANAGER: Pause queueing: {pause}. Clear queue: {clear_queue}. {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._paused = pause
        if clear_queue:
            self._event_queue = queue.Queue(0)

    def _is_obsoleted_by(self, event):
        """Returns the event which renders this one no longer worthy of being processed."""

        def is_same(x):
            return x.type == event.type \
                and x.source == event.source \
                and x.detail1 == event.detail1 \
                and x.detail2 == event.detail2 \
                and x.any_data == event.any_data

        def obsoletes_if_same_type_and_object(x):
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

        def obsoletes_if_same_type_in_sibling(x):
            if x.type != event.type or x.detail1 != event.detail1 or x.detail2 != event.detail2 \
               or x.any_data != event.any_data:
                return False

            skippable = {
                "object:state-changed:focused",
            }
            if not any(x.type.startswith(etype) for etype in skippable):
                return False
            return AXObject.get_parent(x.source) == AXObject.get_parent(event.source)

        def obsoletes_window_event(x):
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

        with self._event_queue.mutex:
            try:
                events = list(reversed(self._event_queue.queue))
            except Exception as error:
                msg = f"EVENT MANAGER: Exception in _isObsoletedBy: {error}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                events = []

        for e in events:
            if e == event:
                return None
            if is_same(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent duplicate"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletes_if_same_type_and_object(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent event of same type for same object"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletes_if_same_type_in_sibling(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent event of same type from sibling"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletes_window_event(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e,
                          "more recent window (de)activation event"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return e

        tokens = ["EVENT MANAGER:", event, "is not obsoleted"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return None

    def _ignore(self, event):
        """Returns True if this event should be ignored."""

        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

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

        if self._in_deluge() and self._ignore_during_deluge(event):
            msg = 'EVENT MANAGER: Ignoring event type due to deluge'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        # gnome-shell fires "focused" events spuriously after the Alt+Tab switcher
        # is used and something else has claimed focus. We don't want to update our
        # location or the keygrabs in response.
        if AXUtilities.is_window(event.source) and "focused" in event_type:
            msg = "EVENT MANAGER: Ignoring event based on type and role"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        # Keep these checks early in the process so we can assume them throughout
        # the rest of our checks.
        focus = focus_manager.get_manager().get_locus_of_focus()
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
            app = AXObject.get_application(event.source)
            app_name = AXObject.get_name(app).lower()
            if "remove" in event_type and app_name in ["gnome-shell", ""]:
                msg = "EVENT MANAGER: Ignoring event based on type and app"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if "remove" in event_type and focus and AXObject.is_dead(focus):
                return False
            if AXObject.is_dead(child):
                msg = 'EVENT_MANAGER: Ignoring due to dead event.any_data'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if AXUtilities.is_menu_related(child) or AXUtilities.is_image(child):
                msg = 'EVENT_MANAGER: Ignoring due to role of event.any_data'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if event_type.endswith("system") and app_name == "thunderbird":
                msg = "EVENT MANAGER: Ignoring event based on type and app"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            script = script_manager.get_manager().get_active_script()
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

    def _queue_println(self, e, is_enqueue=True, is_prune=None):
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

        if is_prune:
            tokens[0:0] = ["EVENT MANAGER: Pruning"]
        elif is_prune is not None:
            tokens[0:0] = ["EVENT MANAGER: Not pruning"]
        elif is_enqueue:
            tokens[0:0] = ["EVENT MANAGER: Queueing"]
        else:
            tokens[0:0] = ["EVENT MANAGER: Dequeued"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

    def _enqueue_object_event(self, e):
        """Callback for Atspi object events."""

        if self._ignore(e):
            return

        self._queue_println(e)

        if self._in_flood() and self._prioritize_during_flood(e):
            msg = 'EVENT MANAGER: Pruning event queue due to flood.'
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._prune_events_during_flood()

        app = AXObject.get_application(e.source)
        tokens = ["EVENT MANAGER: App for event source is", app]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.get_manager().get_script(app, e.source)
        script.event_cache[e.type] = (e, time.time())

        with self._gidle_lock:
            self._event_queue.put(e)
            if not self._gidle_id:
                self._gidle_id = GLib.idle_add(self._dequeue_object_event)

    def _on_no_focus(self):
        if focus_manager.get_manager().focus_and_window_are_unknown():
            return False

        if script_manager.get_manager().get_active_script() is None:
            default_script = script_manager.get_manager().get_default_script()
            script_manager.get_manager().set_active_script(default_script, 'No focus')
            default_script.idleMessage()

        return False

    def _dequeue_object_event(self):
        """Handles all object events destined for scripts."""

        rerun = True
        try:
            event = self._event_queue.get_nowait()
            self._queue_println(event, is_enqueue=False)
            debug.objEvent = event
            debugging = not debug.eventDebugFilter \
                        or debug.eventDebugFilter.match(event.type)
            if debugging:
                start_time = time.time()
                msg = (
                    f"\nvvvvv PROCESS OBJECT EVENT {event.type} "
                    f"(queue size: {self._event_queue.qsize()}) vvvvv"
                )
                debug.printMessage(debug.eventDebugLevel, msg, False)
            self._process_object_event(event)
            if debugging:
                msg = (
                    f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}"
                    f"\n^^^^^ PROCESS OBJECT EVENT {event.type} ^^^^^\n"
                )
                debug.printMessage(debug.eventDebugLevel, msg, False)

            debug.objEvent = None
            with self._gidle_lock:
                if self._event_queue.empty():
                    GLib.timeout_add(2500, self._on_no_focus)
                    self._gidle_id = 0
                    rerun = False  # destroy and don't call again

        except queue.Empty:
            msg = 'EVENT MANAGER: Attempted dequeue, but the event queue is empty'
            debug.printMessage(debug.LEVEL_SEVERE, msg, True)
            self._gidle_id = 0
            rerun = False # destroy and don't call again
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)

        return rerun

    def register_listener(self, event_type):
        """Tells this module to listen for the given event type.

        Arguments:
        - event_type: the event type.
        """

        msg = f'EVENT MANAGER: registering listener for: {event_type}'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if event_type in self._script_listener_counts:
            self._script_listener_counts[event_type] += 1
        else:
            self._listener.register(event_type)
            self._script_listener_counts[event_type] = 1

    def deregister_listener(self, event_type):
        """Tells this module to stop listening for the given event type.

        Arguments:
        - event_type: the event type.
        """

        msg = f'EVENT MANAGER: deregistering listener for: {event_type}'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if event_type not in self._script_listener_counts:
            return

        self._script_listener_counts[event_type] -= 1
        if self._script_listener_counts[event_type] == 0:
            self._listener.deregister(event_type)
            del self._script_listener_counts[event_type]

    def register_script_listeners(self, script):
        """Tells the event manager to start listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        tokens = ["EVENT MANAGER: Registering listeners for:", script]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        for event_type in script.listeners.keys():
            self.register_listener(event_type)

    def deregister_script_listeners(self, script):
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        tokens = ["EVENT MANAGER: De-registering listeners for:", script]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        for event_type in script.listeners.keys():
            self.deregister_listener(event_type)

    @staticmethod
    def _get_script_for_event(event, active_script=None):
        """Returns the script associated with event."""

        if event.source == focus_manager.get_manager().get_locus_of_focus():
            script = active_script or script_manager.get_manager().get_active_script()
            tokens = ["EVENT MANAGER: Script for event from locus of focus is", script]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return script

        if event.type.startswith("mouse:"):
            mouse_event = input_event.MouseButtonEvent(event)
            script = script_manager.get_manager().get_script(
                mouse_event.app, mouse_event.window)
            tokens = ["EVENT MANAGER: Script for event is", script]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return script

        script = None
        app = AXObject.get_application(event.source)
        if AXUtilities.is_defunct(app):
            tokens = ["EVENT MANAGER:", app, "is defunct. Cannot get script for event."]
            debug.printTokens(debug.LEVEL_WARNING, tokens, True)
            return None

        tokens = ["EVENT MANAGER: Getting script for event for", app, event.source]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.get_manager().get_script(app, event.source)
        tokens = ["EVENT MANAGER: Script for event is", script]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return script

    def _is_activatable_event(self, event, script=None):
        """Determines if event should cause us to change the active script."""

        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-branches

        if not event.source:
            return False, "event.source? What event.source??"

        if not script:
            script = self._get_script_for_event(event)
            if not script:
                return False, "There is no script for this event."

        app = AXObject.get_application(event.source)
        if app and not AXUtilities.is_application_in_desktop(app):
            return False, "The application is unknown to AT-SPI2"

        if not script.is_activatable_event(event):
            return False, "The script says not to activate for this event."

        if script.force_script_activation(event):
            return True, "The script insists it should be activated for this event."

        event_type = event.type

        if event_type.startswith('window:activate'):
            window_activation = True
        else:
            window_activation = event_type.startswith('object:state-changed:active') \
                and event.detail1 and AXUtilities.is_frame(event.source)

        if window_activation:
            if event.source != focus_manager.get_manager().get_active_window():
                return True, "Window activation"
            return False, "Window activation for already-active window"

        if event_type.startswith('object:state-changed:focused') and event.detail1:
            return True, "Event source claimed focus."

        if event_type.startswith('object:state-changed:selected') and event.detail1 \
           and AXUtilities.is_menu(event.source) and AXUtilities.is_focusable(event.source):
            return True, "Selection change in focused menu"

        # This condition appears with gnome-screensaver-dialog.
        # See bug 530368.
        if event_type.startswith('object:state-changed:showing') \
           and AXUtilities.is_panel(event.source) and AXUtilities.is_modal(event.source):
            return True, "Modal panel is showing."

        return False, "No reason found to activate a different script."

    def _event_source_is_dead(self, event):
        if AXObject.is_dead(event.source):
            tokens = ["EVENT MANAGER: source of", event.type, "is dead"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def _ignore_during_deluge(self, event):
        """Returns true if this event should be ignored during a deluge."""

        if self._event_source_is_dead(event):
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

        return event.source != focus_manager.get_manager().get_locus_of_focus()

    def _in_flood(self):
        """Returns True if we're in an event flood."""

        size = self._event_queue.qsize()
        if size > 50:
            msg = f"EVENT MANAGER: FLOOD? Queue size is {size}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _in_deluge(self):
        """Returns True if we're in a deluge / huge flood."""

        size = self._event_queue.qsize()
        if size > 100:
            msg = f"EVENT MANAGER: DELUGE! Queue size is {size}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _process_during_flood(self, event, focus=None):
        """Returns true if this event should be processed during a flood."""

        if self._event_source_is_dead(event):
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

        focus = focus or focus_manager.get_manager().get_locus_of_focus()
        return event.source == focus

    def _prioritize_during_flood(self, event):
        """Returns true if this event should be prioritized during a flood."""

        if event.type.startswith("object:state-changed:focused") \
           or event.type.startswith("object:state-changed:selected"):
            return event.detail1

        if event.type.startswith("object:text-selection-changed"):
            return True

        if event.type.startswith("window:activate") or event.type.startswith("window:deactivate"):
            return True

        if event.type.startswith("object:state-changed:active"):
            return AXUtilities.is_frame(event.source) or AXUtilities.is_window(event.source)

        if event.type.startswith("document:load-complete") \
           or event.type.startswith("object:state-changed:busy"):
            return True

        return False

    def _prune_events_during_flood(self):
        """Gets rid of events we don't care about during a flood."""

        old_size = self._event_queue.qsize()

        new_queue = queue.Queue(0)
        focus = focus_manager.get_manager().get_locus_of_focus()
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get()
            except Exception as error:
                msg = f"EVENT MANAGER: Exception pruning events: {error}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            else:
                if self._process_during_flood(event, focus):
                    new_queue.put(event)
                    self._queue_println(event, is_prune=False)
            finally:
                if not self._event_queue.empty():
                    self._event_queue.task_done()

        self._event_queue = new_queue
        new_size = self._event_queue.qsize()

        msg = f"EVENT MANAGER: {old_size - new_size} events pruned. New size: {new_size}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _should_process_event(self, event, event_script, active_script):
        """Returns True if this event should be processed."""

        if event_script == active_script:
            msg = f"EVENT MANAGER: Processing {event.type}: script for event is active"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if event_script.present_if_inactive:
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

    def _process_object_event(self, event):
        """Handles all object events destined for scripts."""

        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        if self._is_obsoleted_by(event):
            return

        script_mgr = script_manager.get_manager()
        focus_mgr = focus_manager.get_manager()

        event_type = event.type
        if event_type.startswith("object:children-changed:remove") \
           and event.source == AXUtilities.get_desktop():
            script_mgr.reclaim_scripts()
            return

        if AXObject.is_dead(event.source) or AXUtilities.is_defunct(event.source):
            tokens = ["EVENT MANAGER: Ignoring defunct object:", event.source]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

            if event_type.startswith("window:de") and focus_mgr.get_active_window() == event.source:
                focus_mgr.clear_state("Active window is dead or defunct")
                script_mgr.set_active_script(None, "Active window is dead or defunct")
            return

        if event_type.startswith("window:") and not event_type.endswith("create"):
            script_mgr.reclaim_scripts()
        elif event_type.endswith("state-changed:active") and AXUtilities.is_frame(event.source):
            script_mgr.reclaim_scripts()

        if AXUtilities.is_iconified(event.source):
            tokens = ["EVENT MANAGER: Ignoring iconified object:", event.source]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        if self._in_flood():
            if not self._process_during_flood(event):
                msg = 'EVENT MANAGER: Not processing this event due to flood.'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return
            if self._prioritize_during_flood(event):
                msg = 'EVENT MANAGER: Pruning event queue due to flood.'
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self._prune_events_during_flood()

        debug.printObjectEvent(debug.LEVEL_INFO, event, timestamp=True)
        if not debug.eventDebugFilter or debug.eventDebugFilter.match(event_type) \
           and not event_type.startswith("mouse:"):
            indent = " " * 32
            debug.printDetails(debug.LEVEL_INFO, indent, event.source)
            if isinstance(event.any_data, Atspi.Accessible):
                debug.printMessage(debug.LEVEL_INFO, f"{indent}ANY DATA:")
                debug.printDetails(debug.LEVEL_INFO, indent, event.any_data, includeApp=False)

        active_script = script_mgr.get_active_script()
        script = self._get_script_for_event(event, active_script)
        if not script:
            msg = "ERROR: Could not get script for event"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if script != active_script:
            set_new_active_script, reason = self._is_activatable_event(event, script)
            msg = f'EVENT MANAGER: Change active script: {set_new_active_script} ({reason})'
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            if set_new_active_script:
                script_mgr.set_active_script(script, reason)
                active_script = script

        if not self._should_process_event(event, script, active_script):
            return

        listener = script.listeners.get(event.type)
        # The listener can be None if the event type has a suffix such as "system".
        if listener is None:
            for key, value in script.listeners.items():
                if event.type.startswith(key):
                    listener = value
                    break

        try:
            listener(event)
        except Exception as error:
            msg = f"EVENT MANAGER: Exception processing {event.type}: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            debug.printException(debug.LEVEL_INFO)

_manager = EventManager()

def get_manager():
    """Returns the Event Manager singleton."""
    return _manager
