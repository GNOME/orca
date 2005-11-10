# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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

"""Provides a SpeechServer factory for gnome-speech drivers.
"""

import chnames
import core
import debug
import settings
import speechserver

from chnames import chnames
from core import ORBit, bonobo

from orca_i18n import _           # for gettext support

ORBit.load_typelib('GNOME_Speech')
import GNOME.Speech, GNOME__POA.Speech


def getSpeechServers(names=None):
    """Factory method to return a list of SpeechServer instances
    that are backed by working gnome-speech servers on the system,
    initializing and activating the drivers for the servers as
    necessary.

    Arguments:
    - names: a list indicating the names of gnome-speech servers we
             care about.  If names is None, all known servers are
             returned.
    """
    
    # Get a list of all the drivers on the system and find out how many
    # of them work.
    #
    servers = bonobo.activation.query(
        "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

    speechServers = []

    for server in servers:
        try:
            driver = bonobo.activation.activate_from_id(server.iid,
                                                        0,
                                                        False)
            driver = driver._narrow(GNOME.Speech.SynthesisDriver)
            if (names is None) \
               or (names.count(driver.driverName)):
                isInitialized = driver.isInitialized()
                if not isInitialized:
                    isInitialized = driver.driverInit()
                if isInitialized:
                    speechServers.append(SpeechServer(driver))
        except:
            debug.printException(debug.LEVEL_OFF)
            continue

    return speechServers


class SpeechCallback(GNOME__POA.Speech.SpeechCallback):
    """Implements gnome-speech's SpeechCallback class.  The speech
    module uses only one global callback object which is used for
    tasks such as sayAll mode.

    SpeechCallback objects contain a speech ended method, as well as the
    current speaking position.

    Here's an idea of how to use this.  I'm just leaving this here to
    remind me what to do when callbacks are re-added...
    
    # [[[TODO: WDW - the register succeeds on JDS/Suse but fails
    # on Fedora.  Dunno why, but we'll just limp along for now.
    # BTW, the error is on the freetts-synthesis-driver side:
    # Jul 30, 2005 4:36:09 AM com.sun.corba.se.impl.ior.IORImpl getProfile
    # WARNING: "IOP00511201: (INV_OBJREF) IOR must have at least one IIOP profile"
    # org.omg.CORBA.INV_OBJREF:   vmcid: SUN  minor code: 1201  completed: No
    #
    try:
        s.registerSpeechCallback(_cb._this())
    except:
        debug.printException(debug.LEVEL_SEVERE)
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Will not use speech callbacks.")    
    """

    def __init__(self):
        self.onSpeechEnded = None
        self.position = 0

    def notify(self, type, id, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.

        Arguments:
        - type:
        - id:
        - offset:
        """
        
        # Call our speech ended Python function if we have one
        #
        if type == GNOME.Speech.speech_callback_speech_ended:
            if self.onSpeechEnded:
                self.onSpeechEnded()

        # Update our speaking position if we get a speech progress
        # notification.  [[[TODO: WDW - need to be able use this to
        # update the magnifier's region of interest.]]]
        #
        elif type == GNOME.Speech.speech_callback_speech_progress:
            self.position = offset


class SpeechServer(speechserver.SpeechServer):
    """Provides SpeechServer implementation for gnome-speech."""

    def __init__(self, driver, initialSettings=None):
        speechserver.SpeechServer.__init__(self)
        self.__speakers = {}
        self.driver = driver
        self.driverName = driver.driverName
        
    def setACSS(self, name, acss):
        """Adds an aural cascading style sheet to this server using
        the given name as its identifier.  Returns 'True' on success,
        meaning this ACSS will work with this SpeechServer.

        Arguments:
        - name: the identifier, to be used in calls to say something
        - acss: the aural cascading style sheet to use
        """

        # In this implementation for gnome-speech, we create a new
        # speaker for each ACSS we're given and index the speaker
        # by the ACSS name.  The speakers will be held in the __speakers
        # dictionary.
        #
        try:
            family = acss[speechserver.ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]
            
            voices = self.driver.getAllVoices()
            found = False
            for voice in voices:
                if voice.name == familyName:
                    found = True
                    break

            if not found:
                return False

            s = self.driver.createSpeaker(voice)
            speaker = s._narrow(GNOME.Speech.Speaker)

            rate = acss[speechserver.ACSS.RATE]
            if rate:
                speaker.setParameterValue("rate", rate)
            else:
                rate = speaker.getParameterValue ("rate")
                acss[speechserver.ACSS.RATE] = rate

            pitch = acss[speechserver.ACSS.AVERAGE_PITCH]
            if pitch:
                speaker.setParameterValue("pitch", pitch)
            else:
                pitch = speaker.getParameterValue ("pitch")
                acss[speechserver.ACSS.AVERAGE_PITCH] = pitch
                
            volume = acss[speechserver.ACSS.GAIN]
            if volume:
                speaker.setParameterValue("volume", volume)
            else:
                volume = speaker.getParameterValue ("volume")
                acss[speechserver.ACSS.GAIN] = volume

            speechserver.SpeechServer.setACSS(self, name, acss)
            self.__speakers[name] = speaker

            return True
        except:
            debug.printException(debug.LEVEL_SEVERE)
            return False

    def getInfo(self):
        """Returns [driverName, synthesizerName]
        """
        return [self.driver.driverName, self.driver.synthesizerName]

    def getVoiceFamilies(self):
        """Returns a list of speechserver.VoiceFamily instances
        representing all the voice families known by the speech server.
        """

        families = []
        try:
            for voice in self.driver.getAllVoices():
                props = {
                    speechserver.VoiceFamily.NAME   : voice.name,
                    speechserver.VoiceFamily.LOCALE : voice.language
                }
                families.append(speechserver.VoiceFamily(props))
        except:
            debug.printException(debug.LEVEL_SEVERE)
            pass

        return families

    def queueText(self, text="", acssName="default"):
        """Adds the text to the queue.

        Arguments:
        - text:     text to be spoken
        - acssName: name of a speechserver.ACSS instance registered
                    via a call to setACSS
                    
        Output is produced by the next call to speak.
        """
        self.speak(text, acssName)

    def queueCharacter(self, character, acssName="default"):
        """Adds a single character to the queue of things to be spoken.

        Output is produced by the next call to speak.
        """
        self.speak(character, acssName)
        
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

    def speakUtterances(self, list, acssName="default"):
        """Speaks the given list of utterances immediately.

        Arguments:
        - list:     list of strings to be spoken
        - acssName: name of a speechserver.ACSS instance registered
                    via a call to setACSS
        """

        for text in list:
            self.speak(text, acssName)            

    def __getSpeaker(self, acssName):
        if self.__speakers.has_key(acssName):
            return self.__speakers[acssName]
        elif acssName == "default":
            voices = self.driver.getAllVoices()
            props = {
                speechserver.VoiceFamily.NAME   : voices[0].name,
                speechserver.VoiceFamily.LOCALE : voices[0].language
            }
            family = speechserver.VoiceFamily(props)
            acss = speechserver.ACSS({speechserver.ACSS.FAMILY : family})
            self.setACSS("default", acss)
        return self.__speakers["default"]

    def speak(self, text=None, acssName="default"):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text: optional text to add to the queue before speaking
        """

        speaker = self.__getSpeaker(acssName)
        
        # If the text to speak is a single character, see if we have a
        # customized character pronunciation
        #
        if len(text) == 1:
            try:
                text = chnames[text.lower()]
            except:
                debug.printException(debug.LEVEL_FINEST)
                pass
        else:
            text = text.replace("...", _(" dot dot dot"), 1)
        
        # Send the text to the GNOME Speech speaker
        #
        debug.println(debug.LEVEL_INFO, "SPEECH OUTPUT: '" + text + "'")

        try:
            #speaker.stop()
            self.__lastText = [text, acssName]
            return speaker.say(text)
        except:
            # On failure, remember what we said, reset our connection to the
            # speech synthesis driver, and try to say it again.
            #
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE, "Restarting speech...")
            self.__reset()

    def increaseSpeechRate(self, acssName=None):
        """Increases the rate of speech for the given ACSS.  If
        acssName is None, the rate increase will be applied to all
        known ACSSs.

        [[[TODO: WDW - this is a hack for now.  Need to take min/max
        values in account, plus also need to take into account that
        different engines provide different rate ranges.]]]
    
        Arguments:
        -acssName: the ACSS whose speech rate should be increased
        """

        rateDelta = settings.getSetting("speechRateDelta", 25)
        if acssName:
            speaker = self.__getSpeaker(acssName)
            try:
                rate = speaker.getParameterValue("rate") + rateDelta
                if speaker.setParameterValue("rate", rate):
                    self.__acss[acssName][speechserver.ACSS.RATE] = rate
                    debug.println(debug.LEVEL_CONFIGURATION,
                                  "speech.increaseSpeechRate: rate is now " \
                                  " %d for %s" % (rate, acssName))
                    return
            except:
                debug.printException(debug.LEVEL_SEVERE)
        else:
            for name in self.__speakers.keys():
                self.increaseSpeechRate(name)

        self.stop()
        self.speak(_("faster."))
        
    def decreaseSpeechRate(self, acssName=None):
        """Decreases the rate of speech for the given ACSS.  If
        acssName is None, the rate decrease will be applied to all
        known ACSSs.

        [[[TODO: WDW - this is a hack for now.  Need to take min/max
        values in account, plus also need to take into account that
        different engines provide different rate ranges.]]]
    
        Arguments:
        -acssName: the ACSS whose speech rate should be decreased
        """

        rateDelta = settings.getSetting("speechRateDelta", 25)
        if acssName:
            speaker = self.__getSpeaker(acssName)
            try:
                rate = speaker.getParameterValue("rate") - rateDelta
                if speaker.setParameterValue("rate", rate):
                    self.__acss[acssName][speechserver.ACSS.RATE] = rate
                    debug.println(debug.LEVEL_CONFIGURATION,
                                  "speech.decreaseSpeechRate: rate is now " \
                                  " %d for %s" % (rate, acssName))
                    return
            except:
                debug.printException(debug.LEVEL_SEVERE)
        else:
            for name in self.__speakers.keys():
                self.decreaseSpeechRate(name)

        self.stop()
        self.speak(_("slower."))

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        for name in self.__speakers.keys():
            try:
                self.__speakers[name].stop()
            except:
                pass

    def shutdown(self):
        """Shuts down the speech engine."""

        for name in self.__speakers.keys():
            try:
                self.__speakers[name].unref()
            except:
                pass
        self.__speakers = {}
        
        try:
            self.driver.unref()
        except:
            pass

        self.driver = None
    
    def __reset(self, text=None, acssName=None):
        """Resets the speech engine."""
        
        speakers = self.__speakers
        self.shutdown()
        
        servers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        for server in servers:
            try:
                driver = bonobo.activation.activate_from_id(server.iid,
                                                            0,
                                                            False)
                driver = driver._narrow(GNOME.Speech.SynthesisDriver)
                if driver.driverName == self.driverName:
                    self.driver = driver
                    if not driver.isInitialized():
                        isInitialized = driver.driverInit()
                    self.__speakers = {}
                    for name in speakers.keys():
                        self.setACSS(name, speakers[name][1])
                    if text and acssName:
                        self.speak(text, acssName)
                    break
            except:
                debug.printException(debug.LEVEL_SEVERE)
