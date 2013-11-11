# Orca
#
# Copyright 2013 The Orca Team.
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
__copyright__ = "Copyright (c) 2013 The Orca Team"
__license__   = "LGPL"

import pyatspi

import orca.script_utilities as script_utilities
import orca.scripts.toolkits.gtk as gtk

class Utilities(gtk.Utilities):

    def __init__(self, script):
        gtk.Utilities.__init__(self, script)

    def offsetsForPhrase(self, obj):
        """Return the start and end offset for the given phrase. Overriden
        here because two functionally different objects (pages of a PDF)
        are currently contained in a single accessible object whose contents
        change. As a result, when a new text selection spans two pages, we
        have a stored offset for our previous location that makes no sense
        because that location no longer exists.

        Arguments:
        - obj: the Accessible object
        """

        try:
            text = obj.queryText()
        except:
            return [0, 0]

        if obj.getRole() != pyatspi.ROLE_DOCUMENT_FRAME:
            return gtk.Utilities.offsetsForPhrase(self, obj)

        lastPos = self._script.pointOfReference.get("lastCursorPosition")
        keyString, mods = self.lastKeyAndModifiers()
        if keyString in ["Up", "Page_Up", "Left", "Home"]:
            # The previous location should have a larger offset. If it does
            # not, we've crossed pages.
            if lastPos[1] <= text.caretOffset:
                return [text.caretOffset, text.characterCount]
            return [text.caretOffset, lastPos[1]]

        if keyString in ["Down", "Page_Down", "Right", "End"]:
            # The previous location should have a smaller offset. If it does
            # not, we've crossed pages.
            if lastPos[1] >= text.caretOffset:
                return [0, text.caretOffset]
            return [lastPos[1], text.caretOffset]

        return gtk.Utilities.offsetsForPhrase(self, obj)
