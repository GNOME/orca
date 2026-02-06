# Orca
#
# Copyright 2026 Igalia, S.L.
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

# pylint: disable=wrong-import-position

"""Module for managing presentation of information to the user via speech, braille, and sound."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from . import braille_presenter
from . import debug
from . import live_region_presenter
from . import phonnames
from . import settings
from . import sound_presenter
from . import speech
from . import speech_and_verbosity_manager
from . import typing_echo_presenter

from .acss import ACSS

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .input_event import KeyboardEvent
    from .scripts import default
    from .sound import Icon, Tone


class PresentationManager:
    """Manages presentation of information to the user via speech, braille, and sound."""

    def _get_active_script(self) -> default.Script | None:
        """Returns the active script."""

        from . import script_manager  # pylint: disable=import-outside-toplevel

        return script_manager.get_manager().get_active_script()

    def _get_voice(self, string: str = "") -> list[ACSS]:
        """Returns the voice to use for the given string."""

        if active_script := self._get_active_script():
            return active_script.speech_generator.voice(string=string)
        return []

    def interrupt_presentation(self, kill_flash: bool = True) -> None:
        """Convenience method to interrupt whatever is being presented at the moment."""

        msg = "PRESENTATION MANAGER: Interrupting presentation"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech_and_verbosity_manager.get_manager().interrupt_speech()
        if kill_flash:
            braille_presenter.get_presenter().kill_flash()
        live_region_presenter.get_presenter().flush_messages()

    def refresh_presenters(self) -> None:
        """Refreshes braille and speech settings after profile/settings change."""

        # Braille settings apply dynamically; just ensure enabled/disabled state is correct.
        braille_presenter.get_presenter().check_braille_setting()
        # Speech needs full restart because synthesizer/server might have changed.
        speech_and_verbosity_manager.get_manager().refresh_speech()

    def shutdown_presenters(self) -> None:
        """Shuts down braille, speech, and sound."""

        msg = "PRESENTATION MANAGER: Shutting down presenters"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        sound_presenter.get_presenter().shutdown_sound()
        speech_and_verbosity_manager.get_manager().shutdown_speech()
        braille_presenter.get_presenter().shutdown_braille()

    def start_presenters(self) -> None:
        """Starts braille, speech, and sound if each is enabled."""

        msg = "PRESENTATION MANAGER: Starting presenters"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech_and_verbosity_manager.get_manager().start_speech()
        braille_presenter.get_presenter().init_braille()
        sound_presenter.get_presenter().init_sound()

    def present_keyboard_event(self, script: default.Script, event: KeyboardEvent) -> None:
        """Presents the KeyboardEvent event."""

        typing_echo_presenter.get_presenter().echo_keyboard_event(script, event)

    def present_key_event(self, event: KeyboardEvent) -> None:
        """Presents a key event via speech (and potentially braille/sound in the future)."""

        key_name = event.get_key_name() if event.is_printable_key() else None
        voice = self._get_voice(string=key_name or "")
        speech.speak_key_event(event, voice[0] if voice else None)

    def present_message(
        self,
        full: str,
        brief: str | None = None,
        voice: ACSS | None = None,
        reset_styles: bool = True,
        force: bool = False,
    ) -> None:
        """Convenience method to speak a message and 'flash' it in braille."""

        if not full:
            return

        if brief is None:
            brief = full

        speech_manager = speech_and_verbosity_manager.get_manager()
        if speech_manager.get_speech_is_enabled_and_not_muted():
            if not speech_manager.get_messages_are_detailed():
                message = brief
            else:
                message = full
            if message:
                self.speak_message(message, voice=voice, reset_styles=reset_styles, force=force)

        presenter = braille_presenter.get_presenter()
        if not (presenter.use_braille() and presenter.get_flash_messages_are_enabled()):
            return

        message = full if presenter.get_flash_messages_are_detailed() else brief
        if not message:
            return

        if isinstance(message[0], list):
            message = message[0]
        if isinstance(message, list):
            message = [i for i in message if isinstance(i, str)]
            message = " ".join(message)

        presenter.display_message(message)

    @staticmethod
    def play_sound(sounds: list[Icon | Tone] | Icon | Tone, interrupt: bool = True) -> None:
        """Plays the specified sound(s)."""

        sound_presenter.get_presenter().play(sounds, interrupt)

    @staticmethod
    def display_message(message: str, restore_previous: bool = True) -> None:
        """Displays a single line in braille."""

        braille_presenter.get_presenter().display_message(
            message, restore_previous=restore_previous
        )

    def spell_item(self, text: str) -> None:
        """Speak the characters in the string one by one."""

        for character in text:
            self.speak_character(character)

    def spell_phonetically(self, item_string: str) -> None:
        """Phonetically spell item_string."""

        for character in item_string:
            voice = self._get_voice(string=character)
            phonetic_string = phonnames.get_phonetic_name(character.lower())
            self.speak_message(phonetic_string, voice)

    def speak_character(self, character: str) -> None:
        """Speaks a single character."""

        voice = self._get_voice(string=character)
        speech.speak_character(character, voice[0] if voice else None)

    def speak_message(
        self,
        text: str,
        voice: ACSS | list[ACSS] | None = None,
        interrupt: bool = True,
        reset_styles: bool = True,
        force: bool = False,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Method to speak a single string."""

        try:
            assert isinstance(text, str)
        except AssertionError:
            tokens = ["PRESENTATION MANAGER: speak_message called with non-string:", text]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)
            debug.print_exception(debug.LEVEL_WARNING)
            return

        speech_manager = speech_and_verbosity_manager.get_manager()
        if speech_manager.get_speech_is_muted() or (
            speech_manager.get_only_speak_displayed_text() and not force
        ):
            return

        voices = settings.voices
        system_voice = voices.get(settings.SYSTEM_VOICE)
        if voice is None:
            voice = self._get_voice(string=text)
        voice = voice or system_voice
        if voice == system_voice and reset_styles:
            cap_style = speech_manager.get_capitalization_style()
            speech_manager.set_capitalization_style("none")

            punct_style = speech_manager.get_punctuation_level()
            speech_manager.set_punctuation_level("some")

        text = speech_manager.adjust_for_presentation(obj, text)
        voice_to_use: ACSS | dict[str, Any] | None = None
        if isinstance(voice, list) and voice:
            voice_to_use = voice[0]
        elif not isinstance(voice, list):
            voice_to_use = voice
        speech.speak(text, voice_to_use, interrupt)

        if voice == system_voice and reset_styles:
            speech_manager.set_capitalization_style(cap_style)
            speech_manager.set_punctuation_level(punct_style)

    def speak_contents(
        self, contents: list[tuple[Atspi.Accessible, int, int, str]], **args: Any
    ) -> None:
        """Speaks the specified contents."""

        tokens = ["PRESENTATION MANAGER: Speaking", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not (active_script := self._get_active_script()):
            return

        utterances = active_script.speech_generator.generate_contents(contents, **args)
        speech.speak(utterances)

    def display_contents(
        self, contents: list[tuple[Atspi.Accessible, int, int, str]], **args: Any
    ) -> None:
        """Displays contents in braille."""

        tokens = ["PRESENTATION MANAGER: Displaying", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        presenter = braille_presenter.get_presenter()
        if not presenter.use_braille():
            return

        if not (active_script := self._get_active_script()):
            return

        regions_list, focused_region = active_script.braille_generator.generate_contents(
            contents, **args
        )
        if not regions_list:
            msg = "PRESENTATION MANAGER: Generating braille contents failed"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        tokens = [
            "PRESENTATION MANAGER: Generated result",
            regions_list,
            "focused region",
            focused_region or "None",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        flattened_regions: list = []
        for regions in regions_list:
            flattened_regions.extend(regions)

        if flattened_regions:
            flattened_regions[-1].string = flattened_regions[-1].string.rstrip(" ")

        presenter.present_regions(flattened_regions, focused_region, indicate_links=False)


_manager: PresentationManager = PresentationManager()


def get_manager() -> PresentationManager:
    """Returns the Presentation Manager singleton."""
    return _manager
