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

"""Provides an Orca speech server for Speech Dispatcher backend.

NOTE: THIS IS EXPERIMENTAL ONLY AND IS NOT A SUPPORTED COMPONENT OF ORCA.
"""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__author__    = "Tomas Cerha <cerha@brailcom.org>"
__copyright__ = "Copyright (c) 2006-2008 Brailcom, o.p.s."
__license__   = "LGPL"

from gi.repository import GObject
import re

from . import chnames
from . import debug
from . import speechserver
from . import settings
from . import orca_state
from . import punctuation_settings
from .acss import ACSS
from .orca_i18n import _

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

PUNCTUATION = re.compile('[^\w\s]', re.UNICODE)
ELLIPSIS = re.compile('(\342\200\246|\.\.\.\s*)')

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
        ' ':     'space',
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
        servers = []
        default = SpeechServer._getSpeechServer(SpeechServer.DEFAULT_SERVER_ID)
        if default is not None:
            servers.append(default)
            for module in default.list_output_modules():
                servers.append(SpeechServer._getSpeechServer(module))
        return servers
    getSpeechServers = staticmethod(getSpeechServers)

    def _getSpeechServer(cls, serverId):
        """Return an active server for given id.

        Attempt to create the server if it doesn't exist yet.  Returns None
        when it is not possible to create the server.
        
        """
        if serverId not in cls._active_servers:
            cls(serverId)
        # Don't return the instance, unless it is succesfully added
        # to `_active_Servers'.
        return cls._active_servers.get(serverId)
    _getSpeechServer = classmethod(_getSpeechServer)

    def getSpeechServer(info=None):
        if info is not None:
            thisId = info[1]
        else:
            thisId = SpeechServer.DEFAULT_SERVER_ID
        return SpeechServer._getSpeechServer(thisId)
    getSpeechServer = staticmethod(getSpeechServer)

    def shutdownActiveServers():
        for server in list(SpeechServer._active_servers.values()):
            server.shutdown()
    shutdownActiveServers = staticmethod(shutdownActiveServers)

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
        try:
            serverId = serverId.encode("UTF-8")
        except UnicodeDecodeError:
            pass

        self._default_voice_name = _("%s default voice") % serverId
        
        try:
            self._init()
        except:
            debug.println(debug.LEVEL_WARNING,
                          "Speech Dispatcher service failed to connect:")
            debug.printException(debug.LEVEL_WARNING)
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

    def updatePunctuationLevel(self):
        """ Punctuation level changed, inform this speechServer. """
        mode = self._PUNCTUATION_MODE_MAP[settings.verbalizePunctuationStyle]
        self._client.set_punctuation(mode)

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
        familyLocale = acss_family.get(speechserver.VoiceFamily.LOCALE)
        if not familyLocale:
            import locale
            familyLocale, encoding = locale.getdefaultlocale()
        if familyLocale:
            lang = familyLocale.split('_')[0]
            if lang and len(lang) == 2:
                self._send_command(self._client.set_language, str(lang))
        try:
            # This command is not available with older SD versions.
            set_synthesis_voice = self._client.set_synthesis_voice
        except AttributeError:
            pass
        else:
            name = acss_family.get(speechserver.VoiceFamily.NAME)
            if isinstance(name, unicode):
                name = name.encode('UTF-8')
            if name != self._default_voice_name:
                self._send_command(set_synthesis_voice, name)
            
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
            elif acss_property == ACSS.FAMILY and current.get(acss_property) \
                    and acss == settings.voices[settings.DEFAULT_VOICE]:
                # We need to explicitly reset (at least) the family.
                # See bgo#626072.
                #
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

        # Translators: we replace the ellipses (both manual and UTF-8)
        # with a spoken string.  The extra space you see at the beginning
        # is because we need the speech synthesis engine to speak the
        # new string well.  For example, "Open..." turns into
        # "Open dot dot dot".
        #
        spokenEllipsis = _(" dot dot dot") + " "
        newText = re.sub(ELLIPSIS, spokenEllipsis, oldText)
        try:
            newText = newText.decode("UTF-8")
        except UnicodeEncodeError:
            pass

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
            try:
                charName = charName.decode("UTF-8")
            except UnicodeEncodeError:
                pass
            newText = re.sub(symbol, charName, newText)

        if orca_state.activeScript:
            newText = orca_state.activeScript.utilities.adjustForDigits(newText)

        try:
            newText = newText.encode("UTF-8")
        except UnicodeDecodeError:
            pass

        return newText

    def _speak(self, text, acss, **kwargs):
        if isinstance(text, ACSS):
            text = ''
        text = self.__addVerbalizedPunctuation(text)
        if orca_state.activeScript and orca_state.usePronunciationDictionary:
            text = orca_state.activeScript.\
                utilities.adjustForPronunciation(text)

        # Replace no break space characters with plain spaces since some
        # synthesizers cannot handle them.  See bug #591734.
        #
        text = text.decode("UTF-8").replace(u'\u00a0', ' ').encode("UTF-8")

        # Replace newline followed by full stop, since
        # this seems to crash sd, see bgo#618334.
        #
        text = text.replace('\n.', '\n')

        self._apply_acss(acss)
        self._send_command(self._client.speak, text, **kwargs)

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
                        context.currentOffset = int(index_mark)
                    else:
                        context.currentOffset = context.startOffset
                elif t == speechserver.SayAllContext.COMPLETED:
                    context.currentOffset = context.endOffset
                GObject.idle_add(orca_callback, context, t)
                if t == speechserver.SayAllContext.COMPLETED:
                    GObject.idle_add(self._say_all, iterator, orca_callback)
            self._speak(context.utterance, acss, callback=callback,
                        event_types=list(self._CALLBACK_TYPE_MAP.keys()))
        return False # to indicate, that we don't want to be called again.

    def _cancel(self):
        self._send_command(self._client.cancel)

    def _change_default_speech_rate(self, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = settings.speechRateDelta * (decrease and -1 or +1)
        try:
            rate = acss[ACSS.RATE]
        except KeyError:
            rate = 50
        acss[ACSS.RATE] = max(0, min(99, rate + delta))
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech rate is now %d" % rate)
        # Translators: This string announces speech rate change.
        self.speak(decrease and _("slower.") or _("faster."), acss=acss)

    def _change_default_speech_pitch(self, decrease=False):
        acss = settings.voices[settings.DEFAULT_VOICE]
        delta = settings.speechPitchDelta * (decrease and -1 or +1)
        try:
            pitch = acss[ACSS.AVERAGE_PITCH]
        except KeyError:
            pitch = 5
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
        families = [speechserver.VoiceFamily({ \
              speechserver.VoiceFamily.NAME: name,
              #speechserver.VoiceFamily.GENDER: speechserver.VoiceFamily.MALE,
              speechserver.VoiceFamily.LOCALE: lang})
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

    def speakUtterances(self, utteranceList, acss=None, interrupt=True):
        #if interrupt:
        #    self._cancel()
        for utterance in utteranceList:
            if utterance:
                self._speak(utterance, acss)

    def sayAll(self, utteranceIterator, progressCallback):
        GObject.idle_add(self._say_all, utteranceIterator, progressCallback)

    def speakCharacter(self, character, acss=None):
        self._apply_acss(acss)
        if character == '\n':
            self._send_command(self._client.sound_icon, 'end-of-line')
            return

        name = chnames.getCharacterName(character)
        if not name:
            self._send_command(self._client.char, character)
            return

        if orca_state.activeScript and orca_state.usePronunciationDictionary:
            name = orca_state.activeScript.\
                utilities.adjustForPronunciation(name)
        self.speak(name, acss)

    def speakKeyEvent(self, event):
        if event.isPrintableKey():
            # We currently only handle printable characters by Speech
            # Dispatcher's KEY command.  For other keys, such as Ctrl, Shift
            # etc. we prefer Orca's verbalization.
            if event.event_string.decode("UTF-8").isupper():
                acss = settings.voices[settings.UPPERCASE_VOICE]
            else:
                acss = None
            key = self.KEY_NAMES.get(event.event_string, event.event_string)
            self._apply_acss(acss)
            self._send_command(self._client.key, key)
        else:
            return super(SpeechServer, self).speakKeyEvent(event)

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

