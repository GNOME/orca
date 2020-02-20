# Orca
#
# Copyright 2018-2019 Igalia, S.L.
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

"""Custom braille generator for Chromium."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import debug
from orca import orca_state
from orca.scripts import web


class BrailleGenerator(web.BrailleGenerator):

    def __init__(self, script):
        super().__init__(script)

    def _generateLabelOrName(self, obj, **args):
        if obj.getRole() == pyatspi.ROLE_FRAME:
            document = self._script.utilities.activeDocument(obj)
            if document and not self._script.utilities.documentFrameURI(document):
                # Eliminates including "untitled" in the frame name.
                return super()._generateLabelOrName(obj.parent)

        return super()._generateLabelOrName(obj)

    def generateBraille(self, obj, **args):
        if self._script.utilities.inDocumentContent(obj):
            return super().generateBraille(obj, **args)

        oldRole = None
        if self._script.utilities.treatAsMenu(obj):
            msg = "CHROMIUM: HACK? Displaying menu item as menu %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            oldRole = self._overrideRole(pyatspi.ROLE_MENU, args)

        result = super().generateBraille(obj, **args)
        if oldRole is not None:
            self._restoreRole(oldRole, args)

        return result
