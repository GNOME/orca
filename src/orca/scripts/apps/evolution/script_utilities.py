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

from orca.scripts.toolkits import gtk
from orca.scripts.toolkits import WebKitGTK
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities


class Utilities(WebKitGTK.Utilities, gtk.Utilities):

    def isMessageListStatusCell(self, obj):
        if not self.isMessageListToggleCell(obj):
            return False

        headers = AXTable.get_column_headers(obj)
        if not headers:
            return False

        return headers[0] and AXObject.get_name(headers[0]) != AXObject.get_name(obj)

    def isMessageListToggleCell(self, obj):
        if self.isWebKitGTK(obj):
            return False

        if not gtk.Utilities.hasMeaningfulToggleAction(self, obj):
            return False

        if not AXObject.get_name(obj):
            return False

        return True

    def realActiveDescendant(self, obj):
        if self.isWebKitGTK(obj):
            return super().realActiveDescendant(obj)

        # TODO - JD: Is this still needed?
        # This is some mystery child of the 'Messages' panel which fails to show
        # up in the hierarchy or emit object:state-changed:focused events.
        if AXUtilities.is_layered_pane(obj):
            return AXObject.find_descendant(obj, AXUtilities.is_tree_table) or obj

        return gtk.Utilities.realActiveDescendant(self, obj)
