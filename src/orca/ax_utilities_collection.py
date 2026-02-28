# Orca
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

# pylint: disable=too-many-public-methods

"""Utilities for finding accessible objects via the collection interface."""

import inspect
import time
from collections.abc import Callable

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_collection import AXCollection
from .ax_utilities_action import AXUtilitiesAction
from .ax_utilities_debugging import AXUtilitiesDebugging
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState


class AXUtilitiesCollection:
    """Utilities for finding accessible objects via the collection interface."""

    @staticmethod
    def _apply_predicate(
        matches: list[Atspi.Accessible],
        pred: Callable[[Atspi.Accessible], bool],
    ) -> list[Atspi.Accessible]:
        if not matches:
            return []

        start = time.time()
        tokens = ["AXUtilitiesCollection: Applying predicate ", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        matches = list(filter(pred, matches))
        msg = f"AXUtilitiesCollection: {len(matches)} matches found in {time.time() - start:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return matches

    @staticmethod
    def _find_all_with_states(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        state_match_type: Atspi.CollectionMatchType,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        if not (root and state_list):
            return []

        state_list = list(state_list)
        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            state_match_type,
            "of:",
            state_list,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(states=state_list, state_match_type=state_match_type)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def _find_all_with_role(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        role_match_type: Atspi.CollectionMatchType,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        if not (root and role_list):
            return []

        role_list = list(role_list)
        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            role_match_type,
            "of:",
            role_list,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(roles=role_list, role_match_type=role_match_type)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_role(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the specified roles"""

        return AXUtilitiesCollection._find_all_with_role(
            root,
            role_list,
            Atspi.CollectionMatchType.ANY,
            pred,
        )

    @staticmethod
    def find_all_with_role_and_all_states(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the roles, and all the states"""

        if not (root and role_list and state_list):
            return []

        role_list = list(role_list)
        state_list = list(state_list)
        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            "Roles:",
            role_list,
            "States:",
            state_list,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(
            roles=role_list,
            role_match_type=Atspi.CollectionMatchType.ANY,
            states=state_list,
            state_match_type=Atspi.CollectionMatchType.ALL,
        )
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_role_without_states(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the roles, and none of the states"""

        if not (root and role_list and state_list):
            return []

        role_list = list(role_list)
        state_list = list(state_list)
        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            "Roles:",
            role_list,
            "States:",
            state_list,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(
            roles=role_list,
            role_match_type=Atspi.CollectionMatchType.ANY,
            states=state_list,
            state_match_type=Atspi.CollectionMatchType.NONE,
        )
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_states(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which have all of the specified states"""

        return AXUtilitiesCollection._find_all_with_states(
            root,
            state_list,
            Atspi.CollectionMatchType.ALL,
            pred,
        )

    @staticmethod
    def find_all_block_quotes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the block quote role"""

        roles = [Atspi.Role.BLOCK_QUOTE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the push- or toggle-button role"""

        roles = [Atspi.Role.BUTTON, Atspi.Role.TOGGLE_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_canvases(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the canvas role"""

        roles = [Atspi.Role.CANVAS]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_check_boxes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the checkbox role"""

        roles = [Atspi.Role.CHECK_BOX]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_clickables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all non-focusable descendants of root which support the click action"""

        if root is None:
            return []

        interfaces = ["Action"]
        states = [Atspi.StateType.FOCUSABLE]
        state_match_type = Atspi.CollectionMatchType.NONE
        roles = AXUtilitiesRole.get_roles_to_exclude_from_clickables_list()
        roles_match_type = Atspi.CollectionMatchType.NONE
        attributes = ["xml-roles:gridcell"]
        attribute_match_type = Atspi.CollectionMatchType.NONE

        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            roles_match_type,
            "of:",
            roles,
            ". pred:",
            pred,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        def is_match(obj):
            result = AXUtilitiesAction.has_action(obj, "click")
            tokens = [
                "AXUtilitiesCollection:",
                obj,
                AXUtilitiesDebugging.actions_as_string(obj),
                "has click Action:",
                result,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if not result:
                return False
            return pred is None or pred(obj)

        rule = AXCollection.create_match_rule(
            interfaces=interfaces,
            attributes=attributes,
            attribute_match_type=attribute_match_type,
            roles=roles,
            role_match_type=roles_match_type,
            states=states,
            state_match_type=state_match_type,
        )
        matches = AXCollection.get_all_matches(root, rule)
        matches = AXUtilitiesCollection._apply_predicate(matches, is_match)
        return matches

    @staticmethod
    def find_all_combo_boxes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the combobox role"""

        roles = [Atspi.Role.COMBO_BOX]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_description_terms(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the description term role"""

        roles = [Atspi.Role.DESCRIPTION_TERM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_editable_objects(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are editable"""

        states = [Atspi.StateType.EDITABLE]
        if must_be_focusable:
            states.append(Atspi.StateType.FOCUSABLE)
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_entries(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the entry role"""

        roles = [Atspi.Role.ENTRY]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_focusable_objects_with_click_ancestor(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all focusable descendants of root which support the click-ancestor action"""

        if root is None:
            return []

        interfaces = ["Action"]
        states = [Atspi.StateType.FOCUSABLE]
        state_match_type = Atspi.CollectionMatchType.ANY
        roles = AXUtilitiesRole.get_roles_to_exclude_from_clickables_list()
        roles_match_type = Atspi.CollectionMatchType.NONE

        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            roles_match_type,
            "of:",
            roles,
            ". pred:",
            pred,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        def is_match(obj):
            result = AXUtilitiesAction.has_action(obj, "click-ancestor")
            tokens = [
                "AXUtilitiesCollection:",
                obj,
                AXUtilitiesDebugging.actions_as_string(obj),
                "has click-ancestor Action:",
                result,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if not result:
                return False
            return pred is None or pred(obj)

        rule = AXCollection.create_match_rule(
            interfaces=interfaces,
            roles=roles,
            role_match_type=roles_match_type,
            states=states,
            state_match_type=state_match_type,
        )
        matches = AXCollection.get_all_matches(root, rule)
        matches = AXUtilitiesCollection._apply_predicate(matches, is_match)
        return matches

    @staticmethod
    def find_all_form_fields(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with a form-field-related role"""

        roles = AXUtilitiesRole.get_form_field_roles()
        if not must_be_focusable:
            return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

        states = [Atspi.StateType.FOCUSABLE]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_grids(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that are grids"""

        if root is None:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(), "Root:", root, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        roles = [Atspi.Role.TABLE]
        attributes = ["xml-roles:grid"]
        rule = AXCollection.create_match_rule(roles=roles, attributes=attributes)
        grids = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            AXUtilitiesCollection._apply_predicate(grids, pred)

        return grids

    @staticmethod
    def find_all_headings(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the heading role"""

        roles = [Atspi.Role.HEADING]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_headings_at_level(
        root: Atspi.Accessible,
        level: int,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the heading role"""

        if root is None:
            return []

        tokens = [
            "AXUtilitiesCollection:",
            inspect.currentframe(),
            "Root:",
            root,
            "Level:",
            level,
            "pred:",
            pred,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        roles = [Atspi.Role.HEADING]
        attributes = [f"level:{level}"]
        rule = AXCollection.create_match_rule(roles=roles, attributes=attributes)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)
        return matches

    @staticmethod
    def find_all_images_and_image_maps(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the image or image map role"""

        roles = [Atspi.Role.IMAGE, Atspi.Role.IMAGE_MAP]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_internal_frames(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the internal frame role"""

        roles = [Atspi.Role.INTERNAL_FRAME]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_labels(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the label role"""

        roles = [Atspi.Role.LABEL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_landmarks(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the landmark role"""

        roles = [Atspi.Role.LANDMARK]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the link role"""

        roles = [Atspi.Role.LINK]
        if not must_be_focusable:
            return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

        states = [Atspi.StateType.FOCUSABLE]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_live_regions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that are live regions"""

        if root is None:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(), "Root:", root, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        levels = ["off", "polite", "assertive"]
        attributes = ["container-live:" + level for level in levels]

        rule = AXCollection.create_match_rule(
            attributes=attributes,
            attribute_match_type=Atspi.CollectionMatchType.ANY,
        )
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_lists(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_description_lists: bool = False,
        include_tab_lists: bool = False,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the list role"""

        roles = [Atspi.Role.LIST]
        if include_description_lists:
            roles.append(Atspi.Role.DESCRIPTION_LIST)
        if include_tab_lists:
            roles.append(Atspi.Role.PAGE_TAB_LIST)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_list_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_description_terms: bool = False,
        include_tabs: bool = False,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the list item role"""

        roles = [Atspi.Role.LIST_ITEM]
        if include_description_terms:
            roles.append(Atspi.Role.DESCRIPTION_TERM)
        if include_tabs:
            roles.append(Atspi.Role.PAGE_TAB)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_page_tabs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the page tab role"""

        roles = [Atspi.Role.PAGE_TAB]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_paragraphs(
        root: Atspi.Accessible,
        treat_headings_as_paragraphs: bool = False,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the paragraph role"""

        roles = [Atspi.Role.PARAGRAPH]
        if treat_headings_as_paragraphs:
            roles.append(Atspi.Role.HEADING)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_push_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the push button role"""

        roles = [Atspi.Role.BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_radio_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the radio button role"""

        roles = [Atspi.Role.RADIO_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_separators(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the separator role"""

        roles = [Atspi.Role.SEPARATOR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_status_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the statusbar role"""

        roles = [Atspi.Role.STATUS_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the table role"""

        if root is None:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(), "Root:", root, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        roles = [Atspi.Role.TABLE]
        attributes = ["layout-guess:true"]
        attribute_match_type = Atspi.CollectionMatchType.NONE
        rule = AXCollection.create_match_rule(
            roles=roles,
            attributes=attributes,
            attribute_match_type=attribute_match_type,
        )

        tables = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            AXUtilitiesCollection._apply_predicate(tables, pred)

        return tables

    @staticmethod
    def find_all_unvisited_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the link role and without the visited state"""

        roles = [Atspi.Role.LINK]
        states = [Atspi.StateType.VISITED]
        result = AXUtilitiesCollection.find_all_with_role_without_states(root, roles, states, pred)
        if must_be_focusable:
            result = list(filter(AXUtilitiesState.is_focusable, result))
        return result

    @staticmethod
    def find_all_visited_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the link role and focused and visited states"""

        roles = [Atspi.Role.LINK]
        states = [Atspi.StateType.VISITED]
        if must_be_focusable:
            states.append(Atspi.StateType.FOCUSABLE)
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_first_with_role(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
    ) -> Atspi.Accessible | None:
        """Returns the first descendant of root with any of the specified roles"""

        if not (root and role_list):
            return None

        rule = AXCollection.create_match_rule(
            roles=role_list,
            role_match_type=Atspi.CollectionMatchType.ANY,
        )
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def find_first_with_role_and_all_states(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
    ) -> Atspi.Accessible | None:
        """Returns the first descendant of root with any of the roles and all the states"""

        if not (root and role_list and state_list):
            return None

        rule = AXCollection.create_match_rule(
            roles=role_list,
            role_match_type=Atspi.CollectionMatchType.ANY,
            states=state_list,
            state_match_type=Atspi.CollectionMatchType.ALL,
        )
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def find_first_with_interfaces(
        root: Atspi.Accessible,
        interface_list: list[str],
    ) -> Atspi.Accessible | None:
        """Returns the first descendant of root implementing all the specified interfaces"""

        if not (root and interface_list):
            return None

        rule = AXCollection.create_match_rule(interfaces=interface_list)
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def find_default_button(root: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the default button inside root"""

        roles = [Atspi.Role.BUTTON]
        states = [Atspi.StateType.IS_DEFAULT]
        rule = AXCollection.create_match_rule(roles=roles, states=states)
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def find_focused_object(root: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the focused object inside root"""

        states = [Atspi.StateType.FOCUSED]
        rule = AXCollection.create_match_rule(states=states)
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def find_info_bar(root: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the info bar inside root"""

        roles = [Atspi.Role.INFO_BAR]
        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        rule = AXCollection.create_match_rule(roles=roles, states=states)
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def find_status_bar(root: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the status bar inside root"""

        roles = [Atspi.Role.STATUS_BAR]
        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        rule = AXCollection.create_match_rule(roles=roles, states=states)
        return AXCollection.get_first_match(root, rule)

    @staticmethod
    def has_combo_box_or_list_box(root: Atspi.Accessible) -> bool:
        """Returns True if there's a showing, visible combobox or listbox inside root"""

        roles = [Atspi.Role.COMBO_BOX, Atspi.Role.LIST_BOX]
        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        rule = AXCollection.create_match_rule(
            roles=roles,
            role_match_type=Atspi.CollectionMatchType.ANY,
            states=states,
        )
        return bool(AXCollection.get_first_match(root, rule))

    @staticmethod
    def has_editable_object(root: Atspi.Accessible) -> bool:
        """Returns True if there's a showing, visible, editable object inside root"""

        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE, Atspi.StateType.EDITABLE]
        rule = AXCollection.create_match_rule(states=states)
        return bool(AXCollection.get_first_match(root, rule))

    @staticmethod
    def has_scroll_pane(root: Atspi.Accessible) -> bool:
        """Returns True if there's a showing, visible scroll pane inside root"""

        roles = [Atspi.Role.SCROLL_PANE]
        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        rule = AXCollection.create_match_rule(
            roles=roles,
            role_match_type=Atspi.CollectionMatchType.ANY,
            states=states,
        )
        return bool(AXCollection.get_first_match(root, rule))

    @staticmethod
    def has_split_pane(root: Atspi.Accessible) -> bool:
        """Returns True if there's a showing, visible split pane inside root"""

        roles = [Atspi.Role.SPLIT_PANE]
        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        rule = AXCollection.create_match_rule(roles=roles, states=states)
        return bool(AXCollection.get_first_match(root, rule))

    @staticmethod
    def has_tree_or_tree_table(root: Atspi.Accessible) -> bool:
        """Returns True if there's a showing, visible tree or tree table inside root"""

        roles = [Atspi.Role.TREE, Atspi.Role.TREE_TABLE]
        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        rule = AXCollection.create_match_rule(
            roles=roles,
            role_match_type=Atspi.CollectionMatchType.ANY,
            states=states,
        )
        return bool(AXCollection.get_first_match(root, rule))
