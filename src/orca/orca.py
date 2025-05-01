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
from . import speech_and_verbosity_manager
from . import sound
from .ax_utilities import AXUtilities

# The user-settings module (see loadUserSettings).
#
_userSettings = None

def loadUserSettings(script=None, skipReloadMessage=False):
    """(Re)Loads the user settings module, re-initializing things such as speech if necessary."""

    debug.print_message(debug.LEVEL_INFO, 'ORCA: Loading User Settings', True)

    global _userSettings

    # Shutdown the output drivers and give them a chance to die.

    player = sound.getPlayer()
    player.shutdown()
    speech_and_verbosity_manager.get_manager().shutdown_speech()
    braille.shutdown()
    mouse_review.get_reviewer().deactivate()

    event_manager.get_manager().pause_queuing(True, True, "Loading user settings.")
    reloaded = False
    if _userSettings:
        _profile = settings_manager.get_manager().get_setting('activeProfile')[1]
        _userSettings = settings_manager.get_manager().get_general_settings(_profile)
        settings_manager.get_manager().set_profile(_profile)
        reloaded = True
    else:
        _profile = settings_manager.get_manager().profile
        _userSettings = settings_manager.get_manager().get_general_settings(_profile)

    if not script:
        script = script_manager.get_manager().get_default_script()

    settings_manager.get_manager().load_app_settings(script)

    if settings_manager.get_manager().get_setting('enableSpeech'):
        speech_and_verbosity_manager.get_manager().start_speech()
        if reloaded and not skipReloadMessage:
            script.speakMessage(messages.SETTINGS_RELOADED)

    if settings_manager.get_manager().get_setting('enableBraille'):
        braille.init(input_event_manager.get_manager().process_braille_event)

    # TODO - JD: This ultimately belongs in an extension manager.
    if settings_manager.get_manager().get_setting('enableMouseReview'):
        mouse_review.get_reviewer().activate()

    if settings_manager.get_manager().get_setting('enableSound'):
        player.init()

    # Handle the case where a change was made in the Orca Preferences dialog.
    orca_modifier_manager.get_manager().refresh_orca_modifiers("Loading user settings.")
    event_manager.get_manager().pause_queuing(False, False, "User settings loaded.")
    debug.print_message(debug.LEVEL_INFO, "ORCA: User Settings Loaded", True)

    manager = debugging_tools_manager.get_manager()
    manager.print_session_details()
    manager.print_running_applications(force=False)

def timeout(signum=None, frame=None):
    msg = 'TIMEOUT: something has hung. Aborting.'
    debug.print_message(debug.LEVEL_SEVERE, msg, True)
    debugging_tools_manager.get_manager().print_running_applications(force=True)
    os.kill(os.getpid(), signal.SIGKILL)

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

    # Pause event queuing first so that it clears its queue and will not accept new
    # events. Then let the script manager unregister script event listeners as well
    # as key grabs. Finally deactivate the event manager, which will also cause the
    # Atspi.Device to be set to None.
    event_manager.get_manager().pause_queuing(True, True, "Shutting down.")
    script_manager.get_manager().deactivate()
    event_manager.get_manager().deactivate()

    # TODO - JD: This ultimately belongs in an extension manager.
    clipboard.get_presenter().deactivate()
    mouse_review.get_reviewer().deactivate()

    # Shutdown all the other support.
    #
    if settings.enableSpeech:
        speech_and_verbosity_manager.get_manager().shutdown_speech()
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

    signal.signal(signal.SIGHUP, shutdownOnSignal)
    signal.signal(signal.SIGINT, shutdownOnSignal)
    signal.signal(signal.SIGTERM, shutdownOnSignal)
    signal.signal(signal.SIGQUIT, shutdownOnSignal)

    debug.print_message(debug.LEVEL_INFO, "ORCA: Enabling accessibility (if needed).", True)
    if not settings_manager.get_manager().is_accessibility_enabled():
        settings_manager.get_manager().set_accessibility(True)

    loadUserSettings()

    def _on_enabled_changed(gsetting, key):
        enabled = gsetting.get_boolean(key)
        msg = f"ORCA: {key} changed to {enabled}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if key == "screen-reader-enabled" and not enabled:
            shutdown()

    try:
        _a11y_applications_gsetting = Settings(schema_id="org.gnome.desktop.a11y.applications")
        connection = _a11y_applications_gsetting.connect("changed", _on_enabled_changed)
        msg = f"ORCA: Connected to a11y applications gsetting: {bool(connection)}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
    except Exception as error:
        msg = f"ORCA: Exception connecting to a11y applications gsetting: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)

    script = script_manager.get_manager().get_default_script()
    script.presentMessage(messages.START_ORCA)

    event_manager.get_manager().activate()
    script_manager.get_manager().activate()
    window = AXUtilities.find_active_window()
    if window and not focus_manager.get_manager().get_locus_of_focus():
        app = AXUtilities.get_application(window)
        focus_manager.get_manager().set_active_window(
            window, app, set_window_as_focus=True, notify_script=True)

        focused_object = focus_manager.get_manager().find_focused_object()
        if focused_object:
            focus_manager.get_manager().set_locus_of_focus(None, focused_object)

        script = script_manager.get_manager().get_script(app, focused_object or window)
        script_manager.get_manager().set_active_script(script, "Launching.")

    clipboard.get_presenter().activate()
    Gdk.notify_startup_complete()

    try:
        debug.print_message(debug.LEVEL_INFO, "ORCA: Starting Atspi main event loop", True)
        Atspi.event_main()
    except Exception as error:
        msg = f"ORCA: Exception starting ATSPI registry: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        os.kill(os.getpid(), signal.SIGKILL)
    return 0

if __name__ == "__main__":
    sys.exit(main())
