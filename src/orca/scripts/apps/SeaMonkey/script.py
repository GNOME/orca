# Orca
#
# Copyright 2016 Igalia, S.L.
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


"""Custom script for SeaMonkey."""

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import cmdnames
from orca import debug
from orca import focus_manager
from orca import input_event
from orca.ax_table import AXTable
from orca.scripts.toolkits import Gecko

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from orca.scripts.toolkits.Gecko.script_utilities import Utilities


class Script(Gecko.Script):
    """Custom script for SeaMonkey."""

    # Type annotation to help with method resolution
    utilities: "Utilities"

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()

        self.input_event_handlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggle_presentation_mode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.input_event_handlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enable_sticky_focus_mode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.input_event_handlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enable_sticky_browse_mode,
                cmdnames.SET_BROWSE_MODE_STICKY)

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.is_content_editable_with_embedded_objects(event.source):
            msg = "SEAMONKEY: Ignoring, event source is content editable"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table and not self.utilities.is_text_document_table(table):
            msg = "SEAMONKEY: Ignoring, table is not text-document table"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_busy_changed(event)

    def use_focus_mode(
        self,
        obj: Atspi.Accessible,
        prev_obj: Atspi.Accessible | None = None
    ) -> bool:
        if self.utilities.is_editable_message(obj):
            tokens = ["SEAMONKEY: Using focus mode for editable message", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["SEAMONKEY:", obj, "is not an editable message."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return super().use_focus_mode(obj, prev_obj)

    def enable_sticky_browse_mode(
        self,
        inputEvent: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        if self.utilities.is_editable_message(focus_manager.get_manager().get_locus_of_focus()):
            return True

        return super().enable_sticky_browse_mode(inputEvent, force_message)

    def enable_sticky_focus_mode(
        self,
        inputEvent: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        if self.utilities.is_editable_message(focus_manager.get_manager().get_locus_of_focus()):
            return True

        return super().enable_sticky_focus_mode(inputEvent, force_message)

    def toggle_presentation_mode(
        self,
        event: input_event.InputEvent | None = None,
        document: Atspi.Accessible | None = None,
        notify_user: bool = True
    ) -> bool:
        if self._in_focus_mode \
           and self.utilities.is_editable_message(focus_manager.get_manager().get_locus_of_focus()):
            return True

        return super().toggle_presentation_mode(event, document)
