# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Manager for screen reader management commands."""

from __future__ import annotations

import os
import signal
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import (
    ax_device_manager,
    clipboard_presenter,
    dbus_service,
    debug,
    event_manager,
    extension_loader,
    guilabels,
    input_event,
    messages,
    mouse_presenter,
    orca_modifier_manager,
    preferences_window,
    presentation_manager,
    screen_reader_manager_command_definitions,
    script_manager,
    systemd,
)
from .extension import Extension

if TYPE_CHECKING:
    from .command import Command
    from .scripts import default


class ScreenReaderManager(Extension):
    """Manages screen reader commands that control Orca itself."""

    GROUP_LABEL = guilabels.KB_GROUP_SCREEN_READER_MANAGEMENT

    def __init__(self) -> None:
        self._is_shutting_down: bool = False
        super().__init__()

    def _get_commands(self) -> list[Command]:
        return screen_reader_manager_command_definitions.get_commands(self)

    def quit(
        self,
        _script: default.Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Quits Orca in response to a command."""

        return self.shutdown()

    def shutdown(self) -> bool:
        """Exits Orca. Returns True if shutdown ran to completion."""

        if self._is_shutting_down:
            msg = "SCREEN READER MANAGER: Shutdown already in progress"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self._is_shutting_down = True

        def _timeout(_signum=None, _frame=None):
            msg = "TIMEOUT: something has hung. Aborting."
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
            os.kill(os.getpid(), signal.SIGKILL)

        debug.print_message(debug.LEVEL_INFO, "SCREEN READER MANAGER: Shutting down", True)
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
        clipboard_presenter.get_presenter().deactivate()
        mouse_presenter.get_presenter().deactivate()

        presentation_manager.get_manager().shutdown_presenters()

        preferences_window.close_preferences_gui_for_shutdown()

        ax_device_manager.get_manager().deactivate()
        systemd.get_manager().notify_stopping()
        signal.alarm(0)
        debug.print_message(
            debug.LEVEL_INFO, "SCREEN READER MANAGER: Quitting Atspi main event loop", True
        )
        Atspi.event_quit()  # pylint: disable=no-value-for-parameter
        debug.print_message(debug.LEVEL_INFO, "SCREEN READER MANAGER: Shutdown complete", True)
        debug.shutdown()
        return True

    def show_app_preferences_gui(
        self,
        current_script: default.Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Shows the app Preferences window."""

        current_script = current_script or script_manager.get_manager().get_active_script()
        current_script = current_script or script_manager.get_manager().get_default_script()
        if current_script is None:
            return False

        return preferences_window.show_app_preferences_gui(current_script)

    def show_preferences_gui(
        self,
        _script: default.Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Displays the Preferences window."""

        default_script = script_manager.get_manager().get_default_script()
        if default_script is None:
            return False

        script_manager.get_manager().set_active_script(default_script, "Global preferences")
        return preferences_window.show_preferences_gui(default_script)


_manager = ScreenReaderManager()


def get_manager() -> ScreenReaderManager:
    """Returns the Screen Reader Manager singleton."""

    return _manager
