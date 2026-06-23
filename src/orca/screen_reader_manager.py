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

from typing import TYPE_CHECKING

from . import (
    guilabels,
    input_event,
    preferences_window,
    screen_reader_manager_command_definitions,
    script_manager,
)
from .extension import Extension

if TYPE_CHECKING:
    from .command import Command
    from .scripts import default


class ScreenReaderManager(Extension):
    """Manages screen reader commands that control Orca itself."""

    GROUP_LABEL = guilabels.KB_GROUP_SCREEN_READER_MANAGEMENT

    def _get_commands(self) -> list[Command]:
        return screen_reader_manager_command_definitions.get_commands(self)

    def quit(
        self,
        _script: default.Script | None = None,
        _event: input_event.InputEvent | None = None,
    ) -> bool:
        """Quits Orca in response to a command."""

        from . import orca  # pylint: disable=import-outside-toplevel

        return orca.shutdown()

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
