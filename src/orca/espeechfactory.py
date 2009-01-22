# Orca
#
# Copyright 2005-2008 Google Inc.
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
#
"""Python wrapper for Emacspeak speech servers.

The emacspeak TTS server provides a simple but powerful and
well-tested speech-server abstraction. That server is implemented
as an external program (typically in TCL).  This wrapper class
provides Python access to available Emacspeak speech servers.

Initially, this class will provide Python access to the TTS
server commands.  Over time, this module may also implement
functionality present in Emacspeak's Lisp layer ---specifically,
higher level TTS functionality provided by the following
emacspeak modules:

0)  dtk-speak.el

1)  emacspeak-pronounce.el

2)  accs-structure.el

"""

__id__ = "$Id$"
__author__ = "T. V. Raman"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Google Inc."
__license__ = "LGPL"
__all__ = ['Speaker']

import os
import re

import debug
import settings
import speechserver

from orca_i18n import _           # for gettext support

class SpeechServer(speechserver.SpeechServer):

    """Provides speech server abstraction.

    Class Variables:

        location -- specifies directory where Emacspeak
        speech servers are installed.

        config --  dictionary of default settings.

    Speaker objects can be initialized with the following parameters:

        engine -- TTS server to instantiate. Default: outloud
        host -- Host that runs   server. Default: localhost
        settings -- Dictionary of default settings.

    """

    location = "/usr/share/emacs/site-lisp/emacspeak/servers"

    config = {'splitcaps' : 1,
              'rate' : 70,
    'capitalize' : 0,
    'allcaps' : 0,
    'punctuations' : 'all'
    }

    # Dictionary of known running servers.  The key is the name and
    # the value is the SpeechServer instance.  We do this to enforce a
    # singleton instance of any given server.
    #
    __activeServers = {}

    # A regexp to match chunks of text which will be sent to speech server
    # NB: this must always match, the question is how many characters.
    _speechChunkRegexp = ('.{0,120}?[\n,.;:!?)][]}"]?\\s+'
                          '|.{1,120}(?:\\Z|\\s+)'
                          '|.{1,120}')

    def getFactoryName():
        """Returns a localized name describing this factory."""
        # Translators: this refers to the speech synthesis services
        # provided by the separate emacspeak utility available at
        # http://emacspeak.sourceforge.net/.
        #
        return _("Emacspeak Speech Services")

    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServers():
        """Gets available speech servers as a list.  The caller
        is responsible for calling the shutdown() method of each
        speech server returned.
        """

        haveNewServers = False
        serversConf = file(os.path.join(SpeechServer.location, '.servers'))
        for name in serversConf:
            name = name.strip()
            if name == '' or name[0] == '#':
                continue
            if name not in SpeechServer.__activeServers:
                try:
                    SpeechServer.__activeServers[name] = SpeechServer(name)
                    haveNewServers = True
                except:
                    debug.printException(debug.LEVEL_WARNING)
        serversConf.close()

        # Check whether some servers have died and remove those from the list
        if haveNewServers:
            from time import sleep
            sleep(1)
        for server in SpeechServer.__activeServers.values():
            if not server.process or server.process.poll() is not None:
                server.shutdown()

        return SpeechServer.__activeServers.values()

    getSpeechServers = staticmethod(getSpeechServers)

    def getSpeechServer(info=['outloud', 'outloud']):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.getInfo() for more info.
        """
        if info[0] in SpeechServer.__activeServers:
            return SpeechServer.__activeServers[info[0]]
        else:
            try:
                return SpeechServer(info[0])
            except:
                debug.printException(debug.LEVEL_SEVERE)
            return None

    getSpeechServer = staticmethod(getSpeechServer)

    def shutdownActiveServers():
        """Cleans up and shuts down this factory.
        """
        for server in SpeechServer.__activeServers.values():
            server.shutdown()

    shutdownActiveServers = staticmethod(shutdownActiveServers)

    def __init__ (self,
                  engine='outloud',
                  host='localhost',
                  initial=config):
        """Launches speech engine."""

        speechserver.SpeechServer.__init__(self)

        self._engine = engine
        self._output = None
        self.process = None

        e = __import__(_getcodes(engine),
                       globals(),
                       locals(),
                       [''])
        self.getvoice     = e.getvoice
        self.getrate      = e.getrate
        self.getvoicelist = e.getvoicelist
        self._specialChars = e.makeSpecialCharMap()
        if host == 'localhost':
            self._server = os.path.join(SpeechServer.location, self._engine)
        else:
            self._server = os.path.join(SpeechServer.location,
                                         "ssh-%s" % self._engine)

        # Start the process and close its output channels since they were
        # closed implicitly in previous version of espeechfactory.py.
        from subprocess import (Popen, PIPE)
        proc = Popen(self._server, close_fds=True,
                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
        proc.stdout.close()
        proc.stderr.close()
        proc.stdout = proc.stderr = None
        self._output = proc.stdin
        self.process = proc

        self._speechChunk = re.compile(self._speechChunkRegexp, re.DOTALL)
        self._settings = {}
        if initial:
            self._settings.update(initial)
            self.configure(self._settings)

    def configure(self, engineSettings):
        """Configure engine with settings."""
        for k in engineSettings.keys():
            if hasattr(self, k) and callable(getattr(self, k)):
                getattr(self, k)(engineSettings[k])

    def settings(self):
        return self._settings

    def getInfo(self):
        """Returns [driverName, serverId]
        """
        return [self._engine, self._engine]

    def getVoiceFamilies(self):
        """Returns a list of speechserver.VoiceFamily instances
        representing all the voice families known by the speech server.
        """

        families = []
        try:
            for voice in self.getvoicelist():
                props = {
                    speechserver.VoiceFamily.NAME   : voice
                }
                families.append(speechserver.VoiceFamily(props))
        except:
            debug.printException(debug.LEVEL_SEVERE)

        return families

    def _quoteSpecialChars(self, text):
        """Replaces all special characters in text by their replacements
        according to self._specialChars.
        """
        for char, name in self._specialChars:
            text = text.replace(char, name)
        return text

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
        if not settings.enableSpeech:
            return

        # A command to send to the speech server queueing text
        cmd = "q { %s }\n"
        if acss:
            try:
                code = self.getvoice(acss)
                cmd = "q {%s %%s %s}\n" % (code[0], code[1])
            except:
                debug.printException(debug.LEVEL_WARNING)

        # Split text into chunks and each chunk queue separately
        for chunk in (t.group() for t in self._speechChunk.finditer(text)):
            self._output.write(cmd % self._quoteSpecialChars(chunk))

    def queueTone(self, pitch=440, duration=50):
        """Adds a tone to the queue.

        Output is produced by the next call to speak.
        """
        self._output.write("t %s %s\n " % (pitch, duration))

    def queueSilence( self, duration=50):
        """Adds silence to the queue.

        Output is produced by the next call to speak.
        """
        self._output.write("sh  %s" %  duration)

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
        if character in '{\\}':
            character = self._quoteSpecialChars(character)
        self._output.write("l {%s}\n" % character)
        self._output.flush()

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
        for utt in utteranceList:
            self.queueText(str(utt), acss)
        self._output.write("d\n")
        self._output.flush()

    def speak(self, text="", acss=None, interrupt=True):
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

        # If the user has speech turned off, just return.
        #
        if not settings.enableSpeech:
            return

        self.queueText(text, acss)
        self._output.write("d\n")
        self._output.flush()

    def increaseSpeechPitch(self, step=0.5):
        """Increases the speech pitch."""
        self._settings['average-pitch'] += step

    def decreaseSpeechPitch(self, step=0.5):
        """Decreases the speech pitch."""
        self._settings['average-pitch'] -= step

    def increaseSpeechRate(self, step=5):
        """Increases the speech rate.
        """
        self._settings['rate'] += step
        self._output.write("tts_set_speech_rate %s\n" \
                            % self.getrate(self._settings['rate']))
        self._output.flush()

    def decreaseSpeechRate(self, step=5):
        """Decreases the speech rate.
        """
        self._settings['rate'] -= step
        self._output.write("tts_set_speech_rate %s\n" \
                            % self.getrate(self._settings['rate']))
        self._output.flush()

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        self._output.write("s\n")
        self._output.flush()

    def shutdown(self):
        """Shuts down the speech engine."""
        if self.process is None:
            return

        if self.process.poll() is None:
            from signal import SIGKILL
            os.kill(self.process.pid, SIGKILL)
            self.process.wait()
        self._output.close()
        self._output = self.process = None
        if self is SpeechServer.__activeServers.get(self._engine, None):
            del SpeechServer.__activeServers[self._engine]

    def reset(self, text=None, acss=None):
        """Resets the speech engine."""
        self._output.write("tts_reset\n")
        self._output.flush()

    def version(self):
        """Speak TTS version info."""
        self._output.write("version\n")

    def punctuations(self, mode):
        """Set punctuation mode."""
        if mode in ['all', 'some', 'none']:
            self._settings['punctuations'] = mode
            self._output.write("tts_set_punctuations %s\n" % mode)
            self._output.flush()

    def rate(self, r):
        """Set speech rate."""
        self._settings['rate'] = r
        self._output.write("tts_set_speech_rate %s\n" % self.getrate(r))
        self._output.flush()

    def splitcaps(self, flag):
        """Set splitcaps mode. 1  turns on, 0 turns off"""
        flag = bool(flag) and 1 or 0
        self._settings['splitcaps'] = flag
        self._output.write("tts_split_caps %s\n" % flag)
        self._output.flush()

    def capitalize(self, flag):
        """Set capitalization  mode. 1  turns on, 0 turns off"""
        flag = bool(flag) and 1 or 0
        self._settings['capitalize'] = flag
        self._output.write("tts_capitalize %s\n" % flag)
        self._output.flush()

    def allcaps(self, flag):
        """Set allcaps  mode. 1  turns on, 0 turns off"""
        flag = bool(flag) and 1 or 0
        self._settings['allcaps'] = flag
        self._output.write("tts_allcaps_beep %s\n" % flag)
        self._output.flush()

    def __del__(self):
        "Shuts down the speech engine."
        self.shutdown()

def _getcodes(engine):
    """Helper function that fetches synthesizer codes for a
    specified engine."""
    if engine not in _codeTable:
        raise Exception("No code table for %s" % engine)
    return _codeTable[engine]

_codeTable = {
    'dtk-exp' : 'dectalk',
    'dtk-mv' : 'dectalk',
    'dtk-soft' : 'dectalk',
    'outloud' : 'outloud',
    }

def _test():
    """Self test."""
    import time
    import acss
    s = SpeechServer()
    a = acss.ACSS()
    s.punctuations('some')
    s.queueText("This is an initial test.")
    s.queueText("Next, we'll test audio formatted output.")
    for d in ['average-pitch', 'pitch-range',
              'richness', 'stress']:
        for i in range(0, 10, 2):
            a[d] = i
            s.queueText("Set %s to %i. " % (d, i), a)
        del a[d]
        s.queueText("Reset %s." % d, a)
    s.speak()
    print "sleeping  while waiting for speech to complete."
    time.sleep(40)
    s.shutdown()


if __name__ == "__main__":
    _test()
