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
import locale
import re
import time
from difflib import SequenceMatcher

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk
from gi.repository import Gtk

from . import colornames
from . import debug
from . import focus_manager
from . import keynames
from . import keybindings
from . import input_event_manager
from . import mathsymbols
from . import messages
from . import object_properties
from . import pronunciation_dict
from . import script_manager
from . import settings
from . import settings_manager
from . import text_attribute_names
from .ax_component import AXComponent
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Utilities:

    _last_clipboard_update = time.time()

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    ZERO_WIDTH_NO_BREAK_SPACE = '\ufeff'
    flags = re.UNICODE
    WORDS_RE = re.compile(r"(\W+)", flags)
    PUNCTUATION = re.compile(r"[^\w\s]", flags)

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        self._script = script
        self._clipboardHandlerId = None
        self._selectedMenuBarMenu = {}

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def childNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell.

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

        if not AXUtilities.is_expanded(obj):
            return []

        parent = AXTable.get_table(obj)
        if parent is None:
            return []

        # First see if this accessible implements RELATION_NODE_PARENT_OF.
        # If it does, the full target list are the nodes. If it doesn't
        # we'll do an old-school, row-by-row search for child nodes.
        nodes = AXUtilities.get_is_node_parent_of(obj)
        tokens = ["SCRIPT UTILITIES:", len(nodes), "child nodes for", obj, "via node-parent-of"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if nodes:
            return nodes

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        row, col = AXTable.get_cell_coordinates(obj, prefer_attribute=False)
        nodeLevel = self.nodeLevel(obj)

        for i in range(row + 1, AXTable.get_row_count(parent, prefer_attribute=False)):
            cell = AXTable.get_cell_at(parent, i, col)
            targets = AXUtilities.get_is_node_child_of(cell)
            if not targets:
                continue

            nodeOf = targets[0]
            if obj == nodeOf:
                nodes.append(cell)
            elif self.nodeLevel(nodeOf) <= nodeLevel:
                break

        tokens = ["SCRIPT UTILITIES:", len(nodes), "child nodes for", obj, "via node-child-of"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return nodes

    def commonAncestor(self, a, b):
        """Finds the common ancestor between Accessible a and Accessible b.

        Arguments:
        - a: Accessible
        - b: Accessible
        """

        tokens = ["SCRIPT UTILITIES: Looking for common ancestor of", a, "and", b]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not (a and b):
            return None

        if a == b:
            return a

        aParents = [a]
        parent = AXObject.get_parent_checked(a)
        while parent:
            aParents.append(parent)
            parent = AXObject.get_parent_checked(parent)
        aParents.reverse()

        bParents = [b]
        parent = AXObject.get_parent_checked(b)
        while parent:
            bParents.append(parent)
            parent = AXObject.get_parent_checked(parent)
        bParents.reverse()

        commonAncestor = None
        maxSearch = min(len(aParents), len(bParents))
        i = 0
        while i < maxSearch:
            if aParents[i] == bParents[i]:
                commonAncestor = aParents[i]
                i += 1
            else:
                break

        tokens = ["SCRIPT UTILITIES: Common ancestor of", a, "and", b, "is", commonAncestor]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return commonAncestor

    def displayedLabel(self, obj):
        """If there is an object labelling the given object, return the
        text being displayed for the object labelling this object.
        Otherwise, return None.

        Argument:
        - obj: the object in question

        Returns the string of the object labelling this object, or None
        if there is nothing of interest here.
        """

        labels = AXUtilities.get_is_labelled_by(obj)
        return " ".join(AXText.get_all_text(label) or AXObject.get_name(label) for label in labels)

    def preferDescriptionOverName(self, obj):
        return False

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

    def displayedDescription(self, obj):
        """Returns the text being displayed for the object describing obj."""

        descriptions = AXUtilities.get_is_described_by(obj)
        return " ".join(AXText.get_all_text(d) or AXObject.get_name(d) for d in descriptions)

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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return results

        topLevel = self.topLevelObject(obj)
        if topLevel is None:
            tokens = ["SCRIPT UTILITIES: could not find top-level object for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return results

        dialog_roles = [Atspi.Role.DIALOG, Atspi.Role.FILE_CHOOSER]
        if self._treatAlertsAsDialogs():
            dialog_roles.append(Atspi.Role.ALERT)

        role = AXObject.get_role(topLevel)
        if role in dialog_roles:
            results[1] = topLevel
        else:
            if role in [Atspi.Role.FRAME, Atspi.Role.WINDOW]:
                results[0] = topLevel

            def isDialog(x):
                return AXObject.get_role(x) in dialog_roles

            if isDialog(obj):
                results[1] = obj
            else:
                results[1] = AXObject.find_ancestor(obj, isDialog)

        tokens = ["SCRIPT UTILITIES:", obj, "is in frame", results[0], "and dialog", results[1]]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return results

    def presentEventFromNonShowingObject(self, event):
        if event.source == focus_manager.get_manager().get_locus_of_focus():
            return True

        return False

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

    def isCodeDescendant(self, obj):
        return False

    def isDockedFrame(self, obj):
        if not AXUtilities.is_frame(obj):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get('window-type') == 'dock'

    def isDesktop(self, obj):
        if not AXUtilities.is_frame(obj):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get('is-desktop') == 'true'

    def isComboBoxWithToggleDescendant(self, obj):
        return False

    def isToggleDescendantOfComboBox(self, obj):
        return False

    def isTypeahead(self, obj):
        return False

    def isOrDescendsFrom(self, obj, ancestor):
        if obj == ancestor:
            return True

        return AXObject.find_ancestor(obj, lambda x: x and x == ancestor)

    def isFunctionalDialog(self, obj):
        """Returns True if the window is a functioning as a dialog.
        This method should be subclassed by application scripts as
        needed.
        """

        return False

    def isContentError(self, obj):
        return False

    def isInlineSuggestion(self, obj):
        return False

    def isFirstItemInInlineContentSuggestion(self, obj):
        return False

    def isLastItemInInlineContentSuggestion(self, obj):
        return False

    def is_empty(self, obj):
        return False

    def isHidden(self, obj):
        return False

    def speakMathSymbolNames(self, obj=None):
        return False

    def isInMath(self):
        return False

    def getMathDenominator(self, obj):
        return None

    def getMathNumerator(self, obj):
        return None

    def getMathRootBase(self, obj):
        return None

    def getMathRootIndex(self, obj):
        return None

    def getMathScriptBase(self, obj):
        return None

    def getMathScriptSubscript(self, obj):
        return None

    def getMathScriptSuperscript(self, obj):
        return None

    def getMathScriptUnderscript(self, obj):
        return None

    def getMathScriptOverscript(self, obj):
        return None

    def getMathPrescripts(self, obj):
        return []

    def getMathPostscripts(self, obj):
        return []

    def getMathEnclosures(self, obj):
        return []

    def getMathFencedSeparators(self, obj):
        return ['']

    def getMathFences(self, obj):
        return ['', '']

    def getMathNestingLevel(self, obj, test=None):
        return 0

    def getLandmarkTypes(self):
        return ["banner",
                "complementary",
                "contentinfo",
                "doc-acknowledgments",
                "doc-afterword",
                "doc-appendix",
                "doc-bibliography",
                "doc-chapter",
                "doc-conclusion",
                "doc-credits",
                "doc-endnotes",
                "doc-epilogue",
                "doc-errata",
                "doc-foreword",
                "doc-glossary",
                "doc-index",
                "doc-introduction",
                "doc-pagelist",
                "doc-part",
                "doc-preface",
                "doc-prologue",
                "doc-toc",
                "form",
                "main",
                "navigation",
                "region",
                "search"]

    def isProgressBar(self, obj):
        if not AXUtilities.is_progress_bar(obj):
            return False
        return AXValue.get_value_as_percent(obj) is not None

    def topLevelObjectIsActiveWindow(self, obj):
        return self.topLevelObject(obj) == focus_manager.get_manager().get_active_window()

    def isProgressBarUpdate(self, obj):
        if not settings_manager.get_manager().get_setting('speakProgressBarUpdates') \
           and not settings_manager.get_manager().get_setting('brailleProgressBarUpdates') \
           and not settings_manager.get_manager().get_setting('beepProgressBarUpdates'):
            return False, "Updates not enabled"

        if not self.isProgressBar(obj):
            return False, "Is not progress bar"

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
            app = AXObject.get_application(obj)
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
        if self.isTopLevelDocument(obj):
            return obj

        return AXObject.find_ancestor(obj, self.isTopLevelDocument)

    def getDocumentForObject(self, obj):
        if not obj:
            return None

        if self.isDocument(obj):
            return obj

        return AXObject.find_ancestor(obj, self.isDocument)

    def getModalDialog(self, obj):
        if not obj:
            return False

        if AXUtilities.is_modal_dialog(obj):
            return obj

        return AXObject.find_ancestor(obj, AXUtilities.is_modal_dialog)

    def isModalDialogDescendant(self, obj):
        if not obj:
            return False

        return self.getModalDialog(obj) is not None

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

    def isSorted(self, obj):
        return False

    def isAscending(self, obj):
        return False

    def isDescending(self, obj):
        return False

    def getSortOrderDescription(self, obj, includeName=False):
        if not (obj and self.isSorted(obj)):
            return ""

        if self.isAscending(obj):
            result = object_properties.SORT_ORDER_ASCENDING
        elif self.isDescending(obj):
            result = object_properties.SORT_ORDER_DESCENDING
        else:
            result = object_properties.SORT_ORDER_OTHER

        if includeName and AXObject.get_name(obj):
            result = f"{AXObject.get_name(obj)}. {result}"

        return result

    def isFocusableLabel(self, obj):
        return AXUtilities.is_label(obj) and AXUtilities.is_focusable(obj)

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
            labels = " ".join(map(AXText.get_all_text, self.unrelatedLabels(obj, False, 1)))
            if labels and labels not in tokens:
                tokens.append(labels)

        description = AXObject.get_description(obj)
        if description and description not in tokens:
            tokens.append(description)

        return " ".join(tokens)

    def isTreeDescendant(self, obj):
        if obj is None:
            return False

        if AXUtilities.is_tree_item(obj):
            return True

        return AXObject.find_ancestor(obj, AXUtilities.is_tree_or_tree_table) is not None

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a container which has
        no presentable information (label, name, displayed text, etc.)."""

        layoutOnly = False

        if not AXObject.is_valid(obj):
            return True

        role = AXObject.get_role(obj)
        parentRole = AXObject.get_role(AXObject.get_parent(obj))
        firstChild = AXObject.get_child(obj, 0)

        topLevelRoles = self._topLevelRoles()
        ignorePanelParent = [Atspi.Role.MENU,
                             Atspi.Role.MENU_ITEM,
                             Atspi.Role.LIST_ITEM,
                             Atspi.Role.TREE_ITEM]

        if role == Atspi.Role.TABLE:
            layoutOnly = AXTable.is_layout_table(obj)
        elif role == Atspi.Role.TABLE_CELL and AXObject.get_child_count(obj):
            if parentRole == Atspi.Role.TREE_TABLE:
                layoutOnly = not AXObject.get_name(obj)
            elif AXUtilities.is_table_cell(firstChild):
                layoutOnly = True
            elif parentRole == Atspi.Role.TABLE:
                layoutOnly = self.isLayoutOnly(AXObject.get_parent(obj))
        elif role == Atspi.Role.SECTION:
            layoutOnly = not AXUtilities.is_block_quote(obj)
        elif role == Atspi.Role.BLOCK_QUOTE:
            layoutOnly = False
        elif role == Atspi.Role.FILLER:
            layoutOnly = True
        elif role == Atspi.Role.SCROLL_PANE:
            layoutOnly = True
        elif role == Atspi.Role.LAYERED_PANE:
            layoutOnly = self.isDesktop(self.topLevelObject(obj))
        elif role == Atspi.Role.AUTOCOMPLETE:
            layoutOnly = True
        elif role in [Atspi.Role.TEAROFF_MENU_ITEM, Atspi.Role.SEPARATOR]:
            layoutOnly = True
        elif role in [Atspi.Role.LIST_BOX, Atspi.Role.TREE_TABLE]:
            layoutOnly = False
        elif role in topLevelRoles:
            layoutOnly = False
        elif role == Atspi.Role.MENU:
            layoutOnly = parentRole == Atspi.Role.COMBO_BOX
        elif role == Atspi.Role.COMBO_BOX:
            layoutOnly = False
        elif role == Atspi.Role.LIST:
            layoutOnly = False
        elif role == Atspi.Role.FORM:
            layoutOnly = False
        elif role in [Atspi.Role.PUSH_BUTTON, Atspi.Role.TOGGLE_BUTTON]:
            layoutOnly = False
        elif role in [Atspi.Role.TEXT, Atspi.Role.PASSWORD_TEXT, Atspi.Role.ENTRY]:
            layoutOnly = False
        elif role == Atspi.Role.LIST_ITEM and parentRole == Atspi.Role.LIST_BOX:
            layoutOnly = False
        elif role in [Atspi.Role.REDUNDANT_OBJECT, Atspi.Role.UNKNOWN]:
            layoutOnly = True
        elif self.isTableRow(obj):
            layoutOnly = not (AXUtilities.is_focusable(obj) or AXUtilities.is_selectable(obj))
        elif role == Atspi.Role.PANEL and AXObject.get_role(firstChild) in ignorePanelParent:
            layoutOnly = True
        elif role == Atspi.Role.PANEL \
                and AXObject.has_same_non_empty_name(obj, AXObject.get_application(obj)):
            layoutOnly = True
        elif AXObject.get_child_count(obj) == 1 \
                and AXObject.has_same_non_empty_name(obj, firstChild):
            layoutOnly = True
        elif self.isHidden(obj):
            layoutOnly = True
        else:
            if not (AXObject.get_name(obj) or self.displayedLabel(obj) or AXText.get_all_text(obj)):
                layoutOnly = True

        if layoutOnly:
            tokens = ["SCRIPT UTILITIES:", obj, "is deemed to be layout only"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return layoutOnly

    def isLink(self, obj):
        """Returns True if obj is a link."""

        return AXUtilities.is_link(obj)

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""

        if not self.isTextArea(obj):
            return False

        if AXUtilities.is_read_only(obj):
            return True

        return AXUtilities.is_focusable(obj) and not AXUtilities.is_editable(obj)

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

    def _hasSamePath(self, obj1, obj2):
        path1 = AXObject.get_path(obj1)
        path2 = AXObject.get_path(obj2)
        if len(path1) != len(path2):
            return False

        if not (path1 and path2):
            return False

        # The first item in all paths, even valid ones, is -1.
        path1 = path1[1:]
        path2 = path2[1:]

        # If the object is being destroyed and the replacement is too, which
        # sadly can happen in at least Firefox, both will have an index of -1.
        # If the rest of the paths are valid and match, it's probably ok.
        if path1[-1] == -1 and path2[-1] == -1:
            path1 = path1[:-1]
            path2 = path2[:-1]

        # If both have invalid child indices, all bets are off.
        if path1.count(-1) and path2.count(-1):
            return False

        try:
            index = path1.index(-1)
        except ValueError:
            try:
                index = path2.index(-1)
            except ValueError:
                index = len(path2)

        return path1[0:index] == path2[0:index]

    def isTextArea(self, obj):
        """Returns True if obj is a GUI component that is for entering text.

        Arguments:
        - obj: an accessible
        """

        if self.isLink(obj):
            return False

        # TODO - JD: This might have been enough way back when, but additional
        # checks are needed now.
        return AXUtilities.is_text_input(obj) \
            or AXUtilities.is_text(obj) \
            or AXUtilities.is_paragraph(obj)

    def nestingLevel(self, obj):
        """Determines the nesting level of this object.

        Arguments:
        -obj: the Accessible object
        """

        if obj is None:
            return 0
        def pred(x):
            if AXUtilities.is_block_quote(obj):
                return AXUtilities.is_block_quote(x)
            if AXUtilities.is_list_item(obj):
                return AXUtilities.is_list(AXObject.get_parent(x))
            return AXUtilities.have_same_role(obj, x)

        ancestors = []
        ancestor = AXObject.find_ancestor(obj, pred)
        while ancestor:
            ancestors.append(ancestor)
            ancestor = AXObject.find_ancestor(ancestor, pred)

        return len(ancestors)

    def nodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not self.isTreeDescendant(obj):
            return -1

        nodes = []
        node = obj
        done = False
        while not done:
            targets = AXUtilities.get_is_node_child_of(node)
            node = None
            if targets:
                node = targets[0]

            # We want to avoid situations where something gives us an
            # infinite cycle of nodes.  Bon Echo has been seen to do
            # this (see bug 351847).
            if nodes.count(node):
                tokens = ["SCRIPT UTILITIES:", node, "is already in the list of nodes for", obj]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                done = True
            if len(nodes) > 100:
                tokens = ["SCRIPT UTILITIES: More than 100 nodes found for", obj]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                done = True
            elif node:
                nodes.append(node)
            else:
                done = True

        return len(nodes) - 1

    def isOnScreen(self, obj, boundingbox=None):
        if AXObject.is_dead(obj):
            return False

        if self.isHidden(obj):
            return False

        if not (AXUtilities.is_showing(obj) and AXUtilities.is_visible(obj)):
            tokens = ["SCRIPT UTILITIES:", obj, "is not showing and visible"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

            if AXUtilities.is_filler(obj):
                AXObject.clear_cache(obj, False, "Suspecting filler might have wrong state")
                if AXUtilities.is_showing(obj) and AXUtilities.is_visible(obj):
                    tokens = ["WARNING: Now", obj, "is showing and visible"]
                    debug.printTokens(debug.LEVEL_INFO, tokens, True)
                    return True

            return False

        if AXComponent.has_no_size_or_invalid_rect(obj):
            tokens = ["SCRIPT UTILITIES: Rect of", obj, "is unhelpful. Treating as onscreen"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXComponent.object_is_off_screen(obj):
            return False

        if boundingbox is None:
            return True

        if not AXComponent.object_intersects_rect(obj, boundingbox):
            tokens = ["SCRIPT UTILITIES:", obj, "not in", boundingbox]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        return True

    def selectedMenuBarMenu(self, menubar):
        if not AXUtilities.is_menu_bar(menubar):
            return None

        if AXObject.supports_selection(menubar):
            selected = self.selectedChildren(menubar)
            if selected:
                return selected[0]
            return None

        for menu in AXObject.iter_children(menubar):
            # TODO - JD: Can we remove this?
            AXObject.clear_cache(menu, False, "Ensuring we have the correct state.")
            if AXUtilities.is_expanded(menu) or AXUtilities.is_selected(menu):
                return menu

        return None

    def isInOpenMenuBarMenu(self, obj):
        if obj is None:
            return False

        menubar = AXObject.find_ancestor(obj, AXUtilities.is_menu_bar)
        if menubar is None:
            return False

        selectedMenu = self._selectedMenuBarMenu.get(hash(menubar))
        if selectedMenu is None:
            selectedMenu = self.selectedMenuBarMenu(menubar)

        if selectedMenu is None:
            return False

        def inSelectedMenu(x):
            return x == selectedMenu

        if inSelectedMenu(obj):
            return True

        return AXObject.find_ancestor(obj, inSelectedMenu) is not None

    def isStaticTextLeaf(self, obj):
        return False

    def isListItemMarker(self, obj):
        return False

    def hasPresentableText(self, obj):
        if self.isStaticTextLeaf(obj):
            return False
        return AXText.has_presentable_text(obj)

    def getOnScreenObjects(self, root, extents=None):
        if not self.isOnScreen(root, extents):
            return []

        if AXObject.get_role(root) == Atspi.Role.INVALID:
            return []

        if AXUtilities.is_button(root) or AXUtilities.is_combo_box(root):
            return [root]

        if AXUtilities.is_menu_bar(root):
            self._selectedMenuBarMenu[hash(root)] = self.selectedMenuBarMenu(root)

        if AXUtilities.is_menu_bar(AXObject.get_parent(root)) \
           and not self.isInOpenMenuBarMenu(root):
            return [root]

        if AXUtilities.is_filler(root) and not AXObject.get_child_count(root):
            AXObject.clear_cache(root, True, "Root is empty filler.")
            count = AXObject.get_child_count(root)
            tokens = ["SCRIPT UTILITIES:", root, f"now reports {count} children"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            if not count:
                tokens = ["WARNING: unexpectedly empty filler", root]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if extents is None:
            extents = AXComponent.get_rect(root)

        if AXObject.supports_table(root) and AXObject.supports_selection(root):
            visibleCells = self.getVisibleTableCells(root)
            if visibleCells:
                return visibleCells

        objects = []
        hasNameOrDesc = AXObject.get_name(root) or AXObject.get_description(root)
        if hasNameOrDesc and (AXUtilities.is_page_tab(root) or AXUtilities.is_image(root)):
            objects.append(root)
        elif self.hasPresentableText(root):
            objects.append(root)

        def pred(x):
            return x is not None and not self.isStaticTextLeaf(x)

        for child in AXObject.iter_children(root, pred):
            objects.extend(self.getOnScreenObjects(child, extents))

        if AXUtilities.is_menu_bar(root):
            self._selectedMenuBarMenu[hash(root)] = None

        if objects:
            return objects

        if AXUtilities.is_label(root) and not hasNameOrDesc and AXText.is_whitespace_or_empty(root):
            return []

        containers = [Atspi.Role.CANVAS,
                      Atspi.Role.FILLER,
                      Atspi.Role.IMAGE,
                      Atspi.Role.LINK,
                      Atspi.Role.LIST_BOX,
                      Atspi.Role.PANEL,
                      Atspi.Role.SECTION,
                      Atspi.Role.SCROLL_PANE,
                      Atspi.Role.VIEWPORT]
        if AXObject.get_role(root) in containers and not hasNameOrDesc:
            return []

        return [root]

    @staticmethod
    def isTableRow(obj):
        """Determines if obj is a table row -- real or functionally."""

        childCount = AXObject.get_child_count(obj)
        if not childCount:
            return False

        if AXObject.get_parent(obj) is None:
            return False

        if AXUtilities.is_table_row(obj):
            return True

        if AXUtilities.is_table_cell_or_header(obj):
            return False

        if not AXUtilities.is_table(AXObject.get_parent(obj)):
            return False

        cells = [x for x in AXObject.iter_children(obj, AXUtilities.is_table_cell_or_header)]
        if len(cells) == childCount:
            return True

        return False

    def realActiveAncestor(self, obj):
        if AXUtilities.is_focused(obj):
            return obj

        def pred(x):
            return AXUtilities.is_table_cell_or_header(x) or AXUtilities.is_list_item(x)

        ancestor = AXObject.find_ancestor(obj, pred)
        if ancestor is not None \
           and not self._script.utilities.isLayoutOnly(AXObject.get_parent(ancestor)):
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
            return x and not self.isStaticTextLeaf(x) \
                and (AXObject.get_name(x) or AXText.get_all_text(x))

        child = AXObject.find_descendant(obj, pred)
        if child is not None:
            return child

        return obj

    def infoBar(self, root):
        return None

    def _topLevelRoles(self):
        roles = [Atspi.Role.DIALOG,
                 Atspi.Role.FILE_CHOOSER,
                 Atspi.Role.FRAME,
                 Atspi.Role.WINDOW]
        if self._treatAlertsAsDialogs():
            roles.append(Atspi.Role.ALERT)
        return roles

    def _locusOfFocusIsTopLevelObject(self):
        focus = focus_manager.get_manager().get_locus_of_focus()
        if not focus:
            return False

        rv = focus == self.topLevelObject(focus)
        tokens = ["SCRIPT UTILITIES:", focus, "is top-level object:", rv]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _findWindowWithDescendant(self, child):
        """Searches each frame/window/dialog of an application to find the one
        which contains child. This is extremely non-performant and should only
        be used to work around broken accessibility trees where topLevelObject
        fails."""

        app = AXObject.get_application(child)
        if app is None:
            return None

        for i in range(AXObject.get_child_count(app)):
            window = AXObject.get_child(app, i)
            if AXObject.find_descendant(window, lambda x: x == child) is not None:
                tokens = ["SCRIPT UTILITIES:", window, "contains", child]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return window

            tokens = ["SCRIPT UTILITIES:", window, "does not contain", child]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

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

        if self._isTopLevelObject(obj):
            rv = obj
        else:
            rv = AXObject.find_ancestor(obj, self._isTopLevelObject)

        tokens = ["SCRIPT UTILITIES:", rv, "is top-level object for:", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if rv is None and useFallbackSearch:
            msg = "SCRIPT UTILITIES: Attempting to find top-level object via fallback search"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
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

        if self._script.spellcheck and self._script.spellcheck.isCheckWindow(root):
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

    def _treatAlertsAsDialogs(self):
        return True

    def unfocusedAlertAndDialogCount(self, obj):
        """If the current application has one or more alert or dialog
        windows and the currently focused window is not an alert or a dialog,
        return a count of the number of alert and dialog windows, otherwise
        return a count of zero.

        Arguments:
        - obj: the Accessible object

        Returns the alert and dialog count.
        """

        roles = [Atspi.Role.DIALOG]
        if self._treatAlertsAsDialogs():
            roles.append(Atspi.Role.ALERT)

        def isDialog(x):
            return AXObject.get_role(x) in roles or self.isFunctionalDialog(x)

        dialogs = [x for x in AXObject.iter_children(AXObject.get_application(obj), isDialog)]
        dialogs.extend([x for x in AXObject.iter_children(self.topLevelObject(obj), isDialog)])

        def isPresentable(x):
            return AXUtilities.is_showing(x) and AXUtilities.is_visible(x) \
                and (AXObject.get_name(x) or AXObject.get_child_count(x))

        def cannotBeActiveWindow(x):
            return not focus_manager.get_manager().can_be_active_window(x)

        presentable = list(filter(isPresentable, set(dialogs)))
        unfocused = list(filter(cannotBeActiveWindow, presentable))
        return len(unfocused)

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################

    def findPreviousObject(self, obj):
        """Finds the object before this one."""

        if not AXObject.is_valid(obj):
            return None

        targets = AXUtilities.get_flows_from(obj)
        if targets:
            return targets[0]

        return AXObject.get_previous_object(obj)

    def findNextObject(self, obj):
        """Finds the object after this one."""

        if not AXObject.is_valid(obj):
            return None

        targets = AXUtilities.get_flows_to(obj)
        if targets:
            return targets[0]

        return AXObject.get_next_object(obj)

    def allSelectedText(self, obj):
        """Get all the text applicable text selections for the given object.
        including any previous or next text objects that also have
        selected text and add in their text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        # TODO - JD: Move to AXText if possible
        textContents, startOffset, endOffset = AXText.get_selected_text(obj)
        if textContents and self._script.point_of_reference.get('entireDocumentSelected'):
            return textContents, startOffset, endOffset

        if self.isSpreadSheetCell(obj):
            return textContents, startOffset, endOffset

        prevObj = self.findPreviousObject(obj)
        while prevObj:
            selection = AXText.get_selected_text(prevObj)[0]
            if not selection:
                 break
            textContents = f"{selection} {textContents}"
            prevObj = self.findPreviousObject(prevObj)

        nextObj = self.findNextObject(obj)
        while nextObj:
            selection = AXText.get_selected_text(nextObj)[0]
            if not selection:
                break
            textContents = f"{textContents} {selection}"
            nextObj = self.findNextObject(nextObj)

        return textContents, startOffset, endOffset

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
            debug.printTokens(debug.LEVEL_INFO, tokens, True, True)
            startOffset = 0
        if endOffset is None:
            tokens = ["SCRIPT UTILITIES: expandEOCs called with end offset of None on", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True, True)
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
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if self.EMBEDDED_OBJECT_CHARACTER in result:
            msg = "SCRIPT UTILITIES: Unable to expand EOCs"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return ""

        return result

    def getError(self, obj):
        return AXUtilities.is_invalid_entry(obj)

    def getErrorMessage(self, obj):
        return ""

    def isErrorMessage(self, obj):
        return bool(AXUtilities.get_is_error_for(obj))

    def deletedText(self, event):
        return event.any_data

    def insertedText(self, event):
        if event.any_data:
            return event.any_data

        msg = "SCRIPT UTILITIES: Broken text insertion event"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if AXUtilities.is_password_text(event.source):
            string = AXText.get_all_text(event.source)
            if string:
                tokens = ["HACK: Returning last char in '", string, "'"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return string[-1]

        msg = "FAIL: Unable to correct broken text insertion event"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return ""

    def getCaretContext(self):
        obj = focus_manager.get_manager().get_locus_of_focus()
        offset = AXText.get_caret_offset(obj)
        return obj, offset

    def getFirstCaretPosition(self, obj):
        # TODO - JD: Do we still need this function? We need to audit callers,
        # mainly in structural navigation.
        return obj, 0

    def setCaretPosition(self, obj, offset, documentFrame=None):
        focus_manager.get_manager().set_locus_of_focus(None, obj, False)
        self.setCaretOffset(obj, offset)

    def setCaretOffset(self, obj, offset):
        # TODO - JD. Remove this function if the web override can be adjusted
        AXText.set_caret_offset(obj, offset)

    def getAppNameForAttribute(self, attribName):
        """Converts the given Atk attribute name into the application's
        equivalent. This is necessary because an application or toolkit
        (e.g. Gecko) might invent entirely new names for the same text
        attributes.

        Arguments:
        - attribName: The name of the text attribute

        Returns the application's equivalent name if found or attribName
        otherwise.
        """

        for key, value in self._script.attributeNamesDict.items():
            if value == attribName:
                return key

        return attribName

    def getAtkNameForAttribute(self, attribName):
        """Converts the given attribute name into the Atk equivalent. This
        is necessary because an application or toolkit (e.g. Gecko) might
        invent entirely new names for the same attributes.

        Arguments:
        - attribName: The name of the text attribute

        Returns the Atk equivalent name if found or attribName otherwise.
        """

        return self._script.attributeNamesDict.get(attribName, attribName)

    def textAttributes(self, acc, offset=None, get_defaults=False):
        # TODO - JD: Replace all calls to this function with the one below
        return AXText.get_text_attributes_at_offset(acc, offset)

    def localizeTextAttribute(self, key, value):
        if key == "weight" and (value == "bold" or int(value) > 400):
            return messages.BOLD

        if key.endswith("spelling") or value == "spelling":
            return messages.MISSPELLED

        localizedKey = text_attribute_names.getTextAttributeName(key, self._script)

        if key == "family-name":
            localizedValue = value.split(",")[0].strip().strip('"')
        elif value and value.endswith("px"):
            value = value.split("px")[0]
            if locale.localeconv()["decimal_point"] in value:
                localizedValue = messages.pixelCount(float(value))
            else:
                localizedValue = messages.pixelCount(int(value))
        elif key.endswith("color"):
            r, g, b = self.rgbFromString(value)
            if settings.useColorNames:
                localizedValue = colornames.rgbToName(r, g, b)
            else:
                localizedValue = "%i %i %i" % (r, g, b)
        else:
            localizedValue = text_attribute_names.getTextAttributeName(value, self._script)

        return f"{localizedKey}: {localizedValue}"

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

    def willEchoCharacter(self, event):
        """Given a keyboard event containing an alphanumeric key,
        determine if the script is likely to echo it as a character.
        """

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not focus or not settings.enableEchoByCharacter:
            return False

        if len(event.event_string) != 1 \
           or event.modifiers & keybindings.ORCA_CTRL_MODIFIER_MASK:
            return False

        if AXUtilities.is_password_text(focus):
            return False

        if AXUtilities.is_editable(focus):
            return True

        return False

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################

    def shouldVerbalizeAllPunctuation(self, obj):
        if not (AXUtilities.is_code(obj) or self.isCodeDescendant(obj)):
            return False

        # If the user has set their punctuation level to All, then the synthesizer will
        # do the work for us. If the user has set their punctuation level to None, then
        # they really don't want punctuation and we mustn't override that.
        style = settings_manager.get_manager().get_setting("verbalizePunctuationStyle")
        if style in [settings.PUNCTUATION_STYLE_ALL, settings.PUNCTUATION_STYLE_NONE]:
            return False

        return True

    def verbalizeAllPunctuation(self, string):
        result = string
        for symbol in set(re.findall(self.PUNCTUATION, result)):
            charName = f" {symbol} "
            result = re.sub(r"\%s" % symbol, charName, result)

        return result

    @staticmethod
    def _convertWordToDigits(word):
        if not word.isnumeric():
            return word

        return ' '.join(list(word))

    def adjustForPronunciation(self, line):
        """Adjust the line to replace words in the pronunciation dictionary,
        with what those words actually sound like.

        Arguments:
        - line: the string to adjust for words in the pronunciation dictionary.

        Returns: a new line adjusted for words found in the pronunciation
        dictionary.
        """

        # TODO - JD: We had been making this change in response to bgo#591734.
        # It may or may not still be needed or wanted to replace no-break-space
        # characters with plain spaces. Surely modern synthesizers can cope with
        # both types of spaces.
        line = line.replace("\u00a0", " ")

        if self.speakMathSymbolNames():
            line = mathsymbols.adjustForSpeech(line)

        if settings.speakNumbersAsDigits:
            words = self.WORDS_RE.split(line)
            line = ''.join(map(self._convertWordToDigits, words))

        if len(line) == 1 and not self._script.inSayAll() and self.isInMath():
            charname = mathsymbols.getCharacterName(line)
            if charname != line:
                return charname

        if not settings.usePronunciationDictionary:
            return line

        newLine = ""
        words = self.WORDS_RE.split(line)
        newLine = ''.join(map(pronunciation_dict.getPronunciation, words))
        return newLine

    def indentationDescription(self, line):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText') \
           or not settings_manager.get_manager().get_setting('enableSpeechIndentation'):
            return ""

        line = line.replace("\u00a0", " ")
        end = re.search("[^ \t]", line)
        if end:
            line = line[:end.start()]

        result = ""
        spaces = [m.span() for m in re.finditer(" +", line)]
        tabs = [m.span() for m in re.finditer("\t+", line)]
        spans = sorted(spaces + tabs)
        for (start, end) in spans:
            if (start, end) in spaces:
                result += f"{messages.spacesCount(end - start)} "
            else:
                result += f"{messages.tabsCount(end - start)} "

        return result

    @staticmethod
    def appendString(text, newText, delimiter=" "):
        """Appends the newText to the given text with the delimiter in between
        and returns the new string.  Edge cases, such as no initial text or
        no newText, are handled gracefully."""

        if not newText:
            return text
        if not text:
            return newText

        return text + delimiter + newText

    def isAutoTextEvent(self, event):
        """Returns True if event is associated with text being autocompleted
        or autoinserted or autocorrected or autosomethingelsed.

        Arguments:
        - event: the accessible event being examined
        """

        if event.type.startswith("object:text-changed:insert"):
            if not event.any_data or not event.source:
                return False

            if not AXUtilities.is_editable(event.source):
                return False
            if not AXUtilities.is_showing(event.source):
                return False
            if AXUtilities.is_focusable(event.source):
                AXObject.clear_cache(event.source, False, "Ensuring we have the correct state.")
                if not AXUtilities.is_focused(event.source):
                    return False

            manager = input_event_manager.get_manager()
            if manager.last_event_was_tab() and event.any_data != "\t":
                return True
            if manager.last_event_was_return() and event.any_data != "\n":
                return True
            if manager.last_event_was_up_or_down() or manager.last_event_was_page_up_or_page_down():
                return self.isEditableDescendantOfComboBox(event.source)
            if not input_event_manager.get_manager().last_event_was_printable_key():
                return False

            string = AXText.get_all_text(event.source)
            if string.endswith(event.any_data):
                selection, start, end = AXText.get_selected_text(event.source)
                if selection == event.any_data:
                    return True

        return False

    def isSentenceDelimiter(self, currentChar, previousChar):
        """Returns True if we are positioned at the end of a sentence.
        This is determined by checking if the current character is a
        white space character and the previous character is one of the
        normal end-of-sentence punctuation characters.

        Arguments:
        - currentChar:  the current character
        - previousChar: the previous character

        Returns True if the given character is a sentence delimiter.
        """

        if currentChar == '\r' or currentChar == '\n':
            return True

        return currentChar in self._script.whitespace \
               and previousChar in '!.?:;'

    def isWordDelimiter(self, character):
        """Returns True if the given character is a word delimiter.

        Arguments:
        - character: the character in question

        Returns True if the given character is a word delimiter.
        """

        return character in self._script.whitespace \
               or character in r'!*+,-./:;<=>?@[\]^_{|}' \
               or character == self._script.NO_BREAK_SPACE_CHARACTER

    @staticmethod
    def labelFromKeySequence(sequence):
        """Turns a key sequence into a user-presentable label."""

        try:
            from gi.repository import Gtk
            key, mods = Gtk.accelerator_parse(sequence)
            newSequence = Gtk.accelerator_get_label(key, mods)
            if newSequence and \
               (not newSequence.endswith('+') or newSequence.endswith('++')):
                sequence = newSequence
        except Exception:
            sequence = sequence.replace("<", "")
            sequence = sequence.replace(">", " ").strip()

        return keynames.localizeKeySequence(sequence)

    def mnemonicShortcutAccelerator(self, obj):
        """Gets the mnemonic, accelerator string and possibly shortcut
        for the given object.  These are based upon the first accessible
        action for the object.

        Arguments:
        - obj: the Accessible object

        Returns: list containing strings: [mnemonic, shortcut, accelerator]
        """

        keybinding = AXObject.get_action_key_binding(obj, 0)
        if not keybinding:
            return ["", "", ""]

        # Action is a string in the format, where the mnemonic and/or
        # accelerator can be missing.
        #
        # <mnemonic>;<full-path>;<accelerator>
        #
        # The keybindings in <full-path> should be separated by ":"
        #

        bindingStrings = keybinding.split(';')
        if len(bindingStrings) == 3:
            mnemonic       = bindingStrings[0]
            fullShortcut   = bindingStrings[1]
            accelerator    = bindingStrings[2]
        elif len(bindingStrings) > 0:
            mnemonic       = ""
            fullShortcut   = bindingStrings[0]
            try:
                accelerator = bindingStrings[1]
            except Exception:
                accelerator = ""
        else:
            mnemonic       = ""
            fullShortcut   = ""
            accelerator    = ""

        fullShortcut = fullShortcut.replace(":", " ").strip()
        fullShortcut = self.labelFromKeySequence(fullShortcut)
        mnemonic = self.labelFromKeySequence(mnemonic)
        accelerator = self.labelFromKeySequence(accelerator)

        return [mnemonic, fullShortcut, accelerator]

    @staticmethod
    def stringToKeysAndDict(string):
        """Converts a string made up of a series of <key>:<value>; pairs
        into a dictionary of keys and values. Text before the colon is the
        key and text afterwards is the value. The final semi-colon, if
        found, is ignored.

        Arguments:
        - string: the string of tokens containing <key>:<value>; pairs.

        Returns a list containing two items:
        A list of the keys in the order they were extracted from the
        string and a dictionary of key/value items.
        """

        try:
            items = [s.strip() for s in string.split(";")]
            items = [item for item in items if len(item.split(':')) == 2]
            keys = [item.split(':')[0].strip() for item in items]
            dictionary = dict([item.split(':') for item in items])
        except Exception:
            return [], {}

        return [keys, dictionary]

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

        if self.isTextArea(obj):
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

    def isButtonWithPopup(self, obj):
        return AXUtilities.is_button(obj) and AXUtilities.has_popup(obj)

    def isPopupMenuForCurrentItem(self, obj):
        focus = focus_manager.get_manager().get_locus_of_focus()
        if obj == focus:
            return False

        if not AXUtilities.is_menu(obj):
            return False

        name = AXObject.get_name(obj)
        if not name:
            return False

        return name == AXObject.get_name(focus)

    def isMenuWithNoSelectedChild(self, obj):
        return AXUtilities.is_menu(obj) and not self.selectedChildCount(obj)

    def inMenu(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if obj is None:
            return False

        if AXUtilities.is_menu_item_of_any_kind(obj) or AXUtilities.is_menu(obj):
            return True

        if AXUtilities.is_panel(obj) or AXUtilities.is_separator(obj):
            return AXObject.find_ancestor(obj, AXUtilities.is_menu) is not None

        return False

    def inContextMenu(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not self.inMenu(obj):
            return False

        return AXObject.find_ancestor(obj, self.isContextMenu) is not None

    def _contextMenuParentRoles(self):
        return Atspi.Role.FRAME, Atspi.Role.WINDOW

    def isContextMenu(self, obj):
        if not AXUtilities.is_menu(obj):
            return False

        return AXObject.get_role(AXObject.get_parent(obj)) in self._contextMenuParentRoles()

    def isTopLevelMenu(self, obj):
        if not AXUtilities.is_menu(obj):
            return False
        return AXObject.get_parent(obj) == self.topLevelObject(obj)

    def isSingleLineAutocompleteEntry(self, obj):
        if not AXUtilities.is_entry(obj):
            return False
        if not AXUtilities.supports_autocompletion(obj):
            return False
        return AXUtilities.is_single_line(obj)

    def isEntryCompletionPopupItem(self, obj):
        return False

    def getEntryForEditableComboBox(self, obj):
        if not AXUtilities.is_combo_box(obj):
            return None

        children = [x for x in AXObject.iter_children(obj, self.isEditableTextArea)]
        if len(children) == 1:
            return children[0]

        return None

    def isEditableComboBox(self, obj):
        return self.getEntryForEditableComboBox(obj) is not None

    def isEditableDescendantOfComboBox(self, obj):
        if not AXUtilities.is_editable(obj):
            return False

        return AXObject.find_ancestor(obj, AXUtilities.is_combo_box) is not None

    def getComboBoxValue(self, obj):
        if not AXObject.get_child_count(obj):
            return AXObject.get_name(obj) or AXText.get_all_text(obj)

        entry = self.getEntryForEditableComboBox(obj)
        if entry:
            return AXText.get_all_text(entry)

        selected = self._script.utilities.selectedChildren(obj)
        selected = selected or self._script.utilities.selectedChildren(AXObject.get_child(obj, 0))
        if len(selected) == 1:
            return AXObject.get_name(selected[0]) or AXText.get_all_text(selected[0])

        return AXObject.get_name(obj) or AXText.get_all_text(obj)

    def isNonModalPopOver(self, obj):
        if not AXUtilities.get_is_popup_for(obj):
            return False
        return not AXUtilities.is_modal(obj)

    def isUselessPanel(self, obj):
        return False

    def rgbFromString(self, attributeValue):
        regex = re.compile(r"rgb|[^\w,]", re.IGNORECASE)
        string = re.sub(regex, "", attributeValue)
        red, green, blue = string.split(",")

        return int(red), int(green), int(blue)

    def isClickableElement(self, obj):
        return False

    def hasLongDesc(self, obj):
        return False

    def hasVisibleCaption(self, obj):
        return False

    def popupType(self, obj):
        return ''

    def headingLevel(self, obj):
        if not AXUtilities.is_heading(obj):
            return 0

        use_cache = not AXUtilities.is_editable(obj)
        attrs = AXObject.get_attributes_dict(obj, use_cache)

        try:
            value = int(attrs.get('level', '0'))
        except ValueError:
            tokens = ["SCRIPT UTILITIES: Exception getting value for", obj, "(", attrs, ")"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return 0

        return value

    def hasMeaningfulToggleAction(self, obj):
        return AXObject.has_action(obj, "toggle") \
            or AXObject.has_action(obj, object_properties.ACTION_TOGGLE)

    def containingTableHeader(self, obj):
        if AXUtilities.is_table_header(obj):
            return obj

        return AXObject.find_ancestor(obj, AXUtilities.is_table_header)

    def setSizeUnknown(self, obj):
        return AXUtilities.is_indeterminate(obj)

    def rowOrColumnCountUnknown(self, obj):
        return AXUtilities.is_indeterminate(obj)

    def treatAsEntry(self, obj):
        return False

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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
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
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return word, start, end

    def textAtPoint(self, obj, x, y, boundary=None):
        # TODO - JD: Audit callers so we don't have to use boundaries.
        # Also, can the logic be entirely moved to AXText?
        if boundary in (None, Atspi.TextBoundaryType.LINE_START):
            string, start, end = AXText.get_line_at_point(obj, x, y)
        elif boundary == Atspi.TextBoundaryType.SENTENCE_START:
            string, start, end = AXText.get_sentence_at_point(obj, x, y)
        elif boundary == Atspi.TextBoundaryType.WORD_START:
            string, start, end = AXText.get_word_at_point(obj, x, y)
        elif boundary == Atspi.TextBoundaryType.CHAR:
            string, start, end = AXText.get_character_at_point(obj, x, y)
        else:
            return "", 0, 0

        if not string:
            return "", start, end

        if boundary == Atspi.TextBoundaryType.WORD_START and not string.strip():
            return "", 0, 0

        extents = AXText.get_range_rect(obj, start, end)
        rect = Atspi.Rect()
        rect.x = x
        rect.y = y
        rect.width = rect.height = 0
        if not AXComponent.get_rect_intersection(extents, rect) and string != "\n":
            return "", 0, 0

        if not string.endswith("\n") or string == "\n":
            return string, start, end

        if boundary == Atspi.TextBoundaryType.CHAR:
            return string, start, end

        char = self.textAtPoint(obj, x, y, Atspi.TextBoundaryType.CHAR)
        if char[0] == "\n" and char[2] - char[1] == 1:
            return char

        return string, start, end

    def visibleRows(self, obj, table_rect):
        nRows = AXTable.get_row_count(obj)

        tokens = ["SCRIPT UTILITIES: ", obj, f"has {nRows} rows"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        cell = AXComponent.get_descendant_at_point(obj, table_rect.x, table_rect.y + 1)
        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        startIndex = max(0, row)
        tokens = ["SCRIPT UTILITIES: First cell:", cell, f"(row: {row}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # Just in case the row above is a static header row in a scrollable table.
        cell_rect = AXComponent.get_rect(cell)
        cell = AXComponent.get_descendant_at_point(
            obj, table_rect.x, table_rect.y + cell_rect.height + 1)
        row, AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        nextIndex = max(startIndex, row)
        tokens = ["SCRIPT UTILITIES: Next cell:", cell, f"(row: {row})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        cell = AXComponent.get_descendant_at_point(
            obj, table_rect.x, table_rect.y + table_rect.height - 1)
        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        tokens = ["SCRIPT UTILITIES: Last cell:", cell, f"(row: {row})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if row == -1:
            row = nRows
        endIndex = row

        rows = list(range(nextIndex, endIndex))
        if startIndex not in rows:
            rows.insert(0, startIndex)

        return rows

    def getVisibleTableCells(self, obj):
        if not AXObject.supports_table(obj):
            return []

        rows = self.visibleRows(obj, AXComponent.get_rect(obj))
        if not rows:
            return []

        colStartIndex, colEndIndex = self._getTableRowRange(obj)
        if colStartIndex == colEndIndex:
            return []

        cells = []
        for col in range(colStartIndex, colEndIndex):
            headers = []
            for row in rows:
                cell = AXTable.get_cell_at(obj, row, col)
                if cell is None:
                    continue
                if not headers:
                    # TODO - JD: This is needed for flat review to include the column headers
                    # above the message list in Thunderbird v110. It does not appear necessary
                    # for more recent versions of Thunderbird (e.g. v115). Looks like a potential
                    # case of broken table support in (at least) Thunderbird 110. Who else might
                    # have this same bug?
                    headers = AXTable.get_column_headers(cell)
                    if headers and self.isOnScreen(headers[0]):
                        cells.append(headers[0])
                if self.isOnScreen(cell):
                    cells.append(cell)

        return cells

    def _getTableRowRange(self, obj):
        table = AXTable.get_table(obj)
        if table is None:
            return -1, -1

        columnCount = AXTable.get_column_count(table, False)
        startIndex, endIndex = 0, columnCount
        if not self.isSpreadSheetCell(obj):
            return startIndex, endIndex

        rect = AXComponent.get_rect(table)
        cell = AXComponent.get_descendant_at_point(table, rect.x + 1, rect.y)
        if cell:
            column = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
            startIndex = column

        cell = AXComponent.get_descendant_at_point(table, rect.x + rect.width - 1, rect.y)
        if cell:
            column = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
            endIndex = column + 1

        return startIndex, endIndex

    def getShowingCellsInSameRow(self, obj, forceFullRow=False):
        row = AXTable.get_cell_coordinates(obj, prefer_attribute=False)[0]
        if row == -1:
            return []

        table = AXTable.get_table(obj)
        if forceFullRow:
            startIndex, endIndex = 0, AXTable.get_column_count(table)
        else:
            startIndex, endIndex = self._getTableRowRange(obj)
        if startIndex == endIndex:
            return []

        cells = []
        for i in range(startIndex, endIndex):
            cell = AXTable.get_cell_at(table, row, i)
            if AXUtilities.is_showing(cell):
                cells.append(cell)

        return cells

    def findReplicant(self, root, obj):
        tokens = ["SCRIPT UTILITIES: Searching for replicant for", obj, "in", root]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not (root and obj):
            return None

        if AXUtilities.is_table(root) or AXUtilities.is_embedded(root):
            return None

        def isSame(x):
            if x == obj:
                return True
            if x is None:
                return False
            if not AXUtilities.have_same_role(obj, x):
                return False
            if self._hasSamePath(obj, x):
                return True
            # Objects which claim to be different and which are in different
            # locations are almost certainly not recreated objects.
            if not AXComponent.objects_have_same_rect(obj, x):
                return False
            return not AXComponent.has_no_size(x)

        if isSame(root):
            replicant = root
        else:
            replicant = AXObject.find_descendant(root, isSame)

        tokens = ["HACK: Returning", replicant, "as replicant for invalid object", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return replicant

    def valuesForTerm(self, obj):
        if not AXUtilities.is_description_term(obj):
            return []

        values = []
        obj = AXObject.get_next_sibling(obj)
        while obj and AXUtilities.is_description_value(obj):
            values.append(obj)
            obj = AXObject.get_next_sibling(obj)

        return values

    def getRoleDescription(self, obj, isBraille=False):
        return ""

    def getCachedTextSelection(self, obj):
        textSelections = self._script.point_of_reference.get('textSelections', {})
        start, end, string = textSelections.get(hash(obj), (0, 0, ''))
        tokens = ["SCRIPT UTILITIES: Cached selection for", obj, f"is '{string}' ({start}, {end})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return start, end, string

    def updateCachedTextSelection(self, obj):
        if self._script.point_of_reference.get('entireDocumentSelected'):
            selectedText = self.allSelectedText(obj)[0]
            if not selectedText:
                self._script.point_of_reference['entireDocumentSelected'] = False
                self._script.point_of_reference['textSelections'] = {}

        textSelections = self._script.point_of_reference.get('textSelections', {})

        # Because some apps and toolkits create, destroy, and duplicate objects
        # and events.
        if hash(obj) in textSelections:
            value = textSelections.pop(hash(obj))
            for x in [k for k in textSelections.keys() if textSelections.get(k) == value]:
                textSelections.pop(x)

        string, start, end = AXText.get_selected_text(obj)
        tokens = ["SCRIPT UTILITIES: New selection for", obj, f"is '{string}' ({start}, {end})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        textSelections[hash(obj)] = start, end, string
        self._script.point_of_reference['textSelections'] = textSelections

    @staticmethod
    def onClipboardContentsChanged(*args):
        script = script_manager.get_manager().get_active_script()
        if script is None:
            return

        if time.time() - Utilities._last_clipboard_update < 0.05:
            msg = "SCRIPT UTILITIES: Clipboard contents change believed to be duplicate"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        Utilities._last_clipboard_update = time.time()
        script.onClipboardContentsChanged(*args)

    def connectToClipboard(self):
        if self._clipboardHandlerId is not None:
            return

        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        self._clipboardHandlerId = clipboard.connect(
            'owner-change', self.onClipboardContentsChanged)

    def disconnectFromClipboard(self):
        if self._clipboardHandlerId is None:
            return

        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        clipboard.disconnect(self._clipboardHandlerId)

    def getClipboardContents(self):
        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        return clipboard.wait_for_text()

    def setClipboardText(self, text):
        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        clipboard.set_text(text, -1)

    def appendTextToClipboard(self, text):
        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        clipboard.request_text(self._appendTextToClipboardCallback, text)

    def _appendTextToClipboardCallback(self, clipboard, text, newText, separator="\n"):
        text = text.rstrip("\n")
        text = f"{text}{separator}{newText}"
        clipboard.set_text(text, -1)

    def isPresentableExpandedChangedEvent(self, event):
        if event.source == focus_manager.get_manager().get_locus_of_focus():
            return True

        if AXUtilities.is_table_row(event.source) or AXUtilities.is_list_box(event.source):
            return True

        if AXUtilities.is_combo_box(event.source) or AXUtilities.is_button(event.source):
            return AXUtilities.is_focused(event.source)

        return False

    def isPresentableTextChangedEventForLocusOfFocus(self, event):
        if not event.type.startswith("object:text-changed:") \
           and not event.type.startswith("object:text-attributes-changed"):
            return False

        if AXUtilities.is_menu_related(event.source) \
           or AXUtilities.is_slider(event.source) \
           or AXUtilities.is_spin_button(event.source) \
           or AXUtilities.is_label(event.source):
            msg = "SCRIPT UTILITIES: Event is not being presented due to role"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_focused(event.source):
            if self.isTypeahead(event.source):
                return True
            if AXUtilities.is_password_text(event.source):
                return True
            if focus_manager.get_manager().focus_is_dead():
                return True
        elif AXUtilities.is_table_cell(event.source) and not AXUtilities.is_selected(event.source):
            msg = "SCRIPT UTILITIES: Event is not being presented due to role and states"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if focus_manager.get_manager().get_locus_of_focus() in \
            [event.source, AXObject.get_parent(event.source)]:
            return True

        msg = "SCRIPT UTILITIES: Event is not being presented due to lack of cause"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return False

    def isBackSpaceCommandTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        if self.isHidden(event.source):
            return False

        return input_event_manager.get_manager().last_event_was_backspace()

    def isDeleteCommandTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        if event.type.endswith("system"):
            return False

        return input_event_manager.get_manager().last_event_was_delete()

    def isUndoCommandTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        if not input_event_manager.get_manager().last_event_was_undo():
            return False

        start, end, string = self.getCachedTextSelection(event.source)
        return not string

    def isSelectedTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        if input_event_manager.get_manager().last_event_was_paste():
            return False

        start, end, string = self.getCachedTextSelection(event.source)
        return string and string.strip() == event.any_data.strip()

    def isSelectedTextInsertionEvent(self, event):
        if not event.type.startswith("object:text-changed:insert"):
            return False

        self.updateCachedTextSelection(event.source)
        start, end, string = self.getCachedTextSelection(event.source)
        return string and string == event.any_data and start == event.detail1

    def isSelectedTextRestoredEvent(self, event):
        if not input_event_manager.get_manager().last_event_was_undo():
            return False

        if self.isSelectedTextInsertionEvent(event):
            return True

        return False

    def isMiddleMouseButtonTextInsertionEvent(self, event):
        if not event.type.startswith("object:text-changed:insert"):
            return False

        return input_event_manager.get_manager().last_event_was_middle_click()

    def isEchoableTextInsertionEvent(self, event):
        if not event.type.startswith("object:text-changed:insert"):
            return False

        if AXUtilities.is_focusable(event.source) \
           and not AXUtilities.is_focused(event.source) \
           and event.source != focus_manager.get_manager().get_locus_of_focus():
            msg = "SCRIPT UTILITIES: Not echoable text insertion event: " \
                 "focusable source is not focused"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_password_text(event.source):
            return settings_manager.get_manager().get_setting("enableKeyEcho")

        if len(event.any_data.strip()) == 1:
            return settings_manager.get_manager().get_setting("enableEchoByCharacter")

        return False

    def isEditableTextArea(self, obj):
        if not self.isTextArea(obj):
            return False
        return AXUtilities.is_editable(obj)

    def isClipboardTextChangedEvent(self, event):
        if not event.type.startswith("object:text-changed"):
            return False

        manager = input_event_manager.get_manager()
        if not manager.last_event_was_command() or manager.last_event_was_undo():
            return False

        if self.isBackSpaceCommandTextDeletionEvent(event):
            return False

        if "delete" in event.type and input_event_manager.get_manager().last_event_was_paste():
            return False

        if not self.isEditableTextArea(event.source):
            return False

        contents = self.getClipboardContents()
        if not contents:
            return False
        if event.any_data == contents:
            return True
        if bool(re.search(r"\w", event.any_data)) != bool(re.search(r"\w", contents)):
            return False

        # HACK: If the application treats each paragraph as a separate object,
        # we'll get individual events for each paragraph rather than a single
        # event whose any_data matches the clipboard contents.
        if "\n" in contents and event.any_data.rstrip() in contents:
            return True

        return False

    def objectContentsAreInClipboard(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not obj or AXObject.is_dead(obj):
            return False

        contents = self.getClipboardContents()
        if not contents:
            return False

        string, start, end = AXText.get_selected_text(obj)
        if string and string in contents:
            return True

        obj = self.realActiveDescendant(obj) or obj
        if AXObject.is_dead(obj):
            return False

        return obj and AXObject.get_name(obj) in contents

    def clearCachedCommandState(self):
        self._script.point_of_reference['undo'] = False
        self._script.point_of_reference['redo'] = False
        self._script.point_of_reference['paste'] = False

    def handleUndoTextEvent(self, event):
        if input_event_manager.get_manager().last_event_was_undo():
            if not self._script.point_of_reference.get('undo'):
                self._script.presentMessage(messages.UNDO)
                self._script.point_of_reference['undo'] = True
            self.updateCachedTextSelection(event.source)
            return True

        if input_event_manager.get_manager().last_event_was_redo():
            if not self._script.point_of_reference.get('redo'):
                self._script.presentMessage(messages.REDO)
                self._script.point_of_reference['redo'] = True
            self.updateCachedTextSelection(event.source)
            return True

        return False

    def handleUndoLocusOfFocusChange(self):
        if self._locusOfFocusIsTopLevelObject():
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
        if self._locusOfFocusIsTopLevelObject():
            return False

        if input_event_manager.get_manager().last_event_was_paste():
            if not self._script.point_of_reference.get('paste'):
                self._script.presentMessage(
                    messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF)
                self._script.point_of_reference['paste'] = True
            return True

        return False

    def eventIsCanvasNoise(self, event):
        return False

    def eventIsSpinnerNoise(self, event):
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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
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

        oldStart, oldEnd, oldString = self.getCachedTextSelection(obj)
        self.updateCachedTextSelection(obj)
        newStart, newEnd, newString = self.getCachedTextSelection(obj)

        if input_event_manager.get_manager().last_event_was_select_all() and newString:
            if not self._script.point_of_reference.get('entireDocumentSelected'):
                self._script.point_of_reference['entireDocumentSelected'] = True
                self._script.speakMessage(messages.DOCUMENT_SELECTED_ALL)
            return True

        # Even though we present a message, treat it as unhandled so the new location is
        # still presented.
        if not input_event_manager.get_manager().last_event_was_caret_selection() \
           and oldString and not newString:
            self._script.speakMessage(messages.SELECTION_REMOVED)
            return False

        changes = []
        oldChars = set(range(oldStart, oldEnd))
        newChars = set(range(newStart, newEnd))
        if not oldChars.union(newChars):
            return False

        if oldChars and newChars and not oldChars.intersection(newChars):
            # A simultaneous unselection and selection centered at one offset.
            changes.append([oldStart, oldEnd, messages.TEXT_UNSELECTED])
            changes.append([newStart, newEnd, messages.TEXT_SELECTED])
        else:
            change = sorted(oldChars.symmetric_difference(newChars))
            if not change:
                return False

            changeStart, changeEnd = change[0], change[-1] + 1
            if oldChars < newChars:
                changes.append([changeStart, changeEnd, messages.TEXT_SELECTED])
                if oldString.endswith(self.EMBEDDED_OBJECT_CHARACTER) and oldEnd == changeStart:
                    # There's a possibility that we have a link spanning multiple lines. If so,
                    # we want to present the continuation that just became selected.
                    child = AXHypertext.get_child_at_offset(obj, oldEnd - 1)
                    self.handleTextSelectionChange(child, False)
            else:
                changes.append([changeStart, changeEnd, messages.TEXT_UNSELECTED])
                if newString.endswith(self.EMBEDDED_OBJECT_CHARACTER):
                    # There's a possibility that we have a link spanning multiple lines. If so,
                    # we want to present the continuation that just became unselected.
                    child = AXHypertext.get_child_at_offset(obj, newEnd - 1)
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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if event is not None and event.type.startswith("object:active-descendant-changed"):
            return self._script.stopSpeechOnActiveDescendantChanged(event)

        if AXUtilities.is_table_cell(old_focus) and AXUtilities.is_text(new_focus) \
           and AXUtilities.is_editable(new_focus):
            msg += "suspected editable cell"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not AXUtilities.is_menu_related(new_focus) \
           and (AXUtilities.is_check_menu_item(old_focus) \
                or AXUtilities.is_radio_menu_item(old_focus)):
            msg += "suspected menuitem state change"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXObject.is_ancestor(new_focus, old_focus):
            if AXObject.get_name(old_focus):
                msg += "old locusOfFocus is ancestor with name of new locusOfFocus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return False
            return True

        if AXUtilities.object_is_controlled_by(old_focus, new_focus) \
           or AXUtilities.object_is_controlled_by(new_focus, old_focus):
            msg += "new locusOfFocus and old locusOfFocus have controls relation"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def stringsAreRedundant(self, str1, str2, threshold=0.7):
        if not (str1 and str2):
            return False

        if str1 in str2 or str2 in str1:
            return True

        similarity = round(SequenceMatcher(None, str1.lower(), str2.lower()).ratio(), 2)
        msg = (
            f"SCRIPT UTILITIES: Similarity between '{str1}', '{str2}': {similarity} "
            f"(threshold: {threshold})"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return similarity >= threshold
