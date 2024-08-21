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

import faulthandler
import gi
import os
import signal
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
from . import input_event_manager
from . import logger
from . import messages
from . import mouse_review
from . import orca_modifier_manager
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
    return settings_manager.get_manager()

def getLogger():
    return _logger

EXIT_CODE_HANG = 50

# The user-settings module (see loadUserSettings).
#
_userSettings = None

def deviceChangeHandler(deviceManager, device):
    """Handles device-* signals."""

    source = device.get_source()
    if source == Gdk.InputSource.KEYBOARD:
        orca_modifier_manager.get_manager().refresh_orca_modifiers("Keyboard change detected.")

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

    script_manager.get_manager().deactivate()

    reloaded = False
    if _userSettings:
        _profile = settings_manager.get_manager().get_setting('activeProfile')[1]
        try:
            _userSettings = settings_manager.get_manager().get_general_settings(_profile)
            settings_manager.get_manager().set_profile(_profile)
            reloaded = True
        except ImportError:
            debug.printException(debug.LEVEL_INFO)
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)
    else:
        _profile = settings_manager.get_manager().profile
        try:
            _userSettings = settings_manager.get_manager().get_general_settings(_profile)
        except ImportError:
            debug.printException(debug.LEVEL_INFO)
        except Exception:
            debug.printException(debug.LEVEL_SEVERE)

    if not script:
        script = script_manager.get_manager().get_default_script()

    settings_manager.get_manager().load_app_settings(script)

    if settings_manager.get_manager().get_setting('enableSpeech'):
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

    if settings_manager.get_manager().get_setting('enableBraille'):
        msg = 'ORCA: About to enable braille'
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        try:
            braille.init(input_event_manager.get_manager().process_braille_event)
        except Exception:
            debug.printException(debug.LEVEL_WARNING)
            msg = 'ORCA: Could not initialize connection to braille.'
            debug.printMessage(debug.LEVEL_WARNING, msg, True)
    else:
        msg = 'ORCA: Braille is not enabled in settings'
        debug.printMessage(debug.LEVEL_INFO, msg, True)


    if settings_manager.get_manager().get_setting('enableMouseReview'):
        mouse_review.get_reviewer().activate()
    else:
        mouse_review.get_reviewer().deactivate()

    if settings_manager.get_manager().get_setting('enableSound'):
        player.init()

    # Handle the case where a change was made in the Orca Preferences dialog.
    orca_modifier_manager.get_manager().refresh_orca_modifiers("Loading user settings.")

    event_manager.get_manager().activate()
    script_manager.get_manager().activate()

    debug.printMessage(debug.LEVEL_INFO, 'ORCA: User Settings Loaded', True)

    return True

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

    if _initialized and settings_manager.get_manager().is_screen_reader_service_enabled():
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

    script = script_manager.get_manager().get_active_script()
    if script is not None:
        script.presentationInterrupt()
        script.presentMessage(messages.STOP_ORCA, resetStyles=False)

    # Pause event queuing first so that it clears its queue and will not accept new
    # events. Then let the script manager unregister script event listeners as well
    # as key grabs. Finally deactivate the event manager, which will also cause the
    # Atspi.Device to be set to None.
    event_manager.get_manager().pause_queuing(True, True, "Shutting down.")
    script_manager.get_manager().deactivate()
    event_manager.get_manager().deactivate()

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
    orca_modifier_manager.get_manager().unset_orca_modifiers("Shutting down.")

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
    orca_modifier_manager.get_manager().unset_orca_modifiers(f"Shutting down: {signalString}.")

    script = script_manager.get_manager().get_active_script()
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
    if not settings_manager.get_manager().is_accessibility_enabled():
        settings_manager.get_manager().set_accessibility(True)

    debug.printMessage(debug.LEVEL_INFO, "ORCA: Initializing.", True)
    event_manager.get_manager().pause_queuing(True, True, "Initialization not complete.")

    init()
    debug.printMessage(debug.LEVEL_INFO, "ORCA: Initialized.", True)

    try:
        script = script_manager.get_manager().get_default_script()
        script.presentMessage(messages.START_ORCA)
    except Exception:
        debug.printException(debug.LEVEL_SEVERE)

    window = focus_manager.get_manager().find_active_window()
    if window and not focus_manager.get_manager().get_locus_of_focus():
        app = AXObject.get_application(window)

        # TODO - JD: Consider having the focus tracker update the active script.
        script = script_manager.get_manager().get_script(app, window)
        script_manager.get_manager().set_active_script(script, "Launching.")
        focus_manager.get_manager().set_active_window(
            window, app, set_window_as_focus=True, notify_script=True)

        # TODO - JD: Consider having the focus tracker update the active script.
        focusedObject = focus_manager.get_manager().find_focused_object()
        if focusedObject:
            focus_manager.get_manager().set_locus_of_focus(None, focusedObject)
            script = script_manager.get_manager().get_script(
                AXObject.get_application(focusedObject), focusedObject)
            script_manager.get_manager().set_active_script(script, "Found focused object.")

    event_manager.get_manager().pause_queuing(False, False, "Initialization complete.")

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
