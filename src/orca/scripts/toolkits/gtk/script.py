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

    def getUtilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def deactivate(self):
        """Called when this script is deactivated."""

        self.utilities.clearCachedObjects()
        super().deactivate()

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if self.utilities.isToggleDescendantOfComboBox(newFocus):
            newFocus = AXObject.find_ancestor(newFocus, AXUtilities.is_combo_box) or newFocus
            focus_manager.get_manager().set_locus_of_focus(event, newFocus, False)
        elif self.utilities.isInOpenMenuBarMenu(newFocus):
            window = self.utilities.topLevelObject(newFocus)
            if window and focus_manager.get_manager().get_active_window() != window:
                focus_manager.get_manager().set_active_window(window)

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not self.utilities.isTypeahead(focus_manager.get_manager().get_locus_of_focus()):
            msg = "GTK: locusOfFocus is not typeahead. Passing along to default script."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            super().on_active_descendant_changed(event)
            return

        msg = "GTK: locusOfFocus believed to be typeahead. Presenting change."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.presentObject(event.any_data, interrupt=True)

    def on_checked_changed(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        obj = event.source
        if self.utilities.isSameObject(obj, focus_manager.get_manager().get_locus_of_focus()):
            default.Script.on_checked_changed(self, event)
            return

        # Present changes of child widgets of GtkListBox items
        if not AXObject.find_ancestor(obj, AXUtilities.is_list_box):
            return

        self.presentObject(obj, alreadyFocused=True, interrupt=True)

    def on_focus(self, event):
        """Callback for focus: accessibility events."""

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # that fail to reliably emit object:state-changed:focused events.

        if self.utilities.eventIsCanvasNoise(event):
            return

        if self.utilities.isLayoutOnly(event.source):
            return

        if event.source == self.mouseReviewer.getCurrentItem():
            msg = "GTK: Event source is current mouse review item"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.isTypeahead(focus) \
           and AXObject.supports_table(event.source) \
           and not AXUtilities.is_focused(event.source):
            return

        ancestor = AXObject.find_ancestor(focus, lambda x: x == event.source)
        if not ancestor:
            focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return

        if AXObject.supports_table(ancestor):
            return

        if AXUtilities.is_menu(ancestor):
            if AXUtilities.is_selected(focus):
                msg = "GTK: Event source is ancestor of selected focus. Ignoring."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return
            msg = "GTK: Event source is ancestor of unselected focus. Updating focus."
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        focus_manager.get_manager().set_locus_of_focus(event, event.source)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self.utilities.isUselessPanel(event.source):
            msg = "GTK: Event source believed to be useless panel"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_ancestor(focus, event.source) and AXUtilities.is_focused(focus):
            msg = "GTK: Ignoring focus change on ancestor of still-focused locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
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
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            selectedChildren = self.utilities.selectedChildren(event.source)
            for child in selectedChildren:
                if not self.utilities.isLayoutOnly(child):
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

        if self.utilities.isPopOver(event.source) \
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
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        super().on_text_deleted(event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not (AXUtilities.is_showing(event.source) and AXUtilities.is_visible(event.source)):
            tokens = ["GTK:", event.source, "is not showing and visible"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return

        super().on_text_inserted(event)

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, focus_manager.get_manager().get_locus_of_focus()):
            return

        default.Script.on_text_selection_changed(self, event)

    def isActivatableEvent(self, event):
        if self.utilities.eventIsCanvasNoise(event):
            return False

        if self.utilities.isUselessPanel(event.source):
            return False

        return super().isActivatableEvent(event)
