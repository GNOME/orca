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

try:
    import speechd
except:
    _speechd_available = False
else:    
    _speechd_available = True
    try:
        from speechd import CallbackType
    except ImportError:
        _speechd_version_ok = False
    else:
        _speechd_version_ok = True

class SpeechServer(speechserver.SpeechServer):
    # See the parent class for documentation.

    _active_servers = {}
    
    DEFAULT_SERVER_ID = 'default'
    
    # Translators: "Default Synthesizer" will appear in the list of available
    # speech engines as a special item.  It refers to the default engine
    # configured within the speech subsystem.  Apart from this item, the user
    # will have a chance to select a particular speech engine by its real
    # name, such as Festival, IBMTTS, etc.
    #
    _SERVER_NAMES = {DEFAULT_SERVER_ID: _("Default Synthesizer")}
    
    KEY_NAMES = {
        '_':     'underscore',
        'space': 'space',
        '"':     'double-quote',
        }


    def getFactoryName():
        # Translators: this is the name of a speech synthesis system
        # called "Speech Dispatcher".
        #
        return _("Speech Dispatcher")
    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServers():
        default = SpeechServer._getSpeechServer(SpeechServer.DEFAULT_SERVER_ID)
        servers = [default]
        for module in default.list_output_modules():
            servers.append(SpeechServer._getSpeechServer(module))
        return servers
    getSpeechServers = staticmethod(getSpeechServers)

    def _getSpeechServer(cls, id):
        """Return an active server for given id.

        Attempt to create the server if it doesn't exist yet.  Returns None
        when it is not possible to create the server.
        
        """
        if not cls._active_servers.has_key(id):
            cls(id)
        # Don't return the instance, unless it is succesfully added
        # to `_active_Servers'.
        return cls._active_servers.get(id)
    _getSpeechServer = classmethod(_getSpeechServer)

    def getSpeechServer(info=None):
        if info is not None:
            id = info[1]
        else:
            id = SpeechServer.DEFAULT_SERVER_ID
        return SpeechServer._getSpeechServer(id)
    getSpeechServer = staticmethod(getSpeechServer)

    def shutdownActiveServers():
        for server in SpeechServer._active_servers.values():
            server.shutdown()
    shutdownActiveServers = staticmethod(shutdownActiveServers)

    # *** Instance methods ***

    def __init__(self, id):
        self._id = id
        self._acss_manipulators = (
            (ACSS.RATE, self._set_rate),
            (ACSS.AVERAGE_PITCH, self._set_pitch),
            (ACSS.GAIN, self._set_volume),
            (ACSS.FAMILY, self._set_family),
            )
        if not _speechd_available:
            debug.println(debug.LEVEL_WARNING,
                          "Speech Dispatcher interface not installed.")
            return
        if not _speechd_version_ok:
            debug.println(debug.LEVEL_WARNING,
                        "Speech Dispatcher version 0.6.2 or later is required.")
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
           #speechd.CallbackType.INDEX_MARK:speechserver.SayAllContext.PROGRESS,
            }
        # Translators: This string will appear in the list of
        # available voices for the current speech engine.  %s will be
        # replaced by the name of the current speech engine, such as
        # "Festival default voice" or "IBMTTS default voice".  It
        # refers to the default voice configured for given speech
        # engine within the speech subsystem.  Apart from this item,
        # the list will contain the names of all available "real"
        # voices provided by the speech engine.
        #
        self._default_voice_name = _("%s default voice") % id
        
        try:
            self._init()
        except Exception, e:
            debug.println(debug.LEVEL_WARNING,
                          "Speech Dispatcher service failed to connect: %s" % e)
        else:
            self.__class__._active_servers[id] = self

    def _init(self):
        self._client = client = speechd.SSIPClient('Orca', component=self._id)
        if self._id != self.DEFAULT_SERVER_ID:
            client.set_output_module(self._id)
        self._current_voice_properties = {}
        mode = self._PUNCTUATION_MODE_MAP[settings.verbalizePunctuationStyle]
        client.set_punctuation(mode)
        
    def _send_command(self, command, *args, **kwargs):
        if hasattr(speechd, 'SSIPCommunicationError'):
            try:
                return command(*args, **kwargs)
            except speechd.SSIPCommunicationError:
                debug.println(debug.LEVEL_CONFIGURATION,
                              "Speech Dispatcher connection lost. "
                              "Trying to reconnect.")
                self.reset()
                return command(*args, **kwargs)
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

    def _set_family(self, acss_family):
        locale = acss_family[VoiceFamily.LOCALE]
        if locale:
            lang = locale.split('_')[0]
            if lang and len(lang) == 2:
                self._send_command(self._client.set_language, lang)
        try:
            # This command is not available with older SD versions.
            set_synthesis_voice = self._client.set_synthesis_voice
        except AttributeError:
            pass
        else:
            name = acss_family[VoiceFamily.NAME]
            if name != self._default_voice_name:
                self._send_command(set_synthesis_voice, name)
            
    def _apply_acss(self, acss):
        current = self._current_voice_properties
        for property, method in self._acss_manipulators:
            value = acss.get(property)
            if value is not None and current.get(property) != value:
                method(value)
                current[property] = value

    def _speak(self, text, acss, **kwargs):
        if acss is not None:
            self._apply_acss(acss)
        self._send_command(self._client.speak, text, **kwargs)

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
                t = self._CALLBACK_TYPE_MAP[type]
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
                        event_types=self._CALLBACK_TYPE_MAP.keys())
        return False # to indicate, that we don't want to be called again.

    def _cancel(self):
        self._send_command(self._client.cancel)

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
        return [self._SERVER_NAMES.get(self._id, self._id), self._id]

    def getVoiceFamilies(self):
        # Always offer the configured default voice with a language
        # set according to the current locale.
        from locale import getlocale, LC_MESSAGES
        locale = getlocale(LC_MESSAGES)[0]
        if locale is None or locale == 'C':
            lang = None
        else:
            lang = locale.split('_')[0]
        voices = ((self._default_voice_name, lang, None),)
        try:
            # This command is not available with older SD versions.
            list_synthesis_voices = self._client.list_synthesis_voices
        except AttributeError:
            pass
        else:
            voices += self._send_command(list_synthesis_voices)
        families = [VoiceFamily({VoiceFamily.NAME: name,
                                 #VoiceFamily.GENDER: VoiceFamily.MALE,
                                 VoiceFamily.LOCALE: lang})
                    for name, lang, dialect in voices]
        return families

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
        self._send_command(self._client.char, character)

    def speakKeyEvent(self, event_string, type):
        if type == orca.KeyEventType.PRINTABLE:
            # We currently only handle printable characters by Speech
            # Dispatcher's KEY command.  For other keys, such as Ctrl, Shift
            # etc. we prefer Orca's verbalization.
            if event_string.decode("UTF-8").isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
            else:
                voice = settings.voices[settings.DEFAULT_VOICE]
            key = self.KEY_NAMES.get(event_string, event_string)
            if voice is not None:
                self._apply_acss(voice)
            self._send_command(self._client.key, key)
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
        del self.__class__._active_servers[self._id]

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

