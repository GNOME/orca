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

import pyatspi

import orca.debug as debug
import orca.orca_state as orca_state
import orca.script_utilities as script_utilities

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def cellIndex(self, obj):
        """Returns the index of the cell which should be used with the
        table interface.  This is necessary because we cannot count on
        the index we need being the same as the index in the parent.
        See, for example, tables with captions and tables with rows
        that have attributes."""

        index = -1
        parent = self.ancestorWithRole(obj,
                                       [pyatspi.ROLE_TABLE, 
                                        pyatspi.ROLE_TREE_TABLE,
                                        pyatspi.ROLE_TREE],
                                       [pyatspi.ROLE_DOCUMENT_FRAME])
        try:
            table = parent.queryTable()
        except:
            pass
        else:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
            index = attrs.get('table-cell-index')
            if index:
                index = int(index)
            else:
                index = obj.getIndexInParent()

        return index

    def displayedText(self, obj):
        """Returns the text being displayed for an object.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.  Overridden in this script because we have lots
        of whitespace we need to remove.
        """

        displayedText = script_utilities.Utilities.displayedText(self, obj)
        if displayedText \
           and not (obj.getState().contains(pyatspi.STATE_EDITABLE) \
                    or obj.getRole() in [pyatspi.ROLE_ENTRY,
                                         pyatspi.ROLE_PASSWORD_TEXT]):
            displayedText = displayedText.strip()
            # Some ARIA widgets (e.g. the list items in the chat box
            # in gmail) implement the accessible text interface but
            # only contain whitespace.
            #
            if not displayedText \
               and obj.getState().contains(pyatspi.STATE_FOCUSED):
                label = self.displayedLabel(obj)
                if not label:
                    displayedText = obj.name

        return displayedText

    def displayedLabel(self, obj):
        """If there is an object labelling the given object, return the
        text being displayed for the object labelling this object.
        Otherwise, return None.  Overridden here to handle instances
        of bogus labels and form fields where a lack of labels necessitates
        our attempt to guess the text that is functioning as a label.

        Argument:
        - obj: the object in question

        Returns the string of the object labelling this object, or None
        if there is nothing of interest here.
        """

        string = None
        labels = self.labelsForObject(obj)
        for label in labels:
            # Check to see if the official labels are valid.
            #
            bogus = False
            if self._script.inDocumentContent() \
               and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                     pyatspi.ROLE_LIST]:
                # Bogus case #1:
                # <label></label> surrounding the entire combo box/list which
                # makes the entire combo box's/list's contents serve as the
                # label. We can identify this case because the child of the
                # label is the combo box/list. See bug #428114, #441476.
                #
                if label.childCount:
                    bogus = (label[0].getRole() == obj.getRole())

            if not bogus:
                # Bogus case #2:
                # <label></label> surrounds not just the text serving as the
                # label, but whitespace characters as well (e.g. the text
                # serving as the label is on its own line within the HTML).
                # Because of the Mozilla whitespace bug, these characters
                # will become part of the label which will cause the label
                # and name to no longer match and Orca to seemingly repeat
                # the label.  Therefore, strip out surrounding whitespace.
                # See bug #441610 and
                # https://bugzilla.mozilla.org/show_bug.cgi?id=348901
                #
                expandedLabel = self.expandEOCs(label)
                if expandedLabel:
                    string = self.appendString(string, expandedLabel.strip())

        return string

    def documentFrame(self):
        """Returns the document frame that holds the content being shown."""

        # [[[TODO: WDW - this is based upon the 12-Oct-2006 implementation
        # that uses the EMBEDS relation on the top level frame as a means
        # to find the document frame.  Future implementations will break
        # this.]]]
        #
        documentFrame = None
        for child in self._script.app:
            if child.getRole() == pyatspi.ROLE_FRAME:
                relationSet = child.getRelationSet()
                for relation in relationSet:
                    if relation.getRelationType()  \
                        == pyatspi.RELATION_EMBEDS:
                        documentFrame = relation.getTarget(0)
                        if documentFrame.getState().contains(
                            pyatspi.STATE_SHOWING):
                            break
                        else:
                            documentFrame = None

        # Certain add-ons can interfere with the above approach. But we
        # should have a locusOfFocus. If so look up and try to find the
        # document frame. See bug 537303.
        #
        if not documentFrame:
            documentFrame = self.ancestorWithRole(
                orca_state.locusOfFocus,
                [pyatspi.ROLE_DOCUMENT_FRAME],
                [pyatspi.ROLE_FRAME])

        return documentFrame

    def documentFrameURI(self):
        """Returns the URI of the document frame that is active."""

        documentFrame = self.documentFrame()
        if documentFrame:
            # If the document frame belongs to a Thunderbird message which
            # has just been deleted, getAttributes() will crash Thunderbird.
            #
            if not documentFrame.getState().contains(pyatspi.STATE_DEFUNCT):
                attrs = documentFrame.queryDocument().getAttributes()
                for attr in attrs:
                    if attr.startswith('DocURL'):
                        return attr[7:]

        return None

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

    def isEntry(self, obj):
        """Returns True if we should treat this object as an entry."""

        if not obj:
            return False

        if obj.getRole() == pyatspi.ROLE_ENTRY:
            return True

        if obj.getState().contains(pyatspi.STATE_EDITABLE) \
           and obj.getRole() in [pyatspi.ROLE_DOCUMENT_FRAME,
                                 pyatspi.ROLE_PARAGRAPH,
                                 pyatspi.ROLE_TEXT]:
            return True

        return False

    def isLayoutOnly(self, obj):
        """Returns True if the given object is for layout purposes only."""

        if self._script.isUselessObject(obj):
            debug.println(debug.LEVEL_FINEST,
                          "Object deemed to be useless: %s" % obj)
            return True

        else:
            return script_utilities.Utilities.isLayoutOnly(self, obj)

    def isPasswordText(self, obj):
        """Returns True if we should treat this object as password text."""

        return obj and obj.getRole() == pyatspi.ROLE_PASSWORD_TEXT

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""

        if not obj.getRole() == pyatspi.ROLE_ENTRY:
            return False

        state = obj.getState()
        readOnly = state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        details = debug.getAccessibleDetails(debug.LEVEL_ALL, obj)
        debug.println(debug.LEVEL_ALL,
                      "Gecko - isReadOnlyTextArea=%s for %s" \
                      % (readOnly, details))

        return readOnly

    def nodeLevel(self, obj):
        """ Determines the level of at which this object is at by using
        the object attribute 'level'.  To be consistent with the default
        nodeLevel() this value is 0-based (Gecko return is 1-based) """

        if obj is None or obj.getRole() == pyatspi.ROLE_HEADING \
           or (obj.parent and obj.parent.getRole() == pyatspi.ROLE_MENU):
            return -1

        try:
            state = obj.getState()
        except:
            return -1
        else:
            if state.contains(pyatspi.STATE_DEFUNCT):
                # Yelp (or perhaps the work-in-progress a11y patch)
                # seems to be guilty of this.
                #
                #print "nodeLevel - obj is defunct", obj
                debug.println(debug.LEVEL_WARNING,
                              "nodeLevel - obj is defunct")
                debug.printStack(debug.LEVEL_WARNING)
                return -1

        attrs = obj.getAttributes()
        if attrs is None:
            return -1
        for attr in attrs:
            if attr.startswith("level:"):
                return int(attr[6:]) - 1
        return -1

    def showingDescendants(self, parent):
        """Given an accessible object, returns a list of accessible children
        that are actually showing/visible/pursable for flat review. We're
        overriding the default method here primarily to handle enormous
        tree tables (such as the Thunderbird message list) which do not
        manage their descendants.

        Arguments:
        - parent: The accessible which manages its descendants

        Returns a list of Accessible descendants which are showing.
        """

        if not parent:
            return []

        # If this object is not a tree table, if it manages its descendants,
        # or if it doesn't have very many children, let the default script
        # handle it.
        #
        if parent.getRole() != pyatspi.ROLE_TREE_TABLE \
           or parent.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or parent.childCount <= 50:
            return script_utilities.Utilities.showingDescendants(self, parent)

        try:
            table = parent.queryTable()
        except NotImplementedError:
            return []

        descendants = []

        # First figure out what columns are visible as there's no point
        # in examining cells which we know won't be visible.
        # 
        visibleColumns = []
        for i in range(table.nColumns):
            header = table.getColumnHeader(i)
            if self.pursueForFlatReview(header):
                visibleColumns.append(i)
                descendants.append(header)

        if not len(visibleColumns):
            return []

        # Now that we know in which columns we can expect to find visible
        # cells, try to quickly locate a visible row.
        #
        startingRow = 0

        # If we have one or more selected items, odds are fairly good
        # (although not guaranteed) that one of those items happens to
        # be showing. Failing that, calculate how many rows can fit in
        # the exposed portion of the tree table and scroll down.
        #
        selectedRows = table.getSelectedRows()
        for row in selectedRows:
            acc = table.getAccessibleAt(row, visibleColumns[0])
            if self.pursueForFlatReview(acc):
                startingRow = row
                break
        else:
            try:
                tableExtents = parent.queryComponent().getExtents(0)
                acc = table.getAccessibleAt(0, visibleColumns[0])
                cellExtents = acc.queryComponent().getExtents(0)
            except:
                pass
            else:
                rowIncrement = max(1, tableExtents.height / cellExtents.height)
                for row in range(0, table.nRows, rowIncrement):
                    acc = table.getAccessibleAt(row, visibleColumns[0])
                    if acc and self.pursueForFlatReview(acc):
                        startingRow = row
                        break

        # Get everything after this point which is visible.
        #
        for row in range(startingRow, table.nRows):
            acc = table.getAccessibleAt(row, visibleColumns[0])
            if self.pursueForFlatReview(acc):
                descendants.append(acc)
                for col in visibleColumns[1:len(visibleColumns)]:
                    descendants.append(table.getAccessibleAt(row, col))
            else:
                break

        # Get everything before this point which is visible.
        #
        for row in range(startingRow - 1, -1, -1):
            acc = table.getAccessibleAt(row, visibleColumns[0])
            if self.pursueForFlatReview(acc):
                thisRow = [acc]
                for col in visibleColumns[1:len(visibleColumns)]:
                    thisRow.append(table.getAccessibleAt(row, col))
                descendants[0:0] = thisRow
            else:
                break

        return descendants

    def uri(self, obj):
        """Return the URI for a given link object.

        Arguments:
        - obj: the Accessible object.
        """

        # Getting a link's URI requires a little workaround due to
        # https://bugzilla.mozilla.org/show_bug.cgi?id=379747.  You
        # should be able to use getURI() directly on the link but
        # instead must use ihypertext.getLink(0) on parent then use
        # getURI on returned ihyperlink.
        try:
            ihyperlink = obj.parent.queryHypertext().getLink(0)
        except:
            return None
        else:
            try:
                return ihyperlink.getURI(0)
            except:
                return None

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################

    def isWordMisspelled(self, obj, offset):
        """Identifies if the current word is flagged as misspelled by the
        application.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.

        Returns True if the word is flagged as misspelled.
        """

        attributes, start, end  = self.textAttributes(obj, offset, True)
        error = attributes.get("invalid")

        return error == "spelling"

    def setCaretOffset(self, obj, characterOffset):
        self._script.setCaretPosition(obj, characterOffset)
        self._script.updateBraille(obj)

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

        # For really large objects, a call to getAttributes can take up to
        # two seconds! This is a Gecko bug. We'll try to improve things
        # by storing attributes.
        #
        attrsForObj = self._script.currentAttrs.get(hash(acc)) or {}
        if offset in attrsForObj:
            return attrsForObj.get(offset)

        attrs = script_utilities.Utilities.textAttributes(
            self, acc, offset, get_defaults)
        self._script.currentAttrs[hash(acc)] = {offset:attrs}

        return attrs

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################
