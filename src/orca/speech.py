# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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

from core import ORBit, bonobo
import sys

# Import user settings

import settings

# Import character pronunciations

from chnames import chnames

# Import gnome-speech definitions

ORBit.load_typelib ('GNOME_Speech')

import GNOME.Speech, GNOME__POA.Speech

# This function is used internall to the speech module only - It
# creates a GNOME Speech speaker based on a speech driver name and a
# voice name.  the voice name refers to a voice specified in the
# user's settings.py file.

def createSpeaker (driverName, voiceName):
    global drivers

    # Find the specified GNOME Speech driver

    found = False
    for driver in drivers:
        if driver.synthesizerName.find(driverName) >= 0:
            found = True
            break
    if not found:
        return None

    # This could probably just as easily be done with a better use of
    # getVoices

    voices = driver.getAllVoices ()
    found = False
    for voice in voices:
        if voice.name.find (voiceName) >= 0:
            found = True
            break
    if not found:
        return None
    return driver.createSpeaker (voice)

# Global list of active gnome-spech drivers

drivers = []

# Dictionary of speakers

speakers = {}

initialized = False

# The speech callback class - objects of this class implement
# gnome-speech's SpeechCallback class.  the speech module uses only
# one global callback object which is used for tasks such as say all
# mode
#
# SpeechCallback objects contain a speech ended method, as well as the
# current speaking position

class SpeechCallback (GNOME__POA.Speech.SpeechCallback):

    # SpeechCallback constructor

    def __init__ (self):
        self.onSpeechEnded = None
        self.position = 0

    # Notify is called by GNOME Speech when the GNOME Speech driver
    # generates a callback

    def notify (self, type, id, offset):

        # Call our speech ended Python function if we have one

        if type == GNOME.Speech.speech_callback_speech_ended:
            if self.onSpeechEnded:
                self.onSpeechEnded ()

        # Update our speaking position if we get a speech progress
        # notification

        elif type == GNOME.Speech.speech_callback_speech_progress:
            self.position = offset


# Global speech callback

cb = SpeechCallback ()

# Specifies whether the speech module is initialized

initialized = False

# Initialize the speech module

def init():
    global initialized
    global drivers
    global speakers
    global cb

    if initialized:
        return False

    # Get a list of all the drivers on the system

    servers = bonobo.activation.query ("repo_ids.has ('IDL:GNOME/Speech/SynthesisDriver:0.3')")

    # How many of them work?

    drivers = []
    for server in servers:
        try:
            driver = bonobo.activation.activate_from_id (server.iid)
        except:
            continue
            
        # Ensure what we have is a SynthesisDriver object - This
        # is needed for Java CORBA ORB interoperability

        driver = driver._narrow (GNOME.Speech.SynthesisDriver)
        isInitialized = driver.isInitialized ()

        # Only initialize the driver if someone else hasn't
        # initialized it already

        if not isInitialized:
            isInitialized = driver.driverInit ()
        if isInitialized:
            drivers.append (driver)

    # Create the speakers

    for voiceName in settings.voices.keys ():
        desc = settings.voices[voiceName]
        s = createSpeaker (desc[0], desc[1])
        if s is not None:
            s = s._narrow (GNOME.Speech.Speaker)
            s.setParameterValue ("rate", desc[2])
            s.setParameterValue ("pitch", desc[3])
            s.setParameterValue ("volume", desc[4])
            speakers[voiceName] = s
            s.registerSpeechCallback (cb._this())

    # If no speakers were defined, select the first voice of the first
    # working driver as the default

    if len(speakers) == 0 and len(drivers) > 0:
            voices = drivers[0].getAllVoices ()
            if len(voices) > 0:
                speakers["default"] = drivers[0].createSpeaker(voices[0])._narrow(GNOME.Speech.Speaker)
    initialized = True
    return True

# Shutdown the speech module

def shutdown ():
    global initialized
    global speakers
    global drivers

    if not initialized:
        return False

    # Unref all the drivers

    # Unref all our speakers

    for speaker in speakers.values():
        speaker.unref ()
    del speakers

    for driver in drivers:
        driver.unref ()

    del drivers

    initialized = False
    return True

# Speak text - This function takes the voice name and the text to
# speak as parameters

def say (voiceName, text):
    global initialized
    global speakers

    if not initialized:
        return -1

    # Do we have the specified voice?

    try:
        s = speakers[voiceName]

    # If not, use the default

    except:
        s = speakers["default"]

    # If the text to speak is a single character, see if we have a
    # customized character pronunciation

    if len(text) == 1:
        try:
            text = chnames[text.lower()]
        except:
            pass

    # Send the text to the GNOME Speech speaker

    return s.say (text)

# Stop the specified voice

def stop (voiceName):
    global initialized
    global speakers

    if not initialized:
        return

    try:
        s = speakers[voiceName]
        s.stop ()
    except:
        pass

# the following functions setup say all mode

# onSayAllStopped is a global reference to a function which is called
# when say all mode is interrupted

onSayAllStopped = None

# onSayAllChunk is a global refernece to a function which is called
# when say all mode needs another chunk of text to speak

onSayAllGetChunk = None

# sayAllVoiceName is a global string contaiing the name of the voice
# used in say all mode

sayAllVoiceName = None

# sayAllEnabled is a global flag indicating whether say all mode is
# enabled

sayAllEnabled = False

# This function is called in say all mode when speech for a chunk of
# text has ended

def sayAllSpeechEnded ():
    global sayAllEnabled
    global cb
    global onSayAllGetChunk

    # If calling sayAllGetChunk fails, then we're done

    if not onSayAllGetChunk ():

        # Call the client's sayAllStopped function

        onSayAllStopped ()

        # Clear the members of the speech callback

        cb.onSpeechEnded = None
        sayAllEnabled = False


# This function starts say all mode - it takes the name of the voice
# to be used in say all mode, a reference to the function to speak
# another chunk of text, and a reference to a function to be called
# when say all mode ends

def startSayAll (voiceName, getChunk, onStopped):
    global sayAllEnabled
    global onSayAllGetChunk
    global onSayAllStopped
    global cb
    global sayAllVoiceName
    
    onSayAllGetChunk = getChunk
    onSayAllStopped = onStopped
    sayAllVoiceName = voiceName
    cb.onSpeechEnded = sayAllSpeechEnded
    sayAllEnabled = True
    

# This function is called to stop say all mode

def stopSayAll ():
    global sayAllEnabled
    global cb
    global sayAllVoiceName

    cb.onSpeechEnded = None
    stop (sayAllVoiceName)
    onSayAllStopped (cb.position)
    sayAllEnabled = False
