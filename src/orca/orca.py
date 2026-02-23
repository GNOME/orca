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

# pylint: disable=too-many-locals

"""The main module for the Orca screen reader."""

import os
import signal
import sys

import gi
from dasbus.connection import SessionMessageBus

gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
from gi.repository import (
    Atspi,
    Gdk,  # pylint: disable=no-name-in-module
    Gio,
    GLib,
)

from . import (
    ax_device_manager,
    clipboard,
    command_manager,
    dbus_service,
    debug,
    debugging_tools_manager,
    event_manager,
    focus_manager,
    gsettings_registry,
    messages,
    mouse_review,
    orca_modifier_manager,
    presentation_manager,
    script_manager,
    systemd,
)
from .ax_utilities import AXUtilities


def load_user_settings(script=None, skip_reload_message=False, is_reload=True):
    """(Re)Loads the user settings module, re-initializing things such as speech if necessary."""

    debug.print_message(debug.LEVEL_INFO, "ORCA: Loading User Settings", True)

    if is_reload:
        presentation_manager.get_manager().shutdown_presenters()
        mouse_review.get_reviewer().deactivate()

    event_manager.get_manager().pause_queuing(True, True, "Loading user settings.")

    if script is None:
        script = script_manager.get_manager().get_default_script()

    command_manager.get_manager().set_keyboard_layout()

    presentation_manager.get_manager().start_presenters()
    if is_reload and not skip_reload_message:
        presentation_manager.get_manager().speak_message(messages.SETTINGS_RELOADED)

    # TODO - JD: This ultimately belongs in an extension manager.
    mouse_reviewer = mouse_review.get_reviewer()
    if mouse_reviewer.get_is_enabled():
        mouse_reviewer.activate()

    # Handle the case where a change was made in the Orca Preferences dialog.
    orca_modifier_manager.get_manager().refresh_orca_modifiers("Loading user settings.")
    event_manager.get_manager().pause_queuing(False, False, "User settings loaded.")
    debug.print_message(debug.LEVEL_INFO, "ORCA: User Settings Loaded", True)

    manager = debugging_tools_manager.get_manager()
    manager.print_session_details()
    manager.print_running_applications(force=False)


def shutdown(_event=None, _signum=None):
    """Exits Orca. Returns True if shutdown ran to completion."""

    if hasattr(shutdown, "in_progress"):
        msg = "ORCA: Shutdown already in progress"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    shutdown.in_progress = True

    def _timeout(_signum=None, _frame=None):
        msg = "TIMEOUT: something has hung. Aborting."
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        debugging_tools_manager.get_manager().print_running_applications(force=True)
        os.kill(os.getpid(), signal.SIGKILL)

    debug.print_message(debug.LEVEL_INFO, "ORCA: Shutting down", True)
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(5)

    manager = presentation_manager.get_manager()
    manager.interrupt_presentation()
    manager.present_message(messages.STOP_ORCA, reset_styles=False)

    dbus_service.get_remote_controller().shutdown()
    orca_modifier_manager.get_manager().unset_orca_modifiers("Shutting down.")

    # Pause event queuing first so that it clears its queue and will not accept new
    # events. Then let the script manager unregister script event listeners as well
    # as key grabs. Finally deactivate the event manager and the device
    # manager, which will cause the Atspi.Device to be set to None.
    event_manager.get_manager().pause_queuing(True, True, "Shutting down.")
    script_manager.get_manager().deactivate()
    event_manager.get_manager().deactivate()

    # TODO - JD: This ultimately belongs in an extension manager.
    clipboard.get_presenter().deactivate()
    mouse_review.get_reviewer().deactivate()

    presentation_manager.get_manager().shutdown_presenters()

    ax_device_manager.get_manager().deactivate()
    systemd.get_manager().notify_stopping()
    signal.alarm(0)
    debug.print_message(debug.LEVEL_INFO, "ORCA: Quitting Atspi main event loop", True)
    Atspi.event_quit()  # pylint: disable=no-value-for-parameter
    debug.print_message(debug.LEVEL_INFO, "ORCA: Shutdown complete", True)
    return True


def _setup_signal_handlers():
    """Sets up signal handlers for reload, shutdown, and preferences."""

    def _reload_on_signal(signum, frame):
        signal_string = f"({signal.strsignal(signum)})"
        tokens = [f"ORCA: Reloading due to signal={signum} {signal_string}", frame]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        systemd.get_manager().notify_reloading()
        load_user_settings()
        systemd.get_manager().notify_ready()

    def _shutdown_on_signal(signum, frame):
        signal_string = f"({signal.strsignal(signum)})"
        tokens = [f"ORCA: Shutting down and exiting due to signal={signum} {signal_string}", frame]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        shutdown()

    def _show_preferences_on_signal(signum, frame):
        signal_string = f"({signal.strsignal(signum)})"
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

    def _glib_shutdown_handler():
        msg = "ORCA: GLib handler received shutdown signal"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        shutdown()
        return GLib.SOURCE_REMOVE

    def _glib_reload_handler():
        msg = "ORCA: GLib handler received reload signal"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        systemd.get_manager().notify_reloading()
        load_user_settings()
        systemd.get_manager().notify_ready()
        return GLib.SOURCE_REMOVE

    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, _glib_shutdown_handler)
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGINT, _glib_shutdown_handler)
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGHUP, _glib_reload_handler)


def _ensure_accessibility_enabled() -> int | None:
    """Ensures the accessibility bus is enabled. Returns error code or None on success."""

    try:
        bus = SessionMessageBus()
        proxy = bus.get_proxy("org.a11y.Bus", "/org/a11y/bus", "org.freedesktop.DBus.Properties")
        enabled = proxy.Get("org.a11y.Status", "IsEnabled")
        msg = f"ORCA: Accessibility enabled: {enabled}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if not enabled:
            msg = "ORCA: Enabling accessibility."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            proxy.Set("org.a11y.Status", "IsEnabled", GLib.Variant("b", True))
    except GLib.GError as error:
        msg = f"ORCA: Could not connect to D-Bus session bus: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        print(msg, file=sys.stderr)  # noqa: T201
        return 1
    return None


def _setup_legacy_gsettings_monitoring() -> Gio.Settings | None:
    """Sets up legacy GSettings monitoring for non-systemd environments."""

    def _on_enabled_changed(gsetting, key):
        enabled = gsetting.get_boolean(key)
        msg = f"ORCA: {key} changed to {enabled}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if key == "screen-reader-enabled" and not enabled:
            shutdown()

    try:
        gsetting = Gio.Settings(schema_id="org.gnome.desktop.a11y.applications")
        connection = gsetting.connect("changed", _on_enabled_changed)
        msg = f"ORCA: Connected to a11y applications gsetting: {bool(connection)}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return gsetting
    except GLib.Error as error:
        msg = f"ORCA: EXCEPTION connecting to a11y applications (schema may be missing): {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
    except (AttributeError, TypeError) as error:
        msg = f"ORCA: EXCEPTION connecting to a11y applications (version incompatibility):{error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
    return None


def _activate_services():
    """Activates Orca services and attempts to find the focused object."""

    ax_device_manager.get_manager().activate()
    event_manager.get_manager().activate()
    script_manager.get_manager().activate()
    window = AXUtilities.find_active_window()
    if window and not focus_manager.get_manager().get_locus_of_focus():
        app = AXUtilities.get_application(window)
        focus_manager.get_manager().set_active_window(
            window,
            app,
            set_window_as_focus=True,
            notify_script=True,
        )

        focused_object = focus_manager.get_manager().find_focused_object()
        if focused_object:
            focus_manager.get_manager().set_locus_of_focus(None, focused_object)

        script = script_manager.get_manager().get_script(app, focused_object or window)
        script_manager.get_manager().set_active_script(script, "Launching.")

    clipboard.get_presenter().activate()
    Gdk.notify_startup_complete()  # pylint: disable=no-value-for-parameter
    systemd.get_manager().notify_ready()


def main(import_dir: str | None = None, prefs_dir: str = ""):
    """The main entry point for Orca."""

    _setup_signal_handlers()
    systemd.get_manager().start_watchdog()

    error = _ensure_accessibility_enabled()
    if error is not None:
        return error

    # TODO - JD: Delete -i/--import-dir support in v52.
    registry = gsettings_registry.get_registry()
    if import_dir:
        registry.import_from_dir(import_dir)
    else:
        registry.migrate_all(prefs_dir)  # TODO - JD: Delete this in v51.

    load_user_settings(is_reload=False)

    is_systemd_managed = systemd.get_manager().is_systemd_managed()
    msg = f"ORCA: Running under systemd: {is_systemd_managed}"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    # Keep a reference to prevent garbage collection of the GSettings connection.
    _gsettings_ref = None
    if not is_systemd_managed:
        _gsettings_ref = _setup_legacy_gsettings_monitoring()

    dbus_service.get_remote_controller().start()
    presentation_manager.get_manager().present_message(messages.START_ORCA)
    _activate_services()

    try:
        debug.print_message(debug.LEVEL_INFO, "ORCA: Starting Atspi main event loop", True)
        Atspi.event_main()  # pylint: disable=no-value-for-parameter
    except GLib.Error as error:
        msg = f"ORCA: Exception starting ATSPI registry: {error}"
        debug.print_message(debug.LEVEL_SEVERE, msg, True)
        os.kill(os.getpid(), signal.SIGKILL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
