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
import locale
import math
import pyatspi
import re

from . import chnames
from . import colornames
from . import debug
from . import keynames
from . import keybindings
from . import input_event
from . import mathsymbols
from . import messages
from . import mouse_review
from . import orca
from . import orca_state
from . import object_properties
from . import pronunciation_dict
from . import settings
from . import text_attribute_names

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities:

    EMBEDDED_OBJECT_CHARACTER = '\ufffc'
    SUPERSCRIPT_DIGITS = \
        ['\u2070', '\u00b9', '\u00b2', '\u00b3', '\u2074',
         '\u2075', '\u2076', '\u2077', '\u2078', '\u2079']
    SUBSCRIPT_DIGITS = \
        ['\u2080', '\u2081', '\u2082', '\u2083', '\u2084',
         '\u2085', '\u2086', '\u2087', '\u2088', '\u2089']

    flags = re.UNICODE
    WORDS_RE = re.compile("(\W+)", flags)
    SUPERSCRIPTS_RE = re.compile("[%s]+" % "".join(SUPERSCRIPT_DIGITS), flags)
    SUBSCRIPTS_RE = re.compile("[%s]+" % "".join(SUBSCRIPT_DIGITS), flags)

    # generatorCache
    #
    DISPLAYED_LABEL = 'displayedLabel'
    DISPLAYED_TEXT = 'displayedText'
    KEY_BINDING = 'keyBinding'
    NESTING_LEVEL = 'nestingLevel'
    NODE_LEVEL = 'nodeLevel'
    REAL_ACTIVE_DESCENDANT = 'realActiveDescendant'

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        self._script = script

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    @staticmethod
    def activeWindow():
        """Traverses the list of known apps looking for one who has an
        immediate child (i.e., a window) whose state includes the active
        state.

        Returns the Python Accessible of the window that's active or None if
        no windows are active.
        """

        apps = Utilities.knownApplications()
        for app in apps:
            for child in app:
                try:
                    if child.getState().contains(pyatspi.STATE_ACTIVE):
                        return child
                except:
                    debug.printException(debug.LEVEL_FINEST)

        return None

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

        debug.println(debug.LEVEL_FINEST,
                      "script_utilities.commonAncestor...")

        if (not a) or (not b):
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

        debug.println(debug.LEVEL_FINEST,
                      "...script_utilities.commonAncestor")

        return commonAncestor

    def componentAtDesktopCoords(self, parent, x, y):
        """Get the descendant component at the given desktop coordinates.

        Arguments:

        - parent: The parent component we are searching below.
        - x: X coordinate.
        - y: Y coordinate.

        Returns end-node that contains the given coordinates, or None.
        """
        acc = self.popupItemAtDesktopCoords(x, y)
        if acc:
            return acc

        container = parent
        while True:
            try:
                ci = container.queryComponent()
            except:
                return None
            else:
                inner_container = container
            container =  ci.getAccessibleAtPoint(x, y, pyatspi.DESKTOP_COORDS)
            if not container or container.queryComponent() == ci:
                break
            if inner_container.getRole() == pyatspi.ROLE_PAGE_TAB_LIST:
                return container

        if inner_container == parent:
            return None
        else:
            return inner_container

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
        except (LookupError, RuntimeError):
            role = None

        if role == pyatspi.ROLE_PUSH_BUTTON and obj.name:
            return obj.name

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

        # [[[WDW - HACK because push buttons can have labels as their
        # children.  An example of this is the Font: button on the General
        # tab in the Editing Profile dialog in gnome-terminal.
        #
        if not displayedText and role == pyatspi.ROLE_PUSH_BUTTON:
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LABEL:
                    childText = self.displayedText(child)
                    if childText and len(childText):
                        displayedText = \
                            self.appendString(displayedText, childText)

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

        return toolbar != None

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

    def isMathFraction(self, obj):
        return False

    def isMathFractionWithoutBar(self, obj):
        return False

    def isMathPhantom(self, obj):
        return False

    def isMathRoot(self, obj):
        return False

    def isMathNthRoot(self, obj):
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

    def isStatic(self, obj):
        role = obj.getRole()
        try:
            isStatic = role == pyatspi.ROLE_STATIC
        except:
            isStatic = False

        if not isStatic and role == pyatspi.ROLE_TEXT:
            isStatic = not obj.getState().contains(pyatspi.STATE_FOCUSABLE)
        return isStatic

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

        if obj and self.isZombie(obj):
            return True

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}
        try:
            role = obj.getRole()
            parentRole = obj.parent.getRole()
        except:
            role = None
            parentRole = None

        try:
            firstChild = obj[0]
        except:
            firstChild = None

        topLevelRoles = [pyatspi.ROLE_ALERT,
                         pyatspi.ROLE_FRAME,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_WINDOW]
        ignorePanelParent = [pyatspi.ROLE_MENU,
                             pyatspi.ROLE_MENU_ITEM,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_TREE_ITEM]

        if role == pyatspi.ROLE_TABLE and attrs.get('layout-guess') != 'true':
            try:
                table = obj.queryTable()
            except:
                layoutOnly = True
            else:
                if not (table.nRows and table.nColumns):
                    layoutOnly = True
                elif not (obj.name or self.displayedLabel(obj)):
                    layoutOnly = not (table.getColumnHeader(0) or table.getRowHeader(0))
        elif role == pyatspi.ROLE_TABLE_CELL and obj.childCount:
            if firstChild.getRole() == pyatspi.ROLE_TABLE_CELL:
                layoutOnly = True
            elif parentRole == pyatspi.ROLE_TABLE:
                layoutOnly = self.isLayoutOnly(obj.parent)
        elif role == pyatspi.ROLE_SECTION:
            layoutOnly = True
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
        elif role == pyatspi.ROLE_MENU and parentRole == pyatspi.ROLE_COMBO_BOX:
            layoutOnly = True
        elif role == pyatspi.ROLE_LIST or self.isTableRow(obj):
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
            debug.println(debug.LEVEL_FINEST,
                          "Object deemed to be for layout purposes only: %s" \
                          % obj)

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
            debug.println(debug.LEVEL_FINE, 'Error - isLink getting role')
            return False

        return role == pyatspi.ROLE_LINK

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""

        if not self.isTextArea(obj):
            return False

        state = obj.getState()
        readOnly = state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        details = debug.getAccessibleDetails(debug.LEVEL_ALL, obj)
        debug.println(debug.LEVEL_ALL,
                      "isReadOnlyTextArea=%s for %s" \
                      % (readOnly, details))

        return readOnly

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
                                         pyatspi.ROLE_PARAGRAPH,
                                         pyatspi.ROLE_TERMINAL)

    @staticmethod
    def knownApplications():
        """Retrieves the list of currently running apps for the desktop
        as a list of Accessible objects.
        """

        debug.println(debug.LEVEL_FINEST,
                      "knownApplications...")

        apps = [x for x in pyatspi.Registry.getDesktop(0) if x is not None]

        debug.println(debug.LEVEL_FINEST,
                      "...knownApplications")

        return apps

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
            debug.println(debug.LEVEL_SEVERE,
                          "labelsForObject() - Error getting RelationSet")
            return label

        allTargets = []
        for relation in relations:
            if relation.getRelationType() \
                   == pyatspi.RELATION_LABELLED_BY:

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
        """Determines the nesting level of this object in a list.  If this
        object is not in a list relation, then 0 will be returned.

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

        nestingLevel = 0
        parent = obj.parent
        while parent.parent and parent.parent.getRole() == pyatspi.ROLE_LIST:
            nestingLevel += 1
            parent = parent.parent

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
                debug.println(debug.LEVEL_SEVERE,
                              "nodeLevel() - Error getting RelationSet")
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
            #
            if (len(nodes) > 100) or nodes.count(node):
                debug.println(debug.LEVEL_WARNING,
                              "nodeLevel detected a cycle!!!")
                done = True
            elif node:
                nodes.append(node)
                debug.println(debug.LEVEL_FINEST,
                              "nodeLevel %d" % len(nodes))
            else:
                done = True

        self._script.generatorCache[self.NODE_LEVEL][obj] = len(nodes) - 1
        return self._script.generatorCache[self.NODE_LEVEL][obj]

    def popupItemAtDesktopCoords(self, x, y):
        """Since pop-up items often don't contain nested components, we need
        a way to efficiently determine if the cursor is over a menu item.

        Arguments:
        - x: X coordinate.
        - y: Y coordinate.

        Returns a menu item the mouse is over, or None.
        """

        suspect_children = []
        if self._script.lastSelectedMenu:
            try:
                si = self._script.lastSelectedMenu.querySelection()
            except NotImplementedError:
                return None

            if si.nSelectedChildren > 0:
                suspect_children = [si.getSelectedChild(0)]
            else:
                suspect_children = self._script.lastSelectedMenu
            for child in suspect_children:
                try:
                    ci = child.queryComponent()
                except NotImplementedError:
                    continue

                if ci.contains(x, y, pyatspi.DESKTOP_COORDS) \
                   and ci.getLayer() == pyatspi.LAYER_POPUP:
                    return child

    def pursueForFlatReview(self, obj):
        """Determines if we should look any further at the object
        for flat review."""

        if self.isHidden(obj):
            return False

        try:
            state = obj.getState()
        except:
            debug.printException(debug.LEVEL_WARNING)
            return False
        else:
            return state.contains(pyatspi.STATE_SHOWING)

    @staticmethod
    def isTableRow(obj):
        """Determines if obj is a table row -- real or functionally."""

        try:
            if not (obj and obj.parent and obj.childCount):
                return False
        except:
            msg = "INFO: Exception getting parent and childCount for %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
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

    def realActiveDescendant(self, obj):
        """Given an object that should be a child of an object that
        manages its descendants, return the child that is the real
        active descendant carrying useful information.

        Arguments:
        - obj: an object that should be a child of an object that
        manages its descendants.
        """

        try:
            return self._script.\
                generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]
        except:
            if self.REAL_ACTIVE_DESCENDANT not in self._script.\
                    generatorCache:
                self._script.generatorCache[self.REAL_ACTIVE_DESCENDANT] = {}
            activeDescendant = None

        # If obj is a table cell and all of it's children are table cells
        # (probably cell renderers), then return the first child which has
        # a non zero length text string. If no such object is found, just
        # fall through and use the default approach below. See bug #376791
        # for more details.
        #
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL and obj.childCount:
            nonTableCellFound = False
            for child in obj:
                if child.getRole() != pyatspi.ROLE_TABLE_CELL:
                    nonTableCellFound = True
            if not nonTableCellFound:
                for child in obj:
                    try:
                        text = child.queryText()
                    except NotImplementedError:
                        continue
                    else:
                        if text.getText(0, text.characterCount):
                            activeDescendant = child

        self._script.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj] = \
            activeDescendant or obj
        return self._script.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]

    def showingDescendants(self, parent):
        """Given a parent that manages its descendants, return a list of
        Accessible children that are actually showing.  This algorithm
        was inspired a little by the srw_elements_from_accessible logic
        in Gnopernicus, and makes the assumption that the children of
        an object that manages its descendants are arranged in a row
        and column format.

        Arguments:
        - parent: The accessible which manages its descendants

        Returns a list of Accessible descendants which are showing.
        """

        import sys

        if not parent:
            return []

        if not parent.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or parent.childCount <= 50:
            return []

        try:
            icomponent = parent.queryComponent()
        except NotImplementedError:
            return []

        descendants = []

        parentExtents = icomponent.getExtents(0)

        # [[[TODO: WDW - HACK related to GAIL bug where table column
        # headers seem to be ignored:
        # http://bugzilla.gnome.org/show_bug.cgi?id=325809.  The
        # problem is that this causes getAccessibleAtPoint to return
        # the cell effectively below the real cell at a given point,
        # making a mess of everything.  So...we just manually add in
        # showing headers for now.  The remainder of the logic below
        # accidentally accounts for this offset, yet it should also
        # work when bug 325809 is fixed.]]]
        #
        try:
            table = parent.queryTable()
        except NotImplementedError:
            table = None

        if table:
            for i in range(0, table.nColumns):
                header = table.getColumnHeader(i)
                if header:
                    extents = header.queryComponent().getExtents(0)
                    stateset = header.getState()
                    if stateset.contains(pyatspi.STATE_SHOWING) \
                       and (extents.x >= 0) and (extents.y >= 0) \
                       and (extents.width > 0) and (extents.height > 0) \
                       and self.containsRegion(
                            extents.x, extents.y,
                            extents.width, extents.height,
                            parentExtents.x, parentExtents.y,
                            parentExtents.width, parentExtents.height):
                        descendants.append(header)

        # This algorithm goes left to right, top to bottom while attempting
        # to do *some* optimization over queries.  It could definitely be
        # improved. The gridSize is a minimal chunk to jump around in the
        # table.
        #
        gridSize = 7
        currentY = parentExtents.y
        while currentY < (parentExtents.y + parentExtents.height):
            currentX = parentExtents.x
            minHeight = sys.maxsize
            index = -1
            while currentX < (parentExtents.x + parentExtents.width):
                child = \
                    icomponent.getAccessibleAtPoint(currentX, currentY + 1, 0)
                if child:
                    index = child.getIndexInParent()
                    extents = child.queryComponent().getExtents(0)
                    if extents.x >= 0 and extents.y >= 0:
                        newX = extents.x + extents.width
                        minHeight = min(minHeight, extents.height)
                        if not descendants.count(child):
                            descendants.append(child)
                    else:
                        newX = currentX + gridSize
                else:
                    debug.println(debug.LEVEL_FINEST,
                            "script_utilities.showingDescendants failed. " \
                            "Last valid child at index %d" % index)
                    break
                if newX <= currentX:
                    currentX += gridSize
                else:
                    currentX = newX
            if minHeight == sys.maxsize:
                minHeight = gridSize
            currentY += minHeight

        return descendants

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

    @staticmethod
    def topLevelObject(obj):
        """Returns the top-level object (frame, dialog ...) containing obj,
        or None if obj is not inside a top-level object.

        Arguments:
        - obj: the Accessible object
        """

        if not obj:
            return None

        stopAtRoles = [pyatspi.ROLE_ALERT,
                       pyatspi.ROLE_DIALOG,
                       pyatspi.ROLE_FRAME,
                       pyatspi.ROLE_WINDOW]

        while obj and obj.parent \
              and not obj.getRole() in stopAtRoles \
              and not obj.parent.getRole() == pyatspi.ROLE_APPLICATION:
            obj = obj.parent

        return obj

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

    def _hasNonDescendableDescendant(self, root):
        roles = [pyatspi.ROLE_PAGE_TAB_LIST,
                 pyatspi.ROLE_SPLIT_PANE,
                 pyatspi.ROLE_TABLE]
        isMatch = lambda x: x and x.getRole() in roles
        return pyatspi.findDescendant(root, isMatch) is not None

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
        allLabels = pyatspi.findAllDescendants(root, hasRole)
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
        window = Utilities.topLevelObject(obj)
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

    def allSelectedText(self, obj):
        """Get all the text applicable text selections for the given object.
        including any previous or next text objects that also have
        selected text and add in their text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        textContents = ""
        startOffset = 0
        endOffset = 0
        text = obj.queryText()
        if text.getNSelections() > 0:
            [textContents, startOffset, endOffset] = self.selectedText(obj)

        current = obj
        morePossibleSelections = True
        while morePossibleSelections:
            morePossibleSelections = False
            for relation in current.getRelationSet():
                if relation.getRelationType() == pyatspi.RELATION_FLOWS_FROM:
                    prevObj = relation.getTarget(0)
                    prevObjText = prevObj.queryText()
                    if prevObjText.getNSelections() > 0:
                        [newTextContents, start, end] = \
                            self.selectedText(prevObj)
                        textContents = newTextContents + " " + textContents
                        current = prevObj
                        morePossibleSelections = True
                    else:
                        displayedText = prevObjText.getText(0,
                            prevObjText.characterCount)
                        if len(displayedText) == 0:
                            current = prevObj
                            morePossibleSelections = True
                    break

        current = obj
        morePossibleSelections = True
        while morePossibleSelections:
            morePossibleSelections = False
            for relation in current.getRelationSet():
                if relation.getRelationType() == pyatspi.RELATION_FLOWS_TO:
                    nextObj = relation.getTarget(0)
                    nextObjText = nextObj.queryText()
                    if nextObjText.getNSelections() > 0:
                        [newTextContents, start, end] = \
                            self.selectedText(nextObj)
                        textContents += " " + newTextContents
                        current = nextObj
                        morePossibleSelections = True
                    else:
                        displayedText = nextObjText.getText(0,
                            nextObjText.characterCount)
                        if len(displayedText) == 0:
                            current = nextObj
                            morePossibleSelections = True
                    break

        return [textContents, startOffset, endOffset]

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
            debug.println(debug.LEVEL_INFO, msg)
        else:
            # We need to make sure that this is an embedded object in
            # some accessible text (as opposed to an imagemap link).
            #
            try:
                obj.parent.queryText()
                offset = hyperlink.startIndex
            except:
                msg = "ERROR: Exception getting startIndex for %s in parent %s" % (obj, obj.parent)
                debug.println(debug.LEVEL_INFO, msg)
            else:
                msg = "INFO: startIndex of %s is %i" % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg)

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
                if Utilities.characterOffsetInParent(child) >= startOffset:
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

    @staticmethod
    def selectedText(obj):
        """Get the text selection for the given object.

        Arguments:
        - obj: the text object to extract the selected text from.

        Returns: the selected text contents plus the start and end
        offsets within the text.
        """

        textContents = ""
        startOffset = endOffset = 0
        textObj = obj.queryText()
        nSelections = textObj.getNSelections()
        for i in range(0, nSelections):
            [startOffset, endOffset] = textObj.getSelection(i)

            debug.println(debug.LEVEL_FINEST,
                "getSelectedText: selection start=%d, end=%d" % \
                (startOffset, endOffset))

            selectedText = textObj.getText(startOffset, endOffset)
            debug.println(debug.LEVEL_FINEST,
                "getSelectedText: selected text=<%s>" % selectedText)

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

    def setCaretPosition(self, obj, offset):
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

        for key, value in list(self._script.attributeNamesDict.items()):
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
        if role == pyatspi.ROLE_TERMINAL:
            return True
        if role == pyatspi.ROLE_PASSWORD_TEXT:
            return False

        if obj.getState().contains(pyatspi.STATE_EDITABLE):
            return True

        return False

    def wordAtCoords(self, acc, x, y):
        """Get the word at the given coords in the accessible.

        Arguments:
        - acc: Accessible that supports the Text interface.
        - x: X coordinate.
        - y: Y coordinate.

        Returns a tuple containing the word, start offset, and end offset.
        """

        try:
            ti = acc.queryText()
        except NotImplementedError:
            return '', 0, 0

        text_contents = ti.getText(0, ti.characterCount)
        line_offsets = []
        start_offset = 0
        while True:
            try:
                end_offset = text_contents.index('\n', start_offset)
            except ValueError:
                line_offsets.append((start_offset, len(text_contents)))
                break
            line_offsets.append((start_offset, end_offset))
            start_offset = end_offset + 1
        for start, end in line_offsets:
            bx, by, bw, bh = \
                ti.getRangeExtents(start, end, pyatspi.DESKTOP_COORDS)
            bb = mouse_review.BoundingBox(bx, by, bw, bh)
            if bb.isInBox(x, y):
                start_offset = 0
                word_offsets = []
                while True:
                    try:
                        end_offset = \
                            text_contents[start:end].index(' ', start_offset)
                    except ValueError:
                        word_offsets.append((start_offset,
                                             len(text_contents[start:end])))
                        break
                    word_offsets.append((start_offset, end_offset))
                    start_offset = end_offset + 1
                for a, b in word_offsets:
                    bx, by, bw, bh = \
                        ti.getRangeExtents(start+a, start+b,
                                           pyatspi.DESKTOP_COORDS)
                    bb = mouse_review.BoundingBox(bx, by, bw, bh)
                    if bb.isInBox(x, y):
                        return text_contents[start+a:start+b], start+a, start+b

        return '', 0, 0

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

            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey == "Tab" and event.any_data != "\t":
                return True
            if lastKey == "Return" and event.any_data != "\n":
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
               or character in '!*+,-./:;<=>?@[\]^_{|}' \
               or character == self._script.NO_BREAK_SPACE_CHARACTER

    @staticmethod
    def containsRegion(ax, ay, awidth, aheight, bx, by, bwidth, bheight):
        """Returns true if any portion of region 'a' is in region 'b'"""

        highestBottom = min(ay + aheight, by + bheight)
        lowestTop = max(ay, by)
        leftMostRightEdge = min(ax + awidth, bx + bwidth)
        rightMostLeftEdge = max(ax, bx)

        if lowestTop <= highestBottom \
           and rightMostLeftEdge <= leftMostRightEdge:
            return True
        elif aheight == 0:
            if awidth == 0:
                return lowestTop == highestBottom \
                       and leftMostRightEdge == rightMostLeftEdge
            else:
                return leftMostRightEdge <= rightMostLeftEdge
        elif awidth == 0:
            return lowestTop <= highestBottom

        return False

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

        debug.println(debug.LEVEL_FINEST, "script_utilities.getKeyBinding: " \
                      + repr([mnemonic, fullShortcut, accelerator]))

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
            debug.println(debug.LEVEL_FINEST, "VALUE WARNING: " \
                          "Error accessing maximumValue for %s" % obj)
        try:
            minValue = value.minimumValue
        except (LookupError, RuntimeError):
            minValue = 0.0
            debug.println(debug.LEVEL_FINEST, "VALUE WARNING: " \
                          "Error accessing minimumValue for %s" % obj)
        try:
            minIncrement = value.minimumIncrement
        except (LookupError, RuntimeError):
            minIncrement = (maxValue - minValue) / 100.0
            debug.println(debug.LEVEL_FINEST, "VALUE WARNING: " \
                          "Error accessing minimumIncrement for %s" % obj)

        if minIncrement != 0.0:
            try:
                decimalPlaces = math.ceil(max(0, -math.log10(minIncrement)))
            except ValueError:
                debug.println(debug.LEVEL_FINEST, "VALUE WARNING: " \
                    "Error calculating decimal places for %s" % obj)
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
        except NotImplementedError:
            msg = "INFO: %s does not implement the selection interface" % obj
            debug.println(debug.LEVEL_INFO, msg)
            return []
        except:
            msg = "ERROR: Exception querying selection interface for %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            return []

        count = selection.nSelectedChildren
        msg = "INFO: %s reports %i selected children" % (obj, count)
        debug.println(debug.LEVEL_INFO, msg)

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
                debug.println(debug.LEVEL_INFO, msg)

        if role == pyatspi.ROLE_COMBO_BOX \
           and children and children[0].getRole() == pyatspi.ROLE_MENU:
            children = self.selectedChildren(children[0])
            if not children and obj.name:
                pred = lambda x: x and x.name == obj.name
                try:
                    children = pyatspi.findAllDescendants(obj, pred)
                except:
                    msg = "ERROR: Exception calling findAllDescendants on %s" % obj
                    debug.println(debug.LEVEL_INFO, msg)

        return children

    def focusedChild(self, obj):
        isFocused = lambda x: x and x.getState().contains(pyatspi.STATE_FOCUSED)
        child = pyatspi.findDescendant(obj, isFocused)
        if child == obj:
            msg = "ERROR: focused child of %s is %s" % (obj, child)
            debug.println(debug.LEVEL_INFO, msg)
            return None

        return child

    def _isNonModalPopOver(self, obj):
        return False

    def rgbFromString(self, attributeValue):
        regex = re.compile("rgb|[^\w,]", re.IGNORECASE)
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
            return 0
        return int(attrs.get('level', '0'))

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

    def cellForCoordinates(self, obj, row, column):
        try:
            table = obj.queryTable()
        except:
            return None

        return table.getAccessibleAt(row, column)

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

    def isZombie(self, obj):
        try:
            index = obj.getIndexInParent()
            state = obj.getState()
            role = obj.getRole()
        except:
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s is null or dead" % obj)
            return True

        topLevelRoles = [pyatspi.ROLE_APPLICATION,
                         pyatspi.ROLE_ALERT,
                         pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_WINDOW,
                         pyatspi.ROLE_FRAME]
        if index == -1 and role not in topLevelRoles:
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s's index is -1" % obj)
            return True
        if state.contains(pyatspi.STATE_DEFUNCT):
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s is defunct" % obj)
            return True
        if state.contains(pyatspi.STATE_INVALID):
            debug.println(debug.LEVEL_INFO, "ZOMBIE: %s is invalid" % obj)
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
                debug.println(debug.LEVEL_INFO, msg)
                replicant = None

        msg = "HACK: Returning %s as replicant for Zombie %s" % (replicant, obj)
        debug.println(debug.LEVEL_INFO, msg)
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

        position = siblings.index(obj)
        setSize = len(siblings)
        return position, setSize
