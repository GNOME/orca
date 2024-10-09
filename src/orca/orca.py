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
import os
import signal
import sys

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk
from gi.repository.Gio import Settings

from . import braille
from . import clipboard
from . import debug
from . import debugging_tools_manager
from . import event_manager
from . import focus_manager
from . import input_event_manager
from . import messages
from . import mouse_review
from . import orca_modifier_manager
from . import script_manager
from . import settings
from . import settings_manager
from . import speech
from . import sound
from .ax_utilities import AXUtilities

def onEnabledChanged(gsetting, key):
    try:
        enabled = gsetting.get_boolean(key)
    except Exception:
        return

    if key == 'screen-reader-enabled' and not enabled:
        shutdown()

EXIT_CODE_HANG = 50

# The user-settings module (see loadUserSettings).
#
_userSettings = None

def loadUserSettings(script=None, inputEvent=None, skipReloadMessage=False):
    """Loads (and reloads) the user settings module, reinitializing
    things such as speech if necessary.

    Returns True to indicate the input event has been consumed.
    """

    debug.print_message(debug.LEVEL_INFO, 'ORCA: Loading User Settings', True)

    global _userSettings

    # Shutdown the output drivers and give them a chance to die.

    player = sound.getPlayer()
    player.shutdown()
    speech.shutdown()
    braille.shutdown()

    event_manager.get_manager().pause_queuing(True, True, "Loading user settings.")
    reloaded = False
    if _userSettings:
        _profile = settings_manager.get_manager().get_setting('activeProfile')[1]
        try:
            _userSettings = settings_manager.get_manager().get_general_settings(_profile)
            settings_manager.get_manager().set_profile(_profile)
            reloaded = True
        except ImportError:
            debug.print_exception(debug.LEVEL_INFO)
        except Exception:
            debug.print_exception(debug.LEVEL_SEVERE)
    else:
        _profile = settings_manager.get_manager().profile
        try:
            _userSettings = settings_manager.get_manager().get_general_settings(_profile)
        except ImportError:
            debug.print_exception(debug.LEVEL_INFO)
        except Exception:
            debug.print_exception(debug.LEVEL_SEVERE)

    if not script:
        script = script_manager.get_manager().get_default_script()

    settings_manager.get_manager().load_app_settings(script)

    if settings_manager.get_manager().get_setting('enableSpeech'):
        msg = 'ORCA: About to enable speech'
        debug.print_message(debug.LEVEL_INFO, msg, True)
        try:
            speech.init()
            if reloaded and not skipReloadMessage:
                script.speakMessage(messages.SETTINGS_RELOADED)
        except Exception:
            debug.print_exception(debug.LEVEL_SEVERE)
    else:
        msg = 'ORCA: Speech is not enabled in settings'
        debug.print_message(debug.LEVEL_INFO, msg, True)

    if settings_manager.get_manager().get_setting('enableBraille'):
        msg = 'ORCA: About to enable braille'
        debug.print_message(debug.LEVEL_INFO, msg, True)
        try:
            braille.init(input_event_manager.get_manager().process_braille_event)
        except Exception:
            debug.print_exception(debug.LEVEL_WARNING)
            msg = 'ORCA: Could not initialize connection to braille.'
            debug.print_message(debug.LEVEL_WARNING, msg, True)
    else:
        msg = 'ORCA: Braille is not enabled in settings'
        debug.print_message(debug.LEVEL_INFO, msg, True)


    if settings_manager.get_manager().get_setting('enableMouseReview'):
        mouse_review.get_reviewer().activate()
    else:
        mouse_review.get_reviewer().deactivate()

    if settings_manager.get_manager().get_setting('enableSound'):
        player.init()

    # Handle the case where a change was made in the Orca Preferences dialog.
    orca_modifier_manager.get_manager().refresh_orca_modifiers("Loading user settings.")
    event_manager.get_manager().pause_queuing(False, False, "User settings loaded.")
    debug.print_message(debug.LEVEL_INFO, "ORCA: User Settings Loaded", True)
    return True

def die(exitCode=1):
    pid = os.getpid()
    if exitCode == EXIT_CODE_HANG:
        # Someting is hung and we wish to abort.
        os.kill(pid, signal.SIGKILL)
        return

    shutdown()
    sys.exit(exitCode)

def timeout(signum=None, frame=None):
    msg = 'TIMEOUT: something has hung. Aborting.'
    debug.print_message(debug.LEVEL_SEVERE, msg, True)
    debugging_tools_manager.get_manager().print_running_applications(force=True)
    die(EXIT_CODE_HANG)

def shutdown(script=None, inputEvent=None, signum=None):
    """Exits Orca. Returns True if shutdown ran to completion."""

    debug.print_message(debug.LEVEL_INFO, "ORCA: Shutting down", True)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(5)

    orca_modifier_manager.get_manager().unset_orca_modifiers("Shutting down.")
    script = script_manager.get_manager().get_active_script()
    if script is not None:
        script.presentationInterrupt()
        script.presentMessage(messages.STOP_ORCA, resetStyles=False)

    if signum == signal.SIGSEGV:
        sys.exit(1)

    # Pause event queuing first so that it clears its queue and will not accept new
    # events. Then let the script manager unregister script event listeners as well
    # as key grabs. Finally deactivate the event manager, which will also cause the
    # Atspi.Device to be set to None.
    event_manager.get_manager().pause_queuing(True, True, "Shutting down.")
    script_manager.get_manager().deactivate()
    event_manager.get_manager().deactivate()
    clipboard.get_presenter().deactivate()

    # Shutdown all the other support.
    #
    if settings.enableSpeech:
        speech.shutdown()
    if settings.enableBraille:
        braille.shutdown()
    if settings.enableSound:
        player = sound.getPlayer()
        player.shutdown()

    signal.alarm(0)
    debug.print_message(debug.LEVEL_INFO, 'ORCA: Quitting Atspi main event loop', True)
    Atspi.event_quit()
    debug.print_message(debug.LEVEL_INFO, 'ORCA: Shutdown complete', True)
    return True

def shutdownOnSignal(signum, frame):
    signalString = f'({signal.strsignal(signum)})'
    msg = f"ORCA: Shutting down and exiting due to signal={signum} {signalString}"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    shutdown(signum=signum)

def main():
    """The main entry point for Orca.  The exit codes for Orca will
    loosely be based on signals, where the exit code will be the
    signal used to terminate Orca (if a signal was used).  Otherwise,
    an exit code of 0 means normal completion and an exit code of 50
    means Orca exited because of a hang."""

    manager = debugging_tools_manager.get_manager()
    manager.print_session_details()
    manager.print_running_applications(force=False)

    signal.signal(signal.SIGHUP, shutdownOnSignal)
    signal.signal(signal.SIGINT, shutdownOnSignal)
    signal.signal(signal.SIGTERM, shutdownOnSignal)
    signal.signal(signal.SIGQUIT, shutdownOnSignal)

    # TODO - JD: Handling was added for this signal so that we could restore CapsLock during a
    # crash. But handling this signal is generally not recommended. If there's a crash, fixing
    # that seems more important than cleaning up CapsLock.
    signal.signal(signal.SIGSEGV, shutdownOnSignal)

    debug.print_message(debug.LEVEL_INFO, "ORCA: Enabling accessibility (if needed).", True)
    if not settings_manager.get_manager().is_accessibility_enabled():
        settings_manager.get_manager().set_accessibility(True)

    loadUserSettings()

    try:
        Settings(schema_id="org.gnome.desktop.a11y.applications").connect(
            "changed", onEnabledChanged)
    except Exception as error:
        msg = f"ORCA: Exception connecting to a11y applications gsetting: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)

    script = script_manager.get_manager().get_default_script()
    script.presentMessage(messages.START_ORCA)

    event_manager.get_manager().activate()
    window = focus_manager.get_manager().find_active_window()
    if window and not focus_manager.get_manager().get_locus_of_focus():
        app = AXUtilities.get_application(window)

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
                AXUtilities.get_application(focusedObject), focusedObject)
            script_manager.get_manager().set_active_script(script, "Found focused object.")

    script_manager.get_manager().activate()
    clipboard.get_presenter().activate()
    Gdk.notify_startup_complete()

    try:
        debug.print_message(debug.LEVEL_INFO, "ORCA: Starting Atspi main event loop", True)
        Atspi.event_main()
    except Exception as error:
        msg = f"ORCA: Exception starting ATSPI registry: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        die(EXIT_CODE_HANG)
    return 0

if __name__ == "__main__":
    sys.exit(main())
