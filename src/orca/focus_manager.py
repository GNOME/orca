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

"""Module to manage the focused object, window, etc."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

from . import braille
from . import debug
from . import script_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities

CARET_TRACKING = "caret-tracking"
FOCUS_TRACKING = "focus-tracking"
FLAT_REVIEW = "flat-review"
MOUSE_REVIEW = "mouse-review"
OBJECT_NAVIGATOR = "object-navigator"
SAY_ALL = "say-all"


class FocusManager:
    """Manages the focused object, window, etc."""

    def __init__(self):
        self._window = None
        self._focus = None
        self._object_of_interest = None
        self._active_mode = None

    def clear_state(self, reason=""):
        """Clears everything we're tracking."""

        msg = "FOCUS MANAGER: Clearing all state"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._focus = None
        self._window = None
        self._object_of_interest = None
        self._active_mode = None

    def find_focused_object(self):
        """Returns the focused object in the active window."""

        result = AXUtilities.get_focused_object(self._window)
        tokens = ["FOCUS MANAGER: Focused object in", self._window, "is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def focus_and_window_are_unknown(self):
        """Returns True if we have no knowledge about what is focused."""

        result = self._focus is None and self._window is None
        if result:
            msg = "FOCUS MANAGER: Focus and window are unknown"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        return result

    def focus_is_dead(self):
        """Returns True if the locus of focus is dead."""

        if not AXObject.is_dead(self._focus):
            return False

        msg = "FOCUS MANAGER: Focus is dead"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def focus_is_active_window(self):
        """Returns True if the locus of focus is the active window."""

        if self._focus is None:
            return False

        return self._focus == self._window

    def focus_is_in_active_window(self):
        """Returns True if the locus of focus is inside the current window."""

        return self._focus is not None and AXObject.is_ancestor(self._focus, self._window)

    def emit_region_changed(self, obj, start_offset=None, end_offset=None, mode=None):
        """Notifies interested clients that the current region of interest has changed."""

        if start_offset is None:
            start_offset = 0
        if end_offset is None:
            end_offset = start_offset
        if mode is None:
            mode = FOCUS_TRACKING

        try:
            obj.emit("mode-changed::" + mode, 1, "")
        except Exception as error:
            msg = f"FOCUS MANAGER: Exception emitting mode-changed notification: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        if mode != self._active_mode:
            tokens = ["FOCUS MANAGER: Switching mode from", self._active_mode, "to", mode]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._active_mode = mode
            if mode == FLAT_REVIEW:
                braille.setBrlapiPriority(braille.BRLAPI_PRIORITY_HIGH)
            else:
                braille.setBrlapiPriority()

        try:
            tokens = ["FOCUS MANAGER: Region of interest:", obj, f"({start_offset}, {end_offset})"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            obj.emit("region-changed", start_offset, end_offset)
        except Exception as error:
            msg = f"FOCUS MANAGER: Exception emitting region-changed notification: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        if obj != self._object_of_interest:
            tokens = ["FOCUS MANAGER: Switching object of interest from",
                      self._object_of_interest, "to", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._object_of_interest = obj

    def get_active_mode_and_object_of_interest(self):
        """Returns the current mode and associated object of interest"""

        tokens = ["FOCUS MANAGER: Active mode:", self._active_mode,
                  "Object of interest:", self._object_of_interest]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._active_mode, self._object_of_interest

    def get_locus_of_focus(self):
        """Returns the current locus of focus (i.e. the object with visual focus)."""

        tokens = ["FOCUS MANAGER: Locus of focus is", self._focus]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._focus

    def set_locus_of_focus(self, event, obj, notify_script=True, force=False):
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

    def active_window_is_active(self):
        """Returns True if the window we think is currently active is actually active."""

        AXObject.clear_cache(self._window, False, "Ensuring the active window is really active.")
        is_active = AXUtilities.is_active(self._window)
        tokens = ["FOCUS MANAGER:", self._window, "is active:", is_active]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return is_active

    def _is_desktop_frame(self, window):
        """Returns True if this object is the desktop frame"""

        if not AXUtilities.is_frame(window):
            return False

        return AXObject.get_attributes_dict(window).get("is-desktop") == "true"

    def can_be_active_window(self, window):
        """Returns True if window can be the active window based on its state."""

        if window is None:
            return False

        AXObject.clear_cache(window, False, "Checking if window can be the active window")
        app = AXUtilities.get_application(window)
        tokens = ["FOCUS MANAGER:", window, "from", app]

        if not AXUtilities.is_active(window):
            tokens.append("lacks active state")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if not AXUtilities.is_showing(window):
            tokens.append("lacks showing state")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilities.is_iconified(window):
            tokens.append("is iconified")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.get_name(app) == "mutter-x11-frames":
            tokens.append("is from app that cannot have the real active window")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if app and not AXUtilities.is_application_in_desktop(app):
            tokens.append("is from app unknown to AT-SPI2")
            # Firefox alerts and dialogs suffer from this bug too, but if we ignore these windows
            # we'll fail to fully present things like the file chooser dialog and the replace-file
            # alert. https://bugzilla.mozilla.org/show_bug.cgi?id=1882794
            if not AXUtilities.is_dialog_or_alert(window):
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

        tokens.append("can be active window")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    def find_active_window(self, *apps):
        """Tries to locate the active window; may or may not succeed."""

        candidates = []
        apps = apps or AXUtilities.get_all_applications(must_have_window=True)
        for app in apps:
            candidates.extend(list(AXObject.iter_children(app, self.can_be_active_window)))

        if not candidates:
            tokens = ["FOCUS MANAGER: Unable to find active window from", apps]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if len(candidates) == 1:
            tokens = ["FOCUS MANAGER: Active window is", candidates[0]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return candidates[0]

        tokens = ["FOCUS MANAGER: These windows all claim to be active:", candidates]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # Some electron apps running in the background claim to be active even when they
        # are not. These are the ones we know about. We can add others as we go.
        suspect_app_names = ["slack",
                             "discord",
                             "outline-client",
                             "whatsapp-desktop-linux"]
        filtered = []
        for frame in candidates:
            if AXObject.get_name(AXUtilities.get_application(frame)) in suspect_app_names:
                tokens = ["FOCUS MANAGER: Suspecting", frame, "is a non-active Electron app"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            else:
                filtered.append(frame)

        if len(filtered) == 1:
            tokens = ["FOCUS MANAGER: Active window is believed to be", filtered[0]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return filtered[0]

        guess = None
        if filtered:
            tokens = ["FOCUS MANAGER: Still have multiple active windows:", filtered]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            guess = filtered[0]

        tokens = ["FOCUS MANAGER: Returning", guess, "as active window"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return guess

    def get_active_window(self):
        """Returns the currently-active window (i.e. without searching or verifying)."""

        tokens = ["FOCUS MANAGER: Active window is", self._window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
        return self._window

    def set_active_window(self, frame, app=None, set_window_as_focus=False, notify_script=False):
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
            real_app, real_frame = AXUtilities.find_real_app_and_window_for(frame, app)
            if real_frame != frame:
                tokens = ["FOCUS MANAGER: Correcting active window to", real_frame, "in", real_app]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                self._window = real_frame
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


_manager = FocusManager()
def get_manager():
    return _manager
