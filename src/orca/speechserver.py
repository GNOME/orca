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

"""Provides an abtract class for working with speech servers.

A speech server (class SpeechServer) provides the ability to tell the
machine to speak.  Each speech server provides a set of known
voices (identified by name) which can be combined with various
attributes to create aural style sheets.
"""

class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME   = "name"
    GENDER = "gender"
    LOCALE = "locale"
    
    settings = {
        NAME   : None,
        GENDER : None,
        LOCALE : None
    }

    def __init__(self,props):
        """Create and initialize VoiceFamily."""
        self.update(VoiceFamily.settings)
        if props is not None:
            self.update(props)
    
class ACSS(dict):
    """Holds ACSS representation of a voice."""

    FAMILY        = 'family'
    RATE          = 'rate'
    GAIN          = 'gain'
    LEFT_VOLUME   = 'left-volume'
    RIGHT_VOLUME  = 'right-volume'
    AVERAGE_PITCH = 'average-pitch'
    PITCH_RANGE   = 'pitch-range'
    STRESS        = 'stress'
    RICHNESS      = 'richness'
    PUNCTUATIONS  = 'punctuations'

    # A value of None means use the engine's default value.
    #
    settings = {
        FAMILY :        None,
        RATE :          None,
        GAIN :          None,
        LEFT_VOLUME :   None,
        RIGHT_VOLUME :  None,
        AVERAGE_PITCH : None,
        PITCH_RANGE :   None, 
        STRESS :        None,
        RICHNESS :      None,
        PUNCTUATIONS :  None
    }

    def __init__(self,props=None):
        """Create and initialize ACSS structure."""
        self.update(ACSS.settings)
        if props is not None:
            self.update(props)


class SpeechServer:
    
    """Provides speech server abstraction."""

    def __init__(self):
        self.__acss = {}

    def setACSS(self, name, acss):
        """Adds an aural cascading style sheet to this server using
        the given name as its identifier.  Returns 'True' on success,
        meaning this ACSS will work with this SpeechServer.

        Arguments:
        - name: the identifier, to be used in calls to say something
        - acss: the aural cascading style sheet to use
        """
        self.__acss[name] = acss

    def getInfo(self):
        """Returns [driverName, synthesizerName]
        """
        pass

    def getVoiceFamilies(self):
        """Returns a list of VoiceFamily instances representing all
        voice families known by the speech server."""
        pass
    
    def queueText(self, text="", acssName="default"):
        """Adds the text to the queue.

        Arguments:
        - text:     text to be spoken
        - acssName: name of a speechserver.ACSS instance registered
                    via a call to setACSS
                    
        Output is produced by the next call to speak.
        """
        pass

    def queueCharacter(self, character, acssName="default"):
        """Adds a single character to the queue of things to be spoken.

        Arguments:
        - character: text to be spoken
        - acssName:  name of a speechserver.ACSS instance registered
                     via a call to setACSS
                    
        Output is produced by the next call to speak.
        """
        pass

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
        pass
    
    def speak(self, text=None, acssName="default"):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text:     text to be spoken
        - acssName: name of a speechserver.ACSS instance registered
                    via a call to setACSS
        """
        pass

    def increaseSpeechRate(self, acssName=None):
        """Increases the rate of speech for the given ACSS.  If
        acssName is None, the rate increase will be applied to all
        known ACSSs.
    
        Arguments:
        -acssName: the ACSS whose speech rate should be increased
        """
        pass
    
    def decreaseSpeechRate(self, acssName=None):
        """Decreases the rate of speech for the given ACSS.  If
        acssName is None, the rate decrease will be applied to all
        known ACSSs.

        Arguments:
        -acssName: the ACSS whose speech rate should be decreased
        """
        pass
    
    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        pass

    def shutdown(self):
        """Shuts down the speech engine."""
        pass
