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


# ruff: noqa: F401
# This unused import keeps Orca working by making pyatspi still available.
# It can only be removed when we have completely eliminated all uses of
# pyatspi API.
import pyatspi

import faulthandler
import gi
import importlib
import os
import re
import signal
import subprocess
import sys

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk

try:
    from gi.repository.Gio import Settings
    a11yAppSettings = Settings(schema_id='org.gnome.desktop.a11y.applications')
except Exception:
    a11yAppSettings = None

from . import braille
from . import debug
from . import event_manager
from . import focus_manager
from . import logger
from . import messages
from . import mouse_review
from . import orca_state
from . import orca_platform
from . import script_manager
from . import settings
from . import settings_manager
from . import speech
from . import sound
from .ax_object import AXObject

_logger = logger.getLogger()

def onEnabledChanged(gsetting, key):
    try:
        enabled = gsetting.get_boolean(key)
    except Exception:
        return

    if key == 'screen-reader-enabled' and not enabled:
        shutdown()

def getSettingsManager():
    return settings_manager.getManager()

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

def deviceChangeHandler(deviceManager, device):
    """New keyboards being plugged in stomp on our changes to the keymappings,
       so we have to re-apply"""
    source = device.get_source()
    if source == Gdk.InputSource.KEYBOARD:
        msg = "ORCA: Keyboard change detected, re-creating the xmodmap"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        _createOrcaXmodmap()

def updateKeyMap(keyboardEvent):
    """Unsupported convenience method to call sad hacks which should go away."""

    global _restoreOrcaKeys
    if keyboardEvent.isPressedKey():
        return

    if keyboardEvent.event_string in settings.orcaModifierKeys \
       and orca_state.bypassNextCommand:
        _restoreXmodmap()
        _restoreOrcaKeys = True
        return

    if _restoreOrcaKeys and not orca_state.bypassNextCommand:
        _createOrcaXmodmap()
        _restoreOrcaKeys = False

def _setXmodmap(xkbmap):
    """Set the keyboard map using xkbcomp."""
    p = subprocess.Popen(['xkbcomp', '-w0', '-', os.environ['DISPLAY']],
        stdin=subprocess.PIPE, stdout=None, stderr=None)
    p.communicate(xkbmap)

def _setCapsLockAsOrcaModifier(enable):
    """Enable or disable use of the caps lock key as an Orca modifier key."""
    interpretCapsLineProg = re.compile(
        r'^\s*interpret\s+Caps[_+]Lock[_+]AnyOfOrNone\s*\(all\)\s*{\s*$', re.I)
    normalCapsLineProg = re.compile(
        r'^\s*action\s*=\s*LockMods\s*\(\s*modifiers\s*=\s*Lock\s*\)\s*;\s*$', re.I)
    interpretShiftLineProg = re.compile(
        r'^\s*interpret\s+Shift[_+]Lock[_+]AnyOf\s*\(\s*Shift\s*\+\s*Lock\s*\)\s*{\s*$', re.I)
    normalShiftLineProg = re.compile(
        r'^\s*action\s*=\s*LockMods\s*\(\s*modifiers\s*=\s*Shift\s*\)\s*;\s*$', re.I)
    disabledModLineProg = re.compile(
        r'^\s*action\s*=\s*NoAction\s*\(\s*\)\s*;\s*$', re.I)
    normalCapsLine = '        action= LockMods(modifiers=Lock);'
    normalShiftLine = '        action= LockMods(modifiers=Shift);'
    disabledModLine = '        action= NoAction();'
    lines = _originalXmodmap.decode('UTF-8').split('\n')
    foundCapsInterpretSection = False
    foundShiftInterpretSection = False
    modified = False
    for i, line in enumerate(lines):
        if not foundCapsInterpretSection and not foundShiftInterpretSection:
            if interpretCapsLineProg.match(line):
                foundCapsInterpretSection = True
            elif interpretShiftLineProg.match(line):
                foundShiftInterpretSection = True
        elif foundCapsInterpretSection:
            if enable:
                if normalCapsLineProg.match(line):
                    lines[i] = disabledModLine
                    modified = True
            else:
                if disabledModLineProg.match(line):
                    lines[i] = normalCapsLine
                    modified = True
            if line.find('}'):
                foundCapsInterpretSection = False
        else: # foundShiftInterpretSection
            if enable:
                if normalShiftLineProg.match(line):
                    lines[i] = disabledModLine
                    modified = True
            else:
                if disabledModLineProg.match(line):
                    lines[i] = normalShiftLine
                    modified = True
            if line.find('}'):
                foundShiftInterpretSection = False
    if modified:
        _setXmodmap(bytes('\n'.join(lines), 'UTF-8'))

def _createOrcaXmodmap():
    """Makes an Orca-specific Xmodmap so that the keys behave as we
    need them to do. This is especially the case for the Orca modifier.
    """

    global _capsLockCleared

    if "Caps_Lock" in settings.orcaModifierKeys \
       or "Shift_Lock" in settings.orcaModifierKeys:
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

    msg = "ORCA: Attempting to restore original xmodmap"
    debug.printMessage(debug.LEVEL_INFO, msg, True)

    global _capsLockCleared
    _capsLockCleared = False
    p = subprocess.Popen(['xkbcomp', '-w0', '-', os.environ['DISPLAY']],
        stdin=subprocess.PIPE, stdout=None, stderr=None)
    p.communicate(_originalXmodmap)

    msg = "ORCA: Original xmodmap restored"
    debug.printMessage(debug.LEVEL_INFO, msg, True)

def loadUserSettings(script=None, inputEvent=None, skipReloadMessage=False):
    """Loads (and reloads) the user settings module, reinitializing
    things such as speech if necessary.

    Returns True to indicate the input event has been consumed.
    """

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Loading User Settings', True)

    global _userSettings

    # Shutdown the output drivers and give them a chance to die.

    player = sound.getPlayer()
    player.shutdown()
    speech.shutdown()
    braille.shutdown()

    script_manager.getManager().deactivate()

    reloaded = False
    if _userSettings:
        _profile = settings_manager.getManager().getSetting('activeProfile')[1]
        try:
            _userSettings = settings_manager.getManager().getGeneralSettings(_profile)
            settings_manager.getManager().setProfile(_profile)
            reloaded = True
        except ImportError:
            debug.printException(debug.LEVEL_INFO)
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        _profile = settings_manager.getManager().profile
        try:
            _userSettings = settings_manager.getManager().getGeneralSettings(_profile)
        except ImportError:
            debug.printException(debug.LEVEL_INFO)
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)

    if not script:
        script = script_manager.getManager().getDefaultScript()

    settings_manager.getManager().loadAppSettings(script)

    if settings_manager.getManager().getSetting('enableSpeech'):
        msg = 'ORCA: About to enable speech'
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        try:
            speech.init()
            if reloaded and not skipReloadMessage:
                script.speakMessage(messages.SETTINGS_RELOADED)
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        msg = 'ORCA: Speech is not enabled in settings'
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    if settings_manager.getManager().getSetting('enableBraille'):
        msg = 'ORCA: About to enable braille'
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        try:
            braille.init(event_manager.getManager().processBrailleEvent)
        except Exception:
            debug.printException(debug.LEVEL_WARNING)
            msg = 'ORCA: Could not initialize connection to braille.'
            debug.printMessage(debug.LEVEL_WARNING, msg, True)
    else:
        msg = 'ORCA: Braille is not enabled in settings'
        debug.printMessage(debug.LEVEL_INFO, msg, True)


    if settings_manager.getManager().getSetting('enableMouseReview'):
        mouse_review.getReviewer().activate()
    else:
        mouse_review.getReviewer().deactivate()

    if settings_manager.getManager().getSetting('enableSound'):
        player.init()

    global _orcaModifiers
    custom = [k for k in settings.orcaModifierKeys if k not in _orcaModifiers]
    _orcaModifiers += custom
    # Handle the case where a change was made in the Orca Preferences dialog.
    #
    if _originalXmodmap:
        _restoreXmodmap(_orcaModifiers)

    _storeXmodmap(_orcaModifiers)
    _createOrcaXmodmap()

    event_manager.getManager().activate()
    script_manager.getManager().activate()

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: User Settings Loaded', True)

    return True

def _showPreferencesUI(script, prefs):
    if orca_state.orcaOS:
        orca_state.orcaOS.showGUI()
        return

    try:
        module = importlib.import_module('.orca_gui_prefs', 'orca')
    except Exception:
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
    """Displays the user interface to configure the settings for a
    specific applications within Orca and set up those app-specific
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    prefs = {}
    for key in settings.userCustomizableSettings:
        prefs[key] = settings_manager.getManager().getSetting(key)

    if script is None:
        script = script_manager.getManager().getActiveScript()
    _showPreferencesUI(script, prefs)

    return True

def showPreferencesGUI(script=None, inputEvent=None):
    """Displays the user interface to configure Orca and set up
    user preferences using a GUI.

    Returns True to indicate the input event has been consumed.
    """

    prefs = settings_manager.getManager().getGeneralSettings(settings_manager.getManager().profile)
    script = script_manager.getManager().getDefaultScript()
    _showPreferencesUI(script, prefs)

    return True

def addKeyGrab(binding):
    """ Add a key grab for the given key binding."""

    if orca_state.device is None:
        return []

    ret = []
    for kd in binding.keyDefs():
        ret.append(orca_state.device.add_key_grab(kd, None))
    return ret

def removeKeyGrab(id):
    """ Remove the key grab for the given key binding."""

    if orca_state.device is None:
        return

    orca_state.device.remove_key_grab(id)

def quitOrca(script=None, inputEvent=None):
    """Quit Orca. Check if the user wants to confirm this action.
    If so, show the confirmation GUI otherwise just shutdown.

    Returns True to indicate the input event has been consumed.
    """

    shutdown()

    return True

def showFindGUI(script=None, inputEvent=None):
    """Displays the user interface to perform an Orca Find.

    Returns True to indicate the input event has been consumed.
    """

    try:
        module = importlib.import_module('.orca_gui_find', 'orca')
        module.showFindUI()
    except Exception:
        debug.printException(debug.LEVEL_SEVERE)

# If True, this module has been initialized.
#
_initialized = False

def init():
    """Initialize the orca module, which initializes the speech and braille
    modules.  Also builds up the application list, registers for AT-SPI events,
    and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Initializing', True)

    global _initialized

    if _initialized and settings_manager.getManager().isScreenReaderServiceEnabled():
        debug.printMessage(debug.LEVEL_INFO, 'ORCA: Already initialized', True)
        return False

    # Do not hang on initialization if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    loadUserSettings()

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    _initialized = True
    # In theory, we can do this through dbus. In practice, it fails to
    # work sometimes. Until we know why, we need to leave this as-is
    # so that we respond when gnome-control-center is used to stop Orca.
    if a11yAppSettings:
        a11yAppSettings.connect('changed', onEnabledChanged)

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Initialized', True)

    return True

def start():
    """Starts Orca."""

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Starting', True)

    if not _initialized:
        init()

    # Do not hang on startup if we can help it.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    # Event handlers for input devices being plugged in/unplugged.
    # Used to re-create the Xmodmap when a new keyboard is plugged in.
    # Necessary, because plugging in a new keyboard resets the Xmodmap
    # and stomps our changes
    display = Gdk.Display.get_default()
    devmanager=display.get_device_manager()
    devmanager.connect("device-added", deviceChangeHandler)
    devmanager.connect("device-removed", deviceChangeHandler)

    Gdk.notify_startup_complete()
    msg = 'ORCA: Startup complete notification made'
    debug.printMessage(debug.LEVEL_INFO, msg, True)

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Starting Atspi main event loop', True)
    Atspi.event_main()

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
    msg = 'TIMEOUT: something has hung. Aborting.'
    debug.printMessage(debug.LEVEL_SEVERE, msg, True)
    debug.printStack(debug.LEVEL_SEVERE)
    debug.examineProcesses(force=True)
    die(EXIT_CODE_HANG)

def shutdown(script=None, inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Shutting down', True)

    global _initialized

    if not _initialized:
        return False

    # Try to say goodbye, but be defensive if something has hung.
    #
    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.signal(signal.SIGALRM, settings.timeoutCallback)
        signal.alarm(settings.timeoutTime)

    script = script_manager.getManager().getActiveScript()
    if script is not None:
        script.presentationInterrupt()
        script.presentMessage(messages.STOP_ORCA, resetStyles=False)

    # Deactivate the event manager first so that it clears its queue and will not
    # accept new events. Then let the script manager unregister script event listeners.
    event_manager.getManager().deactivate()
    script_manager.getManager().deactivate()

    # Shutdown all the other support.
    #
    if settings.enableSpeech:
        speech.shutdown()
    if settings.enableBraille:
        braille.shutdown()
    if settings.enableSound:
        player = sound.getPlayer()
        player.shutdown()

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    _initialized = False
    _restoreXmodmap(_orcaModifiers)

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Quitting Atspi main event loop', True)
    Atspi.event_quit()
    debug.printMessage(debug.LEVEL_INFO, 'ORCA: Shutdown complete', True)

    return True

exitCount = 0
def shutdownOnSignal(signum, frame):
    global exitCount

    signalString = f'({signal.strsignal(signum)})'
    msg = f"ORCA: Shutting down and exiting due to signal={signum} {signalString}"
    debug.printMessage(debug.LEVEL_INFO, msg, True)

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
    except Exception:
        cleanExit = False

    if settings.timeoutCallback and (settings.timeoutTime > 0):
        signal.alarm(0)

    if not cleanExit:
        die(EXIT_CODE_HANG)

def crashOnSignal(signum, frame):
    signalString = f'({signal.strsignal(signum)})'
    msg = f"ORCA: Shutting down and exiting due to signal={signum} {signalString}"
    debug.printMessage(debug.LEVEL_SEVERE, msg, True)
    debug.printStack(debug.LEVEL_SEVERE)
    _restoreXmodmap(_orcaModifiers)

    script = script_manager.getManager().getActiveScript()
    if script is not None:
        script.presentationInterrupt()
        script.presentMessage(messages.STOP_ORCA, resetStyles=False)

    sys.exit(1)

def main():
    """The main entry point for Orca.  The exit codes for Orca will
    loosely be based on signals, where the exit code will be the
    signal used to terminate Orca (if a signal was used).  Otherwise,
    an exit code of 0 means normal completion and an exit code of 50
    means Orca exited because of a hang."""

    msg = f"ORCA: Launching version {orca_platform.version}"
    if orca_platform.revision:
        msg += f" (rev {orca_platform.revision})"

    atspiVersion = Atspi.get_version()
    msg += f" AT-SPI2 version: {atspiVersion[0]}.{atspiVersion[1]}.{atspiVersion[2]}"
    sessionType = os.environ.get('XDG_SESSION_TYPE') or ""
    sessionDesktop = os.environ.get('XDG_SESSION_DESKTOP') or ""
    session = "%s %s".strip() % (sessionType, sessionDesktop)
    if session:
        msg += f" Session: {session}"
    debug.printMessage(debug.LEVEL_INFO, msg, True)

    if debug.debugFile and os.path.exists(debug.debugFile.name):
        faulthandler.enable(file=debug.debugFile, all_threads=True)
    else:
        faulthandler.enable(all_threads=False)

    # Method to call when we think something might be hung.
    #
    settings.timeoutCallback = timeout

    # Various signal handlers we want to listen for.
    #
    signal.signal(signal.SIGHUP, shutdownOnSignal)
    signal.signal(signal.SIGINT, shutdownOnSignal)
    signal.signal(signal.SIGTERM, shutdownOnSignal)
    signal.signal(signal.SIGQUIT, shutdownOnSignal)
    signal.signal(signal.SIGSEGV, crashOnSignal)

    debug.printMessage(debug.LEVEL_INFO, "ORCA: Enabling accessibility (if needed).", True)
    if not settings_manager.getManager().isAccessibilityEnabled():
        settings_manager.getManager().setAccessibility(True)

    debug.printMessage(debug.LEVEL_INFO, "ORCA: Initializing.", True)
    init()
    debug.printMessage(debug.LEVEL_INFO, "ORCA: Initialized.", True)

    try:
        script = script_manager.getManager().getDefaultScript()
        script.presentMessage(messages.START_ORCA)
    except Exception:
        debug.printException(debug.LEVEL_SEVERE)

    window = focus_manager.getManager().find_active_window()
    if window and not focus_manager.getManager().get_locus_of_focus():
        app = AXObject.get_application(window)
        focus_manager.getManager().set_active_window(
            window, app, set_window_as_focus=True, notify_script=True)

        # set_active_window does some corrective work needed thanks to
        # mutter-x11-frames. So retrieve the window just in case.
        window = focus_manager.getManager().get_active_window()
        script = script_manager.getManager().getScript(app, window)
        script_manager.getManager().setActiveScript(script, "Launching.")

        # TODO - JD: Consider having the focus tracker update the active script.
        focusedObject = focus_manager.getManager().find_focused_object()
        if focusedObject:
            focus_manager.getManager().set_locus_of_focus(None, focusedObject)
            script = script_manager.getManager().getScript(
                AXObject.get_application(focusedObject), focusedObject)
            script_manager.getManager().setActiveScript(script, "Found focused object.")

    try:
        msg = "ORCA: Starting ATSPI registry."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        start() # waits until we stop the registry
    except Exception:
        msg = "ORCA: Exception starting ATSPI registry."
        debug.printMessage(debug.LEVEL_SEVERE, msg, True)
        die(EXIT_CODE_HANG)
    return 0

if __name__ == "__main__":
    sys.exit(main())
