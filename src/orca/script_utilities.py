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
import math
import pyatspi
import re
import subprocess
import time
from gi.repository import Gdk
from gi.repository import Gtk

from . import chnames
from . import colornames
from . import debug
from . import keynames
from . import keybindings
from . import input_event
from . import mathsymbols
from . import messages
from . import orca
from . import orca_state
from . import object_properties
from . import pronunciation_dict
from . import settings
from . import settings_manager
from . import text_attribute_names

_settingsManager = settings_manager.getManager()

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities:

    _desktop = pyatspi.Registry.getDesktop(0)

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    SUPERSCRIPT_DIGITS = \
        ['\u2070', '\u00b9', '\u00b2', '\u00b3', '\u2074',
         '\u2075', '\u2076', '\u2077', '\u2078', '\u2079']
    SUBSCRIPT_DIGITS = \
        ['\u2080', '\u2081', '\u2082', '\u2083', '\u2084',
         '\u2085', '\u2086', '\u2087', '\u2088', '\u2089']

    flags = re.UNICODE
    WORDS_RE = re.compile(r"(\W+)", flags)
    SUPERSCRIPTS_RE = re.compile("[%s]+" % "".join(SUPERSCRIPT_DIGITS), flags)
    SUBSCRIPTS_RE = re.compile("[%s]+" % "".join(SUBSCRIPT_DIGITS), flags)

    # generatorCache
    #
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

    def _isActiveAndShowingAndNotIconified(self, obj):
        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not state.contains(pyatspi.STATE_ACTIVE):
            return False

        if state.contains(pyatspi.STATE_ICONIFIED):
            return False

        return state.contains(pyatspi.STATE_SHOWING)

    @staticmethod
    def _getAppCommandLine(app):
        if not app:
            return ""

        pid = app.get_process_id()

        try:
            cmdline = subprocess.getoutput("cat /proc/%s/cmdline" % pid)
        except:
            return ""

        return cmdline.replace("\x00", " ")

    def canBeActiveWindow(self, window):
        if not window:
            return False

        try:
            app = window.getApplication()
        except:
            app = None

        msg = "INFO: Looking at %s from %s %s" % (window, app, self._getAppCommandLine(app))
        debug.println(debug.LEVEL_INFO, msg, True)

        window.clearCache()
        if not self._isActiveAndShowingAndNotIconified(window):
            msg = "INFO: %s is not active and showing, or is iconified" % window
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = "INFO: %s can be active window" % window
        debug.println(debug.LEVEL_INFO, msg, True)
        return True

    def activeWindow(self, *apps):
        """Tries to locate the active window; may or may not succeed."""

        candidates = []
        apps = apps or self.knownApplications()
        for app in apps:
            try:
                candidates.extend([child for child in app if self.canBeActiveWindow(child)])
            except:
                msg = "ERROR: Exception examining children of %s" % app
                debug.println(debug.LEVEL_INFO, msg, True)

        if not candidates:
            msg = "ERROR: Unable to find active window from %s" % list(map(str, apps))
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if len(candidates) == 1:
            msg = "INFO: Active window is %s" % candidates[0]
            debug.println(debug.LEVEL_INFO, msg, True)
            return candidates[0]

        # Sorting by size in a lame attempt to filter out the "desktop" frame of various
        # desktop environments. App name won't work because we don't know it. Getting the
        # screen/desktop size via Gdk risks a segfault depending on the user environment.
        # Asking AT-SPI2 for the size seems to give us 1024x768 regardless of reality....
        # This is why we can't have nice things.
        candidates = sorted(candidates, key=functools.cmp_to_key(self.sizeComparison))
        msg = "WARNING: These windows all claim to be active: %s" % list(map(str, candidates))
        debug.println(debug.LEVEL_INFO, msg, True)

        msg = "INFO: Active window is (hopefully) %s" % candidates[0]
        debug.println(debug.LEVEL_INFO, msg, True)
        return candidates[0]

    @staticmethod
    def ancestorWithRole(obj, ancestorRoles, stopRoles):
        """Returns the object of the specified roles which contains the
        given object, or None if the given object is not contained within
        an object the specified roles.

        Arguments:
        - obj: the Accessible object
        - ancestorRoles: the list of roles to look for
        - stopRoles: the list of roles to stop the search at
        """

        if not obj:
            return None

        if not isinstance(ancestorRoles, [].__class__):
            ancestorRoles = [ancestorRoles]

        if not isinstance(stopRoles, [].__class__):
            stopRoles = [stopRoles]

        ancestor = None

        obj = obj.parent
        while obj and (obj != obj.parent):
            try:
                role = obj.getRole()
            except:
                break
            if role in ancestorRoles:
                ancestor = obj
                break
            elif role in stopRoles:
                break
            else:
                obj = obj.parent

        return ancestor

    def cellIndex(self, obj):
        """Returns the index of the cell which should be used with the
        table interface.  This is necessary because in some apps we
        cannot count on getIndexInParent() returning the index we need.

        Arguments:
        -obj: the table cell whose index we need.
        """

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}

        index = attrs.get('table-cell-index')
        if index:
            return int(index)

        return obj.getIndexInParent()

    def childNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell.

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

        try:
            table = obj.parent.queryTable()
        except:
            return []
        else:
            if not obj.getState().contains(pyatspi.STATE_EXPANDED):
                return []

        nodes = []

        # First see if this accessible implements RELATION_NODE_PARENT_OF.
        # If it does, the full target list are the nodes. If it doesn't
        # we'll do an old-school, row-by-row search for child nodes.
        #
        relations = obj.getRelationSet()
        try:
            for relation in relations:
                if relation.getRelationType() == \
                        pyatspi.RELATION_NODE_PARENT_OF:
                    for target in range(relation.getNTargets()):
                        node = relation.getTarget(target)
                        if node and node.getIndexInParent() != -1:
                            nodes.append(node)
                    return nodes
        except:
            pass

        index = self.cellIndex(obj)
        row = table.getRowAtIndex(index)
        col = table.getColumnAtIndex(index)
        nodeLevel = self.nodeLevel(obj)
        done = False

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        for i in range(row+1, table.nRows):
            cell = table.getAccessibleAt(i, col)
            if not cell:
                continue
            relations = cell.getRelationSet()
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_NODE_CHILD_OF:
                    nodeOf = relation.getTarget(0)
                    if self.isSameObject(obj, nodeOf):
                        nodes.append(cell)
                    else:
                        currentLevel = self.nodeLevel(nodeOf)
                        if currentLevel <= nodeLevel:
                            done = True
                    break
            if done:
                break

        return nodes

    def commonAncestor(self, a, b):
        """Finds the common ancestor between Accessible a and Accessible b.

        Arguments:
        - a: Accessible
        - b: Accessible
        """

        msg = 'INFO: Looking for common ancestor of %s and %s' % (a, b)
        debug.println(debug.LEVEL_INFO, msg, True)

        # Don't do any Zombie checks here, as tempting and logical as it
        # may seem as it can lead to chattiness.
        if not (a and b):
            return None

        if a == b:
            return a

        aParents = [a]
        try:
            parent = a.parent
            while parent and (parent.parent != parent):
                aParents.append(parent)
                parent = parent.parent
            aParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)

        bParents = [b]
        try:
            parent = b.parent
            while parent and (parent.parent != parent):
                bParents.append(parent)
                parent = parent.parent
            bParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)

        commonAncestor = None

        maxSearch = min(len(aParents), len(bParents))
        i = 0
        while i < maxSearch:
            if self.isSameObject(aParents[i], bParents[i]):
                commonAncestor = aParents[i]
                i += 1
            else:
                break

        msg = 'INFO: Common ancestor of %s and %s is %s' % (a, b, commonAncestor)
        debug.println(debug.LEVEL_INFO, msg, True)
        return commonAncestor

    def defaultButton(self, obj):
        """Returns the default button in the dialog which contains obj.

        Arguments:
        - obj: the top-level object (e.g. window, frame, dialog) for
          which the status bar is sought.
        """

        # There are some objects which are not worth descending.
        #
        skipRoles = [pyatspi.ROLE_TREE,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_TABLE]

        if obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or obj.getRole() in skipRoles:
            return

        defaultButton = None
        # The default button is likely near the bottom of the window.
        #
        for i in range(obj.childCount - 1, -1, -1):
            if obj[i].getRole() == pyatspi.ROLE_PUSH_BUTTON \
                and obj[i].getState().contains(pyatspi.STATE_IS_DEFAULT):
                defaultButton = obj[i]
            elif not obj[i].getRole() in skipRoles:
                defaultButton = self.defaultButton(obj[i])

            if defaultButton:
                break

        return defaultButton

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
        except:
            if self.DISPLAYED_LABEL not in self._script.generatorCache:
                self._script.generatorCache[self.DISPLAYED_LABEL] = {}
            labelString = None

        labels = self.labelsForObject(obj)
        for label in labels:
            labelString = \
                self.appendString(labelString, self.displayedText(label))

        self._script.generatorCache[self.DISPLAYED_LABEL][obj] = labelString
        return self._script.generatorCache[self.DISPLAYED_LABEL][obj]

    def displayedText(self, obj):
        """Returns the text being displayed for an object.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        try:
            return self._script.generatorCache[self.DISPLAYED_TEXT][obj]
        except:
            displayedText = None

        try:
            role = obj.getRole()
            name = obj.name
        except:
            msg = 'ERROR: Exception getting role and name of %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            role = None
            name = ''

        if role == pyatspi.ROLE_PUSH_BUTTON and name:
            return name

        try:
            text = obj.queryText()
            displayedText = text.getText(0, text.characterCount)
        except:
            pass
        else:
            if self.EMBEDDED_OBJECT_CHARACTER in displayedText:
                displayedText = None

        if not displayedText:
            # TODO - JD: This should probably get nuked. But all sorts of
            # existing code might be relying upon this bogus hack. So it
            # will need thorough testing when removed.
            try:
                displayedText = obj.name
            except (LookupError, RuntimeError):
                pass

        if not displayedText and role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_LIST_ITEM]:
            labels = self.unrelatedLabels(obj)
            if not labels:
                labels = self.unrelatedLabels(obj, onlyShowing=False)
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
        docRoles = [pyatspi.ROLE_DOCUMENT_EMAIL,
                    pyatspi.ROLE_DOCUMENT_FRAME,
                    pyatspi.ROLE_DOCUMENT_PRESENTATION,
                    pyatspi.ROLE_DOCUMENT_SPREADSHEET,
                    pyatspi.ROLE_DOCUMENT_TEXT,
                    pyatspi.ROLE_DOCUMENT_WEB]
        stopRoles = [pyatspi.ROLE_FRAME, pyatspi.ROLE_SCROLL_PANE]
        document = self.ancestorWithRole(obj, docRoles, stopRoles)
        if not document and orca_state.locusOfFocus:
            if orca_state.locusOfFocus.getRole() in docRoles:
                return orca_state.locusOfFocus

        return document

    def documentFrameURI(self):
        """Returns the URI of the document frame that is active."""

        return None

    @staticmethod
    def focusedObject(root):
        """Returns the accessible that has focus under or including the
        given root.

        TODO: This will currently traverse all children, whether they are
        visible or not and/or whether they are children of parents that
        manage their descendants.  At some point, this method should be
        optimized to take such things into account.

        Arguments:
        - root: the root object where to start searching

        Returns the object with the FOCUSED state or None if no object with
        the FOCUSED state can be found.
        """

        if not root:
            return None

        if root.getState().contains(pyatspi.STATE_FOCUSED):
            return root

        for child in root:
            try:
                candidate = Utilities.focusedObject(child)
                if candidate:
                    return candidate
            except:
                pass

        return None

    def frameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing obj."""

        results = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.getRole() == pyatspi.ROLE_FRAME:
                results[0] = parent
            if parent.getRole() in [pyatspi.ROLE_DIALOG,
                                    pyatspi.ROLE_FILE_CHOOSER]:
                results[1] = parent
            parent = parent.parent

        return results

    def presentEventFromNonShowingObject(self, event):
        return False

    def grabFocusBeforeRouting(self, obj, offset):
        """Whether or not we should perform a grabFocus before routing
        the cursor via the braille cursor routing keys.

        Arguments:
        - obj: the accessible object where the cursor should be routed
        - offset: the offset to which it should be routed

        Returns True if we should do an explicit grabFocus on obj prior
        to routing the cursor.
        """

        if obj and obj.getRole() == pyatspi.ROLE_COMBO_BOX \
           and not self.isSameObject(obj, orca_state.locusOfFocus):
            return True

        return False

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

            try:
                if isinstance(role[0], str):
                    current_role = current.getRoleName()
                else:
                    current_role = current.getRole()
            except:
                current_role = None

            if not current_role in role:
                return False

            current = self.validParent(current)

        return True

    def inFindToolbar(self, obj=None):
        """Returns True if the given object is in the Find toolbar.

        Arguments:
        - obj: an accessible object
        """

        if not obj:
            obj = orca_state.locusOfFocus

        try:
            role = obj.getRole()
        except:
            return False

        if role != pyatspi.ROLE_ENTRY:
            return False

        isToolbar = lambda x: x and x.getRole() == pyatspi.ROLE_TOOL_BAR
        toolbar = pyatspi.findAncestor(obj, isToolbar)

        return toolbar is not None

    def isAnchor(self, obj):
        return False

    def isComboBoxWithToggleDescendant(self, obj):
        return False

    def isToggleDescendantOfComboBox(self, obj):
        return False

    def isTypeahead(self, obj):
        return False

    def isFunctionalDialog(self, obj):
        """Returns True if the window is a functioning as a dialog.
        This method should be subclassed by application scripts as
        needed.
        """

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

    def isFigure(self, obj):
        return False

    def isLandmark(self, obj):
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
        if not (obj and obj.getRole() == pyatspi.ROLE_PROGRESS_BAR):
            return False

        try:
            value = obj.queryValue()
        except NotImplementedError:
            msg = "ERROR: %s doesn't implement AtspiValue" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        except:
            msg = "ERROR: Exception getting value for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        else:
            try:
                if value.maximumValue == value.minimumValue:
                    msg = "INFO: %s is busy indicator" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return False
            except:
                msg = "INFO: %s is either busy indicator or broken" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

        return True

    def isProgressBarUpdate(self, obj, event):
        if not _settingsManager.getSetting('speakProgressBarUpdates') \
           and not _settingsManager.getSetting('brailleProgressBarUpdates') \
           and not _settingsManager.getSetting('beepProgressBarUpdates'):
            return False, "Updates not enabled"

        if not self.isProgressBar(obj):
            return False, "Is not progress bar"

        if self.hasNoSize(obj):
            return False, "Has no size"

        if _settingsManager.getSetting('ignoreStatusBarProgressBars'):
            isStatusBar = lambda x: x and x.getRole() == pyatspi.ROLE_STATUS_BAR
            if pyatspi.findAncestor(obj, isStatusBar):
                return False, "Is status bar descendant"

        verbosity = _settingsManager.getSetting('progressBarVerbosity')
        if verbosity == settings.PROGRESS_BAR_ALL:
            return True, "Verbosity is all"

        if verbosity == settings.PROGRESS_BAR_WINDOW:
            topLevel = self.topLevelObject(obj)
            if topLevel == orca_state.activeWindow:
                return True, "Verbosity is window"
            return False, "Window %s is not %s" % (topLevel, orca_state.activeWindow)

        if verbosity == settings.PROGRESS_BAR_APPLICATION:
            if event:
                app = event.host_application
            else:
                app = obj.getApplication()
            if app == orca_state.activeScript.app:
                return True, "Verbosity is app"
            return False, "App %s is not %s" % (app, orca_state.activeScript.app)

        return True, "Not handled by any other case"

    def getValueAsPercent(self, obj):
        try:
            value = obj.queryValue()
            minval, val, maxval =  value.minimumValue, value.currentValue, value.maximumValue
        except NotImplementedError:
            msg = "ERROR: %s doesn't implement AtspiValue" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None
        except:
            msg = "ERROR: Exception getting value for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if maxval == minval == val:
            if 1 <= val <= 100:
                return int(val)
            return None

        return int((val / (maxval - minval)) * 100)

    def isBlockquote(self, obj):
        return obj and obj.getRole() == pyatspi.ROLE_BLOCK_QUOTE

    def isDocumentList(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_LIST):
            return False

        try:
            document = pyatspi.findAncestor(obj, self.isDocument)
        except:
            msg = "ERROR: Exception finding ancestor of %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            return False

        return document is not None

    def isDocumentPanel(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_PANEL):
            return False

        try:
            document = pyatspi.findAncestor(obj, self.isDocument)
        except:
            msg = "ERROR: Exception finding ancestor of %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            return False

        return document is not None

    def isDocument(self, obj):
        documentRoles = [pyatspi.ROLE_DOCUMENT_EMAIL,
                         pyatspi.ROLE_DOCUMENT_FRAME,
                         pyatspi.ROLE_DOCUMENT_PRESENTATION,
                         pyatspi.ROLE_DOCUMENT_SPREADSHEET,
                         pyatspi.ROLE_DOCUMENT_TEXT,
                         pyatspi.ROLE_DOCUMENT_WEB]
        return obj and obj.getRole() in documentRoles

    def inDocumentContent(self, obj=None):
        obj = obj or orca_state.locusOfFocus
        return self.getContainingDocument(obj) is not None

    def getContainingDocument(self, obj):
        if not obj:
            return None

        try:
            doc = pyatspi.findAncestor(obj, self.isDocument)
        except:
            msg = "ERROR: Exception finding ancestor of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        msg = "INFO: Document containing %s is %s" % (obj, doc)
        debug.println(debug.LEVEL_INFO, msg, True)
        return doc

    def getTable(self, obj):
        if not obj:
            return None

        tableRoles = [pyatspi.ROLE_TABLE, pyatspi.ROLE_TREE_TABLE]
        isTable = lambda x: x and x.getRole() in tableRoles
        if isTable(obj):
            return obj

        try:
            table = pyatspi.findAncestor(obj, isTable)
        except:
            msg = "ERROR: Exception finding ancestor of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return table

    def isTextDocumentTable(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE):
            return False

        doc = self.getContainingDocument(obj)
        if not doc:
            return False

        return doc.getRole() != pyatspi.ROLE_DOCUMENT_SPREADSHEET

    def isGUITable(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE):
            return False

        return self.getContainingDocument(obj) is None

    def isSpreadSheetTable(self, obj):
        if not obj:
            return False

        try:
            role = obj.getRole()
        except:
            msg = 'ERROR: Exception getting role of %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not role == pyatspi.ROLE_TABLE:
            return False

        doc = self.getContainingDocument(obj)
        if not doc:
            return False

        if doc.getRole() == pyatspi.ROLE_DOCUMENT_SPREADSHEET:
            return True

        try:
            table = obj.queryTable()
        except NotImplementedError:
            msg = 'ERROR: Table %s does not implement table interface' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = 'ERROR: Exception querying table interface of %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            return table.nRows > 65536

        return False

    def isTextDocumentCell(self, obj):
        if not obj:
            return False

        try:
            role = obj.getRole()
        except:
            msg = 'ERROR: Exception getting role of %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        cellRoles = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_COLUMN_HEADER,
                     pyatspi.ROLE_ROW_HEADER]
        if not role in cellRoles:
            return False

        return pyatspi.findAncestor(obj, self.isTextDocumentTable)

    def isSpreadSheetCell(self, obj):
        if not obj:
            return False

        try:
            role = obj.getRole()
        except:
            msg = 'ERROR: Exception getting role of %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        cellRoles = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_COLUMN_HEADER,
                     pyatspi.ROLE_ROW_HEADER]
        if not role in cellRoles:
            return False

        return pyatspi.findAncestor(obj, self.isSpreadSheetTable)

    def cellColumnChanged(self, cell):
        row, column = self.coordinatesForCell(cell)
        if column == -1:
            return False

        lastColumn = self._script.pointOfReference.get("lastColumn")
        return column != lastColumn

    def cellRowChanged(self, cell):
        row, column = self.coordinatesForCell(cell)
        if row == -1:
            return False

        lastRow = self._script.pointOfReference.get("lastRow")
        return row != lastRow

    def shouldReadFullRow(self, obj):
        if self._script.inSayAll():
            return False

        table = self.getTable(obj)
        if not table:
            return False

        if not self.getContainingDocument(table):
            return _settingsManager.getSetting('readFullRowInGUITable')

        if self.isSpreadSheetTable(table):
            return _settingsManager.getSetting('readFullRowInSpreadSheet')

        return _settingsManager.getSetting('readFullRowInDocumentTable')

    def isFocusableLabel(self, obj):
        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            return False

        if role != pyatspi.ROLE_LABEL:
            return False

        if state.contains(pyatspi.STATE_FOCUSABLE):
            return True

        if state.contains(pyatspi.STATE_FOCUSED):
            msg = 'INFO: %s is focused but lacks state focusable' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def isNonFocusableList(self, obj):
        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            return False

        if role != pyatspi.ROLE_LIST:
            return False

        if state.contains(pyatspi.STATE_FOCUSABLE):
            return False

        if state.contains(pyatspi.STATE_FOCUSED):
            msg = 'INFO: %s is focused but lacks state focusable' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def isStatusBarNotification(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_NOTIFICATION):
            return False

        isStatusBar = lambda x: x and x.getRole() == pyatspi.ROLE_STATUS_BAR
        if pyatspi.findAncestor(obj, isStatusBar):
            return True

        return False

    def isTreeDescendant(self, obj):
        if not obj:
            return False

        if obj.getRole() == pyatspi.ROLE_TREE_ITEM:
            return True

        isTree = lambda x: x and x.getRole() in [pyatspi.ROLE_TREE, pyatspi.ROLE_TREE_TABLE]
        if pyatspi.findAncestor(obj, isTree):
            return True

        return False

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a container which has
        no presentable information (label, name, displayed text, etc.)."""

        layoutOnly = False

        if self.isDead(obj) or self.isZombie(obj):
            return True

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}
        try:
            role = obj.getRole()
        except:
            role = None

        try:
            parentRole = obj.parent.getRole()
        except:
            parentRole = None

        try:
            firstChild = obj[0]
        except:
            firstChild = None

        topLevelRoles = self._topLevelRoles()
        ignorePanelParent = [pyatspi.ROLE_MENU,
                             pyatspi.ROLE_MENU_ITEM,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_TREE_ITEM]

        if role == pyatspi.ROLE_TABLE and attrs.get('layout-guess') != 'true':
            try:
                table = obj.queryTable()
            except NotImplementedError:
                msg = 'ERROR: Table %s does not implement table interface' % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                layoutOnly = True
            except:
                msg = 'ERROR: Exception querying table interface of %s' % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                layoutOnly = True
            else:
                if not (table.nRows and table.nColumns):
                    layoutOnly = not obj.getState().contains(pyatspi.STATE_FOCUSED)
                elif not (obj.name or self.displayedLabel(obj)):
                    layoutOnly = not (table.getColumnHeader(0) or table.getRowHeader(0))
        elif role == pyatspi.ROLE_TABLE_CELL and obj.childCount:
            if parentRole == pyatspi.ROLE_TREE_TABLE:
                layoutOnly = False
            elif firstChild.getRole() == pyatspi.ROLE_TABLE_CELL:
                layoutOnly = True
            elif parentRole == pyatspi.ROLE_TABLE:
                layoutOnly = self.isLayoutOnly(obj.parent)
        elif role == pyatspi.ROLE_SECTION:
            layoutOnly = not self.isBlockquote(obj)
        elif role == pyatspi.ROLE_FILLER:
            layoutOnly = True
        elif role == pyatspi.ROLE_SCROLL_PANE:
            layoutOnly = True
        elif role == pyatspi.ROLE_AUTOCOMPLETE:
            layoutOnly = True
        elif role in [pyatspi.ROLE_TEAROFF_MENU_ITEM, pyatspi.ROLE_SEPARATOR]:
            layoutOnly = True
        elif role in [pyatspi.ROLE_LIST_BOX, pyatspi.ROLE_TREE_TABLE]:
            layoutOnly = False
        elif role in topLevelRoles:
            layoutOnly = False
        elif role == pyatspi.ROLE_MENU:
            layoutOnly = parentRole == pyatspi.ROLE_COMBO_BOX
        elif role == pyatspi.ROLE_COMBO_BOX:
            layoutOnly = False
        elif role == pyatspi.ROLE_LIST:
            layoutOnly = False
        elif role == pyatspi.ROLE_FORM:
            layoutOnly = False
        elif role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_TOGGLE_BUTTON]:
            layoutOnly = False
        elif role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_PASSWORD_TEXT, pyatspi.ROLE_ENTRY]:
            layoutOnly = False
        elif role == pyatspi.ROLE_LIST_ITEM and parentRole == pyatspi.ROLE_LIST_BOX:
            layoutOnly = False
        elif self.isTableRow(obj):
            state = obj.getState()
            layoutOnly = not (state.contains(pyatspi.STATE_FOCUSABLE) \
                              or state.contains(pyatspi.STATE_SELECTABLE))
        elif role == pyatspi.ROLE_PANEL and obj.childCount and firstChild \
             and firstChild.getRole() in ignorePanelParent:
            layoutOnly = True
        elif obj.childCount == 1 and obj.name and obj.name == firstChild.name:
            layoutOnly = True
        elif self.isHidden(obj):
            layoutOnly = True
        else:
            if not (self.displayedText(obj) or self.displayedLabel(obj)):
                layoutOnly = True

        if layoutOnly:
            msg = 'INFO: %s is deemed to be layout only' % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        return layoutOnly

    @staticmethod
    def isInActiveApp(obj):
        """Returns True if the given object is from the same application that
        currently has keyboard focus.

        Arguments:
        - obj: an Accessible object
        """

        if not obj or not orca_state.locusOfFocus:
            return False

        return orca_state.locusOfFocus.getApplication() == obj.getApplication()

    def isLink(self, obj):
        """Returns True if obj is a link."""

        if not obj:
            return False

        try:
            role = obj.getRole()
        except (LookupError, RuntimeError):
            msg = 'ERROR: Exception getting role for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return role == pyatspi.ROLE_LINK

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""

        if not self.isTextArea(obj):
            return False

        state = obj.getState()
        readOnly = state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        return readOnly

    def isSwitch(self, obj):
        return False

    def _hasSamePath(self, obj1, obj2):
        path1 = pyatspi.utils.getPath(obj1)
        path2 = pyatspi.utils.getPath(obj2)
        if len(path1) != len(path2):
            return False

        # The first item in all paths, even valid ones, is -1.
        path1 = path1[1:]
        path2 = path2[1:]

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

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False):
        if (obj1 == obj2):
            return True
        elif (not obj1) or (not obj2):
            return False

        try:
            if obj1.getRole() != obj2.getRole():
                return False
            if obj1.name != obj2.name and not ignoreNames:
                return False
            if comparePaths and self._hasSamePath(obj1, obj2):
                return True
            else:
                # Comparing the extents of objects which claim to be different
                # addresses both managed descendants and implementations which
                # recreate accessibles for the same widget.
                extents1 = \
                    obj1.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                extents2 = \
                    obj2.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)

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
        except:
            pass

        return False

    def isTextArea(self, obj):
        """Returns True if obj is a GUI component that is for entering text.

        Arguments:
        - obj: an accessible
        """

        if self.isLink(obj):
            return False

        return obj and obj.getRole() in (pyatspi.ROLE_TEXT,
                                         pyatspi.ROLE_ENTRY,
                                         pyatspi.ROLE_PARAGRAPH)

    @staticmethod
    def knownApplications():
        """Retrieves the list of currently running apps for the desktop
        as a list of Accessible objects.
        """

        return [x for x in Utilities._desktop if x is not None]

    def labelsForObject(self, obj):
        """Return a list of the objects that are labelling this object.

        Argument:
        - obj: the object in question

        Returns a list of the objects that are labelling this object.
        """

        # For some reason, some objects are labelled by the same thing
        # more than once.  Go figure, but we need to check for this.
        #
        label = []
        try:
            relations = obj.getRelationSet()
        except (LookupError, RuntimeError):
            msg = 'ERROR: Exception getting relationset for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return label

        allTargets = []
        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_LABELLED_BY:

                # The object can be labelled by more than one thing, so we just
                # get all the labels (from unique objects) and append them
                # together.  An example of such objects live in the "Basic"
                # page of the gnome-accessibility-keyboard-properties app.
                # The "Delay" and "Speed" objects are labelled both by
                # their names and units.
                #
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    if not target in allTargets:
                        allTargets.append(target)
                        label.append(target)
        return label

    @staticmethod
    def linkBasename(obj):
        """Returns the relevant information from the URI.  The idea is
        to attempt to strip off all prefix and suffix, much like the
        basename command in a shell."""

        basename = None

        try:
            hyperlink = obj.queryHyperlink()
        except:
            pass
        else:
            uri = hyperlink.getURI(0)
            if uri and len(uri):
                # Sometimes the URI is an expression that includes a URL.
                # Currently that can be found at the bottom of safeway.com.
                # It can also be seen in the backwards.html test file.
                #
                expression = uri.split(',')
                if len(expression) > 1:
                    for item in expression:
                        if item.find('://') >=0:
                            if not item[0].isalnum():
                                item = item[1:-1]
                            if not item[-1].isalnum():
                                item = item[0:-2]
                            uri = item
                            break

                # We're assuming that there IS a base name to be had.
                # What if there's not? See backwards.html.
                #
                uri = uri.split('://')[-1]
                if not uri:
                    return basename

                # Get the last thing after all the /'s, unless it ends
                # in a /.  If it ends in a /, we'll look to the stuff
                # before the ending /.
                #
                if uri[-1] == "/":
                    basename = uri[0:-1]
                    basename = basename.split('/')[-1]
                elif not uri.count("/"):
                    basename = uri
                else:
                    basename = uri.split('/')[-1]
                    if basename.startswith("index"):
                        basename = uri.split('/')[-2]

                    # Now, try to strip off the suffixes.
                    #
                    basename = basename.split('.')[0]
                    basename = basename.split('?')[0]
                    basename = basename.split('#')[0]
                    basename = basename.split('%')[0]

        return basename

    @staticmethod
    def linkIndex(obj, characterIndex):
        """A brute force method to see if an offset is a link.  This
        is provided because not all Accessible Hypertext implementations
        properly support the getLinkIndex method.  Returns an index of
        0 or greater of the characterIndex is on a hyperlink.

        Arguments:
        -obj: the object with the Accessible Hypertext specialization
        -characterIndex: the text position to check
        """

        if not obj:
            return -1

        try:
            obj.queryText()
        except NotImplementedError:
            return -1

        try:
            hypertext = obj.queryHypertext()
        except NotImplementedError:
            return -1

        for i in range(hypertext.getNLinks()):
            link = hypertext.getLink(i)
            if (characterIndex >= link.startIndex) \
               and (characterIndex <= link.endIndex):
                return i

        return -1

    def nestingLevel(self, obj):
        """Determines the nesting level of this object.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return 0

        try:
            return self._script.generatorCache[self.NESTING_LEVEL][obj]
        except:
            if self.NESTING_LEVEL not in self._script.generatorCache:
                self._script.generatorCache[self.NESTING_LEVEL] = {}

        if self.isBlockquote(obj):
            pred = lambda x: self.isBlockquote(x)
        elif obj.getRole() == pyatspi.ROLE_LIST_ITEM:
            pred = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_LIST
        else:
            role = obj.getRole()
            pred = lambda x: x and x.getRole() == role

        ancestors = []
        ancestor = pyatspi.findAncestor(obj, pred)
        while ancestor:
            ancestors.append(ancestor)
            ancestor = pyatspi.findAncestor(ancestor, pred)

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
        except:
            if self.NODE_LEVEL not in self._script.generatorCache:
                self._script.generatorCache[self.NODE_LEVEL] = {}

        nodes = []
        node = obj
        done = False
        while not done:
            try:
                relations = node.getRelationSet()
            except (LookupError, RuntimeError):
                msg = 'ERROR: Exception getting relationset for %s' % node
                debug.println(debug.LEVEL_INFO, msg, True)
                return -1
            node = None
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_NODE_CHILD_OF:
                    node = relation.getTarget(0)
                    break

            # We want to avoid situations where something gives us an
            # infinite cycle of nodes.  Bon Echo has been seen to do
            # this (see bug 351847).
            if nodes.count(node):
                msg = 'ERROR: %s is already in the list of nodes for %s' % (node, obj)
                debug.println(debug.LEVEL_INFO, msg, True)
                done = True
            if len(nodes) > 100:
                msg = 'INFO: More than 100 nodes found for %s' % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                done = True
            elif node:
                nodes.append(node)
            else:
                done = True

        self._script.generatorCache[self.NODE_LEVEL][obj] = len(nodes) - 1
        return self._script.generatorCache[self.NODE_LEVEL][obj]

    def isOnScreen(self, obj, boundingbox=None):
        if self.isDead(obj):
            return False

        if self.isHidden(obj):
            return False

        if not self.isShowingAndVisible(obj):
            msg = "INFO: %s is not showing and visible" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        try:
            box = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
        except:
            msg = "ERROR: Exception getting extents for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if box.x < 0 and box.y < 0:
            msg = "INFO: %s has negative coordinates" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not (box.width or box.height):
            if not obj.childCount:
                msg = "INFO: %s has no size and no children" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return False
            if obj.getRole() == pyatspi.ROLE_MENU:
                msg = "INFO: %s has no size" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

            return True

        if boundingbox is None or not self._boundsIncludeChildren(obj.parent):
            return True

        if not self.containsRegion(box, boundingbox):
            msg = "INFO: %s %s not in %s" % (obj, box, boundingbox)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def selectedMenuBarMenu(self, menubar):
        try:
            role = menubar.getRole()
        except:
            msg = "ERROR: Exception getting role of %s" % menubar
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if role != pyatspi.ROLE_MENU_BAR:
            return None

        if "Selection" in pyatspi.listInterfaces(menubar):
            selected = self.selectedChildren(menubar)
            if selected:
                return selected[0]
            return None

        for menu in menubar:
            try:
                menu.clearCache()
                state = menu.getState()
            except:
                msg = "ERROR: Exception getting state of %s" % menu
                debug.println(debug.LEVEL_INFO, msg, True)
                continue

            if state.contains(pyatspi.STATE_EXPANDED) \
               or state.contains(pyatspi.STATE_SELECTED):
                return menu

        return None

    def isInOpenMenuBarMenu(self, obj):
        if not obj:
            return False

        isMenuBar = lambda x: x and x.getRole() == pyatspi.ROLE_MENU_BAR
        menubar = pyatspi.findAncestor(obj, isMenuBar)
        if menubar is None:
            return False

        selectedMenu = self._selectedMenuBarMenu.get(hash(menubar))
        if selectedMenu is None:
            selectedMenu = self.selectedMenuBarMenu(menubar)

        if not selectedMenu:
            return False

        inSelectedMenu = lambda x: x == selectedMenu
        if inSelectedMenu(obj):
            return True

        return pyatspi.findAncestor(obj, inSelectedMenu) is not None

    def getOnScreenObjects(self, root, extents=None):
        if not self.isOnScreen(root, extents):
            return []

        try:
            role = root.getRole()
        except:
            msg = "ERROR: Exception getting role of %s" % root
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        if role == pyatspi.ROLE_INVALID:
            return []

        if role == pyatspi.ROLE_COMBO_BOX:
            return [root]

        if role == pyatspi.ROLE_MENU_BAR:
            self._selectedMenuBarMenu[hash(root)] = self.selectedMenuBarMenu(root)

        if root.parent and root.parent.getRole() == pyatspi.ROLE_MENU_BAR \
           and not self.isInOpenMenuBarMenu(root):
            return [root]

        if extents is None:
            try:
                component = root.queryComponent()
                extents = component.getExtents(pyatspi.DESKTOP_COORDS)
            except:
                msg = "ERROR: Exception getting extents of %s" % root
                debug.println(debug.LEVEL_INFO, msg, True)
                extents = 0, 0, 0, 0

        interfaces = pyatspi.listInterfaces(root)
        if 'Table' in interfaces and 'Selection' in interfaces:
            visibleCells = self.getVisibleTableCells(root)
            if visibleCells:
                return visibleCells

        nonText = [pyatspi.ROLE_STATUS_BAR, pyatspi.ROLE_UNKNOWN]
        objects = []
        if (role == pyatspi.ROLE_PAGE_TAB and root.name) \
           or (role not in nonText and "Text" in pyatspi.listInterfaces(root)):
            objects.append(root)

        for child in root:
            objects.extend(self.getOnScreenObjects(child, extents))

        if role == pyatspi.ROLE_MENU_BAR:
            self._selectedMenuBarMenu[hash(root)] = None

        if objects:
            return objects

        containers = [pyatspi.ROLE_FILLER,
                      pyatspi.ROLE_LIST_BOX,
                      pyatspi.ROLE_PANEL,
                      pyatspi.ROLE_SCROLL_PANE,
                      pyatspi.ROLE_VIEWPORT]
        if role in containers:
            return []

        return [root]

    @staticmethod
    def isTableRow(obj):
        """Determines if obj is a table row -- real or functionally."""

        try:
            if not (obj and obj.parent and obj.childCount):
                return False
        except:
            msg = "ERROR: Exception getting parent and childCount for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        role = obj.getRole()
        if role == pyatspi.ROLE_TABLE_ROW:
            return True

        if role == pyatspi.ROLE_TABLE_CELL:
            return False

        if not obj.parent.getRole() == pyatspi.ROLE_TABLE:
            return False

        isCell = lambda x: x and x.getRole() in [pyatspi.ROLE_TABLE_CELL,
                                                 pyatspi.ROLE_ROW_HEADER,
                                                 pyatspi.ROLE_COLUMN_HEADER]
        cellChildren = list(filter(isCell, [x for x in obj]))
        if len(cellChildren) == obj.childCount:
            return True        

        return False

    def realActiveAncestor(self, obj):
        if obj.getState().contains(pyatspi.STATE_FOCUSED):
            return obj

        roles = [pyatspi.ROLE_TABLE_CELL,
                 pyatspi.ROLE_COLUMN_HEADER,
                 pyatspi.ROLE_ROW_HEADER,
                 pyatspi.ROLE_LIST_ITEM]

        ancestor = pyatspi.findAncestor(obj, lambda x: x and x.getRole() in roles)
        if ancestor and not self._script.utilities.isLayoutOnly(ancestor.parent):
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

        if self.isDead(obj):
            return None

        if obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            return obj

        hasContent = [x for x in obj if self.displayedText(x).strip()]
        if len(hasContent) == 1:
            return hasContent[0]

        return obj

    def statusBar(self, obj):
        """Returns the status bar in the window which contains obj.

        Arguments:
        - obj: the top-level object (e.g. window, frame, dialog) for which
          the status bar is sought.
        """

        # There are some objects which are not worth descending.
        #
        skipRoles = [pyatspi.ROLE_TREE,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_TABLE]

        if obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or obj.getRole() in skipRoles:
            return

        statusBar = None
        # The status bar is likely near the bottom of the window.
        #
        for i in range(obj.childCount - 1, -1, -1):
            if obj[i].getRole() == pyatspi.ROLE_STATUS_BAR:
                statusBar = obj[i]
            elif not obj[i].getRole() in skipRoles:
                statusBar = self.statusBar(obj[i])

            if statusBar:
                break

        return statusBar

    def infoBar(self, root):
        return None

    def _topLevelRoles(self):
        return [pyatspi.ROLE_ALERT,
                pyatspi.ROLE_DIALOG,
                pyatspi.ROLE_FRAME,
                pyatspi.ROLE_WINDOW]

    def _locusOfFocusIsTopLevelObject(self):
        if not orca_state.locusOfFocus:
            return False

        try:
            role = orca_state.locusOfFocus.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = role in self._topLevelRoles()
        msg = "INFO: %s is top-level object: %s" % (orca_state.locusOfFocus, rv)
        debug.println(debug.LEVEL_INFO, msg, True)

        return rv

    def topLevelObject(self, obj):
        """Returns the top-level object (frame, dialog ...) containing obj,
        or None if obj is not inside a top-level object.

        Arguments:
        - obj: the Accessible object
        """

        if not obj:
            return None

        stopAtRoles = self._topLevelRoles()

        while obj and obj.parent \
              and not obj.getRole() in stopAtRoles \
              and not obj.parent.getRole() == pyatspi.ROLE_APPLICATION:
            obj = obj.parent

        return obj

    def topLevelObjectIsActiveAndCurrent(self, obj=None):
        obj = obj or orca_state.locusOfFocus

        topLevel = self.topLevelObject(obj)
        if not topLevel:
            return False

        topLevel.clearCache()
        try:
            state = topLevel.getState()
        except:
            msg = "ERROR: Exception getting state of topLevel %s" % topLevel
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not state.contains(pyatspi.STATE_ACTIVE) \
           or state.contains(pyatspi.STATE_DEFUNCT):
            return False

        if not self.isSameObject(topLevel, orca_state.activeWindow):
            return False

        return True

    @staticmethod
    def onSameLine(obj1, obj2, delta=0):
        """Determines if obj1 and obj2 are on the same line."""

        try:
            bbox1 = obj1.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            bbox2 = obj2.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
        except:
            return False

        center1 = bbox1.y + bbox1.height / 2
        center2 = bbox2.y + bbox2.height / 2

        return abs(center1 - center2) <= delta

    @staticmethod
    def pathComparison(path1, path2, treatDescendantAsSame=False):
        """Compares the two paths and returns -1, 0, or 1 to indicate if path1
        is before, the same, or after path2."""

        if path1 == path2:
            return 0

        for x in range(min(len(path1), len(path2))):
            if path1[x] < path2[x]:
                return -1
            if path1[x] > path2[x]:
                return 1

        if treatDescendantAsSame:
            return 0

        rv = len(path1) - len(path2)
        return min(max(rv, -1), 1)

    @staticmethod
    def sizeComparison(obj1, obj2):
        try:
            bbox = obj1.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            width1, height1 = bbox.width, bbox.height
        except:
            width1, height1 = 0, 0

        try:
            bbox = obj2.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            width2, height2 = bbox.width, bbox.height
        except:
            width2, height2 = 0, 0

        return (width1 * height1) - (width2 * height2)

    @staticmethod
    def spatialComparison(obj1, obj2):
        """Compares the physical locations of obj1 and obj2 and returns -1,
        0, or 1 to indicate if obj1 physically is before, is in the same
        place as, or is after obj2."""

        try:
            bbox = obj1.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            x1, y1 = bbox.x, bbox.y
        except:
            x1, y1 = 0, 0

        try:
            bbox = obj2.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            x2, y2 = bbox.x, bbox.y
        except:
            x2, y2 = 0, 0

        rv = y1 - y2 or x1 - x2

        # If the objects claim to have the same coordinates, there is either
        # a horrible design crime or we've been given bogus extents. Fall back
        # on the index in the parent. This is seen with GtkListBox items which
        # had been scrolled off-screen.
        if not rv and obj1.parent == obj2.parent:
            rv = obj1.getIndexInParent() - obj2.getIndexInParent()

        rv = max(rv, -1)
        rv = min(rv, 1)

        return rv

    def hasNoSize(self, obj):
        if not obj:
            return False

        try:
            extents = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
        except:
            msg = "ERROR: Exception getting extents for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return not (extents.width and extents.height)

    def _hasNonDescendableDescendant(self, root):
        roles = [pyatspi.ROLE_PAGE_TAB_LIST,
                 pyatspi.ROLE_SPLIT_PANE,
                 pyatspi.ROLE_TABLE]

        def isMatch(x):
            if not x:
                return False

            if x.getRole() in roles:
                return True

            if 'Table' in pyatspi.listInterfaces(x):
                return x.childCount > 50

            if 'Document' in pyatspi.listInterfaces(x):
                return True

        match = pyatspi.findDescendant(root, isMatch)
        if match:
            msg = "INFO: %s has descendant %s" % (root, match)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def unrelatedLabels(self, root, onlyShowing=True):
        """Returns a list containing all the unrelated (i.e., have no
        relations to anything and are not a fundamental element of a
        more atomic component like a combo box) labels under the given
        root.  Note that the labels must also be showing on the display.

        Arguments:
        - root: the Accessible object to traverse
        - onlyShowing: if True, only return labels with STATE_SHOWING

        Returns a list of unrelated labels under the given root.
        """

        if self._hasNonDescendableDescendant(root):
            return []

        if self._script.spellcheck and self._script.spellcheck.isCheckWindow(root):
            return []

        hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_LABEL
        try:
            allLabels = pyatspi.findAllDescendants(root, hasRole)
        except:
            return []
        try:
            labels = [x for x in allLabels if not x.getRelationSet()]
            if onlyShowing:
                labels = [x for x in labels if x.getState().contains(pyatspi.STATE_SHOWING)]
        except:
            return []

        # Eliminate duplicates
        d = {}
        for label in labels:
            if label.name and label.name in [root.name, label.parent.name]:
                continue
            d[label.name] = label
        labels = list(d.values())

        return sorted(labels, key=functools.cmp_to_key(self.spatialComparison))

    def unfocusedAlertAndDialogCount(self, obj):
        """If the current application has one or more alert or dialog
        windows and the currently focused window is not an alert or a dialog,
        return a count of the number of alert and dialog windows, otherwise
        return a count of zero.

        Arguments:
        - obj: the Accessible object

        Returns the alert and dialog count.
        """

        alertAndDialogCount = 0
        app = obj.getApplication()
        window = self.topLevelObject(obj)
        if window and window.getRole() != pyatspi.ROLE_ALERT and \
           window.getRole() != pyatspi.ROLE_DIALOG and \
           not self.isFunctionalDialog(window):
            for child in app:
                if child.getRole() == pyatspi.ROLE_ALERT or \
                   child.getRole() == pyatspi.ROLE_DIALOG or \
                   self.isFunctionalDialog(child):
                    alertAndDialogCount += 1

        return alertAndDialogCount

    def uri(self, obj):
        """Return the URI for a given link object.

        Arguments:
        - obj: the Accessible object.
        """

        try:
            return obj.queryHyperlink().getURI(0)
        except:
            return None

    def validParent(self, obj):
        """Returns the first valid parent/ancestor of obj. We need to do
        this in some applications and toolkits due to bogus hierarchies.

        Arguments:
        - obj: the Accessible object
        """

        if not obj:
            return None

        return obj.parent

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
        except:
            return

        if not text.getNSelections():
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

        if not obj:
            return None

        for relation in obj.getRelationSet():
            if relation.getRelationType() == pyatspi.RELATION_FLOWS_FROM:
                return relation.getTarget(0)

        index = obj.getIndexInParent() - 1
        if obj.parent and not (0 <= index < obj.parent.childCount - 1):
            obj = obj.parent
            index = obj.getIndexInParent() - 1

        try:
            prevObj = obj.parent[index]
        except:
            prevObj = None

        if prevObj == obj:
            prevObj = None

        return prevObj

    def findNextObject(self, obj):
        """Finds the object after this one."""

        if not obj:
            return None

        for relation in obj.getRelationSet():
            if relation.getRelationType() == pyatspi.RELATION_FLOWS_TO:
                return relation.getTarget(0)

        index = obj.getIndexInParent() + 1
        if obj.parent and not (0 < index < obj.parent.childCount):
            obj = obj.parent
            index = obj.getIndexInParent() + 1

        try:
            nextObj = obj.parent[index]
        except:
            nextObj = None

        if nextObj == obj:
            nextObj = None

        return nextObj

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
                textContents = "%s %s" % (selection, textContents)
            prevObj = self.findPreviousObject(prevObj)

        nextObj = self.findNextObject(obj)
        while nextObj:
            if self.queryNonEmptyText(nextObj):
                selection, start, end = self.selectedText(nextObj)
                if not selection:
                    break
                textContents = "%s %s" % (textContents, selection)
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
        except:
            return []

        rv = []
        try:
            nSelections = text.getNSelections()
        except:
            nSelections = 0
        for i in range(nSelections):
            rv.append(text.getSelection(i))

        return rv

    def characterOffsetInParent(self, obj):
        """Returns the character offset of the embedded object
        character for this object in its parent's accessible text.

        Arguments:
        - obj: an Accessible that should implement the accessible
          hyperlink specialization.

        Returns an integer representing the character offset of the
        embedded object character for this hyperlink in its parent's
        accessible text, or -1 something was amuck.
        """

        offset = -1
        try:
            hyperlink = obj.queryHyperlink()
        except NotImplementedError:
            msg = "INFO: %s does not implement the hyperlink interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            # We need to make sure that this is an embedded object in
            # some accessible text (as opposed to an imagemap link).
            #
            try:
                obj.parent.queryText()
                offset = hyperlink.startIndex
            except:
                msg = "ERROR: Exception getting startIndex for %s in parent %s" % (obj, obj.parent)
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                msg = "INFO: startIndex of %s is %i" % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)

        return offset

    @staticmethod
    def clearTextSelection(obj):
        """Clears the text selection if the object supports it.

        Arguments:
        - obj: the Accessible object.
        """

        try:
            text = obj.queryText()
        except:
            return

        for i in range(text.getNSelections()):
            text.removeSelection(0)

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
        except:
            return ""

        if self.EMBEDDED_OBJECT_CHARACTER in string:
            # If we're not getting the full text of this object, but
            # rather a substring, we need to figure out the offset of
            # the first child within this substring.
            #
            childOffset = 0
            for child in obj:
                if self.characterOffsetInParent(child) >= startOffset:
                    break
                childOffset += 1

            toBuild = list(string)
            count = toBuild.count(self.EMBEDDED_OBJECT_CHARACTER)
            for i in range(count):
                index = toBuild.index(self.EMBEDDED_OBJECT_CHARACTER)
                child = obj[i + childOffset]
                childText = self.expandEOCs(child)
                if not childText:
                    childText = ""
                toBuild[index] = childText

            string = "".join(toBuild)

        return string

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
        if attributes.get("underline") == "error":
            return True

        return False

    def getError(self, obj):
        return obj.getState().contains(pyatspi.STATE_INVALID_ENTRY)

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
        except:
            pass
        else:
            if text.characterCount:
                return text

        return None

    def deletedText(self, event):
        return event.any_data

    def insertedText(self, event):
        if event.any_data:
            return event.any_data

        try:
            role = event.source.getRole()
        except:
            msg = "ERROR: Exception getting role of %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            role = None

        msg = "ERROR: Broken text insertion event"
        debug.println(debug.LEVEL_INFO, msg, True)

        if role == pyatspi.ROLE_PASSWORD_TEXT:
            text = self.queryNonEmptyText(event.source)
            if text:
                string = text.getText(0, -1)
                if string:
                    msg = "HACK: Returning last char in '%s'" % string
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return string[-1]

        msg = "FAIL: Unable to correct broken text insertion event"
        debug.println(debug.LEVEL_INFO, msg, True)
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
        except:
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
        obj = orca_state.locusOfFocus
        try:
            offset = obj.queryText().caretOffset
        except NotImplementedError:
            offset = 0
        except:
            offset = -1

        return obj, offset

    def getFirstCaretPosition(self, obj):
        return obj, 0

    def setCaretPosition(self, obj, offset, documentFrame=None):
        orca.setLocusOfFocus(None, obj, False)
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
        except:
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
        except:
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
        except:
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

        return "%s: %s" % (localizedKey, localizedValue)

    def willEchoCharacter(self, event):
        """Given a keyboard event containing an alphanumeric key,
        determine if the script is likely to echo it as a character.
        """

        if not orca_state.locusOfFocus or not settings.enableEchoByCharacter:
            return False

        if len(event.event_string) != 1 \
           or event.modifiers & keybindings.ORCA_CTRL_MODIFIER_MASK:
            return False

        obj = orca_state.locusOfFocus
        role = obj.getRole()
        if role == pyatspi.ROLE_PASSWORD_TEXT:
            return False

        if obj.getState().contains(pyatspi.STATE_EDITABLE):
            return True

        return False

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################

    def _addRepeatSegment(self, segment, line, respectPunctuation=True):
        """Add in the latest line segment, adjusting for repeat characters
        and punctuation.

        Arguments:
        - segment: the segment of repeated characters.
        - line: the current built-up line to characters to speak.
        - respectPunctuation: if False, ignore punctuation level.

        Returns: the current built-up line plus the new segment, after
        adjusting for repeat character counts and punctuation.
        """

        from . import punctuation_settings
        from . import chnames

        style = settings.verbalizePunctuationStyle
        isPunctChar = True
        try:
            level, action = punctuation_settings.getPunctuationInfo(segment[0])
        except:
            isPunctChar = False
        count = len(segment)
        if (count >= settings.repeatCharacterLimit) \
           and (not segment[0] in self._script.whitespace):
            if (not respectPunctuation) \
               or (isPunctChar and (style <= level)):
                repeatChar = chnames.getCharacterName(segment[0])
                repeatSegment = messages.repeatedCharCount(repeatChar, count)
                line = "%s %s" % (line, repeatSegment)
            else:
                line += segment
        else:
            line += segment

        return line

    def adjustForLinks(self, obj, line, startOffset):
        """Adjust line to include the word "link" after any hypertext links.

        Arguments:
        - obj: the accessible object that this line came from.
        - line: the string to adjust for links.
        - startOffset: the caret offset at the start of the line.

        Returns: a new line adjusted to add the speaking of "link" after
        text which is also a link.
        """

        from . import punctuation_settings

        endOffset = startOffset + len(line)
        try:
            hyperText = obj.queryHypertext()
            nLinks = hyperText.getNLinks()
        except:
            nLinks = 0

        adjustedLine = list(line)
        for n in range(nLinks, 0, -1):
            link = hyperText.getLink(n - 1)
            if not link:
                continue

            # We only care about links in the string, line:
            #
            if startOffset < link.endIndex <= endOffset:
                index = link.endIndex - startOffset
            elif startOffset <= link.startIndex < endOffset:
                index = len(line)
                if link.endIndex < endOffset:
                    index -= 1
            else:
                continue

            linkString = " " + messages.LINK

            # If the link was not followed by a whitespace or punctuation
            # character, then add in a space to make it more presentable.
            #
            nextChar = ""
            if index < len(line):
                nextChar = adjustedLine[index]
            if not (nextChar in self._script.whitespace \
                    or punctuation_settings.getPunctuationInfo(nextChar)):
                linkString += " "
            adjustedLine[index:index] = linkString

        return "".join(adjustedLine)

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

        multipleChars = False
        for i in range(1, len(line)):
            if line[i] == lastChar:
                segment += line[i]
            else:
                multipleChars = True
                newLine = self._addRepeatSegment(segment, newLine)
                segment = line[i]

            lastChar = line[i]

        return self._addRepeatSegment(segment, newLine, multipleChars)

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
        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or not _settingsManager.getSetting('enableSpeechIndentation'):
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
                result += "%s " % messages.spacesCount(end-start)
            else:
                result += "%s " % messages.tabsCount(end-start)

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

    def isAutoTextEvent(self, event):
        """Returns True if event is associated with text being autocompleted
        or autoinserted or autocorrected or autosomethingelsed.

        Arguments:
        - event: the accessible event being examined
        """

        if event.type.startswith("object:text-changed:insert"):
            if not event.any_data or not event.source:
                return False

            state = event.source.getState()
            if not state.contains(pyatspi.STATE_EDITABLE):
                return False
            if not state.contains(pyatspi.STATE_SHOWING):
                return False
            if state.contains(pyatspi.STATE_FOCUSABLE):
                event.source.clearCache()
                state = event.source.getState()
                if not state.contains(pyatspi.STATE_FOCUSED):
                    return False

            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey == "Tab" and event.any_data != "\t":
                return True
            if lastKey == "Return" and event.any_data != "\n":
                return True
            if lastKey in ["Up", "Down", "Page_Up", "Page_Down"]:
                return self.isEditableDescendantOfComboBox(event.source)

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

    def intersectingRegion(self, obj1, obj2, coordType=None):
        """Returns the extents of the intersection of obj1 and obj2."""

        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        try:
            extents1 = obj1.queryComponent().getExtents(coordType)
            extents2 = obj2.queryComponent().getExtents(coordType)
        except:
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
        except:
            if sequence.endswith(" "):
                sequence += chnames.getCharacterName(" ")
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
        except:
            if self.KEY_BINDING not in self._script.generatorCache:
                self._script.generatorCache[self.KEY_BINDING] = {}

        try:
            action = obj.queryAction()
        except NotImplementedError:
            self._script.generatorCache[self.KEY_BINDING][obj] = ["", "", ""]
            return self._script.generatorCache[self.KEY_BINDING][obj]

        # Action is a string in the format, where the mnemonic and/or
        # accelerator can be missing.
        #
        # <mnemonic>;<full-path>;<accelerator>
        #
        # The keybindings in <full-path> should be separated by ":"
        #
        try:
            bindingStrings = action.getKeyBinding(0).split(';')
        except:
            self._script.generatorCache[self.KEY_BINDING][obj] = ["", "", ""]
            return self._script.generatorCache[self.KEY_BINDING][obj]

        if len(bindingStrings) == 3:
            mnemonic       = bindingStrings[0]
            fullShortcut   = bindingStrings[1]
            accelerator    = bindingStrings[2]
        elif len(bindingStrings) > 0:
            mnemonic       = ""
            fullShortcut   = bindingStrings[0]
            try:
                accelerator = bindingStrings[1]
            except:
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
        except:
            return [], {}

        return [keys, dictionary]

    def textForValue(self, obj):
        """Returns the text to be displayed for the object's current value.

        Arguments:
        - obj: the Accessible object that may or may not have a value.

        Returns a string representing the value.
        """

        # Use ARIA "valuetext" attribute if present.  See
        # http://bugzilla.gnome.org/show_bug.cgi?id=552965
        #
        try:
            attributes = obj.getAttributes()
        except:
            return ""
        for attribute in attributes:
            if attribute.startswith("valuetext"):
                return attribute[10:]

        try:
            value = obj.queryValue()
        except NotImplementedError:
            return ""
        else:
            currentValue = value.currentValue

        # "The reports of my implementation are greatly exaggerated."
        try:
            maxValue = value.maximumValue
        except (LookupError, RuntimeError):
            maxValue = 0.0
            msg = 'ERROR: Exception getting maximumValue for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        try:
            minValue = value.minimumValue
        except (LookupError, RuntimeError):
            minValue = 0.0
            msg = 'ERROR: Exception getting minimumValue for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        try:
            minIncrement = value.minimumIncrement
        except (LookupError, RuntimeError):
            minIncrement = (maxValue - minValue) / 100.0
            msg = 'ERROR: Exception getting minimumIncrement for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        if minIncrement != 0.0:
            try:
                decimalPlaces = math.ceil(max(0, -math.log10(minIncrement)))
            except ValueError:
                msg = 'ERROR: Exception calculating decimal places for %s' % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return ""
        elif abs(currentValue) < 1:
            decimalPlaces = 1
        else:
            decimalPlaces = 0

        formatter = "%%.%df" % decimalPlaces
        return formatter % currentValue

    @staticmethod
    def unicodeValueString(character):
        """ Returns a four hex digit representation of the given character
        
        Arguments:
        - The character to return representation
        
        Returns a string representaition of the given character unicode vlue
        """

        try:
            return "%04x" % ord(character)
        except:
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

    @staticmethod
    def getHyperlinkRange(obj):
        """Returns the start and end indices associated with the embedded
        object, obj."""

        try:
            hyperlink = obj.queryHyperlink()
        except NotImplementedError:
            return 0, 0

        return hyperlink.startIndex, hyperlink.endIndex

    def selectedChildren(self, obj):
        try:
            selection = obj.querySelection()
            count = selection.nSelectedChildren
        except NotImplementedError:
            msg = "INFO: %s does not implement the selection interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []
        except:
            msg = "ERROR: Exception querying selection interface for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        msg = "INFO: %s reports %i selected children" % (obj, count)
        debug.println(debug.LEVEL_INFO, msg, True)

        children = []
        for x in range(count):
            child = selection.getSelectedChild(x)
            if not self.isZombie(child):
                children.append(child)

        role = obj.getRole()
        if role == pyatspi.ROLE_MENU and not children:
            pred = lambda x: x and x.getState().contains(pyatspi.STATE_SELECTED)
            try:
                children = pyatspi.findAllDescendants(obj, pred)
            except:
                msg = "ERROR: Exception calling findAllDescendants on %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)

        if role == pyatspi.ROLE_COMBO_BOX \
           and children and children[0].getRole() == pyatspi.ROLE_MENU:
            children = self.selectedChildren(children[0])
            if not children and obj.name:
                pred = lambda x: x and x.name == obj.name
                try:
                    children = pyatspi.findAllDescendants(obj, pred)
                except:
                    msg = "ERROR: Exception calling findAllDescendants on %s" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)

        return children

    def selectedChildCount(self, obj):
        try:
            selection = obj.querySelection()
            count = selection.nSelectedChildren
        except NotImplementedError:
            msg = "INFO: %s does not implement the selection interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0
        except:
            msg = "ERROR: Exception querying selection interface for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0

        msg = "INFO: %s reports %i selected children" % (obj, count)
        debug.println(debug.LEVEL_INFO, msg, True)
        return count

    def focusedChild(self, obj):
        isFocused = lambda x: x and x.getState().contains(pyatspi.STATE_FOCUSED)
        child = pyatspi.findDescendant(obj, isFocused)
        if child == obj:
            msg = "ERROR: focused child of %s is %s" % (obj, child)
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return child

    def popupMenuFor(self, obj):
        if not obj and obj.childCount:
            return None

        menus = [child for child in obj if child.getRole() == pyatspi.ROLE_MENU]
        for menu in menus:
            try:
                state = menu.getState()
            except:
                msg = "ERROR: Exception getting state for %s" % menu
                debug.println(debug.LEVEL_INFO, msg, True)
                continue
            if state.contains(pyatspi.STATE_ENABLED):
                return menu

        return None

    def isMenuButton(self, obj):
        if not obj:
            return False

        try:
            role = obj.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role not in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_TOGGLE_BUTTON]:
            return False

        return self.popupMenuFor(obj) is not None

    def isEntryCompletionPopupItem(self, obj):
        return False

    def getEntryForEditableComboBox(self, obj):
        if not obj:
            return None

        try:
            role = obj.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if role != pyatspi.ROLE_COMBO_BOX:
            return None

        children = [x for x in obj if self.isEditableTextArea(x)]
        if len(children) == 1:
            return children[0]

        return None

    def isEditableComboBox(self, obj):
        return self.getEntryForEditableComboBox(obj) is not None

    def isEditableDescendantOfComboBox(self, obj):
        if not obj:
            return False

        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not state.contains(pyatspi.STATE_EDITABLE):
            return False

        isComboBox = lambda x: x and x.getRole() == pyatspi.ROLE_COMBO_BOX
        return pyatspi.findAncestor(obj, isComboBox) is not None

    def isPopOver(self, obj):
        return False

    def isNonModalPopOver(self, obj):
        if not self.isPopOver(obj):
            return False

        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return not state.contains(pyatspi.STATE_MODAL)

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

    def headingLevel(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_HEADING):
            return 0

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            msg = "ERROR: Exception getting attributes for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0

        try:
            value = int(attrs.get('level', '0'))
        except ValueError:
            msg = "ERROR: Exception getting value for %s (%s)" % (obj, attrs)
            debug.println(debug.LEVEL_INFO, msg, True)
            return 0

        return value

    def hasMeaningfulToggleAction(self, obj):
        try:
            action = obj.queryAction()
        except NotImplementedError:
            return False

        toggleActionNames = ["toggle", object_properties.ACTION_TOGGLE]
        for i in range(action.nActions):
            if action.getName(i) in toggleActionNames:
                return True

        return False

    def columnHeadersForCell(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL):
            return []

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return []

        index = self.cellIndex(obj)
        row, col = table.getRowAtIndex(index), table.getColumnAtIndex(index)
        colspan = table.getColumnExtentAt(row, col)

        headers = []
        for c in range(col, col+colspan):
            headers.append(table.getColumnHeader(c))

        return headers

    def rowHeadersForCell(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL):
            return []

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return []

        index = self.cellIndex(obj)
        row, col = table.getRowAtIndex(index), table.getColumnAtIndex(index)
        rowspan = table.getRowExtentAt(row, col)

        headers = []
        for r in range(row, row+rowspan):
            headers.append(table.getRowHeader(r))

        return headers

    def columnHeaderForCell(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL):
            return None

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return None

        index = self.cellIndex(obj)
        columnIndex = table.getColumnAtIndex(index)
        return table.getColumnHeader(columnIndex)

    def rowHeaderForCell(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL):
            return None

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return None

        index = self.cellIndex(obj)
        rowIndex = table.getRowAtIndex(index)
        return table.getRowHeader(rowIndex)

    def coordinatesForCell(self, obj):
        roles = [pyatspi.ROLE_TABLE_CELL,
                 pyatspi.ROLE_COLUMN_HEADER,
                 pyatspi.ROLE_ROW_HEADER]
        if not (obj and obj.getRole() in roles):
            return -1, -1

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return -1, -1

        index = self.cellIndex(obj)
        return table.getRowAtIndex(index), table.getColumnAtIndex(index)

    def rowAndColumnSpan(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL):
            return -1, -1

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return -1, -1

        index = self.cellIndex(obj)
        row, col = table.getRowAtIndex(index), table.getColumnAtIndex(index)
        return table.getRowExtentAt(row, col), table.getColumnExtentAt(row, col)

    def rowAndColumnCount(self, obj):
        try:
            table = obj.queryTable()
        except:
            return -1, -1

        return table.nRows, table.nColumns

    def containsPoint(self, obj, x, y, coordType, margin=2):
        try:
            component = obj.queryComponent()
        except:
            return False

        if component.contains(x, y, coordType):
            return True

        x1, y1 = x + margin, y + margin
        if component.contains(x1, y1, coordType):
            msg = "INFO: %s contains (%i,%i); not (%i,%i)" % (obj, x1, y1, x, y)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _boundsIncludeChildren(self, obj):
        if not obj:
            return False

        roles = [pyatspi.ROLE_MENU,
                 pyatspi.ROLE_PAGE_TAB]

        return obj.getRole() not in roles

    def _treatAsLeafNode(self, obj):
        if not obj or self.isDead(obj):
            return False

        if not obj.childCount:
            return True

        role = obj.getRole()
        if role == pyatspi.ROLE_TABLE_ROW:
            return False

        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            return not state.contains(pyatspi.STATE_EXPANDED)

        roles = [pyatspi.ROLE_COMBO_BOX,
                 pyatspi.ROLE_PUSH_BUTTON]

        return role in roles

    def descendantAtPoint(self, root, x, y, coordType=None):
        if not root:
            return None

        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        if self.containsPoint(root, x, y, coordType):
            if self._treatAsLeafNode(root) or not self._boundsIncludeChildren(root):
                return root
        elif self._treatAsLeafNode(root) or self._boundsIncludeChildren(root):
            return None

        if "Table" in pyatspi.listInterfaces(root):
            try:
                component = root.queryComponent()
            except:
                msg = "ERROR: Exception querying component of %s" % root
                debug.println(debug.LEVEL_INFO, msg, True)
                child = None
            else:
                child = component.getAccessibleAtPoint(x, y, coordType)
                msg = "INFO: %s is at (%s, %s) in %s" % (child, x, y, root)
                debug.println(debug.LEVEL_INFO, msg, True)

                if child and child != root:
                    cell = self.descendantAtPoint(child, x, y, coordType)
                    msg = "INFO: %s is at (%s, %s) in %s" % (cell, x, y, child)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    if cell:
                        return cell

        for child in root:
            obj = self.descendantAtPoint(child, x, y, coordType)
            if obj:
                return obj

        return None

    def _adjustPointForObj(self, obj, x, y, coordType):
        return x, y

    def textAtPoint(self, obj, x, y, coordType=None, boundary=None):
        text = self.queryNonEmptyText(obj)
        if not text:
            return "", 0, 0

        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        if boundary is None:
            boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        x, y = self._adjustPointForObj(obj, x, y, coordType)
        offset = text.getOffsetAtPoint(x, y, coordType)
        if not 0 <= offset < text.characterCount:
            return "", 0, 0

        string, start, end = text.getTextAtOffset(offset, boundary)
        if not string:
            return "", start, end

        if boundary == pyatspi.TEXT_BOUNDARY_WORD_START and not string.strip():
            return "", 0, 0

        extents = text.getRangeExtents(start, end, coordType)
        if not self.containsRegion(extents, (x, y, 1, 1)):
            return "", 0, 0

        return string, start, end

    def visibleRows(self, obj, boundingbox):
        try:
            table = obj.queryTable()
            nRows = table.nRows
        except:
            return []

        msg = "INFO: %s has %i rows" % (obj, nRows)
        debug.println(debug.LEVEL_INFO, msg, True)

        x, y, width, height = boundingbox
        cell = self.descendantAtPoint(obj, x, y + 1)
        row, col = self.coordinatesForCell(cell)
        startIndex = max(0, row)
        msg = "INFO: First cell: %s (row: %i)" % (cell, row)
        debug.println(debug.LEVEL_INFO, msg, True)

        # Just in case the row above is a static header row in a scrollable table.
        try:
            extents = cell.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
        except:
            nextIndex = startIndex
        else:
            cell = self.descendantAtPoint(obj, x, y + extents.height + 1)
            row, col = self.coordinatesForCell(cell)
            nextIndex = max(startIndex, row)
            msg = "INFO: Next cell: %s (row: %i)" % (cell, row)
            debug.println(debug.LEVEL_INFO, msg, True)

        cell = self.descendantAtPoint(obj, x, y + height - 1)
        row, col = self.coordinatesForCell(cell)
        msg = "INFO: Last cell: %s (row: %i)" % (cell, row)
        debug.println(debug.LEVEL_INFO, msg, True)

        if row == -1:
            row = nRows
        endIndex = row

        rows = list(range(nextIndex, endIndex))
        if startIndex not in rows:
            rows.insert(0, startIndex)

        return rows

    def getVisibleTableCells(self, obj):
        try:
            table = obj.queryTable()
        except:
            return []

        try:
            component = obj.queryComponent()
            extents = component.getExtents(pyatspi.DESKTOP_COORDS)
        except:
            msg = "ERROR: Exception getting extents of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        rows = self.visibleRows(obj, extents)
        if not rows:
            return []

        colStartIndex, colEndIndex = self._getTableRowRange(obj)
        if colStartIndex == colEndIndex:
            return []

        cells = []
        for col in range(colStartIndex, colEndIndex):
            colHeader = table.getColumnHeader(col)
            if colHeader:
                cells.append(colHeader)
            for row in rows:
                try:
                    cell = table.getAccessibleAt(row, col)
                except:
                    continue
                if cell and self.isOnScreen(cell):
                    cells.append(cell)

        return cells

    def _getTableRowRange(self, obj):
        rowCount, columnCount = self.rowAndColumnCount(obj)
        startIndex, endIndex = 0, columnCount
        if not self.isSpreadSheetCell(obj):
            return startIndex, endIndex

        parent = self.getTable(obj)
        try:
            component = parent.queryComponent()
        except:
            msg = "ERROR: Exception querying component interface of %s" % parent
            debug.println(debug.LEVEL_INFO, msg, True)
            return startIndex, endIndex

        x, y, width, height = component.getExtents(pyatspi.DESKTOP_COORDS)
        cell = component.getAccessibleAtPoint(x+1, y, pyatspi.DESKTOP_COORDS)
        if cell:
            row, column = self.coordinatesForCell(cell)
            startIndex = column

        cell = component.getAccessibleAtPoint(x+width-1, y, pyatspi.DESKTOP_COORDS)
        if cell:
            row, column = self.coordinatesForCell(cell)
            endIndex = column + 1

        return startIndex, endIndex

    def getShowingCellsInSameRow(self, obj):
        parent = self.getTable(obj)
        try:
            table = parent.queryTable()
        except:
            msg = "ERROR: Exception querying table interface of %s" % parent
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        row, column = self.coordinatesForCell(obj)
        if row == -1:
            return []

        startIndex, endIndex = self._getTableRowRange(obj)
        if startIndex == endIndex:
            return []

        cells = []
        for i in range(startIndex, endIndex):
            cell = table.getAccessibleAt(row, i)
            try:
                showing = cell.getState().contains(pyatspi.STATE_SHOWING)
            except:
                continue
            if showing:
                cells.append(cell)

        return cells

    def cellForCoordinates(self, obj, row, column, showingOnly=False):
        try:
            table = obj.queryTable()
        except:
            return None

        cell = table.getAccessibleAt(row, column)
        if not showingOnly:
            return cell

        try:
            state = cell.getState()
        except:
            msg = "ERROR: Exception getting state of %s" % cell
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        if not state().contains(pyatspi.STATE_SHOWING):
            return None

        return cell

    def isLastCell(self, obj):
        try:
            role = obj.getRole()
        except:
            msg = "ERROR: Exception getting role of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not role == pyatspi.ROLE_TABLE_CELL:
            return False

        isTable = lambda x: x and 'Table' in pyatspi.listInterfaces(x)
        parent = pyatspi.findAncestor(obj, isTable)
        try:
            table = parent.queryTable()
        except:
            return False

        index = self.cellIndex(obj)
        row, col = table.getRowAtIndex(index), table.getColumnAtIndex(index)
        return row + 1 == table.nRows and col + 1 == table.nColumns

    def isNonUniformTable(self, obj):
        try:
            table = obj.queryTable()
        except:
            return False

        for r in range(table.nRows):
            for c in range(table.nColumns):
                if table.getRowExtentAt(r, c) > 1 \
                   or table.getColumnExtentAt(r, c) > 1:
                    return True

        return False

    def isShowingOrVisible(self, obj):
        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if state.contains(pyatspi.STATE_SHOWING) \
           or state.contains(pyatspi.STATE_VISIBLE):
            return True

        msg = "INFO: %s is neither showing nor visible" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def isShowingAndVisible(self, obj):
        try:
            state = obj.getState()
            role = obj.getRole()
        except:
            msg = "ERROR: Exception getting state and role of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if state.contains(pyatspi.STATE_SHOWING) \
           and state.contains(pyatspi.STATE_VISIBLE):
            return True

        # TODO - JD: This really should be in the toolkit scripts. But it
        # seems to be present in multiple toolkits, so it's either being
        # inherited (e.g. from Gtk in Firefox Chrome, LO, Eclipse) or it
        # may be an AT-SPI2 bug. For now, handling it here.
        menuRoles = [pyatspi.ROLE_MENU,
                     pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM,
                     pyatspi.ROLE_SEPARATOR]

        if role in menuRoles and self.isInOpenMenuBarMenu(obj):
            msg = "HACK: Treating %s as showing and visible" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def isDead(self, obj):
        try:
            name = obj.name
        except:
            debug.println(debug.LEVEL_INFO, "DEAD: %s" % obj, True)
            return True

        return False

    def isZombie(self, obj):
        try:
            index = obj.getIndexInParent()
            state = obj.getState()
            role = obj.getRole()
        except:
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s is null or dead" % obj, True)
            return True

        topLevelRoles = [pyatspi.ROLE_APPLICATION,
                         pyatspi.ROLE_ALERT,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_LABEL, # For Unity Panel Service bug
                         pyatspi.ROLE_PAGE, # For Evince bug
                         pyatspi.ROLE_WINDOW,
                         pyatspi.ROLE_FRAME]
        if index == -1 and role not in topLevelRoles:
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s's index is -1" % obj, True)
            return True
        if state.contains(pyatspi.STATE_DEFUNCT):
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s is defunct" % obj, True)
            return True
        if state.contains(pyatspi.STATE_INVALID):
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s is invalid" % obj, True)
            return True

        return False

    def findReplicant(self, root, obj):
        if not (root and obj):
            return None

        # Given an broken table hierarchy, findDescendant can hang. And the
        # reason we're here in the first place is to work around the app or
        # toolkit killing accessibles. There's only so much we can do....
        if root.getRole() in [pyatspi.ROLE_TABLE, pyatspi.ROLE_EMBEDDED]:
            return None

        isSame = lambda x: x and self.isSameObject(
            x, obj, comparePaths=True, ignoreNames=True)
        if isSame(root):
            replicant = root
        else:
            try:
                replicant = pyatspi.findDescendant(root, isSame)
            except:
                msg = "INFO: Exception from findDescendant for %s" % root
                debug.println(debug.LEVEL_INFO, msg, True)
                replicant = None

        msg = "HACK: Returning %s as replicant for Zombie %s" % (replicant, obj)
        debug.println(debug.LEVEL_INFO, msg, True)
        return replicant

    def getFunctionalChildCount(self, obj):
        if not obj:
            return None

        result = []
        pred = lambda r: r.getRelationType() == pyatspi.RELATION_NODE_PARENT_OF
        relations = list(filter(pred, obj.getRelationSet()))
        if relations:
            return relations[0].getNTargets()

        return obj.childCount

    def getFunctionalChildren(self, obj):
        if not obj:
            return None

        result = []
        pred = lambda r: r.getRelationType() == pyatspi.RELATION_NODE_PARENT_OF
        relations = list(filter(pred, obj.getRelationSet()))
        if relations:
            r = relations[0]
            result = [r.getTarget(i) for i in range(r.getNTargets())]

        return result or [child for child in obj]

    def getFunctionalParent(self, obj):
        if not obj:
            return None

        result = None
        pred = lambda r: r.getRelationType() == pyatspi.RELATION_NODE_CHILD_OF
        relations = list(filter(pred, obj.getRelationSet()))
        if relations:
            result = relations[0].getTarget(0)

        return result or obj.parent

    def getPositionAndSetSize(self, obj):
        if not obj:
            return -1, -1

        isComboBox = obj.getRole() == pyatspi.ROLE_COMBO_BOX
        if isComboBox:
            selected = self.selectedChildren(obj)
            if selected:
                obj = selected[0]

        parent = self.getFunctionalParent(obj)
        childCount = self.getFunctionalChildCount(parent)
        if childCount > 100 and parent == obj.parent:
            return obj.getIndexInParent(), childCount

        siblings = self.getFunctionalChildren(parent)
        if len(siblings) < 100 and not pyatspi.utils.findAncestor(obj, isComboBox):
            layoutRoles = [pyatspi.ROLE_SEPARATOR, pyatspi.ROLE_TEAROFF_MENU_ITEM]
            isNotLayoutOnly = lambda x: not (self.isZombie(x) or x.getRole() in layoutRoles)
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

    def getCachedTextSelection(self, obj):
        textSelections = self._script.pointOfReference.get('textSelections', {})
        start, end, string = textSelections.get(hash(obj), (0, 0, ''))
        msg = "INFO: Cached selection for %s is '%s' (%i, %i)" % (obj, string, start, end)
        debug.println(debug.LEVEL_INFO, msg, True)
        return start, end, string

    def updateCachedTextSelection(self, obj):
        try:
            text = obj.queryText()
        except NotImplementedError:
            msg = "ERROR: %s doesn't implement AtspiText" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            text = None
        except:
            msg = "ERROR: Exception querying text interface for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
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
            except:
                msg = "ERROR: Exception getting selected text for %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                start = end = 0
            if start != end:
                string = text.getText(start, end)
                while string.endswith(self.EMBEDDED_OBJECT_CHARACTER):
                    end -= 1
                    string = string[:-1]

        msg = "INFO: New selection for %s is '%s' (%i, %i)" % (obj, string, start, end)
        debug.println(debug.LEVEL_INFO, msg, True)
        textSelections[hash(obj)] = start, end, string
        self._script.pointOfReference['textSelections'] = textSelections

    @staticmethod
    def onClipboardContentsChanged(*args):
        script = orca_state.activeScript
        if not script:
            return

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

    def _appendTextToClipboardCallback(self, clipboard, text, newText):
        text = text.rstrip("\n")
        text = "%s\n%s" % (text, newText)
        clipboard.set_text(text, -1)

    def lastInputEventWasPrintableKey(self):
        event = orca_state.lastInputEvent
        if not isinstance(event, input_event.KeyboardEvent):
            return False

        return event.isPrintableKey()

    def lastInputEventWasCommand(self):
        keyString, mods = self.lastKeyAndModifiers()
        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasCharNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString in ["Left", "Right"]:
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasWordNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString in ["Left", "Right"]:
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

    def lastInputEventWasLineNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString in ["Up", "Down"]:
            return False

        if self.isEditableDescendantOfComboBox(orca_state.locusOfFocus):
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasLineBoundaryNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString in ["Home", "End"]:
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasPageNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString in ["Page_Up", "Page_Down"]:
            return False

        if self.isEditableDescendantOfComboBox(orca_state.locusOfFocus):
            return False

        return not (mods & keybindings.CTRL_MODIFIER_MASK)

    def lastInputEventWasFileBoundaryNav(self):
        keyString, mods = self.lastKeyAndModifiers()
        if not keyString in ["Home", "End"]:
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
        if keyString == "Delete":
            return True

        keycode, mods = self._lastKeyCodeAndModifiers()
        keynames = self._allNamesForKeyCode(keycode)
        if 'd' not in keynames:
            return False

        return mods & keybindings.CTRL_MODIFIER_MASK

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

        try:
            role = orca_state.locusOfFocus.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        roles = [pyatspi.ROLE_COLUMN_HEADER,
                 pyatspi.ROLE_ROW_HEADER,
                 pyatspi.ROLE_TABLE_COLUMN_HEADER,
                 pyatspi.ROLE_TABLE_ROW_HEADER]

        return role in roles

    def isPresentableTextChangedEventForLocusOfFocus(self, event):
        if not event.type.startswith("object:text-changed:") \
           and not event.type.startswith("object:text-attributes-changed"):
            return False

        try:
            role = event.source.getRole()
            state = event.source.getState()
        except:
            msg = "ERROR: Exception getting role and state of %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        ignoreRoles = [pyatspi.ROLE_LABEL,
                       pyatspi.ROLE_MENU,
                       pyatspi.ROLE_MENU_ITEM,
                       pyatspi.ROLE_SLIDER,
                       pyatspi.ROLE_SPIN_BUTTON]
        if role in ignoreRoles:
            msg = "INFO: Event is not being presented due to role"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_TABLE_CELL \
           and not state.contains(pyatspi.STATE_FOCUSED) \
           and not state.contains(pyatspi.STATE_SELECTED):
            msg = "INFO: Event is not being presented due to role and states"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.isTypeahead(event.source):
            return state.contains(pyatspi.STATE_FOCUSED)

        if role == pyatspi.ROLE_PASSWORD_TEXT and state.contains(pyatspi.STATE_FOCUSED):
            return True

        if orca_state.locusOfFocus in [event.source, event.source.parent]:
            return True

        if self.isDead(orca_state.locusOfFocus):
            return True

        msg = "INFO: Event is not being presented due to lack of cause"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def isBackSpaceCommandTextDeletionEvent(self, event):
        if not event.type.startswith("object:text-changed:delete"):
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

        try:
            role = event.source.getRole()
        except:
            msg = "ERROR: Exception getting role of %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_PASSWORD_TEXT:
            return _settingsManager.getSetting("enableKeyEcho")

        if len(event.any_data.strip()) == 1:
            return _settingsManager.getSetting("enableEchoByCharacter")

        return False

    def isEditableTextArea(self, obj):
        if not self.isTextArea(obj):
            return False

        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return state.contains(pyatspi.STATE_EDITABLE)

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
        obj = obj or orca_state.locusOfFocus
        if not obj or self.isDead(obj):
            return False

        contents = self.getClipboardContents()
        if not contents:
            return False

        string, start, end = self.selectedText(obj)
        if string and string in contents:
            return True

        obj = self.realActiveDescendant(obj) or obj
        if self.isDead(obj):
            return False

        return obj and obj.name in contents

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

    def presentFocusChangeReason(self):
        if self.handleUndoLocusOfFocusChange():
            return True
        if self.handlePasteLocusOfFocusChange():
            return True
        return False

    def handleTextSelectionChange(self, obj):
        # Note: This guesswork to figure out what actually changed with respect
        # to text selection will get eliminated once the new text-selection API
        # is added to ATK and implemented by the toolkits. (BGO 638378)

        oldStart, oldEnd, oldString = self.getCachedTextSelection(obj)
        self.updateCachedTextSelection(obj)
        newStart, newEnd, newString = self.getCachedTextSelection(obj)

        # TODO - JD: This may be (now or soon) obsolete.
        if self._script.pointOfReference.get('lastAutoComplete') == hash(obj):
            return False

        if self._speakTextSelectionState(len(newString)):
            return True

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
            else:
                changes.append([changeStart, changeEnd, messages.TEXT_UNSELECTED])

        speakMessage = not _settingsManager.getSetting('onlySpeakDisplayedText')
        for start, end, message in changes:
            self._script.sayPhrase(obj, start, end)
            if speakMessage:
                self._script.speakMessage(message, interrupt=False)

        return True

    def _getCtrlShiftSelectionsStrings(self):
        """Hacky and to-be-obsoleted method."""
        return [messages.PARAGRAPH_SELECTED_DOWN,
                messages.PARAGRAPH_UNSELECTED_DOWN,
                messages.PARAGRAPH_SELECTED_UP,
                messages.PARAGRAPH_UNSELECTED_UP]

    def _speakTextSelectionState(self, nSelections):
        """Hacky and to-be-obsoleted method."""

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
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
