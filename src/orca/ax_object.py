# Utilites for obtaining information about accessible objects.
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
    def get_parent_checked(obj):
        """Returns the parent of obj, doing checks for tree validity"""

        if obj is None:
            return None

        if Atspi.Accessible.get_role(obj) == Atspi.Role.APPLICATION:
            return None

        parent = Atspi.Accessible.get_parent(obj)
        if parent is None:
            return None

        if parent == obj:
            msg = "ERROR: %s claims to be its own parent" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if debug.LEVEL_INFO < debug.debugLevel:
            return parent

        try:
            index = Atspi.Accessible.get_index_in_parent(obj)
        except Exception as e:
            msg = "ERROR: Exception getting index in parent for %s: %s" % (obj, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return parent

        try:
            nchildren = Atspi.Accessible.get_child_count(parent)
        except Exception as e:
            msg = "ERROR: Exception getting child count for %s: %s" % (parent, e)
            debug.println(debug.LEVEL_INFO, msg, True)
            return parent

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
    def get_child_checked(obj, index):
        """Returns the nth child of obj, doing checks for tree validity"""

        if obj is None:
            return None

        try:
            child = Atspi.Accessible.get_child_at_index(obj, index)
        except Exception as e:
            msg = "ERROR: Exception in get_child_checked: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if child == obj:
            msg = "ERROR: %s claims to be its own child" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if debug.LEVEL_INFO < debug.debugLevel:
            return child

        parent = Atspi.Accessible.get_parent(child)
        if obj != parent:
           msg = "ERROR: %s claims %s as child; child's parent is %s" % (obj, child, parent)
           debug.println(debug.LEVEL_INFO, msg, True)

        return child

    @staticmethod
    def find_descendant(obj, pred):
        """Returns the ancestor of obj if the function pred is true"""

        if obj is None:
            return None

        try:
            nchildren = Atspi.Accessible.get_child_count(obj)
        except Exception as e:
            msg = "ERROR: Exception in find_descendant: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        for i in range(nchildren):
            child = AXObject.get_child_checked(obj, i)
            if child and pred(child):
                return child

            child = AXObject.find_descendant(child, pred)
            if child and pred(child):
                return child

        return None
