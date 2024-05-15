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

from orca import input_event_manager
from orca import focus_manager
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

    def isIgnorableEventFromDocumentPreview(self, obj):
        if not self.isDocumentPreview(obj):
            return False

        if not input_event_manager.get_manager().last_event_was_unmodified_arrow():
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.isWebKitGTK(focus):
            return False
        if not AXUtilities.is_table_cell(focus):
            return False
        if not AXObject.find_ancestor(focus, AXUtilities.is_tree_or_tree_table):
            return False

        return True

    def isDocumentPreview(self, obj):
        """Returns True if obj is or descends from the preview document."""

        if not self.isWebKitGTK(obj):
            return False

        if AXUtilities.is_document(obj):
            document = obj
        else:
            document = AXObject.find_ancestor(obj, AXUtilities.is_document)
        if not document:
            return False

        return AXObject.find_ancestor(document, AXUtilities.is_page_tab)

    def realActiveDescendant(self, obj):
        if self.isWebKitGTK(obj):
            return super().realActiveDescendant(obj)

        # TODO - JD: Is this still needed?
        # This is some mystery child of the 'Messages' panel which fails to show
        # up in the hierarchy or emit object:state-changed:focused events.
        if AXUtilities.is_layered_pane(obj):
            return AXObject.find_descendant(obj, AXUtilities.is_tree_table) or obj

        return gtk.Utilities.realActiveDescendant(self, obj)
