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
as its speech server, or it can feel free to create one of its own.
"""

import debug
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

    debug.println(debug.LEVEL_CONFIGURATION,
                  "Using speech server factory: %s" % moduleName)

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
    if __speechserver:
        __speechserver.sayAll(utteranceIterator, progressCallback)

def speak(text, acss=None):
    if __speechserver:
        __speechserver.speak(text, __resolveACSS(acss))

def speakUtterances(utterances, acss=None):
    if __speechserver:
        __speechserver.speakUtterances(utterances, __resolveACSS(acss))

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

def shutdown():
    global __speechserver
    if __speechserver:
        __speechserver.shutdown()
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
        infos = factory.SpeechServer.getSpeechServerInfos()
        for info in infos:
            try:
                server = factory.SpeechServer.getSpeechServer(info)
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
