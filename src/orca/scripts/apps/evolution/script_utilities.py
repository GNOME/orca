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

"""Custom script utilities for Evolution."""

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import input_event_manager
from orca import focus_manager
from orca.scripts.toolkits import WebKitGTK
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Utilities(WebKitGTK.Utilities):
    """Custom script utilities for Evolution."""

    def is_message_list_status_cell(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a message list status cell."""

        if not self.is_message_list_toggle_cell(obj):
            return False

        headers = AXTable.get_column_headers(obj)
        if not headers:
            return False

        return headers[0] and AXObject.get_name(headers[0]) != AXObject.get_name(obj)

    def is_message_list_toggle_cell(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a message list toggle cell."""

        if self.is_webkit_gtk(obj):
            return False

        if not AXObject.get_name(obj):
            return False

        return self.has_meaningful_toggle_action(obj)

    def is_ignorable_event_from_document_preview(self, event: Atspi.Event) -> bool:
        """Returns True if event is from a document preview and can be ignored."""

        if not self.is_document_preview(event.source):
            return False

        if not input_event_manager.get_manager().last_event_was_unmodified_arrow():
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.is_webkit_gtk(focus):
            return False
        if not AXUtilities.is_table_cell(focus):
            return False
        if not AXObject.find_ancestor(focus, AXUtilities.is_tree_or_tree_table):
            return False

        return True

    def is_document_preview(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is or descends from the preview document."""

        if not self.is_webkit_gtk(obj):
            return False

        if AXUtilities.is_document(obj):
            document = obj
        else:
            document = AXObject.find_ancestor(obj, AXUtilities.is_document)
        if not document:
            return False

        return bool(AXObject.find_ancestor(document, AXUtilities.is_page_tab))
