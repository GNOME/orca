# Utilities related to the clipboard
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

# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=too-many-return-statements

"""Utilities related to the clipboard."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024-2025 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import re
import time
from typing import Any, Callable, TYPE_CHECKING

from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError
from dasbus.client.proxy import InterfaceProxy

import gi
gi.require_version("Atspi", "2.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atspi, Gdk, Gtk

from . import cmdnames
from . import dbus_service
from . import debug
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import script_manager
from . import settings_manager
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from .scripts import default

class _ClipboardManager:
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

        msg = f"{self._name}: Contents changed. {args} {kwargs}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._contents = self._get_contents()
        self._change_callback(self._contents)

class _ClipboardManagerFallback(_ClipboardManager):
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
        msg = f"FALLBACK: Clipboard contents: {debug_string}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        msg = f"FALLBACK: Setting clipboard contents to: {text}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
        clipboard.set_text(text, -1)

class _ClipboardManagerGPaste(_ClipboardManager):
    """Class for interacting with the clipboard via GPaste."""

    def __init__(self, change_callback: Callable[[str], None]) -> None:
        super().__init__("GPASTE", change_callback)
        self._bus: SessionMessageBus | None = None
        self._gpaste_proxy: InterfaceProxy | None = None
        self._props_proxy: InterfaceProxy | None = None
        self._signal_subscription: Any | None = None
        self._original_active_state: bool | None = None

    def connect(self) -> None:
        """Connects to the clipboard manager."""

        try:
            self._bus = SessionMessageBus()
            self._gpaste_proxy = self._bus.get_proxy("org.gnome.GPaste", "/org/gnome/GPaste")

            # Test if the service is actually available by checking properties
            self._props_proxy = self._bus.get_proxy(
                "org.gnome.GPaste", "/org/gnome/GPaste", "org.freedesktop.DBus.Properties"
            )
            self._original_active_state = self._props_proxy.Get("org.gnome.GPaste2", "Active")
        except DBusError as error:
            msg = f"CLIPBOARD PRESENTER: Could not access GPaste interface: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        try:
            self._original_active_state = self._props_proxy.Get("org.gnome.GPaste2", "Active")
            if not self._original_active_state:
                msg = "CLIPBOARD PRESENTER: GPaste is not active. Enabling Tracking."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self._gpaste_proxy.Track(True)
                new_state = self._props_proxy.Get("org.gnome.GPaste2", "Active")
                msg = f"CLIPBOARD PRESENTER: Is active now: {bool(new_state)}"
                debug.print_message(debug.LEVEL_INFO, msg, True)

            self._signal_subscription = self._gpaste_proxy.Update.connect(self._on_contents_changed)
            self._is_active = True
        except DBusError as error:
            msg = f"CLIPBOARD PRESENTER: Could not connect to GPaste signals: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._gpaste_proxy = None
            self._props_proxy = None
            self._bus = None

    def disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

        if self._gpaste_proxy is None or self._props_proxy is None:
            msg = "CLIPBOARD PRESENTER: Cannot disconnect due to missing interface(s)."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self._signal_subscription is not None:
            self._signal_subscription.disconnect()
            self._signal_subscription = None

        if not self._original_active_state:
            msg = "CLIPBOARD PRESENTER: Restoring inactive state by disabling tracking."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._gpaste_proxy.Track(False)
            new_state = self._props_proxy.Get("org.gnome.GPaste2", "Active")
            msg = f"CLIPBOARD PRESENTER: Is active now: {bool(new_state)}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        self._gpaste_proxy = None
        self._props_proxy = None
        self._bus = None
        self._is_active = False

    def _get_contents(self) -> str:
        """Obtains and returns the contents of the clipboard."""

        if self._gpaste_proxy is None:
            return ""

        result = self._gpaste_proxy.GetElementAtIndex(0)[1]
        debug_string = result.replace("\n", "\\n")
        msg = f"GPASTE: Clipboard contents: {debug_string}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        if self._gpaste_proxy is None:
            return

        self._gpaste_proxy.Add(text)

class _ClipboardManagerKlipper(_ClipboardManager):
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
            msg = f"CLIPBOARD PRESENTER: Could not access klipper interface: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        try:
            self._signal_subscription = self._klipper_proxy.clipboardHistoryUpdated.connect(
                self._on_contents_changed
            )
            self._is_active = True
        except DBusError as error:
            msg = f"CLIPBOARD PRESENTER: Could not connect to klipper signal: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
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
        msg = f"KLIPPER: Clipboard contents: {debug_string}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def set_contents(self, text: str) -> None:
        """Sets the contents of the clipboard to text."""

        if self._klipper_proxy is None:
            return

        msg = f"KLIPPER: Setting clipboard contents to: {text}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._klipper_proxy.setClipboardContents(text)

class ClipboardPresenter:
    """Manages clipboard-related functionality."""

    def __init__(self) -> None:
        self._event_listener: Atspi.EventListener = Atspi.EventListener.new(self._listener)
        self._last_clipboard_update_text: str = ""
        self._last_clipboard_update_time: float = time.time()
        self._manager: _ClipboardManager | None = None
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()

        msg = "CLIPBOARD PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("ClipboardPresenter", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the clipboard-presenter keybindings."""

        if refresh:
            msg = f"CLIPBOARD PRESENTER: Refreshing bindings. Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("CLIPBOARD PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the clipboard-presenter handlers."""

        if refresh:
            msg = "CLIPBOARD PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up and returns the clipboard-presenter input event handlers."""

        self._handlers = {}

        self._handlers["present_clipboard_contents"] = \
            input_event.InputEventHandler(
                self.present_clipboard_contents,
                cmdnames.CLIPBOARD_PRESENT_CONTENTS)

    def _setup_bindings(self) -> None:
        """Sets up and returns the clipboard-presenter key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["present_clipboard_contents"],
                1,
                True))

        # This pulls in the user's overrides to alternative keys.
        self._bindings = settings_manager.get_manager().override_key_bindings(
            self._handlers, self._bindings, False)

    @dbus_service.command
    def present_clipboard_contents(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the clipboard contents."""

        tokens = ["CLIPBOARD PRESENTER: present_clipboard_contents. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self._manager is None:
            msg = "CLIPBOARD PRESENTER: Cannot present contents, no active manager."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        contents = self._manager.get_contents()
        if not contents or len(contents) > 5000:
            contents = messages.character_count(len(contents))
        script.present_message(messages.CLIPBOARD_CONTAINS % contents, contents)
        return True

    def _connect(self) -> None:
        """Connects to the clipboard manager."""

        if self._manager is not None:
            return

        manager: _ClipboardManager | None = None

        # If you try to connect to Klipper from a GNOME session, it will fail with a DBus
        # exception. However, if you try to connect to GPaste from a KDE session, it will
        # succeed -- or at least not throw an exception. Therefore, check for Klipper first.
        manager = _ClipboardManagerKlipper(self._present_clipboard_contents_change)
        manager.connect()
        if manager.is_active():
            self._manager = manager
            msg = "CLIPBOARD PRESENTER: Using Klipper."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        # See comment above. Check for GPaste last.
        manager = _ClipboardManagerGPaste(self._present_clipboard_contents_change)
        manager.connect()
        if manager.is_active():
            self._manager = manager
            msg = "CLIPBOARD PRESENTER: Using GPaste."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._manager = _ClipboardManagerFallback(self._present_clipboard_contents_change)
        self._manager.connect()
        msg = "CLIPBOARD PRESENTER: Using Gtk.Clipboard as fallback."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _disconnect(self) -> None:
        """Disconnects from the clipboard manager."""

        if self._manager is None:
            return
        self._manager.disconnect()

    def _get_contents(self) -> str:
        """Returns the clipboard contents."""

        if self._manager is None:
            msg = "CLIPBOARD PRESENTER: Cannot get contents, no active manager"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        result = self._manager.get_contents()
        debug_string = result.replace("\n", "\\n")
        msg = f"CLIPBOARD PRESENTER: Current contents: {debug_string}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def activate(self) -> None:
        """Activates the presenter."""

        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Activating", True)
        self._event_listener.register("object:text-changed")
        self._connect()
        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Activated", True)

    def deactivate(self) -> None:
        """Deactivates the presenter."""

        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Deactivating", True)
        self._event_listener.deregister("object:text-changed")
        self._disconnect()
        debug.print_message(debug.LEVEL_INFO, "CLIPBOARD PRESENTER: Deactivated", True)

    def append_text(self, text: str, separator: str = "\n") -> None:
        """Appends text to the clipboard contents."""

        if self._manager is None:
            msg = "CLIPBOARD PRESENTER: Cannot append text, no active manager."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        old_text = self._manager.get_contents()
        new_text = f"{old_text}{separator}{text}"
        msg = f"CLIPBOARD PRESENTER: Appending '{text}'. New contents: '{new_text}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._manager.set_contents(new_text)

    def set_text(self, text: str) -> None:
        """Sets the clipboard contents to text."""

        if self._manager is None:
            msg = "CLIPBOARD PRESENTER: Cannot set text, no active manager."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        msg = f"CLIPBOARD PRESENTER: Setting text to '{text}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._manager.set_contents(text)

    def is_clipboard_text_changed_event(self, event: Atspi.Event) -> bool:
        """Returns True if event is a text changed event associated with the clipboard."""

        if not event.type.startswith("object:text-changed"):
            return False

        if not (AXUtilities.is_editable(event.source) or AXUtilities.is_terminal(event.source)):
            return False

        manager = input_event_manager.get_manager()
        if not manager.last_event_was_command() or manager.last_event_was_undo():
            return False

        if manager.last_event_was_backspace():
            return False

        if "delete" in event.type and manager.last_event_was_paste():
            return False

        contents = self._get_contents()
        if not contents:
            return False

        if event.any_data == contents:
            return True

        if bool(re.search(r"\w", event.any_data)) != bool(re.search(r"\w", contents)):
            return False

        # Some applications send multiple text insertion events for part of a given paste.
        if contents.startswith(event.any_data.rstrip()):
            return True

        return False

    def _present_clipboard_contents_change(self, string: str) -> None:
        """Presents the clipboard contents change."""

        msg = f"CLIPBOARD PRESENTER: Contents changed to: '{string}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if string == self._last_clipboard_update_text \
           and time.time() - self._last_clipboard_update_time < 1:
            msg = "CLIPBOARD PRESENTER: Not presenting change: likely duplicate."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self._last_clipboard_update_text = string
        self._last_clipboard_update_time = time.time()
        script = script_manager.get_manager().get_active_script()
        if script is None:
            return

        manager = input_event_manager.get_manager()
        if manager.last_event_was_cut():
            script.present_message(messages.CLIPBOARD_CUT_FULL, messages.CLIPBOARD_CUT_BRIEF)
            return

        if manager.last_event_was_copy():
            script.present_message(messages.CLIPBOARD_COPIED_FULL, messages.CLIPBOARD_COPIED_BRIEF)
            return

        if manager.last_event_was_paste():
            script.present_message(messages.CLIPBOARD_PASTED_FULL, messages.CLIPBOARD_PASTED_BRIEF)
            return

        msg = "CLIPBOARD PRESENTER: Not presenting change: is not cut, copy, or paste"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _listener(self, event: Atspi.Event) -> None:
        """Generic listener for events of interest."""

        tokens = ["CLIPBOARD PRESENTER: Possible change event", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if self.is_clipboard_text_changed_event(event):
            self._present_clipboard_contents_change(event.any_data)


_presenter: ClipboardPresenter = ClipboardPresenter()
def get_presenter() -> ClipboardPresenter:
    """Returns the Clipboard Presenter singleton."""

    return _presenter
