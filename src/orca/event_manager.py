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

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals

"""Manager for accessible object events."""

from __future__ import annotations

import itertools
import queue
import threading
import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import (
    braille_presenter,
    debug,
    focus_manager,
    input_event,
    input_event_manager,
    orca_modifier_manager,
    script_manager,
    systemd,
)
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .ax_utilities_debugging import AXUtilitiesDebugging

if TYPE_CHECKING:
    from .scripts import default


class EventManager:
    """Manager for accessible object events."""

    PRIORITY_IMMEDIATE = 1
    PRIORITY_IMPORTANT = 2
    PRIORITY_HIGH = 3
    PRIORITY_NORMAL = 4
    PRIORITY_LOWER = 5
    PRIORITY_LOW = 6

    def __init__(self) -> None:
        debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Initializing", True)
        self._script_listener_counts: dict[str, int] = {}
        self._active: bool = False
        self._paused: bool = False
        self._counter = itertools.count()
        self._event_queue: queue.PriorityQueue[tuple[int, int, Atspi.Event]] = queue.PriorityQueue(
            0,
        )
        self._gidle_id: int = 0
        self._gidle_lock = threading.Lock()
        self._listener: Atspi.EventListener = Atspi.EventListener.new(self._enqueue_object_event)
        self._event_history: dict[str, tuple[int | None, float]] = {}
        debug.print_message(debug.LEVEL_INFO, "Event manager initialized", True)

    def activate(self) -> None:
        """Called when this event manager is activated."""

        debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Activating", True, True)
        if self._active:
            debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Already activated", True)
            return

        input_event_manager.get_manager().start_key_watcher()
        orca_modifier_manager.get_manager().add_grabs_for_orca_modifiers()
        self._active = True
        debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Activated", True)

    def deactivate(self) -> None:
        """Called when this event manager is deactivated."""

        debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Deactivating", True, True)
        if not self._active:
            debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Already deactivated", True)
            return

        input_event_manager.get_manager().stop_key_watcher()
        self._active = False
        self._event_queue = queue.PriorityQueue(0)
        self._script_listener_counts = {}
        debug.print_message(debug.LEVEL_INFO, "EVENT MANAGER: Deactivated", True)

    def pause_queuing(
        self,
        pause: bool = True,
        clear_queue: bool = False,
        reason: str = "",
    ) -> None:
        """Pauses/unpauses event queuing."""

        msg = f"EVENT MANAGER: Pause queueing: {pause}. Clear queue: {clear_queue}. {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._paused = pause
        if clear_queue:
            self._event_queue = queue.PriorityQueue(0)
        input_event_manager.get_manager().pause_key_watcher(pause, reason)

    def _get_priority(self, event: Atspi.Event) -> int:
        """Returns the priority associated with event."""

        event_type = event.type
        if event_type.startswith("window") or (
            event_type == "object:state-changed:active"
            and (AXUtilities.is_frame(event.source) or AXUtilities.is_dialog_or_alert(event.source))
        ):
            priority = EventManager.PRIORITY_IMPORTANT
        elif event_type.startswith(
            ("object:state-changed:focused", "object:active-descendant-changed"),
        ):
            priority = EventManager.PRIORITY_HIGH
        elif event_type.startswith("object:announcement"):
            if event.detail1 == Atspi.Live.ASSERTIVE:
                priority = EventManager.PRIORITY_IMPORTANT
            elif event.detail1 == Atspi.Live.POLITE:
                priority = EventManager.PRIORITY_HIGH
            else:
                priority = EventManager.PRIORITY_NORMAL
        elif event_type.startswith("object:state-changed:invalid-entry"):
            # Setting this to lower ensures we present the state and/or text changes that triggered
            # the invalid state prior to presenting the invalid state.
            priority = EventManager.PRIORITY_LOWER
        elif event_type.startswith("object:children-changed"):
            priority = EventManager.PRIORITY_LOW
        else:
            priority = EventManager.PRIORITY_NORMAL

        tokens = ["EVENT MANAGER:", event, f"has priority level: {priority}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return priority

    def _is_obsoleted_by(self, event: Atspi.Event) -> Atspi.Event | None:
        """Returns the event which renders this one no longer worthy of being processed."""

        def is_same(x):
            return (
                x.type == event.type
                and x.source == event.source
                and x.detail1 == event.detail1
                and x.detail2 == event.detail2
                and x.any_data == event.any_data
            )

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
            if (
                x.type != event.type
                or x.detail1 != event.detail1
                or x.detail2 != event.detail2
                or x.any_data != event.any_data
            ):
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
            return x.source == event.source

        with self._event_queue.mutex:
            try:
                events = list(reversed(self._event_queue.queue))
            except queue.Empty as error:
                msg = f"EVENT MANAGER: Exception in _isObsoletedBy: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                events = []

        for _priority, _counter, e in events:
            if e == event:
                return None
            if is_same(e):
                tokens = ["EVENT MANAGER:", event, "obsoleted by", e, "more recent duplicate"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletes_if_same_type_and_object(e):
                tokens = [
                    "EVENT MANAGER:",
                    event,
                    "obsoleted by",
                    e,
                    "more recent event of same type for same object",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletes_if_same_type_in_sibling(e):
                tokens = [
                    "EVENT MANAGER:",
                    event,
                    "obsoleted by",
                    e,
                    "more recent event of same type from sibling",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return e
            if obsoletes_window_event(e):
                tokens = [
                    "EVENT MANAGER:",
                    event,
                    "obsoleted by",
                    e,
                    "more recent window (de)activation event",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return e

        return None

    def _ignore_by_role(self, event: Atspi.Event) -> bool | None:
        """Returns True/False if the source role determines ignore, or None if inconclusive."""

        event_type = event.type

        # gnome-shell fires "focused" events spuriously after the Alt+Tab switcher
        # is used and something else has claimed focus.
        if AXUtilities.is_window(event.source) and "focused" in event_type:
            msg = f"EVENT MANAGER: Ignoring {event_type} based on type and role"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_frame(event.source):
            app = AXUtilities.get_application(event.source)
            ignore = AXObject.get_name(app) == "mutter-x11-frames"
            prefix = "Ignoring" if ignore else "Not ignoring"
            reason = "application" if ignore else "role"
            msg = f"EVENT MANAGER: {prefix} {event_type} based on {reason}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ignore

        # Events from the text role are typically something we want to handle.
        # One exception is a huge text insertion.
        if AXUtilities.is_text(event.source):
            if event_type.startswith("object:text-changed:insert") and event.detail2 > 5000:
                msg = f"EVENT_MANAGER: Ignoring {event_type} due to size of inserted text"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            if not event_type.startswith("object:text-caret-moved"):
                msg = f"EVENT_MANAGER: Not ignoring {event_type} due to role"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        if AXUtilities.is_notification(event.source) or AXUtilities.is_alert(event.source):
            msg = f"EVENT_MANAGER: Not ignoring {event_type} due to role"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return None

    def _ignore_by_focus_state(
        self,
        event: Atspi.Event,
        focus: Atspi.Accessible | None,
    ) -> bool | None:
        """Returns False if focus/state means we should not ignore, or None if inconclusive."""

        event_type = event.type
        if focus in (event.source, event.any_data):
            reason = "source" if focus == event.source else "any_data"
            msg = f"EVENT_MANAGER: Not ignoring {event_type} due to {reason} being locus of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_selected(event.source):
            msg = f"EVENT_MANAGER: Not ignoring {event_type} due to source being selected"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        # We see an unbelievable number of active-descendant-changed and selection changed
        # from Caja when the user navigates from one giant folder to another. We need the
        # spam filtering below to catch this bad behavior coming from a focused object, so
        # only return early here if the focused object doesn't manage descendants, or the
        # event is not a focus claim.
        if AXUtilities.is_focused(event.source):
            if not AXUtilities.manages_descendants(event.source) or (
                event_type.startswith("object:state-changed:focused") and event.detail1
            ):
                msg = f"EVENT_MANAGER: Not ignoring {event_type} due to source being focused"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        if event_type.startswith("object:text-changed:insert") and AXUtilities.is_section(
            event.source,
        ):
            live = AXObject.get_attribute(event.source, "live")
            if live and live != "off":
                msg = f"EVENT_MANAGER: Not ignoring {event_type} due to source being live region"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        return None

    def _ignore_by_spam_filter(self, event: Atspi.Event) -> bool | None:
        """Returns True if the event is spam, or None if inconclusive."""

        event_type = event.type
        last_app, last_time = self._event_history.get(event_type, (None, 0))
        app = AXUtilities.get_application(event.source)
        ignore = last_app == hash(app) and time.time() - last_time < 0.1
        self._event_history[event_type] = hash(app), time.time()
        if ignore:
            msg = f"EVENT_MANAGER: Ignoring {event_type} due to multiple instances in short time"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXObject.get_name(app) == "mutter-x11-frames":
            msg = f"EVENT MANAGER: Ignoring {event_type} based on application"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return None

    @staticmethod
    def _ignore_children_changed(
        event: Atspi.Event,
        focus: Atspi.Accessible | None,
    ) -> bool | None:
        """Returns True/False for children-changed events, or None if not applicable."""

        event_type = event.type
        if not event_type.startswith("object:children-changed"):
            return None

        if "remove" in event_type:
            if (focus and AXObject.is_dead(focus)) or event.source == AXUtilities.get_desktop():
                return False

        child = event.any_data
        if child is None or AXObject.is_dead(child):
            msg = f"EVENT_MANAGER: Ignoring {event_type} due to null/dead event.any_data"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        if AXUtilities.is_menu_related(child) or AXUtilities.is_image(child):
            msg = f"EVENT_MANAGER: Ignoring {event_type} due to role of event.any_data"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        script = script_manager.get_manager().get_active_script()
        if script is None or script.app != AXUtilities.get_application(event.source):
            reason = (
                "there is no active script" if script is None else "event is not from active app"
            )
            msg = f"EVENT MANAGER: Ignoring {event_type} because {reason}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return None

    @staticmethod
    def _ignore_property_change(event: Atspi.Event) -> bool | None:
        """Returns True/False for property-change events, or None if not applicable."""

        event_type = event.type
        if not event_type.startswith("object:property-change"):
            return None

        role = AXObject.get_role(event.source)
        if "name" in event_type:
            ignore_name_roles = [
                Atspi.Role.CANVAS,
                Atspi.Role.CHECK_BOX,
                Atspi.Role.ICON,
                Atspi.Role.IMAGE,
                Atspi.Role.LIST,
                Atspi.Role.LIST_ITEM,
                Atspi.Role.MENU,
                Atspi.Role.MENU_ITEM,
                Atspi.Role.PANEL,
                Atspi.Role.RADIO_BUTTON,
                Atspi.Role.SECTION,
                Atspi.Role.TABLE_ROW,
                Atspi.Role.TABLE_CELL,
                Atspi.Role.TREE_ITEM,
            ]
            if role in ignore_name_roles:
                msg = f"EVENT MANAGER: Ignoring {event_type} due to role of unfocused source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            return False
        if "value" in event_type:
            if role in [Atspi.Role.SPLIT_PANE, Atspi.Role.SCROLL_BAR]:
                msg = f"EVENT MANAGER: Ignoring {event_type} due to role of unfocused source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            return False

        return None

    @staticmethod
    def _ignore_state_changed(event: Atspi.Event) -> bool | None:
        """Returns True/False for state-changed events, or None if not applicable."""

        event_type = event.type
        if not event_type.startswith("object:state-changed"):
            return None

        role = AXObject.get_role(event.source)
        if event_type.endswith("system"):
            system_ignore_roles = [
                Atspi.Role.TABLE,
                Atspi.Role.TABLE_CELL,
                Atspi.Role.TABLE_ROW,
                Atspi.Role.TREE,
                Atspi.Role.TREE_ITEM,
                Atspi.Role.TREE_TABLE,
            ]
            if role in system_ignore_roles:
                msg = f"EVENT MANAGER: Ignoring {event_type} based on role"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        return EventManager._ignore_state_changed_subtype(event, event_type, role)

    @staticmethod
    def _ignore_state_changed_subtype(
        event: Atspi.Event,
        event_type: str,
        role: int,
    ) -> bool | None:
        """Returns True/False for state-changed subtypes, or None if not applicable."""

        showing_roles = [
            Atspi.Role.ALERT,
            Atspi.Role.ANIMATION,
            Atspi.Role.DIALOG,
            Atspi.Role.INFO_BAR,
            Atspi.Role.MENU,
            Atspi.Role.NOTIFICATION,
            Atspi.Role.STATUS_BAR,
            Atspi.Role.TOOL_TIP,
        ]

        ignore: bool | None = None
        reason = ""
        if "checked" in event_type:
            ignore = not AXUtilities.is_showing(event.source)
            reason = "unfocused, non-showing source"
        elif "selected" in event_type:
            ignore = not event.detail1 and role == Atspi.Role.BUTTON
            reason = "role of source and detail1"
        elif "sensitive" in event_type:
            ignore = role not in [Atspi.Role.TEXT, Atspi.Role.ENTRY]
            reason = "role of unfocused source"
        elif "showing" in event_type:
            ignore = role not in showing_roles
            reason = "role"

        if ignore is None:
            return None

        if ignore:
            msg = f"EVENT MANAGER: Ignoring {event_type} due to {reason}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return ignore

    @staticmethod
    def _ignore_active_descendant_or_selection(event: Atspi.Event) -> bool | None:
        """Returns True/False for active-descendant and selection events."""

        event_type = event.type
        if event_type.startswith("object:active-descendant-changed"):
            child = event.any_data
            if child is None or AXUtilities.is_invalid_role(child):
                msg = f"EVENT_MANAGER: Ignoring {event_type} due to null/invalid event.any_data"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            return False

        if event_type.startswith("object:selection-changed"):
            if AXObject.is_dead(event.source):
                msg = f"EVENT MANAGER: Ignoring {event_type} from dead source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            return False

        return None

    @staticmethod
    def _ignore_text_events(
        event: Atspi.Event,
        focus: Atspi.Accessible | None,
    ) -> bool | None:
        """Returns True/False for text caret-moved and text-changed events."""

        event_type = event.type
        if event_type.startswith("object:text-caret-moved"):
            if AXObject.get_role(event.source) == Atspi.Role.LABEL:
                msg = f"EVENT MANAGER: Ignoring {event_type} due to role of unfocused source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            return False

        if event_type.startswith("object:text-changed"):
            if "insert" in event_type and event.detail2 > 1000:
                msg = f"EVENT MANAGER: Ignoring {event_type} due to inserted text size"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            if event_type.endswith("system") and AXUtilities.is_selectable(focus):
                msg = f"EVENT MANAGER: Ignoring because {event_type} is suspected spam"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            return False

        return None

    def _ignore(self, event: Atspi.Event) -> bool:
        """Returns True if this event should be ignored."""

        debug.print_message(debug.LEVEL_INFO, "")
        tokens = ["EVENT MANAGER:", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if event.type.startswith(("window", "mouse:button")):
            return False

        if not self._active or self._paused:
            msg = "EVENT MANAGER: Ignoring because manager is not active or queueing is paused"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        for check in (
            lambda: self._ignore_by_role(event),
            lambda: self._ignore_by_focus_state(event, focus),
            lambda: self._ignore_by_spam_filter(event),
            lambda: self._ignore_active_descendant_or_selection(event),
            lambda: self._ignore_children_changed(event, focus),
            lambda: self._ignore_property_change(event),
            lambda: self._ignore_state_changed(event),
            lambda: self._ignore_text_events(event, focus),
        ):
            result = check()
            if result is not None:
                return result

        return False

    def _queue_println(
        self,
        event: input_event.InputEvent | Atspi.Event,
        is_enqueue: bool = True,
    ) -> None:
        """Convenience method to output queue-related debugging info."""

        if debug.debugLevel > debug.LEVEL_INFO:
            return

        tokens = []
        if isinstance(event, input_event.KeyboardEvent):
            tokens.extend([event.keyval_name, event.hw_code])
        elif isinstance(event, input_event.BrailleEvent):
            tokens.append(event.event)
        else:
            tokens.append(event)

        if is_enqueue:
            tokens[0:0] = ["EVENT MANAGER: Queueing"]
        else:
            tokens[0:0] = ["EVENT MANAGER: Dequeueing"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def _enqueue_object_event(self, e: Atspi.Event) -> None:
        """Callback for Atspi object events."""

        # If we are enqueuing events, we're not dead and should not be killed
        # and restarted by systemd.
        if self._event_queue.qsize() > 75 and systemd.get_manager().is_systemd_managed():
            systemd.get_manager().notify_alive("Event queue size > 75")

        if self._ignore(e):
            return

        self._queue_println(e)
        app = AXUtilities.get_application(e.source)
        tokens = ["EVENT MANAGER: App for event source is", app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.get_manager().get_script(app, e.source)
        script.event_cache[e.type] = (e, time.time())

        with self._gidle_lock:
            priority = self._get_priority(e)
            counter = next(self._counter)
            self._event_queue.put((priority, counter, e))
            tokens = ["EVENT MANAGER: Queued", e, f"priority: {priority}, counter: {counter}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if not self._gidle_id:
                self._gidle_id = GLib.idle_add(self._dequeue_object_event)

    def _on_no_focus(self) -> bool:
        if focus_manager.get_manager().focus_and_window_are_unknown():
            return False

        if script_manager.get_manager().get_active_script() is None:
            default_script = script_manager.get_manager().get_default_script()
            script_manager.get_manager().set_active_script(default_script, "No focus")
            braille_presenter.get_presenter().disable_braille()

        return False

    def _dequeue_object_event(self) -> bool:
        """Handles all object events destined for scripts."""

        rerun = True
        try:
            priority, counter, event = self._event_queue.get_nowait()
            self._queue_println(event, is_enqueue=False)
            tokens = ["EVENT MANAGER: Dequeued", event, f"priority: {priority}, counter: {counter}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            start_time = time.time()
            msg = (
                f"\nvvvvv START PRIORITY-{priority} OBJECT EVENT {event.type.upper()} "
                f"(queue size: {self._event_queue.qsize()}) vvvvv"
            )
            debug.print_message(debug.LEVEL_INFO, msg, False)
            self._process_object_event(event)
            msg = (
                f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}"
                f"\n^^^^^ FINISHED PRIORITY-{priority} OBJECT EVENT {event.type.upper()} ^^^^^\n"
            )
            debug.print_message(debug.LEVEL_INFO, msg, False)
            with self._gidle_lock:
                if self._event_queue.empty():
                    GLib.timeout_add(2500, self._on_no_focus)
                    self._gidle_id = 0
                    rerun = False  # destroy and don't call again
        except queue.Empty:
            msg = "EVENT MANAGER: Attempted dequeue, but the event queue is empty"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._gidle_id = 0
            rerun = False  # destroy and don't call again
        except Exception:  # pylint: disable=broad-except
            self._gidle_id = GLib.idle_add(self._dequeue_object_event)
            raise

        return rerun

    def register_listener(self, event_type: str) -> None:
        """Tells this module to listen for the given event type.

        Arguments:
        - event_type: the event type.
        """

        msg = f"EVENT MANAGER: registering listener for: {event_type}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if event_type in self._script_listener_counts:
            self._script_listener_counts[event_type] += 1
        else:
            self._listener.register(event_type)
            self._script_listener_counts[event_type] = 1

    def deregister_listener(self, event_type: str) -> None:
        """Tells this module to stop listening for the given event type.

        Arguments:
        - event_type: the event type.
        """

        msg = f"EVENT MANAGER: deregistering listener for: {event_type}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if event_type not in self._script_listener_counts:
            return

        self._script_listener_counts[event_type] -= 1
        if self._script_listener_counts[event_type] == 0:
            try:
                self._listener.deregister(event_type)
            except GLib.GError as error:
                msg = f"EVENT MANAGER: Exception deregistering listener for {event_type}: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            del self._script_listener_counts[event_type]

    def register_script_listeners(self, script: default.Script) -> None:
        """Tells the event manager to start listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        tokens = ["EVENT MANAGER: Registering listeners for:", script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for event_type in script.listeners:
            self.register_listener(event_type)

    def deregister_script_listeners(self, script: default.Script) -> None:
        """Tells the event manager to stop listening for all the event types
        of interest to the script.

        Arguments:
        - script: the script.
        """

        tokens = ["EVENT MANAGER: De-registering listeners for:", script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for event_type in script.listeners:
            self.deregister_listener(event_type)

    @staticmethod
    def _get_script_for_event(
        event: Atspi.Event,
        active_script: default.Script | None = None,
    ) -> default.Script | None:
        """Returns the script associated with event."""

        if event.source == focus_manager.get_manager().get_locus_of_focus():
            script = active_script or script_manager.get_manager().get_active_script()
            tokens = ["EVENT MANAGER: Script for event from locus of focus is", script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return script

        if event.type.startswith("mouse:"):
            mouse_event = input_event.MouseButtonEvent(event)
            script = script_manager.get_manager().get_script(mouse_event.app, mouse_event.window)
            tokens = ["EVENT MANAGER: Script for event is", script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return script

        script = None
        app = AXUtilities.get_application(event.source)
        if AXUtilities.is_defunct(app):
            tokens = ["EVENT MANAGER:", app, "is defunct. Cannot get script for event."]
            debug.print_tokens(debug.LEVEL_WARNING, tokens, True)
            return None

        tokens = ["EVENT MANAGER: Getting script for event for", app, event.source]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.get_manager().get_script(app, event.source)
        tokens = ["EVENT MANAGER: Script for event is", script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return script

    def _is_activatable_event(
        self,
        event: Atspi.Event,
        script: default.Script | None = None,
    ) -> tuple[bool, str]:
        """Determines if event should cause us to change the active script."""

        if not event.source:
            return False, "event.source? What event.source??"

        if not script:
            script = self._get_script_for_event(event)
            if not script:
                return False, "There is no script for this event."

        app = AXUtilities.get_application(event.source)
        if app and not AXUtilities.is_application_in_desktop(app):
            return False, "The application is unknown to AT-SPI2"

        if not script.is_activatable_event(event):
            return False, "The script says not to activate for this event."

        if script.force_script_activation(event):
            return True, "The script insists it should be activated for this event."

        return self._is_activatable_by_event_type(event)

    @staticmethod
    def _is_activatable_by_event_type(event: Atspi.Event) -> tuple[bool, str]:
        """Determines if event type makes this an activatable event."""

        event_type = event.type

        window_activation = event_type.startswith("window:activate") or (
            event_type.startswith("object:state-changed:active")
            and event.detail1
            and AXUtilities.is_frame(event.source)
        )
        if window_activation:
            is_new = event.source != focus_manager.get_manager().get_active_window()
            reason = (
                "Window activation" if is_new else "Window activation for already-active window"
            )
            return is_new, reason

        if event_type.startswith("object:state-changed:focused") and event.detail1:
            return True, "Event source claimed focus."

        if (
            event_type.startswith("object:state-changed:selected")
            and event.detail1
            and AXUtilities.is_menu(event.source)
            and AXUtilities.is_focusable(event.source)
        ):
            return True, "Selection change in focused menu"

        # This condition appears with gnome-screensaver-dialog. See bug 530368.
        if (
            event_type.startswith("object:state-changed:showing")
            and AXUtilities.is_panel(event.source)
            and AXUtilities.is_modal(event.source)
        ):
            return True, "Modal panel is showing."

        return False, "No reason found to activate a different script."

    def _event_source_is_dead(self, event: Atspi.Event) -> bool:
        if AXObject.is_dead(event.source):
            tokens = ["EVENT MANAGER: source of", event.type, "is dead"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def _should_process_event(
        self,
        event: Atspi.Event,
        event_script: default.Script,
        active_script: default.Script,
    ) -> bool:
        """Returns True if this event should be processed."""

        if event_script == active_script:
            msg = f"EVENT MANAGER: Processing {event.type}: script for event is active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if event_script.present_if_inactive:
            msg = f"EVENT MANAGER: Processing {event.type}: script handles events when inactive"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if "accessible-value" in event.type and AXUtilities.is_progress_bar(event.source):
            msg = f"EVENT MANAGER: Processing {event.type}: source is progress bar"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = f"EVENT MANAGER: Not processing {event.type} due to lack of reason"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    @staticmethod
    def _handle_early_event_processing(event: Atspi.Event) -> bool:
        """Handles early event processing. Returns True if the event was fully handled."""

        script_mgr = script_manager.get_manager()
        focus_mgr = focus_manager.get_manager()

        event_type = event.type
        if (
            event_type.startswith("object:children-changed:remove")
            and event.source == AXUtilities.get_desktop()
        ):
            script_mgr.reclaim_scripts()
            return True

        if AXObject.is_dead(event.source) or AXUtilities.is_defunct(event.source):
            tokens = ["EVENT MANAGER: Ignoring defunct object:", event.source]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            if event_type.startswith("window:de") and focus_mgr.get_active_window() == event.source:
                focus_mgr.clear_state("Active window is dead or defunct")
                script_mgr.set_active_script(None, "Active window is dead or defunct")
            return True

        if event_type.startswith("window:") and event_type.endswith("destroy"):
            script_mgr.reclaim_scripts()

        if AXUtilities.is_iconified(event.source):
            tokens = ["EVENT MANAGER: Ignoring iconified object:", event.source]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def _find_listener(script: default.Script, event_type: str):
        """Returns the listener for event_type, or None."""

        listener = script.listeners.get(event_type)
        if listener is not None:
            return listener

        # The listener can be None if the event type has a suffix such as "system".
        for key, value in script.listeners.items():
            if event_type.startswith(key):
                return value

        return None

    def _process_object_event(self, event: Atspi.Event) -> None:
        """Handles all object events destined for scripts."""

        if self._is_obsoleted_by(event) or self._handle_early_event_processing(event):
            return

        if debug.debugLevel <= debug.LEVEL_INFO:
            msg = AXUtilitiesDebugging.object_event_details_as_string(event)
            debug.print_message(debug.LEVEL_INFO, msg, True)

        script_mgr = script_manager.get_manager()
        active_script = script_mgr.get_active_script()
        script = self._get_script_for_event(event, active_script)
        if not script:
            msg = "ERROR: Could not get script for event"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if script != active_script:
            set_new_active_script, reason = self._is_activatable_event(event, script)
            msg = f"EVENT MANAGER: Change active script: {set_new_active_script} ({reason})"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            if set_new_active_script:
                script_mgr.set_active_script(script, reason)
                active_script = script

        try:
            assert active_script is not None
        except AssertionError:
            # TODO - JD: Under what conditions could this actually happen?
            msg = "ERROR: Active script is None"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            if not self._should_process_event(event, script, active_script):
                return

        listener = self._find_listener(script, event.type)
        if listener is None:
            msg = f"EVENT MANAGER: No listener for event type {event.type}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        listener(event)


_manager: EventManager = EventManager()


def get_manager() -> EventManager:
    """Returns the Event Manager singleton."""
    return _manager
