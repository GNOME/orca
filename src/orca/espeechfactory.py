# Orca
#
# Copyright 2005 Google Inc.
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
__author__ = "$Author$"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2005 Google Inc."
__license__ = "LGPL"
__all__=['Speaker']

import os, sys

import debug
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

    location="/usr/share/emacs/site-lisp/emacspeak/servers"

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
    __getSpeechServersCalled = False

    def getFactoryName():
        """Returns a localized name describing this factory."""
        return _("Emacspeak Speech Services")

    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServers():
        """Enumerate available speech servers.

        Returns a list of [name, id] values identifying the available
        speech servers.  The name is a human consumable string and the
        id is an object that can be used to create a speech server
        via the getSpeechServer method.
        """

        if SpeechServer.__getSpeechServersCalled:
            return SpeechServer.__activeServers.values()
        else:
            SpeechServer.__getSpeechServersCalled = True

        f = open(os.path.join(SpeechServer.location, '.servers'))
        for line in f:
            if line[0] == '#' or line.strip() == '': continue
            name = line.strip()
            if not SpeechServer.__activeServers.has_key(name):
                try:
                    SpeechServer.__activeServers[name] = SpeechServer(name)
                except:
                    pass
        f.close()

        return SpeechServer.__activeServers.values()

    getSpeechServers = staticmethod(getSpeechServers)

    def getSpeechServer(info=['outloud','outloud']):
        """Gets a given SpeechServer based upon the info.
        See SpeechServer.getInfo() for more info.
        """
        if SpeechServer.__activeServers.has_key(info[0]):
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
        for key in SpeechServer.__activeServers.keys():
            server = SpeechServer.__activeServers[key]
            server.shutdown()

    shutdownActiveServers = staticmethod(shutdownActiveServers)

    def __init__ (self,
                  engine='outloud',
                  host='localhost',
                  initial=config):
        """Launches speech engine."""

        speechserver.SpeechServer.__init__(self)

        self._engine = engine
        e = __import__(_getcodes(engine),
                       globals(),
                       locals(),
                       [''])
        self.getvoice     = e.getvoice
        self.getrate      = e.getrate
        self.getvoicelist = e.getvoicelist
        if host == 'localhost':
            self._server = os.path.join(SpeechServer.location, self._engine)
        else:
            self._server = os.path.join(SpeechServer.location,
                                         "ssh-%s" % self._engine)
        cmd = '{ ' + self._server + '; } 2>&1'
        #print "Command = ", cmd
        #self._output = os.popen(cmd, "w", 1)
        [self._output, stdout, stderr] = os.popen3(cmd, "w", 1)
        self._settings ={}
        if initial:
            self._settings.update(initial)
            self.configure(self._settings)

    def configure(self, settings):
        """Configure engine with settings."""
        for k in settings.keys():
            if hasattr(self, k) and callable(getattr(self,k)):
                getattr(self,k)(settings[k])

    def settings(self): return self._settings

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
            pass

        return families

    def queueText(self, text="", acss=None):
        """Queue text to be spoken.
        Output is produced by next call to say() or speak()."""
        if acss:
            code =self.getvoice(acss)
            self._output.write("q {%s %s %s}\n" %(code[0], text,
        code[1]))
        else:
            self._output.write("q {%s}\n" %text)

    def queueTone(self, pitch=440, duration=50):
        """Queue specified tone."""
        self._output.write("t %s %s\n " % (pitch, duration))

    def queueSilence( self, duration=50):
        """Queue specified silence."""
        self._output.write("sh  %s" %  duration)

    def speakCharacter(self, character, acss=None):
        """Speak single character."""
        self._output.write("l {%s}\n" % character)

    def speakUtterances(self, list, acss=None):
        """Speak list of utterances."""
        if acss:
            code =self.getvoice(acss)
            for t in list:
                self._output.write("q { %s %s %s }\n" %(code[0], str(t), code[1]))
        else:
            for t in list:
                self._output.write("q { %s }\n" % str(t))
        self._output.write("d\n")

    def speak(self, text="", acss=None):
        """Speaks specified text. All queued text is spoken immediately."""
        if acss:
            code =self.getvoice(acss)
            self._output.write("q {%s %s %s}\nd\n" %(code[0], text, code[1]))
        else:
            self._output.write("q {%s}\nd\n" %text)

    def increaseSpeechRate(self, step=5):
        """Set speech rate."""
        self._settings['rate'] += step
        self._output.write("tts_set_speech_rate %s\n" \
                            % self.getrate(self._settings['rate']))

    def decreaseSpeechRate(self, step=5):
        """Set speech rate."""
        self._settings['rate'] -= step
        self._output.write("tts_set_speech_rate %s\n" \
                            % self.getrate(self._settings['rate']))

    def stop(self):
        """Silence ongoing speech."""
        self._output.write("s\n")

    def shutdown(self):
        """Shutdown speech engine."""
        if SpeechServer.__activeServers.has_key(self._engine):
            self._output.close()
            del SpeechServer.__activeServers[self._engine]

    def reset(self):
        """Reset TTS engine."""
        self._output.write("tts_reset\n")

    def version(self):
        """Speak TTS version info."""
        self._output.write("version\n")

    def punctuations(self, mode):
        """Set punctuation mode."""
        if mode in ['all', 'some', 'none']:
            self._settings['punctuations'] = mode
            self._output.write("tts_set_punctuations %s\n" % mode)

    def rate(self, r):
        """Set speech rate."""
        self._settings['rate'] = r
        self._output.write("tts_set_speech_rate %s\n" % self.getrate(r))

    def splitcaps(self, flag):
        """Set splitcaps mode. 1  turns on, 0 turns off"""
        flag = bool(flag) and 1 or 0
        self._settings['splitcaps'] = flag
        self._output.write("tts_split_caps %s\n" % flag)

    def capitalize(self, flag):
        """Set capitalization  mode. 1  turns on, 0 turns off"""
        flag = bool(flag) and 1 or 0
        self._settings['capitalize'] = flag
        self._output.write("tts_capitalize %s\n" % flag)

    def allcaps(self, flag):
        """Set allcaps  mode. 1  turns on, 0 turns off"""
        flag = bool(flag) and 1 or 0
        self._settings['allcaps'] = flag
        self._output.write("tts_allcaps_beep %s\n" % flag)

    def __del__(self):
        "Shutdown speech engine."
        if hasattr(self, "_output") \
           and not self._output.closed:
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
    s=SpeechServer()
    a=acss.ACSS()
    s.punctuations('some')
    s.queueText("This is an initial test.");
    s.queueText("Next, we'll test audio formatted output.")
    for d in ['average-pitch', 'pitch-range',
              'richness', 'stress']:
        for i in range(0,10,2):
            a[d] = i
            s.queueText("Set %s to %i. " % (d, i), a)
        del a[d]
        s.queueText("Reset %s." % d, a)
    s.speak()
    print "sleeping  while waiting for speech to complete."
    time.sleep(40)
    s.shutdown()


if __name__=="__main__": _test()
