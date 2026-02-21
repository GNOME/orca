# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014-2015 Igalia, S.L.
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

"""Custom script for Gecko."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca.ax_utilities import AXUtilities
from orca.scripts import web

from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(web.ToolkitBridge):
    """Custom script for Gecko."""

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if AXUtilities.is_panel(event.source):
            if focus_manager.get_manager().focus_is_active_window():
                msg = "GECKO: Ignoring event believed to be noise."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        if AXUtilities.is_frame(event.source):
            msg = "GECKO: Ignoring event believed to be noise."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_focused_changed(event)

    def on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        # TODO - JD: Is this workaround still needed? It is here because we normally get a
        # window:activate event when a context menu is shown, but not in the case of Gecko.
        if (
            event.detail1
            and AXUtilities.is_menu(event.source)
            and not self.utilities.in_document_content(event.source)
        ):
            msg = "GECKO: Setting locus of focus to newly shown menu."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return True

        return super().on_showing_changed(event)
