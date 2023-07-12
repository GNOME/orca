# Utilities for obtaining information about containers supporting selection
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
Utilities for obtaining information about containers supporting selection.
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
from .ax_object import AXObject


class AXSelection:

    @staticmethod
    def get_selected_child_count(obj):
        """Returns the selected child count of obj"""

        if not AXObject.supports_selection(obj):
            return 0

        try:
            count = Atspi.Selection.get_n_selected_children(obj)
        except Exception as e:
            msg = "ERROR: Exception in get_selected_child_count: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0

        msg = "AXSelection: %s reports %i selected children" % (obj, count)
        debug.println(debug.LEVEL_INFO, msg, True)
        return count

    @staticmethod
    def get_selected_child(obj, index):
        """Returns the nth selected child of obj."""

        n_children = AXSelection.get_selected_child_count(obj)
        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not (0 <= index < n_children):
            return None

        try:
            child = Atspi.Selection.get_selected_child(obj, index)
        except Exception as e:
            msg = "ERROR: Exception in get_selected_child: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if child == obj:
            msg = "ERROR: %s claims to be its own selected child" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        msg = "AXSelection: %s is selected child #%i of %s" % (child, index, obj)
        debug.println(debug.LEVEL_INFO, msg, True)
        return child

    @staticmethod
    def get_selected_children(obj):
        """Returns a list of all the selected children of obj."""

        count = AXSelection.get_selected_child_count(obj)
        children = set()
        for i in range(count):
            try:
                child = Atspi.Selection.get_selected_child(obj, i)
            except Exception as e:
                msg = "ERROR: Exception in get_selected_children: %s" % e
                debug.println(debug.LEVEL_INFO, msg, True)
                return []

            if child is not None:
                children.add(child)

        if obj in children:
            msg = "ERROR: %s claims to be its own selected child" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            children.remove(obj)

        result = list(children)
        if len(result) != count:
            msg = "ERROR: Selected child count of %s is %i" % (obj, count)
            debug.println(debug.LEVEL_INFO, msg, True)

        return result
