# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Custom script for WebKitGTK."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


from typing import TYPE_CHECKING

from orca import focus_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import web
from orca.scripts.toolkits import gtk

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(web.ToolkitBridge, gtk.Script):
    """Custom script for WebKitGTK."""

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        # TODO - JD: This is likely needed for https://bugs.webkit.org/show_bug.cgi?id=268154,
        # but we should verify if the default logic now takes care of this for us.
        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self.utilities.in_document_content(focus):
            document = self.utilities.get_document_for_object(event.source)
            if document:
                ancestor = AXObject.find_ancestor(document, AXUtilities.is_focused)
                if self.utilities.in_document_content(ancestor):
                    focus_manager.get_manager().set_locus_of_focus(None, document)

        return super().on_caret_moved(event)
