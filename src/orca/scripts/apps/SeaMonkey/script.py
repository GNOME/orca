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

        try:
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            if focusRole == pyatspi.ROLE_TABLE_ROW :
                msg = "SEAMONKEY: Ignoring, locusOfFocus is %s" % orca_state.locusOfFocus
                debug.println(debug.LEVEL_INFO, msg, True)
                return

        super().onBusyChanged(event)

