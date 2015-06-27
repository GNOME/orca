# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
# Copyright (C) 2011-2012 Igalia, S.L.
#
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

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2011-2012 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import re

import orca.script_utilities as script_utilities
import orca.keybindings as keybindings
import orca.orca as orca
import orca.orca_state as orca_state

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
        super().__init__(script)

    def isWebKitGtk(self, obj):
        """Returns True if this object is a WebKitGtk object."""

        if not obj:
            return False

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return False
        return attrs.get('toolkit', '') == 'WebKitGtk'

    def getCaretContext(self):
        # TODO - JD: This is private, but it's only here temporarily until we
        # have the shared web content support.
        obj, offset = self._script._lastCaretContext
        if not obj and self.isWebKitGtk(orca_state.locusOfFocus):
            obj, offset = super().getCaretContext()

        return obj, offset

    def setCaretContext(self, obj, offset):
        # TODO - JD: This is private, but it's only here temporarily until we
        # have the shared web content support.
        self._script._lastCaretContext = obj, offset
        orca.setLocusOfFocus(None, obj, notifyScript=False)

    def setCaretPosition(self, obj, offset):
        self.setCaretContext(obj, offset)
        self.setCaretOffset(obj, offset)

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""

        if not obj.getRole() == pyatspi.ROLE_ENTRY:
            return False

        state = obj.getState()
        readOnly = state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)

        return readOnly

    def displayedText(self, obj):
        """Returns the text being displayed for an object.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        text = script_utilities.Utilities.displayedText(self, obj)
        if text and text != self.EMBEDDED_OBJECT_CHARACTER:
            return text

        if obj.getRole() in [pyatspi.ROLE_LINK, pyatspi.ROLE_LIST_ITEM]:
            text = ' '.join(map(self.displayedText, (x for x in obj)))
            if not text:
                text = self.linkBasename(obj)

        return text

    def getLineContentsAtOffset(self, obj, offset, layoutMode=True, useCache=True):
        return self.getObjectsFromEOCs(
            obj, offset, pyatspi.TEXT_BOUNDARY_LINE_START)

    def getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        return self.getObjectsFromEOCs(obj, offset)

    def getObjectsFromEOCs(self, obj, offset=None, boundary=None):
        """Breaks the string containing a mixture of text and embedded object
        characters into a list of (obj, startOffset, endOffset, string) tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - offset: the character offset. If None, use the current offset.
        - boundary: the pyatspi text boundary type. If None, get all text.

        Returns a list of (obj, startOffset, endOffset, string) tuples.
        """

        try:
            text = obj.queryText()
            htext = obj.queryHypertext()
        except (AttributeError, NotImplementedError):
            return [(obj, 0, 1, '')]

        string = text.getText(0, -1)
        if not string:
            return [(obj, 0, 1, '')]

        if offset == None:
            offset = text.caretOffset
        if boundary == None:
            start = 0
            end = text.characterCount
        else:
            if boundary == pyatspi.TEXT_BOUNDARY_CHAR:
                key, mods = self.lastKeyAndModifiers()
                if (mods & keybindings.SHIFT_MODIFIER_MASK) and key == 'Right':
                    offset -= 1
            segment, start, end = text.getTextAtOffset(offset, boundary)

        pattern = re.compile(self.EMBEDDED_OBJECT_CHARACTER)
        offsets = [m.start(0) for m in re.finditer(pattern, string)]
        offsets = [x for x in offsets if start <= x < end]

        objects = []
        try:
            objs = [obj[htext.getLinkIndex(offset)] for offset in offsets]
        except:
            objs = []
        ranges = [self.getHyperlinkRange(x) for x in objs]
        for i, (first, last) in enumerate(ranges):
            objects.append((obj, start, first, string[start:first]))
            objects.append((objs[i], first, last, ''))
            start = last
        objects.append((obj, start, end, string[start:end]))
        objects = [x for x in objects if x[1] < x[2]]

        return objects

    def findPreviousObject(self, obj):
        """Finds the object before this one."""

        if not obj:
            return None

        if obj.getRole() == pyatspi.ROLE_LINK:
            obj = obj.parent

        index = obj.getIndexInParent() - 1
        if not (0 <= index < obj.parent.childCount - 1):
            obj = obj.parent
            index = obj.getIndexInParent() - 1

        try:
            prevObj = obj.parent[index]
        except:
            prevObj = obj
        else:
            if prevObj.getRole() == pyatspi.ROLE_LIST and prevObj.childCount:
                if self.isTextListItem(prevObj[0]):
                    prevObj = prevObj[-1]

        return prevObj

    def findNextObject(self, obj):
        """Finds the object after this one."""

        if not obj:
            return None

        if obj.getRole() == pyatspi.ROLE_LINK:
            obj = obj.parent

        index = obj.getIndexInParent() + 1
        if not (0 < index < obj.parent.childCount):
            obj = obj.parent
            index = obj.getIndexInParent() + 1

        try:
            nextObj = obj.parent[index]
        except:
            nextObj = None
        else:
            if nextObj.getRole() == pyatspi.ROLE_LIST and nextObj.childCount:
                if self.isTextListItem(nextObj[0]):
                    nextObj = nextObj[0]

        return nextObj

    def isTextListItem(self, obj):
        """Returns True if obj is an item in a non-selectable list."""

        if obj.getRole() != pyatspi.ROLE_LIST_ITEM:
            return False

        return not obj.parent.getState().contains(pyatspi.STATE_FOCUSABLE)

    def isInlineContainer(self, obj):
        """Returns True if obj is an inline/non-wrapped container."""

        if obj.getRole() == pyatspi.ROLE_SECTION:
            if obj.childCount > 1:
                return self.onSameLine(obj[1], obj[1])

            return False

        if obj.getRole() == pyatspi.ROLE_LIST:
            if obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                return False

            if not obj.childCount:
                return 'Text' in pyatspi.utils.listInterfaces(obj)

            if obj.childCount == 1:
                return False

            return self.onSameLine(obj[0], obj[1])

        return False

    def isEmbeddedDocument(self, obj):
        if not self.isWebKitGtk(obj):
            return False

        docRoles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]
        if not (obj and obj.getRole() in docRoles):
            return False

        parent = obj.parent
        if not (parent and self.isWebKitGtk(parent)):
            return False

        parent = parent.parent
        if not (parent and not self.isWebKitGtk(parent)):
            return False

        return True

    def setCaretAtStart(self, obj):
        def implementsText(obj):
            if obj.getRole() == pyatspi.ROLE_LIST:
                return False
            return 'Text' in pyatspi.utils.listInterfaces(obj)

        child = obj
        if not implementsText(obj):
            child = pyatspi.utils.findDescendant(obj, implementsText)
            if not child:
                return None, -1

        index = -1
        text = child.queryText()
        for i in range(text.characterCount):
            if text.setCaretOffset(i):
                index = i
                break

        return child, index

    def treatAsBrowser(self, obj):
        return self.isEmbeddedDocument(obj)

    def inDocumentContent(self, obj=None):
        obj = obj or orca_state.locusOfFocus
        return self.isWebKitGtk(obj)
