# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Provides an abtract class for working with speech servers.

A speech server (class SpeechServer) provides the ability to tell the
machine to speak.  Each speech server provides a set of known
voices (identified by name) which can be combined with various
attributes to create aural style sheets."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import logging
from . import settings
from . import orca_state

log = logging.getLogger("speech")

from . import debug

from .acss import ACSS

class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME   = "name"
    GENDER = "gender"
    LOCALE = "locale"

    MALE   = "male"
    FEMALE = "female"

    settings = {
        NAME   : None,
        GENDER : None,
        LOCALE : None
    }

    def __init__(self, props):
        """Create and initialize VoiceFamily."""
        dict.__init__(self)

        self.update(VoiceFamily.settings)
        if props:
            self.update(props)

class SayAllContext:

    PROGRESS    = 0
    INTERRUPTED = 1
    COMPLETED   = 2

    def __init__(self, obj, utterance, startOffset=-1, endOffset=-1):
        """Creates a new SayAllContext that will be passed to the
        SayAll callback handler for progress updates on speech.
        If the object does not have an accessible text specialization,
        then startOffset and endOffset parameters are meaningless.
        If the object does have an accessible text specialization,
        then values >= 0 for startOffset and endOffset indicate
        where in the text the utterance has come from.

        Arguments:
        -obj:         the Accessible being spoken
        -utterance:   the actual utterance being spoken
        -startOffset: the start offset of the Accessible's text
        -endOffset:   the end offset of the Accessible's text
        """
        self.obj           = obj
        self.utterance     = utterance
        self.startOffset   = startOffset
        self.currentOffset = startOffset
        self.endOffset     = endOffset


class SpeechServer(object):

    """Provides speech server abstraction."""

    def getFactoryName():
        """Returns a localized name describing this factory."""
        pass

    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServers():
        """Gets available speech servers as a list.  The caller
        is responsible for calling the shutdown() method of each
        speech server returned.
        """
        pass

    getSpeechServers = staticmethod(getSpeechServers)

    def getSpeechServer(info):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.getInfo() for more info.
        """
        pass

    getSpeechServer = staticmethod(getSpeechServer)

    def shutdownActiveServers():
        """Cleans up and shuts down this factory.
        """
        pass

    shutdownActiveServers = staticmethod(shutdownActiveServers)

    def __init__(self):
        pass

    def getInfo(self):
        """Returns [name, id]
        """
        pass

    def getVoiceFamilies(self):
        """Returns a list of VoiceFamily instances representing all
        voice families known by the speech server."""
        pass

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
        pass

    def speakKeyEvent(self, event):
        """Speaks a key event immediately.

        Arguments:
        - event: the input_event.KeyboardEvent.
        """
        if event.isPrintableKey() \
           and event.event_string.decode("UTF-8").isupper():
            voice = ACSS(settings.voices[settings.UPPERCASE_VOICE])
        else:
            voice = ACSS(settings.voices[settings.DEFAULT_VOICE])

        event_string = event.getKeyName()
        if orca_state.activeScript and orca_state.usePronunciationDictionary:
            event_string = orca_state.activeScript.\
                utilities.adjustForPronunciation(event_string)

        lockingStateString = event.getLockingStateString()
        event_string = "%s %s" % (event_string, lockingStateString)

        logLine = "SPEECH OUTPUT: '" + event_string +"'"
        debug.println(debug.LEVEL_INFO, logLine)
        log.info(logLine)

        self.speak(event_string, acss=voice)

    def speakUtterances(self, utteranceList, acss=None, interrupt=True):
        """Speaks the given list of utterances immediately.

        Arguments:
        - utteranceList: list of strings to be spoken
        - acss:      acss.ACSS instance; if None,
                     the default voice settings will be used.
                     Otherwise, the acss settings will be
                     used to augment/override the default
                     voice settings.
        - interrupt: if True, stop any speech currently in progress.
        """
        pass

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
        pass

    def isSpeaking(self):
        """"Returns True if the system is currently speaking."""
        return False

    def sayAll(self, utteranceIterator, progressCallback):
        """Iterates through the given utteranceIterator, speaking
        each utterance one at a time.  Subclasses may postpone
        getting a new element until the current element has been
        spoken.

        Arguments:
        - utteranceIterator: iterator/generator whose next() function
                             returns a [SayAllContext, acss] tuple
        - progressCallback:  called as speech progress is made - has a
                             signature of (SayAllContext, type), where
                             type is one of PROGRESS, INTERRUPTED, or
                             COMPLETED.
        """
        for [context, acss] in utteranceIterator:
            logLine = "SPEECH OUTPUT: '" + context.utterance + "'"
            debug.println(debug.LEVEL_INFO, logLine)
            log.info(logLine)
            self.speak(context.utterance, acss)

    def increaseSpeechRate(self, step=5):
        """Increases the speech rate.
        """
        pass

    def decreaseSpeechRate(self, step=5):
        """Decreases the speech rate.
        """
        pass

    def increaseSpeechPitch(self, step=0.5):
        """Increases the speech pitch.
        """
        pass

    def decreaseSpeechPitch(self, step=0.5):
        """Decreases the speech pitch.
        """
        pass

    def updatePunctuationLevel(self):
        """Punctuation level changed, inform this speechServer."""
        pass

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        pass

    def shutdown(self):
        """Shuts down the speech engine."""
        pass

    def reset(self, text=None, acss=None):
        """Resets the speech engine."""
        pass
