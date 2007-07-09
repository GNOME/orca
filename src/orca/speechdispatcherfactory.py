# Copyright 2006, 2007 Brailcom, o.p.s.
#
# Author: Tomas Cerha <cerha@brailcom.org>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides an Orca speech server for Speech Dispatcher backend.

NOTE: THIS IS EXPERIMENTAL ONLY AND IS NOT A SUPPORTED COMPONENT OF ORCA.
"""

__id__        = "$Id: $"
__version__   = "$Revision: $"
__date__      = "$Date: 2007-02-28 $"
__author__    = "Tomas Cerha <cerha@brailcom.org>"
__copyright__ = "Copyright (c) 2006, 2007 Brailcom, o.p.s."
__license__   = "LGPL"

import threading
import gobject
import time
import re

import debug
import speechserver
import settings
import orca
from acss import ACSS
from orca_i18n import _
from speechserver import VoiceFamily

class SpeechDispatcherVersionError(Exception):
    """Incompatible version of the Speech Dispatcher Python Interface."""

class SpeechServer(speechserver.SpeechServer):
    # See the parent class for documentation.

    _activeServers = {}

    KEY_NAMES = {
        '_':     'underscore',
        'space': 'space',
        '"':     'double-quote',
        }

    def getFactoryName():
        return _("Speech Dispatcher")
    getFactoryName = staticmethod(getFactoryName)

    def _getActiveServers(cls):
        if not cls._activeServers:
            import locale
            lang = locale.getlocale(locale.LC_MESSAGES)[0]
            if lang and lang != 'C':
                lang = lang.split('_')[0]
            else:
                lang = None
            cls('default', language=lang)
        return cls._activeServers
    _getActiveServers = classmethod(_getActiveServers)

    def getSpeechServers():
        return SpeechServer._getActiveServers().values()
    getSpeechServers = staticmethod(getSpeechServers)

    def getSpeechServer(info=None):
        servers = SpeechServer._getActiveServers()
        if info is not None:
            return servers.get(info[1])
        elif servers:
            return servers.values()[0]
        else:
            return None
    getSpeechServer = staticmethod(getSpeechServer)

    def shutdownActiveServers():
        for server in SpeechServer.getSpeechServers():
            server.shutdown()
    shutdownActiveServers = staticmethod(shutdownActiveServers)

    # *** Instance methods ***

    def __init__(self, id, language=None):
        self._id = id
        self._default_language = language
        self._acss_manipulators = (
            (ACSS.RATE, self._set_rate),
            (ACSS.AVERAGE_PITCH, self._set_pitch),
            (ACSS.GAIN, self._set_volume),
            )
        try:
            self._init()
        except ImportError:
            debug.println(debug.LEVEL_WARNING,
                          "Speech Dispatcher interface not installed.")
        except SpeechDispatcherVersionError:
            debug.println(debug.LEVEL_WARNING,
                       "Speech Dispatcher version 0.6.2 or later is required.")
        except:
            debug.println(debug.LEVEL_WARNING,
                       "Speech Dispatcher service failed to connect.")
        else:
            self.__class__._activeServers[self.getInfo()[1]] = self

    def _init(self):
        import speechd
        try:
            from speechd import CallbackType
        except ImportError:
            raise SpeechDispatcherVersionError()
        self._client = client = speechd.SSIPClient('Orca', component=self._id)
        if self._default_language is not None:
            client.set_language(self._default_language)
        self._current_voice_properties = {}
        self._apply_acss(settings.voices[settings.DEFAULT_VOICE])
        punctuation_mode = {
            settings.PUNCTUATION_STYLE_ALL:  speechd.PunctuationMode.ALL,
            settings.PUNCTUATION_STYLE_MOST: speechd.PunctuationMode.SOME,
            settings.PUNCTUATION_STYLE_SOME: speechd.PunctuationMode.SOME,
            settings.PUNCTUATION_STYLE_NONE: speechd.PunctuationMode.NONE,
            }[settings.verbalizePunctuationStyle]
        client.set_punctuation(punctuation_mode)
        self._callback_type_map = {
            CallbackType.BEGIN: speechserver.SayAllContext.PROGRESS,
            CallbackType.CANCEL: speechserver.SayAllContext.INTERRUPTED,
            CallbackType.END: speechserver.SayAllContext.COMPLETED,
            #CallbackType.INDEX_MARK:speechserver.SayAllContext.PROGRESS,
            }

    def _set_rate(self, acss_rate):
        rate = int(2 * max(0, min(99, acss_rate)) - 98)
        self._client.set_rate(rate)

    def _set_pitch(self, acss_pitch):
        pitch = int(20 * max(0, min(9, acss_pitch)) - 90)
        self._client.set_pitch(pitch)

    def _set_volume(self, acss_volume):
        volume = int(15 * max(0, min(9, acss_volume)) - 35)
        self._client.set_volume(volume)

    def _apply_acss(self, acss):
        current = self._current_voice_properties
        for property, method in self._acss_manipulators:
            value = acss.get(property)
            if value is not None and current.get(property) != value:
                method(value)
                current[property] = value

    def _speak(self, text, acss, **kwargs):
        self._apply_acss(acss)
        self._client.speak(text, **kwargs)

    def _say_all(self, iterator, orca_callback):
        """Process another sayAll chunk.

        Called by the gidle thread.

        """
        try:
            context, acss = iterator.next()
        except StopIteration:
            pass
        else:
            def callback(type, index_mark=None):
                # This callback is called in Speech Dispatcher listener thread.
                # No subsequent Speech Dispatcher interaction is allowed here,
                # so we pass the calls to the gidle thread.
                t = self._callback_type_map[type]
                if t == speechserver.SayAllContext.PROGRESS:
                    if index_mark:
                        context.currentOffset = int(index_mark)
                    else:
                        context.currentOffset = context.startOffset
                elif t == speechserver.SayAllContext.COMPLETED:
                    context.currentOffset = context.endOffset
                gobject.idle_add(orca_callback, context, t)
                if t == speechserver.SayAllContext.COMPLETED:
                    gobject.idle_add(self._say_all, iterator, orca_callback)
            self._speak(context.utterance, acss, callback=callback,
                        event_types=self._callback_type_map.keys())
        return False # to indicate, that we don't want to be called again.

    def _cancel(self):
        self._client.cancel()

    def _change_default_speech_rate(self, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = settings.speechRateDelta * (decrease and -1 or +1)
        rate = acss[ACSS.RATE]
        acss[ACSS.RATE] = max(0, min(99, rate + delta))
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech rate is now %d" % rate)
        # Translators: This string announces speech rate change.
        self.speak(decrease and _("slower.") or _("faster."), acss=acss)

    def _change_default_speech_pitch(self, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = settings.speechPitchDelta * (decrease and -1 or +1)
        pitch = acss[ACSS.AVERAGE_PITCH]
        acss[ACSS.AVERAGE_PITCH] = max(0, min(9, pitch + delta))
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech pitch is now %d" % pitch)
        # Translators: This string announces speech pitch change.
        self.speak(decrease and _("lower.") or _("higher."), acss=acss)

    def getInfo(self):
        return ["Speech Dispatcher Server (%s)" % self._id, self._id]

    def getVoiceFamilies(self):
        # Only one voice is currently supported -- the Speech Dispatcher
        # configured default voice.
        return (VoiceFamily({VoiceFamily.NAME:
                             _("Speech Dispatcher configured default voice"),
                             VoiceFamily.GENDER: VoiceFamily.MALE,
                             VoiceFamily.LOCALE: self._default_language}),)

    def speak(self, text=None, acss=None, interrupt=True):
        #if interrupt:
        #    self._cancel()
        if text:
            self._speak(text, acss)

    def queueText(self, text="", acss=None):
        if text:
            self._speak(text, acss)

    def speakUtterances(self, list, acss=None, interrupt=True):
        #if interrupt:
        #    self._cancel()
        for utterance in list:
            if utterance:
                self._speak(utterance, acss)

    def sayAll(self, utteranceIterator, progressCallback):
        gobject.idle_add(self._say_all, utteranceIterator, progressCallback)

    def speakCharacter(self, character, acss=None):
        self._client.char(character)

    def speakKeyEvent(self, event_string, type):
        if type == orca.KeyEventType.PRINTABLE:
            # We currently only handle printable characters by Speech
            # Dispatcher's KEY command.  For other keys, such as Ctrl, Shift
            # etc. we prefer Orca's verbalization.
            if event_string.decode("UTF-8").isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
            else:
                voice = settings.voices[settings.DEFAULT_VOICE]
            self._apply_acss(voice)
            self._client.key(self.KEY_NAMES.get(event_string, event_string))
        else:
            return super(SpeechServer, self).speakKeyEvent(event_string, type)

    def increaseSpeechRate(self, step=5):
        self._change_default_speech_rate()

    def decreaseSpeechRate(self, step=5):
        self._change_default_speech_rate(decrease=True)

    def increaseSpeechPitch(self, step=0.5):
        self._change_default_speech_pitch()

    def decreaseSpeechPitch(self, step=0.5):
        self._change_default_speech_pitch(decrease=True)

    def stop(self):
        self._cancel()

    def shutdown(self):
        self._client.close()
        del self.__class__._activeServers[self.getInfo()[1]]

    def reset(self, text=None, acss=None):
        self._cancel()
        self._client.close()
        self._init()
