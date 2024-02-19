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

"""
Utilities for obtaining information about accessible objects.
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

import re
import threading
import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug


class AXObject:
    """Utilities for obtaining information about accessible objects."""

    KNOWN_DEAD = {}
    REAL_APP_FOR_MUTTER_FRAME = {}
    REAL_FRAME_FOR_MUTTER_FRAME = {}
    OBJECT_ATTRIBUTES = {}

    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data():
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXObject._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason=""):
        msg = "AXObject: Clearing local cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        with AXObject._lock:
            tokens = ["AXObject: Clearing known dead-or-alive state for",
                        len(AXObject.KNOWN_DEAD), "objects"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            AXObject.KNOWN_DEAD.clear()

            tokens = ["AXObject: Clearing", len(AXObject.REAL_APP_FOR_MUTTER_FRAME),
                        "real apps for mutter frames"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            AXObject.REAL_APP_FOR_MUTTER_FRAME.clear()

            tokens = ["AXObject: Clearing", len(AXObject.REAL_FRAME_FOR_MUTTER_FRAME),
                        "real frames for mutter frames"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            AXObject.REAL_FRAME_FOR_MUTTER_FRAME.clear()

            tokens = ["AXObject: Clearing cached object attributes for",
                        len(AXObject.OBJECT_ATTRIBUTES), "objects"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            AXObject.OBJECT_ATTRIBUTES.clear()

    @staticmethod
    def clear_cache_now(reason=""):
        """Clears all cached information immediately."""

        AXObject._clear_all_dictionaries(reason)

    @staticmethod
    def start_cache_clearing_thread():
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXObject._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def is_bogus(obj):
        """Hack to ignore certain objects. All entries must have a bug."""

        # TODO - JD: Periodically check for fixes and remove hacks which are no
        # longer needed.

        # https://bugzilla.mozilla.org/show_bug.cgi?id=1879750
        if AXObject.get_role(obj) == Atspi.Role.SECTION \
           and AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.FRAME \
           and Atspi.Accessible.get_toolkit_name(obj).lower() == "gecko":
            tokens = ["AXObject:", obj, "is bogus. See mozilla bug 1879750."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True, True)
            return True

        return False

    @staticmethod
    def is_valid(obj):
        """Returns False if we know for certain this object is invalid"""

        return not (obj is None or AXObject.object_is_known_dead(obj))

    @staticmethod
    def object_is_known_dead(obj):
        """Returns True if we know for certain this object no longer exists"""

        return obj and AXObject.KNOWN_DEAD.get(hash(obj)) is True

    @staticmethod
    def _set_known_dead_status(obj, is_dead):
        """Updates the known-dead status of obj"""

        if obj is None:
            return

        current_status = AXObject.KNOWN_DEAD.get(hash(obj))
        if current_status == is_dead:
            return

        AXObject.KNOWN_DEAD[hash(obj)] = is_dead
        if is_dead:
            msg = "AXObject: Adding to known dead objects"
            debug.printMessage(debug.LEVEL_INFO, msg, True, True)
            return

        if current_status:
            tokens = ["AXObject: Removing", obj, "from known-dead objects"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

    @staticmethod
    def handle_error(obj, error, msg):
        """Parses the exception and potentially updates our status for obj"""

        error = str(error)
        if re.search(r"accessible/\d+ does not exist", error):
            msg = msg.replace(error, "object no longer exists")
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif re.search(r"The application no longer exists", error):
            msg = msg.replace(error, "app no longer exists")
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        else:
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if AXObject.KNOWN_DEAD.get(hash(obj)) is False:
            AXObject._set_known_dead_status(obj, True)

    @staticmethod
    def supports_action(obj):
        """Returns True if the action interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_action_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_action_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_collection(obj):
        """Returns True if the collection interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        app_name = AXObject.get_name(AXObject.get_application(obj))
        if app_name in ["soffice"]:
            tokens = ["AXObject: Treating", app_name, "as not supporting collection."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        try:
            iface = Atspi.Accessible.get_collection_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_collection_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_component(obj):
        """Returns True if the component interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_component_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_component_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None


    @staticmethod
    def supports_document(obj):
        """Returns True if the document interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_document_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_document_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_editable_text(obj):
        """Returns True if the editable-text interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_editable_text_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_editable_text_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_hyperlink(obj):
        """Returns True if the hyperlink interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_hyperlink(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_hyperlink on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_hypertext(obj):
        """Returns True if the hypertext interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_hypertext_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_hypertext_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_image(obj):
        """Returns True if the image interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_image_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_image_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_selection(obj):
        """Returns True if the selection interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_selection_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_selection_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_table(obj):
        """Returns True if the table interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_table_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_table_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_table_cell(obj):
        """Returns True if the table cell interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_table_cell(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_table_cell on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supports_text(obj):
        """Returns True if the text interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_text_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_text_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False
        return iface is not None

    @staticmethod
    def supports_value(obj):
        """Returns True if the value interface is supported on obj"""

        if not AXObject.is_valid(obj):
            return False

        try:
            iface = Atspi.Accessible.get_value_iface(obj)
        except Exception as error:
            msg = f"AXObject: Exception calling get_value_iface on {obj}: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return iface is not None

    @staticmethod
    def supported_interfaces_as_string(obj):
        """Returns the supported interfaces of obj as a string"""

        if not AXObject.is_valid(obj):
            return ""

        iface_checks = [
            (AXObject.supports_action, "Action"),
            (AXObject.supports_collection, "Collection"),
            (AXObject.supports_component, "Component"),
            (AXObject.supports_document, "Document"),
            (AXObject.supports_editable_text, "EditableText"),
            (AXObject.supports_hyperlink, "Hyperlink"),
            (AXObject.supports_hypertext, "Hypertext"),
            (AXObject.supports_image, "Image"),
            (AXObject.supports_selection, "Selection"),
            (AXObject.supports_table, "Table"),
            (AXObject.supports_table_cell, "TableCell"),
            (AXObject.supports_text, "Text"),
            (AXObject.supports_value, "Value"),
        ]

        ifaces = [iface for check, iface in iface_checks if check(obj)]
        return ", ".join(ifaces)

    @staticmethod
    def get_path(obj):
        """Returns the path from application to obj as list of child indices"""

        if not AXObject.is_valid(obj):
            return []

        path = []
        acc = obj
        while acc:
            try:
                path.append(Atspi.Accessible.get_index_in_parent(acc))
            except Exception as error:
                msg = f"AXObject: Exception getting index in parent for {acc}: {error}"
                AXObject.handle_error(acc, error, msg)
                return []
            acc = AXObject.get_parent_checked(acc)

        path.reverse()
        return path

    @staticmethod
    def get_index_in_parent(obj):
        """Returns the child index of obj within its parent"""

        if not AXObject.is_valid(obj):
            return -1

        try:
            index = Atspi.Accessible.get_index_in_parent(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_index_in_parent: {error}"
            AXObject.handle_error(obj, error, msg)
            return -1

        return index

    @staticmethod
    def get_parent(obj):
        """Returns the accessible parent of obj. See also get_parent_checked."""

        if not AXObject.is_valid(obj):
            return None

        try:
            parent = Atspi.Accessible.get_parent(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_parent: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if parent == obj:
            tokens = ["AXObject:", obj, "claims to be its own parent"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        if parent is None \
           and AXObject.get_role(obj) not in [Atspi.Role.INVALID, Atspi.Role.DESKTOP_FRAME]:
            tokens = ["AXObject:", obj, "claims to have no parent"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return parent

    @staticmethod
    def get_parent_checked(obj):
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
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return parent

        # This performs our check and includes any errors. We don't need the return value here.
        AXObject.get_active_descendant_checked(parent, obj)
        return parent

    @staticmethod
    def find_ancestor(obj, pred):
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
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return None

            if pred(parent):
                return parent

            objects.append(parent)
            parent = AXObject.get_parent_checked(parent)

        return None

    @staticmethod
    def is_ancestor(obj, ancestor):
        """Returns true if ancestor is an ancestor of obj"""

        if not AXObject.is_valid(obj):
            return False

        if not AXObject.is_valid(ancestor):
            return False

        return AXObject.find_ancestor(obj, lambda x: x == ancestor) is not None

    @staticmethod
    def get_child(obj, index):
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
        except Exception as error:
            msg = f"AXObject: Exception in get_child: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if child == obj:
            tokens = ["AXObject:", obj, "claims to be its own child"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return child

    @staticmethod
    def get_child_checked(obj, index):
        """Returns the nth child of obj, doing checks for tree validity"""

        if not AXObject.is_valid(obj):
            return None

        child = AXObject.get_child(obj, index)
        if debug.LEVEL_INFO < debug.debugLevel:
            return child

        parent = AXObject.get_parent(child)
        if obj != parent:
            tokens = ["AXObject:", obj, "claims", child, "as child; child's parent is", parent]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return child

    @staticmethod
    def get_active_descendant_checked(container, reported_child):
        """Checks the reported active descendant and return the real/valid one."""

        if not AXObject.has_state(container, Atspi.StateType.MANAGES_DESCENDANTS):
            return reported_child

        index = AXObject.get_index_in_parent(reported_child)
        try:
            real_child = Atspi.Accessible.get_child_at_index(container, index)
        except Exception as error:
            msg = f"AXObject: Exception in get_active_descendant_checked: {error}"
            AXObject.handle_error(container, error, msg)
            return reported_child

        if real_child != reported_child:
            tokens = ["AXObject: ", container, f"'s child at {index} is ", real_child,
                      "; not reported child", reported_child]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return real_child

    @staticmethod
    def _find_descendant(obj, pred):
        """Returns the descendant of obj if the function pred is true"""

        if not AXObject.is_valid(obj):
            return None

        for i in range(AXObject.get_child_count(obj)):
            child = AXObject.get_child_checked(obj, i)
            if child and pred(child):
                return child

            child = AXObject._find_descendant(child, pred)
            if child and pred(child):
                return child

        return None

    @staticmethod
    def find_descendant(obj, pred):
        """Returns the descendant of obj if the function pred is true"""

        start = time.time()
        result = AXObject._find_descendant(obj, pred)
        tokens = ["AXObject: find_descendant: found", result, f"in {time.time() - start:.4f}s"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_deepest_descendant(obj):
        """Returns the deepest descendant of obj"""

        if not AXObject.is_valid(obj):
            return None

        last_child = AXObject.get_child(obj, AXObject.get_child_count(obj) - 1)
        if last_child is None:
            return obj

        return AXObject.find_deepest_descendant(last_child)

    @staticmethod
    def _find_all_descendants(obj, include_if, exclude_if, matches):
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
    def find_all_descendants(root, include_if=None, exclude_if=None):
        """Returns all descendants which match the specified inclusion and exclusion"""

        start = time.time()
        matches = []
        AXObject._find_all_descendants(root, include_if, exclude_if, matches)
        msg = (
            f"AXObject: find_all_descendants: {len(matches)} "
            f"matches found in {time.time() - start:.4f}s"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return matches

    @staticmethod
    def get_role(obj):
        """Returns the accessible role of obj"""

        if not AXObject.is_valid(obj):
            return Atspi.Role.INVALID

        try:
            role = Atspi.Accessible.get_role(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_role: {error}"
            AXObject.handle_error(obj, error, msg)
            return Atspi.Role.INVALID

        AXObject._set_known_dead_status(obj, False)
        return role

    @staticmethod
    def get_role_name(obj):
        """Returns the accessible role name of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            role_name = Atspi.Accessible.get_role_name(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_role_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return role_name

    @staticmethod
    def get_name(obj):
        """Returns the accessible name of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            name = Atspi.Accessible.get_name(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        AXObject._set_known_dead_status(obj, False)
        return name

    @staticmethod
    def has_same_non_empty_name(obj1, obj2):
        """Returns true if obj1 and obj2 share the same non-empty name"""

        name1 = AXObject.get_name(obj1)
        if not name1:
            return False

        return name1 == AXObject.get_name(obj2)

    @staticmethod
    def get_description(obj):
        """Returns the accessible description of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            description = Atspi.Accessible.get_description(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_image_description(obj):
        """Returns the accessible image description of obj"""

        if not AXObject.supports_image(obj):
            return ""

        try:
            description = Atspi.Image.get_image_description(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_image_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_image_size(obj):
        """Returns a (width, height) tuple of the image in obj"""

        if not AXObject.supports_image(obj):
            return 0, 0

        try:
            result = Atspi.Image.get_image_size(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_image_size: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0, 0

        # The return value is an AtspiPoint, hence x and y.
        return result.x, result.y

    @staticmethod
    def get_help_text(obj):
        """Returns the accessible help text of obj"""

        if not AXObject.is_valid(obj):
            return ""

        try:
            # Added in Atspi 2.52.
            text = Atspi.Accessible.get_help_text(obj)
        except Exception:
            # This is for prototyping in the meantime.
            text = AXObject.get_attribute(obj, "helptext") or ""

        return text

    @staticmethod
    def get_child_count(obj):
        """Returns the child count of obj"""

        if not AXObject.is_valid(obj):
            return 0

        try:
            count = Atspi.Accessible.get_child_count(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_child_count: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0

        return count

    @staticmethod
    def iter_children(obj, pred=None):
        """Generator to iterate through obj's children. If the function pred is
        specified, children for which pred is False will be skipped."""

        if not AXObject.is_valid(obj):
            return

        child_count = AXObject.get_child_count(obj)
        for index in range(child_count):
            child = AXObject.get_child(obj, index)
            if child is not None and (pred is None or pred(child)):
                yield child

    @staticmethod
    def get_previous_sibling(obj):
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
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return sibling

    @staticmethod
    def get_next_sibling(obj):
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
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return sibling

    @staticmethod
    def get_next_object(obj):
        """Returns the next object (depth first) in the accessibility tree"""

        if not AXObject.is_valid(obj):
            return None

        index = AXObject.get_index_in_parent(obj) + 1
        parent = AXObject.get_parent(obj)
        while parent and not 0 < index < AXObject.get_child_count(parent):
            obj = parent
            index = AXObject.get_index_in_parent(obj) + 1
            parent = AXObject.get_parent(obj)

        if parent is None:
            return None

        next_object = AXObject.get_child(parent, index)
        if next_object == obj:
            tokens = ["AXObject:", obj, "claims to be its own next object"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return next_object

    @staticmethod
    def get_previous_object(obj):
        """Returns the previous object (depth first) in the accessibility tree"""

        if not AXObject.is_valid(obj):
            return None

        index = AXObject.get_index_in_parent(obj) - 1
        parent = AXObject.get_parent(obj)
        while parent and not 0 <= index < AXObject.get_child_count(parent) - 1:
            obj = parent
            index = AXObject.get_index_in_parent(obj) - 1
            parent = AXObject.get_parent(obj)

        if parent is None:
            return None

        previous_object = AXObject.get_child(parent, index)
        if previous_object == obj:
            tokens = ["AXObject:", obj, "claims to be its own previous object"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        return previous_object

    @staticmethod
    def get_state_set(obj):
        """Returns the state set associated with obj"""

        if not AXObject.is_valid(obj):
            return Atspi.StateSet()

        try:
            state_set = Atspi.Accessible.get_state_set(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_state_set: {error}"
            AXObject.handle_error(obj, error, msg)
            return Atspi.StateSet()

        AXObject._set_known_dead_status(obj, False)
        return state_set

    @staticmethod
    def has_state(obj, state):
        """Returns true if obj has the specified state"""

        if not AXObject.is_valid(obj):
            return False

        return AXObject.get_state_set(obj).contains(state)

    @staticmethod
    def state_set_as_string(obj):
        """Returns the state set associated with obj as a string"""

        if not AXObject.is_valid(obj):
            return ""

        def as_string(state):
            return state.value_name[12:].replace("_", "-").lower()

        return ", ".join(map(as_string, AXObject.get_state_set(obj).get_states()))

    @staticmethod
    def get_relations(obj):
        """Returns the list of Atspi.Relation objects associated with obj"""

        if not AXObject.is_valid(obj):
            return []

        try:
            relations = Atspi.Accessible.get_relation_set(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_relations: {error}"
            AXObject.handle_error(obj, error, msg)
            return []

        return relations

    @staticmethod
    def get_relation(obj, relation_type):
        """Returns the specified Atspi.Relation for obj"""

        if not AXObject.is_valid(obj):
            return None

        for relation in AXObject.get_relations(obj):
            if relation and relation.get_relation_type() == relation_type:
                return relation

        return None

    @staticmethod
    def has_relation(obj, relation_type):
        """Returns true if obj has the specified relation type"""

        if not AXObject.is_valid(obj):
            return False

        return AXObject.get_relation(obj, relation_type) is not None

    @staticmethod
    def get_relation_targets(obj, relation_type, pred=None):
        """Returns the list of targets with the specified relation type to obj.
        If pred is provided, a target will only be included if pred is true."""

        if not AXObject.is_valid(obj):
            return []

        relation = AXObject.get_relation(obj, relation_type)
        if relation is None:
            return []

        targets = set()
        for i in range(relation.get_n_targets()):
            target = relation.get_target(i)
            if pred is None or pred(target):
                targets.add(target)

        # We want to avoid self-referential relationships.
        type_includes_object = [Atspi.RelationType.MEMBER_OF]
        if relation_type not in type_includes_object and obj in targets:
            tokens = ["AXObject: ", obj, "is in its own", relation_type, "target list"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            targets.remove(obj)

        return list(targets)

    @staticmethod
    def relations_as_string(obj):
        """Returns the relations associated with obj as a string"""

        if not AXObject.is_valid(obj):
            return ""

        def as_string(relations):
            return relations.value_name[15:].replace("_", "-").lower()

        def obj_as_string(acc):
            result = AXObject.get_role_name(obj)
            name = AXObject.get_name(obj)
            if name:
                result += f": '{name}'"
            if not result:
                result = "DEAD"
            return f"[{result}]"

        results = []
        for rel in AXObject.get_relations(obj):
            type_string = as_string(rel.get_relation_type())
            targets = AXObject.get_relation_targets(obj, rel.get_relation_type())
            target_string = ",".join(map(obj_as_string, targets))
            results.append(f"{type_string}: {target_string}")

        return "; ".join(results)


    @staticmethod
    def find_real_app_and_window_for(obj, app=None):
        """Work around for window events coming from mutter-x11-frames."""

        if app is None:
            try:
                app = Atspi.Accessible.get_application(obj)
            except Exception as error:
                msg = f"AXObject: Exception getting application of {obj}: {error}"
                AXObject.handle_error(obj, error, msg)
                return None, None

        if AXObject.get_name(app) != "mutter-x11-frames":
            return app, obj

        real_app = AXObject.REAL_APP_FOR_MUTTER_FRAME.get(hash(obj))
        real_frame = AXObject.REAL_FRAME_FOR_MUTTER_FRAME.get(hash(obj))
        if real_app is not None and real_frame is not None:
            return real_app, real_frame

        tokens = ["AXObject:", app, "is not valid app for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        try:
            desktop = Atspi.get_desktop(0)
        except Exception as error:
            tokens = ["AXObject: Exception getting desktop from Atspi:", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None, None

        name = AXObject.get_name(obj)
        for desktop_app in AXObject.iter_children(desktop):
            if AXObject.get_name(desktop_app) == "mutter-x11-frames":
                continue
            for frame in AXObject.iter_children(desktop_app):
                if name == AXObject.get_name(frame):
                    real_app = desktop_app
                    real_frame = frame

        tokens = ["AXObject:", real_app, "is real app for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if real_frame != obj:
            msg = "AXObject: Updated frame to frame from real app"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        AXObject.REAL_APP_FOR_MUTTER_FRAME[hash(obj)] = real_app
        AXObject.REAL_FRAME_FOR_MUTTER_FRAME[hash(obj)] = real_frame
        return real_app, real_frame

    @staticmethod
    def get_application(obj):
        """Returns the accessible application associated with obj"""

        if not AXObject.is_valid(obj):
            return None

        app = AXObject.REAL_APP_FOR_MUTTER_FRAME.get(hash(obj))
        if app is not None:
            return app

        try:
            app = Atspi.Accessible.get_application(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_application: {error}"
            AXObject.handle_error(obj, error, msg)
            return None

        if AXObject.get_name(app) != "mutter-x11-frames":
            return app

        real_app = AXObject.find_real_app_and_window_for(obj, app)[0]
        if real_app is not None:
            app = real_app

        return app

    @staticmethod
    def get_application_toolkit_name(obj):
        """Returns the toolkit name reported for obj's application."""

        if not AXObject.is_valid(obj):
            return ""

        app = AXObject.get_application(obj)
        if app is None:
            return ""

        try:
            name = Atspi.Accessible.get_toolkit_name(app)
        except Exception as error:
            tokens = ["AXObject: Exception in get_application_toolkit_name:", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return ""

        return name

    @staticmethod
    def get_application_toolkit_version(obj):
        """Returns the toolkit version reported for obj's application."""

        if not AXObject.is_valid(obj):
            return ""

        app = AXObject.get_application(obj)
        if app is None:
            return ""

        try:
            version = Atspi.Accessible.get_toolkit_version(app)
        except Exception as error:
            tokens = ["AXObject: Exception in get_application_toolkit_version:", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return ""

        return version

    @staticmethod
    def application_as_string(obj):
        """Returns the application details of obj as a string."""

        if not AXObject.is_valid(obj):
            return ""

        app = AXObject.get_application(obj)
        if app is None:
            return ""

        string = (
            f"{AXObject.get_name(app)} "
            f"({AXObject.get_application_toolkit_name(obj)} "
            f"{AXObject.get_application_toolkit_version(obj)})"
        )
        return string

    @staticmethod
    def clear_cache(obj, recursive=False, reason=""):
        """Clears the Atspi cached information associated with obj"""

        if obj is None:
            return

        tokens = ["AXObject: Clearing AT-SPI cache on", obj, f"Recursive: {recursive}."]
        if reason:
            tokens.append(f" Reason: {reason}")
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not recursive:
            try:
                Atspi.Accessible.clear_cache_single(obj)
            except Exception as error:
                msg = f"AXObject: Exception in clear_cache_single: {error}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        try:
            Atspi.Accessible.clear_cache(obj)
        except Exception as error:
            msg = f"AXObject: Exception in clear_cache: {error}"
            AXObject.handle_error(obj, error, msg)

    @staticmethod
    def get_process_id(obj):
        """Returns the process id associated with obj"""

        if not AXObject.is_valid(obj):
            return -1

        try:
            pid = Atspi.Accessible.get_process_id(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_process_id: {error}"
            AXObject.handle_error(obj, error, msg)
            return -1

        return pid

    @staticmethod
    def is_dead(obj):
        """Returns true of obj exists but is believed to be dead."""

        if obj is None:
            return False

        if not AXObject.is_valid(obj):
            return True

        try:
            # We use the Atspi function rather than the AXObject function because the
            # latter intentionally handles exceptions.
            Atspi.Accessible.get_name(obj)
        except Exception as error:
            msg = f"AXObject: Accessible is dead: {error}"
            AXObject.handle_error(obj, error, msg)
            return True

        AXObject._set_known_dead_status(obj, False)
        return False

    @staticmethod
    def get_attributes_dict(obj, use_cache=True):
        """Returns the object attributes of obj as a dictionary."""

        if not AXObject.is_valid(obj):
            return {}

        if use_cache:
            attributes = AXObject.OBJECT_ATTRIBUTES.get(hash(obj))
            if attributes:
                return attributes

        try:
            attributes = Atspi.Accessible.get_attributes(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_attributes_dict: {error}"
            AXObject.handle_error(obj, error, msg)
            return {}

        if attributes is None:
            return {}

        AXObject.OBJECT_ATTRIBUTES[hash(obj)] = attributes
        return attributes

    @staticmethod
    def get_attribute(obj, attribute_name, use_cache=True):
        """Returns the value of the specified attribute as a string."""

        if not AXObject.is_valid(obj):
            return ""

        attributes = AXObject.get_attributes_dict(obj, use_cache)
        return attributes.get(attribute_name, "")

    @staticmethod
    def attributes_as_string(obj):
        """Returns the object attributes of obj as a string."""

        if not AXObject.is_valid(obj):
            return ""

        def as_string(attribute):
            return f"{attribute[0]}:{attribute[1]}"

        return ", ".join(map(as_string, AXObject.get_attributes_dict(obj).items()))

    @staticmethod
    def get_n_actions(obj):
        """Returns the number of actions supported on obj."""

        if not AXObject.supports_action(obj):
            return 0

        try:
            count = Atspi.Action.get_n_actions(obj)
        except Exception as error:
            msg = f"AXObject: Exception in get_n_actions: {error}"
            AXObject.handle_error(obj, error, msg)
            return 0

        return count

    @staticmethod
    def _normalize_action_name(action_name):
        """Adjusts the name to account for differences in implementations."""

        if not action_name:
            return ""

        name = re.sub(r'(?<=[a-z])([A-Z])', r'-\1', action_name).lower()
        name = re.sub('[!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]', '-', name)
        return name

    @staticmethod
    def get_action_name(obj, i):
        """Returns the name of obj's action at index i."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return ""

        try:
            name = Atspi.Action.get_action_name(obj, i)
        except Exception as error:
            msg = f"AXObject: Exception in get_action_name: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return AXObject._normalize_action_name(name)

    @staticmethod
    def get_action_names(obj):
        """Returns the list of actions supported on obj."""

        results = []
        for i in range(AXObject.get_n_actions(obj)):
            name = AXObject.get_action_name(obj, i)
            if name:
                results.append(name)
        return results

    @staticmethod
    def get_action_description(obj, i):
        """Returns the description of obj's action at index i."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return ""

        try:
            description = Atspi.Action.get_action_description(obj, i)
        except Exception as error:
            msg = f"AXObject: Exception in get_action_description: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return description

    @staticmethod
    def get_action_key_binding(obj, i):
        """Returns the key binding string of obj's action at index i."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return ""

        try:
            keybinding = Atspi.Action.get_key_binding(obj, i)
        except Exception as error:
            msg = f"AXObject: Exception in get_action_key_binding: {error}"
            AXObject.handle_error(obj, error, msg)
            return ""

        return keybinding

    @staticmethod
    def has_action(obj, action_name):
        """Returns true if the named action is supported on obj."""

        return AXObject.get_action_index(obj, action_name) >= 0

    @staticmethod
    def get_action_index(obj, action_name):
        """Returns the index of the named action or -1 if unsupported."""

        action_name = AXObject._normalize_action_name(action_name)
        for i in range(AXObject.get_n_actions(obj)):
            if action_name == AXObject.get_action_name(obj, i):
                return i

        return -1

    @staticmethod
    def do_action(obj, i):
        """Invokes obj's action at index i. The return value, if true, may be
        meaningless because most implementors return true without knowing if
        the action was successfully performed."""

        if not 0 <= i < AXObject.get_n_actions(obj):
            return False

        try:
            result = Atspi.Action.do_action(obj, i)
        except Exception as error:
            msg = f"AXObject: Exception in do_action: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        return result

    @staticmethod
    def do_named_action(obj, action_name):
        """Invokes the named action on obj. The return value, if true, may be
        meaningless because most implementors return true without knowing if
        the action was successfully performed."""

        index = AXObject.get_action_index(obj, action_name)
        if index == -1:
            tokens = ["INFO:", action_name, "not an available action for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        return AXObject.do_action(obj, index)

    @staticmethod
    def actions_as_string(obj):
        """Returns information about the actions as a string."""

        results = []
        for i in range(AXObject.get_n_actions(obj)):
            result = AXObject.get_action_name(obj, i)
            keybinding = AXObject.get_action_key_binding(obj, i)
            if keybinding:
                result += f" ({keybinding})"
            results.append(result)

        return "; ".join(results)

    @staticmethod
    def grab_focus(obj):
        """Attempts to grab focus on obj. Returns true if successful."""

        if not AXObject.supports_component(obj):
            return False

        try:
            result = Atspi.Component.grab_focus(obj)
        except Exception as error:
            msg = f"AXObject: Exception in grab_focus: {error}"
            AXObject.handle_error(obj, error, msg)
            return False

        if debug.LEVEL_INFO < debug.debugLevel:
            return result

        if result and not AXObject.has_state(obj, Atspi.StateType.FOCUSED):
            tokens = ["AXObject:", obj, "lacks focused state after focus grab"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return result

AXObject.start_cache_clearing_thread()
