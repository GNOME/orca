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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"


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
from .ax_component import AXComponent
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Utilities:
    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    ZERO_WIDTH_NO_BREAK_SPACE = '\ufeff'

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        self._script = script

    def nodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

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

    def childNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell.

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

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

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        row, col = AXTable.get_cell_coordinates(obj, prefer_attribute=False)
        nodeLevel = self.nodeLevel(obj)

        for i in range(row + 1, AXTable.get_row_count(table, prefer_attribute=False)):
            cell = AXTable.get_cell_at(table, i, col)
            targets = AXUtilities.get_is_node_child_of(cell)
            if not targets:
                continue

            nodeOf = targets[0]
            if obj == nodeOf:
                nodes.append(cell)
            elif self.nodeLevel(nodeOf) <= nodeLevel:
                break

        tokens = ["SCRIPT UTILITIES:", len(nodes), "child nodes for", obj, "via node-child-of"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return nodes

    def detailsContentForObject(self, obj):
        details = self.detailsForObject(obj)
        return list(map(AXText.get_all_text, details))

    def detailsForObject(self, obj, textOnly=True):
        """Return a list of objects containing details for obj."""

        details = AXUtilities.get_details(obj)
        if not details and AXUtilities.is_toggle_button(obj) and AXUtilities.is_expanded(obj):
            details = [child for child in AXObject.iter_children(obj)]

        if not textOnly:
            return details

        textObjects = []
        for detail in details:

            textObjects.extend(self.findAllDescendants(
                detail, lambda x: not AXText.is_whitespace_or_empty(x)))

        return textObjects

    def documentFrame(self, obj=None):
        """Returns the document frame which is displaying the content.
        Note that this is intended primarily for web content."""

        if not obj:
            obj, offset = self.getCaretContext()

        document = AXObject.find_ancestor(obj, AXUtilities.is_document)
        if document:
            return document

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_document(focus):
            return focus

        return None

    def frameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing obj."""

        results = [None, None]

        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not obj:
            msg = "SCRIPT UTILITIES: frameAndDialog() called without valid object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return results

        topLevel = self.topLevelObject(obj)
        if topLevel is None:
            tokens = ["SCRIPT UTILITIES: could not find top-level object for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return results

        dialog_roles = [Atspi.Role.DIALOG, Atspi.Role.FILE_CHOOSER, Atspi.Role.ALERT]
        role = AXObject.get_role(topLevel)
        if role in dialog_roles:
            results[1] = topLevel
        else:
            if role in [Atspi.Role.FRAME, Atspi.Role.WINDOW]:
                results[0] = topLevel

            def isDialog(x):
                return AXObject.get_role(x) in dialog_roles

            results[1] = AXObject.find_ancestor_inclusive(obj, isDialog)

        tokens = ["SCRIPT UTILITIES:", obj, "is in frame", results[0], "and dialog", results[1]]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return results

    def grabFocusWhenSettingCaret(self, obj):
        return AXUtilities.is_focusable(obj)

    def grabFocusBeforeRouting(self, obj, offset):
        """Whether or not we should perform a grabFocus before routing
        the cursor via the braille cursor routing keys.

        Arguments:
        - obj: the accessible object where the cursor should be routed
        - offset: the offset to which it should be routed

        Returns True if we should do an explicit grabFocus on obj prior
        to routing the cursor.
        """

        return AXUtilities.is_combo_box(obj) \
            and obj != focus_manager.get_manager().get_locus_of_focus()

    def inFindContainer(self, obj=None):
        if obj is None:
            obj = focus_manager.get_manager().get_locus_of_focus()

        if not AXUtilities.is_entry(obj):
            return False

        return AXObject.find_ancestor(obj, AXUtilities.is_tool_bar) is not None

    def getFindResultsCount(self, root=None):
        return ""

    def isAnchor(self, obj):
        return False

    def topLevelObjectIsActiveWindow(self, obj):
        return self.topLevelObject(obj) == focus_manager.get_manager().get_active_window()

    def isProgressBarUpdate(self, obj):
        if not settings_manager.get_manager().get_setting('speakProgressBarUpdates') \
           and not settings_manager.get_manager().get_setting('brailleProgressBarUpdates') \
           and not settings_manager.get_manager().get_setting('beepProgressBarUpdates'):
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
            if self.topLevelObjectIsActiveWindow(obj):
                return True, "Verbosity is window"
            return False, "Top-level object is not active window"

        if verbosity == settings.PROGRESS_BAR_APPLICATION:
            app = AXUtilities.get_application(obj)
            activeApp = script_manager.get_manager().get_active_script_app()
            if app == activeApp:
                return True, "Verbosity is app"
            return False, "App is not active app"

        return True, "Not handled by any other case"

    def descriptionListTerms(self, obj):
        if not AXUtilities.is_description_list(obj):
            return []

        _include = AXUtilities.is_description_term
        _exclude = AXUtilities.is_description_list
        return self.findAllDescendants(obj, _include, _exclude)

    def isDocumentList(self, obj):
        if AXObject.get_role(obj) not in [Atspi.Role.LIST, Atspi.Role.DESCRIPTION_LIST]:
            return False
        return AXObject.find_ancestor(obj, AXUtilities.is_document) is not None

    def isDocumentPanel(self, obj):
        if not AXUtilities.is_panel(obj):
            return False
        return AXObject.find_ancestor(obj, AXUtilities.is_document) is not None

    def isDocument(self, obj):
        return AXUtilities.is_document(obj)

    def inDocumentContent(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        return self.getDocumentForObject(obj) is not None

    def activeDocument(self, window=None):
        return self.getTopLevelDocumentForObject(focus_manager.get_manager().get_locus_of_focus())

    def isTopLevelDocument(self, obj):
        return self.isDocument(obj) and not AXObject.find_ancestor(obj, self.isDocument)

    def getTopLevelDocumentForObject(self, obj):
        return AXObject.find_ancestor_inclusive(obj, self.isTopLevelDocument)

    def getDocumentForObject(self, obj):
        return AXObject.find_ancestor_inclusive(obj, self.isDocument)

    def columnConvert(self, column):
        return column

    def isTextDocumentTable(self, obj):
        if not AXUtilities.is_table(obj):
            return False

        doc = self.getDocumentForObject(obj)
        return doc is not None and not AXUtilities.is_document_spreadsheet(doc)

    def isGUITable(self, obj):
        return AXUtilities.is_table(obj) and self.getDocumentForObject(obj) is None

    def isSpreadSheetTable(self, obj):
        if not (AXUtilities.is_table(obj) and AXObject.supports_table(obj)):
            return False

        doc = self.getDocumentForObject(obj)
        if doc is None:
            return False
        if AXUtilities.is_document_spreadsheet(doc):
            return True

        return AXTable.get_row_count(obj) > 65536

    def isTextDocumentCell(self, obj):
        if not AXUtilities.is_table_cell_or_header(obj):
            return False
        return AXObject.find_ancestor(obj, self.isTextDocumentTable)

    def isGUICell(self, obj):
        if not AXUtilities.is_table_cell_or_header(obj):
            return False
        return AXObject.find_ancestor(obj, self.isGUITable)

    def isSpreadSheetCell(self, obj):
        if not AXUtilities.is_table_cell_or_header(obj):
            return False
        return AXObject.find_ancestor(obj, self.isSpreadSheetTable)

    def cellColumnChanged(self, cell, prevCell=None):
        column = AXTable.get_cell_coordinates(cell)[1]
        if column == -1:
            return False

        if prevCell is None:
            lastColumn = self._script.point_of_reference.get("lastColumn")
        else:
            lastColumn = AXTable.get_cell_coordinates(prevCell)[1]

        return column != lastColumn

    def cellRowChanged(self, cell, prevCell=None):
        row = AXTable.get_cell_coordinates(cell)[0]
        if row == -1:
            return False

        if prevCell is None:
            lastRow = self._script.point_of_reference.get("lastRow")
        else:
            lastRow = AXTable.get_cell_coordinates(prevCell)[0]
        return row != lastRow

    def shouldReadFullRow(self, obj, prevObj=None):
        if self._script.inSayAll():
            return False

        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return False

        if not self.cellRowChanged(obj, prevObj):
            return False

        table = AXTable.get_table(obj)
        if table is None:
            return False

        if not self.getDocumentForObject(table):
            return settings_manager.get_manager().get_setting('readFullRowInGUITable')

        if self.isSpreadSheetTable(table):
            return settings_manager.get_manager().get_setting('readFullRowInSpreadSheet')

        return settings_manager.get_manager().get_setting('readFullRowInDocumentTable')

    def getNotificationContent(self, obj):
        if not AXUtilities.is_notification(obj):
            return ""

        tokens = []
        name = AXObject.get_name(obj)
        if name:
            tokens.append(name)
        text = self.expandEOCs(obj)
        if text and text not in tokens:
            tokens.append(text)
        else:
            labels = " ".join(map(lambda x: AXText.get_all_text(x) or AXObject.get_name(x),
                                  self.unrelatedLabels(obj, False, 1)))
            if labels and labels not in tokens:
                tokens.append(labels)

        description = AXObject.get_description(obj)
        if description and description not in tokens:
            tokens.append(description)

        return " ".join(tokens)

    def isLink(self, obj):
        """Returns True if obj is a link."""

        return AXUtilities.is_link(obj)

    def getObjectFromPath(self, path):
        start = self._script.app
        rv = None
        for p in path:
            if p == -1:
                continue
            try:
                start = start[p]
            except Exception:
                break
        else:
            rv = start

        return rv

    def realActiveAncestor(self, obj):
        if AXUtilities.is_focused(obj):
            return obj

        def pred(x):
            return AXUtilities.is_table_cell_or_header(x) or AXUtilities.is_list_item(x)

        ancestor = AXObject.find_ancestor(obj, pred)
        if ancestor is not None \
           and not AXUtilities.is_layout_only(AXObject.get_parent(ancestor)):
            obj = ancestor

        return obj

    def realActiveDescendant(self, obj):
        """Given an object that should be a child of an object that
        manages its descendants, return the child that is the real
        active descendant carrying useful information.

        Arguments:
        - obj: an object that should be a child of an object that
        manages its descendants.
        """

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

    def _topLevelRoles(self):
        roles = [Atspi.Role.DIALOG,
                 Atspi.Role.FILE_CHOOSER,
                 Atspi.Role.FRAME,
                 Atspi.Role.WINDOW,
                 Atspi.Role.ALERT]
        return roles

    def _findWindowWithDescendant(self, child):
        """Searches each frame/window/dialog of an application to find the one
        which contains child. This is extremely non-performant and should only
        be used to work around broken accessibility trees where topLevelObject
        fails."""

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

    def _isTopLevelObject(self, obj):
        return AXObject.get_role(obj) in self._topLevelRoles() \
            and AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.APPLICATION

    def topLevelObject(self, obj, useFallbackSearch=False):
        """Returns the top-level object (frame, dialog ...) containing obj,
        or None if obj is not inside a top-level object.

        Arguments:
        - obj: the Accessible object
        """

        rv = AXObject.find_ancestor_inclusive(obj, self._isTopLevelObject)
        tokens = ["SCRIPT UTILITIES:", rv, "is top-level object for:", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if rv is None and useFallbackSearch:
            msg = "SCRIPT UTILITIES: Attempting to find top-level object via fallback search"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            rv = self._findWindowWithDescendant(obj)

        return rv

    def topLevelObjectIsActiveAndCurrent(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        topLevel = self.topLevelObject(obj)
        if not topLevel:
            return False

        AXObject.clear_cache(topLevel, False, "Ensuring we have the correct state.")
        if not AXUtilities.is_active(topLevel) or AXUtilities.is_defunct(topLevel):
            return False

        return topLevel == focus_manager.get_manager().get_active_window()

    @staticmethod
    def pathComparison(path1, path2):
        """Compares the two paths and returns -1, 0, or 1 to indicate if path1
        is before, the same, or after path2."""

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

    def findAllDescendants(self, root, includeIf=None, excludeIf=None):
        if root is None:
            return []

        # Don't bother if the root is a 'pre' or 'code' element. Those often have
        # nothing but a TON of static text leaf nodes, which we want to ignore.
        if AXUtilities.is_code(root):
            tokens = ["SCRIPUT UTILITIES: Returning 0 descendants for pre/code", root]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        return AXObject.find_all_descendants(root, includeIf, excludeIf)

    def unrelatedLabels(self, root, onlyShowing=True, minimumWords=3):
        """Returns a list containing all the unrelated (i.e., have no
        relations to anything and are not a fundamental element of a
        more atomic component like a combo box) labels under the given
        root.  Note that the labels must also be showing on the display.

        Arguments:
        - root: the Accessible object to traverse
        - onlyShowing: if True, only return labels with STATE_SHOWING

        Returns a list of unrelated labels under the given root.
        """

        if self._script.spellcheck and self._script.spellcheck.is_spell_check_window(root):
            return []

        labelRoles = [Atspi.Role.LABEL, Atspi.Role.STATIC]
        skipRoles = [Atspi.Role.COMBO_BOX,
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
                     Atspi.Role.PUSH_BUTTON,
                     Atspi.Role.SCROLL_PANE,
                     Atspi.Role.SPLIT_PANE,
                     Atspi.Role.TABLE,
                     Atspi.Role.TOGGLE_BUTTON,
                     Atspi.Role.TREE,
                     Atspi.Role.TREE_TABLE,
                     Atspi.Role.WINDOW]

        if AXObject.get_role(root) in skipRoles:
            return []

        def _include(x):
            if not (x and AXObject.get_role(x) in labelRoles):
                return False
            if not AXUtilities.object_is_unrelated(x):
                return False
            if onlyShowing and not AXUtilities.is_showing(x):
                return False
            return True

        def _exclude(x):
            if not x or AXObject.get_role(x) in skipRoles:
                return True
            if onlyShowing and not AXUtilities.is_showing(x):
                return True
            return False

        labels = self.findAllDescendants(root, _include, _exclude)

        rootName = AXObject.get_name(root)

        # Eliminate things suspected to be labels for widgets
        labels_filtered = []
        for label in labels:
            name = AXObject.get_name(label) or AXText.get_all_text(label)
            if name and name in [rootName, AXObject.get_name(AXObject.get_parent(label))]:
                continue
            if len(name.split()) < minimumWords:
                continue
            if rootName.find(name) >= 0:
                continue
            labels_filtered.append(label)

        return AXComponent.sort_objects_by_position(labels_filtered)

    def findPreviousObject(self, obj, restrict_to=None):
        """Finds the object before this one."""

        if restrict_to is None:
            restrict_to = self.getTopLevelDocumentForObject(obj)

        result = AXUtilities.get_previous_object(obj)
        tokens = ["SCRIPT UTILITIES: Previous object for", obj, "is", result, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if restrict_to is not None and not AXObject.is_ancestor(result, restrict_to, True):
            tokens = ["SCRIPT UTILITIES:", result, "is not a descendant of", restrict_to]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return result

    def findNextObject(self, obj, restrict_to=None):
        """Finds the object after this one."""

        if restrict_to is None:
            restrict_to = self.getTopLevelDocumentForObject(obj)

        result = AXUtilities.get_next_object(obj)
        tokens = ["SCRIPT UTILITIES: Next object for", obj, "is", result, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if restrict_to is not None and not AXObject.is_ancestor(result, restrict_to, True):
            tokens = ["SCRIPT UTILITIES:", result, "is not a descendant of", restrict_to]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None
        return result

    def expandEOCs(self, obj, startOffset=0, endOffset=-1):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with their text.

        Arguments
        - obj: the object whose text should be expanded
        - startOffset: the offset of the first character to be included
        - endOffset: the offset of the last character to be included

        Returns the fully expanded text for the object.
        """

        # TODO - JD: Audit all callers and eliminate these arguments having been set to None.
        if startOffset is None:
            tokens = ["SCRIPT UTILITIES: expandEOCs called with start offset of None on", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            startOffset = 0
        if endOffset is None:
            tokens = ["SCRIPT UTILITIES: expandEOCs called with end offset of None on", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            endOffset = -1

        string = AXText.get_substring(obj, startOffset, endOffset)
        if self.EMBEDDED_OBJECT_CHARACTER not in string:
            return string

        blockRoles = [Atspi.Role.HEADING,
                      Atspi.Role.LIST,
                      Atspi.Role.LIST_ITEM,
                      Atspi.Role.PARAGRAPH,
                      Atspi.Role.SECTION,
                      Atspi.Role.TABLE,
                      Atspi.Role.TABLE_CELL,
                      Atspi.Role.TABLE_ROW]

        toBuild = list(string)
        for i, char in enumerate(toBuild):
            if char == self.EMBEDDED_OBJECT_CHARACTER:
                child = AXHypertext.get_child_at_offset(obj, i + startOffset)
                result = self.expandEOCs(child)
                if child and AXObject.get_role(child) in blockRoles:
                    result += " "
                toBuild[i] = result

        result = "".join(toBuild)
        tokens = ["SCRIPT UTILITIES: Expanded EOCs for", obj, f"range: {startOffset}:{endOffset}:",
                 f"'{result}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.EMBEDDED_OBJECT_CHARACTER in result:
            msg = "SCRIPT UTILITIES: Unable to expand EOCs"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return result

    def isErrorForContents(self, obj, contents=None):
        """Returns True of obj is an error message for the contents."""

        if not contents:
            return False

        if not AXUtilities.get_is_error_for(obj):
            return False

        for acc, _start, _end, _string in contents:
            targets = AXUtilities.get_error_message(acc)
            if obj in targets:
                return True

        return False

    def deletedText(self, event):
        return event.any_data

    def insertedText(self, event):
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

    def getCaretContext(self):
        obj = focus_manager.get_manager().get_locus_of_focus()
        offset = AXText.get_caret_offset(obj)
        return obj, offset

    def setCaretPosition(self, obj, offset, documentFrame=None):
        focus_manager.get_manager().set_locus_of_focus(None, obj, False)
        self.setCaretOffset(obj, offset)

    def setCaretOffset(self, obj, offset):
        # TODO - JD. Remove this function if the web override can be adjusted
        AXText.set_caret_offset(obj, offset)

    def splitSubstringByLanguage(self, obj, start, end):
        """Returns a list of (start, end, string, language, dialect) tuples."""

        rv = []
        allSubstrings = self.getLanguageAndDialectFromTextAttributes(obj, start, end)
        for startOffset, endOffset, language, dialect in allSubstrings:
            if start >= endOffset:
                continue
            if end <= startOffset:
                break
            startOffset = max(start, startOffset)
            endOffset = min(end, endOffset)
            string = AXText.get_substring(obj, startOffset, endOffset)
            rv.append([startOffset, endOffset, string, language, dialect])

        return rv

    def getLanguageAndDialectForSubstring(self, obj, start, end):
        """Returns a (language, dialect) tuple. If multiple languages apply to
        the substring, language and dialect will be empty strings. Callers must
        do any preprocessing to avoid that condition."""

        allSubstrings = self.getLanguageAndDialectFromTextAttributes(obj, start, end)
        for startOffset, endOffset, language, dialect in allSubstrings:
            if startOffset <= start and endOffset >= end:
                return language, dialect

        return "", ""

    def getLanguageAndDialectFromTextAttributes(self, obj, startOffset=0, endOffset=-1):
        """Returns a list of (start, end, language, dialect) tuples for obj
        based on what is exposed via text attributes."""

        rv = []
        attributeSet = AXText.get_all_text_attributes(obj, startOffset, endOffset)
        lastLanguage = lastDialect = ""
        for (start, end, attrs) in attributeSet:
            language = attrs.get("language", "")
            dialect = ""
            if "-" in language:
                language, dialect = language.split("-", 1)
            if rv and lastLanguage == language and lastDialect == dialect:
                rv[-1] = rv[-1][0], end, language, dialect
            else:
                rv.append((start, end, language, dialect))
            lastLanguage, lastDialect = language, dialect

        return rv

    def getLineContentsAtOffset(self, obj, offset, layoutMode=True, useCache=True):
        return []

    def getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        return []

    def previousContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        return obj, offset - 1

    def nextContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        return obj, offset + 1

    def lastContext(self, root):
        offset = max(0, AXText.get_character_count(root) - 1)
        return root, offset

    def selectedChildren(self, obj):
        # TODO - JD: This was originally in the LO script. See if it is still an issue when
        # lots of cells are selected.
        if self.isSpreadSheetTable(obj):
            return []

        return AXSelection.get_selected_children(obj)

    def speakSelectedCellRange(self, obj):
        return False

    def getSelectionContainer(self, obj):
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

        matchingRoles = rolemap.get(AXObject.get_role(obj))
        def isMatch(x):
            if matchingRoles and AXObject.get_role(x) not in matchingRoles:
                return False
            return AXObject.supports_selection(x)

        return AXObject.find_ancestor(obj, isMatch)

    def selectableChildCount(self, obj):
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

        def isMatch(x):
            return AXObject.get_role(x) in rolemap.get(role)

        return len(self.findAllDescendants(obj, isMatch))

    def selectedChildCount(self, obj):
        if AXObject.supports_table(obj):
            return AXTable.get_selected_row_count(obj)
        return AXSelection.get_selected_child_count(obj)

    def isPopupMenuForCurrentItem(self, obj):
        if not AXUtilities.is_menu(obj):
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_menu_item(focus) and AXUtilities.has_popup(focus):
            name = AXObject.get_name(obj)
            return name and name == AXObject.get_name(focus)

        return False

    def isClickableElement(self, obj):
        return False

    def hasLongDesc(self, obj):
        return False

    def hasMeaningfulToggleAction(self, obj):
        return AXObject.has_action(obj, "toggle") \
            or AXObject.has_action(obj, object_properties.ACTION_TOGGLE)

    def getWordAtOffsetAdjustedForNavigation(self, obj, offset=None):
        word, start, end = AXText.get_word_at_offset(obj, offset)
        prevObj, prevOffset = self._script.point_of_reference.get(
            "penultimateCursorPosition", (None, -1))
        if prevObj != obj:
            return word, start, end

        manager = input_event_manager.get_manager()
        wasPreviousWordNav = manager.last_event_was_previous_word_navigation()
        wasNextWordNav = manager.last_event_was_next_word_navigation()

        # If we're in an ongoing series of native navigation-by-word commands, just present the
        # newly-traversed string.
        prevWord, prevStart, prevEnd = AXText.get_word_at_offset(prevObj, prevOffset)
        if self._script.point_of_reference.get("lastTextUnitSpoken") == "word":
            if wasPreviousWordNav:
                start = offset
                end = prevOffset
            elif wasNextWordNav:
                start = prevOffset
                end = offset

            word = AXText.get_substring(obj, start, end)
            debugString = word.replace("\n", "\\n")
            msg = (
                f"SCRIPT UTILITIES: Adjusted word at offset {offset} for ongoing word nav is "
                f"'{debugString}' ({start}-{end})"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return word, start, end

        # Otherwise, attempt some smarts so that the user winds up with the same presentation
        # they would get were this an ongoing series of native navigation-by-word commands.
        if wasPreviousWordNav:
            # If we moved left via native nav, this should be the start of a native-navigation
            # word boundary, regardless of what ATK/AT-SPI2 tells us.
            start = offset

            # The ATK/AT-SPI2 word typically ends in a space; if the ending is neither a space,
            # nor an alphanumeric character, then suspect that character is a navigation boundary
            # where we would have landed before via the native previous word command.
            if not (word[-1].isspace() or word[-1].isalnum()):
                end -= 1

        elif wasNextWordNav:
            # If we moved right via native nav, this should be the end of a native-navigation
            # word boundary, regardless of what ATK/AT-SPI2 tells us.
            end = offset

            # This suggests we just moved to the end of the previous word.
            if word != prevWord and prevStart < offset <= prevEnd:
                start = prevStart

            # If the character to the left of our present position is neither a space, nor
            # an alphanumeric character, then suspect that character is a navigation boundary
            # where we would have landed before via the native next word command.
            lastChar = AXText.get_substring(obj, offset - 1, offset)
            if not (lastChar.isspace() or lastChar.isalnum()):
                start = offset - 1

        word = AXText.get_substring(obj, start, end)

        # We only want to present the newline character when we cross a boundary moving from one
        # word to another. If we're in the same word, strip it out.
        if "\n" in word and word == prevWord:
            if word.startswith("\n"):
                start += 1
            elif word.endswith("\n"):
                end -= 1

        word = AXText.get_substring(obj, start, end)
        debugString = word.replace("\n", "\\n")
        msg = (
            f"SCRIPT UTILITIES: Adjusted word at offset {offset} for new word nav is "
            f"'{debugString}' ({start}-{end})"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return word, start, end

    def clearCachedCommandState(self):
        self._script.point_of_reference['undo'] = False
        self._script.point_of_reference['redo'] = False
        self._script.point_of_reference['paste'] = False

    def handleUndoTextEvent(self, event):
        if input_event_manager.get_manager().last_event_was_undo():
            if not self._script.point_of_reference.get('undo'):
                self._script.presentMessage(messages.UNDO)
                self._script.point_of_reference['undo'] = True
            AXText.update_cached_selected_text(event.source)
            return True

        if input_event_manager.get_manager().last_event_was_redo():
            if not self._script.point_of_reference.get('redo'):
                self._script.presentMessage(messages.REDO)
                self._script.point_of_reference['redo'] = True
            AXText.update_cached_selected_text(event.source)
            return True

        return False

    def handleUndoLocusOfFocusChange(self):
        # TODO - JD: Is this still needed?
        if focus_manager.get_manager().focus_is_active_window():
            return False

        if input_event_manager.get_manager().last_event_was_undo():
            if not self._script.point_of_reference.get('undo'):
                self._script.presentMessage(messages.UNDO)
                self._script.point_of_reference['undo'] = True
            return True

        if input_event_manager.get_manager().last_event_was_redo():
            if not self._script.point_of_reference.get('redo'):
                self._script.presentMessage(messages.REDO)
                self._script.point_of_reference['redo'] = True
            return True

        return False

    def handlePasteLocusOfFocusChange(self):
        # TODO - JD: Is this still needed?
        if focus_manager.get_manager().focus_is_active_window():
            return False

        if input_event_manager.get_manager().last_event_was_paste():
            if not self._script.point_of_reference.get('paste'):
                self._script.presentMessage(
                    messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF)
                self._script.point_of_reference['paste'] = True
            return True

        return False

    def presentFocusChangeReason(self):
        if self.handleUndoLocusOfFocusChange():
            return True
        if self.handlePasteLocusOfFocusChange():
            return True
        return False

    def allItemsSelected(self, obj):
        if not AXObject.supports_selection(obj):
            return False

        if AXUtilities.is_expandable(obj) and not AXUtilities.is_expanded(obj):
            return False

        if AXUtilities.is_combo_box(obj) or AXUtilities.is_menu(obj):
            return False

        childCount = AXObject.get_child_count(obj)
        if childCount == AXSelection.get_selected_child_count(obj):
            # The selection interface gives us access to what is selected, which might
            # not actually be a direct child.
            child = AXSelection.get_selected_child(obj, 0)
            if AXObject.get_parent(child) != obj:
                return False

            msg = f"SCRIPT UTILITIES: All {childCount} children believed to be selected"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return AXTable.all_cells_are_selected(obj)

    def handleContainerSelectionChange(self, obj):
        allAlreadySelected = self._script.point_of_reference.get('allItemsSelected')
        allCurrentlySelected = self.allItemsSelected(obj)
        if allAlreadySelected and allCurrentlySelected:
            return True

        self._script.point_of_reference['allItemsSelected'] = allCurrentlySelected
        if input_event_manager.get_manager().last_event_was_select_all() and allCurrentlySelected:
            self._script.presentMessage(messages.CONTAINER_SELECTED_ALL)
            focus_manager.get_manager().set_locus_of_focus(None, obj, False)
            return True

        return False

    def handleTextSelectionChange(self, obj, speakMessage=True):
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
                self._script.speakMessage(messages.DOCUMENT_SELECTED_ALL)
            return True

        # Even though we present a message, treat it as unhandled so the new location is
        # still presented.
        if not input_event_manager.get_manager().last_event_was_caret_selection() \
           and old_string and not new_string:
            self._script.speakMessage(messages.SELECTION_REMOVED)
            return False

        changes = []
        oldChars = set(range(old_start, old_end))
        newChars = set(range(new_start, new_end))
        if not oldChars.union(newChars):
            return False

        if oldChars and newChars and not oldChars.intersection(newChars):
            # A simultaneous unselection and selection centered at one offset.
            changes.append([old_start, old_end, messages.TEXT_UNSELECTED])
            changes.append([new_start, new_end, messages.TEXT_SELECTED])
        else:
            change = sorted(oldChars.symmetric_difference(newChars))
            if not change:
                return False

            changeStart, changeEnd = change[0], change[-1] + 1
            if oldChars < newChars:
                changes.append([changeStart, changeEnd, messages.TEXT_SELECTED])
                if old_string.endswith(self.EMBEDDED_OBJECT_CHARACTER) and old_end == changeStart:
                    # There's a possibility that we have a link spanning multiple lines. If so,
                    # we want to present the continuation that just became selected.
                    child = AXHypertext.get_child_at_offset(obj, old_end - 1)
                    self.handleTextSelectionChange(child, False)
            else:
                changes.append([changeStart, changeEnd, messages.TEXT_UNSELECTED])
                if new_string.endswith(self.EMBEDDED_OBJECT_CHARACTER):
                    # There's a possibility that we have a link spanning multiple lines. If so,
                    # we want to present the continuation that just became unselected.
                    child = AXHypertext.get_child_at_offset(obj, new_end - 1)
                    self.handleTextSelectionChange(child, False)

        speakMessage = speakMessage \
            and not settings_manager.get_manager().get_setting('onlySpeakDisplayedText')
        for start, end, message in changes:
            string = AXText.get_substring(obj, start, end)
            endsWithChild = string.endswith(self.EMBEDDED_OBJECT_CHARACTER)
            if endsWithChild:
                end -= 1

            if len(string) > 5000 and speakMessage:
                if message == messages.TEXT_SELECTED:
                    self._script.speakMessage(messages.selectedCharacterCount(len(string)))
                else:
                    self._script.speakMessage(messages.unselectedCharacterCount(len(string)))
            else:
                self._script.sayPhrase(obj, start, end)
                if speakMessage and not endsWithChild:
                    self._script.speakMessage(message, interrupt=False)

            if endsWithChild:
                child = AXHypertext.get_child_at_offset(obj, end)
                self.handleTextSelectionChange(child, speakMessage)

        return True

    def shouldInterruptForLocusOfFocusChange(self, old_focus, new_focus, event=None):
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
            if AXObject.get_name(old_focus):
                msg += "old locusOfFocus is ancestor with name of new locusOfFocus"
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
