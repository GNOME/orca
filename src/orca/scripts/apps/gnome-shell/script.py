# Orca
#
# Copyright (C) 2010-2013 Igalia, S.L.
#
# Author: Alejandro Pinheiro Iglesias <apinheiro@igalia.com>
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
__copyright__ = "Copyright (c) 2010-2013 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import focus_manager
from orca.scripts.toolkits import clutter
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .formatting import Formatting
from .script_utilities import Utilities


class Script(clutter.Script):

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        return Utilities(self)

    def deactivate(self):
        """Called when this script is deactivated."""

        self.utilities.clearCachedObjects()
        super().deactivate()

    def skipObjectEvent(self, event):
        """Determines whether or not this event should be skipped due to
        being redundant, part of an event flood, etc."""

        if AXUtilities.is_window(event.source):
            return self.utilities.isBogusWindowFocusClaim(event)

        return clutter.Script.skipObjectEvent(self, event)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        if event is not None and event.type == "window:activate" \
          and newFocus is not None and not AXObject.get_name(newFocus):
            queuedEvent = self._getQueuedEvent("object:state-changed:focused", True)
            if queuedEvent and queuedEvent.source != event.source:
                msg = "GNOME SHELL: Have matching focused event. Not announcing nameless window."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if not AXUtilities.is_label(event.source):
            clutter.Script.on_name_changed(self, event)
            return

        # If we're already in a dialog, and a label inside that dialog changes its name,
        # present the new name. Example: the "Command not found" label in the Run dialog.
        dialog = AXObject.find_ancestor(
            focus_manager.getManager().get_locus_of_focus(), AXUtilities.is_dialog)
        tokens = ["GNOME SHELL: focus is in dialog:", dialog]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if dialog and AXObject.is_ancestor(event.source, dialog):
            msg = "GNOME SHELL: Label changed name in current dialog. Presenting."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.presentMessage(AXObject.get_name(event.source))

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        # Some buttons, like the Wikipedia button, claim to be selected but
        # lack STATE_SELECTED. The other buttons, such as in the Dash and
        # event switcher, seem to have the right state. Since the ones with
        # the wrong state seem to be things we don't want to present anyway
        # we'll stop doing so and hope we are right.
        # TODO - JD: 1) Is this logic still needed? 2) If so, is clearing the
        # cache still needed?
        if event.detail1:
            if AXUtilities.is_panel(event.source):
                AXObject.clear_cache(event.source, False, "Ensuring we have the correct state.")
            if AXUtilities.is_selected(event.source):
                focus_manager.getManager().set_locus_of_focus(event, event.source)
            return

        clutter.Script.on_selected_changed(self, event)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        # We're getting a spurious focus claim from the gnome-shell window after
        # the window switcher is used.
        if AXUtilities.is_window(event.source):
            return

        if not AXObject.get_name(event.source) and AXUtilities.is_menu_item(event.source) \
           and not self.utilities.labelsForObject(event.source):
            descendant = AXObject.find_descendant(event.source, AXUtilities.is_slider)
            if descendant is not None:
                focus_manager.getManager().set_locus_of_focus(event, descendant)
                return

        clutter.Script.on_focused_changed(self, event)

    def isActivatableEvent(self, event):
        if event.type.startswith('object:state-changed:selected') and event.detail1:
            return True

        if self.utilities.isBogusWindowFocusClaim(event):
            return False

        return super().isActivatableEvent(event)
