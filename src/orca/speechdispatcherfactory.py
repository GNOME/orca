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

"""Provides an Orca speech server for Speech Dispatcher backend."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__author__    = "Tomas Cerha <cerha@brailcom.org>"
__copyright__ = "Copyright (c) 2006-2008 Brailcom, o.p.s."
__license__   = "LGPL"

from gi.repository import GLib
import time

from . import debug
from . import guilabels
from . import mathsymbols
from . import messages
from . import speechserver
from . import settings
from . import script_manager
from . import settings_manager
from .acss import ACSS
from .ssml import SSML, SSMLCapabilities

try:
    import speechd
except Exception:
    _speechd_available = False
else:    
    _speechd_available = True
    try:
        getattr(speechd, "CallbackType")
    except AttributeError:
        _speechd_version_ok = False
    else:
        _speechd_version_ok = True

class SpeechServer(speechserver.SpeechServer):
    # See the parent class for documentation.

    _active_servers = {}
    
    DEFAULT_SERVER_ID = 'default'
    _SERVER_NAMES = {DEFAULT_SERVER_ID: guilabels.DEFAULT_SYNTHESIZER}

    @staticmethod
    def getFactoryName():
        return guilabels.SPEECH_DISPATCHER

    @staticmethod
    def getSpeechServers():
        servers = []
        default = SpeechServer._get_speech_server(SpeechServer.DEFAULT_SERVER_ID)
        if default is not None:
            servers.append(default)
            for module in default.list_output_modules():
                servers.append(SpeechServer._get_speech_server(module))
        return servers

    @classmethod
    def _get_speech_server(cls, serverId):
        """Return an active server for given id.

        Attempt to create the server if it doesn't exist yet.  Returns None
        when it is not possible to create the server.
        
        """
        if serverId not in cls._active_servers:
            cls(serverId)
        # Don't return the instance, unless it is successfully added
        # to `_active_Servers'.
        return cls._active_servers.get(serverId)

    @staticmethod
    def get_speech_server(info=None):
        thisId = info[1] if info is not None else SpeechServer.DEFAULT_SERVER_ID
        return SpeechServer._get_speech_server(thisId)

    @staticmethod
    def shutdownActiveServers():
        servers = [s for s in SpeechServer._active_servers.values()]
        for server in servers:
            server.shutdown()

    # *** Instance methods ***

    def __init__(self, serverId):
        super(SpeechServer, self).__init__()
        self._id = serverId
        self._client = None
        self._current_voice_properties = {}
        self._acss_manipulators = (
            (ACSS.RATE, self._set_rate),
            (ACSS.AVERAGE_PITCH, self._set_pitch),
            (ACSS.GAIN, self._set_volume),
            (ACSS.FAMILY, self._set_family),
            )
        if not _speechd_available:
            msg = 'ERROR: Speech Dispatcher is not available'
            debug.printMessage(debug.LEVEL_WARNING, msg, True)
            return
        if not _speechd_version_ok:
            msg = 'ERROR: Speech Dispatcher version 0.6.2 or later is required.'
            debug.printMessage(debug.LEVEL_WARNING, msg, True)
            return
        # The following constants must be initialized in runtime since they
        # depend on the speechd module being available.
        try:
            most = speechd.PunctuationMode.MOST
        except Exception:
            most = speechd.PunctuationMode.SOME
        self._PUNCTUATION_MODE_MAP = {
            settings.PUNCTUATION_STYLE_ALL:  speechd.PunctuationMode.ALL,
            settings.PUNCTUATION_STYLE_MOST: most,
            settings.PUNCTUATION_STYLE_SOME: speechd.PunctuationMode.SOME,
            settings.PUNCTUATION_STYLE_NONE: speechd.PunctuationMode.NONE,
            }
        self._CALLBACK_TYPE_MAP = {
            speechd.CallbackType.BEGIN: speechserver.SayAllContext.PROGRESS,
            speechd.CallbackType.CANCEL: speechserver.SayAllContext.INTERRUPTED,
            speechd.CallbackType.END: speechserver.SayAllContext.COMPLETED,
            speechd.CallbackType.INDEX_MARK:speechserver.SayAllContext.PROGRESS,
            }

        self._default_voice_name = guilabels.SPEECH_DEFAULT_VOICE % serverId

        try:
            self._init()
        except Exception:
            debug.printException(debug.LEVEL_WARNING)
            msg = 'ERROR: Speech Dispatcher service failed to connect'
            debug.printMessage(debug.LEVEL_WARNING, msg, True)
        else:
            SpeechServer._active_servers[serverId] = self

    def _init(self):
        self._client = client = speechd.SSIPClient('Orca', component=self._id)
        client.set_priority(speechd.Priority.MESSAGE)
        if self._id != self.DEFAULT_SERVER_ID:
            client.set_output_module(self._id)
        self._current_voice_properties = {}
        mode = self._PUNCTUATION_MODE_MAP[settings.verbalizePunctuationStyle]
        client.set_punctuation(mode)
        client.set_data_mode(speechd.DataMode.SSML)

    def updateCapitalizationStyle(self):
        """Updates the capitalization style used by the speech server."""

        if settings.capitalizationStyle == settings.CAPITALIZATION_STYLE_ICON:
            style = 'icon'
        elif settings.capitalizationStyle == settings.CAPITALIZATION_STYLE_SPELL:
            style = 'spell'
        else:
            style = 'none'

        try:
            self._client.set_cap_let_recogn(style)
        except speechd.SSIPCommunicationError:
            msg = "SPEECH DISPATCHER: Connection lost. Trying to reconnect."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.reset()
            self._client.set_cap_let_recogn(style)
        except Exception:
            pass

    def updatePunctuationLevel(self):
        """ Punctuation level changed, inform this speechServer. """
        mode = self._PUNCTUATION_MODE_MAP[settings.verbalizePunctuationStyle]
        self._client.set_punctuation(mode)

    def _send_command(self, command, *args, **kwargs):
        try:
            return command(*args, **kwargs)
        except speechd.SSIPCommunicationError:
            msg = "SPEECH DISPATCHER: Connection lost. Trying to reconnect."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.reset()
            return command(*args, **kwargs)
        except Exception:
            pass

    def _set_rate(self, acss_rate):
        rate = int(2 * max(0, min(99, acss_rate)) - 98)
        self._send_command(self._client.set_rate, rate)

    def _set_pitch(self, acss_pitch):
        pitch = int(20 * max(0, min(9, acss_pitch)) - 90)
        self._send_command(self._client.set_pitch, pitch)

    def _set_volume(self, acss_volume):
        volume = int(15 * max(0, min(9, acss_volume)) - 35)
        self._send_command(self._client.set_volume, volume)

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

    def _set_family(self, acss_family):
        lang, dialect = self._get_language_and_dialect(acss_family)
        if lang:
            self._send_command(self._client.set_language, lang)
            if dialect:
                # Try to set precise dialect
                self._send_command(self._client.set_language, lang + '-' + dialect)

        try:
            # This command is not available with older SD versions.
            set_synthesis_voice = self._client.set_synthesis_voice
        except AttributeError:
            pass
        else:
            name = acss_family.get(speechserver.VoiceFamily.NAME)
            if name is not None and name != self._default_voice_name:
                self._send_command(set_synthesis_voice, name)

    def _debug_sd_values(self, prefix=""):
        if debug.debugLevel > debug.LEVEL_INFO:
            return

        try:
            sd_rate = self._send_command(self._client.get_rate)
            sd_pitch = self._send_command(self._client.get_pitch)
            sd_volume = self._send_command(self._client.get_volume)
            sd_language = self._send_command(self._client.get_language)
        except Exception:
            sd_rate = sd_pitch = sd_volume = sd_language = "(exception occurred)"

        family = self._current_voice_properties.get(ACSS.FAMILY)

        styles = {settings.PUNCTUATION_STYLE_NONE: "NONE",
                  settings.PUNCTUATION_STYLE_SOME: "SOME",
                  settings.PUNCTUATION_STYLE_MOST: "MOST",
                  settings.PUNCTUATION_STYLE_ALL: "ALL"}

        msg = (
            f"SPEECH DISPATCHER: {prefix}\n"
            f"ORCA rate {self._current_voice_properties.get(ACSS.RATE)}, "
            f"pitch {self._current_voice_properties.get(ACSS.AVERAGE_PITCH)}, "
            f"volume {self._current_voice_properties.get(ACSS.GAIN)}, "
            f"language {self._get_language_and_dialect(family)[0]}, "
            f"punctuation: "
            f"{styles.get(settings_manager.get_manager().get_setting('verbalizePunctuationStyle'))}\n"
            f"SD rate {sd_rate}, pitch {sd_pitch}, volume {sd_volume}, language {sd_language}"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _apply_acss(self, acss):
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
                method(5.0)
                current[acss_property] = 5.0
            elif acss_property == ACSS.GAIN:
                method(10)
                current[acss_property] = 5.0
            elif acss_property == ACSS.RATE:
                method(50)
                current[acss_property] = 5.0
            elif acss_property == ACSS.FAMILY:
                method({})
                current[acss_property] = {}

    def _speak(self, text, acss, **kwargs):
        if isinstance(text, ACSS):
            text = ''
 
        ssml = SSML.markupText(text, SSMLCapabilities.MARK)

        self._apply_acss(acss)
        self._debug_sd_values(f"Speaking '{ssml}' ")
        self._send_command(self._client.speak, ssml, **kwargs)

    def _say_all(self, iterator, orca_callback):
        """Process another sayAll chunk.

        Called by the gidle thread.

        """
        try:
            context, acss = next(iterator)
        except StopIteration:
            pass
        else:
            def callback(callbackType, index_mark=None):
                # This callback is called in Speech Dispatcher listener thread.
                # No subsequent Speech Dispatcher interaction is allowed here,
                # so we pass the calls to the gidle thread.
                t = self._CALLBACK_TYPE_MAP[callbackType]
                if t == speechserver.SayAllContext.PROGRESS:
                    if index_mark:
                        index = index_mark.split(':')
                        if len(index) >= 2:
                            start, end = index[0:2]
                            context.currentOffset = context.startOffset + int(start)
                            context.currentEndOffset = context.startOffset + int(end)
                            msg = (
                                f"SPEECH DISPATCHER: Got mark "
                                f"{context.currentOffset}:{context.currentEndOffset} / "
                                f"{context.startOffset}:{context.endOffset}"
                            )
                            debug.printMessage(debug.LEVEL_INFO, msg, True)
                    else:
                        context.currentOffset = context.startOffset
                        context.currentEndOffset = None
                elif t == speechserver.SayAllContext.COMPLETED:
                    context.currentOffset = context.endOffset
                    context.currentEndOffset = None
                GLib.idle_add(orca_callback, context.copy(), t)
                if t == speechserver.SayAllContext.COMPLETED:
                    GLib.idle_add(self._say_all, iterator, orca_callback)
            self._speak(context.utterance, acss, callback=callback,
                        event_types=list(self._CALLBACK_TYPE_MAP.keys()))
        return False # to indicate, that we don't want to be called again.

    def _cancel(self):
        self._send_command(self._client.cancel)

    def _change_default_speech_rate(self, step, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            rate = acss[ACSS.RATE]
        except KeyError:
            rate = 50
        acss[ACSS.RATE] = max(0, min(99, rate + delta))
        msg = f"SPEECH DISPATCHER: Rate set to {rate}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.speak(decrease and messages.SPEECH_SLOWER \
                   or messages.SPEECH_FASTER, acss=acss)

    def _change_default_speech_pitch(self, step, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            pitch = acss[ACSS.AVERAGE_PITCH]
        except KeyError:
            pitch = 5
        acss[ACSS.AVERAGE_PITCH] = max(0, min(9, pitch + delta))
        msg = f"SPEECH DISPATCHER: Pitch set to {pitch}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.speak(decrease and messages.SPEECH_LOWER \
                   or messages.SPEECH_HIGHER, acss=acss)

    def _change_default_speech_volume(self, step, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = step * (decrease and -1 or +1)
        try:
            volume = acss[ACSS.GAIN]
        except KeyError:
            volume = 10
        acss[ACSS.GAIN] = max(0, min(9, volume + delta))
        msg = f"SPEECH DISPATCHER: Volume set to {volume}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.speak(decrease and messages.SPEECH_SOFTER \
                   or messages.SPEECH_LOUDER, acss=acss)

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
        voices = ()
        try:
            # This command is not available with older SD versions.
            list_synthesis_voices = self._client.list_synthesis_voices
        except AttributeError:
            pass
        else:
            try:
                voices += self._send_command(list_synthesis_voices)
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

    def speak(self, text=None, acss=None, interrupt=True):
        if not text:
            return

        # In order to re-enable this, a potentially non-trivial amount of work
        # will be needed to ensure multiple utterances sent to speech.speak
        # do not result in the intial utterances getting cut off before they
        # can be heard by the user. Anyone needing to interrupt speech can
        # do so via speech.stop -- or better yet, by using the default script
        # method's presentationInterrupt.
        #if interrupt:
        #    self._cancel()

        if len(text) == 1:
            msg = f"SPEECH DISPATCHER: Speaking '{text}' as char"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._apply_acss(acss)
            self._send_command(self._client.char, text)
        else:
            msg = f"SPEECH DISPATCHER: Speaking '{text}' as string"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._speak(text, acss)

    def say_all(self, utterance_iterator, progress_callback):
        GLib.idle_add(self._say_all, utterance_iterator, progress_callback)

    def speak_character(self, character, acss=None):
        self._apply_acss(acss)

        name = character
        script = script_manager.get_manager().get_active_script()
        if script and script.utilities.speakMathSymbolNames():
            name = mathsymbols.getCharacterName(character)

        if not name or name == character:
            msg = f"SPEECH DISPATCHER: Speaking '{character}' as char"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._send_command(self._client.char, character)
            return

        self.speak(name, acss)

    def speak_key_event(self, event, acss=None):
        event_string = event.get_key_name()
        lockingStateString = event.get_locking_state_string()
        event_string = f"{event_string} {lockingStateString}".strip()
        if len(event_string) == 1:
            msg = f"SPEECH DISPATCHER: Speaking '{event_string}' as key"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._apply_acss(acss)
            self._send_command(self._client.key, event_string)
        else:
            msg = f"SPEECH DISPATCHER: Speaking '{event_string}' as string"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.speak(event_string, acss=acss)

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

    def getLanguage(self):
        """Returns the current language."""

        return self._client.get_language()

    def setLanguage(self, language, dialect):
        """Sets the current language"""

        if not language:
            return

        self._client.set_language(language)
        if dialect:
            self._client.set_language(language + "-" + dialect)

    def _normalizedLanguageAndDialect(self, language, dialect=""):
        """Attempts to ensure consistency across inconsistent formats."""

        if "-" in language:
            normalized_language = language.split("-", 1)[0].lower()
            normalized_dialect = language.split("-", 1)[-1].lower()
        else:
            normalized_language = language.lower()
            normalized_dialect = dialect.lower()

        return normalized_language, normalized_dialect

    def getVoiceFamiliesForLanguage(self, language, dialect, maximum=None):
        """Returns the families for language available in the current synthesizer."""

        start = time.time()
        target_language, target_dialect = self._normalizedLanguageAndDialect(language, dialect)

        result = []
        voices = self._client.list_synthesis_voices()

        for voice in voices:
            normalized_language, normalized_dialect = self._normalizedLanguageAndDialect(voice[1])
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
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return result

    def shouldChangeVoiceForLanguage(self, language, dialect=""):
        """Returns True if we should change the voice for the specified language."""

        current_language, current_dialect = self._normalizedLanguageAndDialect(self.getLanguage())
        other_language, other_dialect = self._normalizedLanguageAndDialect(language, dialect)

        msg = (
            f"SPEECH DISPATCHER: Should change voice for language? "
            f"Current: '{current_language}' '{current_dialect}' "
            f"New: '{other_language}' '{other_dialect}'"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        if current_language == other_language and current_dialect == other_dialect:
            msg ="SPEECH DISPATCHER: No. Language and dialect are the same."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        families = self.getVoiceFamiliesForLanguage(other_language, other_dialect, maximum=1)
        if families:
            tokens = ["SPEECH DISPATCHER: Yes. Found matching family", families[0], "."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["SPEECH DISPATCHER: No. No matching family in", self.getOutputModule(), "."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return True

    def getOutputModule(self):
        return self._client.get_output_module()

    def setOutputModule(self, module):
        self._client.set_output_module(module)

    def stop(self):
        self._cancel()

    def shutdown(self):
        self._client.close()
        del SpeechServer._active_servers[self._id]

    def reset(self, text=None, acss=None):
        self._client.close()
        self._init()
        
    def list_output_modules(self):
        """Return names of available output modules as a tuple of strings.

        This method is not a part of Orca speech API, but is used internally
        by the Speech Dispatcher backend.
        
        The returned tuple can be empty if the information can not be
        obtained (e.g. with an older Speech Dispatcher version).
        
        """
        try:
            return self._send_command(self._client.list_output_modules)
        except AttributeError:
            return ()
        except speechd.SSIPCommandError:
            return ()

