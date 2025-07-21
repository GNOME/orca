# Orca
#
# Copyright 2019 Igalia, S.L.
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

"""Custom script for basic switchers like Metacity."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2019 Igalia, S.L."
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

    def force_script_activation(self, event):
        """Allows scripts to insist that they should become active."""

        if self.utilities.isSwitcherSelectionChangeEventType(event):
            return True

        return super().force_script_activation(event)

    def _handleSwitcherEvent(self, event):
        """Presents the currently selected item, if appropriate."""

        if not self.utilities.isSwitcherContainer(event.source):
            msg = "SWITCHER: Event is not from switcher container"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.isSwitcherSelectionChangeEventType(event):
            msg = "SWITCHER: Not treating event as selection change."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "SWITCHER: Treating event as selection change"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.interrupt_presentation()
        focus_manager.get_manager().set_active_window(self.utilities.topLevelObject(event.source))
        focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        self.present_message(self.utilities.getSelectionName(event.source),
                            reset_styles=False, force=True)
        return True

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        if AXUtilities.is_window(new_focus) and not AXObject.get_name(new_focus):
            msg = "SWITCHER: Not presenting newly-focused nameless window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        super().locus_of_focus_changed(event, old_focus, new_focus)

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_focused_changed(event)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_name_changed(event)

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_selected_changed(event)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_selection_changed(event)

    def on_showing_changed(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_showing_changed(event)

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_caret_moved(event)

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_text_deleted(event)

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self._handleSwitcherEvent(event):
            return

        super().on_text_inserted(event)
