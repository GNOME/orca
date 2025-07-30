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

"""Custom script for gnome-shell."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010-2013 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import default
from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(default.Script):
    """Custom script for gnome-shell."""

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def is_activatable_event(self, event: Atspi.Event) -> bool:
        """Returns True if event should cause this script to become active."""

        if event.type.startswith("object:state-changed:selected") and event.detail1:
            return True

        return super().is_activatable_event(event)

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        # TODO - JD: This workaround no longer works because the window has a name.
        if event is not None and event.type == "window:activate" \
          and new_focus is not None and not AXObject.get_name(new_focus):
            queued_event = self._get_queued_event("object:state-changed:focused", True)
            if queued_event and queued_event.source != event.source:
                msg = "GNOME SHELL: Have matching focused event. Not announcing nameless window."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        return super().locus_of_focus_changed(event, old_focus, new_focus)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return True

        # We're getting a spurious focus claim from the gnome-shell window after
        # the window switcher is used.
        if AXUtilities.is_window(event.source):
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_panel(event.source) and AXObject.is_ancestor(focus, event.source):
            msg = "GNOME SHELL: Event ignored: Source is panel ancestor of current focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not AXObject.get_name(event.source) and AXUtilities.is_menu_item(event.source) \
           and not AXUtilities.get_is_labelled_by(event.source):
            descendant = AXObject.find_descendant(event.source, AXUtilities.is_slider)
            if descendant is not None:
                focus_manager.get_manager().set_locus_of_focus(event, descendant)
                return True

        return super().on_focused_changed(event)

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if not AXUtilities.is_label(event.source):
            return super().on_name_changed(event)

        # If we're already in a dialog, and a label inside that dialog changes its name,
        # present the new name. Example: the "Command not found" label in the Run dialog.
        dialog = AXObject.find_ancestor(
            focus_manager.get_manager().get_locus_of_focus(), AXUtilities.is_dialog)
        tokens = ["GNOME SHELL: focus is in dialog:", dialog]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if dialog and AXObject.is_ancestor(event.source, dialog):
            msg = "GNOME SHELL: Label changed name in current dialog. Presenting."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.present_message(AXObject.get_name(event.source))

        return True

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        # gnome-shell fails to implement the selection interface but fires state-changed
        # selected in the switcher and similar containers.
        if AXUtilities.is_selected(event.source):
            focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return True

        return super().on_selected_changed(event)
