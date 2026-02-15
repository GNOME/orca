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
from . import sound_presenter
from . import speech_manager
from . import speech_presenter
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

    def interrupt_presentation(self, kill_flash: bool = True) -> None:
        """Convenience method to interrupt whatever is being presented at the moment."""

        msg = "PRESENTATION MANAGER: Interrupting presentation"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech_manager.get_manager().interrupt_speech()
        if kill_flash:
            braille_presenter.get_presenter().kill_flash()
        live_region_presenter.get_presenter().flush_messages()

    def refresh_presenters(self) -> None:
        """Refreshes braille and speech settings after profile/settings change."""

        # Braille settings apply dynamically; just ensure enabled/disabled state is correct.
        braille_presenter.get_presenter().check_braille_setting()
        # Speech needs full restart because synthesizer/server might have changed.
        speech_manager.get_manager().refresh_speech()

    def shutdown_presenters(self) -> None:
        """Shuts down braille, speech, and sound."""

        msg = "PRESENTATION MANAGER: Shutting down presenters"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        sound_presenter.get_presenter().shutdown_sound()
        speech_presenter.get_presenter().destroy_monitor()
        speech_manager.get_manager().shutdown_speech()
        braille_presenter.get_presenter().shutdown_braille()

    def start_presenters(self) -> None:
        """Starts braille, speech, and sound if each is enabled."""

        msg = "PRESENTATION MANAGER: Starting presenters"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech_manager.get_manager().start_speech()
        braille_presenter.get_presenter().init_braille()
        sound_presenter.get_presenter().init_sound()
        speech_presenter.get_presenter().init_monitor()

    def present_keyboard_event(self, script: default.Script, event: KeyboardEvent) -> None:
        """Presents the KeyboardEvent event."""

        typing_echo_presenter.get_presenter().echo_keyboard_event(script, event)

    def present_key_event(self, event: KeyboardEvent) -> None:
        """Presents a key event via speech (and potentially braille/sound in the future)."""

        speech_presenter.get_presenter().present_key_event(event)

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

        speech_presenter.get_presenter().present_message(
            full, brief, voice=voice, reset_styles=reset_styles, force=force
        )

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

        presenter.present_message(message)

    @staticmethod
    def play_sound(sounds: list[Icon | Tone] | Icon | Tone, interrupt: bool = True) -> None:
        """Plays the specified sound(s)."""

        sound_presenter.get_presenter().play(sounds, interrupt)

    @staticmethod
    def present_braille_message(message: str, restore_previous: bool = True) -> None:
        """Displays a single line in braille."""

        braille_presenter.get_presenter().present_message(
            message, restore_previous=restore_previous
        )

    def spell_item(self, text: str) -> None:
        """Speak the characters in the string one by one."""

        speech_presenter.get_presenter().spell_item(text)

    def spell_phonetically(self, item_string: str) -> None:
        """Phonetically spell item_string."""

        speech_presenter.get_presenter().spell_phonetically(item_string)

    def speak_character(self, character: str) -> None:
        """Speaks a single character."""

        speech_presenter.get_presenter().speak_character(character)

    def speak_message(
        self,
        text: str,
        voice: ACSS | list[ACSS] | None = None,
        interrupt: bool = True,
        reset_styles: bool = True,
        force: bool = False,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Speaks a single string."""

        speech_presenter.get_presenter().speak_message(
            text, voice=voice, interrupt=interrupt, reset_styles=reset_styles, force=force, obj=obj
        )

    def present_object(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        *,
        generate_speech: bool = True,
        generate_braille: bool = True,
        generate_sound: bool = False,
        **args: Any,
    ) -> None:
        """Generates and presents an object via speech, braille, and sound."""

        if obj is None:
            return

        if generate_speech:
            speech_presenter.get_presenter().present_generated_speech(script, obj, **args)

        if generate_braille:
            braille_presenter.get_presenter().present_generated_braille(script, obj, **args)

        if generate_sound:
            sounds = script.sound_generator.generate_sound(obj, **args)
            sound_presenter.get_presenter().play(sounds)

    def speak_contents(
        self, contents: list[tuple[Atspi.Accessible, int, int, str]], **args: Any
    ) -> None:
        """Speaks the specified contents."""

        speech_presenter.get_presenter().speak_contents(contents, **args)

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
