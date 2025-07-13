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

class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME   = "name"
    GENDER = "gender"
    LANG   = "lang"
    DIALECT = "dialect"
    VARIANT = "variant"

    MALE   = "male"
    FEMALE = "female"

    settings = {
        NAME   : None,
        GENDER : None,
        LANG   : None,
        DIALECT: None,
        VARIANT: None,
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
        self.endOffset     = endOffset
        self.currentOffset = startOffset
        self.currentEndOffset = None

    def __str__(self):
        return "SAY ALL: %s '%s' (%i-%i, current: %i)" % \
            (self.obj, self.utterance, self.startOffset, self.endOffset, self.currentOffset)

    def copy(self):
        new = SayAllContext(self.obj, self.utterance,
                            self.startOffset, self.endOffset)
        new.currentOffset = self.currentOffset
        new.currentEndOffset = self.currentEndOffset
        return new

    def __eq__(self, other):
        return (self.startOffset == other.startOffset and
                self.endOffset == other.endOffset and
                self.obj == other.obj and
                self.utterance == other.utterance)


class SpeechServer(object):
    """Provides speech server abstraction."""

    @staticmethod
    def getFactoryName():
        """Returns a localized name describing this factory."""
        pass

    @staticmethod
    def getSpeechServers():
        """Gets available speech servers as a list.  The caller
        is responsible for calling the shutdown() method of each
        speech server returned.
        """
        pass

    @staticmethod
    def get_speech_server(info):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.get_info() for more info.
        """
        pass

    @staticmethod
    def shutdownActiveServers():
        """Cleans up and shuts down this factory.
        """
        pass

    def __init__(self):
        pass

    def get_info(self):
        """Returns [name, id]
        """
        pass

    def getVoiceFamilies(self):
        """Returns a list of VoiceFamily instances representing all
        voice families known by the speech server."""
        pass

    def getVoiceFamily(self):
        """Returns the current voice family as a VoiceFamily dictionary."""
        pass

    def setVoiceFamily(self, family):
        """Sets the voice family to family VoiceFamily dictionary."""

        pass

    def speak_character(self, character, acss=None):
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

    def speak_key_event(self, event, acss=None):
        """Speaks a key event immediately.

        Arguments:
        - event: the input_event.KeyboardEvent.
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

    def say_all(self, utterance_iterator, progress_callback):
        """Iterates through the given utterance_iterator, speaking
        each utterance one at a time.  Subclasses may postpone
        getting a new element until the current element has been
        spoken.

        Arguments:
        - utterance_iterator: iterator/generator whose next() function
                             returns a [SayAllContext, acss] tuple
        - progress_callback:  called as speech progress is made - has a
                             signature of (SayAllContext, type), where
                             type is one of PROGRESS, INTERRUPTED, or
                             COMPLETED.
        """
        pass

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

    def increaseSpeechVolume(self, step=0.5):
        """Increases the speech volume.
        """
        pass

    def decreaseSpeechVolume(self, step=0.5):
        """Decreases the speech volume.
        """
        pass

    def updateCapitalizationStyle(self):
        """Updates the capitalization style used by the speech server."""
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

    def getOutputModule(self):
        """Returns the output module associated with this speech server."""
        return None

    def setOutputModule(self, module_id):
        """Sets the output module associated with this speech server."""
        pass

    def list_output_modules(self):
        """Return names of available output modules as a tuple of strings."""
        return ()
