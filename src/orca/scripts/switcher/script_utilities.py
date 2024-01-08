# Orca
#
# Copyright 2019 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2019 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca import script_utilities
from orca.ax_object import AXObject


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def isSwitcherContainer(self, obj):
        """Returns True if obj is the switcher container."""

        return obj and AXObject.get_role(obj) == Atspi.Role.STATUS_BAR

    def isSwitcherSelectionChangeEventType(self, event):
        """Returns True if this event is the one we use to present changes."""

        if event.type.startswith("object:text-changed:insert"):
            return True

        if event.type.startswith("object:state-changed:showing"):
            return event.detail1

        return False

    def getSelectionName(self, container):
        """Returns the name of the currently-selected item."""

        if self.isSwitcherContainer(container):
            return AXObject.get_name(container)

        return ""

    def isZombie(self, obj):
        if not super().isZombie(obj):
            return False

        if AXObject.get_index_in_parent(obj) >= 0:
            return True

        # TODO - JD: Is this still needed?
        AXObject.clear_cache(obj, False, "Ensuring we have correct state.")

        if self.isShowingAndVisible(obj):
            tokens = ["SWITCHER: Ignoring bad index of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["SWITCHER:", obj, "has bad index and isn't showing and visible"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return True
