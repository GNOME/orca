# Orca
#
# Copyright 2023 Igalia, S.L.
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

"""
A script which has no commands, has no presentation, and ignores events.
The main use cases for this script are self-voicing apps and VMs which
should be usable without having to quit Orca entirely.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

from orca import braille
from orca import debug
from orca import focus_manager
from orca import messages
from orca import orca_modifier_manager
from orca.scripts import default
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(default.Script):
    """The sleep-mode script."""

    def activate(self) -> None:
        """Called when this script is activated."""

        tokens = ["SLEEP MODE: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        orca_modifier_manager.get_manager().unset_orca_modifiers("Entering sleep mode.")
        self.add_key_grabs("script activation")

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

        tokens = ["SLEEP MODE: De-activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self.remove_key_grabs("script deactivation")
        orca_modifier_manager.get_manager().refresh_orca_modifiers("Exiting sleep mode.")

    def get_braille_generator(self) -> BrailleGenerator:
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self) -> SpeechGenerator:
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_braille_bindings(self) -> dict[str, Any]:
        """Returns the braille bindings for this script."""

        msg = "SLEEP MODE: Has no braille bindings."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return {}

    def get_key_bindings(self, enabled_only: bool = True) -> Any:
        """Defines and returns the key bindings for this script."""

        return self.get_sleep_mode_manager().get_bindings()

    def add_key_grabs(self, reason: str = "") -> None:
        """Adds key grabs for this script."""

        self.key_bindings = self.get_key_bindings()
        self.key_bindings.add_key_grabs()

    def remove_key_grabs(self, reason: str = "") -> None:
        """Adds key grabs for this script."""

        self.key_bindings.remove_key_grabs(reason)

    def setup_input_event_handlers(self) -> Any:
        """Defines the input event handlers for this script."""

        return self.get_sleep_mode_manager().get_handlers()

    def update_braille(self, obj: Atspi.Accessible, **args: Any) -> None:
        """Updates the braille display to show the give object."""

        msg = "SLEEP MODE: Not updating braille."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        tokens = ["SLEEP MODE: focus changed from", old_focus, "to", new_focus, "due to", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if old_focus is None and AXUtilities.is_application(AXObject.get_parent(new_focus)):
            focus_manager.get_manager().clear_state("Sleep mode enabled for this app.")
            braille.clear()
            self.present_message(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(self.app))
            return True

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:active-descendant-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_checked_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:checked accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_column_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:column-reordered accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:removed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_document_load_complete(self, event: Atspi.Event) -> bool:
        """Callback for document:load-complete accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_document_load_stopped(self, event: Atspi.Event) -> bool:
        """Callback for document:load-stopped accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_document_reload(self, event: Atspi.Event) -> bool:
        """Callback for document:reload accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_text_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-attributes-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        focus_manager.get_manager().clear_state("Sleep mode enabled for this app.")
        braille.clear()
        self.present_message(messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(self.app))
        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True
