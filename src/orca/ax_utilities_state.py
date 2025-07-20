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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements

"""Utilities for obtaining state-related information."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from . import messages
from .ax_object import AXObject


class AXUtilitiesState:
    """Utilities for obtaining state-related information."""

    @staticmethod
    def get_current_item_status_string(obj: Atspi.Accessible) -> str:
        """Returns the current item status string of obj."""

        if not AXUtilitiesState.is_active(obj):
            return ""

        result = AXObject.get_attribute(obj, "current")
        if not result:
            return ""
        if result == "date":
            return messages.CURRENT_DATE
        if result == "time":
            return messages.CURRENT_TIME
        if result == "location":
            return messages.CURRENT_LOCATION
        if result == "page":
            return messages.CURRENT_PAGE
        if result == "step":
            return messages.CURRENT_STEP
        return messages.CURRENT_ITEM

    @staticmethod
    def has_no_state(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has an empty state set"""

        return AXObject.get_state_set(obj).is_empty()

    @staticmethod
    def has_popup(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the has-popup state"""

        return AXObject.has_state(obj, Atspi.StateType.HAS_POPUP)

    @staticmethod
    def has_tooltip(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the has-tooltip state"""

        return AXObject.has_state(obj, Atspi.StateType.HAS_TOOLTIP)

    @staticmethod
    def is_active(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the active state"""

        return AXObject.has_state(obj, Atspi.StateType.ACTIVE)

    @staticmethod
    def is_animated(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the animated state"""

        return AXObject.has_state(obj, Atspi.StateType.ANIMATED)

    @staticmethod
    def is_armed(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the armed state"""

        return AXObject.has_state(obj, Atspi.StateType.ARMED)

    @staticmethod
    def is_busy(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the busy state"""

        return AXObject.has_state(obj, Atspi.StateType.BUSY)

    @staticmethod
    def is_checkable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the checkable state"""

        if AXObject.has_state(obj, Atspi.StateType.CHECKABLE):
            return True

        if AXObject.has_state(obj, Atspi.StateType.CHECKED):
            tokens = ["AXUtilitiesState:", obj, "is checked but lacks state checkable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_checked(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the checked state"""

        if not AXObject.has_state(obj, Atspi.StateType.CHECKED):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.CHECKABLE):
            tokens = ["AXUtilitiesState:", obj, "is checked but lacks state checkable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return True

    @staticmethod
    def is_collapsed(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the collapsed state"""

        return AXObject.has_state(obj, Atspi.StateType.COLLAPSED)

    @staticmethod
    def is_default(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the is-default state"""

        return AXObject.has_state(obj, Atspi.StateType.IS_DEFAULT)

    @staticmethod
    def is_defunct(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the defunct state"""

        return AXObject.has_state(obj, Atspi.StateType.DEFUNCT)

    @staticmethod
    def is_editable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the editable state"""

        return AXObject.has_state(obj, Atspi.StateType.EDITABLE)

    @staticmethod
    def is_enabled(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the enabled state"""

        return AXObject.has_state(obj, Atspi.StateType.ENABLED)

    @staticmethod
    def is_expandable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the expandable state"""

        if AXObject.has_state(obj, Atspi.StateType.EXPANDABLE):
            return True

        if AXObject.has_state(obj, Atspi.StateType.EXPANDED):
            tokens = ["AXUtilitiesState:", obj, "is expanded but lacks state expandable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_expanded(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the expanded state"""

        if not AXObject.has_state(obj, Atspi.StateType.EXPANDED):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.EXPANDABLE):
            tokens = ["AXUtilitiesState:", obj, "is expanded but lacks state expandable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return True

    @staticmethod
    def is_focusable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the focusable state"""

        if AXObject.has_state(obj, Atspi.StateType.FOCUSABLE):
            return True

        if AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            tokens = ["AXUtilitiesState:", obj, "is focused but lacks state focusable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_focused(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the focused state"""

        if not AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.FOCUSABLE):
            tokens = ["AXUtilitiesState:", obj, "is focused but lacks state focusable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return True

    @staticmethod
    def is_hidden(obj: Atspi.Accessible) -> bool:
        """Returns true if obj reports being hidden"""

        return AXObject.get_attribute(obj, "hidden", False) == "true"

    @staticmethod
    def is_horizontal(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the horizontal state"""

        return AXObject.has_state(obj, Atspi.StateType.HORIZONTAL)

    @staticmethod
    def is_iconified(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the iconified state"""

        return AXObject.has_state(obj, Atspi.StateType.ICONIFIED)

    @staticmethod
    def is_indeterminate(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the indeterminate state"""

        return AXObject.has_state(obj, Atspi.StateType.INDETERMINATE)

    @staticmethod
    def is_invalid_state(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the invalid_state state"""

        return AXObject.has_state(obj, Atspi.StateType.INVALID)

    @staticmethod
    def is_invalid_entry(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the invalid_entry state"""

        return AXObject.has_state(obj, Atspi.StateType.INVALID_ENTRY)

    @staticmethod
    def is_modal(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the modal state"""

        return AXObject.has_state(obj, Atspi.StateType.MODAL)

    @staticmethod
    def is_multi_line(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the multi_line state"""

        return AXObject.has_state(obj, Atspi.StateType.MULTI_LINE)

    @staticmethod
    def is_multiselectable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the multiselectable state"""

        return AXObject.has_state(obj, Atspi.StateType.MULTISELECTABLE)

    @staticmethod
    def is_opaque(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the opaque state"""

        return AXObject.has_state(obj, Atspi.StateType.OPAQUE)

    @staticmethod
    def is_pressed(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the pressed state"""

        return AXObject.has_state(obj, Atspi.StateType.PRESSED)

    @staticmethod
    def is_read_only(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the read-only state"""

        if AXObject.has_state(obj, Atspi.StateType.READ_ONLY):
            return True
        if AXUtilitiesState.is_editable(obj):
            return False

        # We cannot count on GTK to set the read-only state on text objects.
        return AXObject.get_role(obj) == Atspi.Role.TEXT

    @staticmethod
    def is_required(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the required state"""

        return AXObject.has_state(obj, Atspi.StateType.REQUIRED)

    @staticmethod
    def is_resizable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the resizable state"""

        return AXObject.has_state(obj, Atspi.StateType.RESIZABLE)

    @staticmethod
    def is_selectable(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the selectable state"""

        return AXObject.has_state(obj, Atspi.StateType.SELECTABLE)

    @staticmethod
    def is_selectable_text(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the selectable-text state"""

        return AXObject.has_state(obj, Atspi.StateType.SELECTABLE_TEXT)

    @staticmethod
    def is_selected(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the selected state"""

        return AXObject.has_state(obj, Atspi.StateType.SELECTED)

    @staticmethod
    def is_sensitive(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the sensitive state"""

        return AXObject.has_state(obj, Atspi.StateType.SENSITIVE)

    @staticmethod
    def is_showing(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the showing state"""

        return AXObject.has_state(obj, Atspi.StateType.SHOWING)

    @staticmethod
    def is_single_line(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the single-line state"""

        return AXObject.has_state(obj, Atspi.StateType.SINGLE_LINE)

    @staticmethod
    def is_stale(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the stale state"""

        return AXObject.has_state(obj, Atspi.StateType.STALE)

    @staticmethod
    def is_transient(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the transient state"""

        return AXObject.has_state(obj, Atspi.StateType.TRANSIENT)

    @staticmethod
    def is_truncated(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the truncated state"""

        return AXObject.has_state(obj, Atspi.StateType.TRUNCATED)

    @staticmethod
    def is_vertical(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the vertical state"""

        return AXObject.has_state(obj, Atspi.StateType.VERTICAL)

    @staticmethod
    def is_visible(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the visible state"""

        return AXObject.has_state(obj, Atspi.StateType.VISIBLE)

    @staticmethod
    def is_visited(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the visited state"""

        return AXObject.has_state(obj, Atspi.StateType.VISITED)

    @staticmethod
    def manages_descendants(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the manages-descendants state"""

        return AXObject.has_state(obj, Atspi.StateType.MANAGES_DESCENDANTS)

    @staticmethod
    def supports_autocompletion(obj: Atspi.Accessible) -> bool:
        """Returns true if obj has the supports-autocompletion state"""

        return AXObject.has_state(obj, Atspi.StateType.SUPPORTS_AUTOCOMPLETION)
