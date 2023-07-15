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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
import re

import orca.script_utilities as script_utilities
import orca.keybindings as keybindings
import orca.orca as orca
import orca.orca_state as orca_state
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

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

        attrs = self.objectAttributes(obj)
        return attrs.get('toolkit', '') in ['WebKitGtk', 'WebKitGTK']

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

        if not AXUtilities.is_entry(obj):
            return False

        if AXUtilities.is_read_only(obj):
            return True

        return AXUtilities.is_focusable(obj) and not AXUtilities.is_editable(obj)

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

        if AXUtilities.is_link(obj) or AXUtilities.is_list_item(obj):
            children = [x for x in AXObject.iter_children(obj)]
            text = ' '.join(map(self.displayedText, children))
            if not text:
                text = self.linkBasename(obj)

        return text

    def getLineContentsAtOffset(self, obj, offset, layoutMode=True, useCache=True):
        return self.getObjectsFromEOCs(
            obj, offset, Atspi.TextBoundaryType.LINE_START)

    def getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        return self.getObjectsFromEOCs(obj, offset)

    def getObjectsFromEOCs(self, obj, offset=None, boundary=None):
        """Breaks the string containing a mixture of text and embedded object
        characters into a list of (obj, startOffset, endOffset, string) tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - offset: the character offset. If None, use the current offset.
        - boundary: the text boundary type. If None, get all text.

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

        if offset is None:
            offset = text.caretOffset
        if boundary is None:
            start = 0
            end = text.characterCount
        else:
            if boundary == Atspi.TextBoundaryType.CHAR:
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
        except Exception:
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

        if obj is None:
            return None

        if AXUtilities.is_link(obj):
            obj = AXObject.get_parent(obj)

        prevObj = AXObject.get_previous_object(obj)
        if AXUtilities.is_list(prevObj) and AXObject.get_child_count(prevObj):
            child = AXObject.get_child(prevObj, -1)
            if self.isTextListItem(child):
                prevObj = child

        return prevObj

    def findNextObject(self, obj):
        """Finds the object after this one."""

        if obj is None:
            return None

        if AXUtilities.is_link(obj):
            obj = AXObject.get_parent(obj)

        nextObj = AXObject.get_next_object(obj)
        if AXUtilities.is_list(nextObj) and AXObject.get_child_count(nextObj):
            child = AXObject.get_child(nextObj, 0)
            if self.isTextListItem(child):
                nextObj = child

        return nextObj

    def isTextListItem(self, obj):
        """Returns True if obj is an item in a non-selectable list."""

        if not AXUtilities.is_list_item(obj):
            return False

        parent = AXObject.get_parent(obj)
        if parent is None:
            return False

        return not AXUtilities.is_focusable(parent)

    def isInlineContainer(self, obj):
        """Returns True if obj is an inline/non-wrapped container."""

        if AXUtilities.is_section(obj):
            if AXObject.get_child_count(obj) > 1:
                return self.onSameLine(AXObject.get_child(obj, 0), AXObject.get_child(obj, 1))
            return False

        if AXUtilities.is_list(obj):
            if AXUtilities.is_focusable(obj):
                return False
            childCount = AXObject.get_child_count(obj)
            if not childCount:
                return AXObject.supports_text(obj)
            if childCount == 1:
                return False
            return self.onSameLine(AXObject.get_child(obj, 0), AXObject.get_child(obj, 1))

        return False

    def isEmbeddedDocument(self, obj):
        if not self.isWebKitGtk(obj):
            return False

        if not AXUtilities.is_document(obj):
            return False

        parent = AXObject.get_parent(obj)
        if not (parent and self.isWebKitGtk(parent)):
            return False

        parent = AXObject.get_parent(parent)
        if not (parent and not self.isWebKitGtk(parent)):
            return False

        return True

    def setCaretAtStart(self, obj):
        def implementsText(obj):
            return not AXUtilities.is_list(obj) and AXObject.supports_text(obj)

        child = obj
        if not implementsText(obj):
            child = AXObject.find_descendant(obj, implementsText)
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
