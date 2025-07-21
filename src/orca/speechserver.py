# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
# pylint: disable=unused-argument

"""Functionality for working with speech servers."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import Any, Callable, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    from . import input_event
    from .acss import ACSS

class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME   = "name"
    GENDER = "gender"
    LANG   = "lang"
    DIALECT = "dialect"
    VARIANT = "variant"

    MALE   = "male"
    FEMALE = "female"

    settings = {
        NAME   : None,
        GENDER : None,
        LANG   : None,
        DIALECT: None,
        VARIANT: None,
    }

    def __init__(self, props: dict[str, Any] | None) -> None:
        """Create and initialize VoiceFamily."""
        dict.__init__(self)

        self.update(VoiceFamily.settings)
        if props:
            self.update(props)

class SayAllContext:
    """Contains information about the current state of a Say All operation."""

    PROGRESS    = 0
    INTERRUPTED = 1
    COMPLETED   = 2

    def __init__(
        self,
        obj: Atspi.Accessible,
        utterance: str,
        start_offset: int = -1,
        end_offset: int = -1
    ) -> None:
        self.obj = obj
        self.utterance = utterance
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.current_offset = start_offset
        self.current_end_offset = None

    def __str__(self) -> str:
        return (
            f"SAY ALL: {self.obj} '{self.utterance}' ({self.start_offset}-{self.end_offset}, "
            f"current: {self.current_offset})"
        )

    def copy(self) -> SayAllContext:
        """Returns a copy of this SayAllContext."""

        new = SayAllContext(self.obj, self.utterance, self.start_offset, self.end_offset)
        new.current_offset = self.current_offset
        new.current_end_offset = self.current_end_offset
        return new

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SayAllContext):
            return False
        return (self.start_offset == other.start_offset and
                self.end_offset == other.end_offset and
                self.obj == other.obj and
                self.utterance == other.utterance)


class SpeechServer:
    """Provides speech server abstraction."""

    @staticmethod
    def get_factory_name() -> str:
        """Returns a localized name describing this factory."""

        return ""

    @staticmethod
    def get_speech_servers() -> list[Any]:
        """Returns a list of available speech servers."""

        return []

    @staticmethod
    def get_speech_server(_info: Any) -> SpeechServer | None:
        """Gets a given SpeechServer based upon the [name, id] info."""

        return None

    @staticmethod
    def shutdown_active_servers() -> None:
        """Cleans up and shuts down this factory."""

    def get_info(self) -> list[str]:
        """Returns [name, id] of the current speech server."""

        return ["", ""]

    def get_voice_families(self) -> list[VoiceFamily]:
        """Returns a list of all known VoiceFamily instances provided by the server."""

        return []

    def get_voice_family(self) -> VoiceFamily:
        """Returns the current voice family as a VoiceFamily dictionary."""

        return VoiceFamily({})

    def set_voice_family(self, family: VoiceFamily) -> None:
        """Sets the voice family to family VoiceFamily dictionary."""

    def speak_character(self, character: str, acss: ACSS | None = None) -> None:
        """Speaks character."""

    def speak_key_event(self, event: input_event.KeyboardEvent, acss: ACSS | None = None) -> None:
        """Speaks event."""

    def speak(
        self,
        text: str | None = None,
        acss: ACSS | None = None,
        interrupt: bool = True
    ) -> None:
        """Speaks text using the voice specified by acss."""

    def say_all(
        self,
        utterance_iterator: Iterator[tuple[SayAllContext, ACSS]],
        progress_callback: Callable[[SayAllContext, int], None]
    ) -> None:
        """Iterates through the given utterance_iterator, speaking each utterance."""

    def increase_speech_rate(self, step: int = 5) -> None:
        """Increases the speech rate."""

    def decrease_speech_rate(self, step: int = 5) -> None:
        """Decreases the speech rate."""

    def increase_speech_pitch(self, step: float = 0.5) -> None:
        """Increases the speech pitch."""

    def decrease_speech_pitch(self, step: float = 0.5) -> None:
        """Decreases the speech pitch."""

    def increase_speech_volume(self, step: float = 0.5) -> None:
        """Increases the speech volume."""

    def decrease_speech_volume(self, step: float = 0.5) -> None:
        """Decreases the speech volume."""

    def update_capitalization_style(self) -> None:
        """Updates the capitalization style used by the speech server."""

    def update_punctuation_level(self) -> None:
        """Punctuation level changed, inform this speechServer."""

    def stop(self) -> None:
        """Stops ongoing speech and flushes the queue."""

    def shutdown(self) -> None:
        """Shuts down the speech engine."""

    def reset(self) -> None:
        """Resets the speech engine."""

    def get_output_module(self) -> str:
        """Returns the output module associated with this speech server."""

        return ""

    def set_output_module(self, module_id: str) -> None:
        """Sets the output module associated with this speech server."""

    def list_output_modules(self) -> tuple[str, ...]:
        """Return names of available output modules as a tuple of strings."""

        return ()

    def get_voice_families_for_language(
        self,
        language: str,
        dialect: str,
        maximum: int | None = None
    ) -> list[tuple[str, str, str | None]]:
        """Returns the families for language available in the current synthesizer."""

        return []

    def should_change_voice_for_language(self, language: str, dialect: str = "") -> bool:
        """Returns True if we should change the voice for the specified language."""

        return False
