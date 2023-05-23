# Orca
#
# Copyright (C) 2014 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
import re

import orca.script_utilities as script_utilities
from orca.ax_object import AXObject


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._isTypeahead = {}

    def clearCachedObjects(self):
        self._isTypeahead = {}

    def isTypeahead(self, obj):
        if not (obj and AXObject.get_role(obj) == Atspi.Role.TEXT):
            return False

        rv = self._isTypeahead.get(hash(obj))
        if rv is not None:
            return rv

        parent = AXObject.get_parent(obj)
        while parent and self.isLayoutOnly(parent):
            parent = AXObject.get_parent(parent)

        rv = parent and AXObject.get_role(parent) == Atspi.Role.WINDOW
        self._isTypeahead[hash(obj)] = rv
        return rv

    def rgbFromString(self, attributeValue):
        regex = re.compile(r"rgb|[^\w,]", re.IGNORECASE)
        string = re.sub(regex, "", attributeValue)
        red, green, blue = string.split(",")

        return int(red) >> 8, int(green) >> 8, int(blue) >> 8
