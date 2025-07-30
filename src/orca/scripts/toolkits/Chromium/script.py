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

# pylint: disable=too-many-public-methods

"""Custom script for Chromium."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca.ax_document import AXDocument
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import default
from orca.scripts import web

from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(web.Script):
    """Custom script for Chromium."""

    def __init__(self, app: Atspi.Accessible) -> None:
        super().__init__(app)
        self.present_if_inactive: bool = False

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        if super().locus_of_focus_changed(event, old_focus, new_focus):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.locus_of_focus_changed(self, event, old_focus, new_focus)

    def on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        if super().on_active_changed(event):
            return True

        if event.detail1 and AXUtilities.is_frame(event.source) \
           and not AXUtilities.can_be_active_window(event.source):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_active_changed(self, event)

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        if super().on_busy_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_busy_changed(self, event)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if not AXUtilities.is_web_element(event.source) \
           and AXUtilities.is_web_element(AXObject.get_parent(event.source)):
            msg = "CHROMIUM: Ignoring because source is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_caret_moved(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_caret_moved(self, event)

    def on_checked_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:checked accessibility events."""

        if super().on_checked_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_checked_changed(self, event)

    def on_column_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:column-reordered accessibility events."""

        if super().on_column_reordered(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_column_reordered(self, event)

    def on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        if AXUtilities.is_web_element(event.source) \
           and not AXUtilities.is_web_element(event.any_data):
            msg = "CHROMIUM: Ignoring because child is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_children_added(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_children_added(self, event)

    def on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:removed accessibility events."""

        if AXUtilities.is_web_element(event.source) \
           and not AXUtilities.is_web_element(event.any_data):
            msg = "CHROMIUM: Ignoring because child is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_children_removed(event):
            return True

        msg = "Chromium: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_children_removed(self, event)

    def on_document_load_complete(self, event: Atspi.Event) -> bool:
        """Callback for document:load-complete accessibility events."""

        if super().on_document_load_complete(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_document_load_complete(self, event)

    def on_document_load_stopped(self, event: Atspi.Event) -> bool:
        """Callback for document:load-stopped accessibility events."""

        if not AXDocument.get_uri(event.source):
            msg = "CHROMIUM: Ignoring event from page with no URI."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_document_load_stopped(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_document_load_stopped(self, event)

    def on_document_reload(self, event: Atspi.Event) -> bool:
        """Callback for document:reload accessibility events."""

        if not AXDocument.get_uri(event.source):
            msg = "CHROMIUM: Ignoring event from page with no URI."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_document_reload(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_document_reload(self, event)

    def on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        if super().on_expanded_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_expanded_changed(self, event)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if (self.utilities.is_document(event.source) and not AXDocument.get_uri(event.source)):
            msg = "CHROMIUM: Ignoring event from document with no URI."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_focused_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_focused_changed(self, event)

    def on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button accessibility events."""

        if super().on_mouse_button(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_mouse_button(self, event)

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if super().on_name_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_name_changed(self, event)

    def on_row_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:row-reordered accessibility events."""

        if super().on_row_reordered(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_row_reordered(self, event)

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        if super().on_selected_changed(event):
            return True

        if event.detail1 and not self.utilities.in_document_content(event.source):  # type: ignore
            # The popup for an input with autocomplete on is a listbox child of a nameless frame.
            # It lives outside of the document and also doesn't fire selection-changed events.
            if listbox := AXObject.find_ancestor(event.source, AXUtilities.is_list_box):
                parent = AXObject.get_parent(listbox)
                if AXUtilities.is_frame(parent) and not AXObject.get_name(parent):
                    msg = "CHROMIUM: Event source believed to be in autocomplete popup"
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    focus_manager.get_manager().set_locus_of_focus(event, event.source)
                    return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_selected_changed(self, event)

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        if super().on_selection_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_selection_changed(self, event)

    def on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        if super().on_showing_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_showing_changed(self, event)

    def on_text_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-attributes-changed accessibility events."""

        if super().on_text_attributes_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_text_attributes_changed(self, event)

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        if super().on_text_deleted(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_text_deleted(self, event)

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        if super().on_text_inserted(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_text_inserted(self, event)

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        if not AXUtilities.is_web_element(event.source) \
           and AXUtilities.is_web_element(AXObject.get_parent(event.source)):
            msg = "CHROMIUM: Ignoring because source is not an element"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if super().on_text_selection_changed(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_text_selection_changed(self, event)

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        if not AXUtilities.can_be_active_window(event.source):
            return True

        if super().on_window_activated(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        default.Script.on_window_activated(self, event)

        # Right now we don't get accessibility events for alerts which are
        # already showing at the time of window activation. If that changes,
        # we should store presented alerts so we don't double-present them.
        for child in AXObject.iter_children(event.source):
            if AXUtilities.is_alert(child):
                self.present_object(child)

        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        if super().on_window_deactivated(event):
            return True

        msg = "CHROMIUM: Passing along event to default script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return default.Script.on_window_deactivated(self, event)
