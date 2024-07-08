# Utilities for obtaining state-related information.
#
# Copyright 2023 Igalia, S.L.
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

"""
Utilities for obtaining state-related information.
These utilities are app-type- and toolkit-agnostic. Utilities that might have
different implementations or results depending on the type of app (e.g. terminal,
chat, web) or toolkit (e.g. Qt, Gtk) should be in script_utilities.py file(s).

N.B. There are currently utilities that should never have custom implementations
that live in script_utilities.py files. These will be moved over time.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import threading
import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject


class AXUtilitiesState:
    """Utilities for obtaining state-related information."""

    LAST_KNOWN_CHECKED = {}
    LAST_KNOWN_EXPANDED = {}
    LAST_KNOWN_INDETERMINATE = {}
    LAST_KNOWN_PRESSED = {}
    LAST_KNOWN_SELECTED = {}

    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data():
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXUtilitiesState._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason=""):
        msg = "AXUtilitiesState: Clearing local cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        with AXUtilitiesState._lock:
            AXUtilitiesState.LAST_KNOWN_CHECKED.clear()
            AXUtilitiesState.LAST_KNOWN_EXPANDED.clear()
            AXUtilitiesState.LAST_KNOWN_INDETERMINATE.clear()
            AXUtilitiesState.LAST_KNOWN_PRESSED.clear()
            AXUtilitiesState.LAST_KNOWN_SELECTED.clear()

    @staticmethod
    def clear_cache_now(reason=""):
        """Clears all cached information immediately."""

        AXUtilitiesState._clear_all_dictionaries(reason)

    @staticmethod
    def start_cache_clearing_thread():
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXUtilitiesState._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def save_state_info(obj):
        """Saves some state info to be used with subsequent state-changed events."""

        AXUtilitiesState.LAST_KNOWN_CHECKED[hash(obj)] = AXUtilitiesState.is_checked(obj)
        AXUtilitiesState.LAST_KNOWN_EXPANDED[hash(obj)] = AXUtilitiesState.is_expanded(obj)
        AXUtilitiesState.LAST_KNOWN_INDETERMINATE[hash(obj)] = \
            AXUtilitiesState.is_indeterminate(obj)
        AXUtilitiesState.LAST_KNOWN_PRESSED[hash(obj)] = AXUtilitiesState.is_pressed(obj)
        AXUtilitiesState.LAST_KNOWN_SELECTED[hash(obj)] = AXUtilitiesState.is_selected(obj)

    @staticmethod
    def checked_state_did_change(obj):
        """Returns True if the checked state of obj is known to have changed."""

        old_value = AXUtilitiesState.LAST_KNOWN_CHECKED.get(hash(obj))
        new_value = AXUtilitiesState.is_checked(obj)
        result = old_value != new_value
        tokens = ["AXUtilitiesState: Checked state of", obj, f"was {old_value}, is {new_value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        AXUtilitiesState.LAST_KNOWN_CHECKED[hash(obj)] = new_value
        return result

    @staticmethod
    def expanded_state_did_change(obj):
        """Returns True if the expanded state of obj is known to have changed."""

        old_value = AXUtilitiesState.LAST_KNOWN_EXPANDED.get(hash(obj))
        new_value = AXUtilitiesState.is_expanded(obj)
        result = old_value != new_value
        tokens = ["AXUtilitiesState: Expanded state of", obj, f"was {old_value}, is {new_value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        AXUtilitiesState.LAST_KNOWN_EXPANDED[hash(obj)] = new_value
        return result

    @staticmethod
    def indeterminate_state_did_change(obj):
        """Returns True if the indeterminate state of obj is known to have changed."""

        old_value = AXUtilitiesState.LAST_KNOWN_INDETERMINATE.get(hash(obj))
        new_value = AXUtilitiesState.is_indeterminate(obj)
        result = old_value != new_value
        tokens = ["AXUtilitiesState: Indeterminate state of", obj, f"was {old_value},",
                  f"is {new_value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        AXUtilitiesState.LAST_KNOWN_INDETERMINATE[hash(obj)] = new_value
        return result

    @staticmethod
    def pressed_state_did_change(obj):
        """Returns True if the pressed state of obj is known to have changed."""

        old_value = AXUtilitiesState.LAST_KNOWN_PRESSED.get(hash(obj))
        new_value = AXUtilitiesState.is_pressed(obj)
        result = old_value != new_value
        tokens = ["AXUtilitiesState: Pressed state of", obj, f"was {old_value}, is {new_value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        AXUtilitiesState.LAST_KNOWN_PRESSED[hash(obj)] = new_value
        return result

    @staticmethod
    def selected_state_did_change(obj):
        """Returns True if the selected state of obj is known to have changed."""

        old_value = AXUtilitiesState.LAST_KNOWN_SELECTED.get(hash(obj))
        new_value = AXUtilitiesState.is_selected(obj)
        result = old_value != new_value
        tokens = ["AXUtilitiesState: Selected state of", obj, f"was {old_value}, is {new_value}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        AXUtilitiesState.LAST_KNOWN_SELECTED[hash(obj)] = new_value
        return result

    @staticmethod
    def has_no_state(obj):
        """Returns true if obj has an empty state set"""

        return AXObject.get_state_set(obj).is_empty()

    @staticmethod
    def has_popup(obj):
        """Returns true if obj has the has-popup state"""

        return AXObject.has_state(obj, Atspi.StateType.HAS_POPUP)

    @staticmethod
    def has_tooltip(obj):
        """Returns true if obj has the has-tooltip state"""

        return AXObject.has_state(obj, Atspi.StateType.HAS_TOOLTIP)

    @staticmethod
    def is_active(obj):
        """Returns true if obj has the active state"""

        return AXObject.has_state(obj, Atspi.StateType.ACTIVE)

    @staticmethod
    def is_animated(obj):
        """Returns true if obj has the animated state"""

        return AXObject.has_state(obj, Atspi.StateType.ANIMATED)

    @staticmethod
    def is_armed(obj):
        """Returns true if obj has the armed state"""

        return AXObject.has_state(obj, Atspi.StateType.ARMED)

    @staticmethod
    def is_busy(obj):
        """Returns true if obj has the busy state"""

        return AXObject.has_state(obj, Atspi.StateType.BUSY)

    @staticmethod
    def is_checkable(obj):
        """Returns true if obj has the checkable state"""

        if AXObject.has_state(obj, Atspi.StateType.CHECKABLE):
            return True

        if AXObject.has_state(obj, Atspi.StateType.CHECKED):
            tokens = ["AXUtilitiesState:", obj, "is checked but lacks state checkable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_checked(obj):
        """Returns true if obj has the checked state"""

        if not AXObject.has_state(obj, Atspi.StateType.CHECKED):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.CHECKABLE):
            tokens = ["AXUtilitiesState:", obj, "is checked but lacks state checkable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return True

    @staticmethod
    def is_collapsed(obj):
        """Returns true if obj has the collapsed state"""

        return AXObject.has_state(obj, Atspi.StateType.COLLAPSED)

    @staticmethod
    def is_default(obj):
        """Returns true if obj has the is-default state"""

        return AXObject.has_state(obj, Atspi.StateType.IS_DEFAULT)

    @staticmethod
    def is_defunct(obj):
        """Returns true if obj has the defunct state"""

        return AXObject.has_state(obj, Atspi.StateType.DEFUNCT)

    @staticmethod
    def is_editable(obj):
        """Returns true if obj has the editable state"""

        return AXObject.has_state(obj, Atspi.StateType.EDITABLE)

    @staticmethod
    def is_enabled(obj):
        """Returns true if obj has the enabled state"""

        return AXObject.has_state(obj, Atspi.StateType.ENABLED)

    @staticmethod
    def is_expandable(obj):
        """Returns true if obj has the expandable state"""

        if AXObject.has_state(obj, Atspi.StateType.EXPANDABLE):
            return True

        if AXObject.has_state(obj, Atspi.StateType.EXPANDED):
            tokens = ["AXUtilitiesState:", obj, "is expanded but lacks state expandable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_expanded(obj):
        """Returns true if obj has the expanded state"""

        if not AXObject.has_state(obj, Atspi.StateType.EXPANDED):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.EXPANDABLE):
            tokens = ["AXUtilitiesState:", obj, "is expanded but lacks state expandable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return True

    @staticmethod
    def is_focusable(obj):
        """Returns true if obj has the focusable state"""

        if AXObject.has_state(obj, Atspi.StateType.FOCUSABLE):
            return True

        if AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            tokens = ["AXUtilitiesState:", obj, "is focused but lacks state focusable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_focused(obj):
        """Returns true if obj has the focused state"""

        if not AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.FOCUSABLE):
            tokens = ["AXUtilitiesState:", obj, "is focused but lacks state focusable"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return True

    @staticmethod
    def is_horizontal(obj):
        """Returns true if obj has the horizontal state"""

        return AXObject.has_state(obj, Atspi.StateType.HORIZONTAL)

    @staticmethod
    def is_iconified(obj):
        """Returns true if obj has the iconified state"""

        return AXObject.has_state(obj, Atspi.StateType.ICONIFIED)

    @staticmethod
    def is_indeterminate(obj):
        """Returns true if obj has the indeterminate state"""

        return AXObject.has_state(obj, Atspi.StateType.INDETERMINATE)

    @staticmethod
    def is_invalid_state(obj):
        """Returns true if obj has the invalid_state state"""

        return AXObject.has_state(obj, Atspi.StateType.INVALID)

    @staticmethod
    def is_invalid_entry(obj):
        """Returns true if obj has the invalid_entry state"""

        return AXObject.has_state(obj, Atspi.StateType.INVALID_ENTRY)

    @staticmethod
    def is_modal(obj):
        """Returns true if obj has the modal state"""

        return AXObject.has_state(obj, Atspi.StateType.MODAL)

    @staticmethod
    def is_multi_line(obj):
        """Returns true if obj has the multi_line state"""

        return AXObject.has_state(obj, Atspi.StateType.MULTI_LINE)

    @staticmethod
    def is_multiselectable(obj):
        """Returns true if obj has the multiselectable state"""

        return AXObject.has_state(obj, Atspi.StateType.MULTISELECTABLE)

    @staticmethod
    def is_opaque(obj):
        """Returns true if obj has the opaque state"""

        return AXObject.has_state(obj, Atspi.StateType.OPAQUE)

    @staticmethod
    def is_pressed(obj):
        """Returns true if obj has the pressed state"""

        return AXObject.has_state(obj, Atspi.StateType.PRESSED)

    @staticmethod
    def is_read_only(obj):
        """Returns true if obj has the read-only state"""

        return AXObject.has_state(obj, Atspi.StateType.READ_ONLY)

    @staticmethod
    def is_required(obj):
        """Returns true if obj has the required state"""

        return AXObject.has_state(obj, Atspi.StateType.REQUIRED)

    @staticmethod
    def is_resizable(obj):
        """Returns true if obj has the resizable state"""

        return AXObject.has_state(obj, Atspi.StateType.RESIZABLE)

    @staticmethod
    def is_selectable(obj):
        """Returns true if obj has the selectable state"""

        return AXObject.has_state(obj, Atspi.StateType.SELECTABLE)

    @staticmethod
    def is_selectable_text(obj):
        """Returns true if obj has the selectable-text state"""

        return AXObject.has_state(obj, Atspi.StateType.SELECTABLE_TEXT)

    @staticmethod
    def is_selected(obj):
        """Returns true if obj has the selected state"""

        return AXObject.has_state(obj, Atspi.StateType.SELECTED)

    @staticmethod
    def is_sensitive(obj):
        """Returns true if obj has the sensitive state"""

        return AXObject.has_state(obj, Atspi.StateType.SENSITIVE)

    @staticmethod
    def is_showing(obj):
        """Returns true if obj has the showing state"""

        return AXObject.has_state(obj, Atspi.StateType.SHOWING)

    @staticmethod
    def is_single_line(obj):
        """Returns true if obj has the single-line state"""

        return AXObject.has_state(obj, Atspi.StateType.SINGLE_LINE)

    @staticmethod
    def is_stale(obj):
        """Returns true if obj has the stale state"""

        return AXObject.has_state(obj, Atspi.StateType.STALE)

    @staticmethod
    def is_transient(obj):
        """Returns true if obj has the transient state"""

        return AXObject.has_state(obj, Atspi.StateType.TRANSIENT)

    @staticmethod
    def is_truncated(obj):
        """Returns true if obj has the truncated state"""

        return AXObject.has_state(obj, Atspi.StateType.TRUNCATED)

    @staticmethod
    def is_vertical(obj):
        """Returns true if obj has the vertical state"""

        return AXObject.has_state(obj, Atspi.StateType.VERTICAL)

    @staticmethod
    def is_visible(obj):
        """Returns true if obj has the visible state"""

        return AXObject.has_state(obj, Atspi.StateType.VISIBLE)

    @staticmethod
    def is_visited(obj):
        """Returns true if obj has the visited state"""

        return AXObject.has_state(obj, Atspi.StateType.VISITED)

    @staticmethod
    def manages_descendants(obj):
        """Returns true if obj has the manages-descendants state"""

        return AXObject.has_state(obj, Atspi.StateType.MANAGES_DESCENDANTS)

    @staticmethod
    def supports_autocompletion(obj):
        """Returns true if obj has the supports-autocompletion state"""

        return AXObject.has_state(obj, Atspi.StateType.SUPPORTS_AUTOCOMPLETION)

AXUtilitiesState.start_cache_clearing_thread()
