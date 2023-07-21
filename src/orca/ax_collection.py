# Utilities for obtaining objects via the collection interface.
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
Utilities for obtaining objects via the collection interface.
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


class AXCollection:

    @staticmethod
    def create_match_rule(states=[],
                          state_match_type=Atspi.CollectionMatchType.ALL,
                          attributes=[],
                          attribute_match_type=Atspi.CollectionMatchType.ANY,
                          roles=[],
                          role_match_type=Atspi.CollectionMatchType.ANY,
                          interfaces=[],
                          interface_match_type=Atspi.CollectionMatchType.ALL,
                          invert=False):
        """Creates a match rule based on the supplied criteria."""

        state_set = Atspi.StateSet()
        if states:
            for state in states:
                state_set.add(state)

        attributes_dict = {}
        if attributes:
            for attr in attributes:
                key, value = attr.split(":", 1)
                value = value.replace(":", r"\:")
                if key in attributes_dict:
                    attributes_dict[key] = attributes_dict[key] + ":" + value
                else:
                    attributes_dict[key] = value

        try:
            rule = Atspi.MatchRule.new(state_set,
                                       state_match_type,
                                       attributes_dict,
                                       attribute_match_type,
                                       roles,
                                       role_match_type,
                                       interfaces,
                                       interface_match_type,
                                       invert)
        except Exception as e:
            msg = "AXCollection: Exception in create_match_rule: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return rule

    @staticmethod
    def get_all_matches(obj, rule, order=Atspi.CollectionSortOrder.CANONICAL):
        """Returns a list of objects matching the specified rule."""

        if not AXObject.supports_collection(obj):
            return []

        if rule is None:
            return []

        try:
            # 0 means no limit on the number of results
            # The final argument, traverse, is not supported but is expected.
            matches = Atspi.Collection.get_matches(obj, rule, order, 0, True)
        except Exception as e:
            msg = "AXCollection: Exception in get_all_matches: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        return matches

    @staticmethod
    def get_first_match(obj, rule, order=Atspi.CollectionSortOrder.CANONICAL):
        """Returns the first object matching the specified rule."""

        if not AXObject.supports_collection(obj):
            return None

        if rule is None:
            return None

        try:
            # 1 means limit the number of results to 1
            # The final argument, traverse, is not supported but is expected.
            matches = Atspi.Collection.get_matches(obj, rule, order, 1, True)
        except Exception as e:
            msg = "AXCollection: Exception in get_first_match: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if matches:
            return matches[0]

        return None
