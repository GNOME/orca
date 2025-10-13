# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2023 Igalia, S.L.
#
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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods

"""Module to manage the focused object, window, etc."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import braille
from . import dbus_service
from . import debug
from . import script_manager
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from .input_event import InputEvent
    from .scripts import default

CARET_TRACKING = "caret-tracking"
FOCUS_TRACKING = "focus-tracking"
FLAT_REVIEW = "flat-review"
MOUSE_REVIEW = "mouse-review"
OBJECT_NAVIGATOR = "object-navigator"
SAY_ALL = "say-all"


class FocusManager:
    """Manages the focused object, window, etc."""

    def __init__(self) -> None:
        self._window: Atspi.Accessible | None = None
        self._focus: Atspi.Accessible | None = None
        self._object_of_interest: Atspi.Accessible | None = None
        self._active_mode: str | None = None
        self._last_cell_coordinates: tuple[int, int] = (-1, -1)
        self._last_cursor_position: tuple[Atspi.Accessible | None, int] = (None, -1)
        self._penultimate_cursor_position: tuple[Atspi.Accessible | None, int] = (None, -1)

        msg = "FOCUS MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("FocusManager", self)

    def clear_state(self, reason: str = "") -> None:
        """Clears everything we're tracking."""

        msg = "FOCUS MANAGER: Clearing all state"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._focus = None
        self._window = None
        self._object_of_interest = None
        self._active_mode = None

    def find_focused_object(self) -> Atspi.Accessible | None:
        """Returns the focused object in the active window."""

        result = AXUtilities.get_focused_object(self._window)
        tokens = ["FOCUS MANAGER: Focused object in", self._window, "is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def focus_and_window_are_unknown(self) -> bool:
        """Returns True if we have no knowledge about what is focused."""

        result = self._focus is None and self._window is None
        if result:
            msg = "FOCUS MANAGER: Focus and window are unknown"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        return result

    def focus_is_dead(self) -> bool:
        """Returns True if the locus of focus is dead."""

        if not AXObject.is_dead(self._focus):
            return False

        msg = "FOCUS MANAGER: Focus is dead"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def focus_is_active_window(self) -> bool:
        """Returns True if the locus of focus is the active window."""

        if self._focus is None:
            return False

        return self._focus == self._window

    def focus_is_in_active_window(self) -> bool:
        """Returns True if the locus of focus is inside the current window."""

        return self._focus is not None and AXObject.is_ancestor(self._focus, self._window)

    def emit_region_changed(
        self, obj: Atspi.Accessible,
        start_offset: int | None = None,
        end_offset: int | None = None,
        mode: str | None = None
    ) -> None:
        """Notifies interested clients that the current region of interest has changed."""

        if start_offset is None:
            start_offset = 0
        if end_offset is None:
            end_offset = start_offset
        if mode is None:
            mode = FOCUS_TRACKING

        if obj is not None:
            obj.emit("mode-changed::" + mode, 1, "")

        if mode != self._active_mode:
            tokens = ["FOCUS MANAGER: Switching mode from", self._active_mode, "to", mode]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._active_mode = mode
            if mode == FLAT_REVIEW:
                braille.setBrlapiPriority(braille.BRLAPI_PRIORITY_HIGH)
            else:
                braille.setBrlapiPriority()

        tokens = ["FOCUS MANAGER: Region of interest:", obj, f"({start_offset}, {end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if obj is not None:
            obj.emit("region-changed", start_offset, end_offset)

        if obj != self._object_of_interest:
            tokens = ["FOCUS MANAGER: Switching object of interest from",
                      self._object_of_interest, "to", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._object_of_interest = obj

    def in_say_all(self) -> bool:
        """Returns True if we are in say-all mode."""

        return self._active_mode == SAY_ALL

    def get_active_mode_and_object_of_interest(
        self
    ) -> tuple[str | None, Atspi.Accessible | None]:
        """Returns the current mode and associated object of interest"""

        tokens = ["FOCUS MANAGER: Active mode:", self._active_mode,
                  "Object of interest:", self._object_of_interest]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._active_mode, self._object_of_interest

    def get_penultimate_cursor_position(self) -> tuple[Atspi.Accessible | None, int]:
        """Returns the penultimate cursor position as a tuple of (object, offset)."""

        obj, offset = self._penultimate_cursor_position
        tokens = ["FOCUS MANAGER: Penultimate cursor position:", obj, offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return obj, offset

    def get_last_cursor_position(self) -> tuple[Atspi.Accessible | None, int]:
        """Returns the last cursor position as a tuple of (object, offset)."""

        obj, offset = self._last_cursor_position
        tokens = ["FOCUS MANAGER: Last cursor position:", obj, offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return obj, offset

    def set_last_cursor_position(self, obj: Atspi.Accessible | None, offset: int) -> None:
        """Sets the last cursor position as a tuple of (object, offset)."""

        tokens = ["FOCUS MANAGER: Setting last cursor position to", obj, offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._penultimate_cursor_position = self._last_cursor_position
        self._last_cursor_position = obj, offset

    def get_last_cell_coordinates(self) -> tuple[int, int]:
        """Returns the last known cell coordinates as a tuple of (row, column)."""

        row, column = self._last_cell_coordinates
        msg = f"FOCUS MANAGER: Last known cell coordinates: row={row}, column={column}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return row, column

    def set_last_cell_coordinates(self, row: int, column: int) -> None:
        """Sets the last known cell coordinates as a tuple of (row, column)."""

        msg = f"FOCUS MANAGER: Setting last cell coordinates to row={row}, column={column}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._last_cell_coordinates = row, column

    def get_locus_of_focus(self) -> Atspi.Accessible | None:
        """Returns the current locus of focus (i.e. the object with visual focus)."""

        tokens = ["FOCUS MANAGER: Locus of focus is", self._focus]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._focus

    def set_locus_of_focus(
        self,
        event: Atspi.Event | None,
        obj: Atspi.Accessible | None,
        notify_script: bool = True,
        force: bool = False
    ) -> None:
        """Sets the locus of focus (i.e., the object with visual focus)."""

        tokens = ["FOCUS MANAGER: Request to set locus of focus to", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        # We clear the cache on the locus of focus because too many apps and toolkits fail
        # to emit the correct accessibility events. We do so recursively on table cells
        # to handle bugs like https://gitlab.gnome.org/GNOME/nautilus/-/issues/3253.
        recursive = AXUtilities.is_table_cell(obj)
        AXObject.clear_cache(obj, recursive, "Setting locus of focus.")
        if not force and obj == self._focus:
            msg = "FOCUS MANAGER: Setting locus of focus to existing locus of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        # We save the current row and column of a newly focused or selected table cell so that on
        # subsequent cell focus/selection we only present the changed location.
        row, column = AXTable.get_cell_coordinates(obj, find_cell=True)
        self.set_last_cell_coordinates(row, column)

        # We save the offset for text objects because some apps and toolkits emit caret-moved events
        # immediately after a text object gains focus, even though the caret has not actually moved.
        # TODO - JD: We should consider making this part of `save_object_info_for_events()` for the
        # motivation described above. However, we need to audit callers that set/get the position
        # before doing so.
        self.set_last_cursor_position(obj, AXText.get_caret_offset(obj))
        AXText.update_cached_selected_text(obj)

        # We save additional information about the object for events that were received at the same
        # time as the prioritized focus-change event so we don't double-present aspects about obj.
        AXUtilities.save_object_info_for_events(obj)

        # TODO - JD: Consider always updating the active script here.
        script = script_manager.get_manager().get_active_script()
        if event and (script and not script.app):
            app = AXUtilities.get_application(event.source)
            script = script_manager.get_manager().get_script(app, event.source)
            script_manager.get_manager().set_active_script(script, "Setting locus of focus")

        old_focus = self._focus
        if AXObject.is_dead(old_focus):
            old_focus = None

        if obj is None:
            msg = "FOCUS MANAGER: New locus of focus is null (being cleared)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._focus = None
            return

        if AXObject.is_dead(obj):
            tokens = ["FOCUS MANAGER: New locus of focus (", obj, ") is dead. Not updating."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        if script is not None:
            if not AXObject.is_valid(obj):
                tokens = ["FOCUS MANAGER: New locus of focus (", obj, ") is invalid. Not updating."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

        tokens = ["FOCUS MANAGER: Changing locus of focus from", old_focus,
                  "to", obj, ". Notify:", notify_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._focus = obj
        self.emit_region_changed(obj, mode=FOCUS_TRACKING)

        if not notify_script:
            return

        if script is None:
            msg = "FOCUS MANAGER: Cannot notify active script because there isn't one"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        script.locus_of_focus_changed(event, old_focus, self._focus)

    def active_window_is_active(self) -> bool:
        """Returns True if the window we think is currently active is actually active."""

        AXObject.clear_cache(self._window, False, "Ensuring the active window is really active.")
        is_active = AXUtilities.is_active(self._window)
        tokens = ["FOCUS MANAGER:", self._window, "is active:", is_active]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return is_active

    def get_active_window(self) -> Atspi.Accessible | None:
        """Returns the currently-active window (i.e. without searching or verifying)."""

        tokens = ["FOCUS MANAGER: Active window is", self._window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
        return self._window

    def set_active_window(
        self,
        frame: Atspi.Accessible | None,
        app: Atspi.Accessible | None = None,
        set_window_as_focus: bool = False,
        notify_script: bool = False
    ) -> None:
        """Sets the active window."""

        tokens = ["FOCUS MANAGER: Request to set active window to", frame]
        if app is not None:
            tokens.extend(["in", app])
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if frame == self._window:
            msg = "FOCUS MANAGER: Setting active window to existing active window"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif frame is None:
            self._window = None
        else:
            self._window = frame

        if set_window_as_focus:
            self.set_locus_of_focus(None, self._window, notify_script)
        elif not (self.focus_is_active_window() or self.focus_is_in_active_window()):
            tokens = ["FOCUS MANAGER: Focus", self._focus, "is not in", self._window]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

            # Don't update the focus to the active window if we can't get to the active window
            # from the focused object. https://bugreports.qt.io/browse/QTBUG-130116
            if not AXObject.has_broken_ancestry(self._focus):
                self.set_locus_of_focus(None, self._window, notify_script=True)

        app = AXUtilities.get_application(self._focus)
        script = script_manager.get_manager().get_script(app, self._focus)
        script_manager.get_manager().set_active_script(script, "Setting active window")

    @dbus_service.command
    def toggle_presentation_mode(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Switches between browse mode and focus mode (web content only)."""

        return script.toggle_presentation_mode(event, document=None, notify_user=notify_user)

    @dbus_service.command
    def toggle_layout_mode(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Switches between object mode and layout mode for line presentation (web content only)."""

        return script.toggle_layout_mode(event, notify_user=notify_user)

    @dbus_service.command
    def enable_sticky_browse_mode(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Enables sticky browse mode (web content only)."""

        return script.enable_sticky_browse_mode(event, force_message=notify_user)

    @dbus_service.command
    def enable_sticky_focus_mode(
        self,
        script: default.Script,
        event: InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Enables sticky focus mode (web content only)."""

        return script.enable_sticky_focus_mode(event, force_message=notify_user)

    @dbus_service.getter
    def get_in_layout_mode(self) -> bool:
        """Returns True if layout mode (as opposed to object mode) is active (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return script.in_layout_mode()
        return False

    @dbus_service.getter
    def get_in_focus_mode(self) -> bool:
        """Returns True if focus mode is active (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return script.in_focus_mode()
        return False

    @dbus_service.getter
    def get_focus_mode_is_sticky(self) -> bool:
        """Returns True if focus mode is active and 'sticky' (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return script.focus_mode_is_sticky()
        return False

    @dbus_service.getter
    def get_browse_mode_is_sticky(self) -> bool:
        """Returns True if browse mode is active and 'sticky' (web content only)."""

        if script := script_manager.get_manager().get_active_script():
            return script.browse_mode_is_sticky()
        return False

_manager: FocusManager = FocusManager()

def get_manager() -> FocusManager:
    """Returns the focus manager singleton."""
    return _manager
