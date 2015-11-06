# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Manages the default speech server for orca.  A script can use this
as its speech server, or it can feel free to create one of its own."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import importlib
import time

from . import debug
from . import logger
from . import orca_state
from . import settings
from . import speech_generator

from .acss import ACSS

_logger = logger.getLogger()
log = _logger.newLog("speech")

# The speech server to use for all speech operations.
#
_speechserver = None

def getSpeechServerFactories():
    """Imports all known SpeechServer factory modules.  Returns a list
    of modules that implement the getSpeechServers method, which
    returns a list of speechserver.SpeechServer instances.
    """

    factories = []

    moduleNames = settings.speechFactoryModules
    for moduleName in moduleNames:
        try:
            module = importlib.import_module('orca.%s' % moduleName)
            factories.append(module)
        except:
            debug.printException(debug.LEVEL_CONFIGURATION)

    return factories

def _initSpeechServer(moduleName, speechServerInfo):

    global _speechserver

    if not moduleName:
        return

    debug.println(debug.LEVEL_CONFIGURATION,
                  "Trying to use speech server factory: %s" % moduleName)

    factory = None
    try:
        factory = importlib.import_module('orca.%s' % moduleName)
    except:
        try:
            factory = importlib.import_module(moduleName)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    # Now, get the speech server we care about.
    #
    speechServerInfo = settings.speechServerInfo
    if speechServerInfo:
        _speechserver = factory.SpeechServer.getSpeechServer(speechServerInfo)

    if not _speechserver:
        _speechserver = factory.SpeechServer.getSpeechServer()
        if speechServerInfo:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Invalid speechServerInfo: %s" % speechServerInfo)

    if not _speechserver:
        raise Exception("No speech server for factory: %s" % moduleName)

def init():

    if _speechserver:
        return

    try:
        moduleName = settings.speechServerFactory
        _initSpeechServer(moduleName,
                          settings.speechServerInfo)
    except:
        moduleNames = settings.speechFactoryModules
        for moduleName in moduleNames:
            if moduleName != settings.speechServerFactory:
                try:
                    _initSpeechServer(moduleName, None)
                    if _speechserver:
                        break
                except:
                    debug.printException(debug.LEVEL_SEVERE)

    if _speechserver:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Using speech server factory: %s" % moduleName)
    else:
        debug.println(debug.LEVEL_CONFIGURATION, "Speech not available.")

def __resolveACSS(acss=None):
    if acss:
        return acss
    else:
        voices = settings.voices
        return ACSS(voices[settings.DEFAULT_VOICE])

def sayAll(utteranceIterator, progressCallback):
    if settings.silenceSpeech:
        return
    if _speechserver:
        _speechserver.sayAll(utteranceIterator, progressCallback)
    else:
        for [context, acss] in utteranceIterator:
            logLine = "SPEECH OUTPUT: '" + context.utterance + "'"
            debug.println(debug.LEVEL_INFO, logLine)
            log.info(logLine)

def _speak(text, acss, interrupt):
    """Speaks the individual string using the given ACSS."""

    logLine = "SPEECH OUTPUT: '" + text + "'"
    extraDebug = ""
    if acss in list(settings.voices.values()):
        for key in settings.voices:
            if acss == settings.voices[key]:
                if key != settings.DEFAULT_VOICE:
                    extraDebug = " voice=%s" % key
                break

    debug.println(debug.LEVEL_INFO, logLine + extraDebug + str(acss))
    log.info(logLine + extraDebug)

    if _speechserver:
        voice = ACSS(settings.voices.get(settings.DEFAULT_VOICE))
        try:
            voice.update(acss)
        except:
            pass
        _speechserver.speak(text, __resolveACSS(voice), interrupt)

def speak(content, acss=None, interrupt=True):
    """Speaks the given content.  The content can be either a simple
    string or an array of arrays of objects returned by a speech
    generator."""

    if settings.silenceSpeech:
        return

    validTypes = (str, list, speech_generator.Pause,
                  speech_generator.LineBreak, ACSS)
    error = "bad content sent to speech.speak: '%s'"
    if not isinstance(content, validTypes):
        debug.printStack(debug.LEVEL_WARNING)
        debug.println(debug.LEVEL_WARNING, error % content)
        return

    if isinstance(content, str):
        _speak(content, acss, interrupt)
    if not isinstance(content, list):
        return

    toSpeak = []
    activeVoice = ACSS(acss)
    for element in content:
        if not isinstance(element, validTypes):
            debug.println(debug.LEVEL_WARNING, error % element)
        elif isinstance(element, list):
            speak(element, acss, interrupt)
        elif isinstance(element, str):
            if len(element):
                toSpeak.append(element)
        elif toSpeak:
            newVoice = ACSS(acss)
            newItemsToSpeak = []
            if isinstance(element, speech_generator.Pause):
                if not toSpeak[-1].endswith('.'):
                    toSpeak[-1] += '.'
            elif isinstance(element, ACSS):
                newVoice.update(element)
                if newVoice == activeVoice:
                    continue
                newItemsToSpeak.append(toSpeak.pop())

            if toSpeak:
                string = " ".join(toSpeak)
                _speak(string, activeVoice, interrupt)
            activeVoice = newVoice
            toSpeak = newItemsToSpeak

    if toSpeak:
        string = " ".join(toSpeak)
        _speak(string, activeVoice, interrupt)

def speakKeyEvent(event):
    """Speaks a key event immediately.

    Arguments:
    - event: input_event.KeyboardEvent to speak.
    """

    if settings.silenceSpeech:
        return

    keyname = event.getKeyName()
    lockingStateString = event.getLockingStateString()
    msg = "%s %s" % (keyname, lockingStateString)
    logLine = "SPEECH OUTPUT: '%s'" % msg
    debug.println(debug.LEVEL_INFO, logLine)
    log.info(logLine)

    if _speechserver:
        _speechserver.speakKeyEvent(event)

def speakCharacter(character, acss=None):
    """Speaks a single character immediately.

    Arguments:
    - character: text to be spoken
    - acss:      acss.ACSS instance; if None,
                 the default voice settings will be used.
                 Otherwise, the acss settings will be
                 used to augment/override the default
                 voice settings.
    """
    if settings.silenceSpeech:
        return

    debug.println(debug.LEVEL_INFO, "SPEECH OUTPUT: '" + character + "' " + str(acss))
    log.info("SPEECH OUTPUT: '%s'" % character)

    if _speechserver:
        _speechserver.speakCharacter(character, acss=acss)

def isSpeaking():
    """Returns True if the system is currently speaking."""
    if _speechserver:
        return _speechserver.isSpeaking()
    else:
        return False

def getInfo():
    info = None
    if _speechserver:
        info = _speechserver.getInfo()

    return info

def stop():
    if _speechserver:
        _speechserver.stop()

def updateCapitalizationStyle(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.updateCapitalizationStyle()

    return True

def updatePunctuationLevel(script=None, inputEvent=None):
    """ Punctuation level changed, inform this speechServer. """

    if _speechserver:
        _speechserver.updatePunctuationLevel()

    return True

def increaseSpeechRate(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.increaseSpeechRate()

    return True

def decreaseSpeechRate(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.decreaseSpeechRate()
    else:
        logLine = "SPEECH OUTPUT: 'slower'"
        debug.println(debug.LEVEL_INFO, logLine)
        log.info(logLine)

    return True

def increaseSpeechPitch(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.increaseSpeechPitch()

    return True

def decreaseSpeechPitch(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.decreaseSpeechPitch()

    return True

def increaseSpeechVolume(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.increaseSpeechVolume()
    return True

def decreaseSpeechVolume(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.decreaseSpeechVolume()
    return True

def shutdown():
    global _speechserver
    if _speechserver:
        _speechserver.shutdownActiveServers()
        _speechserver = None

def reset(text=None, acss=None):
    if _speechserver:
        _speechserver.reset(text, acss)

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
    from . import speechserver
    factories = getSpeechServerFactories()
    for factory in factories:
        print(factory.__name__)
        servers = factory.SpeechServer.getSpeechServers()
        for server in servers:
            try:
                print("    ", server.getInfo())
                for family in server.getVoiceFamilies():
                    name = family[speechserver.VoiceFamily.NAME]
                    print("      ", name)
                    acss = ACSS({ACSS.FAMILY : family})
                    server.speak(name, acss)
                    server.speak("testing")
                server.shutdown()
            except:
                debug.printException(debug.LEVEL_OFF)
