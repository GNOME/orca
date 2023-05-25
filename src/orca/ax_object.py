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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug


class AXObject:

    @staticmethod
    def supports_action(obj):
        """Returns True if the action interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_action_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_action_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_collection(obj):
        """Returns True if the collection interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_collection_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_collection_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_component(obj):
        """Returns True if the component interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_component_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_component_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None


    @staticmethod
    def supports_document(obj):
        """Returns True if the document interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_document_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_document_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_editable_text(obj):
        """Returns True if the editable-text interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_editable_text_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_editable_text_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_hyperlink(obj):
        """Returns True if the hyperlink interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_hyperlink(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_hyperlink on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_hypertext(obj):
        """Returns True if the hypertext interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_hypertext_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_hypertext_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_image(obj):
        """Returns True if the image interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_image_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_image_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_selection(obj):
        """Returns True if the selection interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_selection_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_selection_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_table(obj):
        """Returns True if the table interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_table_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_table_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_table_cell(obj):
        """Returns True if the table cell interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_table_cell(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_table_cell on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supports_text(obj):
        """Returns True if the text interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_text_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_text_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        return iface is not None

    @staticmethod
    def supports_value(obj):
        """Returns True if the value interface is supported on obj"""

        if obj is None:
            return False

        try:
            iface = Atspi.Accessible.get_value_iface(obj)
        except NotImplementedError:
            return False
        except Exception as e:
            msg = "ERROR: Exception calling get_value_iface on %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return iface is not None

    @staticmethod
    def supported_interfaces_as_string(obj):
        """Returns the supported interfaces of obj as a string"""

        if obj is None:
            return ""

        ifaces = []
        if AXObject.supports_action(obj):
            ifaces.append("Action")
        if AXObject.supports_collection(obj):
            ifaces.append("Collection")
        if AXObject.supports_component(obj):
            ifaces.append("Component")
        if AXObject.supports_document(obj):
            ifaces.append("Document")
        if AXObject.supports_editable_text(obj):
            ifaces.append("EditableText")
        if AXObject.supports_hyperlink(obj):
            ifaces.append("Hyperlink")
        if AXObject.supports_hypertext(obj):
            ifaces.append("Hypertext")
        if AXObject.supports_image(obj):
            ifaces.append("Image")
        if AXObject.supports_selection(obj):
            ifaces.append("Selection")
        if AXObject.supports_table(obj):
            ifaces.append("Table")
        if AXObject.supports_table_cell(obj):
            ifaces.append("TableCell")
        if AXObject.supports_text(obj):
            ifaces.append("Text")
        if AXObject.supports_value(obj):
            ifaces.append("Value")
        return ", ".join(ifaces)

    @staticmethod
    def get_path(obj):
        """Returns the path from application to obj as list of child indices"""

        if obj is None:
            return []

        path = []
        acc = obj
        while acc:
            try:
                path.append(Atspi.Accessible.get_index_in_parent(acc))
            except Exception as e:
                msg = "ERROR: Exception getting index in parent for %s: %s" % (acc, e)
                debug.println(debug.LEVEL_INFO, msg, True)
                return []
            acc = AXObject.get_parent_checked(acc)

        path.reverse()
        return path

    @staticmethod
    def get_index_in_parent(obj):
        """Returns the child index of obj within its parent"""

        if obj is None:
            return -1

        try:
            index = Atspi.Accessible.get_index_in_parent(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_index_in_parent: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return -1

        return index

    @staticmethod
    def get_parent(obj):
        """Returns the accessible parent of obj. See also get_parent_checked."""

        if obj is None:
            return None

        try:
            parent = Atspi.Accessible.get_parent(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_parent: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if parent == obj:
            msg = "ERROR: %s claims to be its own parent" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return parent

    @staticmethod
    def get_parent_checked(obj):
        """Returns the parent of obj, doing checks for tree validity"""

        if obj is None:
            return None

        role = AXObject.get_role(obj)
        if role in [Atspi.Role.INVALID, Atspi.Role.APPLICATION]:
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        if debug.LEVEL_INFO < debug.debugLevel:
            return parent

        index = AXObject.get_index_in_parent(obj)
        nchildren = AXObject.get_child_count(parent)
        if index < 0 or index > nchildren:
            msg = "ERROR: %s has index %i; parent %s has %i children" % \
                (obj, index, parent, nchildren)
            debug.println(debug.LEVEL_INFO, msg, True)
            return parent

        try:
            child = Atspi.Accessible.get_child_at_index(parent, index)
        except Exception as e:
            msg = "ERROR: Exception in get_parent_checked: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return parent

        if child != obj:
           msg = "ERROR: %s's child at %i is %s; not obj %s" % (parent, index, child, obj)
           debug.println(debug.LEVEL_INFO, msg, True)

        return parent

    @staticmethod
    def find_ancestor(obj, pred):
        """Returns the ancestor of obj if the function pred is true"""

        if obj is None:
            return None

        # Keep track of objects we've encountered in order to handle broken trees.
        objects = [obj]
        parent = AXObject.get_parent_checked(obj)
        while parent:
            if parent in objects:
                msg = "ERROR: Circular tree suspected in find_ancestor. " \
                      "%s already in: %s" % (parent, " ".join(map(str, objects)))
                debug.println(debug.LEVEL_INFO, msg, True)
                return None

            if pred(parent):
                return parent

            objects.append(parent)
            parent = AXObject.get_parent_checked(parent)

        return None

    @staticmethod
    def get_child(obj, index):
        """Returns the nth child of obj. See also get_child_checked."""

        if obj is None:
            return None

        n_children = AXObject.get_child_count(obj)
        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not (0 <= index < n_children):
            return None

        try:
            child = Atspi.Accessible.get_child_at_index(obj, index)
        except Exception as e:
            msg = "ERROR: Exception in get_child: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if child == obj:
            msg = "ERROR: %s claims to be its own child" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return child

    @staticmethod
    def get_child_checked(obj, index):
        """Returns the nth child of obj, doing checks for tree validity"""

        child = AXObject.get_child(obj, index)
        if debug.LEVEL_INFO < debug.debugLevel:
            return child

        parent = AXObject.get_parent(child)
        if obj != parent:
           msg = "ERROR: %s claims %s as child; child's parent is %s" % (obj, child, parent)
           debug.println(debug.LEVEL_INFO, msg, True)

        return child

    @staticmethod
    def find_descendant(obj, pred):
        """Returns the descendant of obj if the function pred is true"""

        if obj is None:
            return None

        nchildren = AXObject.get_child_count(obj)
        for i in range(nchildren):
            child = AXObject.get_child_checked(obj, i)
            if child and pred(child):
                return child

            child = AXObject.find_descendant(child, pred)
            if child and pred(child):
                return child

        return None

    @staticmethod
    def get_role(obj):
        """Returns the accessible role of obj"""

        if obj is None:
            return Atspi.Role.INVALID

        try:
            role = Atspi.Accessible.get_role(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_role: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return Atspi.Role.INVALID

        return role

    @staticmethod
    def get_role_name(obj):
        """Returns the accessible role name of obj"""

        if obj is None:
            return ""

        try:
            role_name = Atspi.Accessible.get_role_name(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_role_name: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return ""

        return role_name

    @staticmethod
    def get_name(obj):
        """Returns the accessible name of obj"""

        if obj is None:
            return ""

        try:
            name = Atspi.Accessible.get_name(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_name: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return ""

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

        if obj is None:
            return ""

        try:
            description = Atspi.Accessible.get_description(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_description: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return ""

        return description

    @staticmethod
    def get_child_count(obj):
        """Returns the child count of obj"""

        if obj is None:
            return 0

        try:
            count = Atspi.Accessible.get_child_count(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_child_count: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0

        return count

    @staticmethod
    def iter_children(obj, pred=None):
        """Generator to iterate through obj's children. If the function pred is
        specified, children for which pred is False will be skipped."""

        if obj is None:
            return

        child_count = AXObject.get_child_count(obj)
        for index in range(child_count):
            child = AXObject.get_child(obj, index)
            if child is not None and (pred is None or pred(child)):
                yield child

    @staticmethod
    def get_previous_sibling(obj):
        """Returns the previous sibling of obj, based on child indices"""

        if obj is None:
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        index = AXObject.get_index_in_parent(obj)
        if index <= 0:
            return None

        sibling = AXObject.get_child(parent, index - 1)
        if sibling == obj:
            msg = "ERROR: %s claims to be its own sibling" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return sibling

    @staticmethod
    def get_next_sibling(obj):
        """Returns the next sibling of obj, based on child indices"""

        if obj is None:
            return None

        parent = AXObject.get_parent(obj)
        if parent is None:
            return None

        index = AXObject.get_index_in_parent(obj)
        if index < 0:
            return None

        sibling = AXObject.get_child(parent, index + 1)
        if sibling == obj:
            msg = "ERROR: %s claims to be its own sibling" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return sibling

    @staticmethod
    def get_next_object(obj):
        """Returns the next object (depth first) in the accessibility tree"""

        if obj is None:
            return None

        index = AXObject.get_index_in_parent(obj) + 1
        parent = AXObject.get_parent(obj)
        while parent and not (0 < index < AXObject.get_child_count(parent)):
            obj = parent
            index = AXObject.get_index_in_parent(obj) + 1
            parent = AXObject.get_parent(obj)

        if parent is None:
            return None

        next_object = AXObject.get_child(parent, index)
        if next_object == obj:
            msg = "ERROR: %s claims to be its own next object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return next_object

    @staticmethod
    def get_previous_object(obj):
        """Returns the previous object (depth first) in the accessibility tree"""

        if obj is None:
            return None

        index = AXObject.get_index_in_parent(obj) - 1
        parent = AXObject.get_parent(obj)
        while parent and not (0 <= index < AXObject.get_child_count(parent) - 1):
            obj = parent
            index = AXObject.get_index_in_parent(obj) - 1
            parent = AXObject.get_parent(obj)

        if parent is None:
            return None

        previous_object = AXObject.get_child(parent, index)
        if previous_object == obj:
            msg = "ERROR: %s claims to be its own previous object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return previous_object

    @staticmethod
    def get_state_set(obj):
        """Returns the state set associated with obj"""

        if obj is None:
            return Atspi.StateSet()

        try:
            state_set = Atspi.Accessible.get_state_set(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_state_set: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return Atspi.StateSet()

        return state_set

    @staticmethod
    def has_state(obj, state):
        """Returns true if obj has the specified state"""

        if obj is None:
            return False

        return AXObject.get_state_set(obj).contains(state)

    @staticmethod
    def state_set_as_string(obj):
        """Returns the state set associated with obj as a string"""

        as_string = lambda x: x.value_name[12:].replace("_", "-").lower()
        return ", ".join(map(as_string, AXObject.get_state_set(obj).getStates()))

    @staticmethod
    def get_relations(obj):
        """Returns the list of Atspi.Relation objects associated with obj"""

        if obj is None:
            return []

        try:
            relations = Atspi.Accessible.get_relation_set(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_relations: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        return relations

    @staticmethod
    def get_relation(obj, relation_type):
        """Returns the specified Atspi.Relation for obj"""

        if obj is None:
            return None

        for relation in AXObject.get_relations(obj):
            if relation and relation.get_relation_type() == relation_type:
                return relation

        return None

    @staticmethod
    def has_relation(obj, relation_type):
        """Returns true if obj has the specified relation type"""

        return AXObject.get_relation(obj, relation_type) is not None

    @staticmethod
    def get_relation_targets(obj, relation_type, pred=None):
        """Returns the list of targets with the specified relation type to obj.
        If pred is provided, a target will only be included if pred is true."""

        if obj is None:
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
        if not relation_type in type_includes_object and obj in targets:
            msg = 'ERROR: %s is in its own %s target list' % (obj, relation_type)
            debug.println(debug.LEVEL_INFO, msg, True)
            targets.remove(obj)

        return list(targets)

    @staticmethod
    def relations_as_string(obj):
        """Returns the relations associated with obj as a string"""

        as_string = lambda x: x.value_name[15:].replace("_", "-").lower()
        relations = [r.get_relation_type() for r in AXObject.get_relations(obj)]
        return ", ".join(map(as_string, relations))

    @staticmethod
    def get_application(obj):
        """Returns the accessible application associated with obj"""

        if obj is None:
            return None

        try:
            app = Atspi.Accessible.get_application(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_application: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return app

    @staticmethod
    def clear_cache(obj):
        """Clears the Atspi cached information associated with obj"""

        if obj is None:
            return

        try:
            Atspi.Accessible.clear_cache(obj)
        except Exception as e:
            msg = "ERROR: Exception in clear_cache: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
