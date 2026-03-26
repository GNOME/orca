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

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import gi

if TYPE_CHECKING:
    from collections.abc import Callable

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug


class AXDeviceManager:
    """Provides shared access to the Atspi device."""

    def __init__(self) -> None:
        self._device: Atspi.Device | None = None
        self._key_pressed_id: int = 0
        self._key_released_id: int = 0
        self._pointer_moved_id: int = 0
        self._mapped_keycodes: list[int] = []
        self._mapped_keysyms: list[int] = []

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

    def start_key_watcher(
        self,
        on_pressed: Callable[..., Any],
        on_released: Callable[..., Any],
        legacy_callback: Callable[..., Any],
    ) -> None:
        """Connects key event handlers to the device."""

        msg = "AXDeviceManager: Starting key watcher."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self._device is None:
            msg = "AXDeviceManager: No device for key watcher."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        atspi_version = Atspi.get_version()  # pylint: disable=no-value-for-parameter
        if atspi_version[0] > 2 or atspi_version[1] >= 60:
            self._key_pressed_id = self._device.connect("key-pressed", on_pressed)
            self._key_released_id = self._device.connect("key-released", on_released)
        else:
            self._device.add_key_watcher(legacy_callback)

    def stop_key_watcher(self) -> None:
        """Disconnects key event handlers from the device."""

        msg = "AXDeviceManager: Stopping key watcher."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self._device is None:
            return

        atspi_version = Atspi.get_version()  # pylint: disable=no-value-for-parameter
        if atspi_version[0] > 2 or atspi_version[1] >= 60:
            self._device.disconnect(self._key_pressed_id)
            self._device.disconnect(self._key_released_id)
            self._key_pressed_id = 0
            self._key_released_id = 0

    def enable_pointer_monitoring(self) -> bool:
        """Enables pointer monitoring on the device. Returns True on success."""

        if self._device is None:
            return False

        try:
            caps = self._device.get_capabilities()
            caps = self._device.set_capabilities(
                caps | Atspi.DeviceCapability.POINTER_MONITOR,
            )
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in enable_pointer_monitoring: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return bool(caps & Atspi.DeviceCapability.POINTER_MONITOR)

    def start_pointer_watcher(self, on_pointer_moved: Callable[..., Any]) -> None:
        """Connects a pointer-moved signal handler to the device."""

        if self._device is None:
            return

        self._pointer_moved_id = self._device.connect(
            "pointer-moved",
            on_pointer_moved,
        )

    def stop_pointer_watcher(self) -> None:
        """Disconnects the pointer-moved signal handler from the device."""

        if self._device is None or self._pointer_moved_id == 0:
            return

        self._device.disconnect(self._pointer_moved_id)
        self._pointer_moved_id = 0

    def add_grab_for_modifier(self, modifier: str, keysym: int, keycode: int) -> int:
        """Adds a key grab for a modifier key, returns the grab ID."""

        kd = Atspi.KeyDefinition()
        kd.keysym = keysym
        kd.keycode = keycode
        kd.modifiers = 0
        grab_id = self.add_key_grab(kd)

        msg = f"AXDeviceManager: Grab id for {modifier}: {grab_id}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return grab_id

    def remove_grab_for_modifier(self, modifier: str, grab_id: int) -> None:
        """Removes a key grab for a modifier key."""

        self.remove_key_grab(grab_id)
        msg = f"AXDeviceManager: Grab id removed for {modifier}: {grab_id}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def add_key_grab(self, key_definition: Atspi.KeyDefinition, callback: object = None) -> int:
        """Adds a key grab, returns the grab ID or 0 on failure."""

        if self._device is None:
            return 0

        try:
            return self._device.add_key_grab(key_definition, callback)
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in add_key_grab: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

    def remove_key_grab(self, grab_id: int) -> None:
        """Removes a key grab."""

        if self._device is None:
            return

        try:
            self._device.remove_key_grab(grab_id)
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in remove_key_grab: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def grab_keyboard(self, reason: str = "") -> None:
        """Grabs the entire keyboard."""

        msg = "AXDeviceManager: Grabbing keyboard"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self._device is None:
            return

        try:
            self._device.grab_keyboard()
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in grab_keyboard: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def ungrab_keyboard(self, reason: str = "") -> None:
        """Releases the keyboard grab."""

        msg = "AXDeviceManager: Ungrabbing keyboard"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if self._device is None:
            return

        try:
            self._device.ungrab_keyboard()
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in ungrab_keyboard: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def map_keysym_to_modifier(self, keysym: int) -> int:
        """Maps keysym as a modifier, returns the mapped modifier or 0 on failure."""

        if self._device is None:
            return 0

        self._mapped_keysyms.append(keysym)
        try:
            return self._device.map_keysym_modifier(keysym)
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in map_keysym_modifier: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

    def _unmap_modifier(self, keycode: int) -> None:
        """Unmaps a single modifier keycode. Only called when device is active."""

        assert self._device is not None
        try:
            self._device.unmap_modifier(keycode)
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in unmap_modifier: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def _unmap_keysym_modifier(self, keysym: int) -> None:
        """Unmaps a single keysym modifier. Only called when device is active."""

        assert self._device is not None
        try:
            self._device.unmap_keysym_modifier(keysym)
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in unmap_keysym_modifier: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def unmap_all_modifiers(self) -> None:
        """Unmaps all previously mapped modifiers."""

        if self._device is not None:
            for keycode in self._mapped_keycodes:
                self._unmap_modifier(keycode)
            for keysym in self._mapped_keysyms:
                self._unmap_keysym_modifier(keysym)

        self._mapped_keycodes.clear()
        self._mapped_keysyms.clear()

    def generate_mouse_event(self, obj: Atspi.Accessible, x: int, y: int, event: str) -> bool:
        """Generates a mouse event at the given coordinates on obj."""

        if self._device is None:
            return False

        try:
            self._device.generate_mouse_event(obj, x, y, event)
        except GLib.GError as error:
            msg = f"AXDeviceManager: Exception in generate_mouse_event: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        return True

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
