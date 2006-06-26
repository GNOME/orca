# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

"""Provides a SpeechServer factory for gnome-speech drivers."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import bonobo

import atspi
import debug
import punctuation_settings
import settings
import speech
import speechserver

from acss import ACSS
from chnames import chnames
from punctuation_settings import punctuation

from orca_i18n import _           # for gettext support

atspi.ORBit.load_typelib('GNOME_Speech')
import GNOME.Speech, GNOME__POA.Speech

class _SayAll:
    def __init__(self, iterator, context, id, progressCallback):
        self.utteranceIterator   = iterator
        self.currentContext      = context
        self.idForCurrentContext = id
        self.progressCallback    = progressCallback

class _Speaker(GNOME__POA.Speech.SpeechCallback):
    """Implements gnome-speech's SpeechCallback class.  The gnome-speech
    server only allows one speech callback to be registered with a speaker
    and there's no way to unregister it.  So...we need to handle stuff
    like that on our own.  This class handles this for us and also delegates
    all calls to the 'real' gnome speech speaker.
    """

    def __init__(self, gnome_speaker):
        self.gnome_speaker = gnome_speaker
        if settings.enableSpeechCallbacks:
            gnome_speaker.registerSpeechCallback(self._this())
        self.__callbacks = []

    def registerCallback(self, callback):
        self.__callbacks.append(callback)

    def deregisterCallback(self, callback):
        self.__callbacks.remove(callback)

    def notify(self, type, id, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.

        Arguments:
        - type:   one of GNOME.Speech.speech_callback_speech_started,
                         GNOME.Speech.speech_callback_speech_progress,
                         GNOME.Speech.speech_callback_speech_ended
        - id:     the id of the utterance (returned by say)
        - offset: the character offset into the utterance (for progress)
        """
        for callback in self.__callbacks:
            callback.notify(type, id, offset)

    def say(self, text):
        return self.gnome_speaker.say(text)

    def stop(self):
        self.gnome_speaker.stop()

    def getSupportedParameters(self):
        return self.gnome_speaker.getSupportedParameters()

    def getParameterValue(self, name):
        return self.gnome_speaker.getParameterValue(name)

    def setParameterValue(self, name, value):
        return self.gnome_speaker.setParameterValue(name, value)

    def unref(self):
        try:
            self.gnome_speaker.unref()
        except:
            pass

class SpeechServer(speechserver.SpeechServer):
    """Provides SpeechServer implementation for gnome-speech."""

    # Dictionary of known running servers.  The key is the iid and the
    # value is the SpeechServer instance.  We do this to enforce a
    # singleton instance of any given server.
    #
    __activeServers = {}

    def __activateDriver(iid):
        driver = bonobo.activation.activate_from_id(iid,
                                                    0,
                                                    False)
        driver = driver._narrow(GNOME.Speech.SynthesisDriver)
        isInitialized = driver.isInitialized()
        if not isInitialized:
            isInitialized = driver.driverInit()
        if not isInitialized:
            try:
                driver.unref()
            except:
                pass
            driver = None
        return driver

    __activateDriver = staticmethod(__activateDriver)

    def __createServer(iid):
        server = None

        if SpeechServer.__activeServers.has_key(iid):
            server = SpeechServer.__activeServers[iid]
        else:
            driver = SpeechServer.__activateDriver(iid)
            if driver:
                server = SpeechServer(driver, iid)
                SpeechServer.__activeServers[iid] = server

        return server

    __createServer = staticmethod(__createServer)

    def getFactoryName():
        """Returns a localized name describing this factory."""
        return _("GNOME Speech Services")

    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServers():
        """Gets available speech servers as a list.  The caller
        is responsible for calling the shutdown() method of each
        speech server returned.
        """

        # Get a list of all the drivers on the system and find out how many
        # of them work.
        #
        knownServers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        for server in knownServers:
            if not SpeechServer.__activeServers.has_key(server.iid):
                try:
                    SpeechServer.__createServer(server.iid)
                except:
                    debug.printException(debug.LEVEL_WARNING)

        return SpeechServer.__activeServers.values()

    getSpeechServers = staticmethod(getSpeechServers)

    def getSpeechServer(info=None):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.getInfo() for more info.
        """

        if info and SpeechServer.__activeServers.has_key(info[1]):
            return SpeechServer.__activeServers[info[1]]

        server = None

        gservers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        if len(gservers) == 0:
            return None

        gserver = None

        # All this logic is to attempt to fall back to a working
        # driver if the desired one cannot be found or is not
        # not working.
        #
        if not info:
            gserver = gservers[0]
        else:
            for s in gservers:
                if s.iid == info[1]:
                    gserver = s
                    break

        if not gserver:
            return None

        try:
            server = SpeechServer.__createServer(gserver.iid)
        except:
            for s in gservers:
                try:
                    server = SpeechServer.__createServer(s.iid)
                except:
                    debug.printException(debug.LEVEL_WARNING)
                    pass

        return server

    getSpeechServer = staticmethod(getSpeechServer)

    def shutdownActiveServers():
        """Cleans up and shuts down this factory.
        """
        for key in SpeechServer.__activeServers.keys():
            server = SpeechServer.__activeServers[key]
            server.shutdown()

    shutdownActiveServers = staticmethod(shutdownActiveServers)

    def __init__(self, driver, iid):
        speechserver.SpeechServer.__init__(self)
        self.__speakers   = {}
        self.__pitchInfo  = {}
        self.__rateInfo   = {}
        self.__volumeInfo = {}
        self.__driver = driver
        self.__driverName = driver.driverName
        self.__iid = iid
        self.__sayAll = None
        self.__isSpeaking = False

    def __getRate(self, speaker):
        """Gets the voice-independent ACSS rate value of a voice."""

        if not self.__rateInfo.has_key(speaker):
            return 50.0

        [minRate, averageRate, maxRate] = self.__rateInfo[speaker]
        rate = speaker.getParameterValue("rate")
        if rate < averageRate:
            return 50.0 * (rate - minRate) / (averageRate - minRate)
        elif rate > averageRate:
            return 50.0 \
                   + (50.0 * (rate - averageRate) / (maxRate - averageRate))
        else:
            return 50.0

    def __setRate(self, speaker, acssRate):
        """Determines the voice-specific rate setting for the
        voice-independent ACSS rate value.
        """

        if not self.__rateInfo.has_key(speaker):
            return

        [minRate, averageRate, maxRate] = self.__rateInfo[speaker]
        if acssRate < 50.0:
            rate = minRate + acssRate * (averageRate - minRate) / 50.0
        elif acssRate > 50.0:
            rate = averageRate \
                   + (acssRate - 50.0) * (maxRate - averageRate) / 50.0
        else:
            rate = averageRate

        speaker.setParameterValue("rate", rate)

    def __getPitch(self, speaker):
        """Gets the voice-specific pitch setting for the
           voice-independent ACSS pitch value.

        Returns the voice-specific pitch setting.
        """

        if not self.__pitchInfo.has_key(speaker):
            return 5.0

        [minPitch, averagePitch, maxPitch] = self.__pitchInfo[speaker]
        pitch = speaker.getParameterValue("pitch")
        if pitch < averagePitch:
            return 5.0 * (pitch - minPitch) / (averagePitch - minPitch)
        elif pitch > averagePitch:
            return 5.0 \
                   + (5.0 * (pitch - averagePitch) / (maxPitch - averagePitch))
        else:
            return 5.0

    def __setPitch(self, speaker, acssPitch):
        """Determines the voice-specific pitch setting for the
        voice-independent ACSS pitch value.
        """

        if not self.__pitchInfo.has_key(speaker):
            return

        [minPitch, averagePitch, maxPitch] = self.__pitchInfo[speaker]
        if acssPitch < 5.0:
            pitch = minPitch + acssPitch * (averagePitch - minPitch) / 5.0
        elif acssPitch > 5.0:
            pitch = averagePitch \
                    + (acssPitch - 5.0) * (maxPitch - averagePitch) / 5.0
        else:
            pitch = averagePitch

        speaker.setParameterValue("pitch", pitch)

    def __setVolume(self, speaker, acssGain):
        """Determines the voice-specific rate setting for the
        voice-independent ACSS rate value.
        """

        if not self.__volumeInfo.has_key(speaker):
            return

        [minVolume, averageVolume, maxVolume] = self.__volumeInfo[speaker]
        volume = minVolume + acssGain * (maxVolume - minVolume) / 10.0

        speaker.setParameterValue("volume", volume)

    def __getSpeaker(self, acss=None):

        voices = settings.voices
        defaultACSS = voices[settings.DEFAULT_VOICE]

        if not acss:
            acss = defaultACSS

        if self.__speakers.has_key(acss.name()):
            return self.__speakers[acss.name()]

        # Create a new voice for all unique ACSS's we see.
        #
        familyName = None
        if acss.has_key(ACSS.FAMILY):
            family = acss[ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]
        elif defaultACSS.has_key(ACSS.FAMILY):
            family = defaultACSS[ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]

        voices = self.__driver.getAllVoices()
        found = False
        for voice in voices:
            if (not familyName) or (voice.name == familyName):
                found = True
                break

        if not found:
            if len(voices) == 0:
                return None
            else:
                voice = voices[0]

        s = self.__driver.createSpeaker(voice)
        speaker = _Speaker(s._narrow(GNOME.Speech.Speaker))
        speaker.registerCallback(self)

        parameters = speaker.getSupportedParameters()
        for parameter in parameters:
            if parameter.name == "rate":
                self.__rateInfo[speaker] = \
                    [parameter.min, parameter.current, parameter.max]
            elif parameter.name == "pitch":
                self.__pitchInfo[speaker] = \
                    [parameter.min, parameter.current, parameter.max]
            elif parameter.name == "volume":
                self.__volumeInfo[speaker] = \
                    [parameter.min, parameter.current, parameter.max]

        if acss.has_key(ACSS.RATE):
            self.__setRate(speaker, acss[ACSS.RATE])

        if acss.has_key(ACSS.AVERAGE_PITCH):
            self.__setPitch(speaker, acss[ACSS.AVERAGE_PITCH])

        if acss.has_key(ACSS.GAIN):
            self.__setVolume(speaker, acss[ACSS.GAIN])

        self.__speakers[acss.name()] = speaker

        return speaker

    def notify(self, type, id, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.  This is for internal use only.

        Arguments:
        - type:   one of GNOME.Speech.speech_callback_speech_started,
                         GNOME.Speech.speech_callback_speech_progress,
                         GNOME.Speech.speech_callback_speech_ended
        - id:     the id of the utterance (returned by say)
        - offset: the character offset into the utterance (for progress)
        """
        if self.__sayAll:
            if self.__sayAll.idForCurrentContext == id:
                context = self.__sayAll.currentContext
                if type == GNOME.Speech.speech_callback_speech_started:
                    self.__isSpeaking = True
                    context.currentOffset = context.startOffset
                    self.__sayAll.progressCallback(
                        self.__sayAll.currentContext,
                        speechserver.SayAllContext.PROGRESS)
                elif type == GNOME.Speech.speech_callback_speech_progress:
                    self.__isSpeaking = True
                    context.currentOffset = context.startOffset + offset
                    self.__sayAll.progressCallback(
                        self.__sayAll.currentContext,
                        speechserver.SayAllContext.PROGRESS)
                elif type == GNOME.Speech.speech_callback_speech_ended:
                    try:
                        [self.__sayAll.currentContext, acss] = \
                            self.__sayAll.utteranceIterator.next()
                        debug.println(debug.LEVEL_INFO,
                                      "SPEECH OUTPUT: '" \
                                      + self.__sayAll.currentContext.utterance\
                                      + "'")
                        self.__sayAll.idForCurrentContext = self.__speak(
                            self.__sayAll.currentContext.utterance,
                            acss)
                    except StopIteration:
                        self.__isSpeaking = False
                        context.currentOffset = context.endOffset
                        self.__sayAll.progressCallback(
                            self.__sayAll.currentContext,
                            speechserver.SayAllContext.COMPLETED)
                        self.__sayAll = None
        elif type == GNOME.Speech.speech_callback_speech_started:
            self.__isSpeaking = True
        elif type == GNOME.Speech.speech_callback_speech_progress:
            self.__isSpeaking = True
        elif type == GNOME.Speech.speech_callback_speech_ended:
            self.__isSpeaking = False

    def getInfo(self):
        """Returns [driverName, serverId]
        """
        return [self.__driverName, self.__iid]

    def getVoiceFamilies(self):
        """Returns a list of speechserver.VoiceFamily instances
        representing all the voice families known by the speech server.
        """

        families = []
        try:
            for voice in self.__driver.getAllVoices():
                props = {
                    speechserver.VoiceFamily.NAME   : voice.name,
                    speechserver.VoiceFamily.LOCALE : voice.language
                }
                families.append(speechserver.VoiceFamily(props))
        except:
            debug.printException(debug.LEVEL_SEVERE)
            pass

        return families

    def queueText(self, text="", acss=None):
        """Adds the text to the queue.

        Arguments:
        - text: text to be spoken
        - acss: acss.ACSS instance; if None,
                the default voice settings will be used.
                Otherwise, the acss settings will be
                used to augment/override the default
                voice settings.

        Output is produced by the next call to speak.
        """
        self.speak(text, acss)

    def queueTone(self, pitch=440, duration=50):
        """Adds a tone to the queue.

        Output is produced by the next call to speak.
        """
        pass

    def queueSilence(self, duration=50):
        """Adds silence to the queue.

        Output is produced by the next call to speak.
        """
        pass

    def speakCharacter(self, character, acss=None):
        """Speaks a single character immediately.

        Arguments:
        - character: text to be spoken
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        """
        self.speak(character, acss)

    def speakUtterances(self, list, acss=None, interrupt=True):
        """Speaks the given list of utterances immediately.

        Arguments:
        - list:      list of strings to be spoken
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        - interrupt: if True, stop any speech currently in progress.
        """
        i = 0
        for text in list:
            if len(text) != 0:
                self.speak(text, acss, interrupt and (i == 0))
            i += 1

    def __addVerbalizedPunctuation(self, oldText):
        """Depending upon the users verbalized punctuation setting, 
        adjust punctuation symbols in the given text to their pronounced 
        equivalents. The pronounced text will either replace the 
        punctuation symbol or be inserted before it. In the latter case, 
        this is to retain spoken prosity.

        If we are moving around by single characters, then always speak 
        the punctuation. We try to detect this by looking for just a 
        single character being spoken.

        Arguments:
        - oldText:      text to be parsed for punctuation.

        Returns a text string with the punctuation symbols adjusted accordingly.
        """

        ## Replace ellipses (both manual and unicode) with "dot dot dot"
        ##
        oldText = oldText.replace("...", _(" dot dot dot"), 1)
        oldText = oldText.replace("\342\200\246",  _(" dot dot dot"), 1)

        style = settings.verbalizePunctuationStyle
        if len(oldText) != 1 and style == settings.PUNCTUATION_STYLE_NONE:
            return oldText

        newText = ''
        for i in range(0, len(oldText)):
            try:
                level, action = punctuation[oldText[i]]
                if len(oldText) == 1 or style <= level:
                    newText += " " + chnames[oldText[i]]
                    if action == punctuation_settings.PUNCTUATION_INSERT:
                        newText += oldText[i] + " "
                else:
                    newText += oldText[i]
            except:
                try:
                    newText += chnames[oldText[i].lower()]
                except:
                    newText += oldText[i]

        return newText

    def __speak(self, text=None, acss=None, interrupt=True):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text:      optional text to add to the queue before speaking
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        - interrupt: if True, stops any speech in progress before
                     speaking the text

        Returns an id of the thing being spoken or -1 if nothing is to
        be spoken.
        """

        speaker = self.__getSpeaker(acss)
        if acss and not acss.has_key(ACSS.RATE):
            voices = settings.voices
            defaultACSS = voices[settings.DEFAULT_VOICE]
            if defaultACSS.has_key(ACSS.RATE):
                self.__setRate(speaker, defaultACSS[ACSS.RATE])

        if not text:
            if interrupt:
                speech.stop()
            return -1

        text = self.__addVerbalizedPunctuation(text)

        try:
            # [[[TODO: WDW - back this stop out for now.  The problem is
            # that we end up clipping too much speech, especially in the
            # case where we want to speak the contents of a popup before
            # speaking the object with focus.]]]
            #
            #if interrupt:
            #    speaker.stop()
            self.__lastText = [text, acss]
            self.__isSpeaking = True
            return speaker.say(text)
        except:
            # On failure, remember what we said, reset our connection to the
            # speech synthesis driver, and try to say it again.
            #
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE, "Restarting speech...")
            self.reset()
            return -1

    def speak(self, text=None, acss=None, interrupt=True):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text:      optional text to add to the queue before speaking
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        - interrupt: if True, stops any speech in progress before
                     speaking the text
        """
        if self.__sayAll:
            self.stop()

        self.__speak(text, acss, interrupt)

    def isSpeaking(self):
        """"Returns True if the system is currently speaking."""
        return self.__isSpeaking

    def sayAll(self, utteranceIterator, progressCallback):
        """Iterates through the given utteranceIterator, speaking
        each utterance one at a time.

        Arguments:
        - utteranceIterator: iterator/generator whose next() function
                             returns a new string to be spoken
        - progressCallback:  called as progress is made
        """
        try:
            [context, acss] = utteranceIterator.next()
            debug.println(debug.LEVEL_INFO,
                          "SPEECH OUTPUT: '" + context.utterance + "'")
            self.__sayAll = _SayAll(utteranceIterator,
                                    context,
                                    self.__speak(context.utterance, acss),
                                    progressCallback)
        except StopIteration:
            pass

    def increaseSpeechPitch(self, step=0.5):
        """Increases the speech pitch for the default voice.

        Arguments:
        - step: the pitch step increment.
        """

        # [[[TODO: richb - this is a hack for now.  Need to take min/max
        # values in account, plus also need to take into account that
        # different engines provide different pitch ranges.]]]

        voices = settings.voices
        acss = voices[settings.DEFAULT_VOICE]
        speaker = self.__getSpeaker(acss)

        pitchDelta = settings.speechPitchDelta

        try:
            pitch = min(10, self.__getPitch(speaker) + pitchDelta)
            acss[ACSS.AVERAGE_PITCH] = pitch
            self.__setPitch(speaker, pitch)
            debug.println(debug.LEVEL_CONFIGURATION,
                          "speech.increaseSpeechPitch: pitch is now " \
                          " %d" % pitch)
            self.speak(_("higher."))
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def decreaseSpeechPitch(self, step=0.5):
        """Decreases the speech pitch for the default voice.

        Arguments:
        - step: the pitch step decrement.
        """

        # [[[TODO: WDW - this is a hack for now.  Need to take min/max
        # values in account, plus also need to take into account that
        # different engines provide different rate ranges.]]]

        voices = settings.voices
        acss = voices[settings.DEFAULT_VOICE]
        speaker = self.__getSpeaker(acss)

        pitchDelta = settings.speechPitchDelta

        try:
            pitch = max(1, self.__getPitch(speaker) - pitchDelta)
            acss[ACSS.AVERAGE_PITCH] = pitch
            self.__setPitch(speaker, pitch)
            debug.println(debug.LEVEL_CONFIGURATION,
                          "speech.decreaseSpeechPitch: pitch is now " \
                          " %d" % pitch)
            self.speak(_("lower."))
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def increaseSpeechRate(self, step=5):
        """Increases the speech rate.

        [[[TODO: WDW - this is a hack for now.  Need to take min/max
        values in account, plus also need to take into account that
        different engines provide different rate ranges.]]]
        """

        voices = settings.voices
        acss = voices[settings.DEFAULT_VOICE]
        speaker = self.__getSpeaker(acss)

        rateDelta = settings.speechRateDelta

        try:
            rate = min(100, self.__getRate(speaker) + rateDelta)
            acss[ACSS.RATE] = rate
            self.__setRate(speaker, rate)
            debug.println(debug.LEVEL_CONFIGURATION,
                          "speech.increaseSpeechRate: rate is now " \
                          " %d" % rate)
            self.speak(_("faster."))
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def decreaseSpeechRate(self, step=5):
        """Decreases the rate of speech for the given ACSS.  If
        acssName is None, the rate decrease will be applied to all
        known ACSSs.

        [[[TODO: WDW - this is a hack for now.  Need to take min/max
        values in account, plus also need to take into account that
        different engines provide different rate ranges.]]]

        Arguments:
        -acssName: the ACSS whose speech rate should be decreased
        """

        voices = settings.voices
        acss = voices[settings.DEFAULT_VOICE]
        speaker = self.__getSpeaker(acss)

        rateDelta = settings.speechRateDelta

        try:
            rate = max(1, self.__getRate(speaker) - rateDelta)
            acss[ACSS.RATE] = rate
            self.__setRate(speaker, rate)
            debug.println(debug.LEVEL_CONFIGURATION,
                          "speech.decreaseSpeechRate: rate is now " \
                          " %d" % rate)
            self.speak(_("slower."))
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        if self.__sayAll:
            self.__sayAll.progressCallback(
                self.__sayAll.currentContext,
                speechserver.SayAllContext.INTERRUPTED)
            self.__sayAll = None
        for name in self.__speakers.keys():
            try:
                self.__speakers[name].stop()
            except:
                pass
        self.__isSpeaking = False

    def shutdown(self):
        """Shuts down the speech engine."""
        if SpeechServer.__activeServers.has_key(self.__iid):
            for speaker in self.__speakers.values():
                speaker.stop()
                speaker.unref()
            self.__speakers = {}
            try:
                self.__driver.unref()
            except:
                pass
            self.__driver = None
            del SpeechServer.__activeServers[self.__iid]

    def reset(self, text=None, acss=None):
        """Resets the speech engine."""

        speakers = self.__speakers
        self.shutdown()

        servers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        for server in servers:
            if server.iid == self.__iid:
                try:
                    self.__driver = self.__activateDriver(self.__iid)
                    self.__speakers = {}
                    for name in speakers.keys():
                        self.__getSpeaker(speakers[name])
                    if text:
                        self.speak(text, acss)
                    break
                except:
                    debug.printException(debug.LEVEL_SEVERE)
                    self.__driver = None
                    pass
