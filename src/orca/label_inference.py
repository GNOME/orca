# Orca
#
# Copyright (C) 2011 Igalia, S.L.
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

"""Heuristic means to infer the functional/displayed label of a widget."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (C) 2011 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

class LabelInference:

    def __init__(self, script):
        """Creates an instance of the LabelInference class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        self._script = script

    def infer(self, obj, focusedOnly=True):
        """Attempt to infer the functional/displayed label of obj.

        Arguments
        - obj: the unlabeled widget
        - focusedOnly: If True, only infer if the widget has focus.

        Returns the text which we think is the label, or None.
        """

        isFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
        if focusedOnly and not isFocused:
            return None

        result = None
        if not result:
            result = self.inferFromLine(obj)
        if not result:
            result = self.inferFromTable(obj)
        if not result:
            result = self.inferFromOtherLines(obj)
        if not result:
            result = obj.name
        if not result:
            result = obj.description
        if result:
            result = result.strip()

        return result

    def _isWidget(self, obj):
        """Returns True if the given object is a widget."""

        widgetRoles = [pyatspi.ROLE_CHECK_BOX,
                       pyatspi.ROLE_RADIO_BUTTON,
                       pyatspi.ROLE_COMBO_BOX,
                       pyatspi.ROLE_DOCUMENT_FRAME,
                       pyatspi.ROLE_LIST,
                       pyatspi.ROLE_ENTRY,
                       pyatspi.ROLE_PASSWORD_TEXT,
                       pyatspi.ROLE_PUSH_BUTTON]

        return obj.getRole() in widgetRoles

    def _getExtents(self, obj, startOffset, endOffset):
        """Returns (x, y, width, height) of the text at the given offsets
        if the object implements accessible text, or just the extents of
        the object if it doesn't implement accessible text."""

        extents = 0, 0, 0, 0

        try:
            text = obj.queryText()
        except AttributeError:
            return extents
        except NotImplementedError:
            pass
        else:
            skipTextExtents = [pyatspi.ROLE_ENTRY, pyatspi.ROLE_PASSWORD_TEXT]
            if not obj.getRole() in skipTextExtents:
                extents = text.getRangeExtents(startOffset, endOffset, 0)

        if extents[2] and extents[3]:
            return extents

        ext = obj.queryComponent().getExtents(0)
        extents = ext.x, ext.y, ext.width, ext.height

        return extents

    def _getLineContents(self, obj):
        """Get the (obj, startOffset, endOffset, string) tuples for the line
        containing the object, obj."""

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START
        contents = self._script.utilities.getObjectsFromEOCs(obj, boundary)
        content = filter(lambda o: o[0] == obj, contents)
        if content == contents:
            start, end = self._script.utilities.getHyperlinkRange(obj)
            contents = self._script.utilities.getObjectsFromEOCs(
                obj.parent, boundary, start)

        return contents

    def inferFromLine(self, obj, proximity=75):
        """Attempt to infer the functional/displayed label of obj by
        looking at the contents of the current line.

        Arguments
        - obj: the unlabeled widget
        - proximity: pixels expected for a match

        Returns the text which we think is the label, or None.
        """

        contents = self._getLineContents(obj)
        content = filter(lambda o: o[0] == obj, contents)
        try:
            index = contents.index(content[0])
        except IndexError:
            index = len(contents)

        onLeft = contents[0:index]
        onLeft.reverse()
        try:
            onRight = contents[index+1:]
        except IndexError:
            onRight = [()]

        # Normally widgets do not label other widgets.
        onLeft = filter(lambda o: not self._isWidget(o[0]), onLeft)
        onRight = filter(lambda o: not self._isWidget(o[0]), onRight)

        # Proximity matters, both in terms of objects and of pixels.
        if onLeft:
            onLeft = onLeft[0]
        if onRight:
            onRight = onRight[0]
        extents = self._getExtents(obj, 0, 1)

        # Sometimes we should prefer what's to the right of the widget.
        onRightRoles = [pyatspi.ROLE_CHECK_BOX, pyatspi.ROLE_RADIO_BUTTON]
        preferRight = obj.getRole() in onRightRoles

        lObj = rObj = None
        lString = rString = ''
        lDistance = rDistance = -1

        if onLeft:
            lObj, lStart, lEnd, lString = onLeft
            lString = (lString or lObj.name).strip()
            if lString:
                lExtents = self._getExtents(lObj, lStart, lEnd)
                lDistance = extents[0] - (lExtents[0] + lExtents[2])
                if not preferRight and lDistance <= proximity:
                    return lString

        if onRight:
            rObj, rStart, rEnd, rString = onRight
            rString = (rString or rObj.name).strip()
            if rString:
                rExtents = self._getExtents(rObj, rStart, rEnd)
                rDistance = rExtents[0] - (extents[0] + extents[2])
                if preferRight and rDistance <= proximity:
                    return rString

        if rString and rDistance <= proximity:
            return rString

        return None

    def inferFromTable(self, obj):
        pass

    def inferFromOtherLines(self, obj):
        pass
