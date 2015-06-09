# Orca
#
# Copyright 2014 Igalia, S.L.
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

"""Custom script for epiphany."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import orca.orca as orca
import orca.scripts.toolkits.gtk as gtk
import orca.scripts.toolkits.WebKitGtk as WebKitGtk

class Script(WebKitGtk.Script):

    def __init__(self, app):
        WebKitGtk.Script.__init__(self, app)

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        gtk.Script.onWindowActivated(self, event)

        obj, offset = self.utilities.getCaretContext()
        if obj:
            orca.setLocusOfFocus(None, obj)

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        gtk.Script.onWindowDeactivated(self, event)

