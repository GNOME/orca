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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-positional-arguments

"""Utilities for obtaining objects via the collection interface."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from .ax_object import AXObject


class AXCollection:
    """Utilities for obtaining objects via the collection interface."""

    # Too many arguments and too many local variables.
    # This function wraps Atspi.MatchRule.new which has all the arguments.
    # pylint: disable=R0913,R0914
    @staticmethod
    def create_match_rule(
        states: list[str] | None = None,
        state_match_type: Atspi.CollectionMatchType = Atspi.CollectionMatchType.ALL,
        attributes: list[str] | None = None,
        attribute_match_type: Atspi.CollectionMatchType = Atspi.CollectionMatchType.ANY,
        roles: list[str] | None = None,
        role_match_type: Atspi.CollectionMatchType = Atspi.CollectionMatchType.ANY,
        interfaces: list[str] | None = None,
        interface_match_type: Atspi.CollectionMatchType = Atspi.CollectionMatchType.ALL,
        invert: bool = False) -> Atspi.MatchRule | None:
        """Creates a match rule based on the supplied criteria."""

        if states is None:
            states = []
        if attributes is None:
            attributes = []
        if roles is None:
            roles = []
        if interfaces is None:
            interfaces = []

        state_set = Atspi.StateSet()
        if states:
            for state in states:
                state_set.add(state)

        attributes_dict: dict[str, str] = {}
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
        except GLib.GError as error:
            tokens = ["AXCollection: Exception in create_match_rule:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return rule
    # pylint: enable=R0913,R0914

    @staticmethod
    def get_all_matches(
        obj: Atspi.Accessible,
        rule: Atspi.MatchRule,
            order: Atspi.CollectionSortOrder = Atspi.CollectionSortOrder.CANONICAL
        ) -> list[Atspi.Accessible]:
        """Returns a list of objects matching the specified rule."""

        if not AXObject.supports_collection(obj):
            tokens = ["AXCollection:", obj, "does not implement this interface."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        if rule is None:
            return []

        start = time.time()
        try:
            # 0 means no limit on the number of results
            # The final argument, traverse, is not supported but is expected.
            matches = Atspi.Collection.get_matches(obj, rule, order, 0, True)
        except GLib.GError as error:
            tokens = ["AXCollection: Exception in get_all_matches:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        msg = f"AXCollection: {len(matches)} match(es) found in {time.time() - start:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return matches

    @staticmethod
    def get_first_match(
        obj: Atspi.Accessible,
        rule: Atspi.MatchRule,
        order: Atspi.CollectionSortOrder = Atspi.CollectionSortOrder.CANONICAL
    ) -> Atspi.Accessible | None:
        """Returns the first object matching the specified rule."""

        if not AXObject.supports_collection(obj):
            tokens = ["AXCollection:", obj, "does not implement this interface."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if rule is None:
            return None

        start = time.time()
        try:
            # 1 means limit the number of results to 1
            # The final argument, traverse, is not supported but is expected.
            matches = Atspi.Collection.get_matches(obj, rule, order, 1, True)
        except GLib.GError as error:
            tokens = ["AXCollection: Exception in get_first_match:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        match = None
        if matches:
            match = matches[0]

        tokens = ["AXCollection: found", match, f"in {time.time() - start:.4f}s"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return match
