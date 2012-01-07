# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2010-2011 The Orca Team
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

"""The main module for the Orca screen reader."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2011 The Orca Team"
__license__   = "LGPL"

import getopt
import os
import subprocess
import re
import signal
import sys
import time
import shutil

from gi.repository.Gio import Settings
a11yAppSettings = Settings('org.gnome.desktop.a11y.applications')      

# We're going to force the name of the app to "orca" so we
# will end up showing us as "orca" to the AT-SPI.  If we don't
# do this, the name can end up being "-c".  See bug 364452 at
# http://bugzilla.gnome.org/show_bug.cgi?id=364452 for more
# information.
#
sys.argv[0] = "orca"
import pyatspi
try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    from gi.repository import Gtk
    from gi.repository import Gdk
except:
    pass

# Importing anything that requires a functioning settings manager
# instance should NOT be done here.
#
import debug
import orca_platform
import settings
from orca_i18n import _
from orca_i18n import ngettext

def onEnabledChanged(gsetting, key):
    try:
        enabled = gsetting.get_boolean(key)
    except:
        return

    if key == 'screen-reader-enabled' and not enabled:
        shutdown()

class Options:
    """Class to handle getting run-time options."""

    def __init__(self):
        """Initialize the Options class."""

        self._arglist = sys.argv[1:]
        if len(self._arglist) == 1:
            self._arglist = self._arglist[0].split()

        self.desktopRunning = False
        try:
            if Gdk.Display.get_default():
                self.desktopRunning = True
        except:
            pass

        self.canEnable = {'speech':'enableSpeech',
                          'braille':'enableBraille',
                          'braille-monitor':'enableBrailleMonitor',
                          'main-window':'showMainWindow',
                          'splash-window':'showSplashWindow'}

        self.invalidOptions = []
        self.settings = {}
        self.profiles = []
        self.disable = []
        self.enable = []
        self.cannotEnable = []
        self._validFeaturesPrinted = False
        self.setupRequested = False
        self.bypassSetup = False
        self.showGUI = False
        self.debug = False
        self.userPrefsDir = None
        self.debugFile = time.strftime('debug-%Y-%m-%d-%H:%M:%S.out')

        self.validOptions, self.validArguments = self.validate()
        self._getPrefsDir()
        self._getProfiles()
        self._getSetup()
        self._getDebug()
        self._getHelp()

    def validate(self):
        """Parses the list of options in arglist and removes those which are
        not valid so that typos do not prevent the user from starting Orca."""

        opts = []
        args = []

        # ? is for help
        # e is for enabling a feature
        # d is for disabling a feature
        # h is for help
        # u is for alternate user preferences location
        # s is for setup
        # n is for no setup
        # t is for text setup
        # v is for version
        # i is for importing a user profile
        #
        shortopts = "?stnvlmd:e:u:i:"
        longopts = ["help",
                    "user-prefs-dir=",
                    "enable=",
                    "disable=",
                    "setup",
                    "gui-setup",
                    "text-setup",
                    "no-setup",
                    "list-apps",
                    "debug",
                    "debug-file=",
                    "version",
                    "replace",
                    "import-file="]

        try:
            opts, args = getopt.getopt(self._arglist, shortopts, longopts)
        except getopt.GetoptError as ex:
            bogusOption = "-%s" % ex.opt
            if len(bogusOption) >= 2:
                bogusOption = "-%s" % bogusOption
            self.invalidOptions.append(bogusOption)
            try:
                self._arglist.remove(bogusOption)
            except:
                pass
            else:
                return self.validate()
        except:
            pass

        return opts, args

    def _get(self, optionsList):
        """Gets a subset of all of the valid options from the commandline.

        Arguments:
        - optionsList: a list of all of the options of interest.

        Returns a list of the matches.
        """

        return filter(lambda x: x[0] in optionsList, self.validOptions)

    def _getValues(self, optionsList, additionalFilter=None):
        """Gets the values for a subset of all of the valid options from
        the commandLine.

        Arguments:
        - optionsList: a list of all of the options of interest.
        - additionalFilter: an optional function which can be used to
          remove items which would otherwise be included.

        Returns a tuple containing two lists: the matches and the items
        which were filtered out.
        """

        opts = [x[1].strip() for x in self._get(optionsList)]
        rv = opts
        removed = []
        if additionalFilter:
            rv = filter(additionalFilter, opts)
            removed = filter(lambda x: x not in rv, opts)

        return rv, removed

    def _getEnableAndDisable(self):
        """Gets the options which are to be enabled and disabled and stores
        them in self.enable and self.disable, along with adding invalid items
        to the list in self.cannotEnable."""

        isValid = lambda x: self.canEnable.get(x) != None
        self.enable, invalid = self._getValues(["-e", "--enable"], isValid)
        self.cannotEnable.extend(invalid)
        self.disable, invalid = self._getValues(["-d", "--disable"], isValid)
        self.cannotEnable.extend(invalid)

    def _getPrefsDir(self):
        """Returns the preferences directory specified by the user."""

        userPrefsDir = None
        dirs, removed = self._getValues(["-u", "--user-prefs-dir"])
        if len(dirs):
            userPrefsDir = dirs[0]
            try:
                os.chdir(userPrefsDir)
            except:
                debug.printException(debug.LEVEL_FINEST)

        self.userPrefsDir = userPrefsDir

    def _getSetup(self):
        """Gets the options associated with setting up Orca and stores them
        in self.setupRequested, self.showGUI, and self.bypassSetup."""

        gui = self._get(["-s", "--gui-setup", "--setup"])
        text = self._get(["-t", "--text-setup"])
        bypass = self._get(["-n", "--no-setup"])

        if gui or text:
            self.setupRequested = True
            self.showGUI = self.desktopRunning and not text

        if bypass:
            self.bypassSetup = True

    def _getDebug(self):
        """Gets the options associated with debugging Orca and stores them
        in self.debug and self.debugFile."""

        noFile = self._get(["--debug"])
        debugFile = ["--debug-file"]
        withFile = self._get(debugFile)
        files, invalid = self._getValues(debugFile)

        if noFile or withFile:
            self.debug = True
            if files:
                self.debugFile = files[0]

    def _getHelp(self):
        """Gets the options associated with Orca help. If there are any,
        the corresponding help information will be printed and this instance
        of Orca exited."""

        isHelp = self._get(["-?", "--help"])
        isVersion = self._get(["-v", "--version"])
        isListApps = self._get(["-l", "--list-apps"])

        message = None
        if isHelp:
            message = self.usageString()
        elif isVersion:
            message = ("Orca %s" % orca_platform.version)
        elif isListApps:
            apps = filter(lambda x: x != None, pyatspi.Registry.getDesktop(0))
            names = [app.name for app in apps]
            message = "\n".join(names)

        if message:
            self._printMessageAndExit(message)

    def _getProfiles(self):
        """Gets the options associated with the profiles which should be
        loaded and stores them in self.profiles."""

        self.profiles, invalid = self._getValues(["-i", "--import-file"])

    def presentInvalidOptions(self):
        """Presents any invalid options to the user. Returns True if there
        were invalid options to present and a message printed; otherwise
        returns False."""

        if self.invalidOptions:
            # Translators: This message is displayed when the user tries
            # to start Orca and includes an invalid option as an argument.
            # After the message, the list of arguments, as typed by the
            # user, is displayed.
            #
            msg = _("The following arguments are not valid: ")
            print (msg + " ".join(self.invalidOptions))
            return True

        return False

    def _printMessageAndExit(self, msg):
        """Prints the specified message string and then exits."""

        # The use of os._exit() to immediately kill a child process
        # after a fork() is documented at docs.python.org.
        #
        # pylint: disable-msg=W0212
        #
        pid = os.fork()
        if pid:
            os.waitpid(pid, 0)
            os._exit(0)
        else:
            print msg
            os._exit(0)

    def convertToSettings(self):
        """Converts known items (currently just those which can be enabled
        or disabled), stores them in the self.settings dictionary and then
        returns that dictionary."""

        self._getEnableAndDisable()
        toEnable = map(self.canEnable.get, self.enable)
        for item in toEnable:
            self.settings[item] = True

        toDisable = map(self.canEnable.get, self.disable)
        for item in toDisable:
            self.settings[item] = False

        self.presentCannotEnable()

        return self.settings

    def presentCannotEnable(self):
        """Presents any non-enable-able items which the user asked us to
        enable/disable. Returns True if there were invalid items; otherwise
        returns False."""

        if self.cannotEnable:
            valid = "\nspeech, braille, braille-monitor, " \
                    "main-window, splash-window"
            # Translators: This message is displayed when the user
            # tries to enable or disable a feature via an argument,
            # but specified an invalid feature. Valid features are:
            # speech, braille, braille-monitor, main-window, and
            # splash-window. These items are not localized and are
            # presented in a list after this message.
            #
            msg = _("The following items can be enabled or disabled:")
            if not self._validFeaturesPrinted:
                print (msg + valid)
                self._validFeaturesPrinted = True
            return True

        return False

    def usage(self):
        """Prints out usage information."""
        print(self.usageString())

    def usageString(self):
        """Generates the usage information string."""
        info = []
        info.append(_("Usage: orca [OPTION...]"))

        # Translators: this is the description of the command line option
        # '-?, --help' that is used to display usage information.
        #
        info.append("-?, --help                   " + \
                  _("Show this help message"))
        info.append("-v, --version                %s" % orca_platform.version)

        # Translators: this is a testing option for the command line.  It prints
        # the names of applications known to the accessibility infrastructure
        # to stdout and then exits.
        #
        info.append("-l, --list-apps              " + \
                  _("Print the known running applications"))

        # Translators: this enables debug output for Orca.  The
        # YYYY-MM-DD-HH:MM:SS portion is a shorthand way of saying that
        # the file name will be formed from the current date and time with
        # 'debug' in front and '.out' at the end.  The 'debug' and '.out'
        # portions of this string should not be translated (i.e., it will
        # always start with 'debug' and end with '.out', regardless of the
        # locale.).
        #
        info.append("--debug                      " + \
                  _("Send debug output to debug-YYYY-MM-DD-HH:MM:SS.out"))

        # Translators: this enables debug output for Orca and overrides
        # the name of the debug file Orca will use for debug output if the
        # --debug option is used.
        #
        info.append("--debug-file=filename        " + \
                  _("Send debug output to the specified file"))

        # Translators: this is the description of the command line option
        # '-s, --setup, --gui-setup' that will initially display a GUI dialog
        # that would allow the user to set their Orca preferences.
        #
        info.append("-s, --setup, --gui-setup     " + \
                  _("Set up user preferences"))

        # Translators: this is the description of the command line option
        # '-t, --text-setup' that will initially display a list of questions
        # in text form, that the user will need to answer, before Orca will
        # startup. For this to happen properly, Orca will need to be run
        # from a terminal window.
        #
        info.append("-t, --text-setup             " + \
                  _("Set up user preferences (text version)"))

        # Translators: this is the description of the command line option
        # '-n, --no-setup' that means that Orca will startup without setting
        # up any user preferences.
        #
        info.append("-n, --no-setup               " +  \
                  _("Skip set up of user preferences"))

        # Translators: this is the description of the command line option
        # '-u, --user-prefs-dir=dirname' that allows you to specify an alternate
        # location for the user preferences.
        #
        info.append("-u, --user-prefs-dir=dirname " + \
                  _("Use alternate directory for user preferences"))

        info.append("-e, --enable=[" \
                        + "speech" + "|" \
                        + "braille" + "|" \
                        + "braille-monitor" + "|" \
                        + "main-window" + "|" \
                        + "splash-window" + "] ")

        # Translators: if the user supplies an option via the '-e, --enable'
        # command line option, it will be automatically enabled as Orca is
        # started.
        #
        info[-1] += _("Force use of option")

        info.append("-d, --disable=[" \
                        + "speech" + "|" \
                        + "braille" + "|" \
                        + "braille-monitor" + "|" \
                        + "main-window" + "|" \
                        + "splash-window" + "] ")

        # Translators: if the user supplies an option via the '-d, --disable'
        # command line option, it will be automatically disabled as Orca is
        # started.
        #
        info[-1] += _("Prevent use of option")

        # Translators: this is the Orca command line option to import to Orca
        # a user profile from a given file
        #
        info.append("-i, --import-file=filename   " + \
                  _("Import a profile from a given orca profile file"))

        # Translators: this is the Orca command line option that will quit Orca.
        # The user would run the Orca shell script again from a terminal window.
        # If this command line option is specified, the script will quit any
        # instances of Orca that are already running.
        #
        info.append("-q, --quit                   " + \
                  _("Quits Orca (if shell script used)"))

        # Translators: this is the Orca command line option that will force
        # the termination of Orca.
        # The user would run the Orca shell script again from a terminal window.
        # If this command line option is specified, the script will quit any
        # instances of Orca that are already running.
        #
        info.append("-f, --forcequit              " + \
                  _("Forces orca to be terminated immediately."))

        # Translators: this is the Orca command line option to tell Orca to
        # replace any existing Orca process(es) that might be running.
        #
        info.append("--replace                    " + \
                  _("Replace a currently running Orca"))

        # Translators: this is text being sent to a terminal and we want to
        # keep the text lines within terminal boundaries.
        #
        info.append("\n" + \
              _("If Orca has not been previously set up by the user, Orca\n" \
                "will automatically launch the preferences set up unless\n" \
                 "the -n or --no-setup option is used."))

        # Translators: this is more text being sent to a terminal and we want to
        # keep the text lines within terminal boundaries.
        #
        info.append("\n" + \
              ("WARNING: suspending Orca, e.g. by pressing Control-Z, from\n" \
               "an AT-SPI enabled shell (such as gnome-terminal), can also\n" \
               "suspend the desktop until Orca is killed."))

        info.append("\n" + _("Report bugs to orca-list@gnome.org."))

        return ("\n".join(info))

options = Options()
if options.userPrefsDir:
    settings.userPrefsDir = options.userPrefsDir

# This needs to occur prior to our importing anything which might in turn
# import anything which might expect to be able to use the Settings Manager
# You have been warned.
#
from settings_manager import SettingsManager
_settingsManager = SettingsManager()
if _settingsManager is None:
    print "Could not load the settings manager. Exiting."
    sys.exit(1)

from event_manager import EventManager
_eventManager = EventManager()

from script_manager import ScriptManager
_scriptManager = ScriptManager()

try:
    # If we don't have an active desktop, we will get a RuntimeError.
    import mouse_review
except RuntimeError:
    pass

if settings.useDBus:
    import dbus.mainloop.glib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    import dbusserver

import braille
import httpserver
import keybindings
import orca_state
import speech
import notification_messages

from input_event import BrailleEvent
from input_event import KeyboardEvent

import gc
if settings.debugMemoryUsage:
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE
                 | gc.DEBUG_COLLECTABLE
                 | gc.DEBUG_INSTANCES
                 | gc.DEBUG_OBJECTS
                 | gc.DEBUG_SAVEALL)


EXIT_CODE_HANG = 50

# The user-settings module (see loadUserSettings).
#
_userSettings = None

# Command line options that override any other settings.
#
_commandLineSettings = {}

# A subset of the original Xmodmap info prior to our stomping on it.
# Right now, this is just for the user's chosen Orca modifier(s).
#
_originalXmodmap = ""
_orcaModifiers = settings.DESKTOP_MODIFIER_KEYS + settings.LAPTOP_MODIFIER_KEYS
_capsLockCleared = False
_restoreOrcaKeys = False

########################################################################
#                                                                      #
# METHODS TO HANDLE APPLICATION LIST AND FOCUSED OBJECTS               #
#                                                                      #
########################################################################

def setLocusOfFocus(event, obj, notifyScript=True, force=False):
    """Sets the locus of focus (i.e., the object with visual focus) and
    notifies the script of the change should the script wish to present
    the change to the user.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible with the new locus of focus.
    - notifyScript: if True, propagate this event
    - force: if True, don't worry if this is the same object as the
      current locusOfFocus
    """

    if not force and obj == orca_state.locusOfFocus:
        return

    # If this event is not for the currently active script, then just return.
    #
    if event and event.source and \
       event.host_application and orca_state.activeScript:
        currentApp = orca_state.activeScript.app
        try:
            appList = [event.host_application, event.source.getApplication()]
        except (LookupError, RuntimeError):
            appList = []
            debug.println(debug.LEVEL_SEVERE,
                           "orca.setLocusOfFocus() application Error")
        if not currentApp in appList:
            return

    oldLocusOfFocus = orca_state.locusOfFocus
    try:
        # Just to see if we have a valid object.
        oldLocusOfFocus.getRole()
    except:
        # Either it's None or it's an invalid remote object.
        oldLocusOfFocus = None

    orca_state.focusHistory = \
        orca_state.focusHistory[:settings.focusHistoryLength - 1]
    orca_state.focusHistory.insert(0, oldLocusOfFocus)

    orca_state.locusOfFocus = obj
    try:
        app = orca_state.locusOfFocus.getApplication()
    except:
        orca_state.locusOfFocus = None
        if event:
            debug.println(debug.LEVEL_FINE,
                          "LOCUS OF FOCUS: None event='%s'" % event.type)
        else:
            debug.println(debug.LEVEL_FINE,
                          "LOCUS OF FOCUS: None event=None")
    else:
        if not app:
            appname = "None"
        else:
            appname = "'" + app.name + "'"
        debug.println(debug.LEVEL_FINE,
                      "LOCUS OF FOCUS: app=%s name='%s' role='%s'" \
                      % (appname,
                         orca_state.locusOfFocus.name,
                         orca_state.locusOfFocus.getRoleName()))

        if event:
            debug.println(debug.LEVEL_FINE,
                          "                event='%s'" % event.type)
        else:
            debug.println(debug.LEVEL_FINE,
                          "                event=None")

    if notifyScript and orca_state.activeScript:
        orca_state.activeScript.locusOfFocusChanged(
            event, oldLocusOfFocus, orca_state.locusOfFocus)

########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################

def cycleDebugLevel(script=None, inputEvent=None):
    levels = [debug.LEVEL_ALL, "all",
              debug.LEVEL_FINEST, "finest",
              debug.LEVEL_FINER, "finer",
              debug.LEVEL_FINE, "fine",
              debug.LEVEL_CONFIGURATION, "configuration",
              debug.LEVEL_INFO, "info",
              debug.LEVEL_WARNING, "warning",
              debug.LEVEL_SEVERE, "severe",
              debug.LEVEL_OFF, "off"]

    try:
        levelIndex = levels.index(debug.debugLevel) + 2
    except:
        levelIndex = 0
    else:
        if levelIndex >= len(levels):
            levelIndex = 0

    debug.debugLevel = levels[levelIndex]

    briefMessage = levels[levelIndex + 1]
    fullMessage =  "Debug level %s." % briefMessage
    orca_state.activeScript.presentMessage(fullMessage, briefMessage)

    return True

def exitListShortcutsMode(self, inputEvent=None):
    """Turns list shortcuts mode off.

    Returns True to indicate the input event has been consumed.
    """

    orca_state.listOfShortcuts = []
    orca_state.typeOfShortcuts = ""
    orca_state.ptrToShortcut = -1
    settings.listShortcutsModeEnabled = False

    # Translators: Orca has a "List Shortcuts Mode" that allows the user to
    # list a group of keyboard shortcuts. Pressing 1 makes it possible for
    # the user to navigate amongst a list of global ("default") commands.
    # Pressing 2 allows the user to navigate amongst Orca commands specific
    # to the application with focus. Escape exists this mode. This string
    # is the prompt which will be presented to the user in both speech and
    # braille upon exiting this mode.
    #
    message = _("Exiting list shortcuts mode.")
    orca_state.activeScript.presentMessage(message)
    return True

########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING KEYBOARD EVENTS.            #
#                                                                      #
########################################################################

_orcaModifierPressed = False

def _processKeyCaptured(event):
    """Called when a new key event arrives and orca_state.capturingKeys=True.
    (used for key bindings redefinition)
    """

    if event.type == 0:
        if event.isModifierKey() or event.isLockingKey():
            return True
        else:
            # We want the keyname rather than the printable character.
            # If it's not on the keypad, get the name of the unshifted
            # character. (i.e. "1" instead of "!")
            #
            keymap = Gdk.Keymap.get_default()
            entries_for_keycode = keymap.get_entries_for_keycode(event.hw_code)
            entries = entries_for_keycode[-1]
            event.event_string = Gdk.keyval_name(entries[0])

            if not event.event_string:
                orca_state.capturingKeys = False
                return False

            if event.event_string.startswith("KP") and \
               event.event_string != "KP_Enter":
                name = Gdk.keyval_name(entries[1].keycode)
                if name.startswith("KP"):
                    event.event_string = name

            orca_state.lastCapturedKey = event
    else:
        pass

    return False

def _processKeyboardEvent(event):
    """The primary key event handler for Orca.  Keeps track of various
    attributes, such as the lastInputEvent.  Also does key echo as well
    as any local keybindings before passing the event on to the active
    script.  This method is called synchronously from the AT-SPI registry
    and should be performant.  In addition, it must return True if it has
    consumed the event (and False if not).

    Arguments:
    - event: an AT-SPI DeviceEvent

    Returns True if the event should be consumed.
    """
    global _orcaModifierPressed

    # Weed out duplicate and otherwise bogus events.
    keyboardEvent = KeyboardEvent(event)
    debug.println(debug.LEVEL_FINE, keyboardEvent.toString())
    if keyboardEvent.ignoreDueToTimestamp():
        debug.println(debug.LEVEL_FINE, "IGNORING EVENT DUE TO TIMESTAMP")
        return

    # Figure out what we've got.
    isOrcaModifier = keyboardEvent.isOrcaModifier()
    isPressedEvent = keyboardEvent.isPressedKey()
    if isOrcaModifier:
        _orcaModifierPressed = isPressedEvent
    if _orcaModifierPressed:
        keyboardEvent.modifiers |= settings.ORCA_MODIFIER_MASK

    # Update our state.
    orca_state.lastInputEventTimestamp = event.timestamp
    orca_state.lastInputEvent = keyboardEvent
    if not keyboardEvent.isModifierKey():
        keyboardEvent.setClickCount()
        orca_state.lastNonModifierKeyEvent = keyboardEvent

    # Echo it based on what it is and the user's settings.
    script = orca_state.activeScript
    if script and isPressedEvent:
        script.presentationInterrupt()
        keyboardEvent.present()
 
    # Special modes.
    if not isPressedEvent and keyboardEvent.event_string == "Escape":
        script.exitLearnMode(keyboardEvent)
    if orca_state.capturingKeys:
        return _processKeyCaptured(keyboardEvent)
    if settings.listShortcutsModeEnabled:
        return listShortcuts(keyboardEvent)
    if notification_messages.listNotificationMessagesModeEnabled:
        return notification_messages.listNotificationMessages(keyboardEvent)
    if settings.learnModeEnabled:
        if keyboardEvent.isPrintableKey() and not _orcaModifierPressed:
            return True

    # See if the event manager wants it (i.e. it is bound to a command.
    if _eventManager.processKeyboardEvent(keyboardEvent):
        return True

    # Do any needed xmodmap crap.
    global _restoreOrcaKeys
    if not isPressedEvent:
        if keyboardEvent.event_string in settings.orcaModifierKeys \
           and orca_state.bypassNextCommand:
            _restoreXmodmap()
            _restoreOrcaKeys = True
        elif _restoreOrcaKeys and not orca_state.bypassNextCommand:
            _createOrcaXmodmap()
            _restoreOrcaKeys = False
    elif not keyboardEvent.isModifierKey():
        orca_state.bypassNextCommand = False
 
    return isOrcaModifier

########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING BRAILLE EVENTS.             #
#                                                                      #
########################################################################

def _processBrailleEvent(event):
    """Called whenever a  key is pressed on the Braille display.

    Arguments:
    - command: the BrlAPI event for the key that was pressed.

    Returns True if the event was consumed; otherwise False
    """

    consumed = False

    # Braille key presses always interrupt speech.
    #
    event = BrailleEvent(event)
    if event.event['command'] not in braille.dontInteruptSpeechKeys:
        speech.stop()
    orca_state.lastInputEvent = event

    try:
        consumed = _eventManager.processBrailleEvent(event)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    if (not consumed) and settings.learnModeEnabled:
        consumed = True

    return consumed

########################################################################
#                                                                      #
# METHODS FOR HANDLING INITIALIZATION, SHUTDOWN, AND USE.              #
#                                                                      #
########################################################################

def toggleSilenceSpeech(script=None, inputEvent=None):
    """Toggle the silencing of speech.

    Returns True to indicate the input event has been consumed.
    """
    speech.stop()
    if settings.silenceSpeech:
        settings.silenceSpeech = False
        # Translators: this is a spoken prompt letting the user know
        # that speech synthesis has been turned back on.
        #
        orca_state.activeScript.presentMessage(_("Speech enabled."))
    else:
        # Translators: this is a spoken prompt letting the user know
        # that speech synthesis has been temporarily turned off.
        #
        orca_state.activeScript.presentMessage(_("Speech disabled."))
        settings.silenceSpeech = True
    return True

def _setXmodmap(xkbmap):
    """Set the keyboard map using xkbcomp."""
    p = subprocess.Popen(['xkbcomp', '-w0', '-', os.environ['DISPLAY']],
        stdin=subprocess.PIPE, stdout=None, stderr=None)
    p.communicate(xkbmap)

def _setCapsLockAsOrcaModifier(enable):
    """Enable or disable use of the caps lock key as an Orca modifier key."""
    interpretCapsLineProg = re.compile(
        r'^\s*interpret\s+Caps[_+]Lock[_+]AnyOfOrNone\s*\(all\)\s*{\s*$', re.I)
    capsModLineProg = re.compile(
        r'^\s*action\s*=\s*SetMods\s*\(\s*modifiers\s*=\s*Lock\s*,\s*clearLocks\s*\)\s*;\s*$', re.I)
    normalCapsLineProg = re.compile(
        r'^\s*action\s*=\s*LockMods\s*\(\s*modifiers\s*=\s*Lock\s*\)\s*;\s*$', re.I)
    normalCapsLine = '        action= LockMods(modifiers=Lock);'
    capsModLine =    '        action= SetMods(modifiers=Lock,clearLocks);'
    lines = _originalXmodmap.split('\n')
    foundCapsInterpretSection = False
    for i in range(len(lines)):
        line = lines[i]
        if not foundCapsInterpretSection:
            if interpretCapsLineProg.match(line):
                foundCapsInterpretSection = True
        else:
            if enable:
                if normalCapsLineProg.match(line):
                    lines[i] = capsModLine
                    _setXmodmap('\n'.join(lines))
                    return
            else:
                if capsModLineProg.match(line):
                    lines[i] = normalCapsLine
                    _setXmodmap('\n'.join(lines))
                    return
            if line.find('}'):
                # Failed to find the line we need to change
                return

def _createOrcaXmodmap():
    """Makes an Orca-specific Xmodmap so that the keys behave as we
    need them to do. This is especially the case for the Orca modifier.
    """

    global _capsLockCleared

    cmd = []
    if "Caps_Lock" in settings.orcaModifierKeys:
        _setCapsLockAsOrcaModifier(True)
        _capsLockCleared = True
    elif _capsLockCleared:
        _setCapsLockAsOrcaModifier(False)
        _capsLockCleared = False

def _storeXmodmap(keyList):
    """Save the original xmodmap for the keys in keyList before we alter it.

    Arguments:
    - keyList: A list of named keys to look for.
    """

    global _originalXmodmap
    _originalXmodmap = subprocess.check_output(['xkbcomp', os.environ['DISPLAY'], '-'])

def _restoreXmodmap(keyList=[]):
    """Restore the original xmodmap values for the keys in keyList.

    Arguments:
    - keyList: A list of named keys to look for. An empty list means
      to restore the entire saved xmodmap.
    """

    global _capsLockCleared
    _capsLockCleared = False
    p = subprocess.Popen(['xkbcomp', '-w0', '-', os.environ['DISPLAY']],
        stdin=subprocess.PIPE, stdout=None, stderr=None)
    p.communicate(_originalXmodmap)

def loadUserSettings(script=None, inputEvent=None, skipReloadMessage=False):
    """Loads (and reloads) the user settings module, reinitializing
    things such as speech if necessary.

    Returns True to indicate the input event has been consumed.
    """

    global _userSettings

    # Shutdown the output drivers and give them a chance to die.

    # Only exit the D-Bus server if we're in an environment where there 
    # is a D-Bus session bus already running.  This helps prevent nastiness
    # on the login screen.
    #
    if settings.useDBus:
        dbusserver.shutdown()

    httpserver.shutdown()
    speech.shutdown()
    braille.shutdown()

    _scriptManager.deactivate()

    reloaded = False
    if _userSettings:
        _profile = _settingsManager.getSetting('activeProfile')[1]
        try:
            _userSettings = _settingsManager.getGeneralSettings(_profile)
            reloaded = True
        except ImportError:
            debug.printException(debug.LEVEL_FINEST)
        except:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        _profile = _settingsManager.profile
        try:
            _userSettings = _settingsManager.getGeneralSettings(_profile)
            if options.debug:
                debug.debugLevel = debug.LEVEL_ALL
                debug.eventDebugLevel = debug.LEVEL_OFF
                debug.debugFile = open(options.debugFile, 'w', 0)
        except ImportError:
            debug.printException(debug.LEVEL_FINEST)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    # If any settings were added to the command line, they take
    # precedence over everything else.
    #
    for key in _commandLineSettings:
        setattr(settings, key, _commandLineSettings[key])

    if settings.enableSpeech:
        try:
            speech.init()
            if reloaded and not skipReloadMessage:
                # Translators: there is a keystroke to reload the user
                # preferences.  This is a spoken prompt to let the user
                # know when the preferences has been reloaded.
                #
                msg = _("Orca user settings reloaded.")
                speech.speak(msg, settings.voices.get(settings.SYSTEM_VOICE))
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Speech module has been initialized.")
        except:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to speech.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")

    if settings.enableBraille:
        try:
            braille.init(_processBrailleEvent, settings.tty)
        except:
            debug.printException(debug.LEVEL_WARNING)
            debug.println(debug.LEVEL_WARNING,
                          "Could not initialize connection to braille.")

    # I'm not sure where else this should go. But it doesn't really look
    # right here.
    try:
        mouse_review.mouse_reviewer.toggle(on=settings.enableMouseReview)
    except NameError:
        pass

    global _orcaModifiers
    custom = [k for k in settings.orcaModifierKeys if k not in _orcaModifiers]
    _orcaModifiers += custom
    # Handle the case where a change was made in the Orca Preferences dialog.
    #
    if _originalXmodmap:
        _restoreXmodmap(_orcaModifiers)

    _storeXmodmap(_orcaModifiers)
    _createOrcaXmodmap()

    showMainWindowGUI()

    _scriptManager.activate()
    _eventManager.activate()

    # Only start the D-Bus server if we're in an environment where there 
    # is a D-Bus session bus already running.  This helps prevent nastiness
    # on the login screen.
    #
    if settings.useDBus:
        dbusserver.init()
    httpserver.init()

    return True

def showAppPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interace to configure the settings for a
    specific applications within Orca and set up those app-specific
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.appGuiPreferencesModule,
                            globals(),
                            locals(),
                            [''])
        module.showPreferencesUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)

    return True

def showPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interace to configure Orca and set up
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.guiPreferencesModule,
                            globals(),
                            locals(),
                            [''])
        module.showPreferencesUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)

    return True

def showMainWindowGUI(script=None, inputEvent=None):
    """Displays the Orca main window.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.mainWindowModule,
                            globals(),
                            locals(),
                            [''])
        if settings.showMainWindow:
            module.showMainUI()
        else:
            module.hideMainUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)

    return True

def _showPreferencesConsole(script=None, inputEvent=None):
    """Displays the user interace to configure Orca and set up
    user preferences via a command line interface.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.consolePreferencesModule,
                            globals(),
                            locals(),
                            [''])
        module.showPreferencesUI(_commandLineSettings)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    return True

def helpForOrca(script=None, inputEvent=None, page=""):
    """Show Orca Help window (part of the GNOME Access Guide).

    Returns True to indicate the input event has been consumed.
    """
    uri = "ghelp:orca"
    if page:
        uri += "?%s" % page
    Gtk.show_uri(Gdk.Screen.get_default(),
                 uri,
                 Gtk.get_current_event_time())
    return True

def listShortcuts(event):
    """When list shortcuts mode is enabled, this function provides a means
    by which users can navigate through Orca bound Orca commands. Pressing
    1 results in a list of the default shortcuts; pressing 2 results in a
    list of shortcuts for the focused application, should one exist. List
    navigation is accomplished through the Up and Down Arrow keys. Escape
    exits the list. In this mode, other keys are disabled.

    Arguments:
    - event: an AT-SPI DeviceEvent

    Returns True if the event is consumed (and False if not).
    """

    numShortcuts = len(orca_state.listOfShortcuts)
    consumed = False
    clickCount = 0
    message = ""

    # Translators: The following string instructs the user how to navigate
    # amongst the list of commands presented in 'list shortcuts' mode as
    # well as how to exit the list when finished.
    #
    navigation = \
        _("Use Up and Down Arrow to navigate the list. Press Escape to exit.")

    if event.type == pyatspi.KEY_PRESSED_EVENT:
        clickCount = event.getClickCount()
        if (event.event_string == "1"):
            if not numShortcuts or orca_state.typeOfShortcuts != "default":
                orca_state.listOfShortcuts = getListOfShortcuts("default")
                orca_state.typeOfShortcuts = "default"
                numShortcuts = len(orca_state.listOfShortcuts)
            orca_state.ptrToShortcut = 0
            # Translators: This message is presented when the user is in
            # 'list of shortcuts mode'. In this messsage, we present the
            # number of shortcuts found.
            #
            message = ngettext("%d Orca default shortcut found.",
                               "%d Orca default shortcuts found.",
                               numShortcuts) % numShortcuts
            message = message + " " + navigation
            orca_state.activeScript.presentMessage(message)
            message = orca_state.listOfShortcuts[orca_state.ptrToShortcut][0]+ \
              " " + orca_state.listOfShortcuts[orca_state.ptrToShortcut][1]
            orca_state.activeScript.speakMessage(message)
            orca_state.activeScript.displayBrailleMessage(message, -1, -1)
            consumed = True
        elif (event.event_string == "2"):
            if not numShortcuts or orca_state.typeOfShortcuts != "application":
                orca_state.listOfShortcuts = getListOfShortcuts("application")
                orca_state.typeOfShortcuts = "application"
                numShortcuts = len(orca_state.listOfShortcuts)
            if numShortcuts > 0: 
                orca_state.ptrToShortcut = 0
                # Translators: This message is presented when the user is in
                # 'list of shortcuts mode'. In this message, we present the
                # number of shortcuts found for the named application.
                #
                message = ngettext( \
                    "%(count)d Orca shortcut for %(application)s found.",
                    "%(count)d Orca shortcuts for %(application)s found.",
                    numShortcuts) % \
                    {"count" : numShortcuts,
                     "application" : orca_state.activeScript.app.name}
                message = message + " " + navigation
                orca_state.activeScript.presentMessage(message)
                message = \
                  orca_state.listOfShortcuts[orca_state.ptrToShortcut][0] + \
                  " " + orca_state.listOfShortcuts[orca_state.ptrToShortcut][1]
                orca_state.activeScript.speakMessage(message)
                orca_state.activeScript.displayBrailleMessage(message, -1, -1)
            else:
                # Translators: This message is presented when the user is in
                # 'list of shortcuts mode'. This is the message we present
                # when the user requested a list of application-specific
                # shortcuts, but none could be found for that application.
                #
                message = _("No Orca shortcuts for %s found.") % \
                    (orca_state.activeScript.app.name)
                orca_state.activeScript.speakMessage(message)
                orca_state.activeScript.displayBrailleMessage(message, -1, -1)
            consumed = True
        elif (event.event_string == "Up"):
            if (numShortcuts > 0):
                if orca_state.ptrToShortcut > 0: 
                    orca_state.ptrToShortcut = orca_state.ptrToShortcut-1
                else:
                    orca_state.ptrToShortcut = numShortcuts-1 
                    # Translators: when the user is attempting to locate a
                    # particular object and the top of a page or list is
                    # reached without that object being found, we "wrap" to
                    # the bottom and continue looking upwards. We need to
                    # inform the user when this is taking place.
                    #
                    orca_state.activeScript.\
                        presentMessage(_("Wrapping to bottom."))

                message = \
                  orca_state.listOfShortcuts[orca_state.ptrToShortcut][0] + \
                  " " + orca_state.listOfShortcuts[orca_state.ptrToShortcut][1]
                orca_state.activeScript.speakMessage(message)
                orca_state.activeScript.displayBrailleMessage(message, -1, -1)
            consumed = True
        elif (event.event_string == "Down"):
            if (numShortcuts > 0): 
                if orca_state.ptrToShortcut < numShortcuts-1: 
                    orca_state.ptrToShortcut = orca_state.ptrToShortcut+1
                else:
                    orca_state.ptrToShortcut = 0 
                    # Translators: when the user is attempting to locate a
                    # particular object and the bottom of a page or list is
                    # reached without that object being found, we "wrap" to the
                    # top and continue looking downwards. We need to inform the
                    # user when this is taking place.
                    #
                    orca_state.activeScript.\
                        presentMessage(_("Wrapping to top."))
                message = \
                  orca_state.listOfShortcuts[orca_state.ptrToShortcut][0] + \
                  " " + orca_state.listOfShortcuts[orca_state.ptrToShortcut][1]
                orca_state.activeScript.speakMessage(message)
                orca_state.activeScript.displayBrailleMessage(message, -1, -1)
            consumed = True
        elif (event.event_string == "Escape"):
            exitListShortcutsMode(event)
            consumed = True 
        else:
            # Translators: Orca has a 'List Shortcuts' mode by which a user can
            # navigate through a list of the bound commands in Orca. Pressing 1
            # presents the commands/shortcuts available for all applications.
            # These are the "default" commands/shortcuts. Pressing 2 presents
            # commands/shortcuts Orca provides for the application with focus.
            # The following message is presented to the user upon entering this
            # mode.
            #
            message = _("Press 1 for Orca's default shortcuts. Press 2 for " \
                        "Orca's shortcuts for the current application. " \
                        "Press escape to exit.")
            orca_state.activeScript.speakMessage(message)
            orca_state.activeScript.displayBrailleMessage(message, -1, -1)
            consumed = True
    elif (event.type == pyatspi.KEY_RELEASED_EVENT) and (event.event_string \
      == "Escape"):
        consumed = True
    return consumed


def getListOfShortcuts(typeOfShortcuts):
    """This function returns a list of Orca default shortcuts if the argument
    is 'default'. It returns a list of Orca shortcuts which are specific to
    the focused application, if the argument is "application". Orca default
    shortcuts are those found in the default script. Application-specific
    shortcuts are those which are present in the active script, but not in
    the default script. Only one shortcut per handler is listed. The list is
    sorted on shortcuts.

    Arguments:
    - typeOfShortcuts: a string specifying the desired type of shortcuts.

    Returns a list of shortcuts; depending on the value of argument.
    """

    numShortcuts = len(orca_state.listOfShortcuts)
    shortcuts = []
    shortcut = ""
    clickCount = ""
    brlKeyName = ""     
    brlHandler = None
    defScript = _scriptManager.getDefaultScript()
    defKeyBindings = defScript.getKeyBindings()
    defBrlBindings = defScript.getBrailleBindings()
    kbindings = keybindings.KeyBindings()
    if typeOfShortcuts == "default":
        for kb in defKeyBindings.keyBindings:
            if kb.keysymstring:
                if not kbindings.hasKeyBinding(kb,"description"):
                    kbindings.add(kb)
    elif typeOfShortcuts == "application":
        for kb in orca_state.activeScript.keyBindings.keyBindings:
            if kb.keysymstring:
                if not (defKeyBindings.hasKeyBinding(kb,"description") or \
                kbindings.hasKeyBinding(kb,"description")):
                    kbindings.add(kb)

    for kb in kbindings.keyBindings:
        keysymString = kb.keysymstring.replace("KP_", _("keypad "))
        clickCount = ""
        if kb.click_count == 2:
            # Translators: Orca keybindings support double
            # and triple "clicks" or key presses, similar to
            # using a mouse.
            #
            clickCount = _("double click")
        elif kb.click_count == 3:
            # Translators: Orca keybindings support double
            # and triple "clicks" or key presses, similar to
            # using a mouse.
            #
            clickCount = _("triple click")
        shortcut = (kb.handler.description, keybindings.getModifierNames\
        (kb.modifiers) + keysymString.title() + " " + clickCount)
        shortcuts.append(shortcut)
        shortcuts = sorted(shortcuts, key=lambda shortcut: shortcut[1])

    if typeOfShortcuts == "orcaDefault":
        for bb in defBrlBindings.keys():
            brlKeyName = braille.command_name[bb]
            brlHandler = defBrlBindings[bb]
            shortcut = (brlHandler.description, brlKeyName)
            shortcuts.append(shortcut) 
    return shortcuts

def quitOrca(script=None, inputEvent=None):
    """Quit Orca. Check if the user wants to confirm this action.
    If so, show the confirmation GUI otherwise just shutdown.

    Returns True to indicate the input event has been consumed.
    """

    if settings.quitOrcaNoConfirmation:
        shutdown()
    else:
        try:
            module = __import__(settings.quitModule,
                                globals(),
                                locals(),
                                [''])
            module.showQuitUI()
        except:
            debug.printException(debug.LEVEL_SEVERE)

    return True

def showFindGUI(script=None, inputEvent=None):
    """Displays the user interace to perform an Orca Find.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.findModule,
                            globals(),
                            locals(),
                            [''])
        module.showFindUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)

def showSplashGUI(script=None, inputEvent=None):
    """Displays a splash screen.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = __import__(settings.splashModule,
                            globals(),
                            locals(),
                            [''])
        if _commandLineSettings.get("showSplashWindow", True):
            module.showSplashUI()
        else:
            module.hideSplashUI()

    except:
        debug.printException(debug.LEVEL_SEVERE)

    return True


# If True, this module has been initialized.
#
_initialized = False

def init(registry):
    """Initialize the orca module, which initializes the speech and braille
    modules.  Also builds up the application list, registers for AT-SPI events,
    and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """

    global _initialized

    if _initialized \
       and a11yAppSettings.get_boolean('screen-reader-enabled'):
        return False

    # Do not hang on initialization if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    loadUserSettings()
    _eventManager.registerKeystrokeListener(_processKeyboardEvent)

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    _initialized = True
    a11yAppSettings.connect('changed', onEnabledChanged)
    return True

def start(registry):
    """Starts Orca.
    """

    if not _initialized:
        init(registry)

    # Do not hang on startup if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    if settings.cacheValues:
        pyatspi.setCacheLevel(pyatspi.CACHE_PROPERTIES)

    registry.start(gil=settings.useGILIdleHandler)

def die(exitCode=1):
    pid = os.getpid()
    if exitCode == EXIT_CODE_HANG:
        # Someting is hung and we wish to abort.
        os.kill(pid, signal.SIGKILL)
        return

    shutdown()
    sys.exit(exitCode)
    if exitCode > 1:
        os.kill(pid, signal.SIGTERM)

def timeout(signum=None, frame=None):
    debug.println(debug.LEVEL_SEVERE,
                  "TIMEOUT: something has hung.  Aborting.")
    debug.printStack(debug.LEVEL_ALL)
    die(EXIT_CODE_HANG)

def shutdown(script=None, inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """

    global _initialized

    if not _initialized:
        return False

    # Try to say goodbye, but be defensive if something has hung.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    # Translators: this is what Orca speaks and brailles when it quits.
    #
    orca_state.activeScript.presentMessage(_("Goodbye."))

    _eventManager.deactivate()
    _scriptManager.deactivate()

    # Shutdown all the other support.
    #
    if settings.enableSpeech:
        speech.shutdown()
    if settings.enableBraille:
        braille.shutdown()

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    _initialized = False
    _restoreXmodmap(_orcaModifiers)

    pyatspi.Registry.stop()

    return True

exitCount = 0
def shutdownOnSignal(signum, frame):
    global exitCount

    debug.println(debug.LEVEL_ALL,
                  "Shutting down and exiting due to signal = %d" \
                  % signum)

    debug.println(debug.LEVEL_ALL, "Current stack is:")
    debug.printStack(debug.LEVEL_ALL)

    # Well...we'll try to exit nicely, but if we keep getting called,
    # something bad is happening, so just quit.
    #
    if exitCount:
        die(signum)
    else:
        exitCount += 1

    # Try to do a graceful shutdown if we can.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    try:
        if _initialized:
            shutdown()
        else:
            # We always want to try to shutdown speech since the
            # speech servers are very persistent about living.
            #
            speech.shutdown()
            shutdown()
        cleanExit = True
    except:
        cleanExit = False

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    if not cleanExit:
        die(EXIT_CODE_HANG)

def abortOnSignal(signum, frame):
    debug.println(debug.LEVEL_ALL,
                  "Aborting due to signal = %d" \
                  % signum)
    die(signum)

def multipleOrcas():
    """Returns True if multiple instances of Orca are running
    which are owned by the same user."""

    openFile = os.popen('pgrep -u %s orca' % os.getuid())
    pids = openFile.read()
    openFile.close()
    orcas = [int(p) for p in pids.split()]

    pid = os.getpid()
    ppid = os.getppid()
    return len(filter(lambda p: p not in [pid, ppid], orcas)) > 0

def cleanupGarbage():
    """Cleans up garbage on the heap."""
    gc.collect()
    for obj in gc.garbage:
        try:
            if isinstance(obj, pyatspi.Accessibility.Accessible):
                gc.garbage.remove(obj)
                obj.__del__()
        except:
            pass

def main():
    """The main entry point for Orca.  The exit codes for Orca will
    loosely be based on signals, where the exit code will be the
    signal used to terminate Orca (if a signal was used).  Otherwise,
    an exit code of 0 means normal completion and an exit code of 50
    means Orca exited because of a hang."""

    # Method to call when we think something might be hung.
    #
    settings.timeoutCallback = timeout

    # Various signal handlers we want to listen for.
    #
    signal.signal(signal.SIGHUP, shutdownOnSignal)
    signal.signal(signal.SIGINT, shutdownOnSignal)
    signal.signal(signal.SIGTERM, shutdownOnSignal)
    signal.signal(signal.SIGQUIT, shutdownOnSignal)
    signal.signal(signal.SIGSEGV, abortOnSignal)

    if options.presentInvalidOptions() and multipleOrcas():
        die(0)

    _commandLineSettings.update(options.convertToSettings())
    for profile in options.profiles:
        # Translators: This message is what is presented to the user
        # when he/she attempts to import a settings profile, but the
        # import failed for some reason.
        #
        msg = _("Unable to import profile.")
        try:
            if _settingsManager.importProfile(profile):
                # Translators: This message is what is presented to the user
                # when he/she successfully imports a settings profile.
                #
                msg = _("Profile import success.")
        except KeyError as ex:
            # Translators: This message is what is presented to the user
            # when he/she attempts to import a settings profile but the
            # import failed due to a bad key.
            #
            msg = _("Import failed due to an unrecognized key: %s") % ex
        except IOError as ex:
            msg = "%s: %s" % (ex.strerror, ex.filename)
        except:
            continue

        print msg
        if multipleOrcas():
            die(0)

    # Check if old config location exists, try to copy all 
    # the data from old location to the new location.
    #
    if not options.userPrefsDir:
        from xdg.BaseDirectory import xdg_data_home
        options.userPrefsDir = os.path.join(xdg_data_home, "orca")
    oldUserPrefsDir = os.path.join(os.environ["HOME"], ".orca")

    if not os.path.exists(options.userPrefsDir):
        os.makedirs(options.userPrefsDir)

    for baseDirName, dirNames, fileNames in os.walk(oldUserPrefsDir):

        for dirName in dirNames:
            relPath = os.path.relpath(baseDirName, oldUserPrefsDir)
            dstDir = os.path.join(os.path.join(
                    options.userPrefsDir, relPath), dirName)
            if not os.path.exists(dstDir):
                os.mkdir(dstDir)

        for fileName in fileNames:
            srcFile = os.path.join(baseDirName, fileName)
            relPath = os.path.relpath(baseDirName, oldUserPrefsDir)
            dstFile = os.path.join(os.path.join(
                    options.userPrefsDir, relPath),
                                   fileName)
            if not os.path.exists(dstFile):
                shutil.copy(srcFile, dstFile)

    settings.userPrefsDir = options.userPrefsDir

    # Do not run Orca if accessibility has not been enabled.
    # We do allow, however, one to force Orca to run via the
    # "-n" switch.  The main reason is so that things such
    # as accessible login can work -- in those cases, the a11y
    # setting is typically not set since the gdm user does not
    # have a home.
    #
    a11yEnabled = _settingsManager.isAccessibilityEnabled()
    if not options.bypassSetup and not a11yEnabled:
        _showPreferencesConsole()
        die()

    if options.setupRequested and not (options.bypassSetup or options.showGUI):
        _showPreferencesConsole()

    if not options.desktopRunning:
        print "Cannot start Orca because it cannot connect"
        print "to the Desktop.  Please make sure the DISPLAY"
        print "environment variable has been set."
        return 1

    userprefs = settings.userPrefsDir
    sys.path.insert(0, userprefs)
    sys.path.insert(0, '') # current directory

    init(pyatspi.Registry)

    try:
        message = _("Welcome to Orca.")
        if not _settingsManager.getSetting('onlySpeakDisplayedText'):
            speech.speak(message, settings.voices.get(settings.SYSTEM_VOICE))
        braille.displayMessage(message)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    showSplashGUI()
    script = orca_state.activeScript
    if script:
        window = script.utilities.activeWindow()
        if window and not orca_state.locusOfFocus:
            setLocusOfFocus(None, window)

    # Check to see if the user wants the configuration GUI. It's
    # done here so that the user's existing preferences can be used
    # to set the initial GUI state.  We'll also force the set to
    # be run if the preferences file doesn't exist, unless the
    # user has bypassed any setup via the --no-setup switch.
    #
    if options.setupRequested and not options.bypassSetup and options.showGUI:
        showPreferencesGUI()
    elif not options.bypassSetup \
         and (not _userSettings or _settingsManager.isFirstStart()):
        if options.desktopRunning:
            if not os.path.exists(userprefs):
                # Hack to work around b.g.o. 601657.
                #
                try:
                    os.mkdir(userprefs)
                except:
                    debug.printException(debug.LEVEL_FINEST)
            showPreferencesGUI()
        else:
            _showPreferencesConsole()
        _settingsManager.setFirstStart()
    elif options.bypassSetup:
        loadUserSettings(skipReloadMessage=True)
        _settingsManager.setFirstStart()

    try:
        start(pyatspi.Registry) # waits until we stop the registry
    except:
        die(EXIT_CODE_HANG)
    return 0

if __name__ == "__main__":
    sys.exit(main())
