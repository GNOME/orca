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

"""Module for managing presentation of information to the user via speech, braille, and sound."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import (
    braille_presenter,
    debug,
    focus_manager,
    live_region_presenter,
    script_manager,
    sound_presenter,
    speech_manager,
    speech_presenter,
    speechserver,
    typing_echo_presenter,
)
from .ax_utilities import AXUtilities
from .ax_value import AXValue

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .acss import ACSS
    from .input_event import KeyboardEvent
    from .scripts import default
    from .sound import Icon, Tone


class PresentationManager:
    """Manages presentation of information to the user via speech, braille, and sound."""

    def _get_active_script(self) -> default.Script | None:
        """Returns the active script."""

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

        key_name = event.get_key_name()
        if len(key_name) == 1:
            self.speak_character(key_name)
            return
        speech_presenter.get_presenter().present_key_event(event)

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def present_message(
        self,
        full: str,
        brief: str | None = None,
        voice: ACSS | None = None,
        reset_styles: bool = True,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Convenience method to speak a message and 'flash' it in braille."""

        if not full:
            return

        if brief is None:
            brief = full

        if speech_manager.get_manager().get_speech_is_enabled_and_not_muted():
            speech_pres = speech_presenter.get_presenter()
            message = full if speech_pres.get_messages_are_detailed() else brief
            if message:
                speech_pres.speak_message(message, voice=voice, reset_styles=reset_styles, obj=obj)

        braille_pres = braille_presenter.get_presenter()
        if not (braille_pres.use_braille() and braille_pres.get_flash_messages_are_enabled()):
            return

        message = full if braille_pres.get_flash_messages_are_detailed() else brief
        if not message:
            return

        if isinstance(message[0], list):
            message = message[0]
        if isinstance(message, list):
            message = [i for i in message if isinstance(i, str)]
            message = " ".join(message)

        braille_pres.present_message(message)

    @staticmethod
    def play_sound(sounds: list[Icon | Tone] | Icon | Tone, interrupt: bool = True) -> None:
        """Plays the specified sound(s)."""

        sound_presenter.get_presenter().play(sounds, interrupt)

    @staticmethod
    def present_braille_message(message: str, restore_previous: bool = True) -> None:
        """Displays a single line in braille."""

        braille_presenter.get_presenter().present_message(
            message,
            restore_previous=restore_previous,
        )

    def spell_item(self, text: str) -> None:
        """Speak the characters in the string one by one."""

        speech_presenter.get_presenter().spell_item(text)

    def spell_phonetically(self, item_string: str) -> None:
        """Phonetically spell item_string."""

        speech_presenter.get_presenter().spell_phonetically(item_string)

    @staticmethod
    def _get_cap_style(character: str) -> speechserver.CapitalizationStyle | None:
        """Returns the capitalization style if character is uppercase alpha."""

        if character.isupper() and character.strip().isalpha():
            style_str = speech_manager.get_manager().get_capitalization_style()
            return speechserver.CapitalizationStyle(style_str)
        return None

    def speak_character(self, character: str) -> None:
        """Speaks a single character."""

        speech_presenter.get_presenter().speak_character(
            character,
            voice_from=character,
            cap_style=self._get_cap_style(character),
        )

    def speak_character_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        character: str,
    ) -> None:
        """Speaks a character at the given offset, handling capitalization style."""

        cap_style = self._get_cap_style(character)
        speech_presenter.get_presenter().speak_character_at_offset(
            obj,
            offset,
            character,
            cap_style=cap_style,
        )

    def speak_accessible_text(self, obj: Atspi.Accessible | None, text: str) -> None:
        """Speaks text from an accessible object."""

        if speech_manager.get_manager().get_speech_is_muted():
            return
        speech_presenter.get_presenter().speak_accessible_text(obj, text)

    def speak_message(
        self,
        text: str,
        voice: ACSS | list[ACSS] | None = None,
        reset_styles: bool = True,
        obj: Atspi.Accessible | None = None,
    ) -> None:
        """Speaks a single string."""

        if speech_manager.get_manager().get_speech_is_muted():
            return
        speech_presenter.get_presenter().speak_message(
            text,
            voice=voice,
            reset_styles=reset_styles,
            obj=obj,
        )

    # pylint: disable-next=too-many-arguments
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

        if args.get("isProgressBarUpdate"):
            percent = AXValue.get_value_as_percent(obj)
            is_same_app = (
                AXUtilities.get_application(obj)
                == script_manager.get_manager().get_active_script_app()
            )
            is_same_window = (
                script.utilities.top_level_object(obj)
                == focus_manager.get_manager().get_active_window()
            )
            if generate_speech:
                generate_speech = (
                    speech_presenter.get_presenter().should_present_progress_bar_update(
                        obj,
                        percent,
                        is_same_app,
                        is_same_window,
                    )
                )
            if generate_braille:
                generate_braille = (
                    braille_presenter.get_presenter().should_present_progress_bar_update(
                        obj,
                        percent,
                        is_same_app,
                        is_same_window,
                    )
                )
            if generate_sound:
                generate_sound = sound_presenter.get_presenter().should_present_progress_bar_update(
                    obj,
                    percent,
                    is_same_app,
                    is_same_window,
                )

        if generate_speech:
            speech_presenter.get_presenter().present_generated_speech(script, obj, **args)

        if generate_braille:
            braille_presenter.get_presenter().present_generated_braille(script, obj, **args)

        if generate_sound:
            sounds = script.get_sound_generator().generate_sound(obj, **args)
            sound_presenter.get_presenter().play(sounds)

    def speak_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args: Any,
    ) -> None:
        """Speaks the specified contents."""

        speech_presenter.get_presenter().speak_contents(contents, **args)

    def display_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args: Any,
    ) -> None:
        """Displays contents in braille."""

        tokens = ["PRESENTATION MANAGER: Displaying", contents, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not (active_script := self._get_active_script()):
            return

        braille_presenter.get_presenter().display_generated_contents(
            active_script,
            contents,
            **args,
        )

    def present_window_title(self, script: default.Script, obj: Atspi.Accessible) -> None:
        """Generates and presents the window title."""

        for string in speech_presenter.get_presenter().generate_window_title_strings(script, obj):
            self.present_message(string)


_manager: PresentationManager = PresentationManager()


def get_manager() -> PresentationManager:
    """Returns the Presentation Manager singleton."""
    return _manager
