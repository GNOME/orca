# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Provides live region support."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import copy
import enum
import heapq
import time
from typing import TYPE_CHECKING

import gi
from gi.repository import GLib

from . import cmdnames
from . import dbus_service
from . import debug
from . import focus_manager
from . import input_event
from . import keybindings
from . import messages
from . import script_manager
from . import settings
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class LivePoliteness(enum.Enum):
    """Live region politeness levels."""

    ASSERTIVE = (0, "assertive")
    POLITE = (1, "polite")
    OFF = (2, "off")

    def __init__(self, priority: int, name_str: str) -> None:
        self.priority = priority
        self.name_str = name_str

    def from_string(self, value: str | None) -> LivePoliteness:
        """Convert string to LivePoliteness enum."""

        for member in LivePoliteness:
            if member.name_str == value:
                return member
        return LivePoliteness.OFF

    def to_string(self) -> str:
        """Convert LivePoliteness enum to string."""

        return self.name_str


class LiveRegionMessage:
    """Represents a live region message in the queue."""

    def __init__(
        self,
        text: str,
        politeness: LivePoliteness,
        obj: Atspi.Accessible,
        timestamp: float | None = None
    ) -> None:
        self.text = text
        self.politeness = politeness
        self.obj = obj
        self.timestamp = timestamp if timestamp is not None else time.time()

    def __lt__(self, other: LiveRegionMessage) -> bool:
        """Compare messages for priority queue ordering."""

        # ASSERTIVE=0 before POLITE=1
        if self.politeness.priority != other.politeness.priority:
            return self.politeness.priority < other.politeness.priority

        # Older before newer
        return self.timestamp < other.timestamp

    def is_duplicate_of(self, other: LiveRegionMessage | None) -> bool:
        """Check if this message is a duplicate of another based on text and time."""

        if other is None:
            return False
        if self.text != other.text:
            return False
        time_delta = self.timestamp - other.timestamp
        return time_delta <= 0.25


class LiveRegionMessageQueue:
    """Holds the prioritized queue of live region messages."""

    # Seconds a message is held in the queue before it is discarded.
    MSG_KEEPALIVE_TIME = 45

    def __init__(self, max_size: int) -> None:
        self._heap: list[LiveRegionMessage] = []
        self._max_size = max_size

    def enqueue(self, message: LiveRegionMessage) -> None:
        """Add a new element to the queue according to priority and timestamp."""

        heapq.heappush(self._heap, message)

        if len(self._heap) > self._max_size:
            self._heap.sort()
            self._heap.pop()
            heapq.heapify(self._heap)

    def dequeue(self) -> LiveRegionMessage | None:
        """Get the highest priority element from the queue."""

        if not self._heap:
            return None

        return heapq.heappop(self._heap)

    def clear(self) -> None:
        """Clear the queue."""

        self._heap.clear()

    def purge_by_keep_alive(self) -> None:
        """Purge items from the queue that are older than the keepalive time."""

        current_time = time.time()

        self._heap = [
            msg for msg in self._heap
            if msg.timestamp + self.MSG_KEEPALIVE_TIME > current_time
        ]
        heapq.heapify(self._heap)

    def purge_by_priority(self, priority: LivePoliteness) -> None:
        """Purge items from the queue that have a lower than or equal priority to priority."""

        self._heap = [
            msg for msg in self._heap
            if msg.politeness.priority < priority.priority
        ]
        heapq.heapify(self._heap)

    def __len__(self) -> int:
        """Return the length of the queue."""
        return len(self._heap)


class LiveRegionPresenter:
    """Presents live region announcements."""

    # Maximum size for message queue and cache
    QUEUE_SIZE = 9

    def __init__(self) -> None:
        self.msg_queue = LiveRegionMessageQueue(max_size=self.QUEUE_SIZE)

        # To make it possible for focus mode to suspend commands without changing
        # the user's preferred setting.
        self._suspended = False

        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

        self.msg_cache: list[str] = []
        self._politeness_overrides: dict[int, LivePoliteness] = {}
        self._restore_overrides: dict[int, LivePoliteness] = {}

        self._last_presented_message: LiveRegionMessage | None = None
        self._monitoring: bool = True
        # Use QUEUE_SIZE as sentinel to indicate "not yet navigating"
        self._current_index: int = self.QUEUE_SIZE

        msg = "LIVE REGION PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("LiveRegionPresenter", self)

    def get_bindings(
        self,
        refresh: bool = False,
        is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the live-region-presenter keybindings."""

        if refresh:
            msg = f"LIVE REGION PRESENTER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("LIVE REGION PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the live-region-presenter handlers."""

        if refresh:
            msg = "LIVE REGION PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the live-region-presenter input event handlers."""

        self._handlers = {}

        self._handlers["toggle_live_region_support"] = \
            input_event.InputEventHandler(
                self.toggle_monitoring,
                cmdnames.LIVE_REGIONS_MONITOR,
                enabled = True)

        self._handlers["present_previous_live_region_message"] = \
            input_event.InputEventHandler(
                self.present_previous_live_region_message,
                cmdnames.LIVE_REGIONS_PREVIOUS,
                enabled = not self._suspended)

        self._handlers["advance_live_politeness"] = \
            input_event.InputEventHandler(
                self._advance_politeness_level,
                cmdnames.LIVE_REGIONS_ADVANCE_POLITENESS,
                enabled = not self._suspended)

        self._handlers["toggle_live_region_presentation"] = \
            input_event.InputEventHandler(
                self.toggle_live_region_presentation,
                cmdnames.LIVE_REGIONS_ARE_ANNOUNCED,
                enabled = not self._suspended)

        self._handlers["present_next_live_region_message"] = \
            input_event.InputEventHandler(
                self.present_next_live_region_message,
                cmdnames.LIVE_REGIONS_NEXT,
                enabled = not self._suspended)

        msg = f"LIVE REGION PRESENTER: Handlers set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the live-region-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "backslash",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["toggle_live_region_support"],
                1,
                True))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["advance_live_politeness"],
                1,
                not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["toggle_live_region_presentation"],
                1,
                not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["present_previous_live_region_message"],
                1,
                not self._suspended))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["present_next_live_region_message"],
                1,
                not self._suspended))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

        msg = f"LIVE REGION PRESENTER: Bindings set up. Suspended: {self._suspended}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def refresh_bindings_and_grabs(self, script: default.Script, reason: str = "") -> None:
        """Refreshes live region bindings and grabs for script."""

        msg = "LIVE REGION PRESENTER: Refreshing bindings and grabs"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.remove(binding, include_grabs=True)

        self._handlers = self.get_handlers(True)
        self._bindings = self.get_bindings(True)

        for binding in self._bindings.key_bindings:
            script.key_bindings.add(binding, include_grabs=not self._suspended)

    def suspend_commands(self, script: default.Script, suspended: bool, reason: str = "") -> None:
        """Suspends live region commands independent of the enabled setting."""

        if suspended == self._suspended:
            return

        msg = f"LIVE REGION PRESENTER: Commands suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._suspended = suspended
        self.refresh_bindings_and_grabs(script, f"Suspended changed to {suspended}")

    def reset(self) -> None:
        """Reset the live region presenter."""

        self._politeness_overrides = {}

    def handle_event(self, script: default.Script, event: Atspi.Event) -> None:
        """Handles a live region event."""

        if not self.is_presentable_live_region_event(script, event):
            return

        politeness = self._get_live_event_type(event.source)
        if politeness == LivePoliteness.OFF:
            return
        if politeness == LivePoliteness.ASSERTIVE:
            self.msg_queue.purge_by_priority(LivePoliteness.POLITE)

        text = self._get_message(event)
        if not text:
            return

        message = LiveRegionMessage(
            text=text,
            politeness=politeness,
            obj=event.source
        )

        # Check for duplicate and update tracking.
        if message.is_duplicate_of(self._last_presented_message):
            msg = f"LIVE REGION PRESENTER: Ignoring duplicate message: {text}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._last_presented_message = message

        if len(self.msg_queue) == 0:
            GLib.timeout_add(100, self._pump_messages)

        self.msg_queue.enqueue(message)

    def is_presentable_live_region_event(self, script: default.Script,event: Atspi.Event) -> bool:
        """Returns whether the given event is a presentable live region event."""

        # Live regions were invented to work with web content. At the time the ARIA working group
        # invented them, they failed to ask for the creation of ATK/AT-SPI API that would make it
        # possible to distinguish live region events from DOM mutations. This, combined with what
        # is stated in the Core-AAM, means that user agents are firing both children changed and
        # text changed events which can cause us to double-present live region messages. Based on
        # testing of various user agents, we sometimes do not receive children changed events, but
        # do receive text changed events. Therefore we only pay attention to the latter here.
        # TODO - JD: Now that we have the "notification" event in AT-SPI, handle that here is well.
        if not event.type.startswith("object:text-changed:insert"):
            msg = f"LIVE REGION PRESENTER: Ignoring event of type {event.type}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self.get_is_enabled():
            msg = "LIVE REGION PRESENTER: Live region presenter is not enabled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not AXUtilities.is_live_region(event.source):
            msg = "LIVE REGION PRESENTER: Event is not from a live region."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self.get_present_live_region_from_inactive_tab():
            this_doc = script.utilities.get_top_level_document_for_object(event.source)
            active_doc = script.utilities.active_document()
            if this_doc and active_doc and this_doc != active_doc:
                tokens = ["LIVE REGION PRESENTER: Event from", this_doc,
                          "but active document is", active_doc]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

        alert = AXObject.find_ancestor(event.source, AXUtilities.is_aria_alert)
        if alert and AXUtilities.get_focused_object(alert) == event.source:
            msg = "LIVE REGION PRESENTER: Focused source will be presented as part of alert"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def _pump_messages(self) -> bool:
        """Presents queued messages."""

        if len(self.msg_queue) > 0:
            debug.print_message(debug.LEVEL_INFO, "\nvvvvv PRESENT LIVE REGION MESSAGE vvvvv")
            self.msg_queue.purge_by_keep_alive()
            message = self.msg_queue.dequeue()
            if message is None:
                return False

            if self._monitoring:
                if script := script_manager.get_manager().get_active_script():
                    script.present_message(message.text)
            else:
                msg = "INFO: Not presenting message because monitoring is off"
                debug.print_message(debug.LEVEL_INFO, msg, True)

            self._cache_message(message.text)

        # We still want to maintain our queue if we are not monitoring.
        if not self._monitoring:
            self.msg_queue.purge_by_keep_alive()

        msg = f"LIVE REGIONS: messages in queue: {len(self.msg_queue)}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        debug.print_message(debug.LEVEL_INFO, "^^^^^ PRESENT LIVE REGION MESSAGE ^^^^^\n")
        return len(self.msg_queue) > 0

    def _advance_politeness_level(
        self,
        script: default.Script,
        _event: input_event.InputEvent
    ) -> bool:
        """Advance the politeness level of the given object"""

        if not self.get_is_enabled():
            script.present_message(messages.LIVE_REGIONS_SUPPORT_DISABLED)
            return False

        obj = focus_manager.get_manager().get_locus_of_focus()
        object_id = self._get_object_id(obj)
        try:
            # The current priority is either a previous override or the live property. If an
            # exception is thrown, an override for this object has never occurred or the object
            # does not have live markup. In either case, set the override to LivePoliteness.OFF.
            cur_priority = self._politeness_overrides[object_id]
        except KeyError:
            attrs = AXObject.get_attributes_dict(obj, False)
            cur_priority = LivePoliteness.OFF.from_string(attrs.get("container-live"))

        if cur_priority == LivePoliteness.OFF:
            self._politeness_overrides[object_id] = LivePoliteness.POLITE
            script.present_message(messages.LIVE_REGIONS_LEVEL_POLITE)
        elif cur_priority == LivePoliteness.POLITE:
            self._politeness_overrides[object_id] = LivePoliteness.ASSERTIVE
            script.present_message(messages.LIVE_REGIONS_LEVEL_ASSERTIVE)
        elif cur_priority == LivePoliteness.ASSERTIVE:
            self._politeness_overrides[object_id] = LivePoliteness.OFF
            script.present_message(messages.LIVE_REGIONS_LEVEL_OFF)
        return True

    def go_last_live_region(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None
    ) -> bool:
        """Move to the last announced live region and speak the contents of that object."""

        if self._last_presented_message is None:
            msg = "LIVE REGION PRESENTER: No last presented live region message."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self.get_is_enabled():
            script.present_message(messages.LIVE_REGIONS_SUPPORT_DISABLED)
            return False

        obj = self._last_presented_message.obj
        script.utilities.set_caret_position(obj, 0)
        script.speak_contents(script.utilities.get_object_contents_at_offset(obj, 0))
        return True

    def present_previous_live_region_message(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None
    ) -> bool:
        """Presents the previous live region message."""

        if not self.get_is_enabled():
            script.present_message(messages.LIVE_REGIONS_SUPPORT_DISABLED)
            return False

        tokens = ["LIVE REGION PRESENTER: present_previous_live_region_message. Script:", script,
                  "Current index:", self._current_index]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.msg_cache:
            script.present_message(messages.LIVE_REGIONS_NO_MESSAGES)
            return True

        oldest_index = -len(self.msg_cache)
        if self._current_index == oldest_index:
            script.present_message(messages.LIVE_REGIONS_LIST_TOP)
            message = self.msg_cache[oldest_index]
            script.present_message(message)
            return True

        if self._current_index >= 0:
            self._current_index = -1
        else:
            self._current_index -= 1

        message = self.msg_cache[self._current_index]
        script.present_message(message)
        return True

    def present_next_live_region_message(
        self,
        script: default.Script,
        _event: input_event.InputEvent | None
    ) -> bool:
        """Presents the next live region message."""

        if not self.get_is_enabled():
            script.present_message(messages.LIVE_REGIONS_SUPPORT_DISABLED)
            return False

        tokens = ["LIVE REGION PRESENTER: present_next_live_region_message. Script:", script,
                  "Current index:", self._current_index]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.msg_cache:
            script.present_message(messages.LIVE_REGIONS_NO_MESSAGES)
            return True

        oldest_index = -len(self.msg_cache)
        if self._current_index == -1:
            script.present_message(messages.LIVE_REGIONS_LIST_BOTTOM)
            message = self.msg_cache[-1]
            script.present_message(message)
            return True

        if self._current_index >= 0:
            self._current_index = -1
        elif self._current_index < oldest_index:
            self._current_index = oldest_index
        else:
            self._current_index += 1

        message = self.msg_cache[self._current_index]
        script.present_message(message)
        return True

    def get_is_enabled(self) -> bool:
        """Returns whether live region support is enabled."""

        return settings.enableLiveRegions

    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether live region support is enabled."""

        if self.get_is_enabled() == value:
            return True

        msg = f"LIVE REGION PRESENTER: Setting enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.enableLiveRegions = value
        return True

    def get_present_live_region_from_inactive_tab(self) -> bool:
        """Returns whether live region messages are presented from inactive tabs."""

        return settings.presentLiveRegionFromInactiveTab

    def set_present_live_region_from_inactive_tab(self, value: bool) -> bool:
        """Sets whether live region messages are presented from inactive tabs."""

        if self.get_present_live_region_from_inactive_tab() == value:
            return True

        msg = f"LIVE REGION PRESENTER: Setting presentLiveRegionFromInactiveTab to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.presentLiveRegionFromInactiveTab = value
        return True

    def toggle_monitoring(self, script: default.Script, _event: input_event.InputEvent) -> bool:
        """Toggles live region monitoring on and off."""

        if not self.get_is_enabled():
            self.set_is_enabled(True)
            script.present_message(messages.LIVE_REGIONS_ENABLED)
            return True

        self.set_is_enabled(False)
        self.flush_messages()
        self._current_index = self.QUEUE_SIZE
        script.present_message(messages.LIVE_REGIONS_DISABLED)
        return True

    def toggle_live_region_presentation(
        self,
        script: default.Script,
        _event: input_event.InputEvent
    ) -> bool:
        """Toggles between presenting live regions and not presenting them."""

        if not self.get_is_enabled():
            script.present_message(messages.LIVE_REGIONS_SUPPORT_DISABLED)
            return False

        document = script.utilities.active_document()

        # The user is currently monitoring live regions but now wants to
        # change all live region politeness on page to LivePoliteness.OFF.
        if self._monitoring:
            script.present_message(messages.LIVE_REGIONS_ALL_OFF)
            self.msg_queue.clear()

            self._restore_overrides = copy.copy(self._politeness_overrides)
            for override in self._politeness_overrides:
                self._politeness_overrides[override] = LivePoliteness.OFF

            matches = AXUtilities.find_all_live_regions(document)
            for match in matches:
                objectid = self._get_object_id(match)
                self._politeness_overrides[objectid] = LivePoliteness.OFF

            self._monitoring = False
            return True

        # The user wants to restore politeness levels,
        for key, value in self._restore_overrides.items():
            self._politeness_overrides[key] = value
        script.present_message(messages.LIVE_REGIONS_ALL_RESTORED)
        self._monitoring = True
        return True

    def _find_container(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        def is_container(x: Atspi.Accessible) -> bool:
            attrs = AXObject.get_attributes_dict(x, False)
            return bool(attrs.get("atomic"))

        container = AXObject.find_ancestor_inclusive(obj, is_container)
        tokens = ["LIVE REGION PRESENTER: Container for", obj, "is", container]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return container

    def _get_message(self, event: Atspi.Event) -> str | None:
        """Gets the message associated with a given live event."""

        attrs = AXObject.get_attributes_dict(event.source, False)
        content = ""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return None

        if attrs.get("container-atomic") != "true":
            if "\ufffc" not in event.any_data:
                content = event.any_data
            else:
                content = script.utilities.expand_eocs(
                    event.source, event.detail1, event.detail1 + event.detail2)
        else:
            container = self._find_container(event.source)
            content = script.utilities.expand_eocs(container)

        content = content.strip()
        if not content:
            return None

        name = AXObject.get_name(event.source).strip()
        if name and name != content:
            content = f"{name}. {content}"
        return content

    def flush_messages(self) -> None:
        """Flushes the message queue."""

        self.msg_queue.clear()

    def _cache_message(self, utts: str) -> None:
        """Cache a message in our cache list of length QUEUE_SIZE"""

        self.msg_cache.append(utts)
        if len(self.msg_cache) > self.QUEUE_SIZE:
            self.msg_cache.pop(0)

    def _get_live_event_type(self, obj: Atspi.Accessible) -> LivePoliteness:
        """Returns the live politeness setting for a given object."""

        object_id = self._get_object_id(obj)
        if object_id in self._politeness_overrides:
            return self._politeness_overrides[object_id]

        attrs = AXObject.get_attributes_dict(obj, False)
        return LivePoliteness.OFF.from_string(attrs.get("container-live"))

    def _get_object_id(self, obj: Atspi.Accessible) -> int:
        """Returns the HTML 'id' or a path to the object is an HTML id is unavailable."""

        attrs = AXObject.get_attributes_dict(obj, False)
        return hash (attrs.get("id") or obj)

_presenter: LiveRegionPresenter = LiveRegionPresenter()

def get_presenter() -> LiveRegionPresenter:
    """Returns the Live Region Presenter singleton."""

    return _presenter
