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

"""
A script which has no commands, has no presentation, and ignores events.
The main use cases for this script are self-voicing apps and VMs which
should be usable without having to quit Orca entirely.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


from orca import command_manager
from orca import debug
from orca import focus_manager
from orca import messages
from orca import orca_modifier_manager
from orca import presentation_manager
from orca import script
from orca import sleep_mode_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(script.Script):
    """The sleep-mode script."""

    def activate(self) -> None:
        """Called when this script is activated."""

        tokens = ["SLEEP MODE: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        exceptions = frozenset({sleep_mode_manager.SleepModeManager.COMMAND_NAME})
        command_manager.get_manager().set_all_suspended(True, exceptions)
        orca_modifier_manager.get_manager().unset_orca_modifiers("Entering sleep mode.")

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

        tokens = ["SLEEP MODE: De-activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        command_manager.get_manager().set_all_suspended(False)
        orca_modifier_manager.get_manager().refresh_orca_modifiers("Leaving sleep mode.")

    def get_braille_generator(self) -> BrailleGenerator:
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self) -> SpeechGenerator:
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None,
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        tokens = ["SLEEP MODE: focus changed from", old_focus, "to", new_focus, "due to", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if old_focus is None and AXUtilities.is_application(AXObject.get_parent(new_focus)):
            focus_manager.get_manager().clear_state("Sleep mode enabled for this app.")
            msg = messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(self.app)
            manager = presentation_manager.get_manager()
            manager.speak_message(msg)

            # Don't restore previous braille content because Orca is no longer active.
            manager.present_braille_message(msg, restore_previous=False)
            return True

        msg = "SLEEP MODE: Ignoring event."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        focus_manager.get_manager().clear_state("Sleep mode enabled for this app.")
        msg = messages.SLEEP_MODE_ENABLED_FOR % AXObject.get_name(self.app)
        manager = presentation_manager.get_manager()
        manager.speak_message(msg)

        # Don't restore previous braille content because Orca is no longer active.
        manager.present_braille_message(msg, restore_previous=False)
        return True
