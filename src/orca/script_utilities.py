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

import functools
import gi
import locale
import re
import time
from difflib import SequenceMatcher

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import Gdk
from gi.repository import Gtk

from . import colornames
from . import debug
from . import focus_manager
from . import keynames
from . import keybindings
from . import input_event
from . import mathsymbols
from . import messages
from . import orca_state
from . import object_properties
from . import pronunciation_dict
from . import script_manager
from . import settings
from . import settings_manager
from . import text_attribute_names
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_table import AXTable
from .ax_utilities import AXUtilities
from .ax_value import AXValue

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities:

    _last_clipboard_update = time.time()

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    ZERO_WIDTH_NO_BREAK_SPACE = '\ufeff'
    SUPERSCRIPT_DIGITS = \
        ['\u2070', '\u00b9', '\u00b2', '\u00b3', '\u2074',
         '\u2075', '\u2076', '\u2077', '\u2078', '\u2079']
    SUBSCRIPT_DIGITS = \
        ['\u2080', '\u2081', '\u2082', '\u2083', '\u2084',
         '\u2085', '\u2086', '\u2087', '\u2088', '\u2089']

    flags = re.UNICODE
    WORDS_RE = re.compile(r"(\W+)", flags)
    SUPERSCRIPTS_RE = re.compile(f"[{''.join(SUPERSCRIPT_DIGITS)}]+", flags)
    SUBSCRIPTS_RE = re.compile(f"[{''.join(SUBSCRIPT_DIGITS)}]+", flags)
    PUNCTUATION = re.compile(r"[^\w\s]", flags)

    # generatorCache
    #
    DISPLAYED_DESCRIPTION = 'displayedDescription'
    DISPLAYED_LABEL = 'displayedLabel'
    DISPLAYED_TEXT = 'displayedText'
    KEY_BINDING = 'keyBinding'
    NESTING_LEVEL = 'nestingLevel'
    NODE_LEVEL = 'nodeLevel'

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
        def pred(x):
            return AXObject.get_index_in_parent(x) >= 0

        nodes = AXObject.get_relation_targets(obj, Atspi.RelationType.NODE_PARENT_OF, pred)
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
            relation = AXObject.get_relation(cell, Atspi.RelationType.NODE_CHILD_OF)
            if not relation:
                continue

            nodeOf = relation.get_target(0)
            if self.isSameObject(obj, nodeOf):
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

        # Don't do any Zombie checks here, as tempting and logical as it
        # may seem as it can lead to chattiness.
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
            if self.isSameObject(aParents[i], bParents[i]):
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

        try:
            return self._script.generatorCache[self.DISPLAYED_LABEL][obj]
        except Exception:
            if self.DISPLAYED_LABEL not in self._script.generatorCache:
                self._script.generatorCache[self.DISPLAYED_LABEL] = {}
            labelString = None

        labels = self.labelsForObject(obj)
        for label in labels:
            labelString = \
                self.appendString(labelString, self.displayedText(label))

        self._script.generatorCache[self.DISPLAYED_LABEL][obj] = labelString
        return self._script.generatorCache[self.DISPLAYED_LABEL][obj]

    def preferDescriptionOverName(self, obj):
        return False

    def descriptionsForObject(self, obj):
        """Return a list of objects describing obj."""

        descriptions = AXObject.get_relation_targets(obj, Atspi.RelationType.DESCRIBED_BY)
        if not descriptions:
            return []

        labels = AXObject.get_relation_targets(obj, Atspi.RelationType.LABELLED_BY)
        if descriptions == labels:
            tokens = ["SCRIPT UTILITIES:", obj,
                      "'s described-by targets are the same as labelled-by targets"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        return descriptions

    def detailsContentForObject(self, obj):
        details = self.detailsForObject(obj)
        return list(map(self.displayedText, details))

    def detailsForObject(self, obj, textOnly=True):
        """Return a list of objects containing details for obj."""

        details = AXObject.get_relation_targets(obj, Atspi.RelationType.DETAILS)
        if not details and AXUtilities.is_toggle_button(obj) \
            and AXUtilities.is_expanded(obj):
            details = [child for child in AXObject.iter_children(obj)]

        if not textOnly:
            return details

        textObjects = []
        for detail in details:
            textObjects.extend(self.findAllDescendants(detail, self.queryNonEmptyText))

        return textObjects

    def displayedDescription(self, obj):
        """Returns the text being displayed for the object describing obj."""

        try:
            return self._script.generatorCache[self.DISPLAYED_DESCRIPTION][obj]
        except Exception:
            if self.DISPLAYED_DESCRIPTION not in self._script.generatorCache:
                self._script.generatorCache[self.DISPLAYED_DESCRIPTION] = {}

        string = " ".join(map(self.displayedText, self.descriptionsForObject(obj)))
        self._script.generatorCache[self.DISPLAYED_DESCRIPTION][obj] = string
        return self._script.generatorCache[self.DISPLAYED_DESCRIPTION][obj]

    def displayedText(self, obj):
        """Returns the text being displayed for an object.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        # TODO - JD: It's finally time to consider killing this for real.

        try:
            return self._script.generatorCache[self.DISPLAYED_TEXT][obj]
        except Exception:
            displayedText = None

        name = AXObject.get_name(obj)
        role = AXObject.get_role(obj)
        if role in [Atspi.Role.PUSH_BUTTON, Atspi.Role.LABEL] and name:
            return name

        if AXObject.supports_text(obj):
            # We should be able to use -1 for the final offset, but that crashes Nautilus.
            text = obj.queryText()
            displayedText = text.getText(0, text.characterCount)
            if self.EMBEDDED_OBJECT_CHARACTER in displayedText:
                displayedText = None

        if not displayedText and role not in [Atspi.Role.COMBO_BOX, Atspi.Role.SPIN_BUTTON]:
            # TODO - JD: This should probably get nuked. But all sorts of
            # existing code might be relying upon this bogus hack. So it
            # will need thorough testing when removed.
            displayedText = name

        if not displayedText and role in [Atspi.Role.PUSH_BUTTON, Atspi.Role.LIST_ITEM]:
            labels = self.unrelatedLabels(obj, minimumWords=1)
            if not labels:
                labels = self.unrelatedLabels(obj, onlyShowing=False, minimumWords=1)
            displayedText = " ".join(map(self.displayedText, labels))

        if self.DISPLAYED_TEXT not in self._script.generatorCache:
            self._script.generatorCache[self.DISPLAYED_TEXT] = {}

        self._script.generatorCache[self.DISPLAYED_TEXT][obj] = displayedText
        return self._script.generatorCache[self.DISPLAYED_TEXT][obj]

    def documentFrame(self, obj=None):
        """Returns the document frame which is displaying the content.
        Note that this is intended primarily for web content."""

        if not obj:
            obj, offset = self.getCaretContext()

        document = AXObject.find_ancestor(obj, AXUtilities.is_document)
        if document:
            return document

        focus = focus_manager.getManager().get_locus_of_focus()
        if AXUtilities.is_document(focus):
            return focus

        return None

    def documentFrameURI(self, documentFrame=None):
        """Returns the URI of the document frame that is active."""

        return None

    def frameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing obj."""

        results = [None, None]

        obj = obj or focus_manager.getManager().get_locus_of_focus()
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
        if event.source == focus_manager.getManager().get_locus_of_focus():
            return True

        return False

    def grabFocus(self, obj):
        try:
            obj.queryComponent().grabFocus()
        except NotImplementedError:
            tokens = ["ERROR:", obj, "does not implement the component interface"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        except Exception as error:
            tokens = ["ERROR: Exception grabbing focus on", obj, error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

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
            and not self.isSameObject(obj, focus_manager.getManager().get_locus_of_focus())

    def hasMatchingHierarchy(self, obj, rolesList):
        """Called to determine if the given object and it's hierarchy of
        parent objects, each have the desired roles. Please note: You
        should strongly consider an alternative means for determining
        that a given object is the desired item. Failing that, you should
        include only enough of the hierarchy to make the determination.
        If the developer of the application you are providing access to
        does so much as add an Adjustment to reposition a widget, this
        method can fail. You have been warned.

        Arguments:
        - obj: the accessible object to check.
        - rolesList: the list of desired roles for the components and the
          hierarchy of its parents.

        Returns True if all roles match.
        """

        current = obj
        for role in rolesList:
            if current is None:
                return False

            if not isinstance(role, list):
                role = [role]

            if isinstance(role[0], str):
                current_role = AXObject.get_role_name(current)
            else:
                current_role = AXObject.get_role(current)

            if current_role not in role:
                return False

            current = AXObject.get_parent_checked(current)

        return True

    def inFindContainer(self, obj=None):
        if obj is None:
            obj = focus_manager.getManager().get_locus_of_focus()

        if not AXUtilities.is_entry(obj):
            return False

        return AXObject.find_ancestor(obj, AXUtilities.is_tool_bar) is not None

    def getFindResultsCount(self, root=None):
        return ""

    def isAnchor(self, obj):
        return False

    def isCode(self, obj):
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

    def isComment(self, obj):
        return False

    def isContentDeletion(self, obj):
        return False

    def isContentError(self, obj):
        return False

    def isContentInsertion(self, obj):
        return False

    def isContentMarked(self, obj):
        return False

    def isContentSuggestion(self, obj):
        return False

    def isInlineSuggestion(self, obj):
        return False

    def isFirstItemInInlineContentSuggestion(self, obj):
        return False

    def isLastItemInInlineContentSuggestion(self, obj):
        return False

    def isEmpty(self, obj):
        return False

    def isHidden(self, obj):
        return False

    def isDPub(self, obj):
        return False

    def isDPubAbstract(self, obj):
        return False

    def isDPubAcknowledgments(self, obj):
        return False

    def isDPubAfterword(self, obj):
        return False

    def isDPubAppendix(self, obj):
        return False

    def isDPubBibliography(self, obj):
        return False

    def isDPubBacklink(self, obj):
        return False

    def isDPubBiblioref(self, obj):
        return False

    def isDPubChapter(self, obj):
        return False

    def isDPubColophon(self, obj):
        return False

    def isDPubConclusion(self, obj):
        return False

    def isDPubCover(self, obj):
        return False

    def isDPubCredit(self, obj):
        return False

    def isDPubCredits(self, obj):
        return False

    def isDPubDedication(self, obj):
        return False

    def isDPubEndnote(self, obj):
        return False

    def isDPubEndnotes(self, obj):
        return False

    def isDPubEpigraph(self, obj):
        return False

    def isDPubEpilogue(self, obj):
        return False

    def isDPubErrata(self, obj):
        return False

    def isDPubExample(self, obj):
        return False

    def isDPubFootnote(self, obj):
        return False

    def isDPubForeword(self, obj):
        return False

    def isDPubGlossary(self, obj):
        return False

    def isDPubGlossref(self, obj):
        return False

    def isDPubIndex(self, obj):
        return False

    def isDPubIntroduction(self, obj):
        return False

    def isDPubPagelist(self, obj):
        return False

    def isDPubPagebreak(self, obj):
        return False

    def isDPubPart(self, obj):
        return False

    def isDPubPreface(self, obj):
        return False

    def isDPubPrologue(self, obj):
        return False

    def isDPubPullquote(self, obj):
        return False

    def isDPubQna(self, obj):
        return False

    def isDPubSubtitle(self, obj):
        return False

    def isDPubToc(self, obj):
        return False

    def isFeed(self, obj):
        return False

    def isFeedArticle(self, obj):
        return False

    def isFigure(self, obj):
        return False

    def isGrid(self, obj):
        return False

    def isGridCell(self, obj):
        return False

    def isLandmark(self, obj):
        return False

    def isLandmarkWithoutType(self, obj):
        return False

    def isLandmarkBanner(self, obj):
        return False

    def isLandmarkComplementary(self, obj):
        return False

    def isLandmarkContentInfo(self, obj):
        return False

    def isLandmarkForm(self, obj):
        return False

    def isLandmarkMain(self, obj):
        return False

    def isLandmarkNavigation(self, obj):
        return False

    def isDPubNoteref(self, obj):
        return False

    def isLandmarkRegion(self, obj):
        return False

    def isLandmarkSearch(self, obj):
        return False

    def isSVG(self, obj):
        return False

    def speakMathSymbolNames(self, obj=None):
        return False

    def isInMath(self):
        return False

    def isMath(self, obj):
        return False

    def isMathLayoutOnly(self, obj):
        return False

    def isMathMultiline(self, obj):
        return False

    def isMathEnclosed(self, obj):
        return False

    def isMathFenced(self, obj):
        return False

    def isMathFractionWithoutBar(self, obj):
        return False

    def isMathPhantom(self, obj):
        return False

    def isMathMultiScript(self, obj):
        return False

    def isMathSubOrSuperScript(self, obj):
        return False

    def isMathUnderOrOverScript(self, obj):
        return False

    def isMathSquareRoot(self, obj):
        return False

    def isMathTable(self, obj):
        return False

    def isMathTableRow(self, obj):
        return False

    def isMathTableCell(self, obj):
        return False

    def isMathToken(self, obj):
        return False

    def isMathTopLevel(self, obj):
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
        return self.isSameObject(
            self.topLevelObject(obj), focus_manager.getManager().get_active_window())

    def isProgressBarUpdate(self, obj):
        if not settings_manager.getManager().getSetting('speakProgressBarUpdates') \
           and not settings_manager.getManager().getSetting('brailleProgressBarUpdates') \
           and not settings_manager.getManager().getSetting('beepProgressBarUpdates'):
            return False, "Updates not enabled"

        if not self.isProgressBar(obj):
            return False, "Is not progress bar"

        if self.hasNoSize(obj):
            return False, "Has no size"

        if settings_manager.getManager().getSetting('ignoreStatusBarProgressBars'):
            if AXObject.find_ancestor(obj, AXUtilities.is_status_bar):
                return False, "Is status bar descendant"

        verbosity = settings_manager.getManager().getSetting('progressBarVerbosity')
        if verbosity == settings.PROGRESS_BAR_ALL:
            return True, "Verbosity is all"

        if verbosity == settings.PROGRESS_BAR_WINDOW:
            if self.topLevelObjectIsActiveWindow(obj):
                return True, "Verbosity is window"
            return False, "Top-level object is not active window"

        if verbosity == settings.PROGRESS_BAR_APPLICATION:
            app = AXObject.get_application(obj)
            activeApp = script_manager.getManager().getActiveScriptApp()
            if app == activeApp:
                return True, "Verbosity is app"
            return False, "App is not active app"

        return True, "Not handled by any other case"

    def isBlockquote(self, obj):
        return AXUtilities.is_block_quote(obj)

    def isDescriptionList(self, obj):
        return AXUtilities.is_description_list(obj)

    def isDescriptionListTerm(self, obj):
        return AXUtilities.is_description_term(obj)

    def isDescriptionListDescription(self, obj):
        return AXUtilities.is_description_value(obj)

    def descriptionListTerms(self, obj):
        if not self.isDescriptionList(obj):
            return []

        _include = self.isDescriptionListTerm
        _exclude = self.isDescriptionList
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
        obj = obj or focus_manager.getManager().get_locus_of_focus()
        return self.getDocumentForObject(obj) is not None

    def activeDocument(self, window=None):
        return self.getTopLevelDocumentForObject(focus_manager.getManager().get_locus_of_focus())

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
            lastColumn = self._script.pointOfReference.get("lastColumn")
        else:
            lastColumn = AXTable.get_cell_coordinates(prevCell)[1]

        return column != lastColumn

    def cellRowChanged(self, cell, prevCell=None):
        row = AXTable.get_cell_coordinates(cell)[0]
        if row == -1:
            return False

        if prevCell is None:
            lastRow = self._script.pointOfReference.get("lastRow")
        else:
            lastRow = AXTable.get_cell_coordinates(prevCell)[0]
        return row != lastRow

    def shouldReadFullRow(self, obj, prevObj=None):
        if self._script.inSayAll():
            return False

        if self._script.getTableNavigator().last_input_event_was_navigation_command():
            return False

        if not self.cellRowChanged(obj, prevObj):
            return False

        table = AXTable.get_table(obj)
        if table is None:
            return False

        if not self.getDocumentForObject(table):
            return settings_manager.getManager().getSetting('readFullRowInGUITable')

        if self.isSpreadSheetTable(table):
            return settings_manager.getManager().getSetting('readFullRowInSpreadSheet')

        return settings_manager.getManager().getSetting('readFullRowInDocumentTable')

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

    def isNonFocusableList(self, obj):
        return AXUtilities.is_list(obj) and not AXUtilities.is_focusable(obj)

    def isStatusBarNotification(self, obj):
        if not AXUtilities.is_notification(obj):
            return False
        return AXObject.find_ancestor(obj, AXUtilities.is_status_bar) is not None

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
            labels = " ".join(map(self.displayedText, self.unrelatedLabels(obj, False, 1)))
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

        if AXObject.is_dead(obj) or self.isZombie(obj):
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
            layoutOnly = not self.isBlockquote(obj)
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
            if not (self.displayedText(obj) or self.displayedLabel(obj)):
                layoutOnly = True

        if layoutOnly:
            tokens = ["SCRIPT UTILITIES:", obj, "is deemed to be layout only"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return layoutOnly

    @staticmethod
    def isInActiveApp(obj):
        """Returns True if the given object is from the same application that
        currently has keyboard focus.

        Arguments:
        - obj: an Accessible object
        """

        focus = focus_manager.getManager().get_locus_of_focus()
        if not (obj and focus):
            return False

        return AXObject.get_application(focus) == AXObject.get_application(obj)

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

    def isSwitch(self, obj):
        return False

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

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False,
                     ignoreDescriptions=True):
        if obj1 == obj2:
            return True

        if obj1 is None or obj2 is None:
            return False

        if not AXUtilities.have_same_role(obj1, obj2):
            return False

        if not ignoreNames and AXObject.get_name(obj1) != AXObject.get_name(obj2):
            return False

        if not ignoreDescriptions \
           and AXObject.get_description(obj1) != AXObject.get_description(obj2):
            return False

        if comparePaths and self._hasSamePath(obj1, obj2):
            return True

        try:
            # Comparing the extents of objects which claim to be different
            # addresses both managed descendants and implementations which
            # recreate accessibles for the same widget.
            extents1 = \
                obj1.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            extents2 = \
                obj2.queryComponent().getExtents(Atspi.CoordType.WINDOW)

            # Objects which claim to be different and which are in different
            # locations are almost certainly not recreated objects.
            if extents1 != extents2:
                return False

            # Objects which claim to have the same role, the same name, and
            # the same size and position are highly likely to be the same
            # functional object -- if they have valid, on-screen extents.
            if extents1.x >= 0 and extents1.y >= 0 and extents1.width > 0 \
                and extents1.height > 0:
                return True
        except Exception as error:
            tokens = ["SCRIPT UTILITIES: Exception in isSameObject (",
                      obj1, "vs", obj2, "):", error]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return False

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

    def labelsForObject(self, obj):
        """Return a list of the labels for this object."""

        def isNotAncestor(acc):
            return not AXObject.find_ancestor(obj, lambda x: x == acc)

        result = AXObject.get_relation_targets(obj, Atspi.RelationType.LABELLED_BY)
        return list(filter(isNotAncestor, result))

    def nestingLevel(self, obj):
        """Determines the nesting level of this object.

        Arguments:
        -obj: the Accessible object
        """

        if obj is None:
            return 0

        try:
            return self._script.generatorCache[self.NESTING_LEVEL][obj]
        except Exception:
            if self.NESTING_LEVEL not in self._script.generatorCache:
                self._script.generatorCache[self.NESTING_LEVEL] = {}

        def pred(x):
            if self.isBlockquote(obj):
                return self.isBlockquote(x)
            if AXUtilities.is_list_item(obj):
                return AXUtilities.is_list(AXObject.get_parent(x))
            return AXUtilities.have_same_role(obj, x)

        ancestors = []
        ancestor = AXObject.find_ancestor(obj, pred)
        while ancestor:
            ancestors.append(ancestor)
            ancestor = AXObject.find_ancestor(ancestor, pred)

        nestingLevel = len(ancestors)
        self._script.generatorCache[self.NESTING_LEVEL][obj] = nestingLevel
        return self._script.generatorCache[self.NESTING_LEVEL][obj]

    def nodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not self.isTreeDescendant(obj):
            return -1

        try:
            return self._script.generatorCache[self.NODE_LEVEL][obj]
        except Exception:
            if self.NODE_LEVEL not in self._script.generatorCache:
                self._script.generatorCache[self.NODE_LEVEL] = {}

        nodes = []
        node = obj
        done = False
        while not done:
            relation = AXObject.get_relation(node, Atspi.RelationType.NODE_CHILD_OF)
            node = None
            if relation:
                node = relation.get_target(0)

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

        self._script.generatorCache[self.NODE_LEVEL][obj] = len(nodes) - 1
        return self._script.generatorCache[self.NODE_LEVEL][obj]

    def isOnScreen(self, obj, boundingbox=None):
        if AXObject.is_dead(obj):
            return False

        if self.isHidden(obj):
            return False

        if not self.isShowingAndVisible(obj):
            tokens = ["SCRIPT UTILITIES:", obj, "is not showing and visible"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        try:
            box = obj.queryComponent().getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception getting extents for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["SCRIPT UTILITIES: Extents for", obj, "are:", box]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if box.x > 10000 or box.y > 10000:
            tokens = ["SCRIPT UTILITIES:", obj, "seems to have bogus coordinates"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if box.x < 0 and box.y < 0 and tuple(box) != (-1, -1, -1, -1):
            tokens = ["SCRIPT UTILITIES:", obj, "has negative coordinates"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if not (box.width or box.height):
            if not AXObject.get_child_count(obj):
                tokens = ["SCRIPT UTILITIES:", obj, "has no size and no children"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return False
            if AXUtilities.is_menu(obj):
                tokens = ["SCRIPT UTILITIES:", obj, "has no size"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return False

            return True

        if boundingbox is None or not self._boundsIncludeChildren(AXObject.get_parent(obj)):
            return True

        if not self.containsRegion(box, boundingbox) and tuple(box) != (-1, -1, -1, -1):
            tokens = ["SCRIPT UTILITIES:", obj, box, "not in", boundingbox]
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

        if not AXObject.supports_text(obj):
            return False

        return bool(re.search(r"\w+", obj.queryText().getText(0, -1)))

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
            tokens = ["SCRIPT UTILITIES:", root, "now reports",
                      AXObject.get_child_count(root), "children"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if extents is None:
            try:
                component = root.queryComponent()
                extents = component.getExtents(Atspi.CoordType.WINDOW)
            except Exception:
                tokens = ["SCRIPT UTILITIES: Exception getting extents of", root]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                extents = 0, 0, 0, 0

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

        if AXUtilities.is_label(root) and not hasNameOrDesc and not self.queryNonEmptyText(root):
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
            return x and not self.isStaticTextLeaf(x) and self.displayedText(x).strip()

        child = AXObject.find_descendant(obj, pred)
        if child is not None:
            return child

        return obj

    def isStatusBarDescendant(self, obj):
        if obj is None:
            return False

        return AXObject.find_ancestor(obj, AXUtilities.is_status_bar) is not None

    def statusBarItems(self, obj):
        if not AXUtilities.is_status_bar(obj):
            return []

        start = time.time()
        items = self._script.pointOfReference.get('statusBarItems')
        if not items:

            def include(x):
                return not AXUtilities.is_status_bar(x)

            items = list(filter(include, self.getOnScreenObjects(obj)))
            self._script.pointOfReference['statusBarItems'] = items

        end = time.time()
        msg = f"SCRIPT UTILITIES: Time getting status bar items: {end - start:.4f}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        return items

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
        focus = focus_manager.getManager().get_locus_of_focus()
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
        obj = obj or focus_manager.getManager().get_locus_of_focus()
        topLevel = self.topLevelObject(obj)
        if not topLevel:
            return False

        AXObject.clear_cache(topLevel, False, "Ensuring we have the correct state.")
        if not AXUtilities.is_active(topLevel) or AXUtilities.is_defunct(topLevel):
            return False

        if not self.isSameObject(topLevel, focus_manager.getManager().get_active_window()):
            return False

        return True

    @staticmethod
    def onSameLine(obj1, obj2, delta=0):
        """Determines if obj1 and obj2 are on the same line."""

        try:
            bbox1 = obj1.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            bbox2 = obj2.queryComponent().getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            return False

        center1 = bbox1.y + bbox1.height / 2
        center2 = bbox2.y + bbox2.height / 2

        return abs(center1 - center2) <= delta

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

    @staticmethod
    def sizeComparison(obj1, obj2):
        try:
            bbox = obj1.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            width1, height1 = bbox.width, bbox.height
        except Exception:
            width1, height1 = 0, 0

        try:
            bbox = obj2.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            width2, height2 = bbox.width, bbox.height
        except Exception:
            width2, height2 = 0, 0

        return (width1 * height1) - (width2 * height2)

    @staticmethod
    def spatialComparison(obj1, obj2):
        """Compares the physical locations of obj1 and obj2 and returns -1,
        0, or 1 to indicate if obj1 physically is before, is in the same
        place as, or is after obj2."""

        try:
            bbox = obj1.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            x1, y1 = bbox.x, bbox.y
        except Exception:
            x1, y1 = 0, 0

        try:
            bbox = obj2.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            x2, y2 = bbox.x, bbox.y
        except Exception:
            x2, y2 = 0, 0

        rv = y1 - y2 or x1 - x2

        # If the objects claim to have the same coordinates, there is either
        # a horrible design crime or we've been given bogus extents. Fall back
        # on the index in the parent. This is seen with GtkListBox items which
        # had been scrolled off-screen.
        if not rv and AXObject.get_parent(obj1) == AXObject.get_parent(obj2):
            rv = AXObject.get_index_in_parent(obj1) - AXObject.get_index_in_parent(obj2)

        rv = max(rv, -1)
        rv = min(rv, 1)

        return rv

    def getTextBoundingBox(self, obj, start, end):
        try:
            extents = obj.queryText().getRangeExtents(start, end, Atspi.CoordType.WINDOW)
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception getting range extents of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return -1, -1, 0, 0

        return extents

    def getBoundingBox(self, obj):
        try:
            extents = obj.queryComponent().getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception getting extents of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return -1, -1, 0, 0

        return extents.x, extents.y, extents.width, extents.height

    def hasNoSize(self, obj):
        if not obj:
            return False

        if AXUtilities.is_application(obj):
            return False

        try:
            extents = obj.queryComponent().getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception getting extents for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return not (extents.width and extents.height)

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
                     Atspi.Role.LIST_BOX,
                     Atspi.Role.MENU,
                     Atspi.Role.MENU_BAR,
                     Atspi.Role.SCROLL_PANE,
                     Atspi.Role.SPLIT_PANE,
                     Atspi.Role.TABLE,
                     Atspi.Role.TREE,
                     Atspi.Role.TREE_TABLE]

        def _include(x):
            if not (x and AXObject.get_role(x) in labelRoles):
                return False
            if AXObject.get_relations(x):
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
            name = AXObject.get_name(label) or self.displayedText(label)
            if name and name in [rootName, AXObject.get_name(AXObject.get_parent(label))]:
                continue
            if len(name.split()) < minimumWords:
                continue
            if rootName.find(name) >= 0:
                continue
            labels_filtered.append(label)

        return sorted(labels_filtered, key=functools.cmp_to_key(self.spatialComparison))

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
            return self.isShowingAndVisible(x) \
                and (AXObject.get_name(x) or AXObject.get_child_count(x))

        def cannotBeActiveWindow(x):
            return not focus_manager.getManager().can_be_active_window(x)

        presentable = list(filter(isPresentable, set(dialogs)))
        unfocused = list(filter(cannotBeActiveWindow, presentable))
        return len(unfocused)

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################

    @staticmethod
    def adjustTextSelection(obj, offset):
        """Adjusts the end point of a text selection

        Arguments:
        - obj: the Accessible object.
        - offset: the new end point - can be to the left or to the right
          depending on the direction of selection
        """

        try:
            text = obj.queryText()
        except Exception:
            return

        if text.getNSelections() <= 0:
            caretOffset = text.caretOffset
            startOffset = min(offset, caretOffset)
            endOffset = max(offset, caretOffset)
            text.addSelection(startOffset, endOffset)
        else:
            startOffset, endOffset = text.getSelection(0)
            if offset < startOffset:
                startOffset = offset
            else:
                endOffset = offset
            text.setSelection(0, startOffset, endOffset)

    def findPreviousObject(self, obj):
        """Finds the object before this one."""

        if not obj or self.isZombie(obj):
            return None

        relation = AXObject.get_relation(obj, Atspi.RelationType.FLOWS_FROM)
        if relation:
            return relation.get_target(0)

        return AXObject.get_previous_object(obj)

    def findNextObject(self, obj):
        """Finds the object after this one."""

        if not obj or self.isZombie(obj):
            return None

        relation = AXObject.get_relation(obj, Atspi.RelationType.FLOWS_TO)
        if relation:
            return relation.get_target(0)

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

        textContents, startOffset, endOffset = self.selectedText(obj)
        if textContents and self._script.pointOfReference.get('entireDocumentSelected'):
            return textContents, startOffset, endOffset

        if self.isSpreadSheetCell(obj):
            return textContents, startOffset, endOffset

        prevObj = self.findPreviousObject(obj)
        while prevObj:
            if self.queryNonEmptyText(prevObj):
                selection, start, end = self.selectedText(prevObj)
                if not selection:
                    break
                textContents = f"{selection} {textContents}"
            prevObj = self.findPreviousObject(prevObj)

        nextObj = self.findNextObject(obj)
        while nextObj:
            if self.queryNonEmptyText(nextObj):
                selection, start, end = self.selectedText(nextObj)
                if not selection:
                    break
                textContents = f"{textContents} {selection}"
            nextObj = self.findNextObject(nextObj)

        return textContents, startOffset, endOffset

    @staticmethod
    def allTextSelections(obj):
        """Get a list of text selections in the given accessible object,
        equivalent to getNSelections()*texti.getSelection()

        Arguments:
        - obj: An accessible.

        Returns list of start and end offsets for multiple selections, or an
        empty list if nothing is selected or if the accessible does not support
        the text interface.
        """

        try:
            text = obj.queryText()
        except Exception:
            return []

        rv = []
        try:
            nSelections = text.getNSelections()
        except Exception:
            nSelections = 0
        for i in range(nSelections):
            rv.append(text.getSelection(i))

        return rv

    def clearTextSelection(self, obj):
        """Clears the text selection if the object supports it.

        Arguments:
        - obj: the Accessible object.
        """

        try:
            text = obj.queryText()
        except Exception:
            return

        for i in range(text.getNSelections()):
            text.removeSelection(i)

    def containsOnlyEOCs(self, obj):
        try:
            string = obj.queryText().getText(0, -1)
        except Exception:
            return False

        return string and not re.search(r"[^\ufffc]", string)

    def expandEOCs(self, obj, startOffset=0, endOffset=-1):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with their text.

        Arguments
        - obj: the object whose text should be expanded
        - startOffset: the offset of the first character to be included
        - endOffset: the offset of the last character to be included

        Returns the fully expanded text for the object.
        """

        try:
            string = self.substring(obj, startOffset, endOffset)
        except Exception:
            return ""

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

        return "".join(toBuild)

    def isWordMisspelled(self, obj, offset):
        """Identifies if the current word is flagged as misspelled by the
        application. Different applications and toolkits flag misspelled
        words differently. Thus each script will likely need to implement
        its own version of this method.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.

        Returns True if the word is flagged as misspelled.
        """

        attributes, start, end  = self.textAttributes(obj, offset, True)
        if attributes.get("invalid") == "spelling":
            return True
        if attributes.get("text-spelling") == "misspelled":
            return True
        if attributes.get("underline") in ["error", "spelling"]:
            return True

        return False

    def getError(self, obj):
        return AXUtilities.is_invalid_entry(obj)

    def getErrorMessage(self, obj):
        return ""

    def isErrorMessage(self, obj):
        return False

    def getCharacterAtOffset(self, obj, offset=None):
        text = self.queryNonEmptyText(obj)
        if text:
            if offset is None:
                offset = text.caretOffset
            return text.getText(offset, offset + 1)

        return ""

    def queryNonEmptyText(self, obj):
        """Get the text interface associated with an object, if it is
        non-empty.

        Arguments:
        - obj: an accessible object
        """

        try:
            text = obj.queryText()
            charCount = text.characterCount
        except NotImplementedError:
            pass
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception getting character count of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        else:
            if charCount:
                return text

        return None

    def deletedText(self, event):
        return event.any_data

    def insertedText(self, event):
        if event.any_data:
            return event.any_data

        msg = "SCRIPT UTILITIES: Broken text insertion event"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if AXUtilities.is_password_text(event.source):
            text = self.queryNonEmptyText(event.source)
            if text:
                string = text.getText(0, -1)
                if string:
                    tokens = ["HACK: Returning last char in '", string, "'"]
                    debug.printTokens(debug.LEVEL_INFO, tokens, True)
                    return string[-1]

        msg = "FAIL: Unable to correct broken text insertion event"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return ""

    def selectedText(self, obj):
        """Get the text selection for the given object.

        Arguments:
        - obj: the text object to extract the selected text from.

        Returns: the selected text contents plus the start and end
        offsets within the text.
        """

        textContents = ""
        startOffset = endOffset = 0
        try:
            textObj = obj.queryText()
        except Exception:
            nSelections = 0
        else:
            nSelections = textObj.getNSelections()

        for i in range(0, nSelections):
            [startOffset, endOffset] = textObj.getSelection(i)
            if startOffset == endOffset:
                continue
            selectedText = self.expandEOCs(obj, startOffset, endOffset)
            if i > 0:
                textContents += " "
            textContents += selectedText

        return [textContents, startOffset, endOffset]

    def getCaretContext(self):
        obj = focus_manager.getManager().get_locus_of_focus()
        try:
            offset = obj.queryText().caretOffset
        except NotImplementedError:
            offset = 0
        except Exception:
            offset = -1

        return obj, offset

    def getFirstCaretPosition(self, obj):
        return obj, 0

    def setCaretPosition(self, obj, offset, documentFrame=None):
        focus_manager.getManager().set_locus_of_focus(None, obj, False)
        self.setCaretOffset(obj, offset)

    def setCaretOffset(self, obj, offset):
        """Set the caret offset on a given accessible. Similar to
        Accessible.setCaretOffset()

        Arguments:
        - obj: Given accessible object.
        - offset: Offset to hich to set the caret.
        """
        try:
            texti = obj.queryText()
        except Exception:
            return None

        texti.setCaretOffset(offset)

    def substring(self, obj, startOffset, endOffset):
        """Returns the substring of the given object's text specialization.

        Arguments:
        - obj: an accessible supporting the accessible text specialization
        - startOffset: the starting character position
        - endOffset: the ending character position. Note that an end offset
          of -1 means the last character
        """

        try:
            text = obj.queryText()
        except Exception:
            return ""

        return text.getText(startOffset, endOffset)

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

    def getAllTextAttributesForObject(self, obj, startOffset=0, endOffset=-1):
        """Returns a list of (start, end, attrsDict) tuples for obj."""
        try:
            text = obj.queryText()
        except Exception:
            return []

        if endOffset == -1:
            endOffset = text.characterCount

        tokens = ["SCRIPT UTILITIES: Getting text attributes for", obj,
                  f"chars: {startOffset}-{endOffset}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        startTime = time.time()

        rv = []
        offset = startOffset
        while offset < endOffset:
            try:
                attrList, start, end = text.getAttributeRun(offset)
                tokens = [f"SCRIPT UTILITIES: At {offset}:", attrList, f"({start}, {end})"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
            except Exception as error:
                msg = f"SCRIPT UTILITIES: Exception getting attributes at {offset}: {error}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return rv
            if start <= end:
                attrDict = dict([attr.split(':', 1) for attr in attrList])
                rv.append((max(start, offset), end, attrDict))
            else:
                # TODO - JD: We're sometimes seeing this from WebKit, e.g. in Evo gitlab messages.
                msg = f"SCRIPT UTILITIES: Start offset {start} > end offset {end}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            offset = max(end, offset + 1)

        endTime = time.time()
        msg = f"SCRIPT UTILITIES: {len(rv)} attribute ranges found in {endTime - startTime:.4f}s"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return rv

    def textAttributes(self, acc, offset=None, get_defaults=False):
        """Get the text attributes run for a given offset in a given accessible

        Arguments:
        - acc: An accessible.
        - offset: Offset in the accessible's text for which to retrieve the
        attributes.
        - get_defaults: Get the default attributes as well as the unique ones.
        Default is True

        Returns a dictionary of attributes, a start offset where the attributes
        begin, and an end offset. Returns ({}, 0, 0) if the accessible does not
        supprt the text attribute.
        """

        rv = {}
        try:
            text = acc.queryText()
        except Exception:
            return rv, 0, 0

        if get_defaults:
            stringAndDict = self.stringToKeysAndDict(text.getDefaultAttributes())
            rv.update(stringAndDict[1])

        if offset is None:
            offset = text.caretOffset

        attrString, start, end = text.getAttributes(offset)
        stringAndDict = self.stringToKeysAndDict(attrString)
        rv.update(stringAndDict[1])

        start = min(start, offset)
        end = max(end, offset + 1)

        return rv, start, end

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
            string = self.substring(obj, startOffset, endOffset)
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
        attributeSet = self.getAllTextAttributesForObject(obj, startOffset, endOffset)
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

        focus = focus_manager.getManager().get_locus_of_focus()
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

    def _addRepeatSegment(self, segment, line):
        """Add in the latest line segment, adjusting for repeat characters
        and punctuation.

        Arguments:
        - segment: the segment of repeated characters.
        - line: the current built-up line to characters to speak.

        Returns: the current built-up line plus the new segment, after
        adjusting for repeat character counts and punctuation.
        """

        count = len(segment)
        if count >= settings.repeatCharacterLimit and segment[0] not in self._script.whitespace:
            repeatChar = segment[0]
            repeatSegment = messages.repeatedCharCount(repeatChar, count)
            line = f"{line} {repeatSegment} "
        else:
            line += segment

        return line

    def shouldVerbalizeAllPunctuation(self, obj):
        if not (self.isCode(obj) or self.isCodeDescendant(obj)):
            return False

        # If the user has set their punctuation level to All, then the synthesizer will
        # do the work for us. If the user has set their punctuation level to None, then
        # they really don't want punctuation and we mustn't override that.
        style = settings_manager.getManager().getSetting("verbalizePunctuationStyle")
        if style in [settings.PUNCTUATION_STYLE_ALL, settings.PUNCTUATION_STYLE_NONE]:
            return False

        return True

    def verbalizeAllPunctuation(self, string):
        result = string
        for symbol in set(re.findall(self.PUNCTUATION, result)):
            charName = f" {symbol} "
            result = re.sub(r"\%s" % symbol, charName, result)

        return result

    def adjustForLinks(self, obj, line, startOffset):
        """Adjust line to include the word "link" after any hypertext links.

        Arguments:
        - obj: the accessible object that this line came from.
        - line: the string to adjust for links.
        - startOffset: the caret offset at the start of the line.

        Returns: a new line adjusted to add the speaking of "link" after
        text which is also a link.
        """

        endOffset = startOffset + len(line)
        links = AXHypertext.get_all_links_in_range(obj, startOffset, endOffset)
        offsets = [AXHypertext.get_link_end_offset(link) for link in links]
        offsets = sorted([offset - startOffset for offset in offsets], reverse=True)
        tokens = list(line)
        for o in offsets:
            string = f" {messages.LINK}"
            if o < len(tokens) and tokens[o].isalnum():
                string += " "
            tokens[o:o] = string

        return "".join(tokens)

    @staticmethod
    def _processMultiCaseString(string):
        return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', string)

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

        if settings.speakMultiCaseStringsAsWords:
            line = self._processMultiCaseString(line)

        if self.speakMathSymbolNames():
            line = mathsymbols.adjustForSpeech(line)

        if settings.speakNumbersAsDigits:
            words = self.WORDS_RE.split(line)
            line = ''.join(map(self._convertWordToDigits, words))

        line = self.adjustForDigits(line)

        if len(line) == 1 and not self._script.inSayAll() and self.isInMath():
            charname = mathsymbols.getCharacterName(line)
            if charname != line:
                return charname

        if not settings.usePronunciationDictionary:
            return line

        newLine = ""
        words = self.WORDS_RE.split(line)
        newLine = ''.join(map(pronunciation_dict.getPronunciation, words))

        if settings.speakMultiCaseStringsAsWords:
            newLine = self._processMultiCaseString(newLine)

        return newLine

    def adjustForRepeats(self, line):
        """Adjust line to include repeat character counts. As some people
        will want this and others might not, there is a setting in
        settings.py that determines whether this functionality is enabled.

        repeatCharacterLimit = <n>

        If <n> is 0, then there would be no repeat characters.
        Otherwise <n> would be the number of same characters (or more)
        in a row that cause the repeat character count output.
        If the value is set to 1, 2 or 3 then it's treated as if it was
        zero. In other words, no repeat character count is given.

        Arguments:
        - line: the string to adjust for repeat character counts.

        Returns: a new line adjusted for repeat character counts (if enabled).
        """

        if (len(line) < 4) or (settings.repeatCharacterLimit < 4):
            return line

        newLine = ''
        segment = lastChar = line[0]

        for i in range(1, len(line)):
            if line[i] == lastChar:
                segment += line[i]
            else:
                newLine = self._addRepeatSegment(segment, newLine)
                segment = line[i]

            lastChar = line[i]

        return self._addRepeatSegment(segment, newLine)

    def adjustForDigits(self, string):
        """Adjusts the string to convert digit-like text, such as subscript
        and superscript numbers, into actual digits.

        Arguments:
        - string: the string to be adjusted

        Returns: a new string which contains actual digits.
        """

        subscripted = set(re.findall(self.SUBSCRIPTS_RE, string))
        superscripted = set(re.findall(self.SUPERSCRIPTS_RE, string))

        for number in superscripted:
            new = [str(self.SUPERSCRIPT_DIGITS.index(d)) for d in number]
            newString = messages.DIGITS_SUPERSCRIPT % "".join(new)
            string = re.sub(number, newString, string)

        for number in subscripted:
            new = [str(self.SUBSCRIPT_DIGITS.index(d)) for d in number]
            newString = messages.DIGITS_SUBSCRIPT % "".join(new)
            string = re.sub(number, newString, string)

        return string

    def indentationDescription(self, line):
        if settings_manager.getManager().getSetting('onlySpeakDisplayedText') \
           or not settings_manager.getManager().getSetting('enableSpeechIndentation'):
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
    def absoluteMouseCoordinates():
        """Gets the absolute position of the mouse pointer."""

        from gi.repository import Gtk
        rootWindow = Gtk.Window().get_screen().get_root_window()
        window, x, y, modifiers = rootWindow.get_pointer()

        return x, y

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

    def treatAsDuplicateEvent(self, event1, event2):
        if not (event1 and event2):
            return False

        # The goal is to find event spam so we can ignore the event.
        if event1 == event2:
            return False

        return event1.source == event2.source \
            and event1.type == event2.type \
            and event1.detail1 == event2.detail1 \
            and event1.detail2 == event2.detail2 \
            and event1.any_data == event2.any_data

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

            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey == "Tab" and event.any_data != "\t":
                return True
            if lastKey == "Return" and event.any_data != "\n":
                return True
            if lastKey in ["Up", "Down", "Page_Up", "Page_Down"]:
                return self.isEditableDescendantOfComboBox(event.source)
            if not self.lastInputEventWasPrintableKey():
                return False

            string = event.source.queryText().getText(0, -1)
            if string.endswith(event.any_data):
                selection, start, end = self.selectedText(event.source)
                if selection == event.any_data:
                    return True
                if string == event.any_data and string.endswith(selection):
                    beginning = string[:string.find(selection)]
                    return beginning.lower().endswith(lastKey.lower())

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

    def intersectingRegion(self, obj1, obj2):
        """Returns the extents of the intersection of obj1 and obj2."""

        try:
            extents1 = obj1.queryComponent().getExtents(Atspi.CoordType.WINDOW)
            extents2 = obj2.queryComponent().getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            return 0, 0, 0, 0

        return self.intersection(extents1, extents2)

    def intersection(self, extents1, extents2):
        x1, y1, width1, height1 = extents1
        x2, y2, width2, height2 = extents2

        xPoints1 = range(x1, x1 + width1 + 1)
        xPoints2 = range(x2, x2 + width2 + 1)
        xIntersection = sorted(set(xPoints1).intersection(set(xPoints2)))

        yPoints1 = range(y1, y1 + height1 + 1)
        yPoints2 = range(y2, y2 + height2 + 1)
        yIntersection = sorted(set(yPoints1).intersection(set(yPoints2)))

        if not (xIntersection and yIntersection):
            return 0, 0, 0, 0

        x = xIntersection[0]
        y = yIntersection[0]
        width = xIntersection[-1] - x
        height = yIntersection[-1] - y

        return x, y, width, height

    def containsRegion(self, extents1, extents2):
        return self.intersection(extents1, extents2) != (0, 0, 0, 0)

    @staticmethod
    def _allNamesForKeyCode(keycode):
        keymap = Gdk.Keymap.get_default()
        entries = keymap.get_entries_for_keycode(keycode)[-1]
        return list(map(Gdk.keyval_name, set(entries)))

    @staticmethod
    def _lastKeyCodeAndModifiers():
        if not isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            return 0, 0

        event = orca_state.lastNonModifierKeyEvent
        if event:
            return event.hw_code, event.modifiers

        return 0, 0

    @staticmethod
    def lastKeyAndModifiers():
        """Convenience method which returns a tuple containing the event
        string and modifiers of the last non-modifier key event or ("", 0)
        if there is no such event."""

        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent) \
           and orca_state.lastNonModifierKeyEvent:
            event = orca_state.lastNonModifierKeyEvent
            if event.keyval_name in ["BackSpace", "Delete"]:
                eventStr = event.keyval_name
            else:
                eventStr = event.event_string
            mods = orca_state.lastInputEvent.modifiers
        else:
            eventStr = ""
            mods = 0

        return (eventStr, mods)

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

        try:
            return self._script.generatorCache[self.KEY_BINDING][obj]
        except Exception:
            if self.KEY_BINDING not in self._script.generatorCache:
                self._script.generatorCache[self.KEY_BINDING] = {}

        keybinding = AXObject.get_action_key_binding(obj, 0)
        if not keybinding:
            self._script.generatorCache[self.KEY_BINDING][obj] = ["", "", ""]
            return self._script.generatorCache[self.KEY_BINDING][obj]

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

        if self.KEY_BINDING not in self._script.generatorCache:
            self._script.generatorCache[self.KEY_BINDING] = {}

        self._script.generatorCache[self.KEY_BINDING][obj] = \
            [mnemonic, fullShortcut, accelerator]
        return self._script.generatorCache[self.KEY_BINDING][obj]

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

    @staticmethod
    def unicodeValueString(character):
        """ Returns a four hex digit representation of the given character

        Arguments:
        - The character to return representation

        Returns a string representaition of the given character unicode vlue
        """

        try:
            return f"{ord(character):04x}"
        except Exception:
            debug.printException(debug.LEVEL_WARNING)
            return ""

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
        offset = 0
        text = self.queryNonEmptyText(root)
        if text:
            offset = text.characterCount - 1

        return root, offset

    def selectedChildren(self, obj):
        children = AXSelection.get_selected_children(obj)
        if children:
            return children

        msg = "SCRIPT UTILITIES: Selected children not retrieved via selection interface."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        role = AXObject.get_role(obj)
        if role == Atspi.Role.MENU and not children:
            children = self.findAllDescendants(obj, AXUtilities.is_selected)

        if role == Atspi.Role.COMBO_BOX \
           and children and AXObject.get_role(children[0]) == Atspi.Role.MENU:
            children = self.selectedChildren(children[0])
            name = AXObject.get_name(obj)
            if not children and name:
                def pred(x):
                    return AXObject.get_name(x) == name

                children = self.findAllDescendants(obj, pred)

        return children

    def speakSelectedCellRange(self, obj):
        return False

    def getSelectionContainer(self, obj):
        if not obj:
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

    def popupMenuFor(self, obj):
        if obj is None:
            return None

        menus = [child for child in AXObject.iter_children(obj, AXUtilities.is_menu)]
        for menu in menus:
            if AXUtilities.is_enabled(menu):
                return menu

        return None

    def isButtonWithPopup(self, obj):
        return AXUtilities.is_button(obj) and AXUtilities.has_popup(obj)

    def isPopupMenuForCurrentItem(self, obj):
        focus = focus_manager.getManager().get_locus_of_focus()
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

    def isMenuButton(self, obj):
        return AXUtilities.is_button(obj) and self.popupMenuFor(obj) is not None

    def inMenu(self, obj=None):
        obj = obj or focus_manager.getManager().get_locus_of_focus()
        if obj is None:
            return False

        if AXUtilities.is_menu_item_of_any_kind(obj) or AXUtilities.is_menu(obj):
            return True

        if AXUtilities.is_panel(obj) or AXUtilities.is_separator(obj):
            return AXObject.find_ancestor(obj, AXUtilities.is_menu) is not None

        return False

    def inContextMenu(self, obj=None):
        obj = obj or focus_manager.getManager().get_locus_of_focus()
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
            return self.displayedText(obj)

        entry = self.getEntryForEditableComboBox(obj)
        if entry:
            return self.displayedText(entry)

        selected = self._script.utilities.selectedChildren(obj)
        selected = selected or self._script.utilities.selectedChildren(AXObject.get_child(obj, 0))
        if len(selected) == 1:
            return selected[0].name or self.displayedText(selected[0])

        return self.displayedText(obj)

    def isPopOver(self, obj):
        return False

    def isNonModalPopOver(self, obj):
        if not self.isPopOver(obj):
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

    def hasDetails(self, obj):
        return False

    def isDetails(self, obj):
        return False

    def detailsFor(self, obj):
        return []

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

    def _objectBoundsMightBeBogus(self, obj):
        return False

    def _objectMightBeBogus(self, obj):
        return False

    def containsPoint(self, obj, x, y, margin=2):
        if self._objectBoundsMightBeBogus(obj) and self.textAtPoint(obj, x, y) == ("", 0, 0):
            return False

        if self._objectMightBeBogus(obj):
            return False

        try:
            component = obj.queryComponent()
        except Exception:
            return False

        if component.contains(x, y, Atspi.CoordType.WINDOW):
            return True

        x1, y1 = x + margin, y + margin
        if component.contains(x1, y1, Atspi.CoordType.WINDOW):
            tokens = ["SCRIPT UTILITIES: ", obj, f"contains ({x1},{y1}); not ({x},{y}"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def _boundsIncludeChildren(self, obj):
        if obj is None:
            return False

        if self.hasNoSize(obj):
            return False

        return not (AXUtilities.is_menu(obj) or AXUtilities.is_page_tab(obj))

    def treatAsEntry(self, obj):
        return False

    def _treatAsLeafNode(self, obj):
        if obj is None or AXObject.is_dead(obj):
            return False

        if not AXObject.get_child_count(obj):
            return True

        if AXUtilities.is_autocomplete(obj) or AXUtilities.is_table_row(obj):
            return False

        if AXUtilities.is_combo_box(obj):
            return AXObject.find_descendant(obj, AXUtilities.is_entry) is None

        if AXUtilities.is_link(obj) and AXObject.get_name(obj):
            return True

        if AXUtilities.is_expandable(obj):
            return not AXUtilities.is_expanded(obj)

        if AXUtilities.is_button(obj):
            return True

        return False

    def accessibleAtPoint(self, root, x, y):
        if self.isHidden(root):
            return None

        try:
            component = root.queryComponent()
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception querying component of", root]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return None

        result = component.getAccessibleAtPoint(x, y, Atspi.CoordType.WINDOW)
        tokens = ["SCRIPT UTILITIES: ", result, "is descendant of", root, f"at ({x}, {y})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def descendantAtPoint(self, root, x, y):
        if not root:
            return None

        if not self.isShowingAndVisible(root):
            return None

        if self.containsPoint(root, x, y):
            if self._treatAsLeafNode(root) or not self._boundsIncludeChildren(root):
                return root
        elif self._treatAsLeafNode(root) or self._boundsIncludeChildren(root):
            return None

        if AXObject.supports_table(root):
            child = self.accessibleAtPoint(root, x, y)
            if child and child != root:
                cell = self.descendantAtPoint(child, x, y)
                if cell:
                    return cell
                return child

        candidates_showing = []
        candidates = []
        for child in AXObject.iter_children(root):
            obj = self.descendantAtPoint(child, x, y)
            if obj:
                return obj
            if not self.containsPoint(child, x, y):
                continue
            if self.queryNonEmptyText(child):
                string = child.queryText().getText(0, -1)
                if re.search(r"[^\ufffc\s]", string):
                    candidates.append(child)
                    if AXUtilities.is_showing(child):
                        candidates_showing.append(child)

        if len(candidates_showing) == 1:
            return candidates_showing[0]
        if len(candidates) == 1:
            # It should have had state "showing" actually
            return candidates[0]

        return None

    def _adjustPointForObj(self, obj, x, y):
        return x, y

    def isMultiParagraphObject(self, obj):
        if not obj:
            return False

        if not AXObject.supports_text(obj):
            return False

        text = obj.queryText()
        string = text.getText(0, -1)
        chunks = list(filter(lambda x: x.strip(), string.split("\n\n")))
        return len(chunks) > 1

    def getWordAtOffsetAdjustedForNavigation(self, obj, offset=None):
        try:
            text = obj.queryText()
            if offset is None:
                offset = text.caretOffset
        except Exception:
            return "", 0, 0

        word, start, end = self.getWordAtOffset(obj, offset)
        prevObj, prevOffset = self._script.pointOfReference.get(
            "penultimateCursorPosition", (None, -1))
        if prevObj != obj:
            return word, start, end

        # If we're in an ongoing series of native navigation-by-word commands, just present the
        # newly-traversed string.
        prevWord, prevStart, prevEnd = self.getWordAtOffset(prevObj, prevOffset)
        if self._script.pointOfReference.get("lastTextUnitSpoken") == "word":
            if self.lastInputEventWasPrevWordNav():
                start = offset
                end = prevOffset
            elif self.lastInputEventWasNextWordNav():
                start = prevOffset
                end = offset

            word = text.getText(start, end)
            debugString = word.replace("\n", "\\n")
            msg = (
                f"SCRIPT UTILITIES: Adjusted word at offset {offset} for ongoing word nav is "
                f"'{debugString}' ({start}-{end})"
            )
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return word, start, end

        # Otherwise, attempt some smarts so that the user winds up with the same presentation
        # they would get were this an ongoing series of native navigation-by-word commands.
        if self.lastInputEventWasPrevWordNav():
            # If we moved left via native nav, this should be the start of a native-navigation
            # word boundary, regardless of what ATK/AT-SPI2 tells us.
            start = offset

            # The ATK/AT-SPI2 word typically ends in a space; if the ending is neither a space,
            # nor an alphanumeric character, then suspect that character is a navigation boundary
            # where we would have landed before via the native previous word command.
            if not (word[-1].isspace() or word[-1].isalnum()):
                end -= 1

        elif self.lastInputEventWasNextWordNav():
            # If we moved right via native nav, this should be the end of a native-navigation
            # word boundary, regardless of what ATK/AT-SPI2 tells us.
            end = offset

            # This suggests we just moved to the end of the previous word.
            if word != prevWord and prevStart < offset <= prevEnd:
                start = prevStart

            # If the character to the left of our present position is neither a space, nor
            # an alphanumeric character, then suspect that character is a navigation boundary
            # where we would have landed before via the native next word command.
            lastChar = text.getText(offset - 1, offset)
            if not (lastChar.isspace() or lastChar.isalnum()):
                start = offset - 1

        word = text.getText(start, end)

        # We only want to present the newline character when we cross a boundary moving from one
        # word to another. If we're in the same word, strip it out.
        if "\n" in word and word == prevWord:
            if word.startswith("\n"):
                start += 1
            elif word.endswith("\n"):
                end -= 1
            word = text.getText(start, end)

        word = text.getText(start, end)
        debugString = word.replace("\n", "\\n")
        msg = (
            f"SCRIPT UTILITIES: Adjusted word at offset {offset} for new word nav is "
            f"'{debugString}' ({start}-{end})"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return word, start, end

    def getWordAtOffset(self, obj, offset=None):
        try:
            text = obj.queryText()
            if offset is None:
                offset = text.caretOffset
        except Exception:
            return "", 0, 0

        word, start, end = text.getTextAtOffset(offset, Atspi.TextBoundaryType.WORD_START)
        debugString = word.replace("\n", "\\n")
        msg = (
            f"SCRIPT UTILITIES: Word at offset {offset} is "
            f"'{debugString}' ({start}-{end})"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return word, start, end

    def textAtPoint(self, obj, x, y, boundary=None):
        text = self.queryNonEmptyText(obj)
        if not text:
            return "", 0, 0

        if boundary is None:
            boundary = Atspi.TextBoundaryType.LINE_START

        x, y = self._adjustPointForObj(obj, x, y)
        offset = text.getOffsetAtPoint(x, y, Atspi.CoordType.WINDOW)
        if not 0 <= offset < text.characterCount:
            return "", 0, 0

        string, start, end = text.getTextAtOffset(offset, boundary)
        if not string:
            return "", start, end

        if boundary == Atspi.TextBoundaryType.WORD_START and not string.strip():
            return "", 0, 0

        extents = text.getRangeExtents(start, end, Atspi.CoordType.WINDOW)
        if not self.containsRegion(extents, (x, y, 1, 1)) and string != "\n":
            return "", 0, 0

        if not string.endswith("\n") or string == "\n":
            return string, start, end

        if boundary == Atspi.TextBoundaryType.CHAR:
            return string, start, end

        char = self.textAtPoint(obj, x, y, Atspi.TextBoundaryType.CHAR)
        if char[0] == "\n" and char[2] - char[1] == 1:
            return char

        return string, start, end

    def visibleRows(self, obj, boundingbox):
        nRows = AXTable.get_row_count(obj)

        tokens = ["SCRIPT UTILITIES: ", obj, f"has {nRows} rows"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        x, y, width, height = boundingbox
        cell = self.descendantAtPoint(obj, x, y + 1)
        row = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
        startIndex = max(0, row)
        tokens = ["SCRIPT UTILITIES: First cell:", cell, f"(row: {row}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # Just in case the row above is a static header row in a scrollable table.
        try:
            extents = cell.queryComponent().getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            nextIndex = startIndex
        else:
            cell = self.descendantAtPoint(obj, x, y + extents.height + 1)
            row, AXTable.get_cell_coordinates(cell, prefer_attribute=False)[0]
            nextIndex = max(startIndex, row)
            tokens = ["SCRIPT UTILITIES: Next cell:", cell, f"(row: {row})"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        cell = self.descendantAtPoint(obj, x, y + height - 1)
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
        if not (AXObject.supports_table(obj) and AXObject.supports_component(obj)):
            return []

        try:
            component = obj.queryComponent()
            extents = component.getExtents(Atspi.CoordType.WINDOW)
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception getting extents of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        rows = self.visibleRows(obj, extents)
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

        try:
            component = table.queryComponent()
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception querying component interface of", table]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return startIndex, endIndex

        x, y, width, height = component.getExtents(Atspi.CoordType.WINDOW)
        cell = component.getAccessibleAtPoint(x+1, y, Atspi.CoordType.WINDOW)
        if cell:
            column = AXTable.get_cell_coordinates(cell, prefer_attribute=False)[1]
            startIndex = column

        cell = component.getAccessibleAtPoint(x+width-1, y, Atspi.CoordType.WINDOW)
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

    def isShowingAndVisible(self, obj):
        if AXUtilities.is_showing(obj) and AXUtilities.is_visible(obj):
            return True

        # TODO - JD: This really should be in the toolkit scripts. But it
        # seems to be present in multiple toolkits, so it's either being
        # inherited (e.g. from Gtk in Firefox Chrome, LO, Eclipse) or it
        # may be an AT-SPI2 bug. For now, handling it here.
        menuRoles = [Atspi.Role.MENU,
                     Atspi.Role.MENU_ITEM,
                     Atspi.Role.CHECK_MENU_ITEM,
                     Atspi.Role.RADIO_MENU_ITEM,
                     Atspi.Role.SEPARATOR]
        if AXObject.get_role(obj) in menuRoles and self.isInOpenMenuBarMenu(obj):
            tokens = ["HACK: Treating", obj, "as showing and visible"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def isZombie(self, obj):
        index = AXObject.get_index_in_parent(obj)
        topLevelRoles = [Atspi.Role.APPLICATION,
                         Atspi.Role.ALERT,
                         Atspi.Role.DIALOG,
                         Atspi.Role.LABEL, # For Unity Panel Service bug
                         Atspi.Role.PAGE, # For Evince bug
                         Atspi.Role.WINDOW,
                         Atspi.Role.FRAME]
        role = AXObject.get_role(obj)
        tokens = ["SCRIPT UTILITIES: ", obj, "is zombie:"]
        if index == -1 and role not in topLevelRoles:
            tokens.append("index is -1")
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True
        if AXUtilities.is_defunct(obj):
            tokens.append("is defunct")
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True
        if AXUtilities.is_invalid_state(obj):
            tokens.append("has invalid state")
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True
        if AXUtilities.is_invalid_role(obj):
            tokens.append("has invalid role")
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def findReplicant(self, root, obj):
        tokens = ["SCRIPT UTILITIES: Searching for replicant for", obj, "in", root]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not (root and obj):
            return None

        if AXUtilities.is_table(root) or AXUtilities.is_embedded(root):
            return None

        def isSame(x):
            return self.isSameObject(x, obj, comparePaths=True, ignoreNames=True)

        if isSame(root):
            replicant = root
        else:
            replicant = AXObject.find_descendant(root, isSame)

        tokens = ["HACK: Returning", replicant, "as replicant for Zombie", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return replicant

    def getFunctionalChildCount(self, obj):
        relation = AXObject.get_relation(obj, Atspi.RelationType.NODE_PARENT_OF)
        if relation:
            return relation.get_n_targets()
        return AXObject.get_child_count(obj)

    def getFunctionalChildren(self, obj, sibling=None):
        result = AXObject.get_relation_targets(obj, Atspi.RelationType.NODE_PARENT_OF)
        if result:
            return result
        if self.isDescriptionListTerm(sibling):
            return self.descriptionListTerms(obj)
        if self.isDescriptionListDescription(sibling):
            return self.valuesForTerm(self.termForValue(sibling))
        return [x for x in AXObject.iter_children(obj)]

    def getFunctionalParent(self, obj):
        relation = AXObject.get_relation(obj, Atspi.RelationType.NODE_CHILD_OF)
        if relation:
            return relation.get_target(0)
        return AXObject.get_parent(obj)

    def getPositionAndSetSize(self, obj, **args):
        if obj is None:
            return -1, -1

        if AXUtilities.is_table_cell(obj) and args.get("readingRow"):
            row = AXTable.get_cell_coordinates(obj)[0]
            rowcount = AXTable.get_row_count(AXTable.get_table(obj))
            return row, rowcount

        if AXUtilities.is_combo_box(obj):
            selected = self.selectedChildren(obj)
            if selected:
                obj = selected[0]
            else:
                def isMenu(x):
                    return AXUtilities.is_menu(x) or AXUtilities.is_list_box(x)

                selected = self.selectedChildren(AXObject.find_descendant(obj, isMenu))
                if selected:
                    obj = selected[0]
                else:
                    return -1, -1

        parent = self.getFunctionalParent(obj)
        childCount = self.getFunctionalChildCount(parent)
        if childCount > 100 and parent == AXObject.get_parent(obj):
            return AXObject.get_index_in_parent(obj), childCount

        siblings = self.getFunctionalChildren(parent, obj)
        if len(siblings) < 100 and not AXObject.find_ancestor(obj, AXUtilities.is_combo_box):
            layoutRoles = [Atspi.Role.SEPARATOR, Atspi.Role.TEAROFF_MENU_ITEM]

            def isNotLayoutOnly(x):
                return not (self.isZombie(x) or AXObject.get_role(x) in layoutRoles)

            siblings = list(filter(isNotLayoutOnly, siblings))

        if not (siblings and obj in siblings):
            return -1, -1

        if self.isFocusableLabel(obj):
            siblings = list(filter(self.isFocusableLabel, siblings))
            if len(siblings) == 1:
                return -1, -1

        position = siblings.index(obj)
        setSize = len(siblings)
        return position, setSize

    def termForValue(self, obj):
        if not self.isDescriptionListDescription(obj):
            return None

        while obj and not self.isDescriptionListTerm(obj):
            obj = AXObject.get_previous_sibling(obj)

        return obj

    def valuesForTerm(self, obj):
        if not self.isDescriptionListTerm(obj):
            return []

        values = []
        obj = AXObject.get_next_sibling(obj)
        while obj and self.isDescriptionListDescription(obj):
            values.append(obj)
            obj = AXObject.get_next_sibling(obj)

        return values

    def getValueCountForTerm(self, obj):
        return len(self.valuesForTerm(obj))

    def getRoleDescription(self, obj, isBraille=False):
        return ""

    def getCachedTextSelection(self, obj):
        textSelections = self._script.pointOfReference.get('textSelections', {})
        start, end, string = textSelections.get(hash(obj), (0, 0, ''))
        tokens = ["SCRIPT UTILITIES: Cached selection for", obj, f"is '{string}' ({start}, {end})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return start, end, string

    def updateCachedTextSelection(self, obj):
        try:
            text = obj.queryText()
        except NotImplementedError:
            tokens = ["SCRIPT UTILITIES:", obj, "doesn't implement AtspiText"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            text = None
        except Exception:
            tokens = ["SCRIPT UTILITIES: Exception querying text interface for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            text = None

        if self._script.pointOfReference.get('entireDocumentSelected'):
            selectedText, selectedStart, selectedEnd = self.allSelectedText(obj)
            if not selectedText:
                self._script.pointOfReference['entireDocumentSelected'] = False
                self._script.pointOfReference['textSelections'] = {}

        textSelections = self._script.pointOfReference.get('textSelections', {})

        # Because some apps and toolkits create, destroy, and duplicate objects
        # and events.
        if hash(obj) in textSelections:
            value = textSelections.pop(hash(obj))
            for x in [k for k in textSelections.keys() if textSelections.get(k) == value]:
                textSelections.pop(x)

        # TODO: JD - this doesn't yet handle the case of multiple non-contiguous
        # selections in a single accessible object.
        start, end, string = 0, 0, ''
        if text:
            try:
                start, end = text.getSelection(0)
            except Exception:
                tokens = ["SCRIPT UTILITIES: Exception getting selected text for", obj]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                start = end = 0
            if start != end:
                string = text.getText(start, end)

        tokens = ["SCRIPT UTILITIES: New selection for", obj, f"is '{string}' ({start}, {end})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        textSelections[hash(obj)] = start, end, string
        self._script.pointOfReference['textSelections'] = textSelections

    @staticmethod
    def onClipboardContentsChanged(*args):
        script = script_manager.getManager().getActiveScript()
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

    def lastInputEventCameFromThisApp(self):
        if not isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            return False

        event = orca_state.lastNonModifierKeyEvent
        return event and event.isFromApplication(self._script.app)

    def lastInputEventWasPrintableKey(self):
        event = orca_state.lastInputEvent
        if not isinstance(event, input_event.KeyboardEvent):
            return False

        return event.isPrintableKey()

    def lastInputEventWasCommand(self):
        keyString, mods = self.lastKeyAndModifiers()
        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasPageSwitch(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString.isnumeric():
            return mods & keybindings.ALT_MODIFIER_MASK

        if keyString in ["Page_Up", "Page_Down"]:
            return mods & keybindings.CTRL_MODIFIER_MASK

        return False

    def lastInputEventWasUnmodifiedArrow(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Left", "Right", "Up", "Down"]:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK \
           or mods & keybindings.SHIFT_MODIFIER_MASK \
           or mods & keybindings.ALT_MODIFIER_MASK \
           or mods & keybindings.ORCA_MODIFIER_MASK:
            return False

        return True

    def lastInputEventWasCaretNav(self):
        return self.lastInputEventWasCharNav() \
            or self.lastInputEventWasWordNav() \
            or self.lastInputEventWasLineNav() \
            or self.lastInputEventWasLineBoundaryNav()

    def lastInputEventWasCharNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Left", "Right"]:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK \
           or mods & keybindings.ALT_MODIFIER_MASK:
            return False

        return True

    def lastInputEventWasWordNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Left", "Right"]:
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasPrevWordNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString == "Left":
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasNextWordNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString == "Right":
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasLineNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Up", "Down"]:
            return False

        if self.isEditableDescendantOfComboBox(focus_manager.getManager().get_locus_of_focus()):
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasLineBoundaryNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Home", "End"]:
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasPageNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Page_Up", "Page_Down"]:
            return False

        if self.isEditableDescendantOfComboBox(focus_manager.getManager().get_locus_of_focus()):
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasFileBoundaryNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Home", "End"]:
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasCaretNavWithSelection(self):
        keyString, mods = self.lastKeyAndModifiers()
        if mods & keybindings.SHIFT_MODIFIER_MASK:
            return keyString in ["Home", "End", "Up", "Down", "Left", "Right"]

        return False

    def lastInputEventWasUndo(self):
        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'z' not in keynames:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK:
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def lastInputEventWasRedo(self):
        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'z' not in keynames:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK:
            return mods & keybindings.SHIFT_MODIFIER_MASK

        return False

    def lastInputEventWasCut(self):
        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'x' not in keynames:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK:
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def lastInputEventWasCopy(self):
        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'c' not in keynames:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK:
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def lastInputEventWasPaste(self):
        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'v' not in keynames:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK:
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def lastInputEventWasSelectAll(self):
        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'a' not in keynames:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK:
            return not (mods & keybindings.SHIFT_MODIFIER_MASK)

        return False

    def lastInputEventWasDelete(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString in ["Delete", "KP_Delete"]:
            return True

        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'd' not in keynames:
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasTab(self):
        keyString, mods = self.lastKeyAndModifiers()
        if keyString not in ["Tab", "ISO_Left_Tab"]:
            return False

        if mods & keybindings.CTRL_MODIFIER_MASK \
           or mods & keybindings.ALT_MODIFIER_MASK \
           or mods & keybindings.ORCA_MODIFIER_MASK:
            return False

        return True

    def lastInputEventWasMouseButton(self):
        return isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent)

    def lastInputEventWasPrimaryMouseClick(self):
        event = orca_state.lastInputEvent
        if isinstance(event, input_event.MouseButtonEvent):
            return event.button == "1" and event.pressed

        return False

    def lastInputEventWasMiddleMouseClick(self):
        event = orca_state.lastInputEvent
        if isinstance(event, input_event.MouseButtonEvent):
            return event.button == "2" and event.pressed

        return False

    def lastInputEventWasSecondaryMouseClick(self):
        event = orca_state.lastInputEvent
        if isinstance(event, input_event.MouseButtonEvent):
            return event.button == "3" and event.pressed

        return False

    def lastInputEventWasPrimaryMouseRelease(self):
        event = orca_state.lastInputEvent
        if isinstance(event, input_event.MouseButtonEvent):
            return event.button == "1" and not event.pressed

        return False

    def lastInputEventWasMiddleMouseRelease(self):
        event = orca_state.lastInputEvent
        if isinstance(event, input_event.MouseButtonEvent):
            return event.button == "2" and not event.pressed

        return False

    def lastInputEventWasSecondaryMouseRelease(self):
        event = orca_state.lastInputEvent
        if isinstance(event, input_event.MouseButtonEvent):
            return event.button == "3" and not event.pressed

        return False

    def lastInputEventWasTableSort(self, delta=0.5):
        event = orca_state.lastInputEvent
        if not event:
            return False

        now = time.time()
        if now - event.time > delta:
            return False

        lastSortTime = self._script.pointOfReference.get('last-table-sort-time', 0.0)
        if now - lastSortTime < delta:
            return False

        if isinstance(event, input_event.MouseButtonEvent):
            if not self.lastInputEventWasPrimaryMouseRelease():
                return False
        elif isinstance(event, input_event.KeyboardEvent):
            if not event.isHandledBy(self._script.leftClickReviewItem):
                keyString, mods = self.lastKeyAndModifiers()
                if keyString not in ["Return", "space", " "]:
                    return False

        return AXUtilities.is_table_header(focus_manager.getManager().get_locus_of_focus())

    def isPresentableExpandedChangedEvent(self, event):
        if self.isSameObject(event.source, focus_manager.getManager().get_locus_of_focus()):
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
            if focus_manager.getManager().focus_is_dead():
                return True
        elif AXUtilities.is_table_cell(event.source) and not AXUtilities.is_selected(event.source):
            msg = "SCRIPT UTILITIES: Event is not being presented due to role and states"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if focus_manager.getManager().get_locus_of_focus() in \
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

        keyString, mods = self.lastKeyAndModifiers()
        if keyString == "BackSpace":
            return True

        return False

    def isDeleteCommandTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        return self.lastInputEventWasDelete()

    def isUndoCommandTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        if not self.lastInputEventWasUndo():
            return False

        start, end, string = self.getCachedTextSelection(event.source)
        return not string

    def isSelectedTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
            return False

        if self.lastInputEventWasPaste():
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
        if not self.lastInputEventWasUndo():
            return False

        if self.isSelectedTextInsertionEvent(event):
            return True

        return False

    def isMiddleMouseButtonTextInsertionEvent(self, event):
        if not event.type.startswith("object:text-changed:insert"):
            return False

        return self.lastInputEventWasMiddleMouseClick()

    def isEchoableTextInsertionEvent(self, event):
        if not event.type.startswith("object:text-changed:insert"):
            return False

        if AXUtilities.is_focusable(event.source) \
           and not AXUtilities.is_focused(event.source) \
           and event.source != focus_manager.getManager().get_locus_of_focus():
            msg = "SCRIPT UTILITIES: Not echoable text insertion event: " \
                 "focusable source is not focused"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_password_text(event.source):
            return settings_manager.getManager().getSetting("enableKeyEcho")

        if len(event.any_data.strip()) == 1:
            return settings_manager.getManager().getSetting("enableEchoByCharacter")

        return False

    def isEditableTextArea(self, obj):
        if not self.isTextArea(obj):
            return False
        return AXUtilities.is_editable(obj)

    def isClipboardTextChangedEvent(self, event):
        if not event.type.startswith("object:text-changed"):
            return False

        if not self.lastInputEventWasCommand() or self.lastInputEventWasUndo():
            return False

        if self.isBackSpaceCommandTextDeletionEvent(event):
            return False

        if "delete" in event.type and self.lastInputEventWasPaste():
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
        obj = obj or focus_manager.getManager().get_locus_of_focus()
        if not obj or AXObject.is_dead(obj):
            return False

        contents = self.getClipboardContents()
        if not contents:
            return False

        string, start, end = self.selectedText(obj)
        if string and string in contents:
            return True

        obj = self.realActiveDescendant(obj) or obj
        if AXObject.is_dead(obj):
            return False

        return obj and AXObject.get_name(obj) in contents

    def clearCachedCommandState(self):
        self._script.pointOfReference['undo'] = False
        self._script.pointOfReference['redo'] = False
        self._script.pointOfReference['paste'] = False
        self._script.pointOfReference['last-selection-message'] = ''

    def handleUndoTextEvent(self, event):
        if self.lastInputEventWasUndo():
            if not self._script.pointOfReference.get('undo'):
                self._script.presentMessage(messages.UNDO)
                self._script.pointOfReference['undo'] = True
            self.updateCachedTextSelection(event.source)
            return True

        if self.lastInputEventWasRedo():
            if not self._script.pointOfReference.get('redo'):
                self._script.presentMessage(messages.REDO)
                self._script.pointOfReference['redo'] = True
            self.updateCachedTextSelection(event.source)
            return True

        return False

    def handleUndoLocusOfFocusChange(self):
        if self._locusOfFocusIsTopLevelObject():
            return False

        if self.lastInputEventWasUndo():
            if not self._script.pointOfReference.get('undo'):
                self._script.presentMessage(messages.UNDO)
                self._script.pointOfReference['undo'] = True
            return True

        if self.lastInputEventWasRedo():
            if not self._script.pointOfReference.get('redo'):
                self._script.presentMessage(messages.REDO)
                self._script.pointOfReference['redo'] = True
            return True

        return False

    def handlePasteLocusOfFocusChange(self):
        if self._locusOfFocusIsTopLevelObject():
            return False

        if self.lastInputEventWasPaste():
            if not self._script.pointOfReference.get('paste'):
                self._script.presentMessage(
                    messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF)
                self._script.pointOfReference['paste'] = True
            return True

        return False

    def eventIsCanvasNoise(self, event):
        return False

    def eventIsSpinnerNoise(self, event):
        return False

    def eventIsUserTriggered(self, event):
        if not orca_state.lastInputEvent:
            msg = "SCRIPT UTILITIES: Not user triggered: No last input event."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        delta = time.time() - orca_state.lastInputEvent.time
        if delta > 1:
            msg = f"SCRIPT UTILITIES: Not user triggered: Last input event {delta:.2f}s ago."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return True

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
        allAlreadySelected = self._script.pointOfReference.get('allItemsSelected')
        allCurrentlySelected = self.allItemsSelected(obj)
        if allAlreadySelected and allCurrentlySelected:
            return True

        self._script.pointOfReference['allItemsSelected'] = allCurrentlySelected
        if self.lastInputEventWasSelectAll() and allCurrentlySelected:
            self._script.presentMessage(messages.CONTAINER_SELECTED_ALL)
            focus_manager.getManager().set_locus_of_focus(None, obj, False)
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

        if self._speakTextSelectionState(len(newString)):
            return True

        # Even though we present a message, treat it as unhandled so the new location is
        # still presented.
        if not self.lastInputEventWasCaretNavWithSelection() and oldString and not newString:
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
            and not settings_manager.getManager().getSetting('onlySpeakDisplayedText')
        text = obj.queryText()
        for start, end, message in changes:
            string = text.getText(start, end)
            endsWithChild = string.endswith(self.EMBEDDED_OBJECT_CHARACTER)
            if endsWithChild:
                end -= 1

            self._script.sayPhrase(obj, start, end)
            if speakMessage and not endsWithChild:
                self._script.speakMessage(message, interrupt=False)

            if endsWithChild:
                child = AXHypertext.get_child_at_offset(obj, end)
                self.handleTextSelectionChange(child, speakMessage)

        return True

    def _getCtrlShiftSelectionsStrings(self):
        """Hacky and to-be-obsoleted method."""
        return [messages.PARAGRAPH_SELECTED_DOWN,
                messages.PARAGRAPH_UNSELECTED_DOWN,
                messages.PARAGRAPH_SELECTED_UP,
                messages.PARAGRAPH_UNSELECTED_UP]

    def _speakTextSelectionState(self, nSelections):
        """Hacky and to-be-obsoleted method."""

        if settings_manager.getManager().getSetting('onlySpeakDisplayedText'):
            return False

        eventStr, mods = self.lastKeyAndModifiers()
        isControlKey = mods & keybindings.CTRL_MODIFIER_MASK
        isShiftKey = mods & keybindings.SHIFT_MODIFIER_MASK
        selectedText = nSelections > 0

        line = None
        if (eventStr == "Page_Down") and isShiftKey and isControlKey:
            line = messages.LINE_SELECTED_RIGHT
        elif (eventStr == "Page_Up") and isShiftKey and isControlKey:
            line = messages.LINE_SELECTED_LEFT
        elif (eventStr == "Page_Down") and isShiftKey and not isControlKey:
            if selectedText:
                line = messages.PAGE_SELECTED_DOWN
            else:
                line = messages.PAGE_UNSELECTED_DOWN
        elif (eventStr == "Page_Up") and isShiftKey and not isControlKey:
            if selectedText:
                line = messages.PAGE_SELECTED_UP
            else:
                line = messages.PAGE_UNSELECTED_UP
        elif (eventStr == "Down") and isShiftKey and isControlKey:
            strings = self._getCtrlShiftSelectionsStrings()
            if selectedText:
                line = strings[0]
            else:
                line = strings[1]
        elif (eventStr == "Up") and isShiftKey and isControlKey:
            strings = self._getCtrlShiftSelectionsStrings()
            if selectedText:
                line = strings[2]
            else:
                line = strings[3]
        elif (eventStr == "Home") and isShiftKey and isControlKey:
            if selectedText:
                line = messages.DOCUMENT_SELECTED_UP
            else:
                line = messages.DOCUMENT_UNSELECTED_UP
        elif (eventStr == "End") and isShiftKey and isControlKey:
            if selectedText:
                line = messages.DOCUMENT_SELECTED_DOWN
            else:
                line = messages.DOCUMENT_SELECTED_UP
        elif self.lastInputEventWasSelectAll() and selectedText:
            if not self._script.pointOfReference.get('entireDocumentSelected'):
                self._script.pointOfReference['entireDocumentSelected'] = True
                line = messages.DOCUMENT_SELECTED_ALL
            else:
                return True

        if not line:
            return False

        if line != self._script.pointOfReference.get('last-selection-message'):
            self._script.pointOfReference['last-selection-message'] = line
            self._script.speakMessage(line)

        return True

    def shouldInterruptForLocusOfFocusChange(self, oldLocusOfFocus, newLocusOfFocus, event=None):
        msg = "SCRIPT UTILITIES: Not interrupting for locusOfFocus change: "
        if event is None:
            msg += "event is None"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if event is not None and event.type.startswith("object:active-descendant-changed"):
            return self._script.stopSpeechOnActiveDescendantChanged(event)

        if AXUtilities.is_table_cell(oldLocusOfFocus) and AXUtilities.is_text(newLocusOfFocus) \
           and AXUtilities.is_editable(newLocusOfFocus):
            msg += "suspected editable cell"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not AXUtilities.is_menu_related(newLocusOfFocus) \
           and (AXUtilities.is_check_menu_item(oldLocusOfFocus) \
                or AXUtilities.is_radio_menu_item(oldLocusOfFocus)):
            msg += "suspected menuitem state change"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXObject.is_ancestor(newLocusOfFocus, oldLocusOfFocus):
            if AXObject.get_name(oldLocusOfFocus):
                msg += "old locusOfFocus is ancestor with name of new locusOfFocus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return False
            return True

        def isOld(target):
            return target == oldLocusOfFocus

        def isNew(target):
            return target == newLocusOfFocus

        if AXObject.get_relation_targets(newLocusOfFocus,
                                         Atspi.RelationType.CONTROLLER_FOR, isOld):
            msg += "new locusOfFocus controls old locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False
        if AXObject.get_relation_targets(oldLocusOfFocus,
                                         Atspi.RelationType.CONTROLLER_FOR, isNew):
            msg += "old locusOfFocus controls new locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False
        return True

    def stringsAreRedundant(self, str1, str2, threshold=0.5):
        if not (str1 and str2):
            return False

        similarity = round(SequenceMatcher(None, str1.lower(), str2.lower()).ratio(), 2)
        msg = (
            f"SCRIPT UTILITIES: Similarity between '{str1}', '{str2}': {similarity} "
            f"(threshold: {threshold})"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return similarity >= threshold
