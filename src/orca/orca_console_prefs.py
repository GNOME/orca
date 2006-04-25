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

"""Uses speech prompts and a command line interface to set Orca
user preferences."""

import acss
import settings
import speech
import speechserver
import orca_prefs

from orca_i18n import _  # for gettext support

def sayAndPrint(text, stop=False, getInput=False):
    """Prints the given text.  In addition, if the text field
    is not None, speaks the given text, optionally interrupting
    anything currently being spoken.

    Arguments:
    - text: the text to print and speak
    - stop: if True, interrupt any speech currently being spoken
    - getInput: if True, elicits raw input from the user and returns it

    Returns raw input from the user if getInput is True.
    """

    if stop:
        speech.stop()

    speech.speak(text)

    if getInput:
        return raw_input(text)
    else:
        print text

def setupSpeech(prefsDict):
    """Sets up speech support.  If speech setup is successful and the
    user wants it, writes speech settings to the setting file and returns
    True.  If speech is not available, or the user doesn't want speech,
    returns False.
    """

    # Use this because callbacks will often hang when not running
    # with bonobo main in use.
    #
    settings.enableSpeechCallbacks = False

    factories = speech.getSpeechServerFactories()
    if len(factories) == 0:
        print _("Speech is unavailable.")
        return False

    speech.init()
    speech.speak(_("Welcome to Orca setup."))

    workingFactories = []
    for factory in factories:
        try:
            infos = factory.SpeechServer.getSpeechServerInfos()
            workingFactories.append([factory, infos])
        except:
            pass

    if len(workingFactories) == 0:
        print _("Speech is unavailable.")
        return False
    elif len(workingFactories) > 1:
        speech.speak(_("Select desired speech system."))
        choices = {}
        i = 1
        for workingFactory in workingFactories:
            choices[i] = workingFactory
            sayAndPrint(_("%d. %s")
                        % (i, workingFactory[0].SpeechServer.getFactoryName()))
            i += 1
        choice = int(sayAndPrint(_("Enter choice: "), False, True))
        if (choice <= 0) or (choice >= i):
            sayAndPrint(_("Speech will not be used.\n"))
            return False
        [factory, infos] = choices[choice]
    else:
        [factory, infos] = workingFactories[0]

    servers = []
    for info in infos:
        try:
            server = factory.SpeechServer.getSpeechServer(info)
            if server:
                servers.append(server)
        except:
            pass

    if len(servers) == 0:
        sayAndPrint(_("No servers available.\n"))
        sayAndPrint(_("Speech will not be used.\n"))
        return False
    if len(servers) > 1:
        speech.stop()
        speech.speak(_("Select desired speech server."))
        i = 1
        choices = {}
        for server in servers:
            sayAndPrint(_("%d. %s") % (i, server.getInfo()[0]))
            choices[i] = server
            i += 1
        choice = int(sayAndPrint(_("Enter choice: "), False, True))
        if (choice <= 0) or (choice >= i):
            sayAndPrint(_("Speech will not be used.\n"))
            return False
        server = choices[choice]
    else:
        server = servers[0]

    families = server.getVoiceFamilies()
    if len(families) == 0:
        sayAndPrint(_("No voices available.\n"))
        sayAndPrint(_("Speech will not be used.\n"))
        return False
    if len(families) > 1:
        speech.stop()
        speech.speak(_("Select desired voice."))
        i = 1
        choices = {}
        for family in families:
            name = family[speechserver.VoiceFamily.NAME]
            voice = acss.ACSS({acss.ACSS.FAMILY : family})
            sayAndPrint(_("%d. %s") % (i, name))
            choices[i] = voice
            i += 1
        choice = int(sayAndPrint(_("Enter choice: "), False, True))
        if (choice <= 0) or (choice >= i):
            sayAndPrint(_("Speech will not be used.\n"))
            return False
        defaultACSS = choices[choice]
    else:
        defaultACSS = acss.ACSS({acss.ACSS.FAMILY : families[0]})

    # Force the rate to 50 so it will be set to something
    # and output to the user settings file.  50 is chosen
    # here, BTW, since it is the default value.  The same
    # goes for gain (volume) and average-pitch, but they
    # range from 0-10 instead of 0-100.
    #
    defaultACSS[acss.ACSS.RATE] = 50
    defaultACSS[acss.ACSS.GAIN] = 9
    defaultACSS[acss.ACSS.AVERAGE_PITCH] = 5
    uppercaseACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 6})
    hyperlinkACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 2})

    voices = {
        settings.DEFAULT_VOICE   : defaultACSS,
        settings.UPPERCASE_VOICE : uppercaseACSS,
        settings.HYPERLINK_VOICE : hyperlinkACSS
    }

    prefsDict["enableSpeech"] = True
    prefsDict["speechServerFactory"] = factory
    prefsDict["speechServerInfo"] = server
    prefsDict["voices"] = voices

    # Ask the user if they would like to enable echoing by word.
    #
    answer = sayAndPrint(_("Enable echo by word?  Enter y or n: "),
                         True, True)
    state = answer[0:1] == 'Y' or answer[0:1] == 'y'
    prefsDict["enableEchoByWord"] = state

    # Ask the user if they would like to enable key echo. If they say
    # yes, then for each of the five different types of keys, ask the
    # user if they would like to enable them.
    #
    # These key types are:
    #
    #   o Alphanumeric and punctuation keys
    #
    #   o Modifier keys: CTRL, ALT, Shift, Insert, and "Fn" on laptops.
    #
    #   o Locking keys: Caps Lock, Num Lock, Scroll Lock, etc.
    #
    #   o Function keys: The keys at the top of the keyboard.
    #
    #   o Action keys: space, enter, escape, tab, backspace, delete, arrow
    #     keys, page up, page down, etc.
    #
    answer = sayAndPrint(_("Enable key echo?  Enter y or n: "), True, True)
    if answer[0:1] == 'Y' or answer[0:1] == 'y':
        prefsDict["enableKeyEcho"] = True
        answer = sayAndPrint(_("Enable alphanumeric and punctuation keys?  Enter y or n: "),
                             True, True)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enablePrintableKeys"] = state

        answer = sayAndPrint(_("Enable modifier keys?  Enter y or n: "),
                             True, True)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableModifierKeys"] = state

        answer = sayAndPrint(_("Enable locking keys?  Enter y or n: "),
                             True, True)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableLockingKeys"] = state

        answer = sayAndPrint(_("Enable function keys?  Enter y or n: "),
                             True, True)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableFunctionKeys"] = state

        answer = sayAndPrint(_("Enable action keys?  Enter y or n: "),
                             True, True)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableActionKeys"] = state

    else:
        prefsDict["enableKeyEcho"]       = False
        prefsDict["enablePrintableKeys"] = False
        prefsDict["enableModifierKeys"]  = False
        prefsDict["enableLockingKeys"]   = False
        prefsDict["enableFunctionKeys"]  = False
        prefsDict["enableActionKeys"]    = False

    return True

def showPreferencesUI():
    """Uses the console to query the user for Orca preferences."""

    prefsDict = {}

    if not setupSpeech(prefsDict):
        prefsDict["enableSpeech"]     = False
        prefsDict["enableEchoByWord"] = False
        prefsDict["enableKeyEcho"]    = False

    answer = sayAndPrint(_("Enable Braille?  Enter y or n: "),
                         True, True)
    state = answer[0:1] == 'Y' or answer[0:1] == 'y'
    prefsDict["enableBraille"] = state

    answer = sayAndPrint(_("Enable Braille Monitor?  Enter y or n: "),
                         True, True)
    state = answer[0:1] == 'Y' or answer[0:1] == 'y'
    prefsDict["enableBrailleMonitor"] = state

    if orca_prefs.writePreferences(prefsDict):
        sayAndPrint("Accessibility support for GNOME has just been enabled.")
        sayAndPrint("You need to log out and log back in for the change "\
                    +"to take effect.")

def main():
    showPreferencesUI()

if __name__ == "__main__":
    main()
