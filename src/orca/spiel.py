# Copyright 2006, 2007, 2008, 2009 Brailcom, o.p.s.
# Copyright © 2024 GNOME Foundation Inc.
#
# Author: Andy Holmes <andyholmes@gnome.org>
# Contributor: Tomas Cerha <cerha@brailcom.org>
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

"""Provides an Orca speech server for Spiel backend."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__author__    = "<andyholmes@gnome.org>"
__copyright__ = "Copyright © 2024 GNOME Foundation Inc. "
__license__   = "LGPL"

import gi

from . import debug
from . import guilabels
from . import speechserver
from . import settings
from . import settings_manager
from .acss import ACSS
from .ssml import SSML, SSMLCapabilities

gi.require_version("GLib", "2.0")
from gi.repository import GLib

try:
    gi.require_version('Spiel', '1.0')
    from gi.repository import Spiel
    _spiel_available = True
except Exception:
    _spiel_available = False

class SpeechServer(speechserver.SpeechServer):
    # See the parent class for documentation.

    _active_providers = {}
    _active_servers = {}

    DEFAULT_SPEAKER = None
    DEFAULT_SERVER_ID = 'default'
    _SERVER_NAMES = {DEFAULT_SERVER_ID: guilabels.DEFAULT_SYNTHESIZER}

    @staticmethod
    def getFactoryName():
        return guilabels.SPIEL

    @staticmethod
    def getSpeechServers():
        servers = []
        default = SpeechServer._get_speech_server(SpeechServer.DEFAULT_SERVER_ID)
        if default is not None:
            servers.append(default)
            for provider in SpeechServer.DEFAULT_SPEAKER.props.providers:
                servers.append(SpeechServer._get_speech_server(provider.props.well_known_name))
        return servers

    @classmethod
    def _updateProviders(cls, providers):
        """Shutdown unavailable providers."""

        cls._SERVER_NAMES = {SpeechServer.DEFAULT_SERVER_ID: guilabels.DEFAULT_SYNTHESIZER}
        for provider in providers:
            cls._SERVER_NAMES[provider.props.well_known_name] = provider.props.name

        # Shutdown unavailable providers
        for well_known_name, server in cls._active_servers.items():
            if well_known_name not in cls._SERVER_NAMES:
                server.shutdown()

        cls._active_providers = {p.props.well_known_name: p for p in providers}

        # Update the default server's voices
        if len(providers) > 0 and cls.DEFAULT_SERVER_ID in cls._active_servers:
            server = cls._active_servers[cls.DEFAULT_SERVER_ID]
            server._updateVoices(providers[0].props.voices)

    def _updateVoices(self, voices):
        """Update the list of known voices for the server.

        getVoiceFamilies() prepends the list with the locale default and
        the default family.
        """
        msg = f"SPIEL: Updating voices for provider {self._id}, got {len(voices)} voices"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        voice_profiles = ()
        for voice in voices:
            for language in voice.props.languages:
                voice_profiles += ((voice.props.name, language, None),)

        self._current_voice_profiles = voice_profiles
        msg = f"SPIEL: Updated voice profiles: {len(voice_profiles)} profiles"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @classmethod
    def _get_speech_server(cls, serverId):
        """Return an active server for given id.

        Attempt to create the server if it doesn't exist yet.  Returns None
        when it is not possible to create the server.

        """
        if serverId not in cls._active_servers:
            cls(serverId)
        # Don't return the instance, unless it is successfully added
        # to `_active_servers'.
        return cls._active_servers.get(serverId)

    @staticmethod
    def get_speech_server(info):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.get_info() for more info.
        """
        thisId = info[1] if info is not None else SpeechServer.DEFAULT_SERVER_ID
        return SpeechServer._get_speech_server(thisId)

    @staticmethod
    def shutdownActiveServers():
        servers = [s for s in SpeechServer._active_servers.values()]
        for server in servers:
            server.shutdown()

    # *** Instance methods ***

    def __init__(self, serverId):
        super().__init__()
        self._id = serverId
        self._provider = None
        self._speaker = None
        self._voices_id = None
        self._default_voice_name = None
        self._current_voice_profiles = ()
        self._current_voice_properties = {}
        self._current_voice = None
        self._acss_defaults = (
            (ACSS.RATE, 50),
            (ACSS.AVERAGE_PITCH, 5.0),
            (ACSS.GAIN, 5.0),
            (ACSS.FAMILY, {}),
            )
        if not _spiel_available:
            msg = 'ERROR: Spiel is not available'
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return

        try:
            self._init()
        except Exception as error:
            debug.print_exception(debug.LEVEL_WARNING)
            msg = f"ERROR: Spiel service failed to connect {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
        else:
            SpeechServer._active_servers[serverId] = self

    def _get_rate(self, acss_rate):
        # The default 50 (0-100) to Spiel's 1.0 (0.1-10.0)
        if acss_rate == 100:
            return 10.0
        rate = (acss_rate / 100.0) * 2
        if acss_rate > 50:
            rate += (rate % 1) * 9
        return max(0.1, min(rate, 10.0))

    def _get_pitch(self, acss_pitch):
        # The default 5.0 (0-10.0) is mapped to Spiel's 1.0 (0-2.0)
        pitch = acss_pitch / 5.0
        return max(0.0, min(pitch, 2.0))

    def _get_volume(self, acss_volume):
        # The default 5.0 (0-10.0) to Spiel's 1.0 (0-2.0)
        volume = acss_volume / 10.0
        return max(0.0, min(volume, 2.0))

    def _get_language_and_dialect(self, acss_family):
        if acss_family is None:
            acss_family = {}

        language = acss_family.get(speechserver.VoiceFamily.LANG)
        dialect = acss_family.get(speechserver.VoiceFamily.DIALECT)

        if not language:
            import locale
            familyLocale, encoding = locale.getdefaultlocale()

            language, dialect = '', ''
            if familyLocale:
                localeValues = familyLocale.split('_')
                language = localeValues[0]
                if len(localeValues) == 2:
                    dialect = localeValues[1]

        return language, dialect

    def _get_language(self, acss_family):
        lang, dialect = self._get_language_and_dialect(acss_family)
        return lang + '-' + dialect

    def _get_voice(self, acss_family):
        """Return a Spiel voice for an ACSS family.

        If an exact match is not found the fallback will prioritize
        lang-dialect, then lang, and failing that anything available. This
        method may return None, in the rare case no voices are available.
        """
        # Use voices from the current provider, not all voices from the speaker
        if self._provider is None or len(self._provider.props.voices) == 0:
            msg = f"SPIEL: No voices available for provider {self._id}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        # Extract voice information from ACSS family
        acss_name = acss_family.get(speechserver.VoiceFamily.NAME) if acss_family else None
        acss_lang, acss_dialect = self._get_language_and_dialect(acss_family)
        accs_lang_dialect = f"{acss_lang}-{acss_dialect}"

        # If we have a tracked voice, prioritize it over ACSS family. This allows D-Bus voice
        # changes to take precedence.
        if self._current_voice:
            return self._current_voice

        # If no specific voice family is requested, use first available voice.
        voices = self._provider.props.voices
        if not acss_name:
            return voices[0] if voices else None

        fallback = voices[0]
        fallback_lang = None
        for voice in voices:
            # Prioritize the voice language, dialect and then family
            for language in voice.props.languages:
                [lang, _, dialect] = language.partition("-")
                if lang == acss_lang:
                    if fallback_lang not in [accs_lang_dialect, acss_lang]:
                        fallback = voice
                        fallback_lang = language

                    if dialect == acss_dialect:
                        break
            else:
                # next voice
                continue

            # Language and dialect are ensured, so a match here is perfect
            if acss_name in [self._default_voice_name, voice.props.name]:
                return voice

        return fallback

    def _debug_spiel_values(self, prefix=""):
        if debug.debugLevel > debug.LEVEL_INFO:
            return

        try:
            rate = self._get_rate(self._current_voice_properties.get(ACSS.RATE))
            pitch = self._get_pitch(self._current_voice_properties.get(ACSS.AVERAGE_PITCH))
            volume = self._get_volume(self._current_voice_properties.get(ACSS.GAIN))
            language = self._get_language(self._current_voice_properties.get(ACSS.FAMILY))
        except Exception:
            rate = pitch = volume = language = "(exception occurred)"

        family = self._current_voice_properties.get(ACSS.FAMILY)

        styles = {settings.PUNCTUATION_STYLE_NONE: "NONE",
                  settings.PUNCTUATION_STYLE_SOME: "SOME",
                  settings.PUNCTUATION_STYLE_MOST: "MOST",
                  settings.PUNCTUATION_STYLE_ALL: "ALL"}
        manager = settings_manager.get_manager()

        msg = (
            f"SPIEL: {prefix}\n"
            f"ORCA rate {self._current_voice_properties.get(ACSS.RATE)}, "
            f"pitch {self._current_voice_properties.get(ACSS.AVERAGE_PITCH)}, "
            f"volume {self._current_voice_properties.get(ACSS.GAIN)}, "
            f"language {self._get_language_and_dialect(family)[0]}, "
            f"punctuation: "
            f"{styles.get(manager.get_setting('verbalizePunctuationStyle'))}\n"
            f"SD rate {rate}, pitch {pitch}, volume {volume}, language {language}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _apply_acss(self, acss):
        if acss is None:
            acss = settings.voices[settings.DEFAULT_VOICE]
        current = self._current_voice_properties
        for acss_property, default in self._acss_defaults:
            value = acss.get(acss_property)
            if value is not None:
                current[acss_property] = value
            else:
                current[acss_property] = default

    def _init(self):
        # Maintain a speaker singleton for all providers
        if SpeechServer.DEFAULT_SPEAKER is None:
            SpeechServer.DEFAULT_SPEAKER = Spiel.Speaker.new_sync(None)
            SpeechServer.DEFAULT_SPEAKER.props.providers.connect('items-changed',
                                                                 SpeechServer._updateProviders)
            SpeechServer._updateProviders(SpeechServer.DEFAULT_SPEAKER.props.providers)

        self._speaker = SpeechServer.DEFAULT_SPEAKER
        self._current_voice_profiles = ()
        self._current_voice_properties = {}
        self._default_voice_name = guilabels.SPEECH_DEFAULT_VOICE % \
            SpeechServer._SERVER_NAMES.get(self._id, self._id)

        if not SpeechServer._active_providers:
            msg = "ERROR: No Spiel providers available."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return

        self._provider = SpeechServer._active_providers.get(self._id)
        if self._provider is None:
            self._provider = next(iter(SpeechServer._active_providers.values()))

        # Load the provider voices for this server
        if self._id and self._id != SpeechServer.DEFAULT_SERVER_ID:
            self._voices_id = self._provider.props.voices.connect(
                "items-changed", self._updateVoices)
            msg = f"SPIEL: Connected voices signal with ID {self._voices_id} for provider {self._id}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            self._voices_id = None
            msg = "SPIEL: No voices signal connection for default server"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        self._updateVoices(self._provider.props.voices)

    def _create_utterance(self, text, acss):
        pitch = self._get_pitch(acss.get(ACSS.AVERAGE_PITCH, 5.0))
        rate = self._get_rate(acss.get(ACSS.RATE, 50))
        volume = self._get_volume(acss.get(ACSS.GAIN, 5))
        voice = self._get_voice(acss.get(ACSS.FAMILY, {}))

        if voice is None:
            debug.print_message(debug.LEVEL_WARNING, "No available voices", True)
            return None

        # If the text is not pre-formatted SSML, and the voice supports it,
        # convert the text to SSML with word offsets marked.
        is_ssml = text.startswith('<speak>') and text.endswith('</speak>')
        if not is_ssml and voice.props.features & Spiel.VoiceFeature.EVENTS_SSML_MARK:
            text = SSML.markupText(text, SSMLCapabilities.MARK)
            is_ssml = True

        return Spiel.Utterance(text=text,
                               pitch=pitch,
                               rate=rate,
                               volume=volume,
                               voice=voice,
                               is_ssml=is_ssml)

    def _speak_utterance(self, utterance, acss):
        if not utterance:
            return

        self._apply_acss(acss)
        self._debug_spiel_values(f"Speaking '{utterance.props.text}' ")
        self._speaker.speak(utterance)

    def get_info(self):
        return [self._SERVER_NAMES.get(self._id, self._id), self._id]

    def getVoiceFamilies(self):
        # Always offer the configured default voice with a language
        # set according to the current locale.
        from locale import getlocale, LC_MESSAGES
        locale = getlocale(LC_MESSAGES)[0]
        if locale is None or '_' not in locale:
            locale_language = None
        else:
            locale_lang, locale_dialect = locale.split('_')
            locale_language = locale_lang + '-' + locale_dialect

        voices = self._current_voice_profiles

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

    def speak_character(self, character, acss=None):
        debug.print_message(debug.LEVEL_INFO, f"SPIEL Character: '{character}'")

        if not acss:
            acss = settings.voices[settings.DEFAULT_VOICE]

        voice = self._get_voice(acss.get(ACSS.FAMILY, {}))
        if voice is None:
            debug.print_message(debug.LEVEL_WARNING, "No available voices", True)
            return

        features = voice.props.features
        if features & Spiel.VoiceFeature.SSML_SAY_AS_CHARACTERS_GLYPHS:
            text = ("<speak>"
                    f'<say-as interpret-as="characters" format="glyphs">{character}</say-as>'
                    "</speak>")
        elif features & Spiel.VoiceFeature.SSML_SAY_AS_CHARACTERS:
            text = f'<speak><say-as interpret-as="characters">{character}</say-as></speak>'
        else:
            text = character

        utterance = self._create_utterance(text, acss)
        self._speak_utterance(utterance, acss)

    def speak_key_event(self, event, acss=None):
        event_string = event.get_key_name()
        lockingStateString = event.get_locking_state_string()
        event_string = f"{event_string} {lockingStateString}".strip()
        if len(event_string) == 1:
            msg = f"SPIEL: Speaking '{event_string}' as key"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._apply_acss(acss)
            self.speak_character(event_string, acss)
        else:
            msg = f"SPIEL: Speaking '{event_string}' as string"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.speak(event_string, acss=acss)

    def speak(self, text=None, acss=None, interrupt=True):
        if not text:
            return

        if not acss:
            acss = settings.voices[settings.DEFAULT_VOICE]

        # See speechdispatcherfactory.py for why this is disabled
        # if interrupt:
        #     self._speaker.cancel()

        if len(text) == 1:
            msg = f"SPIEL: Speaking '{text}' as char"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._apply_acss(acss)
            self.speak_character(text, acss)
        else:
            msg = f"SPIEL: Speaking '{text}' as string"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            utterance = self._create_utterance(text, acss)
            self._speak_utterance(utterance, acss)

    def say_all(self, utterance_iterator, progress_callback):
        try:
            context, acss = next(utterance_iterator)
        except StopIteration:
            pass
        else:
            def _utterance_started(speaker, utterance, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"STARTED: {utterance.props.text}")
                (callback, currentUtterance, _) = sayall_data
                if currentUtterance == utterance:
                    callback(context, speechserver.SayAllContext.PROGRESS)

            def _utterance_finished(speaker, utterance, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"FINISHED: {utterance.props.text}")
                (callback, currentUtterance, handlers) = sayall_data
                if currentUtterance == utterance:
                    callback(context, speechserver.SayAllContext.PROGRESS)
                    [speaker.disconnect(handler) for handler in handlers]
                    callback(context, speechserver.SayAllContext.COMPLETED)
                    context.currentOffset = context.endOffset
                    context.currentEndOffset = None
                    self.say_all(utterance_iterator, callback)

            def _utterance_canceled(speaker, utterance, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"CANCELED: {utterance.props.text}")
                (callback, currentUtterance, handlers) = sayall_data
                if currentUtterance == utterance:
                    [speaker.disconnect(handler) for handler in handlers]
                    callback(context, speechserver.SayAllContext.INTERRUPTED)

            def _utterance_error(speaker, utterance, error, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"ERROR: {utterance.props.text}")
                debug.print_message(debug.LEVEL_WARNING, f"ERROR: {repr(error)}")
                (callback, currentUtterance, handlers) = sayall_data
                if currentUtterance == utterance:
                    [speaker.disconnect(handler) for handler in handlers]
                    callback(context, speechserver.SayAllContext.INTERRUPTED)

            def _mark_reached(_speaker, utterance, name, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"MARK REACHED: {name}")
                (callback, currentUtterance, handlers) = sayall_data
                if currentUtterance == utterance:
                    callback(context, speechserver.SayAllContext.PROGRESS)

            def _range_started(_speaker, utterance, start, end, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"RANGE STARTED: {start}-{end}")
                (callback, currentUtterance, handlers) = sayall_data
                if currentUtterance == utterance:
                    # TODO: map start/end to currentOffset/currentEndOffset
                    callback(context, speechserver.SayAllContext.PROGRESS)

            def _word_started(_speaker, utterance, start, end, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"WORD STARTED: {start}-{end}")
                (callback, currentUtterance, handlers) = sayall_data
                if currentUtterance == utterance:
                    context.currentOffset = start
                    context.currentEndOffset = end
                    # TODO: map start/end to currentOffset/currentEndOffset
                    callback(context, speechserver.SayAllContext.PROGRESS)

            def _sentence_started(_speaker, _utterance, start, end, sayall_data):
                debug.print_message(debug.LEVEL_INFO, f"SENTENCE STARTED: {start}-{end}")
                (callback, currentUtterance, _) = sayall_data
                if currentUtterance == utterance:
                    # TODO: map start/end to currentOffset/currentEndOffset
                    callback(context, speechserver.SayAllContext.PROGRESS)

            utterance = self._create_utterance(context.utterance, acss)
            if not utterance:
                return

            handlers = []
            sayall_data = (progress_callback, utterance, handlers)
            handlers += [
                self._speaker.connect('utterance-started', _utterance_started, sayall_data),
                self._speaker.connect('utterance-finished', _utterance_finished, sayall_data),
                self._speaker.connect('utterance-canceled', _utterance_canceled, sayall_data),
                self._speaker.connect('utterance-error', _utterance_error, sayall_data),
            ]

            # Use the range-started signal for progress, if supported

            try:
                # TODO - JD: This line was in the original commit.
                # Error: 'int' object has no attribute 'props'
                voice = utterance.props.voice
                features = voice.props.features
            except AttributeError as error:
                msg = f"SPIEL: Error getting voice features: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                features = Spiel.VoiceFeature.NONE

            if features & Spiel.VoiceFeature.EVENTS_WORD:
                handlers.append(self._speaker.connect('word-started',
                                                      _word_started,
                                                      sayall_data))
            if features & Spiel.VoiceFeature.EVENTS_SENTENCE:
                handlers.append(self._speaker.connect('sentence-started',
                                                      _sentence_started,
                                                      sayall_data))
            if features & Spiel.VoiceFeature.EVENTS_RANGE:
                handlers.append(self._speaker.connect('range-started',
                                                      _range_started,
                                                      sayall_data))
            if features & Spiel.VoiceFeature.EVENTS_SSML_MARK:
                handlers.append(self._speaker.connect('mark-reached',
                                                      _mark_reached,
                                                      sayall_data))

            self._speak_utterance(utterance, acss)

    def _change_default_speech_rate(self, step, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            rate = acss[ACSS.RATE]
        except KeyError:
            rate = 50
        acss[ACSS.RATE] = max(0, min(99, rate + delta))
        msg = f"SPIEL: Rate set to {rate}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_pitch(self, step, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            pitch = acss[ACSS.AVERAGE_PITCH]
        except KeyError:
            pitch = 5
        acss[ACSS.AVERAGE_PITCH] = max(0, min(9, pitch + delta))
        msg = f"SPIEL: Pitch set to {pitch}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_volume(self, step, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            volume = acss[ACSS.GAIN]
        except KeyError:
            volume = 10
        acss[ACSS.GAIN] = max(0, min(9, volume + delta))
        msg = f"SPIEL: Volume set to {volume}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _maybe_shutdown(self):
        # We're the last speaker, wrap things up
        if len(SpeechServer._active_servers.values()) == 1:
            while SpeechServer.DEFAULT_SPEAKER.props.speaking:
                GLib.MainContext.default().iteration(False)

            # Ensure nothing squeaks through
            SpeechServer.DEFAULT_SPEAKER.pause()
            SpeechServer.DEFAULT_SPEAKER = None
            return True

        return False

    def increaseSpeechRate(self, step=5):
        self._change_default_speech_rate(step)

    def decreaseSpeechRate(self, step=5):
        self._change_default_speech_rate(step, decrease=True)

    def increaseSpeechPitch(self, step=0.5):
        self._change_default_speech_pitch(step)

    def decreaseSpeechPitch(self, step=0.5):
        self._change_default_speech_pitch(step, decrease=True)

    def increaseSpeechVolume(self, step=0.5):
        self._change_default_speech_volume(step)

    def decreaseSpeechVolume(self, step=0.5):
        self._change_default_speech_volume(step, decrease=True)

    def stop(self):
        self._speaker.cancel()

    def shutdown(self):
        msg = f"SPIEL: Shutting down server {self._id}, voices_id: {self._voices_id}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if self._id != SpeechServer.DEFAULT_SERVER_ID and self._voices_id is not None:
            try:
                self._provider.props.voices.disconnect(self._voices_id)
                msg = f"SPIEL: Successfully disconnected voices signal {self._voices_id}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            except Exception as error:
                msg = f"SPIEL: Error disconnecting voices signal {self._voices_id}: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)

        self._maybe_shutdown()
        if self._id in SpeechServer._active_servers:
            del SpeechServer._active_servers[self._id]

    def reset(self, text=None, acss=None):
        self._speaker.cancel()
        if self._id != SpeechServer.DEFAULT_SERVER_ID and self._voices_id is not None:
            try:
                self._provider.props.voices.disconnect(self._voices_id)
            except Exception as error:
                msg = f"SPIEL: Error disconnecting voices signal in reset: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
        self._init()

    def getOutputModule(self):
        return self._id

    def setOutputModule(self, module_id):
        """Set the speech output module to the specified provider."""

        if module_id not in SpeechServer._active_providers:
            tokens = [f"SPIEL: {module_id} is not in", SpeechServer._active_providers]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        if self._id == module_id:
            msg = f"SPIEL: Already using provider {module_id}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self._id and self._id != SpeechServer.DEFAULT_SERVER_ID and self._voices_id is not None:
            try:
                self._provider.props.voices.disconnect(self._voices_id)
                self._voices_id = None
                msg = f"SPIEL: Disconnected voices signal for old provider {self._id}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            except Exception as error:
                msg = f"SPIEL: Error disconnecting voices signal: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)

        old_id = self._id
        self._id = module_id
        self._provider = SpeechServer._active_providers.get(self._id)
        if self._provider is None:
            self._provider = next(iter(SpeechServer._active_providers.values()))

        if old_id in SpeechServer._active_servers:
            del SpeechServer._active_servers[old_id]
        SpeechServer._active_servers[self._id] = self

        if self._id != SpeechServer.DEFAULT_SERVER_ID:
            self._voices_id = self._provider.props.voices.connect(
                "items-changed", self._updateVoices)
            msg = (
                f"SPIEL: Connected voices signal with ID {self._voices_id} "
                f"for new provider {self._id}"
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)

        self._updateVoices(self._provider.props.voices)
        self._default_voice_name = guilabels.SPEECH_DEFAULT_VOICE % \
            SpeechServer._SERVER_NAMES.get(self._id, self._id)

        msg = f"SPIEL: Switched from {old_id} to {self._id}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def getVoiceFamily(self):
        """Returns the current voice family as a VoiceFamily dictionary."""

        voice_name = ""
        language = ""
        try:
            if self._current_voice:
                voice_name = self._current_voice.props.name
                languages = self._current_voice.props.languages
                language = languages[0] if languages else ""
            else:
                voice_name = self._default_voice_name or "spiel-default"
        except (AttributeError, IndexError):
            voice_name = self._default_voice_name or "spiel-default"

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

    def setVoiceFamily(self, family):
        """Sets the voice family to family VoiceFamily dictionary."""

        if not family:
            return

        voice_name = family.get(speechserver.VoiceFamily.NAME, "")
        language = family.get(speechserver.VoiceFamily.LANG, "")
        dialect = family.get(speechserver.VoiceFamily.DIALECT, "")
        if dialect:
            language = f"{language}-{dialect}" if language else dialect

        if not voice_name:
            return

        try:
            voices = self._provider.props.voices
        except AttributeError as error:
            msg = f"SPIEL: Error getting voices from provider: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return

        partial_matches = []
        for voice in voices:
            try:
                if voice.props.name == voice_name:
                    if not language or (language in voice.props.languages):
                        self._current_voice = voice
                        return
                    partial_matches.append(voice)
            except AttributeError as error:
                msg = f"SPIEL: Error accessing voice properties: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)

        if partial_matches:
            msg = (
                f"SPIEL: {len(partial_matches)} partial matches found for voice '{voice_name}'. "
                f"Using the first ({partial_matches[0]})"
            )
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            self._current_voice = partial_matches[0]
