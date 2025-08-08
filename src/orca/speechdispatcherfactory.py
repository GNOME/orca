# Copyright 2006, 2007, 2008, 2009 Brailcom, o.p.s.
#
# Author: Tomas Cerha <cerha@brailcom.org>
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

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes

"""Provides an Orca speech server for Speech Dispatcher backend."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__author__    = "Tomas Cerha <cerha@brailcom.org>"
__copyright__ = "Copyright (c) 2006-2008 Brailcom, o.p.s."
__license__   = "LGPL"

import gc
import locale
import time
from typing import TYPE_CHECKING, Any, Callable, Iterator

from gi.repository import GLib

from . import debug
from . import focus_manager
from . import guilabels
from . import mathsymbols
from . import speechserver
from . import settings
from . import settings_manager
from .acss import ACSS
from .ax_utilities import AXUtilities
from .ssml import SSML, SSMLCapabilities

if TYPE_CHECKING:
    from . import input_event
    from .speechserver import VoiceFamily

try:
    import speechd
except Exception:
    _SPEECHD_AVAILABLE = False
else:
    _SPEECHD_AVAILABLE = True
    try:
        getattr(speechd, "CallbackType")
    except AttributeError:
        _SPEECHD_VERSION_OK = False
    else:
        _SPEECHD_VERSION_OK = True

class SpeechServer(speechserver.SpeechServer):
    """Speech Dispatcher speech server for Orca."""

    _active_servers: dict[str, SpeechServer] = {}

    DEFAULT_SERVER_ID = "default"
    _SERVER_NAMES = {DEFAULT_SERVER_ID: guilabels.DEFAULT_SYNTHESIZER}

    @staticmethod
    def get_factory_name() -> str:
        return guilabels.SPEECH_DISPATCHER

    @staticmethod
    def get_speech_servers() -> list[SpeechServer]:
        servers = []
        default = SpeechServer._get_speech_server(SpeechServer.DEFAULT_SERVER_ID)
        if default is not None:
            servers.append(default)
            for module in default.list_output_modules():
                server = SpeechServer._get_speech_server(module)
                if server is not None:
                    servers.append(server)
        return servers

    @classmethod
    def _get_speech_server(cls, server_id: str) -> SpeechServer | None:
        """Return an active server for given id.

        Attempt to create the server if it doesn't exist yet.  Returns None
        when it is not possible to create the server.
        """

        if server_id not in cls._active_servers:
            cls(server_id)
        # Don't return the instance, unless it is successfully added
        # to `_active_Servers'.
        return cls._active_servers.get(server_id)

    @staticmethod
    def get_speech_server(info: list[str] | None = None) -> SpeechServer | None:
        """Gets a given SpeechServer based upon the info."""

        this_id = info[1] if info is not None else SpeechServer.DEFAULT_SERVER_ID
        return SpeechServer._get_speech_server(this_id)

    @staticmethod
    def shutdown_active_servers() -> None:
        servers = list(SpeechServer._active_servers.values())
        for server in servers:
            server.shutdown()

    # *** Instance methods ***

    def __init__(self, server_id: str) -> None:
        super().__init__()
        self._id = server_id
        self._client: Any = None
        self._current_voice_properties: dict[str, Any] = {}
        self._current_synthesis_voice: str | None = None
        self._acss_manipulators = (
            (ACSS.RATE, self._set_rate),
            (ACSS.AVERAGE_PITCH, self._set_pitch),
            (ACSS.GAIN, self._set_volume),
            (ACSS.FAMILY, self._set_family),
            )
        if not _SPEECHD_AVAILABLE:
            msg = "ERROR: Speech Dispatcher is not available"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return
        if not _SPEECHD_VERSION_OK:
            msg = "ERROR: Speech Dispatcher version 0.6.2 or later is required."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return
        # The following constants must be initialized in runtime since they
        # depend on the speechd module being available.
        try:
            most = speechd.PunctuationMode.MOST
        except Exception:
            most = speechd.PunctuationMode.SOME
        self._punctuation_mode_map = {
            settings.PUNCTUATION_STYLE_ALL:  speechd.PunctuationMode.ALL,
            settings.PUNCTUATION_STYLE_MOST: most,
            settings.PUNCTUATION_STYLE_SOME: speechd.PunctuationMode.SOME,
            settings.PUNCTUATION_STYLE_NONE: speechd.PunctuationMode.NONE,
            }
        self._callback_type_map = {
            speechd.CallbackType.BEGIN: speechserver.SayAllContext.PROGRESS,
            speechd.CallbackType.CANCEL: speechserver.SayAllContext.INTERRUPTED,
            speechd.CallbackType.END: speechserver.SayAllContext.COMPLETED,
            speechd.CallbackType.INDEX_MARK:speechserver.SayAllContext.PROGRESS,
            }

        self._default_voice_name = guilabels.SPEECH_DEFAULT_VOICE % server_id

        try:
            self._init()
        except Exception:
            debug.print_exception(debug.LEVEL_WARNING)
            msg = "ERROR: Speech Dispatcher service failed to connect"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
        else:
            SpeechServer._active_servers[server_id] = self

    def _init(self) -> None:
        try:
            self._client = client = speechd.SSIPClient("Orca", component=self._id)
        except (speechd.SSIPCommunicationError, speechd.SpawnError) as error:
            msg = f"ERROR: Failed to connect to Speech Dispatcher: {error}"
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            self._client = None
            return
        client.set_priority(speechd.Priority.MESSAGE)

        # The speechServerInfo setting is not connected to the speechServerFactory. As a result,
        # the user's chosen server (synthesizer) might be from spiel.
        if self._id and self._id != self.DEFAULT_SERVER_ID:
            try:
                available_modules = client.list_output_modules()
                if self._id not in available_modules:
                    self._id = self.DEFAULT_SERVER_ID
                else:
                    client.set_output_module(self._id)
            except (AttributeError, speechd.SSIPCommandError):
                self._id = self.DEFAULT_SERVER_ID
        self._current_voice_properties = {}
        mode = self._punctuation_mode_map[settings.verbalizePunctuationStyle]
        client.set_punctuation(mode)
        client.set_data_mode(speechd.DataMode.SSML)

    def update_capitalization_style(self) -> None:
        """Updates the capitalization style used by the speech server."""

        if self._client is None:
            return

        if settings.capitalizationStyle == settings.CAPITALIZATION_STYLE_ICON:
            style = "icon"
        elif settings.capitalizationStyle == settings.CAPITALIZATION_STYLE_SPELL:
            style = "spell"
        else:
            style = "none"

        try:
            self._client.set_cap_let_recogn(style)
        except speechd.SSIPCommunicationError:
            msg = "SPEECH DISPATCHER: Connection lost. Trying to reconnect."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.reset()
            if self._client is not None:
                self._client.set_cap_let_recogn(style)
        except Exception:
            pass

    def update_punctuation_level(self) -> None:
        """ Punctuation level changed, inform this speechServer. """
        if self._client is None:
            return
        mode = self._punctuation_mode_map[settings.verbalizePunctuationStyle]
        self._client.set_punctuation(mode)

    def _send_command(self, command: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        try:
            return command(*args, **kwargs)
        except speechd.SSIPCommunicationError:
            msg = "SPEECH DISPATCHER: Connection lost. Trying to reconnect."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.reset()
            if self._client is None:
                return None
            try:
                return command(*args, **kwargs)
            except (AttributeError, speechd.SSIPCommandError) as error:
                msg = f"SPEECH DISPATCHER: Failed to reconnect: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                return None
        except Exception:
            return None

    def _set_rate(self, acss_rate: float) -> None:
        if self._client is None:
            return
        rate = int(2 * max(0, min(99, acss_rate)) - 98)
        self._send_command(self._client.set_rate, rate)

    def _set_pitch(self, acss_pitch: float) -> None:
        if self._client is None:
            return
        pitch = int(20 * max(0, min(9, acss_pitch)) - 90)
        self._send_command(self._client.set_pitch, pitch)

    def _set_volume(self, acss_volume: float) -> None:
        if self._client is None:
            return
        volume = int(15 * max(0, min(9, acss_volume)) - 35)
        self._send_command(self._client.set_volume, volume)

    def _get_language_and_dialect(self, acss_family: dict[str, Any] | None) -> tuple[str, str]:
        if acss_family is None:
            acss_family = {}

        language = acss_family.get(speechserver.VoiceFamily.LANG)
        dialect = acss_family.get(speechserver.VoiceFamily.DIALECT)

        if not language:
            family_locale, _encoding = locale.getlocale()

            language, dialect = "", ""
            if family_locale:
                locale_values = family_locale.split("_")
                language = locale_values[0]
                if len(locale_values) == 2:
                    dialect = locale_values[1]

        return str(language), str(dialect)

    def _set_family(self, acss_family: dict[str, Any] | None) -> None:
        if self._client is None:
            return
        lang, dialect = self._get_language_and_dialect(acss_family)
        if lang:
            self._send_command(self._client.set_language, lang)
            if dialect:
                # Try to set precise dialect
                self._send_command(self._client.set_language, lang + "-" + dialect)

        try:
            # This command is not available with older SD versions.
            set_synthesis_voice = self._client.set_synthesis_voice
        except AttributeError:
            pass
        else:
            if acss_family is not None:
                name = acss_family.get(speechserver.VoiceFamily.NAME)
                if name is not None and name != self._default_voice_name:
                    self._send_command(set_synthesis_voice, name)
                    self._current_synthesis_voice = name

    def _debug_sd_values(self, prefix: str = "") -> None:
        if debug.debugLevel > debug.LEVEL_INFO:
            return

        try:
            if self._client is not None:
                sd_rate = self._send_command(self._client.get_rate)
                sd_pitch = self._send_command(self._client.get_pitch)
                sd_volume = self._send_command(self._client.get_volume)
                sd_language = self._send_command(self._client.get_language)
            else:
                sd_rate = sd_pitch = sd_volume = sd_language = "(client not available)"
        except Exception:
            sd_rate = sd_pitch = sd_volume = sd_language = "(exception occurred)"

        family = self._current_voice_properties.get(ACSS.FAMILY) or {}

        styles = {settings.PUNCTUATION_STYLE_NONE: "NONE",
                  settings.PUNCTUATION_STYLE_SOME: "SOME",
                  settings.PUNCTUATION_STYLE_MOST: "MOST",
                  settings.PUNCTUATION_STYLE_ALL: "ALL"}

        punctuation_style = styles.get(
            settings_manager.get_manager().get_setting("verbalizePunctuationStyle"), "UNKNOWN")

        msg = (
            f"SPEECH DISPATCHER: {prefix}\n"
            f"ORCA rate {self._current_voice_properties.get(ACSS.RATE)}, "
            f"pitch {self._current_voice_properties.get(ACSS.AVERAGE_PITCH)}, "
            f"volume {self._current_voice_properties.get(ACSS.GAIN)}, "
            f"language {self._get_language_and_dialect(family)[0]}, "
            f"punctuation: {punctuation_style}\n"
            f"SD rate {sd_rate}, pitch {sd_pitch}, volume {sd_volume}, language {sd_language}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _apply_acss(self, acss: dict[str, Any] | None) -> None:
        if acss is None:
            acss = settings.voices[settings.DEFAULT_VOICE]
        current = self._current_voice_properties
        for acss_property, method in self._acss_manipulators:
            value = acss.get(acss_property)
            if value is not None:
                if current.get(acss_property) != value:
                    method(value)
                    current[acss_property] = value
            elif acss_property == ACSS.AVERAGE_PITCH:
                self._set_pitch(5.0)
                current[acss_property] = 5.0
            elif acss_property == ACSS.GAIN:
                self._set_volume(10.0)
                current[acss_property] = 10.0
            elif acss_property == ACSS.RATE:
                self._set_rate(50.0)
                current[acss_property] = 50.0
            elif acss_property == ACSS.FAMILY:
                self._set_family({})
                current[acss_property] = {}

    def _speak(self, text: str, acss: dict[str, Any] | None, **kwargs: Any) -> None:
        if isinstance(text, ACSS):
            text = ""

        ssml = SSML.markup_text(text, SSMLCapabilities.MARK)

        self._apply_acss(acss)
        self._debug_sd_values(f"Speaking '{ssml}' ")
        if self._client is not None:
            self._send_command(self._client.speak, ssml, **kwargs)

    def _say_all(
        self,
        iterator: Iterator[tuple[speechserver.SayAllContext, dict[str, Any]]],
        orca_callback: Callable[[speechserver.SayAllContext, int], None]
    ) -> bool:
        """Process another sayAll chunk.

        Called by the gidle thread.

        """
        try:
            context, acss = next(iterator)
        except StopIteration:
            pass
        else:
            def callback(callback_type, index_mark=None):
                # This callback is called in Speech Dispatcher listener thread.
                # No subsequent Speech Dispatcher interaction is allowed here,
                # so we pass the calls to the gidle thread.
                t = self._callback_type_map[callback_type]
                if t == speechserver.SayAllContext.PROGRESS:
                    if index_mark:
                        index = index_mark.split(":")
                        if len(index) >= 2:
                            start, end = index[0:2]
                            context.current_offset = context.start_offset + int(start)
                            context.current_end_offset = context.start_offset + int(end)
                            msg = (
                                f"SPEECH DISPATCHER: Got mark "
                                f"{context.current_offset}:{context.current_end_offset} / "
                                f"{context.start_offset}:{context.end_offset}"
                            )
                            debug.print_message(debug.LEVEL_INFO, msg, True)
                    else:
                        context.current_offset = context.start_offset
                        context.current_end_offset = None
                elif t == speechserver.SayAllContext.COMPLETED:
                    context.current_offset = context.end_offset
                    context.current_end_offset = None
                GLib.idle_add(orca_callback, context.copy(), t)
                if t == speechserver.SayAllContext.COMPLETED:
                    GLib.idle_add(self._say_all, iterator, orca_callback)
            self._speak(context.utterance, acss, callback=callback,
                        event_types=list(self._callback_type_map.keys()))
        return False # to indicate, that we don't want to be called again.

    def _cancel(self) -> None:
        if self._client is not None:
            self._send_command(self._client.cancel)

    def _change_default_speech_rate(self, step: int, decrease: bool = False) -> None:
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            rate = acss[ACSS.RATE]
        except KeyError:
            rate = 50
        acss[ACSS.RATE] = max(0, min(99, rate + delta))
        msg = f"SPEECH DISPATCHER: Rate set to {rate}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_pitch(self, step: float, decrease: bool = False) -> None:
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            pitch = acss[ACSS.AVERAGE_PITCH]
        except KeyError:
            pitch = 5
        acss[ACSS.AVERAGE_PITCH] = max(0, min(9, pitch + delta))
        msg = f"SPEECH DISPATCHER: Pitch set to {pitch}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_volume(self, step: float, decrease: bool = False) -> None:
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            volume = acss[ACSS.GAIN]
        except KeyError:
            volume = 10
        acss[ACSS.GAIN] = max(0, min(9, volume + delta))
        msg = f"SPEECH DISPATCHER: Volume set to {volume}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_info(self) -> list[str]:
        return [self._SERVER_NAMES.get(self._id, self._id), self._id]

    def get_voice_families(self) -> list[speechserver.VoiceFamily]:
        # Always offer the configured default voice with a language
        # set according to the current locale.
        current_locale = locale.getlocale(locale.LC_MESSAGES)[0]
        if current_locale is None or "_" not in current_locale:
            locale_language = None
        else:
            locale_lang, locale_dialect = current_locale.split("_")
            locale_language = locale_lang + "-" + locale_dialect
        voices: tuple[tuple[str, str, str | None], ...] = ()
        if self._client is not None:
            try:
                # This command is not available with older SD versions.
                list_synthesis_voices = self._client.list_synthesis_voices
            except AttributeError:
                pass
            else:
                try:
                    result = self._send_command(list_synthesis_voices)
                    if result:
                        voices = tuple(result)
                except Exception:
                    pass

        default_lang = ""
        if locale_language:
            # Check whether how it appears in the server list
            for name, lang, variant in voices:
                if lang == locale_language:
                    default_lang = locale_language
                    break
            if not default_lang:
                for name, lang, variant in voices:
                    if lang == locale_lang:
                        default_lang = locale_lang
            if not default_lang:
                default_lang = locale_language

        voices = ((self._default_voice_name, default_lang, None),) + voices

        families = []
        for name, lang, variant in voices:

            families.append(speechserver.VoiceFamily({ \
              speechserver.VoiceFamily.NAME: name,
              #speechserver.VoiceFamily.GENDER: speechserver.VoiceFamily.MALE,
              speechserver.VoiceFamily.LANG: lang.partition("-")[0],
              speechserver.VoiceFamily.DIALECT: lang.partition("-")[2],
              speechserver.VoiceFamily.VARIANT: variant}))

        return families

    def speak(
        self,
        text: str | None = None,
        acss: dict[str, Any] | None = None,
        interrupt: bool = True
    ) -> None:
        if not text:
            return

        # In order to re-enable this, a potentially non-trivial amount of work
        # will be needed to ensure multiple utterances sent to speech.speak
        # do not result in the intial utterances getting cut off before they
        # can be heard by the user. Anyone needing to interrupt speech can
        # do so by using the default script's method interrupt_presentation.
        #if interrupt:
        #    self._cancel()

        if len(text) == 1:
            msg = f"SPEECH DISPATCHER: Speaking '{text}' as char"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._apply_acss(acss)
            if self._client is not None:
                self._send_command(self._client.char, text)
        else:
            msg = f"SPEECH DISPATCHER: Speaking '{text}' as string"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._speak(text, acss)

    def say_all(
        self,
        utterance_iterator: Iterator[tuple[speechserver.SayAllContext, dict[str, Any]]],
        progress_callback: Callable[[speechserver.SayAllContext, int], None]
    ) -> None:
        """Iterates through the given utterance_iterator, speaking each utterance."""

        GLib.idle_add(self._say_all, utterance_iterator, progress_callback)

    def speak_character(self, character: str, acss: dict[str, Any] | None = None) -> None:
        """Speaks character."""

        self._apply_acss(acss)
        name = character
        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_math_related(focus):
            # TODO - JD: If we're reaching this point without the name having been adjusted, we're
            # doing it wrong.
            name = mathsymbols.get_character_name(character)

        if not name or name == character:
            msg = f"SPEECH DISPATCHER: Speaking '{character}' as char"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if self._client is not None:
                self._send_command(self._client.char, character)
            return

        self.speak(name, acss)

    def speak_key_event(
        self,
        event: input_event.KeyboardEvent,
        acss: dict[str, Any] | None = None
    ) -> None:
        """Speaks event."""

        event_string = event.get_key_name()
        locking_state_string = event.get_locking_state_string()
        event_string = f"{event_string} {locking_state_string}".strip()
        if len(event_string) == 1:
            msg = f"SPEECH DISPATCHER: Speaking '{event_string}' as key"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._apply_acss(acss)
            if self._client is not None:
                self._send_command(self._client.key, event_string)
        else:
            msg = f"SPEECH DISPATCHER: Speaking '{event_string}' as string"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.speak(event_string, acss=acss)

    def increase_speech_rate(self, step: int = 5) -> None:
        self._change_default_speech_rate(step)

    def decrease_speech_rate(self, step: int = 5) -> None:
        self._change_default_speech_rate(step, decrease=True)

    def increase_speech_pitch(self, step: float = 0.5) -> None:
        self._change_default_speech_pitch(step)

    def decrease_speech_pitch(self, step: float = 0.5) -> None:
        self._change_default_speech_pitch(step, decrease=True)

    def increase_speech_volume(self, step: float = 0.5) -> None:
        self._change_default_speech_volume(step)

    def decrease_speech_volume(self, step: float = 0.5) -> None:
        self._change_default_speech_volume(step, decrease=True)

    def get_language(self) -> str:
        """Returns the current language."""

        if self._client is None:
            return ""
        return self._client.get_language()

    def set_language(self, language: str, dialect: str) -> None:
        """Sets the current language"""

        if not language or self._client is None:
            return

        self._client.set_language(language)
        if dialect:
            self._client.set_language(language + "-" + dialect)

    def _normalized_language_and_dialect(self, language: str, dialect: str = "") -> tuple[str, str]:
        """Attempts to ensure consistency across inconsistent formats."""

        if "-" in language:
            normalized_language = language.split("-", 1)[0].lower()
            normalized_dialect = language.split("-", 1)[-1].lower()
        else:
            normalized_language = language.lower()
            normalized_dialect = dialect.lower()

        return normalized_language, normalized_dialect

    def get_voice_families_for_language(
        self,
        language: str,
        dialect: str,
        maximum: int | None = None
    ) -> list[tuple[str, str, str | None]]:
        """Returns the families for language available in the current synthesizer."""

        start = time.time()
        target_language, target_dialect = self._normalized_language_and_dialect(language, dialect)

        result = []
        if self._client is None:
            return result

        # Get all voices and filter manually
        # TODO - JD: The speech-dispatcher API accepts language parameters for filtering,
        # but this seems to fail for Voxin (returns all voices regardless of language).
        all_voices = self._client.list_synthesis_voices()
        for voice in all_voices:
            normalized_language, normalized_dialect = \
                self._normalized_language_and_dialect(voice[1])
            if normalized_language != target_language:
                continue
            if normalized_dialect == target_dialect:
                result.append(voice)
            elif not normalized_dialect and target_dialect == normalized_language:
                result.append(voice)
            if maximum is not None and len(result) >= maximum:
                break

        msg = (
            f"SPEECH DISPATCHER: Found {len(result)} match(es) for language='{language}' "
            f"dialect='{dialect}' in {time.time() - start:.4f}s."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def should_change_voice_for_language(
        self,
        language: str,
        dialect: str = ""
    ) -> bool:
        """Returns True if we should change the voice for the specified language."""

        current_language, current_dialect = \
            self._normalized_language_and_dialect(self.get_language())
        other_language, other_dialect = self._normalized_language_and_dialect(language, dialect)

        msg = (
            f"SPEECH DISPATCHER: Should change voice for language? "
            f"Current: '{current_language}' '{current_dialect}' "
            f"New: '{other_language}' '{other_dialect}'"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if current_language == other_language and current_dialect == other_dialect:
            msg ="SPEECH DISPATCHER: No. Language and dialect are the same."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        families = self.get_voice_families_for_language(other_language, other_dialect, maximum=1)
        if families:
            tokens = ["SPEECH DISPATCHER: Yes. Found matching family", families[0], "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["SPEECH DISPATCHER: No. No matching family in", self.get_output_module(), "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    def get_output_module(self) -> str:
        if self._client is None:
            return ""
        result = self._send_command(self._client.get_output_module)
        if result is not None:
            return result
        return ""

    def set_output_module(self, module_id: str) -> None:
        """Set the speech output module to the specified provider."""

        # TODO - JD: This updates the output module, but not the the value of self._id.
        # That might be desired (e.g. self._id impacts what is shown in Orca preferences),
        # but it can be confusing.
        if self._client is not None:
            self._send_command(self._client.set_output_module, module_id)

    def stop(self) -> None:
        self._cancel()

    def shutdown(self) -> None:
        try:
            # Don't call _cancel() here because it can cut off messages we want to complete, such
            # as "screen reader off."
            if self._client is not None:
                self._client.close()
                # Set client to None to allow immediate garbage collection.
                self._client = None
                # Force garbage collection to clean up Speech Dispatcher objects immediately
                # This prevents hanging during Python's final garbage collection.
                gc.collect()
        except Exception as error:
            msg = f"SPEECH DISPATCHER: Error during shutdown of server {self._id}: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
        finally:
            if self._id in SpeechServer._active_servers:
                del SpeechServer._active_servers[self._id]

    def reset(self) -> None:
        try:
            msg = f"SPEECH DISPATCHER: Resetting server {self._id}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if self._client is not None:
                self._client.close()
        except Exception as error:
            msg = f"SPEECH DISPATCHER: Error during reset of server {self._id}: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
        finally:
            self._init()

    def list_output_modules(self) -> tuple[str, ...]:
        """Return names of available output modules as a tuple of strings."""

        if self._client is None:
            return ()
        try:
            return self._send_command(self._client.list_output_modules)
        except AttributeError:
            return ()
        except speechd.SSIPCommandError:
            return ()

    def get_voice_family(self) -> VoiceFamily:
        """Returns the current voice family as a VoiceFamily dictionary."""

        voice_name = self._current_synthesis_voice or self._default_voice_name
        language = ""
        try:
            language = self._send_command(self._client.get_language)
        except (AttributeError, speechd.SSIPCommandError) as error:
            msg = f"SPEECH DISPATCHER: Error getting language: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)

        lang_parts = language.partition("-")
        lang = lang_parts[0]
        dialect = lang_parts[2]
        return speechserver.VoiceFamily(
            {
               speechserver.VoiceFamily.NAME: voice_name,
               speechserver.VoiceFamily.LANG: lang,
               speechserver.VoiceFamily.DIALECT: dialect,
               speechserver.VoiceFamily.VARIANT: None
            }
        )

    def set_voice_family(self, family: VoiceFamily) -> None:
        """Sets the voice family to family VoiceFamily dictionary."""

        if not family:
            return

        voice_name = family.get(speechserver.VoiceFamily.NAME, "")
        language = family.get(speechserver.VoiceFamily.LANG, "")
        dialect = family.get(speechserver.VoiceFamily.DIALECT, "")
        if dialect:
            language = f"{language}-{dialect}" if language else dialect

        # Try to set synthesis voice (individual voice like Nathan, Federica)
        if voice_name:
            try:
                self._send_command(self._client.set_synthesis_voice, voice_name)
                self._current_synthesis_voice = voice_name
            except AttributeError as error:
                msg = f"SPEECH DISPATCHER: Synthesis voice not supported: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self._current_synthesis_voice = None
            except speechd.SSIPCommandError as error:
                msg = f"SPEECH DISPATCHER: Error setting synthesis voice {voice_name}: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)

        if language:
            try:
                self._send_command(self._client.set_language, language)
            except speechd.SSIPCommandError as error:
                msg = f"SPEECH DISPATCHER: Error setting language {language}: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
