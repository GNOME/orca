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
