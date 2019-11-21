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

# # [[[TODO: richb - Pylint is giving us a bunch of warnings along these
# lines throughout this file:
#
#  W0142:202:SpeechServer._send_command: Used * or ** magic
#
# So for now, we just disable these warnings in this module.]]]
#
# pylint: disable-msg=W0142

"""Provides an Orca speech server for Speech Dispatcher backend."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__author__    = "Tomas Cerha <cerha@brailcom.org>"
__copyright__ = "Copyright (c) 2006-2008 Brailcom, o.p.s."
__license__   = "LGPL"

from gi.repository import GLib
import re
import time

from . import chnames
from . import debug
from . import guilabels
from . import messages
from . import speechserver
from . import settings
from . import orca_state
from . import punctuation_settings
from . import settings_manager
from .acss import ACSS

_settingsManager = settings_manager.getManager()

try:
    import speechd
except:
    _speechd_available = False
else:    
    _speechd_available = True
    try:
        getattr(speechd, "CallbackType")
    except AttributeError:
        _speechd_version_ok = False
    else:
        _speechd_version_ok = True

PUNCTUATION = re.compile(r'[^\w\s]', re.UNICODE)
ELLIPSIS = re.compile('(\342\200\246|(?<!\\.)\\.{3,4}(?=(\\s|\\Z)))')

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
        default = SpeechServer._getSpeechServer(SpeechServer.DEFAULT_SERVER_ID)
        if default is not None:
            servers.append(default)
            for module in default.list_output_modules():
                servers.append(SpeechServer._getSpeechServer(module))
        return servers

    @classmethod
    def _getSpeechServer(cls, serverId):
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
    def getSpeechServer(info=None):
        thisId = info[1] if info is not None else SpeechServer.DEFAULT_SERVER_ID
        return SpeechServer._getSpeechServer(thisId)

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
            debug.println(debug.LEVEL_WARNING, msg, True)
            return
        if not _speechd_version_ok:
            msg = 'ERROR: Speech Dispatcher version 0.6.2 or later is required.'
            debug.println(debug.LEVEL_WARNING, msg, True)
            return
        # The following constants must be initialized in runtime since they
        # depend on the speechd module being available.
        self._PUNCTUATION_MODE_MAP = {
            settings.PUNCTUATION_STYLE_ALL:  speechd.PunctuationMode.ALL,
            settings.PUNCTUATION_STYLE_MOST: speechd.PunctuationMode.SOME,
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
        except:
            debug.printException(debug.LEVEL_WARNING)
            msg = 'ERROR: Speech Dispatcher service failed to connect'
            debug.println(debug.LEVEL_WARNING, msg, True)
        else:
            SpeechServer._active_servers[serverId] = self

        self._lastKeyEchoTime = None

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
        self._client.set_cap_let_recogn(style)

    def updatePunctuationLevel(self):
        """ Punctuation level changed, inform this speechServer. """
        mode = self._PUNCTUATION_MODE_MAP[settings.verbalizePunctuationStyle]
        self._client.set_punctuation(mode)

    def _send_command(self, command, *args, **kwargs):
        if hasattr(speechd, 'SSIPCommunicationError'):
            try:
                return command(*args, **kwargs)
            except speechd.SSIPCommunicationError:
                msg = "SPEECH DISPATCHER: Connection lost. Trying to reconnect."
                debug.println(debug.LEVEL_INFO, msg, True)
                self.reset()
                return command(*args, **kwargs)
            except:
                pass
        else:
            # It is not possible tho catch the error with older SD versions. 
            return command(*args, **kwargs)

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
            self._send_command(set_synthesis_voice, name)

    def _debug_sd_values(self, prefix=""):
        if debug.debugLevel > debug.LEVEL_INFO:
            return

        try:
            sd_rate = self._send_command(self._client.get_rate)
            sd_pitch = self._send_command(self._client.get_pitch)
            sd_volume = self._send_command(self._client.get_volume)
            sd_language = self._send_command(self._client.get_language)
        except:
            sd_rate = sd_pitch = sd_volume = sd_language = "(exception occurred)"

        family = self._current_voice_properties.get(ACSS.FAMILY)

        current = self._current_voice_properties
        msg = "SPEECH DISPATCHER: %sOrca rate %s, pitch %s, volume %s, language %s; " \
              "SD rate %s, pitch %s, volume %s, language %s" % \
              (prefix,
               self._current_voice_properties.get(ACSS.RATE),
               self._current_voice_properties.get(ACSS.AVERAGE_PITCH),
               self._current_voice_properties.get(ACSS.GAIN),
               self._get_language_and_dialect(family)[0],
               sd_rate,
               sd_pitch,
               sd_volume,
               sd_language)
        debug.println(debug.LEVEL_INFO, msg, True)

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

    def __addVerbalizedPunctuation(self, oldText):
        """Depending upon the users verbalized punctuation setting,
        adjust punctuation symbols in the given text to their pronounced
        equivalents. The pronounced text will either replace the
        punctuation symbol or be inserted before it. In the latter case,
        this is to retain spoken prosity.

        Arguments:
        - oldText: text to be parsed for punctuation.

        Returns a text string with the punctuation symbols adjusted accordingly.
        """

        style = _settingsManager.getSetting("verbalizePunctuationStyle")
        if style == settings.PUNCTUATION_STYLE_NONE:
            return oldText

        spokenEllipsis = messages.SPOKEN_ELLIPSIS + " "
        newText = re.sub(ELLIPSIS, spokenEllipsis, oldText)
        symbols = set(re.findall(PUNCTUATION, newText))
        for symbol in symbols:
            try:
                level, action = punctuation_settings.getPunctuationInfo(symbol)
            except:
                continue

            if level != punctuation_settings.LEVEL_NONE:
                # Speech Dispatcher should handle it.
                #
                continue

            charName = " %s " % chnames.getCharacterName(symbol)
            if action == punctuation_settings.PUNCTUATION_INSERT:
                charName += symbol
            newText = re.sub(symbol, charName, newText)

        if orca_state.activeScript:
            newText = orca_state.activeScript.utilities.adjustForDigits(newText)

        return newText

    def _speak(self, text, acss, **kwargs):
        if isinstance(text, ACSS):
            text = ''

        # Mark beginning of words with U+E000 (private use) and record the
        # string offsets
        # Note: we need to do this before disturbing the text offsets
        # Note2: we assume that text mangling below leave U+E000 untouched
        last_begin = None
        last_end = None
        marks_offsets = []
        marks_endoffsets = []
        marked_text = ""

        for i in range(len(text)):
            c = text[i]
            if c == '\ue000':
                # Original text already contains U+E000. But syntheses will not
                # know what to do of it anyway, so discard it
                continue

            if not c.isspace() and last_begin == None:
                # Word begin
                marked_text += '\ue000'
                last_begin = i

            if c.isspace() and last_begin != None:
                # Word end, add a mark
                marks_offsets.append(last_begin)
                marks_endoffsets.append(i)
                last_begin = None

            marked_text += c

        if last_begin != None:
            # Finished with a word
            marks_offsets.append(last_begin)
            marks_endoffsets.append(i + 1)

        text = marked_text

        text = self.__addVerbalizedPunctuation(text)
        if orca_state.activeScript:
            text = orca_state.activeScript.\
                utilities.adjustForPronunciation(text)

        # Replace no break space characters with plain spaces since some
        # synthesizers cannot handle them.  See bug #591734.
        #
        text = text.replace('\u00a0', ' ')

        # Replace newline followed by full stop, since
        # this seems to crash sd, see bgo#618334.
        #
        text = text.replace('\n.', '\n')

        # Transcribe to SSML, translating U+E000 into marks
        # Note: we need to do this after all mangling otherwise the ssml markup
        # would get mangled too
        ssml = "<speak>"
        i = 0
        for c in text:
            if c == '\ue000':
                if i >= len(marks_offsets):
                    # This is really not supposed to happen
                    msg = "%uth U+E000 does not have corresponding index" % i
                    debug.println(debug.LEVEL_WARNING, msg, True)
                else:
                    ssml += '<mark name="%u:%u"/>' % (marks_offsets[i], marks_endoffsets[i])
                i += 1
            # Disable for now, until speech dispatcher properly parses them (version 0.8.9 or later)
            #elif c == '"':
            #  ssml += '&quot;'
            #elif c == "'":
            #  ssml += '&apos;'
            elif c == '<':
              ssml += '&lt;'
            elif c == '>':
              ssml += '&gt;'
            elif c == '&':
              ssml += '&amp;'
            else:
              ssml += c
        ssml += "</speak>"

        self._apply_acss(acss)
        self._debug_sd_values("Speaking '%s' " % ssml)
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
                            msg = "SPEECH DISPATCHER: Got mark %d:%d / %d-%d" % \
                                (context.currentOffset, context.currentEndOffset, \
                                 context.startOffset, context.endOffset)
                            debug.println(debug.LEVEL_INFO, msg, True)
                    else:
                        context.currentOffset = context.startOffset
                        context.currentEndOffset = None
                elif t == speechserver.SayAllContext.COMPLETED:
                    context.currentOffset = context.endOffset
                    context.currentEndOffset = None
                GLib.idle_add(orca_callback, context, t)
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
        msg = 'SPEECH DISPATCHER: Rate set to %d' % rate
        debug.println(debug.LEVEL_INFO, msg, True)
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
        msg = 'SPEECH DISPATCHER: Pitch set to %d' % pitch
        debug.println(debug.LEVEL_INFO, msg, True)
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
        msg = 'SPEECH DISPATCHER: Volume set to %d' % volume
        debug.println(debug.LEVEL_INFO, msg, True)
        self.speak(decrease and messages.SPEECH_SOFTER \
                   or messages.SPEECH_LOUDER, acss=acss)

    def getInfo(self):
        return [self._SERVER_NAMES.get(self._id, self._id), self._id]

    def getVoiceFamilies(self):
        # Always offer the configured default voice with a language
        # set according to the current locale.
        from locale import getlocale, LC_MESSAGES
        locale = getlocale(LC_MESSAGES)[0]
        if locale is None or locale == 'C':
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
            except:
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
        #if interrupt:
        #    self._cancel()

        # "We will not interrupt a key echo in progress." (Said the comment in
        # speech.py where these next two lines used to live. But the code here
        # suggests we haven't been doing anything with the lastKeyEchoTime in
        # years. TODO - JD: Dig into this and if it's truly useless, kill it.)
        if self._lastKeyEchoTime:
            interrupt = interrupt and (time.time() - self._lastKeyEchoTime) > 0.5

        if text:
            self._speak(text, acss)

    def speakUtterances(self, utteranceList, acss=None, interrupt=True):
        #if interrupt:
        #    self._cancel()
        for utterance in utteranceList:
            if utterance:
                self._speak(utterance, acss)

    def sayAll(self, utteranceIterator, progressCallback):
        GLib.idle_add(self._say_all, utteranceIterator, progressCallback)

    def speakCharacter(self, character, acss=None):
        self._apply_acss(acss)
        name = chnames.getCharacterName(character)
        if not name or name == character:
            self._send_command(self._client.char, character)
            return

        if orca_state.activeScript:
            name = orca_state.activeScript.\
                utilities.adjustForPronunciation(name)
        self.speak(name, acss)

    def speakKeyEvent(self, event, acss=None):
        event_string = event.getKeyName()
        if orca_state.activeScript:
            event_string = orca_state.activeScript.\
                utilities.adjustForPronunciation(event_string)

        lockingStateString = event.getLockingStateString()
        event_string = "%s %s" % (event_string, lockingStateString)
        self.speak(event_string, acss=acss)
        self._lastKeyEchoTime = time.time()

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

