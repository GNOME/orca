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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

from orca import debug
from orca import focus_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import web
from orca.scripts.toolkits import gtk

from .script_utilities import Utilities

class Script(web.Script, gtk.Script):

    def __init__(self, app):
        super().__init__(app)

        # To ensure that when the Gtk script is active, events from document content
        # are not ignored.
        self.present_if_inactive = True

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

        if super().locus_of_focus_changed(event, old_focus, new_focus):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.locus_of_focus_changed(self, event, old_focus, new_focus)

    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if super().on_active_changed(event):
            return

        if event.detail1 and AXUtilities.is_frame(event.source) \
           and not AXUtilities.can_be_active_window(event.source):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_active_changed(self, event)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if super().on_busy_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_busy_changed(self, event)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        tokens = ["WEBKITGTK: Locus of focus is", focus]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.utilities.isWebKitGTK(focus):
            document = self.utilities.getDocumentForObject(event.source)
            if document:
                ancestor = AXObject.find_ancestor(document, AXUtilities.is_focused)
                if self.utilities.isWebKitGTK(ancestor):
                    focus_manager.get_manager().set_locus_of_focus(None, document)

        if super().on_caret_moved(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_caret_moved(self, event)

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if super().on_checked_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_checked_changed(self, event)

    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        if super().on_column_reordered(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_column_reordered(self, event)

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        if super().on_children_added(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_children_added(self, event)

    def on_children_removed(self, event):
        """Callback for object:children-changed:removed accessibility events."""

        if super().on_children_removed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_children_removed(self, event)

    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""

        if super().on_document_load_complete(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_document_load_complete(self, event)

    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if super().on_document_load_stopped(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_document_load_stopped(self, event)

    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""

        if super().on_document_reload(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_document_reload(self, event)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if super().on_expanded_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_expanded_changed(self, event)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if super().on_focused_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_focused_changed(self, event)

    def on_mouse_button(self, event):
        """Callback for mouse:button accessibility events."""

        if super().on_mouse_button(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_mouse_button(self, event)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if super().on_name_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_name_changed(self, event)

    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        if super().on_row_reordered(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_row_reordered(self, event)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if super().on_selected_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_selected_changed(self, event)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        if super().on_selection_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_selection_changed(self, event)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if super().on_showing_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_showing_changed(self, event)

    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        if super().on_text_attributes_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_text_attributes_changed(self, event)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if super().on_text_deleted(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_text_deleted(self, event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if super().on_text_inserted(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_text_inserted(self, event)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if super().on_text_selection_changed(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_text_selection_changed(self, event)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        if super().on_window_activated(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_window_activated(self, event)

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if super().on_window_deactivated(event):
            return

        msg = "WEBKITGTK: Passing along event to gtk script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gtk.Script.on_window_deactivated(self, event)
