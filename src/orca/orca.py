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

# pylint: disable=too-many-statements
# pylint: disable=wrong-import-position

"""The main module for the Orca screen reader."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2011 The Orca Team" \
                "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

import os
import signal
import sys

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Atspi
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib

from . import braille
from . import braille_presenter
from . import clipboard
from . import dbus_service
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
from . import systemd
from .ax_utilities import AXUtilities

def load_user_settings(script=None, skip_reload_message=False, is_reload=True):
    """(Re)Loads the user settings module, re-initializing things such as speech if necessary."""

    debug.print_message(debug.LEVEL_INFO, 'ORCA: Loading User Settings', True)

    if is_reload:
        sound.get_player().shutdown()
        speech_and_verbosity_manager.get_manager().shutdown_speech()
        braille.shutdown()
        mouse_review.get_reviewer().deactivate()

    event_manager.get_manager().pause_queuing(True, True, "Loading user settings.")
    if is_reload:
        _profile = settings_manager.get_manager().get_setting('activeProfile')[1]
        settings_manager.get_manager().set_profile(_profile)

    if script is None:
        script = script_manager.get_manager().get_default_script()

    settings_manager.get_manager().load_app_settings(script)
    speech_manager = speech_and_verbosity_manager.get_manager()
    if speech_manager.get_speech_is_enabled():
        speech_manager.start_speech()
        if is_reload and not skip_reload_message:
            script.speak_message(messages.SETTINGS_RELOADED)

    if braille_presenter.get_presenter().get_braille_is_enabled():
        braille.init(input_event_manager.get_manager().process_braille_event)

    # TODO - JD: This ultimately belongs in an extension manager.
    mouse_reviewer = mouse_review.get_reviewer()
    if mouse_reviewer.get_is_enabled():
        mouse_reviewer.activate()

    if settings_manager.get_manager().get_setting('enableSound'):
        sound.get_player().init()

    # Handle the case where a change was made in the Orca Preferences dialog.
    orca_modifier_manager.get_manager().refresh_orca_modifiers("Loading user settings.")
    event_manager.get_manager().pause_queuing(False, False, "User settings loaded.")
    debug.print_message(debug.LEVEL_INFO, "ORCA: User Settings Loaded", True)

    manager = debugging_tools_manager.get_manager()
    manager.print_session_details()
    manager.print_running_applications(force=False)

def shutdown(script=None, _event=None, _signum=None):
    """Exits Orca. Returns True if shutdown ran to completion."""

    if hasattr(shutdown, "in_progress"):
        msg = "ORCA: Shutdown already in progress"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    systemd.get_manager().notify_stopping()

    shutdown.in_progress = True

    def _timeout(_signum=None, _frame=None):
        msg = "TIMEOUT: something has hung. Aborting."
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        debugging_tools_manager.get_manager().print_running_applications(force=True)
        os.kill(os.getpid(), signal.SIGKILL)

    debug.print_message(debug.LEVEL_INFO, "ORCA: Shutting down", True)
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(5)

    dbus_service.get_remote_controller().shutdown()

    orca_modifier_manager.get_manager().unset_orca_modifiers("Shutting down.")
    if script := script_manager.get_manager().get_active_script():
        if speech_and_verbosity_manager.get_manager().get_current_server():
            script.interrupt_presentation()
            script.present_message(messages.STOP_ORCA, reset_styles=False)

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
    speech_manager = speech_and_verbosity_manager.get_manager()
    if speech_manager.get_speech_is_enabled():
        speech_manager.shutdown_speech()

    if braille_presenter.get_presenter().get_braille_is_enabled():
        braille.shutdown()
    if settings.enableSound:
        player = sound.get_player()
        player.shutdown()

    signal.alarm(0)
    debug.print_message(debug.LEVEL_INFO, 'ORCA: Quitting Atspi main event loop', True)
    Atspi.event_quit()
    debug.print_message(debug.LEVEL_INFO, 'ORCA: Shutdown complete', True)
    return True

def main():
    """The main entry point for Orca."""

    def _reload_on_signal(signum, frame):
        signal_string = f'({signal.strsignal(signum)})'
        tokens = [f"ORCA: Reloading due to signal={signum} {signal_string}", frame]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        systemd.get_manager().notify_reloading()
        load_user_settings()
        systemd.get_manager().notify_ready()

    def _shutdown_on_signal(signum, frame):
        signal_string = f'({signal.strsignal(signum)})'
        tokens = [f"ORCA: Shutting down and exiting due to signal={signum} {signal_string}", frame]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        shutdown()

    def _show_preferences_on_signal(signum, frame):
        signal_string = f'({signal.strsignal(signum)})'
        tokens = [f"ORCA: Showing preferences due to signal={signum} {signal_string}", frame]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        manager = script_manager.get_manager()
        script = manager.get_active_script() or manager.get_default_script()
        if script:
            script.show_preferences_gui()

    signal.signal(signal.SIGHUP, _reload_on_signal)
    signal.signal(signal.SIGINT, _shutdown_on_signal)
    signal.signal(signal.SIGTERM, _shutdown_on_signal)
    signal.signal(signal.SIGQUIT, _shutdown_on_signal)
    signal.signal(signal.SIGUSR1, _show_preferences_on_signal)

    systemd.get_manager().start_watchdog()

    debug.print_message(debug.LEVEL_INFO, "ORCA: Enabling accessibility (if needed).", True)
    if not settings_manager.get_manager().is_accessibility_enabled():
        settings_manager.get_manager().set_accessibility(True)

    load_user_settings(is_reload=False)

    if not systemd.get_manager().is_systemd_managed():
        # Legacy behavior, here for backwards-compatibility. You really should
        # never rely on this. Run git blame and read the commit message!

        def _on_enabled_changed(gsetting, key):
            enabled = gsetting.get_boolean(key)
            msg = f"ORCA: {key} changed to {enabled}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if key == "screen-reader-enabled" and not enabled:
                shutdown()

        try:
            _a11y_applications_gsetting = Gio.Settings(
                schema_id="org.gnome.desktop.a11y.applications")
            connection = _a11y_applications_gsetting.connect("changed", _on_enabled_changed)
            msg = f"ORCA: Connected to a11y applications gsetting: {bool(connection)}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        except GLib.Error as error:
            msg = (
                f"ORCA: EXCEPTION connecting to a11y applications (schema may be missing): {error}"
            )
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
        except (AttributeError, TypeError) as error:
            msg = (
                "ORCA: EXCEPTION connecting to a11y applications (version incompatibility):"
                f"{error}"
            )
            debug.print_message(debug.LEVEL_SEVERE, msg, True)

    dbus_service.get_remote_controller().start()
    script = script_manager.get_manager().get_default_script()
    script.present_message(messages.START_ORCA)

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
    systemd.get_manager().notify_ready()

    try:
        debug.print_message(debug.LEVEL_INFO, "ORCA: Starting Atspi main event loop", True)
        Atspi.event_main()
    except GLib.Error as error:
        msg = f"ORCA: Exception starting ATSPI registry: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        os.kill(os.getpid(), signal.SIGKILL)
    return 0

if __name__ == "__main__":
    sys.exit(main())
