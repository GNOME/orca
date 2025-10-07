# Orca
#
# Copyright 2010 Joanmarie Diggs.
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
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-return-statements

"""Utilities for providing app/toolkit-specific information about objects and events."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

from typing import Callable

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from . import focus_manager
from . import input_event_manager
from . import messages
from . import object_properties
from . import script_manager
from . import settings
from . import settings_manager
from . import speech_and_verbosity_manager
from .ax_component import AXComponent
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Utilities:
    """Utilities for providing app/toolkit-specific information about objects and events."""

    ZERO_WIDTH_NO_BREAK_SPACE = '\ufeff'

    def __init__(self, script):
        self._script = script

        # TODO - JD: We actually need to keep track of a root object and its descendant
        # caret context, just like we do in the web script. And it all should move into
        # the focus manager. In the meantime, just get things working for the active app.
        self._caret_context = (None, -1)

    def node_level(self, obj: Atspi.Accessible) -> int:
        """Returns the node level of the specified tree item."""

        if not AXObject.find_ancestor(obj, AXUtilities.is_tree_or_tree_table):
            return -1

        attrs = AXObject.get_attributes_dict(obj)
        if "level" in attrs:
            # ARIA levels are 1-based.
            return int(attrs.get("level", 0)) - 1

        nodes = []
        node = obj
        while node and (targets := AXUtilities.get_is_node_child_of(node)):
            node = targets[0]
            nodes.append(node)

        return len(nodes) - 1

    def child_nodes(self, obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Gets all of the objects that have RELATION_NODE_CHILD_OF pointing to this cell."""

        if not AXUtilities.is_expanded(obj):
            return []

        table = AXTable.get_table(obj)
        if table is None:
            return []

        nodes = AXUtilities.get_is_node_parent_of(obj)
        tokens = ["SCRIPT UTILITIES:", len(nodes), "child nodes for", obj, "via node-parent-of"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if nodes:
            return nodes

        # Candidates will be in the rows beneath the current row. Only check in the current column
        # and stop checking as soon as the node level of a candidate is equal or less than our
        # current level.
        row, col = AXTable.get_cell_coordinates(obj, prefer_attribute=False)
        level = self.node_level(obj)

        for i in range(row + 1, AXTable.get_row_count(table, prefer_attribute=False)):
            cell = AXTable.get_cell_at(table, i, col)
            targets = AXUtilities.get_is_node_child_of(cell)
            if not targets:
                continue

            node_of = targets[0]
            if obj == node_of:
                nodes.append(cell)
            elif self.node_level(node_of) <= level:
                break

        tokens = ["SCRIPT UTILITIES:", len(nodes), "child nodes for", obj, "via node-child-of"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return nodes

    def details_content_for_object(self, obj: Atspi.Accessible) -> list[str]:
        """Returns a list of strings containing the details for obj."""

        details = self._details_for_object(obj)
        return list(map(AXText.get_all_text, details))

    def _details_for_object(self, obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Return a list of objects containing details for obj."""

        details = AXUtilities.get_details(obj)
        if not details and AXUtilities.is_toggle_button(obj) and AXUtilities.is_expanded(obj):
            details = list(AXObject.iter_children(obj))

        text_objects = []
        for detail in details:
            text_objects.extend(self._find_all_descendants(
                detail, lambda x: not AXText.is_whitespace_or_empty(x)))

        return text_objects

    def frame_and_dialog(
        self,
        obj: Atspi.Accessible | None = None
    ) -> list[Atspi.Accessible | None]:
        """Returns the frame and (possibly) the dialog containing obj."""

        results = [None, None]

        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not obj:
            msg = "SCRIPT UTILITIES: frame_and_dialog() called without valid object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return results

        top_level = self.top_level_object(obj)
        if top_level is None:
            tokens = ["SCRIPT UTILITIES: could not find top-level object for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return results

        dialog_roles = [Atspi.Role.DIALOG, Atspi.Role.FILE_CHOOSER, Atspi.Role.ALERT]
        role = AXObject.get_role(top_level)
        if role in dialog_roles:
            results[1] = top_level
        else:
            if role in [Atspi.Role.FRAME, Atspi.Role.WINDOW]:
                results[0] = top_level

            def is_dialog(x):
                return AXObject.get_role(x) in dialog_roles

            results[1] = AXObject.find_ancestor_inclusive(obj, is_dialog)

        tokens = ["SCRIPT UTILITIES:", obj, "is in frame", results[0], "and dialog", results[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return results

    def grab_focus_when_setting_caret(self, obj: Atspi.Accessible) -> bool:
        """Returns true if we should grab focus when setting the caret."""

        return AXUtilities.is_focusable(obj)

    def grab_focus_before_routing(self, obj: Atspi.Accessible) -> bool:
        """Returns true if we should grab focus before routing the cursor."""

        return AXUtilities.is_combo_box(obj) \
            and obj != focus_manager.get_manager().get_locus_of_focus()

    def in_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is in a find-in-page container."""

        if obj is None:
            obj = focus_manager.get_manager().get_locus_of_focus()

        if not AXUtilities.is_entry(obj):
            return False

        return AXObject.find_ancestor(obj, AXUtilities.is_tool_bar) is not None

    def get_find_results_count(self, _root: Atspi.Accessible | None = None) -> str:
        """Returns a string description of the number of find-in-page results in root."""

        return ""

    def is_anchor(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is an anchor."""

        # TODO - JD: Move this into the AXUtilities.
        return AXUtilities.is_link(obj) and not AXUtilities.is_focusable(obj) \
           and not AXObject.has_action(obj, "jump") and not AXUtilities.has_role_from_aria(obj)

    def is_progress_bar_update(self, obj: Atspi.Accessible) -> tuple[bool, str]:
        """Returns a (is-update, reason) tuple if updates to obj should be presented."""

        # TODO - JD: Move this into the AXUtilities.
        if not settings_manager.get_manager().get_setting("speakProgressBarUpdates") \
           and not settings_manager.get_manager().get_setting("brailleProgressBarUpdates") \
           and not settings_manager.get_manager().get_setting("beepProgressBarUpdates"):
            return False, "Updates not enabled"

        if not AXUtilities.is_progress_bar(obj):
            return False, "Is not progress bar"

        if not AXValue.get_value_as_percent(obj):
            return False, "Could not obtain value"

        if AXComponent.has_no_size(obj):
            return False, "Has no size"

        if settings_manager.get_manager().get_setting('ignoreStatusBarProgressBars'):
            if AXObject.find_ancestor(obj, AXUtilities.is_status_bar):
                return False, "Is status bar descendant"

        verbosity = settings_manager.get_manager().get_setting('progressBarVerbosity')
        if verbosity == settings.PROGRESS_BAR_ALL:
            return True, "Verbosity is all"

        if verbosity == settings.PROGRESS_BAR_WINDOW:
            if self.top_level_object(obj) == focus_manager.get_manager().get_active_window():
                return True, "Verbosity is window"
            return False, "Top-level object is not active window"

        if verbosity == settings.PROGRESS_BAR_APPLICATION:
            app = AXUtilities.get_application(obj)
            active_app = script_manager.get_manager().get_active_script_app()
            if app == active_app:
                return True, "Verbosity is app"
            return False, "App is not active app"

        return True, "Not handled by any other case"

    def description_list_terms(self, obj: Atspi.Accessible) -> list[Atspi.Accessible]:
        """Returns a list of all the accessible description list terms in obj."""

        # TODO - JD: The only caller is the web speech generator. Consider moving this there.
        if not AXUtilities.is_description_list(obj):
            return []

        _include = AXUtilities.is_description_term
        _exclude = AXUtilities.is_description_list
        return self._find_all_descendants(obj, _include, _exclude)

    def is_document_list(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a list inside a document."""

        # TODO - JD: Move this into AXUtilities.
        if not (AXUtilities.is_list(obj) or AXUtilities.is_description_list(obj)):
            return False
        return AXObject.find_ancestor(obj, AXUtilities.is_document) is not None

    def is_document_panel(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a panel inside a document."""

        # TODO - JD: Move this into AXUtilities.
        if not AXUtilities.is_panel(obj):
            return False
        return AXObject.find_ancestor(obj, AXUtilities.is_document) is not None

    def is_document(self, obj: Atspi.Accessible, _exclude_document_frame=False) -> bool:
        """Returns True if obj is a document."""

        # TODO - JD: See if the web script logic can be included here and then it all moved
        # into AXUtilities.
        return AXUtilities.is_document(obj)

    def in_document_content(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj (or the locus of focus) is in document content."""

        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        return self.get_document_for_object(obj) is not None

    def active_document(self) -> Atspi.Accessible | None:
        """Returns the active document."""

        window = focus_manager.get_manager().get_active_window()
        documents = list(filter(self.is_document, AXUtilities.get_embeds(window)))
        documents = list(filter(AXUtilities.is_showing, documents))
        if len(documents) == 1:
            tokens = ["SCRIPT UTILITIES: Active document (via embeds):", documents[0]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return documents[0]

        document = self.get_top_level_document_for_object(
            focus_manager.get_manager().get_locus_of_focus())
        tokens = ["SCRIPT UTILITIES: Active document (via locus of focus):", document]
        return document

    def is_top_level_document(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a top-level document."""

        return self.is_document(obj) and not AXObject.find_ancestor(obj, self.is_document)

    def get_top_level_document_for_object(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the top-level document containing obj."""

        return AXObject.find_ancestor_inclusive(obj, self.is_top_level_document)

    def get_document_for_object(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the nearest document ancestor of obj, or obj if it is a document."""

        # TODO - JD: Replace callers of this function with the logic below.
        return AXObject.find_ancestor_inclusive(obj, self.is_document)

    def convert_column_to_string(self, column: int) -> str:
        """Converts a column number to a string representation."""

        return str(column)

    def is_text_document_table(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a text document table (i.e. not a spreadsheet or GUI table)"""

        # TODO - JD: Move this into AXUtilities.

        if not AXUtilities.is_table(obj):
            return False

        doc = self.get_document_for_object(obj)
        return doc is not None and not AXUtilities.is_document_spreadsheet(doc)

    def is_gui_table(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a GUI table."""

        # TODO - JD: Move this into AXUtilities.

        return AXUtilities.is_table(obj) and self.get_document_for_object(obj) is None

    def is_spreadsheet_table(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a spreadsheet table."""

        # TODO - JD: Move this into AXUtilities.

        if not (AXUtilities.is_table(obj) and AXObject.supports_table(obj)):
            return False

        doc = self.get_document_for_object(obj)
        if doc is None:
            return False
        if AXUtilities.is_document_spreadsheet(doc):
            return True

        return AXTable.get_row_count(obj) > 65536

    def is_text_document_cell(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a cell in a text document table."""

        # TODO - JD: Move this into AXUtilities.

        if not AXUtilities.is_table_cell_or_header(obj):
            return False
        return AXObject.find_ancestor(obj, self.is_text_document_table) is not None

    def is_gui_cell(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a cell in a GUI table."""

        # TODO - JD: Move this into AXUtilities.

        if not AXUtilities.is_table_cell_or_header(obj):
            return False
        return AXObject.find_ancestor(obj, self.is_gui_table) is not None

    def is_spreadsheet_cell(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a cell in a spreadsheet table."""

        # TODO - JD: Move this into AXUtilities.

        if not AXUtilities.is_table_cell_or_header(obj):
            return False
        return AXObject.find_ancestor(obj, self.is_spreadsheet_table) is not None

    def cell_column_changed(
        self,
        cell: Atspi.Accessible,
        prior_cell: Atspi.Accessible | None = None
    ) -> bool:
        """Returns True if the column of cell has changed since prior_cell."""

        column = AXTable.get_cell_coordinates(cell)[1]
        if column == -1:
            return False

        if prior_cell is None:
            _last_row, last_column = focus_manager.get_manager().get_last_cell_coordinates()
        else:
            last_column = AXTable.get_cell_coordinates(prior_cell)[1]

        return column != last_column

    def cell_row_changed(
        self,
        cell: Atspi.Accessible,
        prior_cell: Atspi.Accessible | None = None
    ) -> bool:
        """Returns True if the row of cell has changed since prior_cell."""

        row = AXTable.get_cell_coordinates(cell)[0]
        if row == -1:
            return False

        if prior_cell is None:
            last_row, _last_column = focus_manager.get_manager().get_last_cell_coordinates()
        else:
            last_row = AXTable.get_cell_coordinates(prior_cell)[0]
        return row != last_row

    def should_read_full_row(
        self,
        obj: Atspi.Accessible,
        previous_object: Atspi.Accessible | None = None
    ) -> bool:
        """Returns True if we should present the full row in speech."""

        if focus_manager.get_manager().in_say_all():
            return False

        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return False

        if not self.cell_row_changed(obj, previous_object):
            return False

        table = AXTable.get_table(obj)
        if table is None:
            return False

        manager = speech_and_verbosity_manager.get_manager()
        if not self.get_document_for_object(table):
            return manager.get_speak_row_in_gui_table()
        if self.is_spreadsheet_table(table):
            return manager.get_speak_row_in_spreadsheet()
        return manager.get_speak_row_in_document_table()

    def get_notification_content(self, obj: Atspi.Accessible) -> str:
        """Returns a string containing the content of the notification obj."""

        if not AXUtilities.is_notification(obj):
            return ""

        tokens = []
        name = AXObject.get_name(obj)
        if name:
            tokens.append(name)
        text = self.expand_eocs(obj)
        if text and text not in tokens:
            tokens.append(text)
        else:
            labels = " ".join(map(lambda x: AXText.get_all_text(x) or AXObject.get_name(x),
                                  self.unrelated_labels(obj, False, 1)))
            if labels and labels not in tokens:
                tokens.append(labels)

        description = AXObject.get_description(obj)
        if description and description not in tokens:
            tokens.append(description)

        return " ".join(tokens)

    def is_link(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a link."""

        return AXUtilities.is_link(obj)

    def _get_object_from_path(self, path):
        # TODO - JD: This broad exception is swallowing a pyatspism meaning the one caller
        # (recovery code for web brokeness) is not recovering. Which suggests that code can
        # be removed.
        start = self._script.app
        rv = None
        for p in path:
            if p == -1:
                continue
            try:
                start = start[p]
            except (IndexError, TypeError, AttributeError):
                break
        else:
            rv = start

        return rv

    def active_descendant(self, obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Legacy table-cell code originally for managed descendants."""

        # TODO - JD: Determine what actually needs this support and why.

        if AXObject.is_dead(obj):
            return None

        if not AXUtilities.is_table_cell(obj):
            return obj

        if AXObject.get_name(obj):
            return obj

        def pred(x):
            return AXObject.get_name(x) or AXText.get_all_text(x)

        child = AXObject.find_descendant(obj, pred)
        if child is not None:
            return child

        return obj

    def _top_level_roles(self) -> list[Atspi.Role]:
        # TODO - JD: Move this into AXUtilities.
        roles = [Atspi.Role.DIALOG,
                 Atspi.Role.FILE_CHOOSER,
                 Atspi.Role.FRAME,
                 Atspi.Role.WINDOW,
                 Atspi.Role.ALERT]
        return roles

    def _find_window_witih_descendant(self, child: Atspi.Accessible) -> Atspi.Accessible | None:
        """A terrible, non-performant workaround for broken ancestry."""

        app = AXUtilities.get_application(child)
        if app is None:
            return None

        for i in range(AXObject.get_child_count(app)):
            window = AXObject.get_child(app, i)
            if AXObject.find_descendant(window, lambda x: x == child) is not None:
                tokens = ["SCRIPT UTILITIES:", window, "contains", child]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return window

            tokens = ["SCRIPT UTILITIES:", window, "does not contain", child]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return None

    def _is_top_level_object(self, obj: Atspi.Accessible) -> bool:
        return AXObject.get_role(obj) in self._top_level_roles() \
            and AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.APPLICATION

    def top_level_object(
        self,
        obj: Atspi.Accessible,
        use_fallback_search: bool = False
    ) -> Atspi.Accessible | None:
        """Returns the top-level object (frame, dialog ...) containing obj."""

        rv = AXObject.find_ancestor_inclusive(obj, self._is_top_level_object)
        tokens = ["SCRIPT UTILITIES:", rv, "is top-level object for:", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if rv is None and use_fallback_search:
            msg = "SCRIPT UTILITIES: Attempting to find top-level object via fallback search"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            rv = self._find_window_witih_descendant(obj)

        return rv

    def top_level_object_is_active_and_current(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns true if the top-level object for obj/locus-of-focus is active and current."""

        # TODO - JD: Candidate for the focus manager.
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        top_level = self.top_level_object(obj)
        if not top_level:
            return False

        AXObject.clear_cache(top_level, False, "Ensuring we have the correct state.")
        if not AXUtilities.is_active(top_level) or AXUtilities.is_defunct(top_level):
            return False

        return top_level == focus_manager.get_manager().get_active_window()

    @staticmethod
    def path_comparison(path1: list[int], path2: list[int]) -> int:
        """Returns -1, 0, or 1 to indicate if path1 is before, the same, or after path2."""

        # TODO - JD: Move into AXUtilities.

        if path1 == path2:
            return 0

        size = max(len(path1), len(path2))
        path1 = (path1 + [-1] * size)[:size]
        path2 = (path2 + [-1] * size)[:size]

        for x in range(min(len(path1), len(path2))):
            if path1[x] < path2[x]:
                return -1
            if path1[x] > path2[x]:
                return 1

        return 0

    def _find_all_descendants(
        self,
        root: Atspi.Accessible | None,
        include_if: Callable[[Atspi.Accessible], bool] | None = None,
        exclude_if: Callable[[Atspi.Accessible], bool] | None = None
    ) -> list[Atspi.Accessible]:
        # TODO - JD: Move this into AXUtilities.
        if root is None:
            return []

        # Don't bother if the root is a 'pre' or 'code' element. Those often have
        # nothing but a TON of static text leaf nodes, which we want to ignore.
        if AXUtilities.is_code(root):
            tokens = ["SCRIPUT UTILITIES: Returning 0 descendants for pre/code", root]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        return AXObject.find_all_descendants(root, include_if, exclude_if)

    def unrelated_labels(
        self,
        root: Atspi.Accessible | None = None,
        only_showing: bool = True,
        minimum_words: int = 3
    ) -> list[Atspi.Accessible]:
        """Returns a list of labels in root that lack a relationship."""

        if self._script.spellcheck and self._script.spellcheck.is_spell_check_window(root):
            return []

        label_roles = [Atspi.Role.LABEL, Atspi.Role.STATIC]
        skip_roles = [Atspi.Role.BUTTON,
                      Atspi.Role.COMBO_BOX,
                      Atspi.Role.DOCUMENT_EMAIL,
                      Atspi.Role.DOCUMENT_FRAME,
                      Atspi.Role.DOCUMENT_PRESENTATION,
                      Atspi.Role.DOCUMENT_SPREADSHEET,
                      Atspi.Role.DOCUMENT_TEXT,
                      Atspi.Role.DOCUMENT_WEB,
                      Atspi.Role.FRAME,
                      Atspi.Role.LIST_BOX,
                      Atspi.Role.LIST,
                      Atspi.Role.LIST_ITEM,
                      Atspi.Role.MENU,
                      Atspi.Role.MENU_BAR,
                      Atspi.Role.SCROLL_PANE,
                      Atspi.Role.SPLIT_PANE,
                      Atspi.Role.TABLE,
                      Atspi.Role.TOGGLE_BUTTON,
                      Atspi.Role.TREE,
                      Atspi.Role.TREE_TABLE,
                      Atspi.Role.WINDOW]

        if AXObject.get_role(root) in skip_roles:
            return []

        def _include(x):
            if not (x and AXObject.get_role(x) in label_roles):
                return False
            if not AXUtilities.object_is_unrelated(x):
                return False
            if only_showing and not AXUtilities.is_showing(x):
                return False
            return True

        def _exclude(x):
            if not x or AXObject.get_role(x) in skip_roles:
                return True
            if only_showing and not AXUtilities.is_showing(x):
                return True
            return False

        labels = self._find_all_descendants(root, _include, _exclude)

        root_name = AXObject.get_name(root)

        # Eliminate things suspected to be labels for widgets
        labels_filtered = []
        for label in labels:
            name = AXObject.get_name(label) or AXText.get_all_text(label)
            if name and name in [root_name, AXObject.get_name(AXObject.get_parent(label))]:
                continue
            if len(name.split()) < minimum_words:
                continue
            if root_name.find(name) >= 0:
                continue
            labels_filtered.append(label)

        return AXComponent.sort_objects_by_position(labels_filtered)

    def find_previous_object(
        self,
        obj: Atspi.Accessible,
        restrict_to: Atspi.Accessible | None = None
    ) -> Atspi.Accessible | None:
        """Finds the object before this one."""

        if restrict_to is None:
            restrict_to = self.get_top_level_document_for_object(obj)

        result = AXUtilities.get_previous_object(obj)
        tokens = ["SCRIPT UTILITIES: Previous object for", obj, "is", result, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if restrict_to is not None and not AXObject.is_ancestor(result, restrict_to, True):
            tokens = ["SCRIPT UTILITIES:", result, "is not a descendant of", restrict_to]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return result

    def find_next_object(
        self,
        obj: Atspi.Accessible,
        restrict_to: Atspi.Accessible | None = None
    ) -> Atspi.Accessible | None:
        """Finds the object after this one."""

        if restrict_to is None:
            restrict_to = self.get_top_level_document_for_object(obj)

        result = AXUtilities.get_next_object(obj)
        tokens = ["SCRIPT UTILITIES: Next object for", obj, "is", result, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if restrict_to is not None and not AXObject.is_ancestor(result, restrict_to, True):
            tokens = ["SCRIPT UTILITIES:", result, "is not a descendant of", restrict_to]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None
        return result

    def expand_eocs(
        self,
        obj: Atspi.Accessible,
        start_offset: int = 0,
        end_offset: int = -1
    ) -> str:
        """Expands the current object replacing embedded object characters with their text."""

        text = AXText.get_substring(obj, start_offset, end_offset)
        if "\ufffc" not in text:
            return text

        block_roles = [Atspi.Role.HEADING,
                      Atspi.Role.LIST,
                      Atspi.Role.LIST_ITEM,
                      Atspi.Role.PARAGRAPH,
                      Atspi.Role.SECTION,
                      Atspi.Role.TABLE,
                      Atspi.Role.TABLE_CELL,
                      Atspi.Role.TABLE_ROW]

        to_build = list(text)
        for i, char in enumerate(to_build):
            if char == "\ufffc":
                child = AXHypertext.find_child_at_offset(obj, i + start_offset)
                result = self.expand_eocs(child)
                if child and AXObject.get_role(child) in block_roles:
                    result += " "
                to_build[i] = result

        result = "".join(to_build)
        tokens = ["SCRIPT UTILITIES: Expanded EOCs for", obj,
                 f"range: {start_offset}:{end_offset}: '{result}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if "\ufffc" in result:
            msg = "SCRIPT UTILITIES: Unable to expand EOCs"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return result

    def is_error_for_contents(
        self,
        obj: Atspi.Accessible,
        contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
    ) -> bool:
        """Returns True of obj is an error message for the contents."""

        if not contents:
            return False

        if not AXUtilities.get_is_error_for(obj):
            return False

        for acc, _start, _end, _string in contents:
            targets = AXUtilities.get_error_message(acc)
            if targets is not None and obj in targets:
                return True

        return False

    def deleted_text(self, event: Atspi.Event) -> str:
        """Tries to determine the real deleted text for the given event. Because app bugs."""

        return event.any_data

    def inserted_text(self, event: Atspi.Event) -> str:
        """Tries to determine the real inserted text for the given event. Because app bugs."""

        if event.any_data:
            return event.any_data

        msg = "SCRIPT UTILITIES: Broken text insertion event"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if AXUtilities.is_password_text(event.source):
            string = AXText.get_all_text(event.source)
            if string:
                tokens = ["HACK: Returning last char in '", string, "'"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return string[-1]

        msg = "FAIL: Unable to correct broken text insertion event"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return ""

    def clear_caret_context(
        self,
        document: Atspi.Accessible | None = None # pylint: disable=unused-argument
    ) -> None:
        """Clears the caret context."""

        # TODO - JD: This logic ultimately belongs in the focus manager.
        self._caret_context = (None, -1)

    def set_caret_context(
        self,
        obj: Atspi.Accessible | None = None, # pylint: disable=unused-argument
        offset: int = -1, # pylint: disable=unused-argument
        document: Atspi.Accessible | None = None # pylint: disable=unused-argument
    ) -> None:
        """Sets the caret context in document to (obj, offset)."""

        # TODO - JD: This logic ultimately belongs in the focus manager.
        self._caret_context = (obj, offset)

    def get_caret_context(
        self,
        document: Atspi.Accessible | None = None,  # pylint: disable=unused-argument
        get_replicant: bool = False,  # pylint: disable=unused-argument
        search_if_needed: bool = True  # pylint: disable=unused-argument
    ) -> tuple[Atspi.Accessible, int]:
        """Returns an (obj, offset) tuple representing the current location."""

        obj, offset = self._caret_context
        if obj is not None:
            tokens = ["SCRIPT UTILITIES: Returning cached caret context", obj, offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, offset

        obj = focus_manager.get_manager().get_locus_of_focus()
        offset = AXText.get_caret_offset(obj)
        tokens = ["SCRIPT UTILITIES: Returning focus + caret offset", obj, offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return obj, offset

    def set_caret_position(
        self,
        obj: Atspi.Accessible,
        offset: int,
        document: Atspi.Accessible | None = None  # pylint: disable=unused-argument
    ) -> None:
        """Sets the locus of focus to obj and sets the caret position to offset."""

        manager = focus_manager.get_manager()
        manager.set_locus_of_focus(None, obj, False)
        if self.grab_focus_when_setting_caret(obj):
            AXObject.grab_focus(obj)

        # We cannot count on implementations clearing the selection for us when we set the caret
        # offset. Also, we should clear the selected text first.
        # https://bugs.documentfoundation.org/show_bug.cgi?id=167930
        AXText.clear_all_selected_text(obj)
        self.set_caret_offset(obj, offset)

        # TODO - JD: The web script's set_caret_position() also sets the caret context.
        # Ensuring global structural navigation, caret navigation, browse mode, etc.
        # work means we should do the same here. Ultimately, however, we need to clearly
        # define and unite the whole offset + position + context + locus of focus +
        # last cursor position.
        manager.set_last_cursor_position(obj, offset)
        self.set_caret_context(obj, offset)

        scroll_to = max(0, min(offset, AXText.get_character_count(obj) - 1))
        self._script.get_event_synthesizer().scroll_into_view(obj, scroll_to)

    def set_caret_offset(
        self,
        obj: Atspi.Accessible,
        offset: int
    ) -> None:
        """Sets the caret offset via AtspiText."""

        # TODO - JD. Remove this function if the web override can be adjusted
        AXText.set_caret_offset(obj, offset)

    def split_substring_by_language(
        self,
        obj: Atspi.Accessible,
        start: int,
        end: int
    ) -> list[tuple[int, int, str, str, str]]:
        """Returns a list of (start, end, string, language, dialect) tuples."""

        rv: list[tuple[int, int, str, str, str]] = []
        all_substrings = self.get_language_and_dialect_from_text_attributes(obj, start, end)
        for start_offset, end_offset, language, dialect in all_substrings:
            if start >= end_offset:
                continue
            if end <= start_offset:
                break
            start_offset = max(start, start_offset)
            end_offset = min(end, end_offset)
            string = AXText.get_substring(obj, start_offset, end_offset)
            rv.append((start_offset, end_offset, string, language, dialect))

        return rv

    def get_language_and_dialect_for_substring(
        self,
        obj: Atspi.Accessible,
        start: int, end: int
    ) -> tuple[str, str]:
        """Returns a (language, dialect) tuple. If multiple languages apply to
        the substring, language and dialect will be empty strings. Callers must
        do any preprocessing to avoid that condition."""

        all_substrings = self.get_language_and_dialect_from_text_attributes(obj, start, end)
        for start_offset, end_offset, language, dialect in all_substrings:
            if start_offset <= start and end_offset >= end:
                return language, dialect

        return "", ""

    def get_language_and_dialect_from_text_attributes(
        self,
        obj: Atspi.Accessible,
        start_offset: int = 0,
        end_offset: int = -1
    ) -> list[tuple[int, int, str, str]]:
        """Returns a list of (start, end, language, dialect) tuples for obj."""

        rv: list[tuple[int, int, str, str]] = []
        attribute_set = AXText.get_all_text_attributes(obj, start_offset, end_offset)
        last_language = last_dialect = ""
        for (start, end, attrs) in attribute_set:
            language = attrs.get("language", "")
            dialect = ""
            if "-" in language:
                language, dialect = language.split("-", 1)
            if rv and last_language == language and last_dialect == dialect:
                rv[-1] = rv[-1][0], end, language, dialect
            else:
                rv.append((start, end, language, dialect))
            last_language, last_dialect = language, dialect

        return rv

    def get_word_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int = 0,
        use_cache: bool = True # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the word at offset."""

        text, start, end = AXText.get_word_at_offset(obj, offset)
        return [(obj, start, end, text)]

    def get_previous_line_contents(
        self,
        obj: Atspi.Accessible | None = None, # pylint: disable=unused-argument
        offset: int = -1, # pylint: disable=unused-argument
        layout_mode: bool | None = None, # pylint: disable=unused-argument
        use_cache: bool = True # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the previous line."""

        if obj is None:
            obj, offset = self.get_caret_context()

        if offset == -1:
            offset = AXText.get_caret_offset(obj)

        text, start, end = AXText.get_previous_line(obj, offset)
        if text:
            return [(obj, start, end, text)]

        _this_line, this_start, _this_end = AXText.get_line_at_offset(obj, offset)
        if not this_start:
            prev_obj, prev_offset = self.previous_context(obj, 0)
            return self.get_line_contents_at_offset(prev_obj, prev_offset)

        return [(obj, 0, 0, "")]

    def get_line_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        layout_mode: bool | None = None, # pylint: disable=unused-argument
        use_cache: bool = True  # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the line at offset."""

        text, start, end = AXText.get_line_at_offset(obj, offset)
        return [(obj, start, end, text)]

    def get_next_line_contents(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        layout_mode: bool | None = None, # pylint: disable=unused-argument
        use_cache: bool = True # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the next line."""

        if obj is None:
            obj, offset = self.get_caret_context()

        if offset == -1:
            offset = AXText.get_caret_offset(obj)

        text, start, end = AXText.get_next_line(obj, offset)
        if text:
            return [(obj, start, end, text)]

        _this_line, _this_start, this_end = AXText.get_line_at_offset(obj, offset)
        if this_end == AXText.get_character_count(obj):
            next_obj, next_offset = self.next_context(obj, this_end)
            return self.get_line_contents_at_offset(next_obj, next_offset)

        return [(obj, 0, 0, "")]

    def get_object_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int = 0, # pylint: disable=unused-argument
        use_cache: bool = True # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the object at offset."""

        text = AXText.get_all_text(obj)
        return [(obj, 0, len(text), text)]

    def get_sentence_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        use_cache: bool = True # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns the sentence contents for the specified offset."""

        text, start, end = AXText.get_sentence_at_offset(obj, offset)
        return [(obj, start, end, text)]

    def previous_context(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        skip_space: bool = False,
        restrict_to: Atspi.Accessible | None = None
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the previous viable/valid caret context given obj and offset."""

        if obj is None:
            obj, offset = self.get_caret_context()

        prev_offset = offset - 1
        if skip_space:
            char = AXText.get_character_at_offset(obj, prev_offset)[0]
            while char and char.isspace():
                prev_offset -= 1
                char = AXText.get_character_at_offset(obj, prev_offset)[0]

        if prev_offset >= 0:
            return obj, prev_offset

        if prev_obj := self.find_previous_object(obj, restrict_to):
            if prev_obj != obj and not AXText.get_character_count(prev_obj) and not skip_space:
                return prev_obj, 0
            length = AXText.get_character_count(prev_obj)
            return self.previous_context(prev_obj, length, skip_space, restrict_to)

        return None, -1

    def next_context(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        skip_space: bool = False,
        restrict_to: Atspi.Accessible | None = None
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the next viable/valid caret context given obj and offset."""

        if obj is None:
            obj, offset = self.get_caret_context()

        next_offset = offset + 1
        if skip_space:
            char = AXText.get_character_at_offset(obj, next_offset)[0]
            while char and char.isspace():
                next_offset += 1
                char = AXText.get_character_at_offset(obj, next_offset)[0]

        if next_offset <= AXText.get_character_count(obj):
            return obj, next_offset

        if next_obj := self.find_next_object(obj, restrict_to):
            if next_obj != obj and not AXText.get_character_count(next_obj) and not skip_space:
                return next_obj, 0
            return self.next_context(next_obj, -1, skip_space, restrict_to)

        return None, -1

    def first_context(self, obj: Atspi.Accessible, offset: int) -> tuple[Atspi.Accessible, int]:
        """Returns the first viable/valid caret context given obj and offset."""

        if AXObject.supports_text(obj):
            return obj, offset

        descendant = AXObject.find_descendant(obj, AXObject.supports_text)
        if descendant is not None:
            return descendant, 0

        return obj, offset

    def filter_contents_for_presentation(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        infer_labels: bool = False  # pylint: disable=unused-argument
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Filters contents for presentation, removing objects that should not be included."""

        return contents

    def last_context(self, root: Atspi.Accessible) -> tuple[Atspi.Accessible, int]:
        """Returns the last viable/valid caret context in root."""

        offset = max(0, AXText.get_character_count(root) - 1)
        return root, offset

    def selected_children(
        self,
        obj: Atspi.Accessible
    ) -> list[Atspi.Accessible]:
        """Returns a list of selected children in obj."""

        # TODO - JD: This was originally in the LO script. See if it is still an issue when
        # lots of cells are selected.
        if self.is_spreadsheet_table(obj):
            return []

        return AXSelection.get_selected_children(obj)

    def speak_selected_cell_range(
        self,
        _obj: Atspi.Accessible
    ) -> bool:
        """Speaks the selected cell range in obj."""

        # TODO - JD: This doesn't belong here.
        return False

    def get_selection_container(
        self,
        obj: Atspi.Accessible
    ) -> Atspi.Accessible | None:
        """Returns the selection container for obj."""

        # TODO - JD: Move this into AXUtilities. Or into the where am i presenter.
        if not obj:
            return None

        # LO Writer implements the selection interface on paragraphs and possibly
        # other things.
        if AXUtilities.is_paragraph(obj) or AXUtilities.is_editable(obj):
            return None

        if AXObject.supports_selection(obj):
            return obj

        rolemap = {
            Atspi.Role.CANVAS: [Atspi.Role.LAYERED_PANE],
            Atspi.Role.ICON: [Atspi.Role.LAYERED_PANE],
            Atspi.Role.LIST_ITEM: [Atspi.Role.LIST_BOX],
            Atspi.Role.TREE_ITEM: [Atspi.Role.TREE, Atspi.Role.TREE_TABLE],
            Atspi.Role.TABLE_CELL: [Atspi.Role.TABLE, Atspi.Role.TREE_TABLE],
            Atspi.Role.TABLE_ROW: [Atspi.Role.TABLE, Atspi.Role.TREE_TABLE],
        }

        matching_roles = rolemap.get(AXObject.get_role(obj))
        def is_match(x):
            if matching_roles and AXObject.get_role(x) not in matching_roles:
                return False
            return AXObject.supports_selection(x)

        return AXObject.find_ancestor(obj, is_match)

    def selectable_child_count(
        self,
        obj: Atspi.Accessible
    ) -> int:
        """Returns the number of selectable children in obj."""

        # TODO - JD: Move this into AXUtilities.

        if not AXObject.supports_selection(obj):
            return 0

        if AXObject.supports_table(obj):
            rows = AXTable.get_row_count(obj)
            return max(0, rows)

        rolemap = {
            Atspi.Role.LIST_BOX: [Atspi.Role.LIST_ITEM],
            Atspi.Role.TREE: [Atspi.Role.TREE_ITEM],
        }

        role = AXObject.get_role(obj)
        if role not in rolemap:
            return AXObject.get_child_count(obj)

        def is_match(x):
            return AXObject.get_role(x) in rolemap.get(role)

        return len(self._find_all_descendants(obj, is_match))

    def selected_child_count(
        self,
        obj: Atspi.Accessible
    ) -> int:
        """Returns the number of selected children in obj."""

        # TODO - JD: Move this into AXUtilities.

        if AXObject.supports_table(obj):
            return AXTable.get_selected_row_count(obj)
        return AXSelection.get_selected_child_count(obj)

    def is_clickable_element(
        self,
        obj: Atspi.Accessible # pylint: disable=unused-argument
    ) -> bool:
        """Returns true if obj is a clickable element (in the web sense of that word)."""

        return False

    def has_long_desc(
        self,
        obj: Atspi.Accessible # pylint: disable=unused-argument
    ) -> bool:
        """Returns true if obj has a longdesc (deprecated web attribute)."""

        return False

    def has_meaningful_toggle_action(
        self,
        obj: Atspi.Accessible
    ) -> bool:
        """Returns true if obj has a toggle action that is meaningful. Because app bugs."""

        return AXObject.has_action(obj, "toggle") \
            or AXObject.has_action(obj, object_properties.ACTION_TOGGLE)

    def get_word_at_offset_adjusted_for_navigation(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the word at offset, adjusted for native navigation commands."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        word, start, end = AXText.get_word_at_offset(obj, offset)
        prev_obj, prev_offset = focus_manager.get_manager().get_penultimate_cursor_position()
        if prev_obj != obj:
            return word, start, end

        manager = input_event_manager.get_manager()
        was_previous_word_nav = manager.last_event_was_previous_word_navigation()
        was_next_word_nav = manager.last_event_was_next_word_navigation()

        # If we're in an ongoing series of native navigation-by-word commands, just present the
        # newly-traversed string.
        prev_word, prev_start, prev_end = AXText.get_word_at_offset(prev_obj, prev_offset)
        if self._script.point_of_reference.get("lastTextUnitSpoken") == "word":
            if was_previous_word_nav:
                start = offset
                end = prev_offset
            elif was_next_word_nav:
                start = prev_offset
                end = offset

            word = AXText.get_substring(obj, start, end)
            debug_string = word.replace("\n", "\\n")
            msg = (
                f"SCRIPT UTILITIES: Adjusted word at offset {offset} for ongoing word nav is "
                f"'{debug_string}' ({start}-{end})"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return word, start, end

        # Otherwise, attempt some smarts so that the user winds up with the same presentation
        # they would get were this an ongoing series of native navigation-by-word commands.
        if was_previous_word_nav:
            # If we moved left via native nav, this should be the start of a native-navigation
            # word boundary, regardless of what ATK/AT-SPI2 tells us.
            start = offset

            # The ATK/AT-SPI2 word typically ends in a space; if the ending is neither a space,
            # nor an alphanumeric character, then suspect that character is a navigation boundary
            # where we would have landed before via the native previous word command.
            if not (word[-1].isspace() or word[-1].isalnum()):
                end -= 1

        elif was_next_word_nav:
            # If we moved right via native nav, this should be the end of a native-navigation
            # word boundary, regardless of what ATK/AT-SPI2 tells us.
            end = offset

            # This suggests we just moved to the end of the previous word.
            if word != prev_word and prev_start < offset <= prev_end:
                start = prev_start

            # If the character to the left of our present position is neither a space, nor
            # an alphanumeric character, then suspect that character is a navigation boundary
            # where we would have landed before via the native next word command.
            if offset > 0:
                last_char = AXText.get_substring(obj, offset - 1, offset)
                if not (last_char.isspace() or last_char.isalnum()):
                    start = offset - 1

        word = AXText.get_substring(obj, start, end)

        # We only want to present the newline character when we cross a boundary moving from one
        # word to another. If we're in the same word, strip it out.
        if "\n" in word and word == prev_word:
            if word.startswith("\n"):
                start += 1
            elif word.endswith("\n"):
                end -= 1

        word = AXText.get_substring(obj, start, end)
        debug_string = word.replace("\n", "\\n")
        msg = (
            f"SCRIPT UTILITIES: Adjusted word at offset {offset} for new word nav is "
            f"'{debug_string}' ({start}-{end})"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return word, start, end

    def clear_cached_command_state_deprecated(self) -> None:
        """Clears the cached state for undo, redo, and paste commands."""

        self._script.point_of_reference["undo"] = False
        self._script.point_of_reference["redo"] = False
        self._script.point_of_reference["paste"] = False

    def handle_undo_text_event(
        self,
        event: Atspi.Event
    ) -> bool:
        """Handles a text-changed event resulting from an undo/redo."""

        if input_event_manager.get_manager().last_event_was_undo():
            if not self._script.point_of_reference.get("undo"):
                self._script.present_message(messages.UNDO)
                self._script.point_of_reference["undo"] = True
            AXText.update_cached_selected_text(event.source)
            return True

        if input_event_manager.get_manager().last_event_was_redo():
            if not self._script.point_of_reference.get("redo"):
                self._script.present_message(messages.REDO)
                self._script.point_of_reference["redo"] = True
            AXText.update_cached_selected_text(event.source)
            return True

        return False

    def handle_undo_locus_of_focus_change(self) -> bool:
        """Presents an undo/redo message when the locus of focus changes."""

        if input_event_manager.get_manager().last_event_was_undo():
            if not self._script.point_of_reference.get("undo"):
                self._script.present_message(messages.UNDO)
                self._script.point_of_reference["undo"] = True
            return True

        if input_event_manager.get_manager().last_event_was_redo():
            if not self._script.point_of_reference.get("redo"):
                self._script.present_message(messages.REDO)
                self._script.point_of_reference["redo"] = True
            return True

        return False

    def handle_paste_locus_of_focus_change(self) -> bool:
        """Presents a paste message when the locus of focus changes."""

        if input_event_manager.get_manager().last_event_was_paste():
            if not self._script.point_of_reference.get("paste"):
                self._script.present_message(
                    messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF)
                self._script.point_of_reference["paste"] = True
            return True

        return False

    def all_items_selected(
        self,
        obj: Atspi.Accessible
    ) -> bool:
        """Returns True if all items in obj are selected."""

        # TODO - JD: Move this into AXUtilities.
        if not AXObject.supports_selection(obj):
            return False

        if AXUtilities.is_expandable(obj) and not AXUtilities.is_expanded(obj):
            return False

        if AXUtilities.is_combo_box(obj) or AXUtilities.is_menu(obj):
            return False

        child_count = AXObject.get_child_count(obj)
        if child_count == AXSelection.get_selected_child_count(obj):
            # The selection interface gives us access to what is selected, which might
            # not actually be a direct child.
            child = AXSelection.get_selected_child(obj, 0)
            if AXObject.get_parent(child) != obj:
                return False

            msg = f"SCRIPT UTILITIES: All {child_count} children believed to be selected"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return AXTable.all_cells_are_selected(obj)

    def handle_container_selection_change(
        self,
        obj: Atspi.Accessible
    ) -> bool:
        """Handles a change in a container that supports selection."""

        all_already_selected = self._script.point_of_reference.get("allItemsSelected")
        all_currently_selected = self.all_items_selected(obj)
        if all_already_selected and all_currently_selected:
            return True

        self._script.point_of_reference["allItemsSelected"] = all_currently_selected
        if input_event_manager.get_manager().last_event_was_select_all() and all_currently_selected:
            self._script.present_message(messages.CONTAINER_SELECTED_ALL)
            focus_manager.get_manager().set_locus_of_focus(None, obj, False)
            return True

        return False

    def handle_text_selection_change(
        self,
        obj: Atspi.Accessible,
        speak_message: bool = True
    ) -> bool:
        """Handles a change in the selected text."""

        # Note: This guesswork to figure out what actually changed with respect
        # to text selection will get eliminated once the new text-selection API
        # is added to ATK and implemented by the toolkits. (BGO 638378)

        if not AXObject.supports_text(obj):
            return False

        if input_event_manager.get_manager().last_event_was_cut():
            return False

        old_string, old_start, old_end = AXText.get_cached_selected_text(obj)
        AXText.update_cached_selected_text(obj)
        new_string, new_start, new_end = AXText.get_cached_selected_text(obj)

        if input_event_manager.get_manager().last_event_was_select_all() and new_string:
            if new_string != old_string:
                self._script.speak_message(messages.DOCUMENT_SELECTED_ALL)
            return True

        # Even though we present a message, treat it as unhandled so the new location is
        # still presented.
        if not input_event_manager.get_manager().last_event_was_caret_selection() \
           and old_string and not new_string:
            self._script.speak_message(messages.SELECTION_REMOVED)
            return False

        changes = []
        old_chars = set(range(old_start, old_end))
        new_chars = set(range(new_start, new_end))
        if not old_chars.union(new_chars):
            return False

        if old_chars and new_chars and not old_chars.intersection(new_chars):
            # A simultaneous unselection and selection centered at one offset.
            changes.append([old_start, old_end, messages.TEXT_UNSELECTED])
            changes.append([new_start, new_end, messages.TEXT_SELECTED])
        else:
            change = sorted(old_chars.symmetric_difference(new_chars))
            if not change:
                return False

            change_start, change_end = change[0], change[-1] + 1
            if old_chars < new_chars:
                changes.append([change_start, change_end, messages.TEXT_SELECTED])
                if old_string.endswith("\ufffc") and old_end == change_start:
                    # There's a possibility that we have a link spanning multiple lines. If so,
                    # we want to present the continuation that just became selected.
                    child = AXHypertext.find_child_at_offset(obj, old_end - 1)
                    self.handle_text_selection_change(child, False)
            else:
                changes.append([change_start, change_end, messages.TEXT_UNSELECTED])
                if new_string.endswith("\ufffc"):
                    # There's a possibility that we have a link spanning multiple lines. If so,
                    # we want to present the continuation that just became unselected.
                    child = AXHypertext.find_child_at_offset(obj, new_end - 1)
                    self.handle_text_selection_change(child, False)

        speak_message = speak_message \
            and not speech_and_verbosity_manager.get_manager().get_only_speak_displayed_text()
        for start, end, message in changes:
            string = AXText.get_substring(obj, start, end)
            ends_with_child = string.endswith("\ufffc")
            if ends_with_child:
                end -= 1

            if len(string) > 5000 and speak_message:
                if message == messages.TEXT_SELECTED:
                    self._script.speak_message(messages.selected_character_count(len(string)))
                else:
                    self._script.speak_message(messages.unselected_character_count(len(string)))
            else:
                self._script.say_phrase(obj, start, end)
                if speak_message and not ends_with_child:
                    self._script.speak_message(message, interrupt=False)

            if ends_with_child:
                child = AXHypertext.find_child_at_offset(obj, end)
                self.handle_text_selection_change(child, speak_message)

        return True

    def should_interrupt_for_locus_of_focus_change(
        self,
        old_focus: Atspi.Accessible,
        new_focus: Atspi.Accessible,
        event: Atspi.Event | None = None
    ) -> bool:
        """Returns True if speech should be interrupted to present the new focus."""

        msg = "SCRIPT UTILITIES: Not interrupting for locusOfFocus change: "
        if event is None:
            msg += "event is None"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.type.startswith("object:active-descendant-changed"):
            msg += "event is active-descendant-changed"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_table_cell(old_focus) and AXUtilities.is_text(new_focus) \
           and AXUtilities.is_editable(new_focus):
            msg += "suspected editable cell"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not AXUtilities.is_menu_related(new_focus) \
           and (AXUtilities.is_check_menu_item(old_focus) \
                or AXUtilities.is_radio_menu_item(old_focus)):
            msg += "suspected menuitem state change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXObject.is_ancestor(new_focus, old_focus):
            if old_name := AXObject.get_name(old_focus):
                if old_name == AXObject.get_name(new_focus):
                    msg += "old locusOfFocus is ancestor with same name as new locusOfFocus"
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    return True
                msg += "old locusOfFocus is ancestor of new locusOfFocus, and has a name"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False
            if AXUtilities.is_dialog_or_window(old_focus):
                if AXUtilities.is_menu(new_focus):
                    return True
                msg += "old locusOfFocus is ancestor dialog or window of the new locusOfFocus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False
            return True

        if AXUtilities.object_is_controlled_by(old_focus, new_focus) \
           or AXUtilities.object_is_controlled_by(new_focus, old_focus):
            msg += "new locusOfFocus and old locusOfFocus have controls relation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True
