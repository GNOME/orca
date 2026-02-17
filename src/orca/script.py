# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

# pylint:disable=too-many-instance-attributes
# pylint:disable=too-many-public-methods
# pylint:disable=unused-argument

"""The base Script class."""

from __future__ import annotations
from typing import TYPE_CHECKING

from . import braille_generator
from . import chat_presenter
from . import debug
from . import script_utilities
from . import sound_generator
from . import speech_generator
from . import structural_navigator
from .ax_object import AXObject

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import label_inference


class Script:
    """The base Script class."""

    def __init__(self, app: Atspi.Accessible) -> None:
        self.app = app
        self.app_name: str | None = AXObject.get_name(self.app) or None
        self.name = f"{self.app_name or 'default'} (module={self.__module__})"
        self.present_if_inactive: bool = True
        self.run_find_command_on: Atspi.Accessible | None = None
        self.point_of_reference: dict = {}
        self.event_cache: dict = {}

        self.listeners = self.get_listeners()
        self.utilities = self.get_utilities()

        self.braille_generator = self.get_braille_generator()
        self.sound_generator = self.get_sound_generator()
        self.speech_generator = self.get_speech_generator()

        # pylint:disable=assignment-from-none
        self.label_inference = self.get_label_inference()
        self.chat = self.get_chat()
        # pylint:enable=assignment-from-none

        self.set_up_commands()

        self._default_sn_mode: structural_navigator.NavigationMode = (
            structural_navigator.NavigationMode.OFF
        )
        self._default_caret_navigation_enabled: bool = False

        msg = f"SCRIPT: {self.name} initialized"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_listeners(self) -> dict:
        """Returns a dictionary of the event listeners for this script."""

        return {}

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

    def get_braille_generator(self) -> braille_generator.BrailleGenerator:
        """Returns the braille generator for this script."""

        return braille_generator.BrailleGenerator(self)

    def get_sound_generator(self) -> sound_generator.SoundGenerator:
        """Returns the sound generator for this script."""

        return sound_generator.SoundGenerator(self)

    def get_speech_generator(self) -> speech_generator.SpeechGenerator:
        """Returns the speech generator for this script."""

        return speech_generator.SpeechGenerator(self)

    def get_chat(self) -> chat_presenter.Chat:
        """Returns the Chat object for this script."""

        # In practice, self will always be an instance/subclass of default.Script.
        return chat_presenter.Chat(self)  # type: ignore[arg-type]

    def get_utilities(self) -> script_utilities.Utilities:
        """Returns the utilities for this script."""

        return script_utilities.Utilities(self)

    def get_label_inference(self) -> label_inference.LabelInference | None:
        """Returns the label inference functionality for this script."""

        return None

    def _get_queued_event(
        self, event_type: str, detail1: int | None = None, detail2: int | None = None, any_data=None
    ) -> Atspi.Event | None:
        cached_event = self.event_cache.get(event_type, [None, 0])[0]
        if not cached_event:
            tokens = ["SCRIPT: No queued event of type", event_type]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail1 is not None and detail1 != cached_event.detail1:
            tokens = [
                "SCRIPT: Queued event's detail1 (",
                str(cached_event.detail1),
                ") doesn't match",
                str(detail1),
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail2 is not None and detail2 != cached_event.detail2:
            tokens = [
                "SCRIPT: Queued event's detail2 (",
                str(cached_event.detail2),
                ") doesn't match",
                str(detail2),
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if any_data is not None and any_data != cached_event.any_data:
            tokens = [
                "SCRIPT: Queued event's any_data (",
                cached_event.any_data,
                ") doesn't match",
                any_data,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = ["SCRIPT: Found matching queued event:", cached_event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cached_event

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None,
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        return True

    def is_activatable_event(self, event: Atspi.Event) -> bool:
        """Returns True if event should cause this script to become active."""

        return True

    def force_script_activation(self, event: Atspi.Event) -> bool:
        """Allows scripts to insist that they should become active."""

        return False

    def activate(self) -> None:
        """Called when this script is activated."""

    def deactivate(self) -> None:
        """Called when this script is deactivated."""
