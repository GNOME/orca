# Utilities for finding all objects that meet a certain criteria.
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
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

"""Utilities for finding all objects that meet a certain criteria."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import inspect
import time
from typing import Callable

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_collection import AXCollection
from .ax_object import AXObject
from .ax_utilities_debugging import AXUtilitiesDebugging
from .ax_utilities_relation import AXUtilitiesRelation
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState


class AXUtilitiesCollection:
    """Utilities for finding all objects that meet a certain criteria."""

    @staticmethod
    def _apply_predicate(
        matches: list[Atspi.Accessible],
        pred: Callable[[Atspi.Accessible], bool]
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
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        if not (root and state_list):
            return []

        state_list = list(state_list)
        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, state_match_type, "of:", state_list]
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
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        if not (root and role_list):
            return []

        role_list = list(role_list)
        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, role_match_type, "of:", role_list]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(roles=role_list, role_match_type=role_match_type)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_interfaces(
        root: Atspi.Accessible,
        interface_list: list[str],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which implement all the specified interfaces"""

        if not (root and interface_list):
            return []

        interface_list = list(interface_list)
        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "all of:", interface_list]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(interfaces=interface_list)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_role(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the specified roles"""

        return AXUtilitiesCollection._find_all_with_role(
            root, role_list, Atspi.CollectionMatchType.ANY, pred)

    @staticmethod
    def find_all_without_roles(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which have none of the specified roles"""

        return AXUtilitiesCollection._find_all_with_role(
            root, role_list, Atspi.CollectionMatchType.NONE, pred)

    @staticmethod
    def find_all_with_role_and_all_states(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the roles, and all the states"""

        if not (root and role_list and state_list):
            return []

        role_list = list(role_list)
        state_list = list(state_list)
        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "Roles:", role_list, "States:", state_list]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(
            roles=role_list, states=state_list, state_match_type=Atspi.CollectionMatchType.ALL)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_role_and_any_state(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the roles, and any of the states"""

        if not (root and role_list and state_list):
            return []

        role_list = list(role_list)
        state_list = list(state_list)
        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "Roles:", role_list, "States:", state_list]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(
            roles=role_list, states=state_list, state_match_type=Atspi.CollectionMatchType.ANY)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_role_without_states(
        root: Atspi.Accessible,
        role_list: list[Atspi.Role],
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with any of the roles, and none of the states"""

        if not (root and role_list and state_list):
            return []

        role_list = list(role_list)
        state_list = list(state_list)
        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "Roles:", role_list, "States:", state_list]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rule = AXCollection.create_match_rule(
            roles=role_list, states=state_list, state_match_type=Atspi.CollectionMatchType.NONE)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_with_states(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which have all of the specified states"""

        return AXUtilitiesCollection._find_all_with_states(
            root, state_list, Atspi.CollectionMatchType.ALL, pred)

    @staticmethod
    def find_all_with_any_state(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which have any of the specified states"""

        return AXUtilitiesCollection._find_all_with_states(
            root, state_list, Atspi.CollectionMatchType.ANY, pred)

    @staticmethod
    def find_all_without_states(
        root: Atspi.Accessible,
        state_list: list[Atspi.StateType],
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which have none of the specified states"""

        return AXUtilitiesCollection._find_all_with_states(
            root, state_list, Atspi.CollectionMatchType.NONE, pred)

    @staticmethod
    def find_all_accelerator_labels(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the accelerator label role"""

        roles = [Atspi.Role.ACCELERATOR_LABEL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_alerts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the alert role"""

        roles = [Atspi.Role.ALERT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_animations(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the animation role"""

        roles = [Atspi.Role.ANIMATION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_arrows(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the arrow role"""

        roles = [Atspi.Role.ARROW]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_articles(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the article role"""

        roles = [Atspi.Role.ARTICLE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_audios(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the audio role"""

        roles = [Atspi.Role.AUDIO]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_autocompletes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the autocomplete role"""

        roles = [Atspi.Role.AUTOCOMPLETE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_block_quotes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the block quote role"""

        roles = [Atspi.Role.BLOCK_QUOTE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the push- or toggle-button role"""

        roles = [Atspi.Role.BUTTON, Atspi.Role.TOGGLE_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_calendars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the calendar role"""

        roles = [Atspi.Role.CALENDAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_canvases(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the canvas role"""

        roles = [Atspi.Role.CANVAS]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_captions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the caption role"""

        roles = [Atspi.Role.CAPTION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_charts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the chart role"""

        roles = [Atspi.Role.CHART]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_check_boxes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the checkbox role"""

        roles = [Atspi.Role.CHECK_BOX]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_check_menu_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the check menuitem role"""

        roles = [Atspi.Role.CHECK_MENU_ITEM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_clickables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
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

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, roles_match_type, "of:", roles, ". pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        def is_match(obj):
            result = AXObject.has_action(obj, "click")
            tokens = ["AXUtilitiesCollection:", obj, AXUtilitiesDebugging.actions_as_string(obj),
                      "has click Action:", result]
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
            state_match_type=state_match_type)
        matches = AXCollection.get_all_matches(root, rule)
        matches = AXUtilitiesCollection._apply_predicate(matches, is_match)
        return matches

    @staticmethod
    def find_all_color_choosers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the color_chooser role"""

        roles = [Atspi.Role.COLOR_CHOOSER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_column_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the column header role"""

        roles = [Atspi.Role.COLUMN_HEADER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_combo_boxes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the combobox role"""

        roles = [Atspi.Role.COMBO_BOX]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_comments(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the comment role"""

        roles = [Atspi.Role.COMMENT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_content_deletions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the content deletion role"""

        roles = [Atspi.Role.CONTENT_DELETION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_content_insertions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the content insertion role"""

        roles = [Atspi.Role.CONTENT_INSERTION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_date_editors(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the date editor role"""

        roles = [Atspi.Role.DATE_EDITOR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_definitions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the definition role"""

        roles = [Atspi.Role.DEFINITION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_description_lists(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the description list role"""

        roles = [Atspi.Role.DESCRIPTION_LIST]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_description_terms(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the description term role"""

        roles = [Atspi.Role.DESCRIPTION_TERM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_description_values(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the description value role"""

        roles = [Atspi.Role.DESCRIPTION_VALUE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_desktop_frames(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the desktop frame role"""

        roles = [Atspi.Role.DESKTOP_FRAME]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_desktop_icons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the desktop icon role"""

        roles = [Atspi.Role.DESKTOP_ICON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_dials(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the dial role"""

        roles = [Atspi.Role.DIAL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_dialogs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the dialog role"""

        roles = [Atspi.Role.DIALOG]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_dialogs_and_alerts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has any dialog or alert role"""

        roles = AXUtilitiesRole.get_dialog_roles(True)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_directory_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the directory pane role"""

        roles = [Atspi.Role.DIRECTORY_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_documents(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has any document-related role"""

        roles = AXUtilitiesRole.get_document_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_document_emails(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the document email role"""

        roles = [Atspi.Role.DOCUMENT_EMAIL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_document_frames(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the document frame role"""

        roles = [Atspi.Role.DOCUMENT_FRAME]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_document_presentations(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the document presentation role"""

        roles = [Atspi.Role.DOCUMENT_PRESENTATION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_document_spreadsheets(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the document spreadsheet role"""

        roles = [Atspi.Role.DOCUMENT_SPREADSHEET]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_document_texts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the document text role"""

        roles = [Atspi.Role.DOCUMENT_TEXT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_document_webs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the document web role"""

        roles = [Atspi.Role.DOCUMENT_WEB]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_drawing_areas(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the drawing area role"""

        roles = [Atspi.Role.DRAWING_AREA]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_editable_objects(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are editable"""

        states = [Atspi.StateType.EDITABLE]
        if must_be_focusable:
            states.append(Atspi.StateType.FOCUSABLE)
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_editbars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the editbar role"""

        roles = [Atspi.Role.EDITBAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_embeddeds(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the embedded role"""

        roles = [Atspi.Role.EMBEDDED]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_entries(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the entry role"""

        roles = [Atspi.Role.ENTRY]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_extendeds(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the extended role"""

        roles = [Atspi.Role.EXTENDED]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_file_choosers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the file chooser role"""

        roles = [Atspi.Role.FILE_CHOOSER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_fillers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the filler role"""

        roles = [Atspi.Role.FILLER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_focusable_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are focusable"""

        states = [Atspi.StateType.FOCUSABLE]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_focusable_objects_with_click_ancestor(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all focusable descendants of root which support the click-ancestor action"""

        if root is None:
            return []

        interfaces = ["Action"]
        states = [Atspi.StateType.FOCUSABLE]
        state_match_type = Atspi.CollectionMatchType.ANY
        roles = AXUtilitiesRole.get_roles_to_exclude_from_clickables_list()
        roles_match_type = Atspi.CollectionMatchType.NONE

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, roles_match_type, "of:", roles, ". pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        def is_match(obj):
            result = AXObject.has_action(obj, "click-ancestor")
            tokens = ["AXUtilitiesCollection:", obj, AXUtilitiesDebugging.actions_as_string(obj),
                      "has click-ancestor Action:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if not result:
                return False
            return pred is None or pred(obj)

        rule = AXCollection.create_match_rule(
            interfaces=interfaces,
            roles=roles,
            role_match_type=roles_match_type,
            states=states,
            state_match_type=state_match_type)
        matches = AXCollection.get_all_matches(root, rule)
        matches = AXUtilitiesCollection._apply_predicate(matches, is_match)
        return matches

    @staticmethod
    def find_all_focused_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are focused"""

        states = [Atspi.StateType.FOCUSED]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_focus_traversables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the focus traversable role"""

        roles = [Atspi.Role.FOCUS_TRAVERSABLE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_font_choosers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the font chooser role"""

        roles = [Atspi.Role.FONT_CHOOSER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_footers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the footer role"""

        roles = [Atspi.Role.FOOTER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_footnotes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the footnote role"""

        roles = [Atspi.Role.FOOTNOTE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_forms(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the form role"""

        roles = [Atspi.Role.FORM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_form_fields(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with a form-field-related role"""

        roles = AXUtilitiesRole.get_form_field_roles()
        if not must_be_focusable:
            return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

        states = [Atspi.StateType.FOCUSABLE]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_frames(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the frame role"""

        roles = [Atspi.Role.FRAME]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_glass_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the glass pane role"""

        roles = [Atspi.Role.GLASS_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_grids(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that are grids"""

        if root is None:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        roles = [Atspi.Role.TABLE]
        attributes = ["xml-roles:grid"]
        rule = AXCollection.create_match_rule(roles=roles, attributes=attributes)
        grids = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            AXUtilitiesCollection._apply_predicate(grids, pred)

        return grids

    @staticmethod
    def find_all_grid_cells(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that are grid cells"""

        if root is None:
            return []

        grids = AXUtilitiesCollection.find_all_grids(root, pred)
        if not grids:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        cells = []
        for grid in grids:
            cells.extend(AXUtilitiesCollection.find_all_table_cells(grid))

        if pred is not None:
            AXUtilitiesCollection._apply_predicate(cells, pred)

        return cells

    @staticmethod
    def find_all_groupings(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the grouping role"""

        roles = [Atspi.Role.GROUPING]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the header role"""

        roles = [Atspi.Role.HEADER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_headings(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the heading role"""

        roles = [Atspi.Role.HEADING]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_headings_at_level(
        root: Atspi.Accessible,
        level: int,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the heading role"""

        if root is None:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "Level:", level, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        roles = [Atspi.Role.HEADING]
        attributes = [f"level:{level}"]
        rule = AXCollection.create_match_rule(roles=roles, attributes=attributes)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)
        return matches

    @staticmethod
    def find_all_html_containers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the html container role"""

        roles = [Atspi.Role.HTML_CONTAINER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_horizontal_scrollbars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that is a horizontal scrollbar"""

        roles = [Atspi.Role.SCROLL_BAR]
        states = [Atspi.StateType.HORIZONTAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_horizontal_separators(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that is a horizontal separator"""

        roles = [Atspi.Role.SEPARATOR]
        states = [Atspi.StateType.HORIZONTAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_horizontal_sliders(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that is a horizontal slider"""

        roles = [Atspi.Role.SLIDER]
        states = [Atspi.StateType.HORIZONTAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_icons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the icon role"""

        roles = [Atspi.Role.ICON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_icons_and_canvases(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the icon or canvas role"""

        roles = [Atspi.Role.ICON, Atspi.Role.CANVAS]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_images(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the image role"""

        roles = [Atspi.Role.IMAGE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_images_and_canvases(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the image or canvas role"""

        roles = [Atspi.Role.IMAGE, Atspi.Role.CANVAS]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_images_and_image_maps(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the image or image map role"""

        roles = [Atspi.Role.IMAGE, Atspi.Role.IMAGE_MAP]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_image_maps(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the image map role"""

        roles = [Atspi.Role.IMAGE_MAP]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_info_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the info bar role"""

        roles = [Atspi.Role.INFO_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_input_method_windows(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the input method window role"""

        roles = [Atspi.Role.INPUT_METHOD_WINDOW]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_internal_frames(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the internal frame role"""

        roles = [Atspi.Role.INTERNAL_FRAME]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_labels(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the label role"""

        roles = [Atspi.Role.LABEL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_labels_and_captions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the label or caption role"""

        roles = [Atspi.Role.LABEL, Atspi.Role.CAPTION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_landmarks(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the landmark role"""

        roles = [Atspi.Role.LANDMARK]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_large_containers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that we consider a large container"""

        roles = AXUtilitiesRole.get_large_container_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_layered_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the layered pane role"""

        roles = [Atspi.Role.LAYERED_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_level_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the level bar role"""

        roles = [Atspi.Role.LEVEL_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None
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
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that are live regions"""

        if root is None:
            return []

        tokens = ["AXUtilitiesCollection:", inspect.currentframe(),
                  "Root:", root, "pred:", pred]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        attributes = []
        levels = ["off", "polite", "assertive"]
        for level in levels:
            attributes.append('container-live:' + level)

        rule = AXCollection.create_match_rule(attributes=attributes)
        matches = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            matches = AXUtilitiesCollection._apply_predicate(matches, pred)

        return matches

    @staticmethod
    def find_all_lists(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_description_lists: bool = False,
        include_tab_lists: bool = False
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the list role"""

        roles = [Atspi.Role.LIST]
        if include_description_lists:
            roles.append(Atspi.Role.DESCRIPTION_LIST)
        if include_tab_lists:
            roles.append(Atspi.Role.PAGE_TAB_LIST)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_list_boxes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the list box role"""

        roles = [Atspi.Role.LIST_BOX]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_list_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_description_terms: bool = False,
        include_tabs: bool = False
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the list item role"""

        roles = [Atspi.Role.LIST_ITEM]
        if include_description_terms:
            roles.append(Atspi.Role.DESCRIPTION_TERM)
        if include_tabs:
            roles.append(Atspi.Role.PAGE_TAB)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_logs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the log role"""

        roles = [Atspi.Role.LOG]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_marks(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the mark role"""

        roles = [Atspi.Role.MARK]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_marquees(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the marquee role"""

        roles = [Atspi.Role.MARQUEE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_maths(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the math role"""

        roles = [Atspi.Role.MATH]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_math_fractions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the math fraction role"""

        roles = [Atspi.Role.MATH_FRACTION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_math_roots(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the math root role"""

        roles = [Atspi.Role.MATH_ROOT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_menus(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the menu role"""

        roles = [Atspi.Role.MENU]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_menu_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the menubar role"""

        roles = [Atspi.Role.MENU_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_menu_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the menu item role"""

        roles = [Atspi.Role.MENU_ITEM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_menu_items_of_any_kind(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has any menu item role"""

        roles = AXUtilitiesRole.get_menu_item_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_menu_related_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has any menu-related role"""

        roles = AXUtilitiesRole.get_menu_related_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_modal_dialogs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the alert or dialog role and modal state"""

        roles = AXUtilitiesRole.get_dialog_roles(True)
        states = [Atspi.StateType.MODAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_multi_line_entries(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the entry role and multiline state"""

        roles = [Atspi.Role.ENTRY]
        states = [Atspi.StateType.MULTI_LINE]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_notifications(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the notification role"""

        roles = [Atspi.Role.NOTIFICATION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_option_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the option pane role"""

        roles = [Atspi.Role.OPTION_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_pages(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the page role"""

        roles = [Atspi.Role.PAGE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_page_tabs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the page tab role"""

        roles = [Atspi.Role.PAGE_TAB]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_page_tab_lists(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the page tab list role"""

        roles = [Atspi.Role.PAGE_TAB_LIST]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_page_tab_list_related_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the page tab or page tab list role"""

        roles = [Atspi.Role.PAGE_TAB_LIST, Atspi.Role.PAGE_TAB]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_panels(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the panel role"""

        roles = [Atspi.Role.PANEL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_paragraphs(
        root: Atspi.Accessible,
        treat_headings_as_paragraphs: bool = False,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the paragraph role"""

        roles = [Atspi.Role.PARAGRAPH]
        if treat_headings_as_paragraphs:
            roles.append(Atspi.Role.HEADING)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_password_texts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the password text role"""

        roles = [Atspi.Role.PASSWORD_TEXT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_popup_menus(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the popup menu role"""

        roles = [Atspi.Role.POPUP_MENU]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_progress_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the progress bar role"""

        roles = [Atspi.Role.PROGRESS_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_push_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the push button role"""

        roles = [Atspi.Role.BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_push_button_menus(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the push button menu role"""

        roles = [Atspi.Role.PUSH_BUTTON_MENU]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_radio_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the radio button role"""

        roles = [Atspi.Role.RADIO_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_radio_menu_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the radio menu item role"""

        roles = [Atspi.Role.RADIO_MENU_ITEM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_ratings(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the rating role"""

        roles = [Atspi.Role.RATING]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_root_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the root pane role"""

        roles = [Atspi.Role.ROOT_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_row_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the row header role"""

        roles = [Atspi.Role.ROW_HEADER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_rulers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the ruler role"""

        roles = [Atspi.Role.RULER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_scroll_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the scrollbar role"""

        roles = [Atspi.Role.SCROLL_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_scroll_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the scroll pane role"""

        roles = [Atspi.Role.SCROLL_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_sections(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the section role"""

        roles = [Atspi.Role.SECTION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_selectable_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are selectable"""

        states = [Atspi.StateType.SELECTABLE]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_selected_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are selected"""

        states = [Atspi.StateType.SELECTED]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_separators(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the separator role"""

        roles = [Atspi.Role.SEPARATOR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_set_containers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with a set container role"""

        roles = AXUtilitiesRole.get_set_container_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_showing_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are showing"""

        states = [Atspi.StateType.SHOWING]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_showing_and_visible_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are showing and visible"""

        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_showing_or_visible_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are showing or visible"""

        states = [Atspi.StateType.SHOWING, Atspi.StateType.VISIBLE]
        return AXUtilitiesCollection.find_all_with_any_state(root, states, pred)

    @staticmethod
    def find_all_single_line_entries(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the entry role and multiline state"""

        roles = [Atspi.Role.ENTRY]
        states = [Atspi.StateType.SINGLE_LINE]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_sliders(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the slider role"""

        roles = [Atspi.Role.SLIDER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_spin_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the spin button role"""

        roles = [Atspi.Role.SPIN_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_split_panes(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the split pane role"""

        roles = [Atspi.Role.SPLIT_PANE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_statics(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the static role"""

        roles = [Atspi.Role.STATIC]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_status_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the statusbar role"""

        roles = [Atspi.Role.STATUS_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_subscripts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the subscript role"""

        roles = [Atspi.Role.SUBSCRIPT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_subscripts_and_superscripts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the subscript or superscript role"""

        roles = [Atspi.Role.SUBSCRIPT, Atspi.Role.SUPERSCRIPT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_suggestions(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the suggestion role"""

        roles = [Atspi.Role.SUGGESTION]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_superscripts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the superscript role"""

        roles = [Atspi.Role.SUPERSCRIPT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_supports_action(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the action interface"""

        interfaces = ["Action"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_document(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the document interface"""

        interfaces = ["Document"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_editable_text(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the editable text interface"""

        interfaces = ["EditableText"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_hypertext(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the hypertext interface"""

        interfaces = ["Hypertext"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_hyperlink(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the hyperlink interface"""

        interfaces = ["Hyperlink"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_selection(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the selection interface"""

        interfaces = ["Selection"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_table(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the table interface"""

        interfaces = ["Table"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_table_cell(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the table cell interface"""

        interfaces = ["TableCell"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_text(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the text interface"""

        interfaces = ["Text"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_supports_value(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which support the value interface"""

        interfaces = ["Value"]
        return AXUtilitiesCollection.find_all_with_interfaces(root, interfaces, pred)

    @staticmethod
    def find_all_tables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
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
            attribute_match_type=attribute_match_type)

        tables = AXCollection.get_all_matches(root, rule)
        if pred is not None:
            AXUtilitiesCollection._apply_predicate(tables, pred)

        return tables

    @staticmethod
    def find_all_table_cells(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the table cell role"""

        roles = [Atspi.Role.TABLE_CELL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_table_cells_and_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the table cell or a header-related role"""

        roles = AXUtilitiesRole.get_table_cell_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_table_column_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the table column header role"""

        roles = [Atspi.Role.TABLE_COLUMN_HEADER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_table_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has a table header related role"""

        roles = AXUtilitiesRole.get_table_header_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_table_related_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None,
        include_caption: bool = False
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has a table related role"""

        roles = AXUtilitiesRole.get_table_related_roles(include_caption)
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_table_rows(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the table row role"""

        roles = [Atspi.Role.TABLE_ROW]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_table_row_headers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the table row header role"""

        roles = [Atspi.Role.TABLE_ROW_HEADER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tearoff_menu_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the tearoff menu item role"""

        roles = [Atspi.Role.TEAROFF_MENU_ITEM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_terminals(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the terminal role"""

        roles = [Atspi.Role.TERMINAL]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_texts(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the text role"""

        roles = [Atspi.Role.TEXT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_text_inputs(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has any role associated with textual input"""

        roles = [Atspi.Role.ENTRY, Atspi.Role.PASSWORD_TEXT, Atspi.Role.SPIN_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_timers(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the timer role"""

        roles = [Atspi.Role.TIMER]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_title_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the titlebar role"""

        roles = [Atspi.Role.TITLE_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_toggle_buttons(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the toggle button role"""

        roles = [Atspi.Role.TOGGLE_BUTTON]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tool_bars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the toolbar role"""

        roles = [Atspi.Role.TOOL_BAR]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tool_tips(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the tooltip role"""

        roles = [Atspi.Role.TOOL_TIP]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_trees(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the tree role"""

        roles = [Atspi.Role.TREE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_trees_and_tree_tables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the tree or tree table role"""

        roles = [Atspi.Role.TREE, Atspi.Role.TREE_TABLE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tree_related_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that has a tree related role"""

        roles = AXUtilitiesRole.get_tree_related_roles()
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tree_items(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the tree item role"""

        roles = [Atspi.Role.TREE_ITEM]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_tree_tables(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the tree table role"""

        roles = [Atspi.Role.TREE_TABLE]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_unrelated_labels(
        root: Atspi.Accessible,
        must_be_showing: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all the descendants of root that have a label role, but no relations"""

        def _pred(obj):
            if not AXUtilitiesRelation.object_is_unrelated(obj):
                return False
            if pred is not None:
                return pred(obj)
            return True

        roles = [Atspi.Role.LABEL, Atspi.Role.STATIC]
        if not must_be_showing:
            matches = AXUtilitiesCollection.find_all_with_role(root, roles, _pred)
        else:
            states = [Atspi.StateType.SHOWING]
            matches = AXUtilitiesCollection.find_all_with_role_and_all_states(
                root, roles, states, _pred)

        return matches

    @staticmethod
    def find_all_unvisited_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the link role and without the visited state"""

        roles = [Atspi.Role.LINK]
        states = [Atspi.StateType.VISITED]
        result = AXUtilitiesCollection.find_all_with_role_without_states(root, roles, states, pred)
        if must_be_focusable:
            result = list(filter(AXUtilitiesState.is_focusable, result))
        return result

    @staticmethod
    def find_all_vertical_scrollbars(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that is a vertical scrollbar"""

        roles = [Atspi.Role.SCROLL_BAR]
        states = [Atspi.StateType.VERTICAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_vertical_separators(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that is a vertical separator"""

        roles = [Atspi.Role.SEPARATOR]
        states = [Atspi.StateType.VERTICAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_vertical_sliders(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root that is a vertical slider"""

        roles = [Atspi.Role.SLIDER]
        states = [Atspi.StateType.VERTICAL]
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

    @staticmethod
    def find_all_visible_objects(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root which are visible"""

        states = [Atspi.StateType.VISIBLE]
        return AXUtilitiesCollection.find_all_with_states(root, states, pred)

    @staticmethod
    def find_all_videos(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the video role"""

        roles = [Atspi.Role.VIDEO]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_viewports(
        root: Atspi.Accessible,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the viewport role"""

        roles = [Atspi.Role.VIEWPORT]
        return AXUtilitiesCollection.find_all_with_role(root, roles, pred)

    @staticmethod
    def find_all_visited_links(
        root: Atspi.Accessible,
        must_be_focusable: bool = True,
        pred: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        """Returns all descendants of root with the link role and focused and visited states"""

        roles = [Atspi.Role.LINK]
        states = [Atspi.StateType.VISITED]
        if must_be_focusable:
            states.append(Atspi.StateType.FOCUSABLE)
        return AXUtilitiesCollection.find_all_with_role_and_all_states(root, roles, states, pred)

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
        rule = AXCollection.create_match_rule(roles=roles, states=states)
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
        rule = AXCollection.create_match_rule(roles=roles, states=states)
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
        rule = AXCollection.create_match_rule(roles=roles, states=states)
        return bool(AXCollection.get_first_match(root, rule))
