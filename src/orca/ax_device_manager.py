# Orca
#
# Copyright 2026 SUSE LLC.
# Author: Mike Gorse <mgorse@suse.com>
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

"""Handle activating and providing access to the AT-SPI device."""

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug


class AXDeviceManager:
    """Provides shared access to the Atspi device."""

    def __init__(self) -> None:
        self._device: Atspi.Device | None = None

    def activate(self) -> None:
        """Called when this device manager is activated."""

        if self._device is None:
            self._device = Atspi.Device.new_full("org.gnome.Orca")

    def deactivate(self) -> None:
        """Called when this device manager is deactivated."""

        self._device = None

    def is_active(self) -> bool:
        """Returns True if we have an active device."""

        return self._device is not None

    def get_device(self) -> Atspi.Device:
        """Returns the AT-SPI device."""

        return self._device

    def get_locked_modifiers(self) -> int:
        """Returns a bitmask of locked modifiers, or 0 if unavailable."""

        # Requires at-spi2-core >= 2.59.0. Earlier versions always return 0.

        if self._device is None:
            msg = "AXDeviceManager: get_locked_modifiers called with no device"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        try:
            result = self._device.get_locked_modifiers()
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in get_locked_modifiers: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        msg = f"AXDeviceManager: get_locked_modifiers returned {result} ({result:#x})"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result


_manager: AXDeviceManager = AXDeviceManager()


def get_manager() -> AXDeviceManager:
    """Returns the device manager singleton."""

    return _manager
