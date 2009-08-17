# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Provides a SpeechServer factory for gnome-speech drivers."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import logging
log = logging.getLogger("speech")

import gobject
import Queue
import threading
import time

import bonobo
import ORBit

# Init the ORB if we need to.  With AT-SPI/CORBA, we depend upon the pyatspi
# implementation to init the ORB for us.  [[[WDW: With AT-SPI/D-Bus, we need
# to do it ourselves.  I'm not sure how to ask ORBit itself if it's been
# init'ed yet, so I do so indirectly by looking for an attribute of pyatspi.
# This attribute has been set if AT-SPI/CORBA is in use and it not set if
# AT-SPI/D-Bus is in use.]]]
#
try:
    import pyatspi
    poa = pyatspi.Accessibility__POA
except AttributeError:
    orb = ORBit.CORBA.ORB_init()

import chnames
import debug
import orca
import orca_state
import punctuation_settings
import settings
import speech
import speechserver

from acss import ACSS

from orca_i18n import _           # for gettext support

ORBit.load_typelib('GNOME_Speech')
import GNOME.Speech, GNOME__POA.Speech

def _matchLanguage(desired, actual):
    """Compares a desired language to an actual language and returns
    a numerical value representing the degree of match.  The expected
    language format is a string similar to the following, where the
    delimiter can be '-' '_' or '.':

      de-DE (German for Germany)
      en-US (English as used in the United States)

    Additional extensions for variants or dialects are allowed as well.

    The return value is one of the following:

      0 - no match at all
      1 - some match
      2 - exact match
    """

    if desired == actual:
        return 2
    if not desired or not actual:
        return 0

    # Break the strings into arrays where the delimiters are
    # - or _.  Also lowercase everything to help with string 
    # compares.
    #
    desired = desired.lower().replace("-","_").replace(".","_").split("_")
    actual = actual.lower().replace("-","_").replace(".","_").split("_")

    matchCount = 0
    for i in range(0, min(len(desired), len(actual))):
        if desired[i] == actual[i]:
            matchCount += 1
        else:
            break

    if matchCount == len(desired):
        return 2
    elif matchCount:
        return 1
    else:
        return 0
        
class _SayAll:
    def __init__(self, iterator, context, utteranceId, progressCallback):
        self.utteranceIterator   = iterator
        self.currentContext      = context
        self.idForCurrentContext = utteranceId
        self.progressCallback    = progressCallback

class _Speaker(GNOME__POA.Speech.SpeechCallback):
    """Implements gnome-speech's SpeechCallback class.  The gnome-speech
    server only allows one speech callback to be registered with a speaker
    and there's no way to unregister it.  So...we need to handle stuff
    like that on our own.  This class handles this for us and also delegates
    all calls to the 'real' gnome speech speaker.
    """

    def __init__(self, gnome_speaker, voice):

        # We know what we are doing here, so tell pylint not to flag
        # the self._this() method call as an error.  The disable-msg is
        # localized to just this method.
        #
        # pylint: disable-msg=E1101

        self.gnome_speaker = gnome_speaker
        if settings.enableSpeechCallbacks:
            gnome_speaker.registerSpeechCallback(self._this())
        self.__callbacks = []
        self.voiceInfo = [voice.name, voice.language, voice.gender]

    def registerCallback(self, callback):
        self.__callbacks.append(callback)

    def deregisterCallback(self, callback):
        self.__callbacks.remove(callback)

    def notify(self, progressType, utteranceId, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.

        Arguments:
        - progressType:  one of GNOME.Speech.speech_callback_speech_started,
                         GNOME.Speech.speech_callback_speech_progress,
                         GNOME.Speech.speech_callback_speech_ended
        - utteranceId:   the id of the utterance (returned by say)
        - offset:        the character offset into the utterance (for progress)
        """
        for callback in self.__callbacks:
            callback.notify(progressType, utteranceId, offset)

    def say(self, text):
        if isinstance(text, unicode):
            text = text.encode("UTF-8")
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

        # We know what we are doing here, so tell pylint not to flag
        # the _narrow method call as a warning.  The disable-msg is
        # localized to just this method.
        #
        # pylint: disable-msg=W0212

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

        if iid in SpeechServer.__activeServers:
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
            if server.iid not in SpeechServer.__activeServers:
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

        if info and info[1] in SpeechServer.__activeServers:
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

        server = None
        try:
            server = SpeechServer.__createServer(gserver.iid)
        except:
            debug.printException(debug.LEVEL_WARNING)

        if not server:
            for s in gservers:
                try:
                    server = SpeechServer.__createServer(s.iid)
                    if server:
                        break
                except:
                    debug.printException(debug.LEVEL_WARNING)

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
        self.__speakers      = {}
        self.__pitchInfo     = {}
        self.__rateInfo      = {}
        self.__volumeInfo    = {}
        self.__driver        = driver
        self.__driverName    = driver.driverName
        self.__iid           = iid
        self.__sayAll        = None
        self.__isSpeaking    = False
        self.__eventQueue    = Queue.Queue(0)
        self.__gidleId       = 0
        self.__gidleLock     = threading.Lock()
        self.__lastResetTime = 0
        self.__lastText      = None
        self.textCharIndices = []

    def __getRate(self, speaker):
        """Gets the voice-independent ACSS rate value of a voice."""

        if speaker not in self.__rateInfo:
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

        if speaker not in self.__rateInfo:
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

        if speaker not in self.__pitchInfo:
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

        if speaker not in self.__pitchInfo:
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

        if speaker not in self.__volumeInfo:
            return

        [minVolume, averageVolume, maxVolume] = self.__volumeInfo[speaker]
        volume = minVolume + acssGain * (maxVolume - minVolume) / 10.0

        speaker.setParameterValue("volume", volume)

    def __getSpeaker(self, acss=None):

        voices = settings.voices
        defaultACSS = voices[settings.DEFAULT_VOICE]

        if not acss:
            acss = defaultACSS

        if acss.name() in self.__speakers:
            return self.__speakers[acss.name()]

        # Search for matching languages first, as that is the most
        # important thing.  We also try to look for the desired language
        # first, but then fall back to the default language.
        #
        languages = []
        try:
            if ACSS.FAMILY in acss:
                family = acss[ACSS.FAMILY]
                languages = [family[speechserver.VoiceFamily.LOCALE]]
            elif ACSS.FAMILY in defaultACSS:
                family = defaultACSS[ACSS.FAMILY]
                languages = [family[speechserver.VoiceFamily.LOCALE]]
        except:
            pass

        # [[[TODO: WDW - I'm using an array of languages here because
        # it will give us the opportunity to provide a match for
        # gnome-speech driver implementations that do not designate
        # languages using the combination of ISO 639-1 and 3166-1
        # language_region strings (e.g., they use 'english' instead of
        # "en_US").  Thus, we could detect the default language is
        # "en_US" and just automatically append "english" and such to
        # the list to allow us to accomodate these kind of
        # variants.]]]
        #
        if len(languages) == 0:
            import locale
            language, encoding = locale.getdefaultlocale()
            languages = [language]

        voices = self.__driver.getAllVoices()
        foundVoices = []
        for voice in voices:
            match = 0
            for language in languages:
                match = max(match, _matchLanguage(voice.language, language))

            # Exact matches get put at the beginning, inexact get added to
            # the end.
            #
            if match == 2:
                foundVoices.insert(0, voice)
            elif match:
                foundVoices.append(voice)

        # If we didn't find any matches, well...punt.
        #
        if len(foundVoices):
            voices = foundVoices
        else:
            voices = self.__driver.getAllVoices()

        # Now search for a matching family name.
        #
        familyName = None
        if ACSS.FAMILY in acss:
            family = acss[ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]
        elif ACSS.FAMILY in defaultACSS:
            family = defaultACSS[ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]

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

        # We know what we are doing here, so tell pylint not to flag
        # the _narrow method call as a warning.  The disable-msg is
        # localized to just this method.
        #
        # pylint: disable-msg=W0212

        speaker = _Speaker(s._narrow(GNOME.Speech.Speaker), voice)

        # Turn off punctuation.  We do this because we want to handle
        # spoken punctuation on our own.  Only do so if "punctuation mode"
        # is available (see # bug #528797).
        #
        try:
            parameters = speaker.getSupportedParameters()
            for parameter in parameters:
                if parameter.name == "punctuation mode":
                    speaker.setParameterValue("punctuation mode", 0.0)
                    break
        except:
            pass

        speaker.registerCallback(self)

        # Hack - see if we have created a new speaker for a new voice
        # for the engine.  If so, save away the min/current/max parameters.
        # Otherwise, use the ones we saved away.  The problem is that
        # each time we get the parameters, the current one reflects the
        # current value.  We only want to save the value the first time
        # because at that time, the current value is the default value.
        #
        saveParameters = True
        for existingSpeaker in self.__speakers.values():
            if existingSpeaker.voiceInfo == speaker.voiceInfo:
                try:
                    self.__rateInfo[speaker] = \
                        self.__rateInfo[existingSpeaker]
                except:
                    pass
                try:
                    self.__pitchInfo[speaker] = \
                        self.__pitchInfo[existingSpeaker]
                except:
                    pass
                try:
                    self.__volumeInfo[speaker] = \
                        self.__volumeInfo[existingSpeaker]
                except:
                    pass
                saveParameters = False
                break

        if saveParameters:
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

        if ACSS.RATE in acss:
            self.__setRate(speaker, acss[ACSS.RATE])

        if ACSS.AVERAGE_PITCH in acss:
            self.__setPitch(speaker, acss[ACSS.AVERAGE_PITCH])

        if ACSS.GAIN in acss:
            self.__setVolume(speaker, acss[ACSS.GAIN])

        self.__speakers[acss.name()] = speaker

        return speaker

    def __idleHandler(self):
        """Called by the gidle thread when there is something to do.
        The goal is to try to do all AT-SPI interactions on the gidle
        thread as a means to help prevent hangs."""

        # Added in the notify method below.
        #
        # thisId   = the id of the utterance we sent to gnome-speech
        # thisType = the type of progress we're getting
        # offset   = character offset into the utterance
        #
        (thisId, thisType, offset) = self.__eventQueue.get()

        offset = self.__adjustTextCharIndex(offset)

        if self.__sayAll:
            if self.__sayAll.idForCurrentContext == thisId:
                context = self.__sayAll.currentContext
                if thisType == GNOME.Speech.speech_callback_speech_started:
                    context.currentOffset = context.startOffset
                    self.__sayAll.progressCallback(
                        self.__sayAll.currentContext,
                        speechserver.SayAllContext.PROGRESS)
                elif thisType == GNOME.Speech.speech_callback_speech_progress:
                    context.currentOffset = context.startOffset + offset
                    self.__sayAll.progressCallback(
                        self.__sayAll.currentContext,
                        speechserver.SayAllContext.PROGRESS)
                elif thisType == GNOME.Speech.speech_callback_speech_ended:
                    try:
                        while True:
                            [self.__sayAll.currentContext, acss] = \
                                self.__sayAll.utteranceIterator.next()
                            utterance = self.__sayAll.currentContext.utterance
                            logLine = "SPEECH OUTPUT: '" + utterance + "'"
                            debug.println(debug.LEVEL_INFO, logLine)
                            log.info(logLine)
                            if utterance and len(utterance)\
                               and not utterance.isspace():
                                self.__sayAll.idForCurrentContext = \
                                    self.__speak(utterance, acss)
                                break
                    except StopIteration:
                        self.__isSpeaking = False
                        context.currentOffset = context.endOffset
                        self.__sayAll.progressCallback(
                            self.__sayAll.currentContext,
                            speechserver.SayAllContext.COMPLETED)
                        self.__sayAll = None
                    except:
                        # This is here to deal with the situation where speech
                        # might have stopped and __sayAll was set to None.
                        # If we don't handle those cases, Say All can stop
                        # working.
                        #
                        pass

        rerun = True

        self.__gidleLock.acquire()
        if self.__eventQueue.empty():
            self.__gidleId = 0
            rerun = False # destroy and don't call again
        self.__gidleLock.release()

        return rerun

    def notify(self, progressType, utteranceId, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.  This is for internal use only.

        Arguments:
        - progressType:  one of GNOME.Speech.speech_callback_speech_started,
                         GNOME.Speech.speech_callback_speech_progress,
                         GNOME.Speech.speech_callback_speech_ended
        - utteranceId:   the id of the utterance (returned by say)
        - offset:        the character offset into the utterance (for progress)
        """

        if progressType == GNOME.Speech.speech_callback_speech_started:
            self.__isSpeaking = True
        elif progressType == GNOME.Speech.speech_callback_speech_progress:
            self.__isSpeaking = True
        elif (progressType == GNOME.Speech.speech_callback_speech_ended) \
            and (not self.__sayAll):
            self.__isSpeaking = False

        if self.__sayAll:
            self.__gidleLock.acquire()
            self.__eventQueue.put((utteranceId, progressType, offset))
            if not self.__gidleId:
                if settings.gilSleepTime:
                    time.sleep(settings.gilSleepTime)
                self.__gidleId = gobject.idle_add(self.__idleHandler)
            self.__gidleLock.release()

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
        chname = chnames.getCharacterName(character)
        if orca_state.activeScript and orca_state.usePronunciationDictionary:
            chname = orca_state.activeScript.adjustForPronunciation(chname)
        self.speak(chname, acss)

    def speakUtterances(self, utterances, acss=None, interrupt=True):
        """Speaks the given list of utterances immediately.

        Arguments:
        - utterances: list of strings to be spoken
        - acss:       acss.ACSS instance; if None,
                      the default voice settings will be used.
                      Otherwise, the acss settings will be
                      used to augment/override the default
                      voice settings.
        - interrupt: if True, stop any speech currently in progress.
        """
        i = 0
        for text in utterances:
            if len(text):
                self.speak(text, acss, interrupt and (i == 0))
            i += 1

    def __adjustTextCharIndex(self, offset):
        """Get the original character index into the text string (before
        the string was adjusted for verbalized punctuation.

        Arguments:
        - offset: character offset into text string

        Returns the equivalent character index into the original text string.
        """

        equivalentIndex = 0
        for i in range(0, len(self.textCharIndices)):
            equivalentIndex = i
            if self.textCharIndices[i] >= offset:
                break

        return equivalentIndex

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

        # Translators: we replace the ellipses (both manual and UTF-8)
        # with a spoken string.  The extra space you see at the beginning
        # is because we need the speech synthesis engine to speak the
        # new string well.  For example, "Open..." turns into
        # "Open dot dot dot".
        #
        oldText = oldText.replace("...", _(" dot dot dot"), 1)
        oldText = oldText.replace("\342\200\246",  _(" dot dot dot"), 1)
        oldText = oldText.decode("UTF-8")

        ## Don't speak newlines unless the user is moving through text
        ## using a right or left arrow key.
        ##
        removeNewLines = True
        if orca_state.lastInputEvent and \
               "event_string" in orca_state.lastInputEvent.__dict__:
            lastKey = orca_state.lastInputEvent.event_string
            if lastKey == "Left" or lastKey == "Right":
                removeNewLines = False

        if removeNewLines:
            oldText = oldText.replace("\n", "", 1)

        # Used to keep a list of character offsets into the new text string,
        # once it has been converted to use verbalized punctuation, one for
        # each character in the original string.
        #
        self.textCharIndices = []
        style = settings.verbalizePunctuationStyle
        newText = ''
        for i in range(0, len(oldText)):
            self.textCharIndices.append(len(newText))
            try:
                level, action = \
                    punctuation_settings.getPunctuationInfo(oldText[i])

                # Special case for punctuation in text like filenames or URL's:
                #
                isPrev = isNext = isSpecial = False
                if i > 0:
                    isPrev = not oldText[i - 1].isspace()
                if i < (len(oldText) - 1):
                    isNext = not oldText[i + 1].isspace()

                # If this is a period and there is a non-space character
                # on either side of it, then always speak it.
                #
                isSpecial = isPrev and isNext and (oldText[i] == ".")

                # If this is a dash and the users punctuation level is not
                # NONE and the previous character is a white space character,
                # and the next character is a dollar sign or a digit, then
                # always speak it. See bug #392939.
                #
                prevCharMatches = nextCharMatches = False
                if orca_state.activeScript:
                    currencySymbols = \
                        orca_state.activeScript.getUnicodeCurrencySymbols()
                if i == 0:
                    prevCharMatches = True
                if i > 0:
                    prevCharMatches = oldText[i - 1].isspace()
                if i < (len(oldText) - 1):
                    nextCharMatches = (oldText[i + 1].isdigit() or \
                                       oldText[i + 1] in currencySymbols)

                if oldText[i] == "-" and \
                   style != settings.PUNCTUATION_STYLE_NONE and \
                   prevCharMatches and nextCharMatches:
                    if isPrev:
                        newText += " "
                    # Translators: this is to be sent to a speech synthesis
                    # engine to prefix a negative number (e.g., "-56" turns
                    # into "minus 56".  We cannot always be sure of the type
                    # of the number (floating point, integer, mixed with other
                    # odd characters, etc.), so we need to unfortunately
                    # build up the utterance in this manner.
                    #
                    newText += _("minus")
                elif (len(oldText) == 1) or isSpecial or (style <= level):
                    if isPrev:
                        newText += " "
                    newText += chnames.getCharacterName(oldText[i])
                    if (action == punctuation_settings.PUNCTUATION_INSERT) \
                        and not isNext:
                        newText += oldText[i].encode("UTF-8")
                    if isNext:
                        newText += " "
                else:
                    newText += oldText[i].encode("UTF-8")
            except:
                if (len(oldText) == 1):
                    newText += chnames.getCharacterName(oldText[i])
                else:
                    newText += oldText[i].encode("UTF-8")

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

        # If the user has speech turned off, just return.
        #
        if not settings.enableSpeech:
            return -1

        speaker = self.__getSpeaker(acss)
        if acss and ACSS.RATE not in acss:
            voices = settings.voices
            defaultACSS = voices[settings.DEFAULT_VOICE]
            if ACSS.RATE in defaultACSS:
                self.__setRate(speaker, defaultACSS[ACSS.RATE])

        if not text:
            if interrupt:
                speech.stop()
            return -1

        text = self.__addVerbalizedPunctuation(text)

        # Replace no break space characters with plain spaces since some
        # synthesizers cannot handle them.  See bug #591734.
        #
        text = text.decode("UTF-8").replace(u'\u00a0', ' ').encode("UTF-8")

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

        if not acss and text and text.decode("UTF-8").isupper():
            try:
                acss = \
                    orca_state.activeScript.voices[settings.UPPERCASE_VOICE]
            except:
                pass

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
            logLine = "SPEECH OUTPUT: '" + context.utterance + "'"
            debug.println(debug.LEVEL_INFO, logLine)
            log.info(logLine)
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
            # Translators: this is a short string saying that the speech
            # synthesis engine is now speaking in a higher pitch.
            #
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
            # Translators: this is a short string saying that the speech
            # synthesis engine is now speaking in a lower pitch.
            #
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
            # Translators: this is a short string saying that the speech
            # synthesis engine is now speaking at a faster rate (words
            # per minute).
            #
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
            # Translators: this is a short string saying that the speech
            # synthesis engine is now speaking at a slower rate (words
            # per minute).
            #
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
        if self.__iid in SpeechServer.__activeServers:
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

        # We might get into a vicious loop of resetting speech, so
        # we will abort if we see this happening.
        #
        if (time.time() - self.__lastResetTime) < 20:
            debug.println(debug.LEVEL_SEVERE,
                          "Something looks wrong with speech.  Aborting.")
            debug.printStack(debug.LEVEL_ALL)
            orca.die(50)
        else:
            self.__lastResetTime = time.time()

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
