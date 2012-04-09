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
import orca.settings as settings

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

    def headingLevel(self, obj):
        """Determines the heading level of the given object.  A value
        of 0 means there is no heading level."""

        level = 0

        if obj is None:
            return level

        if obj.getRole() == pyatspi.ROLE_HEADING:
            attributes = obj.getAttributes()
            if attributes is None:
                return level
            for attribute in attributes:
                if attribute.startswith("level:"):
                    level = int(attribute.split(":")[1])
                    break

        return level

    def isWebKitGtk(self, obj):
        """Returns True if this object is a WebKitGtk object."""

        if not obj:
            return False

        attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        return attrs.get('toolkit', '') == 'WebKitGtk'

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

    def getObjectsFromEOCs(self, obj, boundary=None, offset=None):
        """Breaks the string containing a mixture of text and embedded object
        characters into a list of (obj, startOffset, endOffset, string) tuples.

        Arguments
        - obj: the object whose EOCs we need to expand into tuples
        - boundary: the pyatspi text boundary type. If None, get all text.
        - offset: the character offset. If None, use the current offset.

        Returns a list of (obj, startOffset, endOffset, string) tuples.
        """

        try:
            text = obj.queryText()
            htext = obj.queryHypertext()
        except (AttributeError, NotImplementedError):
            return [(obj, 0, 1, '')]

        string = text.getText(0, -1).decode('UTF-8')
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
                if (mods & settings.SHIFT_MODIFIER_MASK) and key == 'Right':
                    offset -= 1
            segment, start, end = text.getTextAtOffset(offset, boundary)

        pattern = re.compile(self.EMBEDDED_OBJECT_CHARACTER)
        offsets = [m.start(0) for m in re.finditer(pattern, string)]
        offsets = filter(lambda x: start <= x < end, offsets)

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
        objects = filter(lambda x: x[1] < x[2], objects)

        return objects
