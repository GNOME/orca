# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Manages the default speech server for orca.  A script can use this
as its speech server, or it can feel free to create one of its own."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import logging
log = logging.getLogger("speech")

import re
import time

import chnames
import debug
import keynames
import orca
import orca_state
import settings
import sound
import speech_generator

from acss import ACSS
from orca_i18n import _           # for gettext support

# The speech server to use for all speech operations.
#
_speechserver = None

# regular expressions for multiCaseStrings
#
multiCaseReg1 = re.compile("([a-z]+)([A-Z])")
multiCaseReg2 = re.compile("([A-Z][A-Z]+)([A-Z][a-z]+)")
multiCaseReg3 = re.compile("([A-Z])([A-Z][a-z]+)")

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

    global _speechserver

    if _speechserver:
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
            moduleName = moduleName.replace("orca.", "", 1)
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
        _speechserver = factory.SpeechServer.getSpeechServer(speechServerInfo)
    else:
        _speechserver = factory.SpeechServer.getSpeechServer()

def __resolveACSS(acss=None):
    if acss:
        return acss
    else:
        voices = settings.voices
        return voices[settings.DEFAULT_VOICE]

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

    if settings.speakMultiCaseStringsAsWords:
        text = _processMultiCaseString(text)
    if orca_state.activeScript and orca_state.usePronunciationDictionary:
        text = orca_state.activeScript.adjustForPronunciation(text)
    if settings.speakMultiCaseStringsAsWords:
        text = _processMultiCaseString(text)

    logLine = "SPEECH OUTPUT: '" + text + "'"
    extraDebug = ""
    if acss in settings.voices.values():
        for key in settings.voices:
            if acss == settings.voices[key]:
                if key != settings.DEFAULT_VOICE:
                    extraDebug = " voice=%s" % key
                break
    debug.println(debug.LEVEL_INFO, logLine + extraDebug)
    log.info(logLine + extraDebug)

    if _speechserver:
        _speechserver.speak(text, __resolveACSS(acss), interrupt)


def speak(content, acss=None, interrupt=True):
    """Speaks the given content.  The content can be either a simple
    string or an array of arrays of objects returned by a speech
    generator."""

    # We will not interrupt a key echo in progress.
    #
    if orca_state.lastKeyEchoTime:
        interrupt = interrupt \
            and ((time.time() - orca_state.lastKeyEchoTime) > 0.5)

    if settings.silenceSpeech:
        return

    subString = None
    if isinstance(content, basestring):
        subString = content
    elif isinstance(content, list):
        for element in content:
            if isinstance(element, basestring):
                if subString:
                    subString += " " + element
                else:
                    subString = element
            elif isinstance(element, speech_generator.Pause):
                if subString:
                    if subString[-1] != ".":
                        subString += "."
                    if settings.enablePauseBreaks:
                        _speak(subString, acss, interrupt)
                        subString = None
            elif isinstance(element, speech_generator.LineBreak):
                if subString:
                    _speak(subString, acss, interrupt)
                    subString = None
            elif isinstance(element, sound.Sound):
                if subString:
                    _speak(subString, acss, interrupt)
                    subString = None
                element.play()
            else:
                if subString:
                    _speak(subString, acss, interrupt)
                subString = None
                if isinstance(element, list):
                    speak(element, acss, interrupt)
                elif isinstance(element, ACSS):
                    acss = ACSS(acss)
                    acss.update(element)
                else:
                    debug.println(debug.LEVEL_WARNING,
                                  "UNKNOWN speech element: '%s'" % element)
    elif isinstance(content, sound.Sound):
        content.play()
    elif isinstance(content, (speech_generator.Pause,
                              speech_generator.LineBreak)):
        pass
    else:
        debug.printStack(debug.LEVEL_WARNING)
        debug.println(debug.LEVEL_WARNING, 
                      "bad content sent to speech.speak: '%s'" % repr(content))

    if subString:
        _speak(subString, acss, interrupt)

def speakKeyEvent(event_string, eventType):
    """Speaks a key event immediately.

    Arguments:
    - event_string: string representing the key event as defined by
                    input_event.KeyboardEvent.
    - eventType:    key event type as one of orca.KeyEventType constants.

    """
    if settings.silenceSpeech:
        return

    if _speechserver:
        _speechserver.speakKeyEvent(event_string, eventType)
    else:
        # Check to see if there are localized words to be spoken for
        # this key event.
        #
        event_string = keynames.getKeyName(event_string)

        if eventType == orca.KeyEventType.LOCKING_LOCKED:
            # Translators: this represents the state of a locking modifier
            # key (e.g., Caps Lock)
            #
            event_string += " " + _("on")
        elif eventType == orca.KeyEventType.LOCKING_UNLOCKED:
            # Translators: this represents the state of a locking modifier
            # key (e.g., Caps Lock)
            #
            event_string += " " + _("off")

        logLine = "SPEECH OUTPUT: '" + event_string +"'"
        debug.println(debug.LEVEL_INFO, logLine)
        log.info(logLine)

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

    spokenCharacter = chnames.getCharacterName(character)
    debug.println(debug.LEVEL_INFO, "SPEECH OUTPUT: '" + spokenCharacter + "'")
    log.info("SPEECH OUTPUT: '%s'" % spokenCharacter)

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

def increaseSpeechRate(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.increaseSpeechRate()
    else:
        logLine = "SPEECH OUTPUT: 'faster'"
        debug.println(debug.LEVEL_INFO, logLine)
        log.info(logLine)

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
    else:
        logLine = "SPEECH OUTPUT: 'higher'"
        debug.println(debug.LEVEL_INFO, logLine)
        log.info(logLine)

    return True

def decreaseSpeechPitch(script=None, inputEvent=None):
    if _speechserver:
        _speechserver.decreaseSpeechPitch()
    else:
        logLine = "SPEECH OUTPUT: 'lower'"
        debug.println(debug.LEVEL_INFO, logLine)
        log.info(logLine)

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

def _processMultiCaseString(string):
    """Helper function, applies the regexes to split multiCaseStrings
    to multiple words.
    """

    string = multiCaseReg1.sub('\\1 \\2', string)
    string = multiCaseReg2.sub('\\1 \\2', string)
    string = multiCaseReg3.sub('\\1 \\2', string)    
    return string
