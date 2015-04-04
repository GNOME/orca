# Orca
#
# Copyright 2010 Joanmarie Diggs.
# Copyright 2014 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import re

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

    def documentFrame(self):
        """Returns the document frame that holds the content being shown."""

        # [[[TODO: WDW - this is based upon the 12-Oct-2006 implementation
        # that uses the EMBEDS relation on the top level frame as a means
        # to find the document frame.  Future implementations will break
        # this.]]]
        #
        documentFrame = None
        for child in self._script.app:
            if child.getRole() == pyatspi.ROLE_FRAME \
               and child.getState().contains(pyatspi.STATE_ACTIVE):
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

        if not documentFrame and orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            documentFrame = orca_state.locusOfFocus

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

    def inFindToolbar(self, obj=None):
        if not obj:
            obj = orca_state.locusOfFocus

        if obj and obj.parent \
           and obj.parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            return False

        return script_utilities.Utilities.inFindToolbar(obj)

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

    def isLink(self, obj):
        """Returns True if we should treat this object as a link."""

        if not obj:
            return False

        role = obj.getRole()
        if role == pyatspi.ROLE_LINK:
            return True

        if role == pyatspi.ROLE_TEXT \
           and obj.parent.getRole() == pyatspi.ROLE_LINK \
           and obj.name and obj.name == obj.parent.name:
            return True

        return False

    def isPasswordText(self, obj):
        """Returns True if we should treat this object as password text."""

        return obj and obj.getRole() == pyatspi.ROLE_PASSWORD_TEXT

    def isHidden(self, obj):
        attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        isHidden = attrs.get('hidden', False)

        return isHidden

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

        try:
            attrs = obj.getAttributes()
        except:
            attrs = None
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

    # TODO - JD: Ultimately "utilities" need to be properly organized into
    # functionality-based modules. But they belong even less in the script.

    def extentsAreOnSameLine(self, a, b, pixelDelta=5):
        """Determine if extents a and b are on the same line.

        Arguments:
        -a: [x, y, width, height]
        -b: [x, y, width, height]

        Returns True if a and b are on the same line.
        """

        if a == b:
            return True

        aX, aY, aWidth, aHeight = a
        bX, bY, bWidth, bHeight = b

        if aWidth == 0 and aHeight == 0:
            return bY <= aY <= bY + bHeight
        if bWidth == 0 and bHeight == 0:
            return aY <= bY <= aY + aHeight

        highestBottom = min(aY + aHeight, bY + bHeight)
        lowestTop = max(aY, bY)
        if lowestTop >= highestBottom:
            return False

        aMiddle = aY + aHeight / 2
        bMiddle = bY + bHeight / 2
        if abs(aMiddle - bMiddle) > pixelDelta:
            return False

        return True

    def getExtents(self, obj, startOffset, endOffset):
        """Returns [x, y, width, height] of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text.
        """
        if not obj:
            return [0, 0, 0, 0]

        role = obj.getRole()
        text = self.queryNonEmptyText(obj)
        if text and not self._treatTextObjectAsWhole(obj):
            return list(text.getRangeExtents(startOffset, endOffset, 0))

        parentRole = obj.parent.getRole()
        if role in [pyatspi.ROLE_MENU, pyatspi.ROLE_LIST_ITEM] \
           and parentRole in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_LIST_BOX]:
            ext = obj.parent.queryComponent().getExtents(0)
        else:
            ext = obj.queryComponent().getExtents(0)

        return [ext.x, ext.y, ext.width, ext.height]

    def findObjectInContents(self, obj, offset, contents):
        if not obj or not contents:
            return -1

        offset = max(0, offset)
        matches = [x for x in contents if self.isSameObject(x[0], obj)]
        match = [x for x in matches if x[1] <= offset < x[2]]
        if match and match[0] and match[0] in contents:
            return contents.index(match[0])

        return -1

    def _treatTextObjectAsWhole(self, obj):
        roles = [pyatspi.ROLE_CHECK_BOX,
                 pyatspi.ROLE_CHECK_MENU_ITEM,
                 pyatspi.ROLE_MENU_ITEM,
                 pyatspi.ROLE_RADIO_MENU_ITEM,
                 pyatspi.ROLE_RADIO_BUTTON,
                 pyatspi.ROLE_PUSH_BUTTON,
                 pyatspi.ROLE_TOGGLE_BUTTON]

        role = obj.getRole()
        if role in roles:
            return True

        return False

    def __findRange(self, obj, offset, boundary):
        # We should not have to do any of this. Seriously. This is why
        # We can't have nice things.
        if not obj:
            return '', 0, 0

        text = self.queryNonEmptyText(obj)
        if not text:
            return '', 0, 1

        allText = text.getText(0, -1)
        extents = list(text.getRangeExtents(offset, offset + 1, 0))

        def _inThisSentence(span):
            return span[0] <= offset <= span[1]

        def _inThisWord(span):
            return span[0] <= offset <= span[1]

        def _onThisLine(span):
            rangeExtents = list(text.getRangeExtents(span[0], span[0] + 1, 0))
            return self.extentsAreOnSameLine(extents, rangeExtents)

        words = [m.span() for m in re.finditer("[^\s\ufffc]+", allText)]
        sentences = [m.span() for m in re.finditer("\S[^\.\?\!]+((?<!\w)[\.\?\!]+(?!\w)|\S*)", allText)]
        if boundary == pyatspi.TEXT_BOUNDARY_LINE_START:
            segments = list(filter(_onThisLine, words))
        elif boundary == pyatspi.TEXT_BOUNDARY_WORD_START:
            segments = list(filter(_inThisWord, words))
        elif boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START:
            sentences = sentences or [(0, text.characterCount)]
            segments = list(filter(_inThisSentence, sentences))
        else:
            return '', 0, 0

        if segments and segments[0]:
            start = segments[0][0]
            end = segments[-1][1] + 1
            if start <= offset < end:
                string = allText[start:end]
                return string, start, end

        return allText[offset:offset+1], offset, offset + 1

    def _getTextAtOffset(self, obj, offset, boundary):
        if not obj:
            return '', 0, 0

        text = self.queryNonEmptyText(obj)
        if not text:
            return '', 0, 1

        treatAsWhole = self._treatTextObjectAsWhole(obj)
        if not treatAsWhole and boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START:
            state = obj.getState()
            if state.contains(pyatspi.STATE_EDITABLE) \
               and state.contains(pyatspi.STATE_FOCUSED):
                treatAsWhole = False
            elif obj.getRole() in [pyatspi.ROLE_LIST_ITEM, pyatspi.ROLE_HEADING] \
               or not self.isTextBlockElement(obj):
                treatAsWhole = True

        if treatAsWhole:
            return text.getText(0, -1), 0, text.characterCount

        offset = max(0, offset)
        string, start, end = text.getTextAtOffset(offset, boundary)

        # The above should be all that we need to do, but....
        needSadHack = False
        testString, testStart, testEnd = text.getTextAtOffset(start, boundary)
        if (string, start, end) != (testString, testStart, testEnd):
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]")
            s2 = testString.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]")
            msg = "FAIL: Bad results for text at offset for %s using %s.\n" \
                  "      For offset %i - String: '%s', Start: %i, End: %i.\n" \
                  "      For offset %i - String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is the above results should be the same.\n" \
                  "      This very likely needs to be fixed by Mozilla." \
                  % (obj, boundary, offset, s1.replace("\n", "\\n"), start, end,
                     start, s2.replace("\n", "\\n"), testStart, testEnd)
            debug.println(debug.LEVEL_INFO, msg)
            needSadHack = True
        elif not string and 0 <= offset < text.characterCount:
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]")
            s2 = text.getText(0, -1).replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]")
            msg = "FAIL: Bad results for text at offset %i for %s using %s:\n" \
                  "      String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is no text reported for a valid offset.\n" \
                  "      Character count: %i, Full text: '%s'.\n" \
                  "      This very likely needs to be fixed by Mozilla." \
                  % (offset, obj, boundary, s1.replace("\n", "\\n"), start, end,
                     text.characterCount, s2.replace("\n", "\\n"))
            debug.println(debug.LEVEL_INFO, msg)
            needSadHack = True
        elif not (start <= offset < end):
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]")
            msg = "FAIL: Bad results for text at offset %i for %s using %s:\n" \
                  "      String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is the range returned is outside of the offset.\n" \
                  "      This very likely needs to be fixed by Mozilla." \
                  % (offset, obj, boundary, s1.replace("\n", "\\n"), start, end)
            debug.println(debug.LEVEL_INFO, msg)
            needSadHack = True

        if needSadHack:
            sadString, sadStart, sadEnd = self.__findRange(obj, offset, boundary)
            s = sadString.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]")
            msg = "HACK: Attempting to recover from above failure.\n" \
                  "      Returning: '%s' (%i, %i) " % (s, sadStart, sadEnd)
            debug.println(debug.LEVEL_INFO, msg)
            return sadString, sadStart, sadEnd

        return text.getText(start, end), start, end

    def _getContentsForObj(self, obj, offset, boundary):
        if not obj:
            return []

        string, start, end = self._getTextAtOffset(obj, offset, boundary)
        if not string:
            return [[obj, start, end, string]]

        stringOffset = offset - start
        try:
            char = string[stringOffset]
        except:
            pass
        else:
            if char == self.EMBEDDED_OBJECT_CHARACTER:
                childIndex = self._script.getChildIndex(obj, offset)
                child = obj[childIndex]
                return [[child, 0, 1, ""]]

        ranges = [m.span() for m in re.finditer("[^\ufffc]+", string)]
        strings = list(filter(lambda x: x[0] <= stringOffset <= x[1], ranges))
        if len(strings) == 1:
            rangeStart, rangeEnd = strings[0]
            start += rangeStart
            string = string[rangeStart:rangeEnd]
            end = start + len(string)

        return [[obj, start, end, string]]

    def getSentenceContentsAtOffset(self, obj, offset):
        if not obj:
            return []

        boundary = pyatspi.TEXT_BOUNDARY_SENTENCE_START
        objects = self._getContentsForObj(obj, offset, boundary)
        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE) \
           and state.contains(pyatspi.STATE_FOCUSED):
            return objects

        def _treatAsSentenceEnd(x):
            xObj, xStart, xEnd, xString = x
            if not self.isTextBlockElement(xObj):
                return False

            text = self.queryNonEmptyText(xObj)
            if text and 0 < text.characterCount <= xEnd:
                return True

            if 0 <= xStart <= 5:
                xString = " ".join(xString.split()[1:])

            match = re.search("\S[\.\!\?]+(\s|\Z)", xString)
            return match != None

        # Check for things in the same sentence before this object.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        while firstObj and firstString:
            if firstStart == 0 and self.isTextBlockElement(firstObj):
                break

            prevObj, pOffset = self._script.findPreviousCaretInOrder(firstObj, firstStart)
            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
            onLeft = list(filter(lambda x: x not in objects, onLeft))
            endsOnLeft = list(filter(_treatAsSentenceEnd, onLeft))
            if endsOnLeft:
                i = onLeft.index(endsOnLeft[-1])
                onLeft = onLeft[i+1:]

            if not onLeft:
                break

            objects[0:0] = onLeft
            firstObj, firstStart, firstEnd, firstString = objects[0]

        # Check for things in the same sentence after this object.
        while not _treatAsSentenceEnd(objects[-1]):
            lastObj, lastStart, lastEnd, lastString = objects[-1]
            nextObj, nOffset = self._script.findNextCaretInOrder(lastObj, lastEnd - 1)
            onRight = self._getContentsForObj(nextObj, nOffset, boundary)
            onRight = list(filter(lambda x: x not in objects, onRight))
            if not onRight:
                break

            objects.extend(onRight)

        return objects

    def getWordContentsAtOffset(self, obj, offset):
        if not obj:
            return []

        boundary = pyatspi.TEXT_BOUNDARY_WORD_START
        objects = self._getContentsForObj(obj, offset, boundary)
        extents = self.getExtents(obj, offset, offset + 1)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd or not xString:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)
            return self.extentsAreOnSameLine(extents, xExtents)

        # Check for things in the same word to the left of this object.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        prevObj, pOffset = self._script.findPreviousCaretInOrder(firstObj, firstStart)
        while prevObj and firstString:
            text = self.queryNonEmptyText(prevObj)
            if not text or text.getText(pOffset, pOffset + 1).isspace():
                break

            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
            onLeft = list(filter(_include, onLeft))
            if not onLeft:
                break

            objects[0:0] = onLeft
            firstObj, firstStart, firstEnd, firstString = objects[0]
            prevObj, pOffset = self._script.findPreviousCaretInOrder(firstObj, firstStart)

        # Check for things in the same word to the right of this object.
        lastObj, lastStart, lastEnd, lastString = objects[-1]
        while lastObj and lastString and not lastString[-1].isspace():
            nextObj, nOffset = self._script.findNextCaretInOrder(lastObj, lastEnd - 1)
            onRight = self._getContentsForObj(nextObj, nOffset, boundary)
            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastStart, lastEnd, lastString = objects[-1]

        # We want to treat the list item marker as its own word.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        if firstStart == 0 and firstObj.getRole() == pyatspi.ROLE_LIST_ITEM:
            objects = [objects[0]]

        return objects

    def _contentIsSubsetOf(self, contentA, contentB):
        objA, startA, endA, stringA = contentA
        objB, startB, endB, stringB = contentB
        if objA == objB:
            setA = set(range(startA, endA))
            setB = set(range(startB, endB))
            return setA.issubset(setB)

        return False

    def getLineContentsAtOffset(self, obj, offset, layoutMode=True):
        if not obj:
            return []

        objects = []
        extents = self.getExtents(obj, offset, offset + 1)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)
            return self.extentsAreOnSameLine(extents, xExtents)

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START
        objects = self._getContentsForObj(obj, offset, boundary)

        firstObj, firstStart, firstEnd, firstString = objects[0]
        lastObj, lastStart, lastEnd, lastString = objects[-1]
        prevObj, pOffset = self._script.findPreviousCaretInOrder(firstObj, firstStart)
        nextObj, nOffset = self._script.findNextCaretInOrder(lastObj, lastEnd - 1)
        if not layoutMode:
            if firstString and not re.search("\w", firstString) \
               and (re.match("[^\w\s]", firstString[0]) or not firstString.strip()):
                onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
                onLeft = list(filter(_include, onLeft))
                objects[0:0] = onLeft

            char = self._script.getCharacterAtOffset(nextObj, nOffset)
            if re.match("[^\w\s]", char):
                objects.append([nextObj, nOffset, nOffset + 1, char])

            return objects

        # Check for things on the same line to the left of this object.
        while prevObj:
            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
            onLeft = list(filter(_include, onLeft))
            if not onLeft:
                break

            if self._contentIsSubsetOf(objects[0], onLeft[-1]):
                objects.pop(0)

            objects[0:0] = onLeft
            firstObj, firstStart = objects[0][0], objects[0][1]
            prevObj, pOffset = self._script.findPreviousCaretInOrder(firstObj, firstStart)
            if self._script.getCharacterAtOffset(prevObj, pOffset) in [" ", "\xa0"]:
                prevObj, pOffset = self._script.findPreviousCaretInOrder(prevObj, pOffset)

        # Check for things on the same line to the right of this object.
        while nextObj:
            onRight = self._getContentsForObj(nextObj, nOffset, boundary)
            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastEnd = objects[-1][0], objects[-1][2]
            nextObj, nOffset = self._script.findNextCaretInOrder(lastObj, lastEnd - 1)
            if self._script.getCharacterAtOffset(nextObj, nOffset) in [" ", "\xa0"]:
                nextObj, nOffset = self._script.findNextCaretInOrder(nextObj, nOffset)

        return objects

    def justEnteredObject(self, obj, startOffset, endOffset):
        lastKey, mods = self.lastKeyAndModifiers()
        if (lastKey == "Down" and not mods) or self._script.inSayAll():
            return startOffset == 0

        if lastKey == "Up" and not mods:
            text = self.queryNonEmptyText(obj)
            if not text:
                return True
            return endOffset == text.characterCount

        return True

    def isFocusModeWidget(self, obj):
        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            return False

        if state.contains(pyatspi.STATE_EDITABLE) \
           or state.contains(pyatspi.STATE_EXPANDABLE):
            return True

        focusModeRoles = [pyatspi.ROLE_COMBO_BOX,
                          pyatspi.ROLE_ENTRY,
                          pyatspi.ROLE_LIST_BOX,
                          pyatspi.ROLE_LIST_ITEM,
                          pyatspi.ROLE_MENU,
                          pyatspi.ROLE_MENU_ITEM,
                          pyatspi.ROLE_CHECK_MENU_ITEM,
                          pyatspi.ROLE_RADIO_MENU_ITEM,
                          pyatspi.ROLE_PAGE_TAB,
                          pyatspi.ROLE_PASSWORD_TEXT,
                          pyatspi.ROLE_PROGRESS_BAR,
                          pyatspi.ROLE_SLIDER,
                          pyatspi.ROLE_SPIN_BUTTON,
                          pyatspi.ROLE_TOOL_BAR,
                          pyatspi.ROLE_TABLE_CELL,
                          pyatspi.ROLE_TABLE_ROW,
                          pyatspi.ROLE_TABLE,
                          pyatspi.ROLE_TREE_TABLE,
                          pyatspi.ROLE_TREE]

        if role in focusModeRoles \
           and not self.isTextBlockElement(obj):
            return True

        return False

    def isTextBlockElement(self, obj):
        if not (obj and self._script.inDocumentContent(obj)):
            return False

        textBlockElements = [pyatspi.ROLE_COLUMN_HEADER,
                             pyatspi.ROLE_DOCUMENT_FRAME,
                             pyatspi.ROLE_FORM,
                             pyatspi.ROLE_HEADING,
                             pyatspi.ROLE_LIST,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_PANEL,
                             pyatspi.ROLE_PARAGRAPH,
                             pyatspi.ROLE_ROW_HEADER,
                             pyatspi.ROLE_SECTION,
                             pyatspi.ROLE_TEXT,
                             pyatspi.ROLE_TABLE_CELL]

        role = obj.getRole()
        if not role in textBlockElements:
            return False

        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            return False

        if role == pyatspi.ROLE_DOCUMENT_FRAME:
            return True

        if not state.contains(pyatspi.STATE_FOCUSABLE) \
           and not state.contains(pyatspi.STATE_FOCUSED):
            return True

        return False

    def filterContentsForPresentation(self, contents, inferLabels=False):
        def _include(x):
            obj, start, end, string = x
            if not obj:
                return False

            if (self.isTextBlockElement(obj) and not string.strip()) \
               or self.isLabellingContents(x, contents) \
               or self.isOffScreenLabel(obj, start):
                return False

            if inferLabels and self.isInferredLabelForContents(x, contents):
                return False

            return True

        return list(filter(_include, contents))

    def needsSeparator(self, lastChar, nextChar):
        if lastChar.isspace() or nextChar.isspace():
            return False

        openingPunctuation = ["(", "[", "{", "<"]
        closingPunctuation = [".", "?", "!", ":", ",", ";", ")", "]", "}", ">"]
        if lastChar in closingPunctuation or nextChar in openingPunctuation:
            return True
        if lastChar in openingPunctuation or nextChar in closingPunctuation:
            return False

        return lastChar.isalnum()

    def getObjectsFromEOCs(self, obj, offset=None, boundary=None):
        """Expands the current object replacing EMBEDDED_OBJECT_CHARACTERS
        with [obj, startOffset, endOffset, string] tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - offset: the character offset after which
        - boundary: the pyatspi text boundary type

        Returns a list of object tuples.
        """

        if not obj:
            return []

        elif boundary and obj.getRole() == pyatspi.ROLE_TABLE:
            if obj[0] and obj[0].getRole() in [pyatspi.ROLE_CAPTION,
                                               pyatspi.ROLE_LIST]:
                obj = obj[0]
            else:
                obj = obj.queryTable().getAccessibleAt(0, 0)

            if not obj:
                debug.printStack(debug.LEVEL_WARNING)
                return []

        objects = []
        text = self.queryNonEmptyText(obj)
        if text:
            if offset == None:
                offset = max(0, text.caretOffset)

            if boundary:
                [string, start, end] = self._getTextAtOffset(obj, offset, boundary)
                if end == -1:
                    end = text.characterCount
            else:
                start = offset
                end = text.characterCount
                string = text.getText(start, end)
        else:
            string = ""
            start = 0
            end = 1

        unicodeText = string
        objects.append([obj, start, end, unicodeText])

        pattern = re.compile(self._script.EMBEDDED_OBJECT_CHARACTER)
        matches = re.finditer(pattern, unicodeText)

        offset = 0
        for m in matches:
            # Adjust the last object's endOffset to the last character
            # before the EOC.
            #
            childOffset = m.start(0) + start
            lastObj = objects[-1]
            lastObj[2] = childOffset
            if lastObj[1] == lastObj[2]:
                # A zero-length object is an indication of something
                # whose sole contents was an EOC.  Delete it from the
                # list.
                #
                objects.pop()
            else:
                # Adjust the string to reflect just this segment.
                #
                lastObj[3] = unicodeText[offset:m.start(0)]

            offset = m.start(0) + 1
 
            # Recursively tack on the child's objects.
            #
            childIndex = self._script.getChildIndex(obj, childOffset)
            child = obj[childIndex]
            objects.extend(self.getObjectsFromEOCs(child, 0, boundary))

            # Tack on the remainder of the original object, if any.
            #
            if end > childOffset + 1:
                restOfText = unicodeText[offset:len(unicodeText)]
                objects.append([obj, childOffset + 1, end, restOfText])
 
        if obj.getRole() in [pyatspi.ROLE_IMAGE, pyatspi.ROLE_TABLE, pyatspi.ROLE_TABLE_ROW]:
            # Imagemaps that don't have alternative text won't implement
            # the text interface, but they will have children (essentially
            # EOCs) that we need to get. The same is true for tables.
            #
            toAdd = []
            for child in obj:
                toAdd.extend(self.getObjectsFromEOCs(child, 0, boundary))
            if len(toAdd):
                if self.isSameObject(objects[-1][0], obj):
                    objects.pop()
                objects.extend(toAdd)

        return objects

    def isOffScreenLabel(self, obj, offset=0):
        if not obj:
            return False

        isLabelFor = lambda x: x.getRelationType() == pyatspi.RELATION_LABEL_FOR
        relations = list(filter(isLabelFor, obj.getRelationSet()))
        if relations:
            offset = max(offset, 0)
            x, y, width, height = self.getExtents(obj, offset, offset + 1)
            if x < 0 or y < 0:
                return True

        return False

    def shouldInferLabelFor(self, obj):
        if self.displayedLabel(obj) or obj.name:
            return False

        roles =  [pyatspi.ROLE_CHECK_BOX,
                  pyatspi.ROLE_COMBO_BOX,
                  pyatspi.ROLE_ENTRY,
                  pyatspi.ROLE_LIST_BOX,
                  pyatspi.ROLE_PASSWORD_TEXT,
                  pyatspi.ROLE_RADIO_BUTTON]
        if not obj.getRole() in roles:
            return False

        if not self._script.inDocumentContent():
            return False

        return True

    def isInferredLabelForContents(self, content, contents):
        obj, start, end, string = content
        objs = list(filter(self.shouldInferLabelFor, [x[0] for x in contents]))
        if not objs:
            return None

        for o in objs:
            label, sources = self._script.labelInference.infer(o, False)
            if obj in sources and label.strip() == string.strip():
                return o

        return None

    def isLabellingContents(self, content, contents):
        obj, start, end, string = content
        if obj.getRole() != pyatspi.ROLE_LABEL:
            return None

        relationSet = obj.getRelationSet()
        if not relationSet:
            return None

        for relation in relationSet:
            if relation.getRelationType() \
                == pyatspi.RELATION_LABEL_FOR:
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    for content in contents:
                        if content[0] == target:
                            return target

        return None

    def isClickableElement(self, obj):
        if not self._script.inDocumentContent(obj):
            return False

        # For Gecko, we want to identify things which are ONLY clickable.
        # Things which are focusable, while technically "clickable", are
        # easily discoverable (e.g. via role) and activatable (e.g. via
        # pressing Space or Enter.
        state = obj.getState()
        if state.contains(pyatspi.STATE_FOCUSABLE):
            return False

        try:
            action = obj.queryAction()
        except NotImplementedError:
            return False

        for i in range(action.nActions):
            if action.getName(i) in ["click"]:
                return True

        return False

    def hasLongDesc(self, obj):
        if not self._script.inDocumentContent(obj):
            return False

        try:
            action = obj.queryAction()
        except NotImplementedError:
            return False

        for i in range(action.nActions):
            if action.getName(i) in ["showlongdesc"]:
                return True

        return False
