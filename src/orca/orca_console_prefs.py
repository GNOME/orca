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
from . import settings
from . import speech
from . import speechserver

from .orca_i18n import _

workingFactories   = []
speechServerChoice = None
speechVoiceChoice  = None

# Translators: this is a regular expression that is intended to match
# a positive 'yes' response from a user at the command line.  The expression
# as given means - does it begin with (that's the '^' character) any of
# the characters in the '[' ']'?  In this case, we've chosen 'Y', 'y', and
# '1' to mean positive answers, so any string beginning with 'Y', 'y', or
# '1' will match.  For an example of translation, assume your language has
# the words 'posolutely' and 'absitively' as common words that mean the
# equivalent of 'yes'.  You might make the expression match the upper and
# lower case forms: "^[aApP1]".  If the 'yes' and 'no' words for your
# locale begin with the same character, the regular expression should be
# modified to use words.  For example: "^(yes|Yes)" (note the change from
# using '[' and ']' to '(' and ')').
#
# Finally, this expression should match what you've chosen for the
# translation of the "Enter y or n:" strings for this file.
#
YESEXPR = re.compile(_("^[Yy1]"))
NOEXPR = re.compile(_("^[Nn0]"))

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
        return raw_input(text)
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

    # Use this because callbacks in this setup can hang.
    # TODO: Is this true still??
    #
    settings.enableSpeechCallbacks = False

    factories = speech.getSpeechServerFactories()
    if len(factories) == 0:
        # Translators: this means speech synthesis (i.e., the machine
        # speaks to you from its speakers) is not installed or working.
        #
        print(_("Speech is unavailable."))
        return False

    try:
        speech.init()
    except:
        # Translators: this means speech synthesis (i.e., the machine
        # speaks to you from its speakers) is not installed or working.
        #
        print(_("Speech is unavailable."))
        return False

    sayAndPrint(_("Welcome to Orca setup."))

    workingFactories = []
    for factory in factories:
        try:
            servers = factory.SpeechServer.getSpeechServers()
            if len(servers):
                workingFactories.append([factory, servers])
        except:
            pass

    if len(workingFactories) == 0:
        # Translators: this means speech synthesis (i.e., the machine
        # speaks to you from its speakers) is not installed or working.
        #
        print(_("Speech is unavailable."))
        return False
    elif len(workingFactories) > 1:
        # Translators: the speech system represents what general
        # speech wrapper is going to be used.  Speech-dispatcher
        # is an example of a speech system. It provides wrappers
        # around specific speech servers (engines).
        #
        sayAndPrint(_("Select desired speech system:"))
        choices = {}
        i = 1
        for workingFactory in workingFactories:
            choices[i] = workingFactory
            sayAndPrint("%d. %s" \
                        % (i, workingFactory[0].SpeechServer.getFactoryName()))
            i += 1

        # Translators: this is prompting for a numerical choice.
        #
        while True:
            try:
                choice = int(sayAndPrint(_("Enter choice: "), False, True))
                break
            except:
                # Translators: this is letting the user they input an
                # invalid integer value on the command line and is
                # also requesting they enter a valid integer value.
                #
                sayAndPrint(_("Please enter a valid number."))
        if (choice <= 0) or (choice >= i):
            # Translators: this means speech synthesis will not be used.
            #
            sayAndPrint(_("Speech will not be used.\n"))
            return False
        [factory, servers] = choices[choice]
    else:
        [factory, servers] = workingFactories[0]

    if len(servers) == 0:
        # Translators: this means no working speech servers (speech
        # synthesis engines) can be found.
        #
        sayAndPrint(_("No servers available.\n"))
        sayAndPrint(_("Speech will not be used.\n"))
        return False
    if len(servers) > 1:
        # Translators: this is prompting for a numerical choice from a list
        # of available speech synthesis engines.
        #
        sayAndPrint(_("Select desired speech server."),
                    len(workingFactories) > 1)
        i = 1
        choices = {}
        for server in servers:
            sayAndPrint("%d. %s" % (i, server.getInfo()[0]))
            choices[i] = server
            i += 1

        # Translators: this is prompting for a numerical choice.
        #
        while True:
            try:
                choice = int(sayAndPrint(_("Enter choice: "), False, True))
                break
            except:
                sayAndPrint(_("Please enter a valid number."))
        if (choice <= 0) or (choice >= i):
            # Translators: this means speech synthesis will not be used.
            #
            sayAndPrint(_("Speech will not be used.\n"))
            return False
        speechServerChoice = choices[choice]
    else:
        speechServerChoice = servers[0]

    families = speechServerChoice.getVoiceFamilies()
    if len(families) == 0:
        # Translators: this means the speech server (speech synthesis
        # engine) is not working properly and no voices (e.g., male,
        # female, child) are available.
        #
        sayAndPrint(_("No voices available.\n"))

        # Translators: this means speech synthesis will not be used.
        #
        sayAndPrint(_("Speech will not be used.\n"))
        return False
    if len(families) > 1:
        # Translators: this is prompting for a numerical value from a
        # list of choices of speech synthesis voices (e.g., male,
        # female, child).
        #
        sayAndPrint(_("Select desired voice:"),
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
                # Translators: this is prompting for a numerical choice.
                #
                choice = int(sayAndPrint(_("Enter choice: "),
                                         False,               # stop
                                         True,                # getInput
                                         speechServerChoice)) # speech server
                break
            except:
                sayAndPrint(_("Please enter a valid number."))
        if (choice <= 0) or (choice >= i):
            # Translators: this means speech synthesis will not be used.
            #
            sayAndPrint(_("Speech will not be used.\n"))
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
    uppercaseACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 6})
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
        # Translators: the word echo feature of Orca will speak the
        # word prior to the caret when the user types a word
        # delimiter.
        #
        answer = sayAndPrint(_("Enable echo by word?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableEchoByWord"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    stop = True
    while True:
        # Translators: if key echo is enabled, Orca will speak the
        # name of a key as the user types on the keyboard.  If the
        # user wants key echo, they will then be prompted for which
        # classes of keys they want echoed.
        #
        answer = sayAndPrint(_("Enable key echo?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                         speechVoiceChoice)
        try:
            prefsDict["enableKeyEcho"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    keyEcho = prefsDict["enableKeyEcho"]
    if not keyEcho:
        prefsDict["enableKeyEcho"]       = False
        prefsDict["enablePrintableKeys"] = False
        prefsDict["enableModifierKeys"]  = False
        prefsDict["enableFunctionKeys"]  = False
        prefsDict["enableActionKeys"]    = False

    stop = True
    while keyEcho and True:
        # Translators: this is in reference to key echo for
        # normal text entry keys.
        #
        answer = sayAndPrint( \
            _("Enable alphanumeric and punctuation keys?  Enter y or n: "),
            stop,
            True,
            speechServerChoice,
            speechVoiceChoice)
        try:
            prefsDict["enablePrintableKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    stop = True
    while keyEcho and True:
        # Translators: this is in reference to key echo for
        # CTRL, ALT, Shift, Insert, and "Fn" on laptops.
        #
        answer = sayAndPrint(_("Enable modifier keys?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableModifierKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    stop = True
    while keyEcho and True:
        # Translators: this is in reference to key echo for
        # the keys at the top of the keyboard.
        #
        answer = sayAndPrint(_("Enable function keys?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableFunctionKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    stop = True
    while keyEcho and True:
        # Translators: this is in reference to key echo for
        # space, enter, escape, tab, backspace, delete, arrow
        # keys, page up, page down, etc.
        #
        answer = sayAndPrint(_("Enable action keys?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableActionKeys"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    # Translators: we allow the user to choose between the desktop (i.e.,
    # has a numeric keypad) and laptop (i.e., small and compact) keyboard
    # layouts for how they might control Orca.
    #
    sayAndPrint(_("Select desired keyboard layout."),
                True,
                False,
                speechServerChoice,
                speechVoiceChoice)
    i = 1
    choices = {}

    # Translators: we allow the user to choose between the desktop (i.e.,
    # has a numeric keypad) and laptop (i.e., small and compact) keyboard
    # layouts for how they might control Orca.
    #
    sayAndPrint(_("1. Desktop"),
                False, False, speechServerChoice, speechVoiceChoice)

    # Translators: we allow the user to choose between the desktop (i.e.,
    # has a numeric keypad) and laptop (i.e., small and compact) keyboard
    # layouts for how they might control Orca.
    #
    sayAndPrint(_("2. Laptop"),
                False, False, speechServerChoice, speechVoiceChoice)

    while True:
        try:
            # Translators: this is prompting for a numerical choice.
            #
            choice = int(sayAndPrint(_("Enter choice: "),
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
                sayAndPrint(_("Please enter a valid number."))
        except:
            sayAndPrint(_("Please enter a valid number."))

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
        # Translators: this is prompting for whether the user wants to
        # use a refreshable braille display (an external hardware
        # device) or not.
        #
        answer = sayAndPrint(_("Enable Braille?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableBraille"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    stop = True
    while True:
        # Translators: the braille monitor is a graphical display on
        # the screen that is used for debugging and demoing purposes.
        # It presents what would be (or is being) shown on the
        # external refreshable braille display.
        #
        answer = sayAndPrint(_("Enable Braille Monitor?  Enter y or n: "),
                             stop,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        try:
            prefsDict["enableBrailleMonitor"] = checkYes(answer)
            break
        except:
            stop = False
            sayAndPrint(_("Please enter y or n."))

    stop = True

    # Sanity check for bug #642285
    #
    if 'profile' not in prefsDict:
        prefsDict['profile'] = settings.profile

    answer = sayAndPrint(_("Setup complete.  Press Return to continue."),
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
