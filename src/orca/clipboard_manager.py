# Orca
#
# Copyright 2024-2025 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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


"""Sets and gets the clipboard contents via the desktop's clipboard manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import gi
from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from . import debug

if TYPE_CHECKING:
    from collections.abc import Callable

    from dasbus.client.proxy import InterfaceProxy


class _ClipboardManagerBase:
    """Base class for interacting with clipboard managers."""

    def __init__(self, name: str, change_callback: Callable[[str], None]) -> None:
        self._name: str = name
        self._change_callback: Callable[[str], None] = change_callback
        self._contents: str = ""
        self._is_active: bool = False

    def is_active(self) -> bool:
        """Returns True if this manager is active."""

        return self._is_active

    def connect(self) -> None:
        """Connects to the clipboard manager."""

    def disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

    def get_contents(self) -> str:
        """Returns the pre-stored contents of the clipboard."""

        if not self._contents:
            self._contents = self._get_contents()
        return self._contents

    def _get_contents(self) -> str:
        """Obtains and returns the contents of the clipboard."""

        return ""

    def _on_contents_changed(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """Notifies the registered callback that the contents changed."""

        tokens = [self._name, ": Contents changed.", args, kwargs]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._contents = self._get_contents()
        self._change_callback(self._contents)


class _ClipboardManagerFallback(_ClipboardManagerBase):
    """Class for interacting with the clipboard via Gtk.Clipboard."""

    def __init__(self, change_callback: Callable[[str], None]) -> None:
        super().__init__("FALLBACK", change_callback)
        self._handler_id: int | None = None

    def connect(self) -> None:
        """Connects to the clipboard manager."""

        if self._handler_id is not None:
            return

        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        self._handler_id = clipboard.connect("owner-change", self._on_contents_changed)
        self._is_active = True

    def disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

        self._is_active = False
        if self._handler_id is None:
            return

        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        clipboard.disconnect(self._handler_id)
        self._handler_id = None

    def _get_contents(self) -> str:
        """Obtains and returns the contents of the clipboard."""

        if self._handler_id is None:
            return ""

        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        result = clipboard.wait_for_text()
        if result is None:
            msg = "FALLBACK: Have handler, but text is None"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        debug_string = result.replace("\n", "\\n")
        tokens = ["FALLBACK: Clipboard contents:", debug_string]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        tokens = ["FALLBACK: Setting clipboard contents to:", text]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        clipboard.set_text(text, -1)


class _ClipboardManagerGPaste(_ClipboardManagerBase):
    """Class for interacting with the clipboard via GPaste."""

    _DBUS_TIMEOUT_MS = 1000
    _DBUS_INTERFACE = ""

    def __init__(self, change_callback: Callable[[str], None]) -> None:
        super().__init__("GPASTE", change_callback)
        self._bus: SessionMessageBus | None = None
        self._gpaste_proxy: InterfaceProxy | None = None
        self._props_proxy: InterfaceProxy | None = None
        self._signal_subscription: Any | None = None
        self._original_active_state: bool | None = None

    def _set_active(self, active: bool) -> None:
        """Enables or disables clipboard tracking."""

        raise NotImplementedError

    def connect(self) -> None:
        """Connects to the clipboard manager."""

        try:
            self._bus = SessionMessageBus()
            self._gpaste_proxy = self._bus.get_proxy("org.gnome.GPaste", "/org/gnome/GPaste")

            # Test if the service is actually available by checking properties
            self._props_proxy = self._bus.get_proxy(
                "org.gnome.GPaste",
                "/org/gnome/GPaste",
                "org.freedesktop.DBus.Properties",
            )
            self._original_active_state = self._props_proxy.Get(
                self._DBUS_INTERFACE,
                "Active",
                timeout=self._DBUS_TIMEOUT_MS,
            )
        except (DBusError, TimeoutError) as error:
            tokens = ["CLIPBOARD MANAGER: Could not access GPaste interface:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._gpaste_proxy = None
            self._props_proxy = None
            self._bus = None
            return

        try:
            if not self._original_active_state:
                msg = "CLIPBOARD MANAGER: GPaste is not active. Enabling Tracking."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self._set_active(True)
                new_state = self._props_proxy.Get(
                    self._DBUS_INTERFACE,
                    "Active",
                    timeout=self._DBUS_TIMEOUT_MS,
                )
                tokens = ["CLIPBOARD MANAGER: Is active now:", bool(new_state)]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            self._signal_subscription = self._gpaste_proxy.Update.connect(self._on_contents_changed)
            self._is_active = True
        except (DBusError, TimeoutError) as error:
            tokens = ["CLIPBOARD MANAGER: Could not connect to GPaste signals:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._gpaste_proxy = None
            self._props_proxy = None
            self._bus = None

    def disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

        if self._gpaste_proxy is None or self._props_proxy is None:
            msg = "CLIPBOARD MANAGER: Cannot disconnect due to missing interface(s)."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self._signal_subscription is not None:
            self._signal_subscription.disconnect()
            self._signal_subscription = None

        if not self._original_active_state:
            msg = "CLIPBOARD MANAGER: Restoring inactive state by disabling tracking."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            try:
                self._set_active(False)
                new_state = self._props_proxy.Get(
                    self._DBUS_INTERFACE,
                    "Active",
                    timeout=self._DBUS_TIMEOUT_MS,
                )
                tokens = ["CLIPBOARD MANAGER: Is active now:", bool(new_state)]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            except (DBusError, TimeoutError) as error:
                tokens = ["CLIPBOARD MANAGER: Could not restore GPaste state:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._gpaste_proxy = None
        self._props_proxy = None
        self._bus = None
        self._is_active = False


class _ClipboardManagerGPaste2(_ClipboardManagerGPaste):
    """Class for interacting with the clipboard via GPaste2."""

    _DBUS_INTERFACE = "org.gnome.GPaste2"

    def _set_active(self, active: bool) -> None:
        assert self._gpaste_proxy is not None
        self._gpaste_proxy.Track(active, timeout=self._DBUS_TIMEOUT_MS)

    def _get_contents(self) -> str:
        """Obtains and returns the contents of the clipboard."""

        if self._gpaste_proxy is None:
            return ""

        try:
            result = self._gpaste_proxy.GetElementAtIndex(0, timeout=self._DBUS_TIMEOUT_MS)[1]
        except (DBusError, TimeoutError) as error:
            tokens = ["GPASTE2: Could not get clipboard contents:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        debug_string = result.replace("\n", "\\n")
        tokens = ["GPASTE2: Clipboard contents:", debug_string]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        if self._gpaste_proxy is None:
            return

        try:
            self._gpaste_proxy.Add(text, timeout=self._DBUS_TIMEOUT_MS)
        except (DBusError, TimeoutError) as error:
            tokens = ["GPASTE2: Could not set clipboard contents:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)


class _ClipboardManagerGPaste3(_ClipboardManagerGPaste):
    """Class for interacting with the clipboard via GPaste3."""

    _DBUS_INTERFACE = "org.gnome.GPaste3"

    def _set_active(self, active: bool) -> None:
        assert self._gpaste_proxy is not None
        self._gpaste_proxy.SetActive(active, timeout=self._DBUS_TIMEOUT_MS)

    def _get_contents(self) -> str:
        """Obtains and returns the contents of the clipboard."""

        if self._gpaste_proxy is None:
            return ""

        try:
            result = self._gpaste_proxy.GetItemAtIndex(0, timeout=self._DBUS_TIMEOUT_MS)[1]
        except (DBusError, TimeoutError) as error:
            tokens = ["GPASTE3: Could not get clipboard contents:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        debug_string = result.replace("\n", "\\n")
        tokens = ["GPASTE3: Clipboard contents:", debug_string]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        if self._gpaste_proxy is None:
            return

        try:
            self._gpaste_proxy.AddText(text, timeout=self._DBUS_TIMEOUT_MS)
        except (DBusError, TimeoutError) as error:
            tokens = ["GPASTE3: Could not set clipboard contents:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)


class _ClipboardManagerKlipper(_ClipboardManagerBase):
    """Class for interacting with the clipboard via Klipper ."""

    def __init__(self, change_callback: Callable[[str], None]) -> None:
        super().__init__("KLIPPER", change_callback)
        self._bus: SessionMessageBus | None = None
        self._klipper_proxy: InterfaceProxy | None = None
        self._signal_subscription: Any | None = None

    def connect(self) -> None:
        """Connects to the clipboard manager."""

        try:
            self._bus = SessionMessageBus()
            self._klipper_proxy = self._bus.get_proxy("org.kde.klipper", "/klipper")

            # Test if the service is actually available by calling a simple method
            self._klipper_proxy.getClipboardContents()
        except DBusError as error:
            tokens = ["CLIPBOARD MANAGER: Could not access klipper interface:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return

        try:
            self._signal_subscription = self._klipper_proxy.clipboardHistoryUpdated.connect(
                self._on_contents_changed,
            )
            self._is_active = True
        except DBusError as error:
            tokens = ["CLIPBOARD MANAGER: Could not connect to klipper signal:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._klipper_proxy = None
            self._bus = None

    def disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

        if self._signal_subscription is not None:
            self._signal_subscription.disconnect()
        self._signal_subscription = None
        self._klipper_proxy = None
        self._bus = None
        self._is_active = False

    def _get_contents(self) -> str:
        """Obtains and returns the contents of the clipboard."""

        if self._klipper_proxy is None:
            return ""

        result = self._klipper_proxy.getClipboardContents()
        debug_string = result.replace("\n", "\\n")
        tokens = ["KLIPPER: Clipboard contents:", debug_string]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        if self._klipper_proxy is None:
            return

        tokens = ["KLIPPER: Setting clipboard contents to:", text]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._klipper_proxy.setClipboardContents(text)


class ClipboardManager:
    """Sets and gets the clipboard contents via the desktop's clipboard manager."""

    def __init__(self) -> None:
        self._manager: _ClipboardManagerBase | None = None

    def connect(self, change_callback: Callable[[str], None]) -> None:
        """Connects to the clipboard manager, calling change_callback when the contents change."""

        if self._manager is not None:
            return

        manager: _ClipboardManagerBase | None = None

        # If you try to connect to Klipper from a GNOME session, it will fail with a DBus
        # exception. However, if you try to connect to GPaste from a KDE session, it will
        # succeed -- or at least not throw an exception. Therefore, check for Klipper first.
        manager = _ClipboardManagerKlipper(change_callback)
        manager.connect()
        if manager.is_active():
            self._manager = manager
            msg = "CLIPBOARD MANAGER: Using Klipper."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        # See comment above. Check for GPaste last.
        manager = _ClipboardManagerGPaste3(change_callback)
        manager.connect()
        if manager.is_active():
            self._manager = manager
            msg = "CLIPBOARD MANAGER: Using GPaste3."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        manager = _ClipboardManagerGPaste2(change_callback)
        manager.connect()
        if manager.is_active():
            self._manager = manager
            msg = "CLIPBOARD MANAGER: Using GPaste2."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._manager = _ClipboardManagerFallback(change_callback)
        self._manager.connect()
        msg = "CLIPBOARD MANAGER: Using Gtk.Clipboard as fallback."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

        if self._manager is None:
            return
        self._manager.disconnect()

    def is_ready(self) -> bool:
        """Returns True if connect() has found a clipboard manager."""

        return self._manager is not None

    def get_text(self) -> str:
        """Returns the clipboard contents."""

        if self._manager is None:
            msg = "CLIPBOARD MANAGER: Cannot get contents, no active manager"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        result = self._manager.get_contents()
        debug_string = result.replace("\n", "\\n")
        tokens = ["CLIPBOARD MANAGER: Current contents:", debug_string]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def append_text(self, text: str, separator: str = "\n") -> None:
        """Appends text to the clipboard contents."""

        if self._manager is None:
            msg = "CLIPBOARD MANAGER: Cannot append text, no active manager."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        old_text = self._manager.get_contents()
        new_text = f"{old_text}{separator}{text}"
        tokens = ["CLIPBOARD MANAGER: Appending '", text, "'. New contents: '", new_text, "'."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._manager.set_contents(new_text)

    def set_text(self, text: str) -> None:
        """Sets the clipboard contents to text."""

        if self._manager is None:
            msg = "CLIPBOARD MANAGER: Cannot set text, no active manager."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        tokens = ["CLIPBOARD MANAGER: Setting text to '", text, "'."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._manager.set_contents(text)


_manager: ClipboardManager = ClipboardManager()


def get_manager() -> ClipboardManager:
    """Returns the Clipboard Manager singleton."""

    return _manager
