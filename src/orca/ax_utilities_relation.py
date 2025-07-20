# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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
# pylint: disable=too-many-public-methods

"""Utilities for obtaining relation-related information."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import threading
import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from .ax_object import AXObject


class AXUtilitiesRelation:
    """Utilities for obtaining relation-related information."""

    RELATIONS: dict[int, list[Atspi.Relation]] = {}
    TARGETS: dict[int, dict[Atspi.RelationType, list[Atspi.Accessible]]] = {}

    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data() -> None:
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXUtilitiesRelation._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason: str = "") -> None:
        msg = "AXUtilitiesRelation: Clearing local cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        with AXUtilitiesRelation._lock:
            AXUtilitiesRelation.RELATIONS.clear()
            AXUtilitiesRelation.TARGETS.clear()

    @staticmethod
    def clear_cache_now(reason: str = "") -> None:
        """Clears all cached information immediately."""

        AXUtilitiesRelation._clear_all_dictionaries(reason)

    @staticmethod
    def start_cache_clearing_thread() -> None:
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXUtilitiesRelation._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def get_relations(obj: Atspi.Accessible) -> list[Atspi.Relation]:
        """Returns the list of Atspi.Relation objects associated with obj"""

        if not AXObject.is_valid(obj):
            return []

        relations = AXUtilitiesRelation.RELATIONS.get(hash(obj))
        if relations is not None:
            return relations

        try:
            relations = Atspi.Accessible.get_relation_set(obj)
        except GLib.GError as error:
            msg = f"AXUtilitiesRelation: Exception in get_relations: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        AXUtilitiesRelation.RELATIONS[hash(obj)] = relations
        return relations

    @staticmethod
    def _get_relation(
        obj: Atspi.Accessible,
        relation_type: Atspi.RelationType
    ) -> Atspi.Relation | None:
        """Returns the specified Atspi.Relation for obj"""

        for relation in AXUtilitiesRelation.get_relations(obj):
            if relation and relation.get_relation_type() == relation_type:
                return relation

        return None

    @staticmethod
    def get_relation_targets_for_debugging(
        obj: Atspi.Accessible, relation_type: Atspi.RelationType
    ) -> list[Atspi.Accessible]:
        """Returns the list of targets with the specified relation type to obj."""

        return AXUtilitiesRelation._get_relation_targets(obj, relation_type)

    @staticmethod
    def _get_relation_targets(
        obj: Atspi.Accessible,
        relation_type: Atspi.RelationType
    ) -> list[Atspi.Accessible]:
        """Returns the list of targets with the specified relation type to obj."""

        cached_targets = AXUtilitiesRelation.TARGETS.get(hash(obj), {})
        cached_relation = cached_targets.get(relation_type)
        if isinstance(cached_relation, list):
            return cached_relation

        relation = AXUtilitiesRelation._get_relation(obj, relation_type)
        if relation is None:
            cached_targets[relation_type] = []
            AXUtilitiesRelation.TARGETS[hash(obj)] = cached_targets
            return []

        targets = set()
        for i in range(relation.get_n_targets()):
            if target := relation.get_target(i):
                targets.add(target)

        # We want to avoid self-referential relationships.
        type_includes_object = [Atspi.RelationType.MEMBER_OF]
        if relation_type not in type_includes_object and obj in targets:
            tokens = ["AXUtilitiesRelation: ", obj, "is in its own", relation_type, "target list"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            targets.remove(obj)

        result = list(targets)
        cached_targets[relation_type] = result
        AXUtilitiesRelation.TARGETS[hash(obj)] = cached_targets
        return result

    @staticmethod
    def get_is_controlled_by(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is controlled by."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.CONTROLLED_BY)
        tokens = ["AXUtilitiesRelation:", obj, "is controlled by:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_controller_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the controller for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.CONTROLLER_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "is controller for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_described_by(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is described by."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.DESCRIBED_BY)
        tokens = ["AXUtilitiesRelation:", obj, "is described by:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_description_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the description for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.DESCRIPTION_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "is description for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_details(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that contain details for obj."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.DETAILS)
        tokens = ["AXUtilitiesRelation:", obj, "has details in:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_details_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj contains details for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.DETAILS_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "contains details for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_embedded_by(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is embedded by."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.EMBEDDED_BY)
        tokens = ["AXUtilitiesRelation:", obj, "is embedded by:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_embeds(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj embeds."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.EMBEDS)
        tokens = ["AXUtilitiesRelation:", obj, "embeds:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_error_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj contains an error message for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.ERROR_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "is error for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_error_message(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that contain an error message for obj."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.ERROR_MESSAGE)
        tokens = ["AXUtilitiesRelation:", obj, "has error messages in:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_flows_from(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj flows from."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.FLOWS_FROM)
        tokens = ["AXUtilitiesRelation:", obj, "flows from:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_flows_to(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj flows to."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.FLOWS_TO)
        tokens = ["AXUtilitiesRelation:", obj, "flows to:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_label_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the label for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.LABEL_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "is label for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_labelled_by(
        obj: Atspi.Accessible,
        exclude_ancestors: bool = True
    ) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is labelled by."""

        def is_not_ancestor(acc):
            return not AXObject.is_ancestor(obj, acc)

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.LABELLED_BY)
        if exclude_ancestors:
            result = list(filter(is_not_ancestor, result))

        tokens = ["AXUtilitiesRelation:", obj, "is labelled by:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_member_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is a member of."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.MEMBER_OF)
        tokens = ["AXUtilitiesRelation:", obj, "is member of:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_node_child_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the node child of."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.NODE_CHILD_OF)
        tokens = ["AXUtilitiesRelation:", obj, "is node child of:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_node_parent_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the node parent of."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.NODE_PARENT_OF)
        tokens = ["AXUtilitiesRelation:", obj, "is node parent of:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_parent_window_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is a parent window of."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.PARENT_WINDOW_OF)
        tokens = ["AXUtilitiesRelation:", obj, "is parent window of:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_popup_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the popup for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.POPUP_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "is popup for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_subwindow_of(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is a subwindow of."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.SUBWINDOW_OF)
        tokens = ["AXUtilitiesRelation:", obj, "is subwindow of:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_is_tooltip_for(obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of accessible objects that obj is the tooltip for."""

        result = AXUtilitiesRelation._get_relation_targets(obj, Atspi.RelationType.TOOLTIP_FOR)
        tokens = ["AXUtilitiesRelation:", obj, "is tooltip for:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def object_is_controlled_by(obj1: Atspi.Accessible, obj2: Atspi.Accessible) -> bool:
        """Returns True if obj1 is controlled by obj2."""

        targets = AXUtilitiesRelation._get_relation_targets(obj1, Atspi.RelationType.CONTROLLED_BY)
        result = obj2 in targets
        tokens = ["AXUtilitiesRelation:", obj1, "is controlled by", obj2, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def object_is_unrelated(obj: Atspi.Accessible) -> bool:
        """Returns True if obj does not have any relations."""

        return not AXUtilitiesRelation.get_relations(obj)

AXUtilitiesRelation.start_cache_clearing_thread()
