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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import acss
import settings
import speech
import speechserver
import orca_prefs
import platform
import time

desktopRunning = False
try:
    import gtk
    if gtk.gdk.display_get_default():
        desktopRunning = True
except:
    pass

from orca_i18n import _  # for gettext support

workingFactories   = []
speechServerChoice = None
speechVoiceChoice  = None

def sayAndPrint(text,
                stop=False,
                getInput=False,
                speechServer=None,
                acss=None):
    """Prints the given text.  In addition, if the text field
    is not None, speaks the given text, optionally interrupting
    anything currently being spoken.

    Arguments:
    - text: the text to print and speak
    - stop: if True, interrupt any speech currently being spoken
    - getInput: if True, elicits raw input from the user and returns it
    - speechServer: the speech server to use
    - acss: the ACSS to use for speaking

    Returns raw input from the user if getInput is True.
    """

    if stop:
        speech.stop()
        if speechServer:
            speechServer.stop()

    if speechServer:
        speechServer.speak(text, acss)
    else:
        speech.speak(text, acss)

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

    global workingFactories
    global speechServerChoice
    global speechVoiceChoice

    # Use this because callbacks will often hang when not running
    # with bonobo main in use.
    #
    settings.enableSpeechCallbacks = False

    factories = speech.getSpeechServerFactories()
    if len(factories) == 0:
        print _("Speech is unavailable.")
        return False

    speech.init()
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
        print _("Speech is unavailable.")
        return False
    elif len(workingFactories) > 1:
        sayAndPrint(_("Select desired speech system:"))
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
        [factory, servers] = choices[choice]
    else:
        [factory, servers] = workingFactories[0]

    if len(servers) == 0:
        sayAndPrint(_("No servers available.\n"))
        sayAndPrint(_("Speech will not be used.\n"))
        return False
    if len(servers) > 1:
        sayAndPrint(_("Select desired speech server."),
                    len(workingFactories) > 1)
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
        speechServerChoice = choices[choice]
    else:
        speechServerChoice = servers[0]

    families = speechServerChoice.getVoiceFamilies()
    if len(families) == 0:
        sayAndPrint(_("No voices available.\n"))
        sayAndPrint(_("Speech will not be used.\n"))
        return False
    if len(families) > 1:
        sayAndPrint(_("Select desired voice:"),
                    True,               # stop
                    False,              # getInput
                    speechServerChoice) # server
        i = 1
        choices = {}
        for family in families:
            name = family[speechserver.VoiceFamily.NAME]
            voice = acss.ACSS({acss.ACSS.FAMILY : family})
            sayAndPrint(_("%d. %s") % (i, name),
                        False,              # stop
                        False,              # getInput
                        speechServerChoice, # speech server
                        voice)              # voice
            choices[i] = voice
            i += 1
        choice = int(sayAndPrint(_("Enter choice: "),
                                 False,               # stop
                                 True,                # getInput
                                 speechServerChoice)) # speech server
        if (choice <= 0) or (choice >= i):
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
    defaultACSS[acss.ACSS.GAIN] = 9
    defaultACSS[acss.ACSS.AVERAGE_PITCH] = 5
    uppercaseACSS = acss.ACSS({acss.ACSS.AVERAGE_PITCH : 6})
    hyperlinkACSS = acss.ACSS({})

    voices = {
        settings.DEFAULT_VOICE   : defaultACSS,
        settings.UPPERCASE_VOICE : uppercaseACSS,
        settings.HYPERLINK_VOICE : hyperlinkACSS
    }

    prefsDict["enableSpeech"] = True
    prefsDict["speechServerFactory"] = factory
    prefsDict["speechServerInfo"] = speechServerChoice
    prefsDict["voices"] = voices

    # Ask the user if they would like to enable echoing by word.
    #
    answer = sayAndPrint(_("Enable echo by word?  Enter y or n: "),
                         True,
                         True,
                         speechServerChoice,
                         speechVoiceChoice)
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
    answer = sayAndPrint(_("Enable key echo?  Enter y or n: "),
                         True,
                         True,
                         speechServerChoice,
                         speechVoiceChoice)
    if answer[0:1] == 'Y' or answer[0:1] == 'y':
        prefsDict["enableKeyEcho"] = True
        answer = sayAndPrint(_("Enable alphanumeric and punctuation keys?  Enter y or n: "),
                             True,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enablePrintableKeys"] = state

        answer = sayAndPrint(_("Enable modifier keys?  Enter y or n: "),
                             True,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableModifierKeys"] = state

        answer = sayAndPrint(_("Enable locking keys?  Enter y or n: "),
                             True,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableLockingKeys"] = state

        answer = sayAndPrint(_("Enable function keys?  Enter y or n: "),
                             True,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableFunctionKeys"] = state

        answer = sayAndPrint(_("Enable action keys?  Enter y or n: "),
                             True,
                             True,
                             speechServerChoice,
                             speechVoiceChoice)
        state = answer[0:1] == 'Y' or answer[0:1] == 'y'
        prefsDict["enableActionKeys"] = state

    else:
        prefsDict["enableKeyEcho"]       = False
        prefsDict["enablePrintableKeys"] = False
        prefsDict["enableModifierKeys"]  = False
        prefsDict["enableLockingKeys"]   = False
        prefsDict["enableFunctionKeys"]  = False
        prefsDict["enableActionKeys"]    = False

    sayAndPrint(_("Select desired keyboard layout."),
                True,
                True,
                speechServerChoice,
                speechVoiceChoice)
    i = 1
    choices = {}
    sayAndPrint(_("1. Desktop"))
    sayAndPrint(_("2. Laptop"))
    choice = int(sayAndPrint(_("Enter choice: "), False, True))
    if choice == 2:
        prefsDict["keyboardLayout"] = settings.GENERAL_KEYBOARD_LAYOUT_LAPTOP
        prefsDict["orcaModifierKeys"] = settings.LAPTOP_MODIFIER_KEYS
    else:
        prefsDict["keyboardLayout"] = settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
        prefsDict["orcaModifierKeys"] = settings.DESKTOP_MODIFIER_KEYS
    if (choice <= 0) or (choice >= 3):
        sayAndPrint(_("Invalid choice. Selecting desktop keyboard layout.\n"))

    return True

def logoutUser():
    """Automatically log the user out of the GNOME desktop."""

    import gnome
    import gnome.ui

    program = gnome.init(platform.package, platform.version)
    client = gnome.ui.master_client()

    client.request_save(gnome.ui.SAVE_GLOBAL,  # Save style
                        True,                  # Shutdown
                        gnome.ui.INTERACT_ANY, # Allow user interaction
                        False,                 # Fast
                        True)                  # All apps save state

def showPreferencesUI():
    """Uses the console to query the user for Orca preferences."""

    prefsDict = {}

    if not setupSpeech(prefsDict):
        prefsDict["enableSpeech"]     = False
        prefsDict["enableEchoByWord"] = False
        prefsDict["enableKeyEcho"]    = False

    answer = sayAndPrint(_("Enable Braille?  Enter y or n: "),
                         True,
                         True,
                         speechServerChoice,
                         speechVoiceChoice)
    state = answer[0:1] == 'Y' or answer[0:1] == 'y'
    prefsDict["enableBraille"] = state

    answer = sayAndPrint(_("Enable Braille Monitor?  Enter y or n: "),
                         True,
                         True,
                         speechServerChoice,
                         speechVoiceChoice)
    state = answer[0:1] == 'Y' or answer[0:1] == 'y'
    prefsDict["enableBrailleMonitor"] = state

    logoutNeeded = orca_prefs.writePreferences(prefsDict)
    if logoutNeeded:
        sayAndPrint(_("Accessibility support for GNOME has just been enabled. "),
                    logoutNeeded,
                    False,
                    speechServerChoice,
                    speechVoiceChoice)
        sayAndPrint(_("You need to log out and log back in for the change to take effect. "),
                    False,
                    False,
                    speechServerChoice,
                    speechVoiceChoice)

        if desktopRunning:
            answer = sayAndPrint(_("Do you want to logout now?  Enter y or n: "),
                                 False,
                                 True,
                                 speechServerChoice,
                                 speechVoiceChoice)
            if answer[0:1] == 'Y' or answer[0:1] == 'y':
                sayAndPrint(_("Setup complete. Logging out now."),
                            False,
                            False,
                            speechServerChoice,
                            speechVoiceChoice)
                time.sleep(2)

                import bonobo
                import gobject

                gobject.threads_init()
                gobject.idle_add(logoutUser)
                bonobo.main()

    answer = sayAndPrint(_("Setup complete.  Press Return to continue."),
                         not logoutNeeded,
                         True,
                         speechServerChoice,
                         speechVoiceChoice)

    for [factory, servers] in workingFactories:
        factory.SpeechServer.shutdownActiveServers()

def main():
    showPreferencesUI()

if __name__ == "__main__":
    main()
