# Orca
#
# Copyright (C) 2013-2019 Igalia, S.L.
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013-2019 Igalia, S.L."
__license__   = "LGPL"

import orca.debug as debug
import orca.focus_manager as focus_manager
import orca.scripts.default as default
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .script_utilities import Utilities


class Script(default.Script):

    def __init__(self, app):
        super().__init__(app)

    def getUtilities(self):
        return Utilities(self)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if AXUtilities.is_accelerator_label(event.source):
            msg = "QT: Ignoring event due to role."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        super().onCaretMoved(event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        if AXUtilities.is_accelerator_label(event.source):
            msg = "QT: Ignoring event due to role."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        frame = self.utilities.topLevelObject(event.source)
        if not frame:
            msg = "QT: Ignoring event because we couldn't find an ancestor window."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        isActive = AXUtilities.is_active(frame)
        if not isActive:
            tokens = ["QT: Event came from inactive top-level object", frame]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

            AXObject.clear_cache(frame, False, "Ensuring we have correct active state.")
            isActive = AXUtilities.is_active(frame)
            tokens = ["QT: Cleared cache of", frame, ". Frame is now active:", isActive]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_focused(event.source):
            super().onFocusedChanged(event)
            return

        msg = "QT: WARNING - source lacks focused state. Setting focus anyway."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        focus_manager.getManager().set_locus_of_focus(event, event.source)
