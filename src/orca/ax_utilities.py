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

"""
Utilities for performing tasks related to accessibility inspection.
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

import inspect

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject
from .ax_utilities_collection import AXUtilitiesCollection
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState


class AXUtilities:
    """Utilities for performing tasks related to accessibility inspection."""

    COMPARE_COLLECTION_PERFORMANCE = False

    @staticmethod
    def get_desktop():
        """Returns the accessible desktop"""

        try:
            desktop = Atspi.get_desktop(0)
        except Exception as error:
            tokens = ["ERROR: Exception getting desktop from Atspi:", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return desktop

    @staticmethod
    def get_all_applications(must_have_window=False):
        """Returns a list of running applications known to Atspi, filtering out
        those which have no child windows if must_have_window is True."""

        desktop = AXUtilities.get_desktop()
        if desktop is None:
            return []

        def pred(obj):
            if must_have_window:
                return AXObject.get_child_count(obj) > 0
            return True

        return list(AXObject.iter_children(desktop, pred))

    @staticmethod
    def is_application_in_desktop(app):
        """Returns true if app is known to Atspi"""

        desktop = AXUtilities.get_desktop()
        if desktop is None:
            return False

        for child in AXObject.iter_children(desktop):
            if child == app:
                return True

        tokens = ["WARNING:", app, "is not in", desktop]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return False

    @staticmethod
    def get_application_with_pid(pid):
        """Returns the accessible application with the specified pid"""

        desktop = AXUtilities.get_desktop()
        if desktop is None:
            return None

        for app in AXObject.iter_children(desktop):
            if AXObject.get_process_id(app) == pid:
                return app

        tokens = ["WARNING: app with pid", pid, "is not in", desktop]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return None

    @staticmethod
    def get_all_static_text_leaf_nodes(obj):
        """Returns all the descendants of obj that are static text leaf nodes"""

        roles = [Atspi.Role.STATIC, Atspi.Role.TEXT]
        def is_not_element(acc):
            return AXObject.get_attribute(acc, "tag") in (None, "", "br")

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_all_with_role(obj, roles, is_not_element)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        def is_match(acc):
            return AXObject.get_role(acc) in roles and is_not_element(acc)

        return AXObject.find_all_descendants(obj, is_match)

    @staticmethod
    def get_all_widgets(obj, must_be_showing_and_visible=True, exclude_push_button=False):
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
    def get_default_button(obj):
        """Returns the default button descendant of obj"""

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_default_button(obj)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        return AXObject.find_descendant(obj, AXUtilitiesRole.is_default_button)

    @staticmethod
    def get_focused_object(obj):
        """Returns the focused descendant of obj"""

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_focused_object(obj)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        return AXObject.find_descendant(obj, AXUtilitiesState.is_focused)

    @staticmethod
    def get_status_bar(obj):
        """Returns the status bar descendant of obj"""

        result = None
        if AXObject.supports_collection(obj):
            result = AXUtilitiesCollection.find_status_bar(obj)
            if not AXUtilities.COMPARE_COLLECTION_PERFORMANCE:
                return result

        return AXObject.find_descendant(obj, AXUtilitiesRole.is_status_bar)

    @staticmethod
    def is_message_dialog(obj):
        """Returns True if obj is a dialog that should be treated as a message dialog"""

        if not AXUtilitiesRole.is_dialog_or_alert(obj):
            return False

        if not AXObject.supports_collection(obj):
            widgets = AXUtilities.get_all_widgets(obj, exclude_push_button=True)
            return not widgets

        if AXUtilitiesCollection.has_scroll_pane(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has scroll pane"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_split_pane(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has split pane"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_tree_or_tree_table(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has tree or tree table"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_combo_box_or_list_box(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has combo box or list box"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilitiesCollection.has_editable_object(obj):
            tokens = ["AXUtilities:", obj, "is not a message dialog: has editable object"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["AXUtilities:", obj, "is believed to be a message dialog"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return True


for name, method in inspect.getmembers(AXUtilitiesRole, predicate=inspect.isfunction):
    setattr(AXUtilities, name, method)

for name, method in inspect.getmembers(AXUtilitiesState, predicate=inspect.isfunction):
    setattr(AXUtilities, name, method)

for name, method in inspect.getmembers(AXUtilitiesCollection, predicate=inspect.isfunction):
    if name.startswith("find"):
        setattr(AXUtilities, name, method)
