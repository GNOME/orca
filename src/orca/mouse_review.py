# Mouse reviewer for Orca
#
# Copyright 2008 Eitan Isaacson
# Copyright 2016 Igalia, S.L.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals

"""Mouse review mode."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Eitan Isaacson" \
                "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import math
import os
import time
from collections import deque
from typing import TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

_MOUSE_REVIEW_CAPABLE = False
try:
    if os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland":
        gi.require_version("Wnck", "3.0")
        from gi.repository import Wnck
        _MOUSE_REVIEW_CAPABLE = Wnck.Screen.get_default() is not None
except Exception:
    pass

from . import cmdnames
from . import dbus_service
from . import debug
from . import focus_manager
from . import keybindings
from . import input_event
from . import messages
from . import script_manager
from . import settings_manager
from . import speech_and_verbosity_manager
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from .scripts import default


class _StringContext:
    """The textual information associated with an _ItemContext."""

    def __init__(
        self,
        obj: Atspi.Accessible,
        script: default.Script | None = None,
        string: str = "",
        start: int = 0,
        end: int = 0
    ) -> None:
        self._obj = obj
        self._script = script
        self._string = string
        self._start = start
        self._end = end
        self._rect = AXText.get_range_rect(obj, start, end)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _StringContext):
            return False
        return other is not None \
            and self._obj == other._obj \
            and self._string == other._string \
            and self._start == other._start \
            and self._end == other._end

    def is_substring_of(self, other: _StringContext | None) -> bool:
        """Returns True if this is a substring of other."""

        if other is None:
            return False

        if not (self._obj and other.get_object()):
            return False

        this_box = self.get_bounding_box()
        if this_box == (0, 0, 0, 0):
            return False

        other_box = other.get_bounding_box()
        if other_box == (0, 0, 0, 0):
            return False

        # We get various and sundry results for the bounding box if the implementor
        # included newline characters as part of the word or line at offset. Try to
        # detect this and adjust the bounding boxes before getting the intersection.
        if this_box[3] != other_box[3] and self._obj == other.get_object():
            this_newline_count = self._string.count("\n")
            if this_newline_count and this_box[3] / this_newline_count == other_box[3]:
                this_box = *this_box[0:3], other_box[3]

        this_rect = Atspi.Rect()
        this_rect.x, this_rect.y, this_rect.width, this_rect.height = this_box
        other_rect = Atspi.Rect()
        other_rect.x, other_rect.y, other_rect.width, other_rect.height = other_box
        if AXComponent.get_rect_intersection(this_rect, other_rect) != this_rect:
            return False

        if not (self._string and self._string.strip() in other.get_string()):
            return False

        msg = f"MOUSE REVIEW: '{self._string}' is substring of '{other.get_string()}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def get_bounding_box(self) -> tuple[int, int, int, int]:
        """Returns the bounding box associated with this context's range."""

        return self._rect.x, self._rect.y, self._rect.width, self._rect.height

    def get_object(self) -> Atspi.Accessible:
        """Returns the accessible object associated with this context."""

        return self._obj

    def get_string(self) -> str:
        """Returns the string associated with this context."""

        return self._string

    def present(self) -> bool:
        """Presents this context to the user."""

        if not self._script:
            msg = "MOUSE REVIEW: Not presenting due to lack of script"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self._string:
            msg = "MOUSE REVIEW: Not presenting due to lack of string"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        voice = self._script.speech_generator.voice(obj=self._obj, string=self._string)
        manager = speech_and_verbosity_manager.get_manager()
        string = manager.adjust_for_presentation(self._obj, self._string)

        focus_manager.get_manager().emit_region_changed(
            self._obj, self._start, self._end, focus_manager.MOUSE_REVIEW)
        self._script.speak_message(string, voice=voice, interrupt=False)
        self._script.display_message(self._string, -1)
        return True


class _ItemContext:
    """Holds all the information of the item at a specified point."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        obj: Atspi.Accessible | None = None,
        granularity=None,
        frame: Atspi.Accessible | None = None,
        script: default.Script | None = None
    ) -> None:
        self._x = x
        self._y = y
        self._obj = obj
        self._granularity = granularity
        self._frame = frame
        self._script = script
        self._string = self._get_string_context()
        self._time = time.time()
        self._rect = AXComponent.get_rect(obj)

    def __eq__(self, other) -> bool:
        return other is not None \
            and self._frame == other._frame \
            and self._obj == other._obj \
            and self._string == other._string

    def _treat_as_duplicate(self, prior: _ItemContext) -> bool:
        if self._obj != prior.get_object() or self._frame != prior.get_frame():
            msg = "MOUSE REVIEW: Not a duplicate: different objects"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self.get_string() and prior.get_string() and not self._is_substring_of(prior):
            msg = "MOUSE REVIEW: Not a duplicate: not a substring of"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        prior_x, prior_y = prior.get_bounding_box()[0:2]
        if self._x == prior_x and self._y == prior_y:
            msg = "MOUSE REVIEW: Treating as duplicate: mouse didn't move"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        interval = self._time - prior.get_time()
        if interval > 0.5:
            msg = f"MOUSE REVIEW: Not a duplicate: was {interval:.2f}s ago"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "MOUSE REVIEW: Treating as duplicate"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def _treat_as_single_object(self) -> bool:
        return AXText.is_whitespace_or_empty(self._obj)

    def _get_string_context(self) -> _StringContext:
        """Returns the _StringContext associated with the specified point."""

        if not (self._script and self._obj):
            return _StringContext(self._obj)

        if self._treat_as_single_object():
            return _StringContext(self._obj, self._script)

        if self._granularity == Atspi.TextGranularity.WORD:
            string, start, end = AXText.get_word_at_point(self._obj, self._x, self._y)
        else:
            string, start, end = AXText.get_line_at_point(self._obj, self._x, self._y)

        if string:
            string = self._script.utilities.expand_eocs(self._obj, start, end)

        return _StringContext(self._obj, self._script, string, start, end)

    def _get_container(self):
        def is_container(x):
            return AXUtilities.is_dialog_or_window(x) \
                or AXUtilities.is_layered_pane(x) \
                or AXUtilities.is_menu(x) \
                or AXUtilities.is_page_tab(x) \
                or AXUtilities.is_tool_bar(x)
        return AXObject.find_ancestor(self._obj, is_container)

    def _is_substring_of(self, other: _ItemContext) -> bool:
        """Returns True if this is a substring of other."""

        return self._string.is_substring_of(other.get_string_context())

    def get_object(self) -> Atspi.Accessible | None:
        """Returns the accessible object associated with this context."""

        return self._obj

    def get_frame(self) -> Atspi.Accessible | None:
        """Returns the frame associated with this context."""

        return self._frame

    def get_bounding_box(self) -> tuple[int, int, int, int]:
        """Returns the bounding box associated with this context."""

        x, y, width, height = self._string.get_bounding_box()
        if not (width or height):
            return self._rect.x, self._rect.y, self._rect.width, self._rect.height

        return x, y, width, height

    def get_string(self) -> str:
        """Returns the string associated with this context."""

        return self._string.get_string()

    def get_string_context(self) -> _StringContext:
        """Returns the string context associated with this context."""

        return self._string

    def get_time(self) -> float:
        """Returns the time associated with this context."""

        return self._time

    def _is_inline_child(self, prior: _ItemContext) -> bool:
        prior_obj = prior.get_object()
        if not self._obj or not prior_obj:
            return False

        if AXObject.get_parent(prior_obj) != self._obj:
            return False

        if self._treat_as_single_object():
            return False

        return AXUtilities.is_link(prior_obj)

    def present(self, prior: _ItemContext) -> bool:
        """Presents this context to the user."""

        if self == prior or self._treat_as_duplicate(prior):
            msg = "MOUSE REVIEW: Not presenting due to no change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        prior_obj = prior.get_object()
        prior_x, prior_y = prior.get_bounding_box()[0:2]
        interrupt = self._obj and self._obj != prior_obj \
            or math.sqrt((self._x - prior_x)**2 + (self._y - prior_y)**2) > 25

        assert self._script, "Script must not be None"
        if interrupt:
            self._script.interrupt_presentation()

        if self._frame and self._frame != prior.get_frame():
            self._script.present_object(self._frame,
                                        alreadyFocused=True,
                                        inMouseReview=True,
                                        interrupt=True)

        if self._obj and self._obj != prior_obj and not self._is_inline_child(prior):
            prior_obj = prior_obj or self._get_container()
            focus_manager.get_manager().emit_region_changed(
                self._obj, mode=focus_manager.MOUSE_REVIEW)
            self._script.present_object(self._obj, priorObj=prior_obj, inMouseReview=True)
            if self._string.get_string() == AXObject.get_name(self._obj):
                return True
            if not (AXUtilities.is_editable(self._obj) or AXUtilities.is_terminal(self._obj)):
                return True
            if AXUtilities.is_table_cell(self._obj):
                text = AXText.get_all_text(self._obj) or AXObject.get_name(self._obj)
                if self._string.get_string() == text:
                    return True

        if self._string.get_string() != prior.get_string() and self._string.present():
            return True

        return True


class MouseReviewer:
    """Main class for the mouse-review feature."""

    def __init__(self) -> None:
        self._active: bool = self.get_is_enabled()
        self._current_mouse_over: _ItemContext = _ItemContext()
        self._workspace = None
        self._windows: list[Wnck.Window] = []
        self._all_windows: list[Wnck.Window] = []
        self._handler_ids: dict[int, Wnck.Screen] = {}
        self._event_listener: Atspi.EventListener = Atspi.EventListener.new(self._listener)
        self.in_mouse_event: bool = False
        self._event_queue: deque = deque()
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()

        if not _MOUSE_REVIEW_CAPABLE:
            msg = "MOUSE REVIEW ERROR: Wnck is not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._active = False
            return

        msg = "MOUSE REVIEW: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("MouseReviewer", self)
        if not self._active:
            return

        self.activate()

    def get_bindings(self, refresh: bool = False, is_desktop: bool = True):
        """Returns the mouse-review keybindings."""

        if refresh:
            msg = f"MOUSE REVIEW: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("MOUSE REVIEW: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the mouse-review handlers."""

        if refresh:
            msg = "MOUSE REVIEW: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the mouse-review input event handlers."""

        self._handlers = {}

        self._handlers["toggleMouseReviewHandler"] = \
            input_event.InputEventHandler(
                self.toggle,
                cmdnames.MOUSE_REVIEW_TOGGLE)

        msg = "MOUSE REVIEW: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the mouse-review key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["toggleMouseReviewHandler"]))

        msg = "MOUSE REVIEW: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def activate(self) -> None:
        """Activates mouse review."""

        if not _MOUSE_REVIEW_CAPABLE:
            msg = "MOUSE REVIEW ERROR: Wnck is not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._active = False
            return

        # Set up the initial object as the one with the focus to avoid
        # presenting irrelevant info the first time.
        obj = focus_manager.get_manager().get_locus_of_focus()
        script = None
        frame = None
        if obj:
            script = script_manager.get_manager().get_script(AXUtilities.get_application(obj), obj)
        if script:
            frame = script.utilities.top_level_object(obj)
        self._current_mouse_over = _ItemContext(obj=obj, frame=frame, script=script)

        self._event_listener.register("mouse:abs")
        screen = Wnck.Screen.get_default()
        if screen is None:
            self._active = False
            return

        # On first startup windows and workspace are likely to be None,
        # but the signals we connect to will get emitted when proper values
        # become available;  but in case we got disabled and re-enabled we
        # have to get the initial values manually.
        stacked = screen.get_windows_stacked()
        if stacked:
            stacked.reverse()
            self._all_windows = stacked
        self._workspace = screen.get_active_workspace()
        if self._workspace:
            self._update_workspace_windows()

        i = screen.connect("window-stacking-changed", self._on_stacking_changed)
        self._handler_ids[i] = screen
        i = screen.connect("active-workspace-changed", self._on_workspace_changed)
        self._handler_ids[i] = screen
        self._active = True

    def deactivate(self) -> None:
        """Deactivates mouse review."""

        try:
            self._event_listener.deregister("mouse:abs")
        except GLib.GError as error:
            msg = f"MOUSE REVIEW: Exception deregistering 'mouse:abs' listener: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        for key, value in self._handler_ids.items():
            value.disconnect(key)
        self._handler_ids = {}
        self._workspace = None
        self._windows = []
        self._all_windows = []
        self._event_queue.clear()
        self._active = False

    def get_current_item(self):
        """Returns the accessible object being reviewed."""

        if not _MOUSE_REVIEW_CAPABLE:
            return None

        if not self._active:
            return None

        obj = self._current_mouse_over.get_object()

        if time.time() - self._current_mouse_over.get_time() > 0.1:
            tokens = ["MOUSE REVIEW: Treating", obj, "as stale"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return obj

    @dbus_service.getter
    def get_is_enabled(self) -> bool:
        """Returns whether mouse review is enabled (requires Wnck)."""

        return settings_manager.get_manager().get_setting("enableMouseReview")

    @dbus_service.setter
    def set_is_enabled(self, value: bool) -> bool:
        """Sets whether mouse review is enabled (requires Wnck)."""

        if not _MOUSE_REVIEW_CAPABLE:
            msg = "MOUSE REVIEW ERROR: Wnck is not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = f"MOUSE REVIEW: Setting enable mouse review to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if value == self._active:
            return True

        settings_manager.get_manager().set_setting("enableMouseReview", value)
        if value:
            self.activate()
        else:
            self.deactivate()

        return True

    @dbus_service.command
    def toggle(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggle mouse reviewing on or off (requires Wnck)."""

        tokens = ["MOUSE REVIEW: Toggle. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        new_state = not self._active
        if not self.set_is_enabled(new_state):
            return False

        if notify_user:
            if new_state:
                msg = messages.MOUSE_REVIEW_ENABLED
            else:
                msg = messages.MOUSE_REVIEW_DISABLED
            script.present_message(msg)

        return True

    def _update_workspace_windows(self) -> None:
        self._windows = [w for w in self._all_windows
                         if w.is_on_workspace(self._workspace)]

    def _on_stacking_changed(self, screen) -> None:
        """Callback for Wnck's window-stacking-changed signal."""

        stacked = screen.get_windows_stacked()
        stacked.reverse()
        self._all_windows = stacked
        if self._workspace:
            self._update_workspace_windows()

    def _on_workspace_changed(self, screen, _prev_ws=None) -> None:
        """Callback for Wnck's active-workspace-changed signal."""

        self._workspace = screen.get_active_workspace()
        self._update_workspace_windows()

    def _accessible_window_at_point(self, point_x: int, point_y: int) -> tuple[object, int, int]:
        """Returns the accessible window and window based coordinates for the screen coordinates."""

        window = None
        for w in self._windows:
            if w.is_minimized():
                continue

            x, y, width, height = w.get_client_window_geometry()
            if x <= point_x <= x + width and y <= point_y <= y + height:
                window = w
                break

        if not window:
            return None, -1, -1

        window_app = window.get_application()
        if not window_app:
            return None, -1, -1

        app = AXUtilities.get_application_with_pid(window_app.get_pid())
        if not app:
            return None, -1, -1

        # Adjust the pointer screen coordinates to be relative to the window. This is
        # needed because we won't be able to get the screen coordinates in Wayland.
        relative_x = point_x - x
        relative_y = point_y - y

        candidates = list(AXObject.iter_children(
            app, lambda x: AXComponent.object_contains_point(x, relative_x, relative_y)))
        if len(candidates) == 1:
            return candidates[0], relative_x, relative_y

        name = window.get_name()
        matches = [o for o in candidates if AXObject.get_name(o) == name]
        if len(matches) == 1:
            return matches[0], relative_x, relative_y

        matches = [o for o in matches if AXUtilities.is_active(o)]
        if len(matches) == 1:
            return matches[0], relative_x, relative_y

        return None, -1, -1

    def _is_multi_paragraph_object(self, obj) -> bool:
        """Returns True if obj has multiple paragraphs of text."""

        string = AXText.get_all_text(obj)
        chunks = list(filter(lambda x: x.strip(), string.split("\n\n")))
        return len(chunks) > 1

    def _on_mouse_moved(self, event) -> None:
        """Callback for mouse:abs events."""

        point_x, point_y = event.detail1, event.detail2
        window, window_x, window_y = self._accessible_window_at_point(point_x, point_y)
        tokens = [f"MOUSE REVIEW: Window at ({point_x}, {point_y}) is", window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not window:
            return

        script = script_manager.get_manager().get_script(AXUtilities.get_application(window))
        if not script:
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_dead(focus):
            menu = None
        elif AXUtilities.is_menu(focus):
            menu = focus
        else:
            menu = AXObject.find_ancestor(focus, AXUtilities.is_menu)

        obj = None
        if menu:
            obj = AXComponent.get_descendant_at_point(menu, window_x, window_y)
            tokens = ["MOUSE REVIEW: Object in", menu, f"at ({window_x}, {window_y}) is", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if obj is None:
            obj = AXComponent.get_descendant_at_point(window, window_x, window_y)
            tokens = ["MOUSE REVIEW: Object in", window, f"at ({window_x}, {window_y}) is", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        script = script_manager.get_manager().get_script(AXUtilities.get_application(window), obj)
        if menu and obj and not AXObject.find_ancestor(obj, AXUtilities.is_menu):
            if AXComponent.objects_overlap(obj, menu):
                tokens = ["MOUSE REVIEW:", obj, "believed to be under", menu]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

        granularity = Atspi.TextGranularity.LINE
        _x, y, _width, height = self._current_mouse_over.get_bounding_box()
        if y <= window_y <= y + height and self._current_mouse_over.get_string():
            granularity = Atspi.TextGranularity.WORD

        if len(self._event_queue):
            msg = "MOUSE REVIEW: Mouse moved again."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        new = _ItemContext(window_x, window_y, obj, granularity, window, script)
        if new.present(self._current_mouse_over):
            self._current_mouse_over = new

    def _process_event(self) -> None:
        if not self._event_queue:
            return

        event = self._event_queue.popleft()
        if len(self._event_queue):
            return

        start_time = time.time()
        tokens = ["\nvvvvv PROCESS OBJECT EVENT", event.type, "vvvvv"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, False)

        self.in_mouse_event = True
        self._on_mouse_moved(event)
        self.in_mouse_event = False

        msg = f"TOTAL PROCESSING TIME: {time.time() - start_time:.4f}\n"
        msg += f"^^^^^ PROCESS OBJECT EVENT {event.type} ^^^^^\n"
        debug.print_message(debug.LEVEL_INFO, msg, False)

    def _listener(self, event) -> None:
        """Generic listener for events of interest."""

        if event.type.startswith("mouse:abs"):
            self._event_queue.append(event)
            GLib.timeout_add(50, self._process_event)


_reviewer = MouseReviewer()
def get_reviewer() -> MouseReviewer:
    """Returns the Mouse Reviewer singleton."""

    return _reviewer
