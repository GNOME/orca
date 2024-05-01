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

# For the "AXUtilities has no ... member"
# pylint: disable=E1101

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Orca Team." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"


from orca import debug
from orca import focus_manager
from orca.ax_utilities import AXUtilities
from orca.scripts import default
from orca.scripts import web
from .script_utilities import Utilities


class Script(web.Script):

    def __init__(self, app):
        super().__init__(app)

        self.present_if_inactive = False

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

        if super().locus_of_focus_changed(event, old_focus, new_focus):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.locus_of_focus_changed(self, event, old_focus, new_focus)

    def on_active_changed(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if super().on_active_changed(event):
            return

        if event.detail1 and AXUtilities.is_frame(event.source) \
           and not focus_manager.get_manager().can_be_active_window(event.source):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_active_changed(self, event)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if super().on_active_descendant_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_active_descendant_changed(self, event)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.isNotRealDocument(event.source):
            msg = "GECKO: Ignoring: Event source is not real document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if super().on_busy_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_busy_changed(self, event)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if super().on_caret_moved(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_caret_moved(self, event)

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if super().on_checked_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_checked_changed(self, event)

    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        if super().on_column_reordered(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_column_reordered(self, event)

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        if super().on_children_added(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_children_added(self, event)

    def on_children_removed(self, event):
        """Callback for object:children-changed:removed accessibility events."""

        if super().on_children_removed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_children_removed(self, event)

    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""

        if self.utilities.isNotRealDocument(event.source):
            msg = "GECKO: Ignoring: Event source is not real document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if super().on_document_load_complete(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_document_load_complete(self, event)

    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if super().on_document_load_stopped(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_document_load_stopped(self, event)

    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""

        if super().on_document_reload(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_document_reload(self, event)

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if super().on_expanded_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_expanded_changed(self, event)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if super().on_focused_changed(event):
            return

        if AXUtilities.is_panel(event.source):
            if focus_manager.get_manager().focus_is_active_window():
                msg = "GECKO: Ignoring event believed to be noise."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_focused_changed(self, event)

    def on_mouse_button(self, event):
        """Callback for mouse:button accessibility events."""

        if super().on_mouse_button(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_mouse_button(self, event)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if super().on_name_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_name_changed(self, event)

    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        if super().on_row_reordered(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_row_reordered(self, event)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if super().on_selected_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_selected_changed(self, event)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        if super().on_selection_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_selection_changed(self, event)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if super().on_showing_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_showing_changed(self, event)

    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        if super().on_text_attributes_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_text_attributes_changed(self, event)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if super().on_text_deleted(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_text_deleted(self, event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if super().on_text_inserted(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_text_inserted(self, event)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if super().on_text_selection_changed(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_text_selection_changed(self, event)

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        if not focus_manager.get_manager().can_be_active_window(event.source):
            return

        if super().on_window_activated(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_window_activated(self, event)

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        if super().on_window_deactivated(event):
            return

        msg = "GECKO: Passing along event to default script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        default.Script.on_window_deactivated(self, event)
