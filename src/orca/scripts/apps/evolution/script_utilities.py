# Orca
#
# Copyright (C) 2015 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.scripts.toolkits.gtk as gtk
import orca.scripts.toolkits.WebKitGtk as WebKitGtk

class Utilities(WebKitGtk.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def isMessageListToggleCell(self, obj):
        if self.isWebKitGtk(obj):
            return False

        if not gtk.Utilities.hasMeaningfulToggleAction(self, obj):
            return False

        if not obj.name:
            return False

        header = self.columnHeaderForCell(obj)
        return header and header.name == obj.name
