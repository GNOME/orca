# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""Manages the speech for orca.

Provides support for voice styles, speaking, and sayAll mode.
"""
import debug
from core import ORBit, bonobo
import sys
import settings
from chnames import chnames  # character (e.g., punctuation) pronunciations

ORBit.load_typelib ('GNOME_Speech')
import GNOME.Speech, GNOME__POA.Speech

# Global list of active gnome-spech drivers
#
drivers = []

# Dictionary of speakers.  The key is the voice style name (e.g., "default")
# and the value is the speaker.
#
speakers = {}

# If True, this module has been initialized.
#
initialized = False

# Last text and voice spoken.
#
lastText = None

def createSpeaker (driverName, voiceName):
    """Internal to speech module only.

    Creates a GNOME Speech speaker based on a speech driver name and a voice
    name.

    Arguments:
    - driverName: speech driver name (e.g., "Festival Speech Synthesis System")
    - voiceName: voice style name from settings.py

    Returns a speaker from the driver or None if the speaker cannot be
    created or the driver cannot be found.
    """
    
    global drivers

    # Find the specified GNOME Speech driver
    #
    found = False
    for driver in drivers:
        if driver.synthesizerName.find(driverName) >= 0:
            found = True
            break
    if not found:
        return None

    # [[[TODO: MM - This could probably just as easily be done with a
    # better use of getVoices.]]]
    #
    voices = driver.getAllVoices ()
    found = False
    for voice in voices:
        if voice.name.find (voiceName) >= 0:
            found = True
            break
    if not found:
        return None

    return driver.createSpeaker (voice)


class SpeechCallback (GNOME__POA.Speech.SpeechCallback):
    """Implements gnome-speech's SpeechCallback class.  The speech
    module uses only one global callback object which is used for
    tasks such as sayAll mode.

    SpeechCallback objects contain a speech ended method, as well as the
    current speaking position.
    """

    def __init__ (self):
        self.onSpeechEnded = None
        self.position = 0


    def notify (self, type, id, offset):
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
                self.onSpeechEnded ()

        # Update our speaking position if we get a speech progress
        # notification.  [[[TODO: WDW - need to be able use this to
        # update the magnifier's region of interest.]]]
        #
        elif type == GNOME.Speech.speech_callback_speech_progress:
            self.position = offset


# Global speech callback instance.
#
cb = SpeechCallback ()


def init ():
    """Initializes the speech module, connecting to the various speech
    drivers and creating the various speakersvoice styles defined in the
    user's settings.py.

    Returns True if the initialization procedure was run or False if this
    module has already been initialized.
    """
    
    global initialized
    global drivers
    global speakers
    global cb

    if initialized:
        return False

    # Get a list of all the drivers on the system and find out how many
    # of them work.
    #
    servers = bonobo.activation.query (
        "repo_ids.has ('IDL:GNOME/Speech/SynthesisDriver:0.3')")

    drivers = []
    for server in servers:
        try:
            driver = bonobo.activation.activate_from_id (server.iid, 0, False)
        except:
            continue
            
        # Ensure what we have is a SynthesisDriver object - This
        # is needed for Java CORBA ORB interoperability
        #
        driver = driver._narrow (GNOME.Speech.SynthesisDriver)
        isInitialized = driver.isInitialized ()

        # Only initialize the driver if someone else hasn't
        # initialized it already.  [[[TODO: WDW - unless we're doing
        # the configuration, we probably do not want to initialize
        # all the drivers.]]]
        #
        if not isInitialized:
            isInitialized = driver.driverInit ()
        if isInitialized:
            drivers.append (driver)

    # Create the speakers
    #
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
    #
    if len(speakers) == 0 and len(drivers) > 0:
        voices = drivers[0].getAllVoices ()
        if len(voices) > 0:
            speakers["default"] = drivers[0].createSpeaker(
                voices[0])._narrow(GNOME.Speech.Speaker)

    initialized = True

    return True


def shutdown ():
    """Shuts down the speech module, freeing speakers, disconnecting
    from the GNOME speech drivers, and reseting the initialized state
    to False.  [[[TODO: WDW - make sure this is shutting down
    correctly.  Seems like this is too easy.  :-)]]]

    Returns True if the shutdown procedure was run or False if this
    module has not been initialized.
    """
    
    global initialized
    global speakers
    global drivers

    if not initialized:
        return False

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
    """Speaks the given text using the given voice style.

    Arguments:
    - voiceName: the name of the voice style to use (e.g., "default")
    - text: the text to speak

    Returns the result of the GNOME Speech say method call or -1 if
    this module has not been initialized.  [[[TODO: WDW - just what is
    this result?  In addition, this is asynchronous (i.e., doesn't
    wait for the text to be spoken), right?]]]
    """

    global initialized
    global speakers
    global lastText
    
    if not initialized:
        return -1

    # Do we have the specified voice?
    #
    if speakers.has_key (voiceName):
        s = speakers[voiceName]
    else:
        s = speakers["default"]

    # If the text to speak is a single character, see if we have a
    # customized character pronunciation
    #
    if len(text) == 1:
        try:
            text = chnames[text.lower()]
        except:
            pass

    # Send the text to the GNOME Speech speaker
    #
    debug.println("speech.say (" + text + ")")
    #debug.printStack ()
    try:
        s.stop ()
        lastText = [voiceName, text]
        return s.say (text)
    except:
        debug.printException ()


def sayAgain ():
    """Speaks the last text again.
    """

    if lastText:
        say (lastText[0], lastText[1])

    
def stop (voiceName):
    """Stops the specified voice.  This will tell the voice to stop
    all requests in progress and delete all requests waiting to be spoken.

    Arguments:
    - voiceName: the name of the voice style (e.g., "default")
    """
    
    global initialized
    global speakers

    if not initialized:
        return

    if speakers.has_key (voiceName):
        s = speakers[voiceName]
        s.stop ()


########################################################################
#                                                                      #
# SAYALL SUPPORT                                                       #    
#                                                                      #
########################################################################

# onSayAllStopped is a global reference to a function which is called
# when sayAll mode is interrupted
#
onSayAllStopped = None

# onSayAllChunk is a global refernece to a function which is called
# when sayAll mode needs another chunk of text to speak
#
onSayAllGetChunk = None

# sayAllVoiceName is a global string contaiing the name of the voice
# used in sayAll mode
#
sayAllVoiceName = None

# sayAllEnabled is a global flag indicating whether sayAll mode is
# enabled
#
sayAllEnabled = False

# This function is called in sayAll mode when speech for a chunk of
# text has ended

def sayAllSpeechEnded ():
    """Called in sayAll mode when speech for a chunk of text has
    ended.  This will prompt sayAll mode to attempt to speak the
    next chunk of text.

    """
    
    global sayAllEnabled
    global cb
    global onSayAllGetChunk

    # If calling sayAllGetChunk fails, then we're done
    #
    if not onSayAllGetChunk ():
        # Call the client's sayAllStopped function
        #
        onSayAllStopped ()

        # Clear the members of the speech callback
        #
        cb.onSpeechEnded = None
        sayAllEnabled = False


def startSayAll (voiceName, getChunk, onStopped):
    """Starts sayAll mode.  Takes the name of the voice style to be
    used, a reference to the function to speak another chunk of
    text, and a reference to a function to be called when sayAll
    mode ends.  This merely sets up pointers and doesn't invoke
    any speaking actions.

    Implementation note: this depends upon the speech driver giving us
    speech ended callback notification.
    
    Arguments:
    - voiceName: the name of the voice style (e.g., "default")
    - getChunk: the client/script callback that will speak more text
    - onStopped: the client/script callback that will be notified when
                 sayAll mode has been stopped.
    """
    
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
    

def stopSayAll ():
    """Stops the sayAll mode currently in progress.
    """
    
    global sayAllEnabled
    global cb
    global sayAllVoiceName

    cb.onSpeechEnded = None
    stop (sayAllVoiceName)
    onSayAllStopped (cb.position)
    sayAllEnabled = False
