# Utilities for obtaining information about accessible objects.
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
# pylint: disable=too-many-lines
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-public-methods

"""Utilities for obtaining information about accessible objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import re
import threading
import time
from typing import Callable, Generator

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi
from gi.repository import GLib
from gi.repository import Gtk

from . import debug
from . import keynames


class AXObject:
    """Utilities for obtaining information about accessible objects."""

    KNOWN_DEAD: dict[int, bool] = {}
    OBJECT_ATTRIBUTES: dict[int, dict[str, str]] = {}

    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data() -> None:
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXObject._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason: str = "") -> None:
        msg = "AXObject: Clearing local cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        with AXObject._lock:
            AXObject.KNOWN_DEAD.clear()
            AXObject.OBJECT_ATTRIBUTES.clear()

    @staticmethod
    def clear_cache_now(reason: str = "") -> None:
        """Clears all cached information immediately."""

        AXObject._clear_all_dictionaries(reason)

    @staticmethod
    def start_cache_clearing_thread() -> None:
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXObject._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def get_toolkit_name(obj: Atspi.Accessible) -> str:
        """Returns the toolkit name of obj as a lowercase string"""

        try:
            app = Atspi.Accessible.get_application(obj)
            name = Atspi.Accessible.get_toolkit_name(app) or ""
        except GLib.GError as error:
            tokens = ["AXObject: Exception calling _get_toolkit_name_on", app, f": {error}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        return name.lower()

    @staticmethod
    def is_bogus(obj: Atspi.Accessible) -> bool:
        """Hack to ignore certain objects. All entries must have a bug."""

        # TODO - JD: Periodically check for fixes and remove hacks which are no
        # longer needed.

        # https://bugzilla.mozilla.org/show_bug.cgi?id=1879750
        if AXObject.get_role(obj) == Atspi.Role.SECTION \
           and AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.FRAME \
           and AXObject.get_toolkit_name(obj) == "gecko":
            tokens = ["AXObject:", obj, "is bogus. See mozilla bug 1879750."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            return True

        return False

    @staticmethod
    def has_broken_ancestry(obj: Atspi.Accessible) -> bool:
        """Returns True if obj's ancestry is broken."""

        if obj is None:
            return False

        # https://bugreports.qt.io/browse/QTBUG-130116
        toolkit_name = AXObject.get_toolkit_name(obj)
        if not toolkit_name.startswith("qt"):
            return False

        reached_app = False
        parent = AXObject.get_parent(obj)
        while parent and not reached_app:
            reached_app = AXObject.get_role(parent) == Atspi.Role.APPLICATION
            parent = AXObject.get_parent(parent)

        if not reached_app:
            tokens = ["AXObject:", obj, "has broken ancestry. See qt bug 130116."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    @staticmethod
    def is_valid(obj: Atspi.Accessible) -> bool:
        """Returns False if we know for certain this object is invalid"""

        return not (obj is None or AXObject.object_is_known_dead(obj))

    @staticmethod
    def object_is_known_dead(obj: Atspi.Accessible) -> bool:
        """Returns True if we know for certain this object no longer exists"""

        return bool(obj and AXObject.KNOWN_DEAD.get(hash(obj))) is True

    @staticmethod
    def _set_known_dead_status(obj: Atspi.Accessible, is_dead: bool) -> None:
        """Updates the known-dead status of obj"""

        if obj is None:
            return

        current_status = AXObject.KNOWN_DEAD.get(hash(obj))
        if current_status == is_dead:
            return

        AXObject.KNOWN_DEAD[hash(obj)] = is_dead
        if is_dead:
            msg = "AXObject: Adding to known dead objects"
            debug.print_message(debug.LEVEL_INFO, msg, True, True)
            return

        if current_status:
            tokens = ["AXObject: Removing", obj, "from known-dead objects"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def handle_error(obj: Atspi.Accessible, error: Exception, msg: str) -> None:
        """Parses the exception and potentially updates our status for obj"""

        error_string = str(error)
        if re.search(r"accessible/\d+ does not exist", error_string):
            msg = msg.replace(error_string, "object no longer exists")
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif re.search(r"The application no longer exists", error_string):
            msg = msg.replace(error_string, "app no longer exists")
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if AXObject.KNOWN_DEAD.get(hash(obj)) is False:
            AXObject._set_known_dead_status(obj, True)

    @staticmethod
    def supports_action(obj: Atspi.Accessible) -> bool:
        """Returns True if the action interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_action_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_action_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def _has_document_spreadsheet(obj: Atspi.Accessible) -> bool:
        # To avoid circular import. pylint: disable=import-outside-toplevel
        from .ax_collection import AXCollection
        rule = AXCollection.create_match_rule(roles=[Atspi.Role.DOCUMENT_SPREADSHEET])
        if rule is None:
            return False

        frame = AXObject.find_ancestor_inclusive(
            obj, lambda x: AXObject.get_role(x) == Atspi.Role.FRAME)
        if frame is None:
            return False
        return bool(Atspi.Collection.get_matches(
            frame, rule, Atspi.CollectionSortOrder.CANONICAL, 1, True))

    @staticmethod
    def supports_collection(obj: Atspi.Accessible) -> bool:
        """Returns True if the collection interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            app = Atspi.Accessible.get_application(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in supports_collection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        try:
            iface = Atspi.Accessible.get_collection_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_collection_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        app_name = AXObject.get_name(app)
        if app_name != "soffice":
            return iface is not None

        if AXObject.find_ancestor_inclusive(
            obj, lambda x: AXObject.get_role(x) == Atspi.Role.DOCUMENT_TEXT):
            return True

        if AXObject._has_document_spreadsheet(obj):
            msg = "AXObject: Treating soffice as not supporting collection due to spreadsheet."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True

    @staticmethod
    def supports_component(obj: Atspi.Accessible) -> bool:
        """Returns True if the component interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_component_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_component_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None


    @staticmethod
    def supports_document(obj: Atspi.Accessible) -> bool:
        """Returns True if the document interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_document_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_document_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_editable_text(obj: Atspi.Accessible) -> bool:
        """Returns True if the editable-text interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_editable_text_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_editable_text_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_hyperlink(obj: Atspi.Accessible) -> bool:
        """Returns True if the hyperlink interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_hyperlink(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_hyperlink on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_hypertext(obj: Atspi.Accessible) -> bool:
        """Returns True if the hypertext interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_hypertext_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_hypertext_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_image(obj: Atspi.Accessible) -> bool:
        """Returns True if the image interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_image_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_image_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_selection(obj: Atspi.Accessible) -> bool:
        """Returns True if the selection interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_selection_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_selection_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_table(obj: Atspi.Accessible) -> bool:
        """Returns True if the table interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_table_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_table_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_table_cell(obj: Atspi.Accessible) -> bool:
        """Returns True if the table cell interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_table_cell(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_table_cell on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_text(obj: Atspi.Accessible) -> bool:
        """Returns True if the text interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_text_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_text_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False
        return iface is not None

    @staticmethod
    def supports_value(obj: Atspi.Accessible) -> bool:
        """Returns True if the value interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_value_iface(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception calling get_value_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def get_path(obj: Atspi.Accessible) -> list[int]:
        """Returns the path from application to obj as list of child indices"""

        if not AXObject.is_valid(obj):
            return []

        path = []
        acc = obj
        while acc:
            try:
                path.append(Atspi.Accessible.get_index_in_parent(acc))
            except GLib.GError as error:
                msg = f"AXObject: Exception getting index in parent for {acc}: {error}"
                AXObject.handle_error(acc, error, msg)
                return []
            acc = AXObject.get_parent_checked(acc)

        path.reverse()
        return path

    @staticmethod
    def get_index_in_parent(obj: Atspi.Accessible) -> int:
        """Returns the child index of obj within its parent"""

        if not AXObject.is_valid(obj):
            return -1

        try:
            index = Atspi.Accessible.get_index_in_parent(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_index_in_parent: {error}"
            AXObject.handle_error(obj, error, msg)
            return -1

        return index

    @staticmethod
    def get_parent(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the accessible parent of obj. See also get_parent_checked."""

        if not AXObject.is_valid(obj):
            return None

        try:
            parent = Atspi.Accessible.get_parent(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_parent: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if parent == obj:
            tokens = ["AXObject:", obj, "claims to be its own parent"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if parent is None \
           and AXObject.get_role(obj) not in [Atspi.Role.INVALID, Atspi.Role.DESKTOP_FRAME]:
            tokens = ["AXObject:", obj, "claims to have no parent"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return parent

    @staticmethod
    def get_parent_checked(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the parent of obj, doing checks for tree validity"""

        if not AXObject.is_valid(obj):
            return None

        role = AXObject.get_role(obj)
        if role in [Atspi.Role.INVALID, Atspi.Role.APPLICATION]:
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        if debug.LEVEL_INFO < debug.debugLevel:
            return parent

        if AXObject.is_dead(obj):
            return parent

        index = AXObject.get_index_in_parent(obj)
        n_children = AXObject.get_child_count(parent)
        if index < 0 or index >= n_children:
            tokens = ["AXObject:", obj, "has index", index,
                      "; parent", parent, "has", n_children, "children"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return parent

        # This performs our check and includes any errors. We don't need the return value here.
        AXObject.get_active_descendant_checked(parent, obj)
        return parent

    @staticmethod
    def _get_ancestors(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of the ancestors of obj, starting with its parent."""

        ancestors = []
        parent = AXObject.get_parent_checked(obj)
        while parent:
            ancestors.append(parent)
            parent = AXObject.get_parent_checked(parent)
        ancestors.reverse()
        return ancestors

    @staticmethod
    def get_common_ancestor(
        obj1: Atspi.Accessible,
        obj2: Atspi.Accessible
    ) -> Atspi.Accessible | None:
        """Returns the common ancestor of obj1 and obj2."""

        tokens = ["AXObject: Looking for common ancestor of", obj1, "and", obj2]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not (obj1 and obj2):
            return None

        if obj1 == obj2:
            return obj1

        obj1_ancestors = AXObject._get_ancestors(obj1) + [obj1]
        obj2_ancestors = AXObject._get_ancestors(obj2) + [obj2]
        result = None
        for a1, a2 in zip(obj1_ancestors, obj2_ancestors):
            if a1 == a2:
                result = a1
            else:
                break

        tokens = ["AXObject: Common ancestor of", obj1, "and", obj2, "is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_ancestor_inclusive(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool]
    ) -> Atspi.Accessible | None:
        """Returns obj, or the ancestor of obj, for which the function pred is true"""

        if pred(obj):
            return obj

        return AXObject.find_ancestor(obj, pred)

    @staticmethod
    def find_ancestor(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool]
    ) -> Atspi.Accessible | None:
        """Returns the ancestor of obj if the function pred is true"""

        if not AXObject.is_valid(obj):
            return None

        # Keep track of objects we've encountered in order to handle broken trees.
        objects = [obj]
        parent = AXObject.get_parent_checked(obj)
        while parent:
            if parent in objects:
                tokens = ["AXObject: Circular tree suspected in find_ancestor. ",
                          parent, "already in: ", objects]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return None

            if pred(parent):
                return parent

            objects.append(parent)
            parent = AXObject.get_parent_checked(parent)

        return None

    @staticmethod
    def is_ancestor(
        obj: Atspi.Accessible,
        ancestor: Atspi.Accessible,
        inclusive: bool = False
    ) -> bool:
        """Returns true if ancestor is an ancestor of obj or, if inclusive, obj is ancestor."""

        if not AXObject.is_valid(obj):
            return False

        if not AXObject.is_valid(ancestor):
            return False

        if obj == ancestor and inclusive:
            return True

        return AXObject.find_ancestor(obj, lambda x: x == ancestor) is not None

    @staticmethod
    def get_child(obj: Atspi.Accessible, index: int) -> Atspi.Accessible | None:
        """Returns the nth child of obj. See also get_child_checked."""

        if not AXObject.is_valid(obj):
            return None

        n_children = AXObject.get_child_count(obj)
        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not 0 <= index < n_children:
            return None

        try:
            child = Atspi.Accessible.get_child_at_index(obj, index)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_child: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if child == obj:
            tokens = ["AXObject:", obj, "claims to be its own child"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return child

    @staticmethod
    def get_child_checked(
        obj: Atspi.Accessible, index: int
    ) -> Atspi.Accessible | None:
        """Returns the nth child of obj, doing checks for tree validity"""

        if not AXObject.is_valid(obj):
            return None

        child = AXObject.get_child(obj, index)
        if debug.LEVEL_INFO < debug.debugLevel:
            return child

        parent = AXObject.get_parent(child)
        if obj != parent:
            tokens = ["AXObject:", obj, "claims", child, "as child; child's parent is", parent]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return child

    @staticmethod
    def get_active_descendant_checked(
        container: Atspi.Accessible,
        reported_child: Atspi.Accessible
    ) -> Atspi.Accessible | None:
        """Checks the reported active descendant and return the real/valid one."""

        if not AXObject.has_state(container, Atspi.StateType.MANAGES_DESCENDANTS):
            return reported_child

        index = AXObject.get_index_in_parent(reported_child)
        try:
            real_child = Atspi.Accessible.get_child_at_index(container, index)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_active_descendant_checked: {error}"
            AXObject.handle_error(container, error, msg)
            return reported_child

        if real_child != reported_child:
            tokens = [
                "AXObject: ", container, f"'s child at {index} is ", real_child,
                "; not reported child", reported_child
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return real_child

    @staticmethod
    def _find_descendant(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool]
    ) -> Atspi.Accessible | None:
        """Returns the descendant of obj if the function pred is true"""

        if not AXObject.is_valid(obj):
            return None

        for i in range(AXObject.get_child_count(obj)):
            child = AXObject.get_child_checked(obj, i)
            if child is None:
                continue
            if pred(child):
                return child
            child = AXObject._find_descendant(child, pred)
            if child:
                return child

        return None

    @staticmethod
    def find_descendant(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool]
    ) -> Atspi.Accessible | None:
        """Returns the descendant of obj if the function pred is true"""

        start = time.time()
        result = AXObject._find_descendant(obj, pred)
        tokens = ["AXObject: find_descendant: found", result, f"in {time.time() - start:.4f}s"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_deepest_descendant(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the deepest descendant of obj"""

        if not AXObject.is_valid(obj):
            return None

        last_child = AXObject.get_child(obj, AXObject.get_child_count(obj) - 1)
        if last_child is None:
            return obj

        return AXObject.find_deepest_descendant(last_child)

    @staticmethod
    def _find_all_descendants(
        obj: Atspi.Accessible,
        include_if: Callable[[Atspi.Accessible], bool] | None,
        exclude_if: Callable[[Atspi.Accessible], bool] | None,
        matches: list[Atspi.Accessible]
    ) -> None:
        """Returns all descendants which match the specified inclusion and exclusion"""

        if not AXObject.is_valid(obj):
            return

        child_count = AXObject.get_child_count(obj)
        for i in range(child_count):
            child = AXObject.get_child(obj, i)
            if exclude_if and exclude_if(child):
                continue
            if include_if and include_if(child):
                matches.append(child)
            AXObject._find_all_descendants(child, include_if, exclude_if, matches)

    @staticmethod
    def find_all_descendants(
        root: Atspi.Accessible,
        include_if: Callable[[Atspi.Accessible], bool] | None = None,
        exclude_if: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants which match the specified inclusion and exclusion"""

        start = time.time()
        matches: list[Atspi.Accessible] = []
        AXObject._find_all_descendants(root, include_if, exclude_if, matches)
        msg = (
            f"AXObject: find_all_descendants: {len(matches)} "
            f"matches found in {time.time() - start:.4f}s"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return matches

    @staticmethod
    def get_role(obj: Atspi.Accessible) -> Atspi.Role:
        """Returns the accessible role of obj"""

        if not AXObject.is_valid(obj):
            return Atspi.Role.INVALID

        try:
            role = Atspi.Accessible.get_role(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_role: {error}"
            AXObject.handle_error(obj, error, msg)
            return Atspi.Role.INVALID

        AXObject._set_known_dead_status(obj, False)
        return role

    @staticmethod
    def get_role_name(obj: Atspi.Accessible, localized: bool = False) -> str:
        """Returns the accessible role name of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            if not localized:
                role_name = Atspi.Accessible.get_role_name(obj)
            else:
                role_name = Atspi.Accessible.get_localized_role_name(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_role_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return role_name

    @staticmethod
    def get_role_description(obj: Atspi.Accessible, is_braille: bool = False) -> str:
        """Returns the accessible role description of obj"""

        if not AXObject.is_valid(obj):
            return ""

        attrs = AXObject.get_attributes_dict(obj)
        rv = attrs.get("roledescription", "")
        if is_braille:
            rv = attrs.get("brailleroledescription", rv)
        return rv

    @staticmethod
    def get_accessible_id(obj: Atspi.Accessible) -> str:
        """Returns the accessible id of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            result = Atspi.Accessible.get_accessible_id(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_accessible_id: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        AXObject._set_known_dead_status(obj, False)
        return result

    @staticmethod
    def get_name(obj: Atspi.Accessible) -> str:
        """Returns the accessible name of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            name = Atspi.Accessible.get_name(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        AXObject._set_known_dead_status(obj, False)
        return name

    @staticmethod
    def has_same_non_empty_name(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool:
        """Returns true if obj1 and obj2 share the same non-empty name"""

        name1 = AXObject.get_name(obj1)
        if not name1:
            return False

        return name1 == AXObject.get_name(obj2)

    @staticmethod
    def get_description(obj: Atspi.Accessible) -> str:
        """Returns the accessible description of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            description = Atspi.Accessible.get_description(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_image_description(obj: Atspi.Accessible) -> str:
        """Returns the accessible image description of obj"""

        if not AXObject.supports_image(obj):
            return ""

        try:
            description = Atspi.Image.get_image_description(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_image_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_image_size(obj: Atspi.Accessible) -> tuple[int, int]:
        """Returns a (width, height) tuple of the image in obj"""

        if not AXObject.supports_image(obj):
            return 0, 0

        try:
            result = Atspi.Image.get_image_size(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_image_size: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0, 0

        # The return value is an AtspiPoint, hence x and y.
        return result.x, result.y

    @staticmethod
    def get_help_text(obj: Atspi.Accessible) -> str:
        """Returns the accessible help text of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            # Added in Atspi 2.52.
            text = Atspi.Accessible.get_help_text(obj) or ""
        except GLib.GError:
            # This is for prototyping in the meantime.
            text = AXObject.get_attribute(obj, "helptext") or ""

        return text

    @staticmethod
    def get_child_count(obj: Atspi.Accessible) -> int:
        """Returns the child count of obj"""

        if not AXObject.is_valid(obj):
            return 0

        try:
            count = Atspi.Accessible.get_child_count(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_child_count: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0

        return count

    @staticmethod
    def iter_children(
        obj: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> Generator[Atspi.Accessible, None, None]:
        """Generator to iterate through obj's children. If the function pred is
        specified, children for which pred is False will be skipped."""

        if not AXObject.is_valid(obj):
            return

        child_count = AXObject.get_child_count(obj)
        if child_count > 500:
            tokens = ["AXObject:", obj, "has more than 500 children"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        for index in range(child_count):
            child = AXObject.get_child(obj, index)
            if child is None and not AXObject.is_valid(obj):
                tokens = ["AXObject:", obj, "is no longer valid"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return

            if child is not None and (pred is None or pred(child)):
                yield child

    @staticmethod
    def get_previous_sibling(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the previous sibling of obj, based on child indices"""

        if not AXObject.is_valid(obj):
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        index = AXObject.get_index_in_parent(obj)
        if index <= 0:
            return None

        sibling = AXObject.get_child(parent, index - 1)
        if sibling == obj:
            tokens = ["AXObject:", obj, "claims to be its own sibling"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return sibling

    @staticmethod
    def get_next_sibling(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the next sibling of obj, based on child indices"""

        if not AXObject.is_valid(obj):
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        index = AXObject.get_index_in_parent(obj)
        if index < 0:
            return None

        sibling = AXObject.get_child(parent, index + 1)
        if sibling == obj:
            tokens = ["AXObject:", obj, "claims to be its own sibling"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return sibling

    @staticmethod
    def get_state_set(obj: Atspi.Accessible) -> Atspi.StateSet:
        """Returns the state set associated with obj"""

        if not AXObject.is_valid(obj):
            return Atspi.StateSet()

        try:
            state_set = Atspi.Accessible.get_state_set(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_state_set: {error}"
            AXObject.handle_error(obj, error, msg)
            return Atspi.StateSet()

        AXObject._set_known_dead_status(obj, False)
        return state_set

    @staticmethod
    def has_state(obj: Atspi.Accessible, state: Atspi.StateType) -> bool:
        """Returns true if obj has the specified state"""

        if not AXObject.is_valid(obj):
            return False

        return AXObject.get_state_set(obj).contains(state)

    @staticmethod
    def clear_cache(
        obj: Atspi.Accessible,
        recursive: bool = False,
        reason: str = ""
    ) -> None:
        """Clears the Atspi cached information associated with obj"""

        if obj is None:
            return

        tokens = ["AXObject: Clearing AT-SPI cache on", obj, f"Recursive: {recursive}."]
        if reason:
            tokens.append(f" Reason: {reason}")
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not recursive:
            try:
                Atspi.Accessible.clear_cache_single(obj)
            except GLib.GError as error:
                msg = f"AXObject: Exception in clear_cache_single: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        try:
            Atspi.Accessible.clear_cache(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in clear_cache: {error}"
            AXObject.handle_error(obj, error, msg)

    @staticmethod
    def get_process_id(obj: Atspi.Accessible) -> int:
        """Returns the process id associated with obj"""

        if not AXObject.is_valid(obj):
            return -1

        try:
            pid = Atspi.Accessible.get_process_id(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_process_id: {error}"
            AXObject.handle_error(obj, error, msg)
            return -1

        return pid

    @staticmethod
    def is_dead(obj: Atspi.Accessible) -> bool:
        """Returns true of obj exists but is believed to be dead."""

        if obj is None:
            return False

        if not AXObject.is_valid(obj):
            return True

        try:
            # We use the Atspi function rather than the AXObject function because the
            # latter intentionally handles exceptions.
            Atspi.Accessible.get_name(obj)
        except GLib.GError as error:
            msg = f"AXObject: Accessible is dead: {error}"
            AXObject.handle_error(obj, error, msg)
            return True

        AXObject._set_known_dead_status(obj, False)
        return False

    @staticmethod
    def get_attributes_dict(
        obj: Atspi.Accessible,
        use_cache: bool = True
    ) -> dict[str, str]:
        """Returns the object attributes of obj as a dictionary."""

        if not AXObject.is_valid(obj):
            return {}

        if use_cache:
            attributes = AXObject.OBJECT_ATTRIBUTES.get(hash(obj))
            if attributes:
                return attributes

        try:
            attributes = Atspi.Accessible.get_attributes(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_attributes_dict: {error}"
            AXObject.handle_error(obj, error, msg)
            return {}

        if attributes is None:
            return {}

        AXObject.OBJECT_ATTRIBUTES[hash(obj)] = attributes
        return attributes

    @staticmethod
    def get_attribute(
        obj: Atspi.Accessible,
        attribute_name: str,
        use_cache: bool = True
    ) -> str:
        """Returns the value of the specified attribute as a string."""

        if not AXObject.is_valid(obj):
            return ""

        attributes = AXObject.get_attributes_dict(obj, use_cache)
        return attributes.get(attribute_name, "")

    @staticmethod
    def get_n_actions(obj: Atspi.Accessible) -> int:
        """Returns the number of actions supported on obj."""

        if not AXObject.supports_action(obj):
            return 0

        try:
            count = Atspi.Action.get_n_actions(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_n_actions: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0

        return count

    @staticmethod
    def _normalize_action_name(action_name: str) -> str:
        """Adjusts the name to account for differences in implementations."""

        if not action_name:
            return ""

        name = re.sub(r'(?<=[a-z])([A-Z])', r'-\1', action_name).lower()
        name = re.sub('[!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]', '-', name)
        return name

    @staticmethod
    def get_action_name(obj: Atspi.Accessible, i: int) -> str:
        """Returns the name of obj's action at index i."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return ""

        try:
            name = Atspi.Action.get_action_name(obj, i)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_action_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return AXObject._normalize_action_name(name)

    @staticmethod
    def get_action_names(obj: Atspi.Accessible) -> list[str]:
        """Returns the list of actions supported on obj."""

        results = []
        for i in range(AXObject.get_n_actions(obj)):
            name = AXObject.get_action_name(obj, i)
            if name:
                results.append(name)
        return results

    @staticmethod
    def get_action_description(obj: Atspi.Accessible, i: int) -> str:
        """Returns the description of obj's action at index i."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return ""

        try:
            description = Atspi.Action.get_action_description(obj, i)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_action_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_action_key_binding(obj: Atspi.Accessible, i: int) -> str:
        """Returns the key binding string of obj's action at index i."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return ""

        try:
            keybinding = Atspi.Action.get_key_binding(obj, i)
        except GLib.GError as error:
            msg = f"AXObject: Exception in get_action_key_binding: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        # GTK4 does this.
        if keybinding == "<VoidSymbol>":
            return ""
        return keybinding

    @staticmethod
    def _get_label_for_key_sequence(sequence: str) -> str:
        """Returns the human consumable label for the key sequence."""

        if not sequence:
            return ""

        # We get all sorts of variations in the keybinding string. Try to normalize it.
        if len(sequence) > 1 and not sequence.startswith("<") and "," not in sequence:
            tokens = sequence.split("+")
            sequence = "".join(f"<{part}>" for part in tokens[:-1]) + tokens[-1]

        # We use Gtk for conversion to handle things like <Primary>.
        try:
            key, mods = Gtk.accelerator_parse(sequence)
            result = Gtk.accelerator_get_label(key, mods)
        except GLib.GError as error:
            msg = f"AXObject: Exception in _get_label_for_key_sequence: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            sequence = sequence.replace("<", "").replace(">", " ").strip()
        else:
            if result and not result.endswith("+"):
                sequence = result

        return keynames.localize_key_sequence(sequence)

    @staticmethod
    def get_accelerator(obj: Atspi.Accessible) -> str:
        """Returns the accelerator/shortcut associated with obj."""

        attrs = AXObject.get_attributes_dict(obj)
        # The ARIA spec suggests a given shortcut's components should be separated by a "+".
        # Multiple shortcuts are apparently allowed and separated by a space.
        shortcuts = attrs.get("keyshortcuts", "").split(" ")
        if shortcuts and shortcuts[0]:
            result = " ".join(map(AXObject._get_label_for_key_sequence, shortcuts)).strip()
            # Accelerators are typically modified and thus more than one character.
            if len(result) > 1:
                return result

        index = AXObject._find_first_action_with_keybinding(obj)
        if index == -1:
            return ""

        # This should be a string separated by semicolons and in the form:
        #     <mnemonic>;<full sequence>;<accelerator/shortcut> (optional)
        # In practice we get all sorts of variations.

        # If there's a third item, it's probably the accelerator.
        strings = AXObject.get_action_key_binding(obj, index).split(";")
        if len(strings) == 3:
            return AXObject._get_label_for_key_sequence(strings[2])

        # If the last thing has Ctrl in it, it's probably the accelerator.
        result = AXObject._get_label_for_key_sequence(strings[-1])
        if "Ctrl" in result:
            return result

        return ""

    @staticmethod
    def get_mnemonic(obj: Atspi.Accessible) -> str:
        """Returns the mnemonic associated with obj."""

        attrs = AXObject.get_attributes_dict(obj)
        # The ARIA spec suggests a given shortcut's components should be separated by a "+".
        # Multiple shortcuts are apparently allowed and separated by a space.
        shortcuts = attrs.get("keyshortcuts", "").split(" ")
        if shortcuts and shortcuts[0]:
            result = " ".join(map(AXObject._get_label_for_key_sequence, shortcuts)).strip()
            # If it's not a single letter it's probably not the mnemonic.
            if len(result) == 1:
                return result

        index = AXObject._find_first_action_with_keybinding(obj)
        if index == -1:
            return ""

        # This should be a string separated by semicolons and in the form:
        #     <mnemonic>;<full sequence>;<accelerator/shortcut> (optional)
        # In practice we get all sorts of variations.

        strings = AXObject.get_action_key_binding(obj, index).split(";")
        result = AXObject._get_label_for_key_sequence(strings[0])
        # If Ctrl is in the result, it's probably the accelerator rather than the mnemonic.
        if "Ctrl" in result or "Control" in result:
            return ""

        # Don't treat space as a mnemonic.
        if result.lower() in [" ", "space", "<space>"]:
            return ""

        return result

    @staticmethod
    def _find_first_action_with_keybinding(obj: Atspi.Accessible) -> int:
        """Returns the index of the first action with a keybinding on obj."""

        for i in range(AXObject.get_n_actions(obj)):
            if AXObject.get_action_key_binding(obj, i):
                return i
        return -1

    @staticmethod
    def has_action(obj: Atspi.Accessible, action_name: str) -> bool:
        """Returns true if the named action is supported on obj."""

        return AXObject.get_action_index(obj, action_name) >= 0

    @staticmethod
    def get_action_index(obj: Atspi.Accessible, action_name: str) -> int:
        """Returns the index of the named action or -1 if unsupported."""

        action_name = AXObject._normalize_action_name(action_name)
        for i in range(AXObject.get_n_actions(obj)):
            if action_name == AXObject.get_action_name(obj, i):
                return i

        return -1

    @staticmethod
    def do_action(obj: Atspi.Accessible, i: int) -> bool:
        """Invokes obj's action at index i. The return value, if true, may be
        meaningless because most implementors return true without knowing if
        the action was successfully performed."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return False

        try:
            result = Atspi.Action.do_action(obj, i)
        except GLib.GError as error:
            msg = f"AXObject: Exception in do_action: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return result

    @staticmethod
    def do_named_action(obj: Atspi.Accessible, action_name: str) -> bool:
        """Invokes the named action on obj. The return value, if true, may be
        meaningless because most implementors return true without knowing if
        the action was successfully performed."""

        index = AXObject.get_action_index(obj, action_name)
        if index == -1:
            tokens = ["INFO:", action_name, "not an available action for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        return AXObject.do_action(obj, index)

    @staticmethod
    def grab_focus(obj: Atspi.Accessible) -> bool:
        """Attempts to grab focus on obj. Returns true if successful."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.grab_focus(obj)
        except GLib.GError as error:
            msg = f"AXObject: Exception in grab_focus: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        if debug.LEVEL_INFO < debug.debugLevel:
            return result

        if result and not AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            tokens = ["AXObject:", obj, "lacks focused state after focus grab"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

AXObject.start_cache_clearing_thread()
