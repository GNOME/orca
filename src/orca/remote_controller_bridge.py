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

from . import input_event, input_event_manager, script_manager

if TYPE_CHECKING:
    from collections.abc import Callable


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


_bridge: RemoteControllerBridge = RemoteControllerBridge()


def get_bridge() -> RemoteControllerBridge:
    """Returns the Remote Controller Bridge singleton."""

    return _bridge
