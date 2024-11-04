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
from .script_utilities import Utilities


class Script(default.Script):

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def deactivate(self):
        """Called when this script is deactivated."""

        self.utilities.clearCachedObjects()
        super().deactivate()

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

        manager = focus_manager.get_manager()
        if self.utilities.isToggleDescendantOfComboBox(new_focus):
            new_focus = AXObject.find_ancestor(new_focus, AXUtilities.is_combo_box) or new_focus
            manager.set_locus_of_focus(event, new_focus, False)
        elif self.utilities.isInOpenMenuBarMenu(new_focus):
            window = self.utilities.topLevelObject(new_focus)
            if window and manager.get_active_window() != window:
                manager.set_active_window(window)

        super().locus_of_focus_changed(event, old_focus, new_focus)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.isTypeahead(focus):
            msg = "GTK: Locus of focus believed to be typeahead. Presenting change."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.presentObject(event.any_data, interrupt=True)
            return

        if AXUtilities.is_table_related(event.source):
            AXObject.clear_cache(event.any_data, True, "active-descendant-changed event.")
            AXUtilities.clear_all_cache_now(event.source, "active-descendant-changed event.")

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

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if event.source == focus_manager.get_manager().get_locus_of_focus():
            default.Script.on_checked_changed(self, event)
            return

        # Present changes of child widgets of GtkListBox items
        if not AXObject.find_ancestor(event.source, AXUtilities.is_list_box):
            return

        self.presentObject(event.source, alreadyFocused=True, interrupt=True)

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

        if self.utilities.isEntryCompletionPopupItem(event.source):
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
        if self.utilities.isComboBoxWithToggleDescendant(event.source) \
            and self.utilities.isOrDescendsFrom(focus, event.source):
            super().on_selection_changed(event)
            return

        isFocused = AXUtilities.is_focused(event.source)
        if AXUtilities.is_combo_box(event.source) and not isFocused:
            return

        if not isFocused and self.utilities.isTypeahead(focus):
            msg = "GTK: locusOfFocus believed to be typeahead. Presenting change."
            debug.print_message(debug.LEVEL_INFO, msg, True)

            selectedChildren = self.utilities.selectedChildren(event.source)
            for child in selectedChildren:
                if not AXUtilities.is_layout_only(child):
                    self.presentObject(child)
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
            self.presentObject(event.source, interrupt=True)
            return

        super().on_showing_changed(event)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not (AXUtilities.is_showing(event.source) and AXUtilities.is_visible(event.source)):
            tokens = ["GTK:", event.source, "is not showing and visible"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        super().on_text_deleted(event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not (AXUtilities.is_showing(event.source) and AXUtilities.is_visible(event.source)):
            tokens = ["GTK:", event.source, "is not showing and visible"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        super().on_text_inserted(event)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if event.source != focus_manager.get_manager().get_locus_of_focus():
            return

        super().on_text_selection_changed(event)

    def is_activatable_event(self, event):
        """Returns True if event should cause this script to become active."""

        if self.utilities.eventIsCanvasNoise(event):
            return False

        return super().is_activatable_event(event)
