# Orca
#
# Copyright 2018-2019 Igalia, S.L.
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

"""Custom script for Chromium."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import debug, focus_manager
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import web

from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(web.ToolkitBridge):
    """Custom script for Chromium."""

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if not AXUtilities.is_web_element(event.source) and AXUtilities.is_web_element(
            AXObject.get_parent(event.source),
        ):
            msg = "CHROMIUM: Ignoring because source is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_caret_moved(event)

    def on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        if AXUtilities.is_web_element(event.source) and not AXUtilities.is_web_element(
            event.any_data,
        ):
            msg = "CHROMIUM: Ignoring because child is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_children_added(event)

    def on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:removed accessibility events."""

        if AXUtilities.is_web_element(event.source) and not AXUtilities.is_web_element(
            event.any_data,
        ):
            msg = "CHROMIUM: Ignoring because child is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_children_removed(event)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if self.utilities.is_document(event.source) and not AXDocument.get_uri(event.source):
            msg = "CHROMIUM: Ignoring event from document with no URI."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_focused_changed(event)

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        if event.detail1 and not self.utilities.in_document_content(event.source):  # type: ignore
            if listbox := AXObject.find_ancestor(event.source, AXUtilities.is_list_box):
                parent = AXObject.get_parent(listbox)
                if AXUtilities.is_frame(parent) and not AXObject.get_name(parent):
                    msg = "CHROMIUM: Event source believed to be in autocomplete popup"
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    focus_manager.get_manager().set_locus_of_focus(event, event.source)
                    return True

        return super().on_selected_changed(event)

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        if not AXUtilities.is_web_element(event.source) and AXUtilities.is_web_element(
            AXObject.get_parent(event.source),
        ):
            msg = "CHROMIUM: Ignoring because source is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_text_selection_changed(event)

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)

        for child in AXObject.iter_children(event.source):
            if AXUtilities.is_alert(child):
                self.present_object(child)

        return True
