# Orca
#
# Copyright 2016 Igalia, S.L.
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

"""Script for terminal support."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca import typing_echo_presenter
from orca.scripts import default
from orca.ax_text import AXText

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(default.Script):
    """Script for terminal support."""

    utilities: Utilities

    def __init__(self, app: Atspi.Accessible) -> None:
        super().__init__(app)
        self.present_if_inactive: bool = False

    def get_braille_generator(self) -> BrailleGenerator:
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self) -> SpeechGenerator:
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        if self.utilities.treat_event_as_noise(event):
            msg = "TERMINAL: Deletion is believed to be noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_text_deleted(event)

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        typing_echo_presenter.get_presenter().echo_delayed_terminal_press(self, event)

        if not self.utilities.treat_event_as_command(event):
            msg = "TERMINAL: Passing along event to default script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return super().on_text_inserted(event)

        msg = "TERMINAL: Insertion is believed to be due to terminal command"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self.update_braille(event.source)

        new_string = self.utilities.inserted_text(event)
        if len(new_string) == 1:
            self.speak_character(new_string)
        else:
            voice = self.speech_generator.voice(obj=event.source, string=new_string)
            self.speak_message(new_string, voice)

        if self.get_flat_review_presenter().is_active():
            msg = "TERMINAL: Flat review presenter is active. Ignoring insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        offset = AXText.get_caret_offset(event.source)
        focus_manager.get_manager().set_last_cursor_position(event.source, offset)
        AXText.update_cached_selected_text(event.source)
        return True
