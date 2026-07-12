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
    extension_loader,
    focus_manager,
    messages,
    mouse_presenter,
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
        mouse_presenter.get_presenter().deactivate()

    event_manager.get_manager().pause_queuing(True, True, "Loading user settings.")

    if script is None:
        script = script_manager.get_manager().get_default_script()

    command_manager.get_manager().load_keyboard_layout()

    presentation_manager.get_manager().start_presenters()
    if is_reload and not skip_reload_message:
        presentation_manager.get_manager().speak_message(messages.SETTINGS_RELOADED)

    # TODO - JD: This ultimately belongs in an extension manager.
    presenter = mouse_presenter.get_presenter()
    if presenter.get_is_enabled():
        presenter.activate()

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
        os.kill(os.getpid(), signal.SIGKILL)

    debug.print_message(debug.LEVEL_INFO, "ORCA: Shutting down", True)
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(5)

    manager = presentation_manager.get_manager()
    manager.interrupt_presentation()
    manager.present_message(messages.STOP_ORCA)

    extension_loader.get_loader().shutdown_user_extensions()
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
    mouse_presenter.get_presenter().deactivate()

    presentation_manager.get_manager().shutdown_presenters()

    # pylint: disable-next=import-outside-toplevel
    from . import preferences_window

    preferences_window.close_preferences_gui_for_shutdown()

    ax_device_manager.get_manager().deactivate()
    systemd.get_manager().notify_stopping()
    signal.alarm(0)
    debug.print_message(debug.LEVEL_INFO, "ORCA: Quitting Atspi main event loop", True)
    Atspi.event_quit()  # pylint: disable=no-value-for-parameter
    debug.print_message(debug.LEVEL_INFO, "ORCA: Shutdown complete", True)
    debug.shutdown()
    return True


def _setup_signal_handlers():
    """Sets up signal handlers for reload, shutdown, and preferences."""

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
        return GLib.SOURCE_CONTINUE

    def _glib_show_preferences_handler():
        msg = "ORCA: GLib handler received show-preferences signal"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        from . import screen_reader_manager  # pylint: disable=import-outside-toplevel

        screen_reader_manager.get_manager().show_preferences_gui()
        return GLib.SOURCE_CONTINUE

    for signum, handler in (
        (signal.SIGINT, _glib_shutdown_handler),
        (signal.SIGTERM, _glib_shutdown_handler),
        (signal.SIGHUP, _glib_reload_handler),
        (signal.SIGUSR1, _glib_show_preferences_handler),
    ):
        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signum, handler)

    # We have historically shut down gracefully on SIGQUIT and want to continue doing so.
    # But GLib.unix_signal_add only supports SIGHUP/SIGINT/SIGTERM/SIGUSR1/SIGUSR2/SIGWINCH,
    # so SIGQUIT uses a raw handler that defers the shutdown to the main loop.
    def _quit_on_signal(_signum, _frame):
        GLib.idle_add(_glib_shutdown_handler, priority=GLib.PRIORITY_HIGH)

    signal.signal(signal.SIGQUIT, _quit_on_signal)


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


def main():
    """The main entry point for Orca."""

    _setup_signal_handlers()
    systemd.get_manager().start_watchdog()

    error = _ensure_accessibility_enabled()
    if error is not None:
        return error

    ax_device_manager.get_manager().activate()
    load_user_settings(is_reload=False)

    is_systemd_managed = systemd.get_manager().is_systemd_managed()
    msg = f"ORCA: Running under systemd: {is_systemd_managed}"
    debug.print_message(debug.LEVEL_INFO, msg, True)

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
