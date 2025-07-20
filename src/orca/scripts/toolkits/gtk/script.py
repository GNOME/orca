# Orca
#
# Copyright (C) 2013-2014 Igalia, S.L.
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

"""Custom script for GTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013-2014 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import focus_manager
from orca.scripts import default
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

class Script(default.Script):
    """Custom script for GTK."""

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

        manager = focus_manager.get_manager()
        if AXUtilities.is_toggle_button(new_focus):
            new_focus = AXObject.find_ancestor(new_focus, AXUtilities.is_combo_box) or new_focus
            manager.set_locus_of_focus(event, new_focus, False)
        elif AXObject.find_ancestor(new_focus, AXUtilities.is_menu_bar):
            window = self.utilities.topLevelObject(new_focus)
            if window and manager.get_active_window() != window:
                manager.set_active_window(window)

        super().locus_of_focus_changed(event, old_focus, new_focus)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if AXUtilities.is_table_related(event.source):
            AXObject.clear_cache(event.any_data, True, "active-descendant-changed event.")
            AXUtilities.clear_all_cache_now(event.source, "active-descendant-changed event.")

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_table_cell(focus):
            table = AXObject.find_ancestor(focus, AXUtilities.is_tree_or_tree_table)
            if table is not None and table != event.source:
                msg = "GTK: Event is from a different tree or tree table."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return

        child = AXObject.get_active_descendant_checked(event.source, event.any_data)
        if child is not None and child != event.any_data:
            tokens = ["GTK: Bogus any_data suspected. Setting focus to", child]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, child)
            return

        msg = "GTK: Passing event to super class for processing."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        super().on_active_descendant_changed(event)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if not AXUtilities.is_focused(event.source):
            AXObject.clear_cache(event.source, False, "Work around possibly-missing focused state.")
        super().on_caret_moved(event)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_ancestor(focus, event.source) and AXUtilities.is_focused(focus):
            msg = "GTK: Ignoring focus change on ancestor of still-focused locusOfFocus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        super().on_focused_changed(event)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        # Handle changes within an entry completion popup.
        if AXUtilities.is_table_cell(event.source) \
           and AXObject.find_ancestor(event.source, AXUtilities.is_window) is not None:
            if event.detail1:
                focus_manager.get_manager().set_locus_of_focus(event, event.source)
                return
            if focus_manager.get_manager().get_locus_of_focus() == event.source:
                focus_manager.get_manager().set_locus_of_focus(event, None)
                return

        if AXUtilities.is_icon_or_canvas(event.source) \
           and self.utilities.handleContainerSelectionChange(AXObject.get_parent(event.source)):
            return

        super().on_selected_changed(event)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_toggle_button(focus) and AXUtilities.is_combo_box(event.source) \
           and AXObject.is_ancestor(focus, event.source):
            super().on_selection_changed(event)
            return

        is_focused = AXUtilities.is_focused(event.source)
        if AXUtilities.is_combo_box(event.source) and not is_focused:
            return

        if AXUtilities.is_layered_pane(event.source) \
           and self.utilities.selectedChildCount(event.source) > 1:
            return

        super().on_selection_changed(event)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if not event.detail1:
            super().on_showing_changed(event)
            return

        if AXUtilities.get_is_popup_for(event.source) \
           or AXUtilities.is_alert(event.source) \
           or AXUtilities.is_info_bar(event.source):
            if AXUtilities.is_application(AXObject.get_parent(event.source)):
                return
            self.present_object(event.source, interrupt=True)
            return

        super().on_showing_changed(event)
