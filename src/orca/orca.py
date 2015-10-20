# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2010-2011 The Orca Team
# Copyright 2012 Igalia, S.L.
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
                "Copyright (c) 2010-2011 The Orca Team" \
                "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

import gi
import importlib
import os
import pyatspi
import re
import signal
import subprocess
import sys

try:
    from gi.repository.Gio import Settings
    a11yAppSettings = Settings(schema_id='org.gnome.desktop.a11y.applications')
except:
    a11yAppSettings = None

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk

    # Note: This last import is here due to bgo #673396.
    # See bgo#673397 for the rest of the story.
    gi.require_version("GdkX11", "3.0")
    from gi.repository.GdkX11 import X11Screen
except:
    pass

from . import braille
from . import debug
from . import event_manager
from . import keybindings
from . import logger
from . import messages
from . import notification_messages
from . import orca_state
from . import orca_platform
from . import script_manager
from . import settings
from . import settings_manager
from . import speech
from .input_event import BrailleEvent
from .input_event import KeyboardEvent

_eventManager = event_manager.getManager()
_scriptManager = script_manager.getManager()
_settingsManager = settings_manager.getManager()
_logger = logger.getLogger()

try:
    # If we don't have an active desktop, we will get a RuntimeError.
    from . import mouse_review
except RuntimeError:
    pass

def onEnabledChanged(gsetting, key):
    try:
        enabled = gsetting.get_boolean(key)
    except:
        return

    if key == 'screen-reader-enabled' and not enabled:
        shutdown()

def getSettingsManager():
    return _settingsManager

def getLogger():
    return _logger

EXIT_CODE_HANG = 50

# The user-settings module (see loadUserSettings).
#
_userSettings = None

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
        try:
            appname = "'" + app.name + "'"
        except:
            appname = "None"
        try:
            name = orca_state.locusOfFocus.name
            rolename = orca_state.locusOfFocus.getRoleName()
        except:
            name = "Error"
            rolename = "Error"
        debug.println(debug.LEVEL_FINE,
                      "LOCUS OF FOCUS: app=%s name='%s' role='%s'" \
                      % (appname, name, rolename))

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
# METHODS FOR PRE-PROCESSING AND MASSAGING KEYBOARD EVENTS.            #
#                                                                      #
########################################################################

_orcaModifierPressed = False

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

    keyboardEvent = KeyboardEvent(event)
    debug.println(debug.LEVEL_FINE, keyboardEvent.toString())

    # Weed out duplicate and otherwise bogus events.
    # TODO - JD: Be sure these are the right values to return
    if not keyboardEvent.timestamp:
        debug.println(debug.LEVEL_FINE, "IGNORING EVENT: NO TIMESTAMP")
        return False
    if keyboardEvent == orca_state.lastInputEvent:
        debug.println(debug.LEVEL_FINE, "IGNORING EVENT: DUPLICATE")
        return False

    # Figure out what we've got.
    isOrcaModifier = keyboardEvent.isOrcaModifier()
    isPressedEvent = keyboardEvent.isPressedKey()
    if isOrcaModifier:
        _orcaModifierPressed = isPressedEvent
    if _orcaModifierPressed:
        keyboardEvent.modifiers |= keybindings.ORCA_MODIFIER_MASK

    # Update our state.
    orca_state.lastInputEvent = keyboardEvent
    if not keyboardEvent.isModifierKey():
        keyboardEvent.setClickCount()
        orca_state.lastNonModifierKeyEvent = keyboardEvent

    # Echo it based on what it is and the user's settings.
    script = orca_state.activeScript
    if not script:
        debug.println(debug.LEVEL_FINE, "IGNORING EVENT DUE TO NO SCRIPT")
        return False

    if isPressedEvent:
        if not orca_state.activeWindow:
            orca_state.activeWindow = script.utilities.activeWindow()
        script.presentationInterrupt()
    script.presentKeyboardEvent(keyboardEvent)
    if keyboardEvent.isModifierKey() and not isOrcaModifier:
        return False
 
    # Special modes.
    if not isPressedEvent and keyboardEvent.event_string == "Escape":
        script.exitLearnMode(keyboardEvent)
    if orca_state.learnModeEnabled and not keyboardEvent.modifiers:
        if keyboardEvent.event_string == "F1":
            orca_state.learnModeEnabled = False
            return helpForOrca()
        if isPressedEvent and keyboardEvent.event_string in ["F2", "F3"]:
            return script.listOrcaShortcuts(keyboardEvent)
    if orca_state.capturingKeys:
        return False
    if notification_messages.listNotificationMessagesModeEnabled:
        return notification_messages.listNotificationMessages(script, keyboardEvent)

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
        _orcaModifierPressed = False
        orca_state.bypassNextCommand = False
 
    return isOrcaModifier or orca_state.learnModeEnabled

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

    if (not consumed) and orca_state.learnModeEnabled:
        consumed = True

    return consumed

########################################################################
#                                                                      #
# METHODS FOR HANDLING INITIALIZATION, SHUTDOWN, AND USE.              #
#                                                                      #
########################################################################

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
    lines = _originalXmodmap.decode('UTF-8').split('\n')
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
                    _setXmodmap(bytes('\n'.join(lines), 'UTF-8'))
                    return
            else:
                if capsModLineProg.match(line):
                    lines[i] = normalCapsLine
                    _setXmodmap(bytes('\n'.join(lines), 'UTF-8'))
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

    debug.println(debug.LEVEL_FINEST, 'INFO: Loading User Settings')

    global _userSettings

    # Shutdown the output drivers and give them a chance to die.

    speech.shutdown()
    braille.shutdown()

    _scriptManager.deactivate()

    reloaded = False
    if _userSettings:
        _profile = _settingsManager.getSetting('activeProfile')[1]
        try:
            _userSettings = _settingsManager.getGeneralSettings(_profile)
            _settingsManager.setProfile(_profile)
            reloaded = True
        except ImportError:
            debug.printException(debug.LEVEL_FINEST)
        except:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        _profile = _settingsManager.profile
        try:
            _userSettings = _settingsManager.getGeneralSettings(_profile)
        except ImportError:
            debug.printException(debug.LEVEL_FINEST)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    _settingsManager.loadAppSettings(script)

    if _settingsManager.getSetting('enableSpeech'):
        try:
            speech.init()
            if reloaded and not skipReloadMessage:
                speech.speak(messages.SETTINGS_RELOADED,
                             settings.voices.get(settings.SYSTEM_VOICE))
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Speech module has been initialized.")
        except:
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to speech.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")

    if _settingsManager.getSetting('enableBraille'):
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

    _scriptManager.activate()
    _eventManager.activate()

    debug.println(debug.LEVEL_FINEST, 'INFO: User Settings Loaded')

    return True

def _showPreferencesUI(script, prefs):
    if orca_state.orcaOS:
        orca_state.orcaOS.showGUI()
        return

    try:
        module = importlib.import_module('.orca_gui_prefs', 'orca')
    except:
        debug.printException(debug.LEVEL_SEVERE)
        return

    uiFile = os.path.join(orca_platform.datadir,
                          orca_platform.package,
                          "ui",
                          "orca-setup.ui")

    orca_state.orcaOS = module.OrcaSetupGUI(uiFile, "orcaSetupWindow", prefs)
    orca_state.orcaOS.init(script)
    orca_state.orcaOS.showGUI()

def showAppPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interace to configure the settings for a
    specific applications within Orca and set up those app-specific
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    prefs = {}
    for key in settings.userCustomizableSettings:
        prefs[key] = _settingsManager.getSetting(key)

    script = script or orca_state.activeScript
    _showPreferencesUI(script, prefs)

    return True

def showPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interace to configure Orca and set up
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    prefs = _settingsManager.getGeneralSettings(_settingsManager.profile)
    script = _scriptManager.getDefaultScript()
    _showPreferencesUI(script, prefs)

    return True

def helpForOrca(script=None, inputEvent=None, page=""):
    """Show Orca Help window (part of the GNOME Access Guide).

    Returns True to indicate the input event has been consumed.
    """
    uri = "help:orca"
    if page:
        uri += "?%s" % page
    Gtk.show_uri(Gdk.Screen.get_default(),
                 uri,
                 Gtk.get_current_event_time())
    return True

def quitOrca(script=None, inputEvent=None):
    """Quit Orca. Check if the user wants to confirm this action.
    If so, show the confirmation GUI otherwise just shutdown.

    Returns True to indicate the input event has been consumed.
    """

    shutdown()

    return True

def showFindGUI(script=None, inputEvent=None):
    """Displays the user interace to perform an Orca Find.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = importlib.import_module('.orca_gui_find', 'orca')
        module.showFindUI()
    except:
        debug.printException(debug.LEVEL_SEVERE)

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

    debug.println(debug.LEVEL_FINEST, 'INFO: Initializing Orca module')

    global _initialized

    if _initialized and _settingsManager.isScreenReaderServiceEnabled():
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
    # In theory, we can do this through dbus. In practice, it fails to
    # work sometimes. Until we know why, we need to leave this as-is
    # so that we respond when gnome-control-center is used to stop Orca.
    if a11yAppSettings:
        a11yAppSettings.connect('changed', onEnabledChanged)

    debug.println(debug.LEVEL_FINEST, 'INFO: Orca module initialized')

    return True

def start(registry, cacheValues):
    """Starts Orca.
    """

    debug.println(debug.LEVEL_FINEST, 'INFO: Starting Orca')

    if not _initialized:
        init(registry)

    # Do not hang on startup if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    if cacheValues:
        pyatspi.setCacheLevel(pyatspi.CACHE_PROPERTIES)

    debug.println(debug.LEVEL_FINEST, 'INFO: Orca starting registry')
    registry.start(gil=False)

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
    debug.examineProcesses()
    die(EXIT_CODE_HANG)

def shutdown(script=None, inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """

    debug.println(debug.LEVEL_FINEST, 'INFO: Shutting down Orca')

    global _initialized

    if not _initialized:
        return False

    # Try to say goodbye, but be defensive if something has hung.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    orca_state.activeScript.presentMessage(messages.STOP_ORCA)

    _scriptManager.deactivate()

    _eventManager.deregisterKeystrokeListener(_processKeyboardEvent)
    _eventManager.deactivate()

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

    debug.println(debug.LEVEL_FINEST, 'INFO: Orca stopping registry')
    pyatspi.Registry.stop()

    debug.println(debug.LEVEL_FINEST, 'INFO: Orca shutdown complete')

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

def main(cacheValues=True):
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

    if not _settingsManager.isAccessibilityEnabled():
        _settingsManager.setAccessibility(True)

    init(pyatspi.Registry)

    try:
        message = messages.START_ORCA
        if not _settingsManager.getSetting('onlySpeakDisplayedText'):
            speech.speak(message, settings.voices.get(settings.SYSTEM_VOICE))
        if _settingsManager.getSetting('enableBraille') \
           or _settingsManager.getSetting('enableBrailleMonitor'):
            braille.displayMessage(message)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    script = orca_state.activeScript
    if script:
        window = script.utilities.activeWindow()
        if window and not orca_state.locusOfFocus:
            setLocusOfFocus(None, window)

    try:
        start(pyatspi.Registry, cacheValues) # waits until we stop the registry
    except:
        die(EXIT_CODE_HANG)
    return 0

if __name__ == "__main__":
    sys.exit(main())
