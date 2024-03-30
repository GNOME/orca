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

from orca import focus_manager
from orca import input_event_manager
from orca import script_utilities

from orca.ax_component import AXComponent
from orca.ax_hypertext import AXHypertext
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities


class Utilities(script_utilities.Utilities):

    def isWebKitGtk(self, obj):
        """Returns True if this object is a WebKitGtk object."""

        if not obj:
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get('toolkit', '') in ['WebKitGtk', 'WebKitGTK']

    def getCaretContext(self):
        # TODO - JD: This is private, but it's only here temporarily until we
        # have the shared web content support.
        obj, offset = self._script._lastCaretContext
        if not obj and self.isWebKitGtk(focus_manager.getManager().get_locus_of_focus()):
            obj, offset = super().getCaretContext()

        return obj, offset

    def setCaretContext(self, obj, offset):
        # TODO - JD: This is private, but it's only here temporarily until we
        # have the shared web content support.
        self._script._lastCaretContext = obj, offset
        focus_manager.getManager().set_locus_of_focus(None, obj, notify_script=False)

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
                text = AXHypertext.get_link_basename(obj, remove_extension=True)

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

        if not (AXObject.supports_text(obj) and AXObject.supports_hypertext(obj)):
            return [(obj, 0, 1, '')]

        string = AXText.get_all_text(obj)
        if not string:
            return [(obj, 0, 1, '')]

        if offset is None:
            offset = AXText.get_caret_offset(obj)
        if boundary == Atspi.TextBoundaryType.CHAR:
            if input_event_manager.getManager().last_event_was_forward_caret_selection():
                offset -= 1
            start, end = AXText.get_character_at_offset(obj, offset)[1:]
        elif boundary in (None, Atspi.TextBoundaryType.LINE_START):
            start, end = AXText.get_line_at_offset(obj, offset)[1:]
        elif boundary == Atspi.TextBoundaryType.SENTENCE_START:
            start, end = AXText.get_sentence_at_offset(obj, offset)[1:]
        elif boundary == Atspi.TextBoundaryType.WORD_START:
            start, end = AXText.get_word_at_offset(obj, offset)[1:]
        else:
            start, end = 0, AXText.get_character_count(obj)

        pattern = re.compile(self.EMBEDDED_OBJECT_CHARACTER)
        offsets = [m.start(0) for m in re.finditer(pattern, string)]
        offsets = [x for x in offsets if start <= x < end]

        objects = []
        objs = []
        for offset in offsets:
            child = AXHypertext.get_child_at_offset(obj, offset)
            if child:
                objs.append(child)

        def _get_range(obj):
            return AXHypertext.get_link_start_offset(obj), AXHypertext.get_link_end_offset(obj)

        ranges = [_get_range(x) for x in objs]
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
                return AXComponent.on_same_line(
                    AXObject.get_child(obj, 0), AXObject.get_child(obj, 1))
            return False

        if AXUtilities.is_list(obj):
            if AXUtilities.is_focusable(obj):
                return False
            childCount = AXObject.get_child_count(obj)
            if not childCount:
                return AXObject.supports_text(obj)
            if childCount == 1:
                return False
            return AXComponent.on_same_line(AXObject.get_child(obj, 0), AXObject.get_child(obj, 1))

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
        child, index = self.getFirstCaretPosition(obj)
        if child is not None:
            AXText.set_caret_offset(child, index)
        return child, index

    def treatAsBrowser(self, obj):
        return self.isEmbeddedDocument(obj)

    def inDocumentContent(self, obj=None):
        obj = obj or focus_manager.getManager().get_locus_of_focus()
        return self.isWebKitGtk(obj)
