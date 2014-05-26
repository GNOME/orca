# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Uses speech prompts and a command line interface to set Orca
user preferences."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import re
import sys

from . import acss
from . import messages
from . import settings
from . import speech
from . import speechserver

workingFactories   = []
speechServerChoice = None
speechVoiceChoice  = None
YESEXPR = re.compile(messages.CONSOLE_SETUP_YESEXPR)
NOEXPR = re.compile(messages.CONSOLE_SETUP_NOEXPR)

def checkYes(value) :
    """Checks if a string represents a yes, no.
    Arguments:
    - value: a string read from the console

    Returns True if the argument represents a yes
    """
    if YESEXPR.match(value) != None:
        return True
    elif NOEXPR.match(value) != None:
        return False
    else:
        raise ValueError

def sayAndPrint(text,
                stop=False,
                getInput=False,
                speechServer=None,
                voice=None):
    """Prints the given text.  In addition, if the text field
    is not None, speaks the given text, optionally interrupting
    anything currently being spoken.

    Arguments:
    - text: the text to print and speak
    - stop: if True, interrupt any speech currently being spoken
    - getInput: if True, elicits raw input from the user and returns it
    - speechServer: the speech server to use
    - voice: the ACSS to use for speaking

    Returns raw input from the user if getInput is True.
    """

    if stop:
        speech.stop()
        if speechServer:
            speechServer.stop()

    if speechServer:
        speechServer.speak(text, voice)
    else:
        speech.speak(text, voice)

    if getInput:
        return input(text)
    else:
        print(text)

def setupSpeech(prefsDict):
    """Sets up speech support.  If speech setup is successful and the
    user wants it, writes speech settings to the setting file and returns
    True.  If speech is not available, or the user doesn't want speech,
    returns False.
    """

    global workingFactories
    global speechServerChoice
    global speechVoiceChoice

    factories = speech.getSpeechServerFactories()
    if len(factories) == 0:
        print(messages.SPEECH_UNAVAILABLE)
        return False

    try:
        speech.init()
    except:
        print(messages.SPEECH_UNAVAILABLE)
        return False

    sayAndPrint(messages.CONSOLE_SETUP_START)

    workingFactories = []
    for factory in factories:
        try:
            servers = factory.SpeechServer.getSpeechServers()
            if len(servers):
                workingFactories.append([factory, servers])
        except:
            pass

    if len(workingFactories) == 0:
        print(messages.SPEECH_UNAVAILABLE)
        return False
    elif len(workingFactories) > 1:
        sayAndPrint(messages.CONSOLE_SETUP_SELECT_SPEECH_SYSTEM)
        choices = {}
        i = 1
        for workingFactory in workingFactories:
            choices[i] = workingFactory
            sayAndPrint("%d. %s" \
                        % (i, workingFactory[0].SpeechServer.getFactoryName()))
            i += 1
        while True:
            try:
                choice = int(sayAndPrint(messages.CONSOLE_SETUP_ENTER_CHOICE,
                                         False, True))
                break
            except:
                sayAndPrint(messages.CONSOLE_SETUP_ENTER_VALID_NUMBER)
        if (choice <= 0) or (choice >= i):
            sayAndPrint(messages.CONSOLE_SETUP_SPEECH_NOT_USED)
            return False
        [factory, servers] = choices[choice]
    else:
        [factory, servers] = workingFactories[0]

    if len(servers) == 0:
        sayAndPrint(messages.CONSOLE_SETUP_SERVERS_NOT_AVAILABLE)
        sayAndPrint(messages.CONSOLE_SETUP_SPEECH_NOT_USED)
        return False
    if len(servers) > 1:
        sayAndPrint(messages.CONSOLE_SETUP_SELECT_SPEECH_SERVER,
                    len(workingFactories) > 1)
        i = 1
        choices = {}
        for server in servers:
            sayAndPrint("%d. %s" % (i, server.getInfo()[0]))
            choices[i] = server
            i += 1
        while True:
            try:
                choice = int(sayAndPrint(messages.CONSOLE_SETUP_ENTER_CHOICE,
                                         False, True))
                break
            except:
                sayAndPrint(messages.CONSOLE_SETUP_ENTER_VALID_NUMBER)
        if (choice <= 0) or (choice >= i):
            sayAndPrint(messages.CONSOLE_SETUP_SPEECH_NOT_USED)
            return False
        speechServerChoice = choices[choice]
    else:
        speechServerChoice = servers[0]

    families = speechServerChoice.getVoiceFamilies()
    if len(families) == 0:
        sayAndPrint(messages.CONSOLE_SETUP_VOICES_NOT_AVAILABLE)
        sayAndPrint(messages.CONSOLE_SETUP_SPEECH_NOT_USED)
        return False
    if len(families) > 1:

        sayAndPrint(messages.CONSOLE_SETUP_SELECT_VOICE,
                    True,               # stop
                    False,              # getInput
                    speechServerChoice) # server
        i = 1
        choices = {}
        for family in families:
            name = family[speechserver.VoiceFamily.NAME] \
                + " (%s)" %  family[speechserver.VoiceFamily.LOCALE]
            voice = acss.ACSS({acss.ACSS.FAMILY : family})
            sayAndPrint("%d. %s" % (i, name),
                        False,              # stop
                        False,              # getInput
                        speechServerChoice, # speech server
                        voice)              # voice
            choices[i] = voice
            i += 1

        while True:
            try:
                choice = int(sayAndPrint(messages.CONSOLE_SETUP_ENTER_CHOICE,
                                         False,               # stop
                                         True,                # getInput
                                         speechServerChoice)) # speech server
                break
            except:
                sayAndPrint(messages.CONSOLE_SETUP_ENTER_VALID_NUMBER)
        if (choice <= 0) or (choice >= i):
            sayAndPrint(messages.CONSOLE_SETUP_SPEECH_NOT_USED)
            return False
        defaultACSS = choices[choice]
    else:
        defaultACSS = acss.ACSS({acss.ACSS.FAMILY : families[0]})

    speechVoiceChoice = defaultACSS

    # Force the rate to 50 so it will be set to something
    # and output to the user settings file.  50 is chosen
    # here, BTW, since it is the default value.  The same
    # goes for gain (volume) and average-pitch, but they
    # range from 0-10 instead of 0-100.
    #
    defaultACSS[acss.ACSS.RATE] = 50
    defaultACSS[acss.ACSS.GAIN] = 100
    defaultACSS[acss.ACSS.AVERAGE_PITCH] = 5
    uppercaseACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 7})
    hyperlinkACSS = acss.ACSS({})
    systemACSS = acss.ACSS({})

    voices = {
        settings.DEFAULT_VOICE   : defaultACSS,
        settings.UPPERCASE_VOICE : uppercaseACSS,
        settings.HYPERLINK_VOICE : hyperlinkACSS,
        settings.SYSTEM_VOICE    : systemACSS
    }

    prefsDict["enableSpeech"] = True
    prefsDict["speechServerFactory"] = factory.__name__
    prefsDict["speechServerInfo"] = speechServerChoice.getInfo()
    prefsDict["voices"] = voices

    stop = True
    while True:
        answer = sayAndPrint(messages.CONSOLE_SETUP_ENABLE_ECHO_WORD,
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableEchoByWord"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    stop = True
    while True:
        answer = sayAndPrint(messages.CONSOLE_SETUP_ENABLE_ECHO_KEY,
                             stop,
                             True,
                             speechServerChoice,
                         speechVoiceChoice)
        try:
            prefsDict["enableKeyEcho"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    keyEcho = prefsDict["enableKeyEcho"]
    if not keyEcho:
        prefsDict["enableKeyEcho"]       = False
        prefsDict["enablePrintableKeys"] = False
        prefsDict["enableModifierKeys"]  = False
        prefsDict["enableFunctionKeys"]  = False
        prefsDict["enableActionKeys"]    = False

    stop = True
    while keyEcho and True:
        answer = sayAndPrint(
            messages.CONSOLE_SETUP_ENABLE_ECHO_PRINTABLE_KEYS,
            stop,
            True,
            speechServerChoice,
            speechVoiceChoice)
        try:
            prefsDict["enablePrintableKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    stop = True
    while keyEcho and True:
        answer = sayAndPrint(messages.CONSOLE_SETUP_ENABLE_ECHO_MODIFIER_KEYS,
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableModifierKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    stop = True
    while keyEcho and True:
        answer = sayAndPrint(messages.CONSOLE_SETUP_ENABLE_ECHO_FUNCTION_KEYS,
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableFunctionKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    stop = True
    while keyEcho and True:
        answer = sayAndPrint(messages.CONSOLE_SETUP_ENABLE_ECHO_ACTION_KEYS,
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableActionKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    sayAndPrint(messages.CONSOLE_SETUP_SELECT_KEYBOARD_LAYOUT,
                True,
                False,
                speechServerChoice,
                speechVoiceChoice)
    i = 1
    choices = {}
    sayAndPrint(messages.CONSOLE_SETUP_KEYBOARD_LAYOUT_DESKTOP,
                False, False, speechServerChoice, speechVoiceChoice)
    sayAndPrint(messages.CONSOLE_SETUP_KEYBOARD_LAYOUT_LAPTOP,
                False, False, speechServerChoice, speechVoiceChoice)

    while True:
        try:
            choice = int(sayAndPrint(messages.CONSOLE_SETUP_ENTER_CHOICE,
                         False, True, speechServerChoice, speechVoiceChoice))
            if choice == 2:
                prefsDict["keyboardLayout"] = \
                    settings.GENERAL_KEYBOARD_LAYOUT_LAPTOP
                prefsDict["orcaModifierKeys"] = \
                    settings.LAPTOP_MODIFIER_KEYS
                break
            elif choice == 1:
                prefsDict["keyboardLayout"] = \
                    settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
                prefsDict["orcaModifierKeys"] = \
                    settings.DESKTOP_MODIFIER_KEYS
                break
            else:
                sayAndPrint(messages.CONSOLE_SETUP_ENTER_VALID_NUMBER)
        except:
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_VALID_NUMBER)

    return True

def showPreferencesUI(commandLineSettings):
    """Uses the console to query the user for Orca preferences."""

    prefsDict = {}

    if ("enableSpeech" in commandLineSettings and \
        not commandLineSettings["enableSpeech"]) or \
       (not setupSpeech(prefsDict)):
        prefsDict["enableSpeech"]     = False
        prefsDict["enableEchoByWord"] = False
        prefsDict["enableKeyEcho"]    = False

    stop = True
    while True:
        answer = sayAndPrint(messages.CONSOLE_SETUP_ENABLE_BRAILLE,
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableBraille"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(messages.CONSOLE_SETUP_ENTER_Y_OR_N)

    stop = True

    # Sanity check for bug #642285
    #
    if 'profile' not in prefsDict:
        prefsDict['profile'] = settings.profile
    answer = sayAndPrint(messages.CONSOLE_SETUP_COMPLETE,
                         True,
                         True,
                         speechServerChoice,
                         speechVoiceChoice)

    for [factory, servers] in workingFactories:
        factory.SpeechServer.shutdownActiveServers()

def main():
    showPreferencesUI(sys.argv[1:])

if __name__ == "__main__":
    main()
