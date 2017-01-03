# Orca
#
# Copyright 2016 Igalia, S.L.
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

"""Custom script for SeaMonkey."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import debug
from orca import orca_state
from orca.scripts.toolkits import Gecko


class Script(Gecko.Script):

    def __init__(self, app):
        super().__init__(app)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            msg = "SEAMONKEY: Ignoring, event source is content editable"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        table = self.utilities.getTable(orca_state.locusOfFocus)
        if table and not self.utilities.isTextDocumentTable(table):
            msg = "SEAMONKEY: Ignoring, locusOfFocus is %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().onBusyChanged(event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
            return

        try:
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            focusRole = None

        if focusRole != pyatspi.ROLE_ENTRY or not self.utilities.inDocumentContent():
            super().onFocus(event)
            return

        if event.source.getRole() == pyatspi.ROLE_MENU:
            msg = "SEAMONKEY: Non-document menu claimed focus from document entry"
            debug.println(debug.LEVEL_INFO, msg, True)

            if self.utilities.lastInputEventWasPrintableKey():
                msg = "SEAMONKEY: Ignoring, believed to be result of printable input"
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        super().onFocus(event)
