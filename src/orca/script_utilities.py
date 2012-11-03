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

import math
import pyatspi
import re

from . import debug
from . import keynames
from . import input_event
from . import mouse_review
from . import orca_state
from . import settings

from .orca_i18n import _
from .orca_i18n import ngettext

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities:

    EMBEDDED_OBJECT_CHARACTER = u'\ufffc'
    SUPERSCRIPT_DIGITS = \
        [u'\u2070', u'\u00b9', u'\u00b2', u'\u00b3', u'\u2074',
         u'\u2075', u'\u2076', u'\u2077', u'\u2078', u'\u2079']
    SUBSCRIPT_DIGITS = \
        [u'\u2080', u'\u2081', u'\u2082', u'\u2083', u'\u2084',
         u'\u2085', u'\u2086', u'\u2087', u'\u2088', u'\u2089']

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
    def __hasLabelForRelation(label):
        """Check if label has a LABEL_FOR relation

        Arguments:
        - label: the label in question

        Returns TRUE if label has a LABEL_FOR relation.
        """
        if (not label) or (label.getRole() != pyatspi.ROLE_LABEL):
            return False

        relations = label.getRelationSet()

        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_LABEL_FOR:
                return True

        return False

    @staticmethod
    def __isLabeling(label, obj):
        """Check if label is connected via  LABEL_FOR relation with object

        Arguments:
        - obj: the object in question
        - labeled: the label in question

        Returns TRUE if label has a relation LABEL_FOR for object.
        """

        if not obj or not label or label.getRole() != pyatspi.ROLE_LABEL:
            return False

        relations = label.getRelationSet()
        if not relations:
            return False

        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_LABEL_FOR:
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    if target == obj:
                        return True

        return False

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
    def allDescendants(root, onlyShowing=True):
        """Returns a list of all objects under the given root.  Objects
        are returned in no particular order - this function does a simple
        tree traversal, ignoring the children of objects which report the
        MANAGES_DESCENDANTS state.

        Arguments:
        - root: the Accessible object to traverse
        - onlyShowing: examine only those objects that are SHOWING

        Returns: a list of all objects under the specified object
        """

        if root.childCount <= 0:
            return []

        objlist = []
        for i, child in enumerate(root):
            debug.println(debug.LEVEL_FINEST,
                          "Script.allDescendants looking at child %d" % i)
            if child \
               and ((not onlyShowing) or (onlyShowing and \
                    (child.getState().contains(pyatspi.STATE_SHOWING)))):
                objlist.append(child)
                if (child.getState().contains( \
                    pyatspi.STATE_MANAGES_DESCENDANTS) == 0) \
                    and (child.childCount > 0):
                    objlist.extend(Utilities.allDescendants(child, onlyShowing))

        return objlist

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
                        nodes.append(relation.getTarget(target))
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
            if container.getRole() == pyatspi.ROLE_PAGE_TAB_LIST:
                try:
                    si = container.querySelection()
                    container = si.getSelectedChild(0)[0]
                except NotImplementedError:
                    pass
            try:
                ci = container.queryComponent()
            except:
                return None
            else:
                inner_container = container
            container =  ci.getAccessibleAtPoint(x, y, pyatspi.DESKTOP_COORDS)
            if not container or container.queryComponent() == ci:
                break
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

    @staticmethod
    def descendantsWithRole(root, role, onlyShowing=True):
        """Returns a list of all objects of a specific role beneath the
        given root.

        Arguments:
        - root: the Accessible object to traverse
        - role: the string describing the Accessible role of the object
        - onlyShowing: examine only those objects that are SHOWING

        Returns a list of descendants of the root that are of the given role.
        """

        allObjs = Utilities.allDescendants(root, onlyShowing)
        return [o for o in allObjs if o.getRole() == role]

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

    def _displayedTextInComboBox(self, combo):

        """Returns the text being displayed in a combo box.  If nothing is
        displayed, then None is returned.

        Arguments:
        - combo: the combo box

        Returns the text in the combo box or an empty string if nothing is
        displayed.
        """

        displayedText = None

        # Find the text displayed in the combo box.  This is either:
        #
        # 1) The last text object that's a child of the combo box
        # 2) The selected child of the combo box.
        # 3) The contents of the text of the combo box itself when
        #    treated as a text object.
        #
        # Preference is given to #1, if it exists.
        #
        # If the label of the combo box is the same as the utterance for
        # the child object, then this utterance is only displayed once.
        #
        # [[[TODO: WDW - Combo boxes are complex beasts.  This algorithm
        # needs serious work.  Logged as bugzilla bug 319745.]]]
        #
        textObj = None
        for child in combo:
            if child and child.getRole() == pyatspi.ROLE_TEXT:
                textObj = child

        if textObj:
            [displayedText, caretOffset, startOffset] = \
                self._script.getTextLineAtCaret(textObj)
            #print "TEXTOBJ", displayedText
        else:
            try:
                comboSelection = combo.querySelection()
                selectedItem = comboSelection.getSelectedChild(0)
            except:
                selectedItem = None

            if selectedItem:
                displayedText = self.displayedText(selectedItem)
                #print "SELECTEDITEM", displayedText
                if displayedText:
                    return displayedText
            if combo.name and len(combo.name):
                # We give preference to the name over the text because
                # the text for combo boxes seems to never change in
                # some cases.  The main one where we see this is in
                # the gaim "Join Chat" window.
                #
                displayedText = combo.name
                #print "NAME", displayedText
            else:
                [displayedText, caretOffset, startOffset] = \
                    self._script.getTextLineAtCaret(combo)
                # Set to None instead of empty string.
                displayedText = displayedText or None
                #print "TEXT", displayedText

        return displayedText

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

        if role == pyatspi.ROLE_COMBO_BOX:
            displayedText = self._displayedTextInComboBox(obj)
            if self.DISPLAYED_TEXT not in self._script.generatorCache:
                self._script.generatorCache[self.DISPLAYED_TEXT] = {}
            self._script.generatorCache[self.DISPLAYED_TEXT][obj] = \
                displayedText
            return self._script.generatorCache[self.DISPLAYED_TEXT][obj]

        # The accessible text of an object is used to represent what is
        # drawn on the screen.
        #
        try:
            text = obj.queryText()
        except NotImplementedError:
            pass
        else:
            displayedText = text.getText(0, self._script.getTextEndOffset(text))

            # [[[WDW - HACK to account for things such as Gecko that want
            # to use the EMBEDDED_OBJECT_CHARACTER on a label to hold the
            # object that has the real accessible text for the label.  We
            # detect this by the specfic case where the text for the
            # current object is a single EMBEDDED_OBJECT_CHARACTER.  In
            # this case, we look to the child for the real text.]]]
            #
            unicodeText = displayedText.decode("UTF-8")
            if unicodeText \
               and len(unicodeText) == 1 \
               and unicodeText[0] == self.EMBEDDED_OBJECT_CHARACTER \
               and obj.childCount > 0:
                try:
                    displayedText = self.displayedText(obj[0])
                except:
                    debug.printException(debug.LEVEL_WARNING)
            elif unicodeText:
                # [[[TODO: HACK - Welll.....we'll just plain ignore any
                # text with EMBEDDED_OBJECT_CHARACTERs here.  We still need a
                # general case to handle this stuff and expand objects
                # with EMBEDDED_OBJECT_CHARACTERs.]]]
                #
                for i in range(len(unicodeText)):
                    if unicodeText[i] == self.EMBEDDED_OBJECT_CHARACTER:
                        displayedText = None
                        break

        if not displayedText:
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

    def documentFrame(self):
        """Returns the document frame which is displaying the content.
        Note that this is intended primarily for web content."""

        return None

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

        if obj and obj.getRole() == pyatspi.ROLE_ENTRY \
           and obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            return True

        return False

    def isFunctionalDialog(self, obj):
        """Returns True if the window is a functioning as a dialog.
        This method should be subclassed by application scripts as
        needed.
        """

        return False

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a table and is for layout
        purposes only."""

        layoutOnly = False

        try:
            attributes = obj.getAttributes()
        except:
            attributes = None
        try:
            role = obj.getRole()
        except:
            role = None

        if role == pyatspi.ROLE_TABLE and attributes:
            for attribute in attributes:
                if attribute == "layout-guess:true":
                    layoutOnly = True
                    break
        elif role == pyatspi.ROLE_PANEL:
            text = self.displayedText(obj)
            label = self.displayedLabel(obj)
            if not ((label and len(label)) or (text and len(text))):
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

    def isSameObject(self, obj1, obj2):
        if (obj1 == obj2):
            return True
        elif (not obj1) or (not obj2):
            return False

        try:
            if (obj1.name != obj2.name) or (obj1.getRole() != obj2.getRole()):
                return False
            else:
                # Gecko sometimes creates multiple accessibles to represent
                # the same object.  If the two objects have the same name
                # and the same role, check the extents.  If those also match
                # then the two objects are for all intents and purposes the
                # same object.
                #
                extents1 = \
                    obj1.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                extents2 = \
                    obj2.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                if (extents1.x == extents2.x) and \
                   (extents1.y == extents2.y) and \
                   (extents1.width == extents2.width) and \
                   (extents1.height == extents2.height):
                    return True

            # When we're looking at children of objects that manage
            # their descendants, we will often get different objects
            # that point to the same logical child.  We want to be able
            # to determine if two objects are in fact pointing to the
            # same child.
            # If we cannot do so easily (i.e., object equivalence), we examine
            # the hierarchy and the object index at each level.
            #
            parent1 = obj1
            parent2 = obj2
            while (parent1 and parent2 and \
                    parent1.getState().contains( \
                        pyatspi.STATE_TRANSIENT) and \
                    parent2.getState().contains(pyatspi.STATE_TRANSIENT)):
                if parent1.getIndexInParent() != parent2.getIndexInParent():
                    return False
                parent1 = parent1.parent
                parent2 = parent2.parent
            if parent1 and parent2 and parent1 == parent2:
                return self.realActiveDescendant(obj1).name == \
                       self.realActiveDescendant(obj2).name
        except:
            pass

        # [[[TODO - JD: Why is this here? If it is truly limited to the
        # Java toolkit, it should be dealt with in Orca's Java toolkit
        # script. If it applies more broadly we should update the comment
        # to reflect that.]]]
        #
        # In java applications, TRANSIENT state is missing for tree items
        # (fix for bug #352250)
        #
        try:
            parent1 = obj1
            parent2 = obj2
            while parent1 and parent2 and \
                    parent1.getRole() == pyatspi.ROLE_LABEL and \
                    parent2.getRole() == pyatspi.ROLE_LABEL:
                if parent1.getIndexInParent() != parent2.getIndexInParent():
                    return False
                parent1 = parent1.parent
                parent2 = parent2.parent
            if parent1 and parent2 and parent1 == parent2:
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

        # [[[TODO: HACK - we've discovered oddness in hierarchies such as
        # the gedit Edit->Preferences dialog.  In this dialog, we have
        # labeled groupings of objects.  The grouping is done via a FILLER
        # with two children - one child is the overall label, and the
        # other is the container for the grouped objects.  When we detect
        # this, we add the label to the overall context.
        #
        # We are also looking for objects which have a PANEL or a FILLER as
        # parent, and its parent has more children. Through these children,
        # a potential label with LABEL_FOR relation may exists. We want to
        # present this label.
        # This case can be seen in FileChooserDemo application, in Open dialog
        # window, the line with "Look In" label, a combobox and some
        # presentation buttons.
        #
        # Finally, we are searching the hierarchy of embedded components for
        # children that are labels.]]]
        #
        if not len(label):
            potentialLabels = []
            useLabel = False
            if (obj.getRole() == pyatspi.ROLE_EMBEDDED):
                candidate = obj
                while candidate.childCount:
                    candidate = candidate[0]
                # The parent of this object may contain labels
                # or it may contain filler that contains labels.
                #
                candidate = candidate.parent
                for child in candidate:
                    if child.getRole() == pyatspi.ROLE_FILLER:
                        candidate = child
                        break
                # If there are labels in this embedded component,
                # they should be here.
                #
                for child in candidate:
                    if child.getRole() == pyatspi.ROLE_LABEL:
                        useLabel = True
                        potentialLabels.append(child)
            elif ((obj.getRole() == pyatspi.ROLE_FILLER) \
                    or (obj.getRole() == pyatspi.ROLE_PANEL)) \
                and (obj.childCount == 2):
                child0, child1 = obj
                child0_role = child0.getRole()
                child1_role = child1.getRole()
                if child0_role == pyatspi.ROLE_LABEL \
                    and not self.__hasLabelForRelation(child0) \
                    and child1_role in [pyatspi.ROLE_FILLER, \
                                             pyatspi.ROLE_PANEL]:
                    useLabel = True
                    potentialLabels.append(child0)
                elif child1_role == pyatspi.ROLE_LABEL \
                    and not self.__hasLabelForRelation(child1) \
                    and child0_role in [pyatspi.ROLE_FILLER, \
                                             pyatspi.ROLE_PANEL]:
                    useLabel = True
                    potentialLabels.append(child1)
            else:
                parent = obj.parent
                try:
                    parentRole = parent.getRole()
                except:
                    parentRole = None
                if parentRole in [pyatspi.ROLE_FILLER, pyatspi.ROLE_PANEL]:
                    for potentialLabel in parent:
                        try:
                            useLabel = self.__isLabeling(potentialLabel, obj)
                            if useLabel:
                                potentialLabels.append(potentialLabel)
                                break
                        except:
                            pass

            if useLabel and len(potentialLabels):
                label = potentialLabels

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

        if not obj:
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

    @staticmethod
    def pursueForFlatReview(obj):
        """Determines if we should look any further at the object
        for flat review."""

        try:
            state = obj.getState()
        except:
            debug.printException(debug.LEVEL_WARNING)
            return False
        else:
            return state.contains(pyatspi.STATE_SHOWING)

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
                        if text.getText(0, self._script.getTextEndOffset(text)):
                            activeDescendant = child

        # [[[TODO: WDW - this is an odd hacky thing I've somewhat drawn
        # from Gnopernicus.  The notion here is that we get an active
        # descendant changed event, but that object tends to have children
        # itself and we need to decide what to do.  Well...the idea here
        # is that the last child (Gnopernicus chooses child(1)), tends to
        # be the child with information.  The previous children tend to
        # be non-text or just there for spacing or something.  You will
        # see this in the various table demos of gtk-demo and you will
        # also see this in the Contact Source Selector in Evolution.
        #
        # Just note that this is most likely not a really good solution
        # for the general case.  That needs more thought.  But, this
        # comment is here to remind us this is being done in poor taste
        # and we need to eventually clean up our act.]]]
        #
        if not activeDescendant and obj and obj.childCount >= 0:
            try:
                activeDescendant = obj[-1]
            except:
                pass

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
                       and self.isVisibleRegion(
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

        while obj and obj.parent and (obj != obj.parent) \
              and (obj.parent.getRole() != pyatspi.ROLE_APPLICATION):
            obj = obj.parent

        if obj and obj.parent and \
           (obj.parent.getRole() == pyatspi.ROLE_APPLICATION):
            pass
        else:
            obj = None

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
        rv = max(rv, -1)
        rv = min(rv, 1)

        return rv

    def unrelatedLabels(self, root):
        """Returns a list containing all the unrelated (i.e., have no
        relations to anything and are not a fundamental element of a
        more atomic component like a combo box) labels under the given
        root.  Note that the labels must also be showing on the display.

        Arguments:
        - root the Accessible object to traverse

        Returns a list of unrelated labels under the given root.
        """

        allLabels = self.descendantsWithRole(root, pyatspi.ROLE_LABEL)
        labels = [x for x in allLabels if not x.getRelationSet()]
        labels = [x for x in labels if x.parent and x.name != x.parent.name]
        labels = [x for x in labels if x.getState().contains(pyatspi.STATE_SHOWING)]

        # Eliminate duplicates
        d = {}
        for label in labels:
            d[label.name] = label
        labels = list(d.values())

        return sorted(labels, self.spatialComparison)

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
                            self._script.getTextEndOffset(prevObjText))
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
                            self._script.getTextEndOffset(nextObjText))
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

    @staticmethod
    def characterOffsetInParent(obj):
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
            pass
        else:
            # We need to make sure that this is an embedded object in
            # some accessible text (as opposed to an imagemap link).
            #
            try:
                obj.parent.queryText()
                offset = hyperlink.startIndex
            except:
                pass

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

        string = self.substring(obj, startOffset, endOffset)
        if string:
            unicodeText = string.decode("UTF-8")
            if unicodeText and self.EMBEDDED_OBJECT_CHARACTER in unicodeText:
                # If we're not getting the full text of this object, but
                # rather a substring, we need to figure out the offset of
                # the first child within this substring.
                #
                childOffset = 0
                for child in obj:
                    if Utilities.characterOffsetInParent(child) >= startOffset:
                        break
                    childOffset += 1

                toBuild = list(unicodeText)
                count = toBuild.count(self.EMBEDDED_OBJECT_CHARACTER)
                for i in range(count):
                    index = toBuild.index(self.EMBEDDED_OBJECT_CHARACTER)
                    child = obj[i + childOffset]
                    childText = self.expandEOCs(child)
                    if not childText:
                        childText = ""
                    try:
                        toBuild[index] = childText.decode("UTF-8")
                    except UnicodeEncodeError:
                        toBuild[index] = childText
                string = "".join(toBuild)

        return string

    def hasTextSelections(self, obj):
        """Return an indication of whether this object has selected text.
        Note that it's possible that this object has no selection, but is part
        of a selected text area. Because of this, we need to check the
        objects on either side to see if they are none zero length and
        have text selections.

        Arguments:
        - obj: the text object to start checking for selected text.

        Returns: an indication of whether this object has selected text,
        or adjacent text objects have selected text.
        """

        currentSelected = False
        otherSelected = False
        text = obj.queryText()
        nSelections = text.getNSelections()
        if nSelections:
            currentSelected = True
        else:
            otherSelected = False
            text = obj.queryText()
            displayedText = text.getText(0, self._script.getTextEndOffset(text))
            if (text.caretOffset == 0) or len(displayedText) == 0:
                current = obj
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    for relation in current.getRelationSet():
                        if relation.getRelationType() == \
                               pyatspi.RELATION_FLOWS_FROM:
                            prevObj = relation.getTarget(0)
                            prevObjText = prevObj.queryText()
                            if prevObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = prevObjText.getText(0,
                                    self._script.getTextEndOffset(prevObjText))
                                if len(displayedText) == 0:
                                    current = prevObj
                                    morePossibleSelections = True
                            break

                current = obj
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    for relation in current.getRelationSet():
                        if relation.getRelationType() == \
                               pyatspi.RELATION_FLOWS_TO:
                            nextObj = relation.getTarget(0)
                            nextObjText = nextObj.queryText()
                            if nextObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = nextObjText.getText(0,
                                    self._script.getTextEndOffset(nextObjText))
                                if len(displayedText) == 0:
                                    current = nextObj
                                    morePossibleSelections = True
                            break

        return [currentSelected, otherSelected]

    @staticmethod
    def isTextSelected(obj, startOffset, endOffset):
        """Returns an indication of whether the text is selected by
        comparing the text offset with the various selected regions of
        text for this accessible object.

        Arguments:
        - obj: the Accessible object.
        - startOffset: text start offset.
        - endOffset: text end offset.

        Returns an indication of whether the text is selected.
        """

        if startOffset == endOffset:
            return False

        try:
            text = obj.queryText()
        except:
            return False

        for i in range(text.getNSelections()):
            [startSelOffset, endSelOffset] = text.getSelection(i)
            if (startOffset >= startSelOffset) and (endOffset <= endSelOffset):
                return True

        return False

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

        return False

    def offsetsForPhrase(self, obj):
        """Return the start and end offset for the given phrase

        Arguments:
        - obj: the Accessible object
        """

        try:
            text = obj.queryText()
        except:
            return [0, 0]

        lastPos = self._script.pointOfReference.get("lastCursorPosition")
        startOffset = lastPos[1]
        endOffset = text.caretOffset

        # Swap values if in wrong order.
        #
        if (startOffset > endOffset and endOffset != -1) or startOffset == -1:
            temp = endOffset
            endOffset = startOffset
            startOffset = temp

        return [startOffset, endOffset]

    def offsetsForLine(self, obj):
        """Return the start and end offset for the given line

        Arguments:
        - obj: the Accessible object
        """

        lineAndOffsets = self._script.getTextLineAtCaret(obj)
        return [lineAndOffsets[1], lineAndOffsets[2]]

    def offsetsForWord(self, obj):
        """Return the start and end offset for the given word

        Arguments:
        - obj: the Accessible object
        """

        try:
            text = obj.queryText()
        except:
            return [0, 0]

        wordAndOffsets = text.getTextAtOffset(
            text.caretOffset, pyatspi.TEXT_BOUNDARY_WORD_START)

        return [wordAndOffsets[1], wordAndOffsets[2]]

    def offsetsForChar(self, obj):
        """Return the start and end offset for the given character

        Arguments:
        - obj: the Accessible object
        """

        try:
            text = obj.queryText()
        except:
            return [0, 0]

        lastKey, mods = self.lastKeyAndModifiers()
        if mods & settings.SHIFT_MODIFIER_MASK and lastKey == "Right":
            startOffset = text.caretOffset - 1
            endOffset = text.caretOffset
        else:
            startOffset = text.caretOffset
            endOffset = text.caretOffset + 1

        return [startOffset, endOffset]

    @staticmethod
    def queryNonEmptyText(obj):
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

    def textAttributes(self, acc, offset, get_defaults=False):
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
            stringAndDict = \
                self.stringToKeysAndDict(text.getDefaultAttributes())
            rv.update(stringAndDict[1])

        attrString, start, end = text.getAttributes(offset)
        stringAndDict = self.stringToKeysAndDict(attrString)
        rv.update(stringAndDict[1])

        return rv, start, end

    def unicodeText(self, obj):
        """Returns the unicode text for an object or None if the object
        doesn't implement the accessible text specialization.
        """

        text = self.queryNonEmptyText(obj)
        if text:
            unicodeText = text.getText(0, -1).decode("UTF-8")
        else:
            unicodeText = None

        return unicodeText

    def willEchoCharacter(self, event):
        """Given a keyboard event containing an alphanumeric key,
        determine if the script is likely to echo it as a character.
        """

        if not orca_state.locusOfFocus or not settings.enableEchoByCharacter:
            return False

        # The check here in English is something like this: "If this
        # character echo is enabled, then character echo is likely to
        # happen if the locus of focus is a focusable editable text
        # area or terminal and neither of the Ctrl, Alt, or Orca
        # modifiers are pressed.  If that's the case, then character
        # echo will kick in for us."
        #
        return (self.isTextArea(orca_state.locusOfFocus)\
                     or orca_state.locusOfFocus.getRole() \
                        == pyatspi.ROLE_ENTRY) \
                and (orca_state.locusOfFocus.getRole() \
                     == pyatspi.ROLE_TERMINAL \
                     or (not self.isReadOnlyTextArea(orca_state.locusOfFocus) \
                         and (orca_state.locusOfFocus.getState().contains( \
                                  pyatspi.STATE_FOCUSABLE)))) \
                and not (event.modifiers & settings.ORCA_CTRL_MODIFIER_MASK)

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

        text_contents = ti.getText(0, self._script.getTextEndOffset(ti))
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
    # Debugging and Reporting Utilities                                     #
    #                                                                       #
    #########################################################################

    def _isInterestingObj(self, obj):
        import inspect

        interesting = False

        if getattr(obj, "__class__", None):
            name = obj.__class__.__name__
            if name not in ["function",
                            "type",
                            "list",
                            "dict",
                            "tuple",
                            "wrapper_descriptor",
                            "module",
                            "method_descriptor",
                            "member_descriptor",
                            "instancemethod",
                            "builtin_function_or_method",
                            "frame",
                            "classmethod",
                            "classmethod_descriptor",
                            "_Environ",
                            "MemoryError",
                            "_Printer",
                            "_Helper",
                            "getset_descriptor",
                            "weakref",
                            "property",
                            "cell",
                            "staticmethod",
                            "EventListener",
                            "KeystrokeListener",
                            "KeyBinding",
                            "InputEventHandler",
                            "Rolename"]:
                try:
                    filename = inspect.getabsfile(obj.__class__)
                    if filename.index("orca"):
                        interesting = True
                except:
                    pass

        return interesting

    def _detectCycle(self, obj, visitedObjs, indent=""):
        """Attempts to discover a cycle in object references."""

        # [[[TODO: WDW - not sure this really works.]]]

        import gc
        visitedObjs.append(obj)
        for referent in gc.get_referents(obj):
            try:
                if visitedObjs.index(referent):
                    if self._isInterestingObj(referent):
                        print(indent, "CYCLE!!!!", repr(referent))
                    break
            except:
                pass
            self._detectCycle(referent, visitedObjs, " " + indent)
        visitedObjs.remove(obj)

    def printAncestry(self, child):
        """Prints a hierarchical view of a child's ancestry."""

        if not child:
            return

        ancestorList = [child]
        parent = child.parent
        while parent and (parent.parent != parent):
            ancestorList.insert(0, parent)
            parent = parent.parent

        indent = ""
        for ancestor in ancestorList:
            line = indent + "+- " + \
                debug.getAccessibleDetails(debug.LEVEL_OFF, ancestor)
            debug.println(debug.LEVEL_OFF, line)
            print(line)
            indent += "  "

    def printApps(self):
        """Prints a list of all applications to stdout."""

        apps = self.knownApplications()
        line = "There are %d Accessible applications" % len(apps)
        debug.println(debug.LEVEL_OFF, line)
        print(line)
        for app in apps:
            line = debug.getAccessibleDetails(
                debug.LEVEL_OFF, app, "  App: ", False)
            debug.println(debug.LEVEL_OFF, line)
            print(line)
            for child in app:
                line = debug.getAccessibleDetails(
                    debug.LEVEL_OFF, child, "    Window: ", False)
                debug.println(debug.LEVEL_OFF, line)
                print(line)
                if child.parent != app:
                    debug.println(debug.LEVEL_OFF,
                                  "      WARNING: child's parent is not app!!!")

        return True

    def printHierarchy(self, root, ooi, indent="",
                       onlyShowing=True, omitManaged=True):
        """Prints the accessible hierarchy of all children

        Arguments:
        -indent:      Indentation string
        -root:        Accessible where to start
        -ooi:         Accessible object of interest
        -onlyShowing: If True, only show children painted on the screen
        -omitManaged: If True, omit children that are managed descendants
        """

        if not root:
            return

        if root == ooi:
            line = indent + "(*) " + debug.getAccessibleDetails(
                debug.LEVEL_OFF, root)
        else:
            line = indent + "+- " + debug.getAccessibleDetails(
                debug.LEVEL_OFF, root)

        debug.println(debug.LEVEL_OFF, line)
        print(line)

        rootManagesDescendants = root.getState().contains(
            pyatspi.STATE_MANAGES_DESCENDANTS)

        for child in root:
            if child == root:
                line = indent + "  " + "WARNING CHILD == PARENT!!!"
                debug.println(debug.LEVEL_OFF, line)
                print(line)
            elif not child:
                line = indent + "  " + "WARNING Child IS NONE!!!"
                debug.println(debug.LEVEL_OFF, line)
                print(line)
            elif self.validParent(child) != root:
                line = indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
                debug.println(debug.LEVEL_OFF, line)
                print(line)
            else:
                paint = (not onlyShowing) or (onlyShowing and \
                         child.getState().contains(pyatspi.STATE_SHOWING))
                paint = paint \
                        and ((not omitManaged) \
                             or (omitManaged and not rootManagesDescendants))

                if paint:
                    self.printHierarchy(child,
                                        ooi,
                                        indent + "  ",
                                        onlyShowing,
                                        omitManaged)

    def scriptInfo(self):
        """Output useful information on the current script via speech
        and braille.  This information will be helpful to script writers.
        """

        infoString = "SCRIPT INFO: Script name='%s'" % self._script.name
        app = orca_state.locusOfFocus.getApplication()
        if orca_state.locusOfFocus and app:
            infoString += " Application name='%s'" \
                          % app.name

            try:
                infoString += " Toolkit name='%s'" \
                              % app.toolkitName
            except:
                infoString += " Toolkit unknown"

            try:
                infoString += " Version='%s'" \
                              % app.toolkitVersion
            except:
                infoString += " Version unknown"

            debug.println(debug.LEVEL_OFF, infoString)
            print(infoString)
            self._script.speakMessage(infoString)
            self._script.displayBrailleMessage(infoString)

        return True

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

        try:
            line = line.decode("UTF-8")
        except UnicodeEncodeError:
            pass

        try:
            segment = segment.decode("UTF-8")
        except UnicodeEncodeError:
            pass

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
                # Translators: Orca will tell you how many characters
                # are repeated on a line of text.  For example: "22
                # space characters".  The %d is the number and the %s
                # is the spoken word for the character.
                #
                repeatSegment = ngettext("%(count)d %(repeatChar)s character",
                                "%(count)d %(repeatChar)s characters",
                                 count) \
                                 % {"count" : count, "repeatChar": repeatChar}

                try:
                    repeatSegment = repeatSegment.decode("UTF-8")
                except UnicodeEncodeError:
                    pass

                line = "%s %s" % (line, repeatSegment)
            else:
                line += segment
        else:
            line += segment

        return line

    def _pronunciationForSegment(self, segment):
        """Adjust the word segment to potentially replace it with what
        those words actually sound like. Two pronunciation dictionaries
        are checked. First the application specific one (which might be
        empty), then the default (global) one.

        Arguments:
        - segment: the string to adjust for words in the pronunciation
          dictionaries.

        Returns: a new word segment adjusted for words found in the
        pronunciation dictionaries, or the original word segment if there
        was no dictionary entry.
        """

        from . import pronunciation_dict

        newSegment = pronunciation_dict.getPronunciation(
            segment, self._script.app_pronunciation_dict)

        if isinstance(segment, unicode):
            segment = segment.encode('UTF-8')
        if isinstance(newSegment, unicode):
            newSegment = newSegment.encode('UTF-8')

        if newSegment == segment:
            newSegment = pronunciation_dict.getPronunciation(segment)

        return newSegment

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

        try:
            line = line.decode("UTF-8")
        except UnicodeEncodeError:
            pass

        endOffset = startOffset + len(line)

        try:
            hyperText = obj.queryHypertext()
            nLinks = hyperText.getNLinks()
        except:
            nLinks = 0

        adjustedLine = list(line)
        for n in range(nLinks, 0, -1):
            link = hyperText.getLink(n - 1)

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

            # Translators: this indicates that this piece of
            # text is a hypertext link.
            #
            linkString = " " + _("link").decode("UTF-8")

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

        return "".join(adjustedLine).encode("UTF-8")

    def adjustForPronunciation(self, line):
        """Adjust the line to replace words in the pronunciation dictionary,
        with what those words actually sound like.

        Arguments:
        - line: the string to adjust for words in the pronunciation dictionary.

        Returns: a new line adjusted for words found in the pronunciation
        dictionary.
        """

        newLine = ""
        try:
            line = line.decode("UTF-8")
        except UnicodeEncodeError:
            pass

        words = self.WORDS_RE.split(line)
        newLine = ''.join(map(self._pronunciationForSegment, words))

        try:
            newLine = newLine.encode("UTF-8")
        except UnicodeDecodeError:
            pass

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

        try:
            line = line.decode("UTF-8")
        except UnicodeEncodeError:
            pass

        if (len(line) < 4) or (settings.repeatCharacterLimit < 4):
            return line.encode("UTF-8")

        newLine = u''
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

        newLine = self._addRepeatSegment(segment, newLine, multipleChars)

        # Pylint is confused and flags this with the following error:
        #
        # E1103:5188:Script.adjustForRepeats: Instance of 'True' has
        # no 'encode' member (but some types could not be inferred)
        #
        # We know newLine is a unicode string, so we'll just tell pylint
        # that we know what we are doing.
        #
        # pylint: disable-msg=E1103

        try:
            newLine = newLine.encode("UTF-8")
        except UnicodeDecodeError:
            pass

        return newLine

    def adjustForDigits(self, string):
        """Adjusts the string to convert digit-like text, such as subscript
        and superscript numbers, into actual digits.

        Arguments:
        - string: the string to be adjusted

        Returns: a new string which contains actual digits.
        """

        try:
            uString = string.decode("UTF-8")
        except UnicodeEncodeError:
            uString = string

        subscripted = set(re.findall(self.SUBSCRIPTS_RE, uString))
        superscripted = set(re.findall(self.SUPERSCRIPTS_RE, uString))

        for number in superscripted:
            new = [str(self.SUPERSCRIPT_DIGITS.index(d)) for d in number]
            # Translators: This string is part of the presentation of an
            # item that includes one or several consequtive superscripted
            # characters, e.g. 'X' followed by 'superscript 2' followed by
            # 'superscript 3' should be presented as 'X superscript 23'.
            #
            newString = _(" superscript %s") % "".join(new)
            try:
                newString = newString.decode("UTF-8")
            except UnicodeEncodeError:
                pass
            uString = re.sub(number, newString, uString)

        for number in subscripted:
            new = [str(self.SUBSCRIPT_DIGITS.index(d)) for d in number]
            # Translators: This string is part of the presentation of an
            # item that includes one or several consequtive subscripted
            # characters, e.g. 'X' followed by 'subscript 2' followed by
            # 'subscript 3', should be presented as 'X subscript 23.'
            #
            newString = _(" subscript %s") % "".join(new)
            uString = re.sub(number, newString, uString)
            try:
                newString = newString.decode("UTF-8")
            except UnicodeEncodeError:
                pass
        try:
            uString = uString.encode("UTF-8")
        except UnicodeDecodeError:
            pass

        return uString

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

        try:
            text = text.decode("UTF-8")
        except UnicodeEncodeError:
            pass

        try:
            newText = newText.decode("UTF-8")
        except UnicodeEncodeError:
            pass

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

        if not isinstance(currentChar, unicode):
            currentChar = currentChar.decode("UTF-8")

        if not isinstance(previousChar, unicode):
            previousChar = previousChar.decode("UTF-8")

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

        if not isinstance(character, unicode):
            character = character.decode("UTF-8")

        return character in self._script.whitespace \
               or character in '!*+,-./:;<=>?@[\]^_{|}' \
               or character == self._script.NO_BREAK_SPACE_CHARACTER

    @staticmethod
    def isVisibleRegion(ax, ay, awidth, aheight, bx, by, bwidth, bheight):
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
            eventStr = orca_state.lastNonModifierKeyEvent.event_string
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
                # Translators: this is the spoken word for the space character
                #
                sequence += _("space")
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
            bindingStrings = action.getKeyBinding(0).decode("UTF-8").split(';')
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
            if not isinstance(character, unicode):
                character = character.decode('UTF-8')
            return "%04x" % ord(character)
        except:
            debug.printException(debug.LEVEL_WARNING)
            return ""

    def getObjectsFromEOCs(self, obj, boundary=None, offset=None):
        """Breaks the string containing a mixture of text and embedded object
        characters into a list of (obj, startOffset, endOffset, string) tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - boundary: the pyatspi text boundary type. If None, get all text.
        - offset: the character offset. If None, use the current offset.

        Returns a list of (obj, startOffset, endOffset, string) tuples.
        """

        # For now, each script should implement this functionality itself.

        return []

    @staticmethod
    def getHyperlinkRange(obj):
        """Returns the start and end indices associated with the embedded
        object, obj."""

        try:
            hyperlink = obj.queryHyperlink()
        except NotImplementedError:
            return 0, 0

        return hyperlink.startIndex, hyperlink.endIndex
