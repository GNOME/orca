# Orca
#
# Copyright (C) 2023 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.debug as debug
import orca.script_utilities as script_utilities

from orca.ax_object import AXObject

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def _isTopLevelObject(self, obj):
        # This is needed because Qt apps might insert some junk (e.g. a filler) in
        # between the window/frame/dialog and the application.
        return AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.APPLICATION

    def topLevelObject(self, obj, useFallbackSearch=False):
        # The fallback search is needed because sometimes we can ascend the accessibility
        # tree all the way to the top; other times, we cannot get the parent, but can still
        # get the children. The fallback search handles the latter scenario.
        result = super().topLevelObject(obj, useFallbackSearch=True)
        if result is not None and AXObject.get_role(result) not in self._topLevelRoles():
            msg = "QT: Top level object %s lacks expected role." % result
            debug.println(debug.LEVEL_INFO, msg, True)

        return result
