# Orca
#
# Copyright (C) 2013 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.orca as orca
import orca.scripts.default as default

class Script(default.Script):

    def __init__(self, app):
        default.Script.__init__(self, app)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        # HACK: Although we get object:state-changed:focused events, the
        # object emitting them might not claim state focusable or state
        # focused. For now, assume that we won't get bogus focus claims.
        orca.setLocusOfFocus(event, event.source)
        return
