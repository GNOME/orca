# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Bridge between the D-Bus remote controller and the rest of Orca."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import (
    focus_manager,
    input_event,
    input_event_manager,
    orca,
    presentation_manager,
    screen_reader_manager,
    script_manager,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class RemoteControllerBridge:
    """Handles requests from the D-Bus remote controller."""

    def run_command(
        self, method: Callable[..., Any], arguments: dict[str, Any], is_testing: bool
    ) -> Any:
        """Runs method with the active script and a remote controller event."""

        event: input_event.RemoteControllerEvent
        if is_testing:
            event = input_event.RemoteControllerTestingEvent()
        else:
            event = input_event.RemoteControllerEvent()
        manager = script_manager.get_manager()
        script = manager.get_active_script() or manager.get_default_script()
        result = method(script=script, event=event, **arguments)
        input_event_manager.get_manager().process_remote_controller_event(event)
        return result

    def show_preferences(self) -> bool:
        """Shows the preferences for the active script. Returns False if there is no script."""

        manager = script_manager.get_manager()
        script = manager.get_active_script() or manager.get_default_script()
        if script is None:
            return False

        screen_reader_manager.get_manager().show_preferences_gui(script)
        return True

    def present_message(self, message: str) -> None:
        """Presents message in speech and braille."""

        presentation_manager.get_manager().present_message(message)

    def speak_message(self, message: str) -> None:
        """Speaks message."""

        presentation_manager.get_manager().speak_message(message)

    def display_message(self, message: str, persistent: bool) -> None:
        """Displays message in braille."""

        presentation_manager.get_manager().display_message(message, persistent=persistent)

    def play_sound_file(self, path: str, interrupt: bool, volume: float) -> bool:
        """Plays the sound file at path."""

        return presentation_manager.get_manager().play_sound_file(
            path,
            interrupt=interrupt,
            volume=volume,
        )

    def play_tone(
        self, duration: float, frequency: int, volume: float, wave: str, interrupt: bool
    ) -> bool:
        """Plays a tone."""

        return presentation_manager.get_manager().play_tone(
            duration,
            frequency,
            volume=volume,
            wave=wave,
            interrupt=interrupt,
        )

    def get_active_window(self) -> Atspi.Accessible | None:
        """Returns the active window."""

        return focus_manager.get_manager().get_active_window()

    def get_current_object(self) -> Atspi.Accessible | None:
        """Returns the current object."""

        return focus_manager.get_manager().get_locus_of_focus()

    def quit(self) -> None:
        """Quits Orca."""

        orca.shutdown()


_bridge: RemoteControllerBridge = RemoteControllerBridge()


def get_bridge() -> RemoteControllerBridge:
    """Returns the Remote Controller Bridge singleton."""

    return _bridge
