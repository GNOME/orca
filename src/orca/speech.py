# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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

"""Manages the default speech server for orca.  A script can use this
as its speech server, or it can feel free to create one of its own."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import time

import debug
import orca_state
import platform
import settings

from acss import ACSS
from orca_i18n import _           # for gettext support

# The speech server to use for all speech operations.
#
__speechserver = None

def getSpeechServerFactories():
    """Imports all known SpeechServer factory modules.  Returns a list
    of modules that implement the getSpeechServers method, which
    returns a list of speechserver.SpeechServer instances.
    """

    factories = []

    moduleNames = settings.speechFactoryModules
    for moduleName in moduleNames:
        try:
            module =  __import__(moduleName,
                                 globals(),
                                 locals(),
                                 [''])
            factories.append(module)
        except:
            debug.printException(debug.LEVEL_OFF)

    return factories

def init():

    global __speechserver

    if __speechserver:
        return

    # First, find the factory module to use.  We will
    # allow the user to give their own factory module,
    # thus we look first in the global name space, and
    # then we look in the orca namespace.
    #
    moduleName = settings.speechServerFactory

    if moduleName:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Using speech server factory: %s" % moduleName)
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech not available.")
        return

    factory = None
    try:
        factory =  __import__(moduleName,
                              globals(),
                              locals(),
                              [''])
    except:
        try:
            moduleName = moduleName.replace("orca.","",1)
            factory =  __import__(moduleName,
                                  globals(),
                                  locals(),
                                  [''])
        except:
            debug.printException(debug.LEVEL_SEVERE)

    # Now, get the speech server we care about.
    #
    speechServerInfo = settings.speechServerInfo
    if speechServerInfo:
        __speechserver = factory.SpeechServer.getSpeechServer(speechServerInfo)
    else:
        __speechserver = factory.SpeechServer.getSpeechServer()

def __resolveACSS(acss=None):
    if acss:
        return acss
    else:
        voices = settings.voices
        return voices[settings.DEFAULT_VOICE]

def sayAll(utteranceIterator, progressCallback):
    if settings.silenceSpeech:
        return
    if __speechserver:
        __speechserver.sayAll(utteranceIterator, progressCallback)

def speak(text, acss=None, interrupt=True):
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

    # We will not interrupt a key echo in progress.
    #
    if orca_state.lastKeyEchoTime:
        interrupt = interrupt \
            and ((time.time() - orca_state.lastKeyEchoTime) > 0.5)

    if settings.silenceSpeech:
        return

    debug.println(debug.LEVEL_INFO, "SPEECH OUTPUT: '" + text + "'")
    if __speechserver:
        __speechserver.speak(text, __resolveACSS(acss), interrupt)

def isSpeaking():
    """"Returns True if the system is currently speaking."""
    if __speechserver:
        return __speechserver.isSpeaking()
    else:
        return False

def speakUtterances(utterances, acss=None, interrupt=True):
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

    # We will not interrupt a key echo in progress.
    #
    if orca_state.lastKeyEchoTime:
        interrupt = interrupt \
            and ((time.time() - orca_state.lastKeyEchoTime) > 0.5)

    if settings.silenceSpeech:
        return
    for utterance in utterances:
        debug.println(debug.LEVEL_INFO,
                      "SPEECH OUTPUT: '" + utterance + "'")
        if __speechserver:
            __speechserver.speakUtterances(utterances,
                                           __resolveACSS(acss),
                                           interrupt)

def stop():
    if __speechserver:
        __speechserver.stop()

def increaseSpeechRate(script=None, inputEvent=None):
    if __speechserver:
        __speechserver.increaseSpeechRate()
    return True

def decreaseSpeechRate(script=None, inputEvent=None):
    if __speechserver:
        __speechserver.decreaseSpeechRate()
    return True

def increaseSpeechPitch(script=None, inputEvent=None):
    if __speechserver:
        __speechserver.increaseSpeechPitch()
    return True

def decreaseSpeechPitch(script=None, inputEvent=None):
    if __speechserver:
        __speechserver.decreaseSpeechPitch()
    return True

def shutdown():
    global __speechserver
    if __speechserver:
        __speechserver.shutdownActiveServers()
        __speechserver = None

def reset(text=None, acss=None):
    global __speechserver
    if __speechserver:
        __speechserver.reset(text, acss)

def testNoSettingsInit():
    init()
    speak("testing")
    speak("this is higher", ACSS({'average-pitch' : 7}))
    speak("this is slower", ACSS({'rate' : 3}))
    speak("this is faster", ACSS({'rate' : 80}))
    speak("this is quiet",  ACSS({'gain' : 2}))
    speak("this is loud",   ACSS({'gain' : 10}))
    speak("this is normal")

def test():
    import speechserver
    factories = getSpeechServerFactories()
    for factory in factories:
        print factory.__name__
        servers = factory.SpeechServer.getSpeechServers()
        for server in servers:
            try:
                print "    ", server.getInfo()
                for family in server.getVoiceFamilies():
                    name = family[speechserver.VoiceFamily.NAME]
                    print "      ", name
                    acss = ACSS({ACSS.FAMILY : family})
                    server.speak(name, acss)
                    server.speak("testing")
                server.shutdown()
            except:
                debug.printException(debug.LEVEL_OFF)
                pass
