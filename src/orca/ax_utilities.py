# Utilities for performing tasks related to accessibility inspection.
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

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-branches
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-statements
# pylint: disable=wrong-import-position

"""Utilities for performing tasks related to accessibility inspection."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import functools
import inspect
import threading
import time
from typing import Optional

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities_application import AXUtilitiesApplication
from .ax_utilities_collection import AXUtilitiesCollection
from .ax_utilities_event import AXUtilitiesEvent
from .ax_utilities_relation import AXUtilitiesRelation
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState


class AXUtilities:
    """Utilities for performing tasks related to accessibility inspection."""

    COMPARE_COLLECTION_PERFORMANCE = False

    # Things we cache.
    SET_MEMBERS: dict[int, list[Atspi.Accessible]] = {}
    IS_LAYOUT_ONLY: dict[int, tuple[bool, str]] = {}
    DISPLAYED_DESCRIPTION: dict[int, str] = {}
    DISPLAYED_LABEL: dict[int, str] = {}

    _lock = threading.Lock()

    @staticmethod
    def start_cache_clearing_thread() -> None:
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXUtilities._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def _clear_stored_data() -> None:
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXUtilities._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason: str = "") -> None:
        msg = "AXUtilities: Clearing cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        with AXUtilities._lock:
            AXUtilities.SET_MEMBERS.clear()
            AXUtilities.IS_LAYOUT_ONLY.clear()
            AXUtilities.DISPLAYED_DESCRIPTION.clear()
            AXUtilities.DISPLAYED_LABEL.clear()

    @staticmethod
    def clear_all_cache_now(obj: Optional[Atspi.Accessible] = None, reason: str = "") -> None:
        """Clears all cached information immediately."""

        AXUtilities._clear_all_dictionaries(reason)
        AXObject.clear_cache_now(reason)
        AXUtilitiesRelation.clear_cache_now(reason)
        AXUtilitiesEvent.clear_cache_now(reason)
        if AXUtilitiesRole.is_table_related(obj):
            AXTable.clear_cache_now(reason)

    @staticmethod
    def can_be_active_window(window: Atspi.Accessible) -> bool:
        """Returns True if window can be the active window based on its state."""

        if window is None:
            return False

        AXObject.clear_cache(window, False, "Checking if window can be the active window")
        app = AXUtilitiesApplication.get_application(window)
        tokens = ["AXUtilities:", window, "from", app]

        if not AXUtilitiesState.is_active(window):
            tokens.append("lacks active state")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if not AXUtilitiesState.is_showing(window):
            tokens.append("lacks showing state")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesState.is_iconified(window):
            tokens.append("is iconified")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.get_name(app) == "mutter-x11-frames":
            tokens.append("is from app that cannot have the real active window")
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if app and not AXUtilitiesApplication.is_application_in_desktop(app):
            tokens.append("is from app unknown to AT-SPI2")
            # Firefox alerts and dialogs suffer from this bug too, but if we ignore these windows
            # we'll fail to fully present things like the file chooser dialog and the replace-file
            # alert. https://bugzilla.mozilla.org/show_bug.cgi?id=1882794
            if not AXUtilitiesRole.is_dialog_or_alert(window):
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

        tokens.append("can be active window")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    @staticmethod
    def find_active_window() -> Optional[Atspi.Accessible]:
        """Tries to locate the active window; may or may not succeed."""

        candidates = []
        apps = AXUtilitiesApplication.get_all_applications(must_have_window=True)
        for app in apps:
            candidates.extend(list(AXObject.iter_children(app, AXUtilities.can_be_active_window)))

        if not candidates:
            tokens = ["AXUtilities: Unable to find active window from", apps]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if len(candidates) == 1:
            tokens = ["AXUtilities: Active window is", candidates[0]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return candidates[0]

        tokens = ["AXUtilities: These windows all claim to be active:", candidates]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # Some electron apps running in the background claim to be active even when they
        # are not. These are the ones we know about. We can add others as we go.
        suspect_apps = ["slack",
                        "discord",
                        "outline-client",
                        "whatsapp-desktop-linux"]
        filtered = []
        for frame in candidates:
            if AXObject.get_name(AXUtilitiesApplication.get_application(frame)) in suspect_apps:
                tokens = ["AXUtilities: Suspecting", frame, "is a non-active Electron app"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            else:
                filtered.append(frame)

        if len(filtered) == 1:
            tokens = ["AXUtilities: Active window is believed to be", filtered[0]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return filtered[0]

        guess: Optional[Atspi.Accessible] = None
        if filtered:
            tokens = ["AXUtilities: Still have multiple active windows:", filtered]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            guess = filtered[0]

        if guess is not None:
            tokens = ["AXUtilities: Returning", guess, "as active window"]
        else:
            tokens = ["AXUtilities: No active window found"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return guess

    @staticmethod
    def is_unfocused_alert_or_dialog(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is an unfocused alert or dialog with presentable items."""

        if not AXUtilitiesRole.is_dialog_or_alert(obj):
            return False
        if not AXObject.get_child_count(obj):
            return False
        if not AXUtilitiesState.is_showing(obj):
            return False
        return not AXUtilities.can_be_active_window(obj)

    @staticmethod
    def get_unfocused_alerts_and_dialogs(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of all the unfocused alerts and dialogs in the app and window of obj."""

        app = AXUtilitiesApplication.get_application(obj)
        result = list(AXObject.iter_children(app, AXUtilities.is_unfocused_alert_or_dialog))

        frame = AXObject.find_ancestor(
            obj, lambda x: AXUtilitiesRole.is_application(AXObject.get_parent(x)))
        result.extend(list(AXObject.iter_children(frame, AXUtilities.is_unfocused_alert_or_dialog)))

        tokens = ["AXUtilities: Unfocused alerts and dialogs for", obj, ":", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_all_widgets(
        obj: Atspi.Accessible,
        must_be_showing_and_visible: bool = True,
        exclude_push_button: bool = False
    ) -> list[Atspi.Accessible]:
        """Returns all the descendants of obj with a widget role"""

        roles = AXUtilitiesRole.get_widget_roles()
        if exclude_push_button and Atspi.Role.PUSH_BUTTON in roles:
            roles.remove(Atspi.Role.PUSH_BUTTON)

        result = None
        if AXObject.supports_collection(obj):
            if not must_be_showing_and_visible:
                result = AXUtilitiesCollection.find_all_with_role(obj, roles)
            else:
                states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
                result = AXUtilitiesCollection.find_all_with_role_and_all_states(
                    obj, roles, states)

            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        def is_match(acc):
            if AXObject.get_role(acc) not in roles:
                return False
            if must_be_showing_and_visible:
                return AXUtilitiesState.is_showing(acc) and AXUtilitiesState.is_visible(acc)
            return True

        return AXObject.find_all_descendants(obj, is_match)

    @staticmethod
    def get_default_button(obj: Atspi.Accessible) -> Optional[Atspi.Accessible]:
        """Returns the default button descendant of obj"""

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_default_button(obj)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        return AXObject.find_descendant(obj, AXUtilitiesRole.is_default_button)

    @staticmethod
    def get_focused_object(obj: Atspi.Accessible) -> Optional[Atspi.Accessible]:
        """Returns the focused descendant of obj"""

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_focused_object(obj)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        return AXObject.find_descendant(obj, AXUtilitiesState.is_focused)

    @staticmethod
    def get_status_bar(obj: Atspi.Accessible) -> Optional[Atspi.Accessible]:
        """Returns the status bar descendant of obj"""

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_status_bar(obj)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        return AXObject.find_descendant(obj, AXUtilitiesRole.is_status_bar)

    @staticmethod
    def _is_layout_only(obj: Atspi.Accessible) -> tuple[bool, str]:
        """Returns True and a string reason if obj is believed to serve only for layout."""

        reason = ""
        role = AXObject.get_role(obj)
        if role in AXUtilitiesRole.get_layout_only_roles():
            return True, "has layout-only role"

        if AXUtilitiesRole.is_layered_pane(obj, role):
            result = AXObject.find_ancestor(obj, AXUtilitiesRole.is_desktop_frame) is not None
            if result:
                reason = "is inside desktop frame"
            return result, reason

        if AXUtilitiesRole.is_menu(obj, role) or AXUtilitiesRole.is_list(obj, role):
            result = AXUtilitiesRole.is_combo_box(AXObject.get_parent(obj))
            if result:
                reason = "is inside combo box"
            return result, reason

        if AXUtilitiesRole.is_group(obj, role):
            result = not AXUtilities.has_explicit_name(obj)
            if result:
                reason = "lacks explicit name"
            return result, reason

        if AXUtilitiesRole.is_panel(obj, role) or AXUtilitiesRole.is_grouping(obj, role):
            name = AXObject.get_name(obj)
            description = AXObject.get_description(obj)
            labelled_by = AXUtilitiesRelation.get_is_labelled_by(obj)
            described_by = AXUtilitiesRelation.get_is_described_by(obj)
            if not (name or description or labelled_by or described_by):
                return True, "lacks name, description, and relations"
            if name == AXObject.get_name(AXUtilitiesApplication.get_application(obj)):
                return True, "has same name as app"
            if AXObject.get_child_count(obj) == 1:
                child = AXObject.get_child(obj, 0)
                if name == AXObject.get_name(child):
                    return True, "has same name as its only child"
                if not AXUtilitiesRole.is_label(child) and child in labelled_by:
                    return True, "is labelled by non-label only child"
            set_roles = AXUtilitiesRole.get_set_container_roles()
            if AXObject.find_ancestor(obj, lambda x: AXObject.get_role(x) in set_roles):
                return True, "is in set container"
            return False, reason

        if AXUtilitiesRole.is_section(obj, role) or AXUtilitiesRole.is_document(obj, role):
            if AXUtilitiesState.is_focusable(obj):
                return False, "is focusable"
            if AXObject.has_action(obj, "click"):
                return False, "has click action"
            return True, "is not interactive"

        if AXUtilitiesRole.is_tool_bar(obj):
            result = AXUtilitiesRole.is_page_tab_list(AXObject.get_child(obj, 0))
            if result:
                reason = "is parent of page tab list"
            return result, reason

        if AXUtilitiesRole.is_table(obj, role):
            result = AXTable.is_layout_table(obj)
            if result:
                reason = "is layout table"
            return result, reason

        if AXUtilitiesRole.is_table_row(obj):
            if AXUtilitiesState.is_focusable(obj):
                return False, "is focusable"
            if AXUtilitiesState.is_selectable(obj):
                return False, "is selectable"
            if AXUtilitiesState.is_expandable(obj):
                return False, "is expandable"
            if AXUtilities.has_explicit_name(obj):
                return False, "has explicit name"
            return True, "is not focusable, selectable, or expandable and lacks explicit name"

        if AXUtilitiesRole.is_table_cell(obj, role):
            if AXUtilitiesRole.is_table_cell(AXObject.get_child(obj, 0)):
                return True, "child of this cell is table cell"
            table = AXTable.get_table(obj)
            if AXUtilitiesRole.is_table(table):
                result = AXTable.is_layout_table(table)
                if result:
                    reason = "is in layout table"
                return result, reason

        return False, reason

    @staticmethod
    def is_layout_only(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is believed to serve only for layout."""

        if hash(obj) in AXUtilities.IS_LAYOUT_ONLY:
            result, reason = AXUtilities.IS_LAYOUT_ONLY.get(hash(obj), (False, ""))
        else:
            result, reason = AXUtilities._is_layout_only(obj)
            AXUtilities.IS_LAYOUT_ONLY[hash(obj)] = result, reason

        if reason:
            tokens = ["AXUtilities:", obj, f"believed to be layout only: {result}, {reason}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    @staticmethod
    def is_message_dialog(obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a dialog that should be treated as a message dialog"""

        if not AXUtilitiesRole.is_dialog_or_alert(obj):
            return False

        if not AXObject.supports_collection(obj):
            widgets = AXUtilities.get_all_widgets(obj, exclude_push_button=True)
            return not widgets

        if AXUtilitiesCollection.has_scroll_pane(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has scroll pane"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_split_pane(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has split pane"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_tree_or_tree_table(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has tree or tree table"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_combo_box_or_list_box(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has combo box or list box"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_editable_object(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has editable object"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["AXUtilities:", obj, "is believed to be a message dialog"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    @staticmethod
    def is_redundant_object(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool:
        """Returns True if obj2 is redundant to obj1."""

        if obj1 == obj2:
            return False

        if AXObject.get_name(obj1) != AXObject.get_name(obj2) \
           or AXObject.get_role(obj1) != AXObject.get_role(obj2):
            return False

        tokens = ["AXUtilities:", obj2, "is redundant to", obj1]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    @staticmethod
    def _sort_by_child_index(object_list: list[Atspi.Accessible]) -> list[Atspi.Accessible]:
        """Returns the list of objects sorted according to child index."""

        def cmp(x, y):
            return AXObject.get_index_in_parent(y) - AXObject.get_index_in_parent(x)

        result = sorted(object_list, key=functools.cmp_to_key(cmp))
        if object_list != result:
            tokens = ["AXUtilities: Original list", object_list]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            tokens = ["AXUtilities: Sorted list", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    @staticmethod
    def _get_set_members(
        obj: Atspi.Accessible, container: Atspi.Accessible
    ) -> list[Atspi.Accessible]:
        """Returns the members of the container of obj"""

        if container is None:
            tokens = ["AXUtilities: Members of", obj, "not obtainable: container is None"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        result = AXUtilitiesRelation.get_is_member_of(obj)
        if result:
            tokens = ["AXUtilities: Members of", obj, "in", container, "via member-of", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return AXUtilities._sort_by_child_index(result)

        result = AXUtilitiesRelation.get_is_node_parent_of(obj)
        if result:
            tokens = ["AXUtilities: Members of", obj, "in", container, "via node-parent-of", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return AXUtilities._sort_by_child_index(result)

        if AXUtilitiesRole.is_description_value(obj):
            previous_sibling = AXObject.get_previous_sibling(obj)
            while previous_sibling and AXUtilitiesRole.is_description_value(previous_sibling):
                result.append(previous_sibling)
                previous_sibling = AXObject.get_previous_sibling(previous_sibling)
            result.append(obj)
            next_sibling = AXObject.get_next_sibling(obj)
            while next_sibling and AXUtilitiesRole.is_description_value(next_sibling):
                result.append(next_sibling)
                next_sibling = AXObject.get_next_sibling(next_sibling)
            tokens = ["AXUtilities: Members of", obj, "in", container, "based on siblings", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        if AXUtilitiesRole.is_menu_related(obj):
            result = list(AXObject.iter_children(container, AXUtilitiesRole.is_menu_related))
            tokens = ["AXUtilities: Members of", obj, "in", container, "based on menu role", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        role = AXObject.get_role(obj)
        result = list(AXObject.iter_children(container, lambda x: AXObject.get_role(x) == role))
        tokens = ["AXUtilities: Members of", obj, "in", container, "based on role", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_set_members(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns the members of the container of obj."""

        result: list[Atspi.Accessible] = []
        container = AXObject.get_parent_checked(obj)
        if hash(container) in AXUtilities.SET_MEMBERS:
            result = AXUtilities.SET_MEMBERS.get(hash(container), [])

        if obj not in result:
            if result:
                tokens = ["AXUtilities:", obj, "not in cached members of", container, ":", result]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            result = AXUtilities._get_set_members(obj, container)
            AXUtilities.SET_MEMBERS[hash(container)] = result

        # In a collapsed combobox, one can arrow to change the selection without showing the items.
        must_be_showing = not AXObject.find_ancestor(obj, AXUtilitiesRole.is_combo_box)
        if not must_be_showing:
            return result

        filtered = list(filter(AXUtilitiesState.is_showing, result))
        if result != filtered:
            tokens = ["AXUtilities: Filtered non-showing:", set(result).difference(set(filtered))]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return filtered

    @staticmethod
    def get_set_size(obj: Atspi.Accessible) -> int:
        """Returns the total number of objects in this container."""

        result = AXObject.get_attribute(obj, "setsize", False)
        if isinstance(result, str) and result.isnumeric():
            return int(result)

        if AXUtilitiesRole.is_table_row(obj):
            return AXTable.get_row_count(AXTable.get_table(obj))

        if AXUtilitiesRole.is_table_cell_or_header(obj) \
           and not AXUtilitiesRole.is_table_row(AXObject.get_parent(obj)):
            return AXTable.get_row_count(AXTable.get_table(obj))

        if AXUtilitiesRole.is_combo_box(obj):
            selected_children = AXSelection.get_selected_children(obj)
            if len(selected_children) == 1:
                obj = selected_children[0]

        if AXUtilitiesRole.is_list(obj) or AXUtilitiesRole.is_list_box(obj):
            obj = AXObject.find_descendant(obj, AXUtilitiesRole.is_list_item)

        child_count = AXObject.get_child_count(AXObject.get_parent(obj))
        if child_count > 500:
            return child_count

        members = AXUtilities.get_set_members(obj)
        return len(members)

    @staticmethod
    def get_set_size_is_unknown(obj: Atspi.Accessible) -> bool:
        """Returns True if the total number of objects in this container is unknown."""

        if AXUtilitiesState.is_indeterminate(obj):
            return True

        attrs = AXObject.get_attributes_dict(obj, False)
        if attrs.get("setsize") == "-1":
            return True

        if AXUtilitiesRole.is_table(obj):
            return attrs.get("rowcount") == "-1" or attrs.get("colcount") == "-1"

        return False

    @staticmethod
    def get_position_in_set(obj: Atspi.Accessible) -> int:
        """Returns the position of obj with respect to the number of items in its container."""

        result = AXObject.get_attribute(obj, "posinset", False)
        if isinstance(result, str) and result.isnumeric():
            # ARIA posinset is 1-based.
            return int(result) - 1

        if AXUtilitiesRole.is_table_row(obj):
            result = AXObject.get_attribute(obj, "rowindex", False)
            if isinstance(result, str) and result.isnumeric():
                # ARIA posinset is 1-based.
                return int(result) - 1

            if AXObject.get_child_count(obj):
                cell = AXObject.find_descendant(obj, AXUtilitiesRole.is_table_cell_or_header)
                result = AXObject.get_attribute(cell, "rowindex", False)

            if isinstance(result, str) and result.isnumeric():
                # ARIA posinset is 1-based.
                return int(result) - 1

        if AXUtilitiesRole.is_table_cell_or_header(obj) \
           and not AXUtilitiesRole.is_table_row(AXObject.get_parent(obj)):
            return AXTable.get_cell_coordinates(obj)[0]

        if AXUtilitiesRole.is_combo_box(obj):
            selected_children = AXSelection.get_selected_children(obj)
            if len(selected_children) == 1:
                obj = selected_children[0]

        child_count = AXObject.get_child_count(AXObject.get_parent(obj))
        if child_count > 500:
            return AXObject.get_index_in_parent(obj)

        members = AXUtilities.get_set_members(obj)
        if obj not in members:
            return -1

        return members.index(obj)

    @staticmethod
    def has_explicit_name(obj: Atspi.Accessible) -> bool:
        """Returns True if obj has an author/app-provided name as opposed to a calculated name."""

        return AXObject.get_attribute(obj, "explicit-name") == "true"

    @staticmethod
    def get_displayed_label(obj: Atspi.Accessible) -> str:
        """Returns the displayed label of obj."""

        if hash(obj) in AXUtilities.DISPLAYED_LABEL:
            return AXUtilities.DISPLAYED_LABEL.get(hash(obj), "")

        labels = AXUtilitiesRelation.get_is_labelled_by(obj)
        strings = [AXObject.get_name(label) or AXText.get_all_text(label) for label in labels]
        result = " ".join(strings)
        AXUtilities.DISPLAYED_LABEL[hash(obj)] = result
        return result

    @staticmethod
    def get_displayed_description(obj: Atspi.Accessible) -> str:
        """Returns the displayed description of obj."""

        if hash(obj) in AXUtilities.DISPLAYED_DESCRIPTION:
            return AXUtilities.DISPLAYED_DESCRIPTION.get(hash(obj), "")

        descriptions = AXUtilitiesRelation.get_is_described_by(obj)
        strings = [AXObject.get_name(desc) or AXText.get_all_text(desc) for desc in descriptions]
        result = " ".join(strings)
        AXUtilities.DISPLAYED_DESCRIPTION[hash(obj)] = result
        return result


for method_name, method in inspect.getmembers(AXUtilitiesApplication, predicate=inspect.isfunction):
    setattr(AXUtilities, method_name, method)

for method_name, method in inspect.getmembers(AXUtilitiesEvent, predicate=inspect.isfunction):
    setattr(AXUtilities, method_name, method)

for method_name, method in inspect.getmembers(AXUtilitiesRelation, predicate=inspect.isfunction):
    setattr(AXUtilities, method_name, method)

for method_name, method in inspect.getmembers(AXUtilitiesRole, predicate=inspect.isfunction):
    setattr(AXUtilities, method_name, method)

for method_name, method in inspect.getmembers(AXUtilitiesState, predicate=inspect.isfunction):
    setattr(AXUtilities, method_name, method)

for method_name, method in inspect.getmembers(AXUtilitiesCollection, predicate=inspect.isfunction):
    if method_name.startswith("find"):
        setattr(AXUtilities, method_name, method)

AXUtilities.start_cache_clearing_thread()
