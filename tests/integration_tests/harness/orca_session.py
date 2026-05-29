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

"""Orca subprocess session wrapper for integration tests."""

import contextlib
import os
import secrets
import shutil
import subprocess
import sys
import time
from collections.abc import Iterator
from typing import Any

import gi
from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError

gi.require_version("Gdk", "3.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gdk, GLib

from . import keyboard


class OrcaSession:
    """Launches Orca as a subprocess and exposes its D-Bus remote controller."""

    _BUS_NAME = "org.gnome.Orca1.Service"
    _BASE_PATH = "/org/gnome/Orca1/Service"
    _PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
    _BINARY_ENV_VAR = "ORCA_TEST_BINARY"
    _RPC_ENV_VAR = "ORCA_TEST_RPC_SECRET"

    def __init__(self, env: dict[str, str]) -> None:
        self._env = env
        self._rpc_secret = secrets.token_hex(32)
        self._env[self._RPC_ENV_VAR] = self._rpc_secret
        self._process: subprocess.Popen | None = None
        self._bus = SessionMessageBus()
        self._orca_modifier_keysym: int | None = None

    def launch(self, readiness_timeout: float = 45.0) -> None:
        """Starts Orca as a subprocess and waits for the D-Bus service to come up."""

        argv = [self._resolve_orca_binary()]
        # Set ORCA_TEST_DEBUG_FILE to capture Orca's own debug log for a run (single test
        # at a time; multiple Orca processes would share the path).
        if debug_file := os.environ.get("ORCA_TEST_DEBUG_FILE"):
            argv = [*argv, f"--debug-file={debug_file}"]
        if os.environ.get("ORCA_TEST_COVERAGE"):
            argv = [sys.executable, "-m", "coverage", "run", "--parallel-mode", *argv]
        # Not a `with`: the Orca process must outlive launch() and is terminated in quit().
        # pylint: disable-next=consider-using-with
        self._process = subprocess.Popen(argv, env=self._env)
        self._wait_for_service(readiness_timeout)

    def quit(self, grace_period: float = 3.0) -> None:
        """Terminates the Orca subprocess, escalating to SIGKILL if needed."""

        if self._process is None or self._process.poll() is not None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=grace_period)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

    def set(self, module: str, name: str, value: bool | str) -> None:
        """Sets an Orca D-Bus property; lets errors bubble up."""

        proxy = self._properties_proxy(module)
        proxy.Set(f"org.gnome.Orca1.{module}", name, _to_variant(value))

    def get(self, module: str, name: str) -> Any:
        """Gets an Orca D-Bus property and returns the unpacked value."""

        proxy = self._properties_proxy(module)
        result = proxy.Get(f"org.gnome.Orca1.{module}", name)
        return result.unpack() if hasattr(result, "unpack") else result

    def call(self, module: str, command: str, *args: Any) -> Any:
        """Invokes a D-Bus command on an Orca module and returns its result."""

        proxy = self._bus.get_proxy(self._BUS_NAME, f"{self._BASE_PATH}/{module}")
        # dasbus exposes each D-Bus method as a dynamic attribute, so a command named
        # at runtime can only be reached via getattr.
        return getattr(proxy, command)(*args)

    def _properties_proxy(self, module: str) -> Any:
        """Returns a proxy bound to the freedesktop Properties interface for module."""

        return self._bus.get_proxy(
            self._BUS_NAME,
            f"{self._BASE_PATH}/{module}",
            interface_name=self._PROPERTIES_INTERFACE,
        )

    def press_orca_key(self, keysym: int, extra_modifiers: list[int] | None = None) -> None:
        """Presses keysym with Orca's modifier (and any extra_modifiers) held."""

        if self._orca_modifier_keysym is None:
            is_desktop = self.get("CommandManager", "KeyboardLayoutIsDesktop")
            modifier_getter = "DesktopModifierKeys" if is_desktop else "LaptopModifierKeys"
            self._orca_modifier_keysym = Gdk.keyval_from_name(
                self.get("CommandManager", modifier_getter)[0]
            )
        modifiers = [self._orca_modifier_keysym, *(extra_modifiers or [])]
        keyboard.press_chord(modifiers, keysym)

    def available_keybindings(self, count: int = 1) -> list[tuple[str, int]]:
        """Returns up to count currently-unbound Orca-modified keybindings (test-only RPC)."""

        return self.call(
            "CommandManager", "GetAvailableKeybindingsForTesting", self._rpc_secret, count
        )

    def bind_command(self, command_name: str, keysym: str, modifiers: int) -> None:
        """Binds command_name to keysym+modifiers; call refresh_keybindings to apply it."""

        self.call(
            "CommandManager",
            "BindCommandForTesting",
            self._rpc_secret,
            command_name,
            keysym,
            modifiers,
        )

    def unbind_command(self, command_name: str) -> None:
        """Removes the test binding for command_name; call refresh_keybindings to apply it."""

        self.call("CommandManager", "UnbindCommandForTesting", self._rpc_secret, command_name)

    def refresh_keybindings(self) -> None:
        """Re-applies keybinding overrides and refreshes the AT-SPI grabs (test-only RPC)."""

        self.call("CommandManager", "RefreshKeybindingsForTesting", self._rpc_secret)

    @contextlib.contextmanager
    def bound_command(self, command_name: str, keysym: str, modifiers: int) -> Iterator[None]:
        """Binds command_name for the duration of the block, refreshing grabs on entry and exit."""

        self.bind_command(command_name, keysym, modifiers)
        self.refresh_keybindings()
        try:
            yield
        finally:
            self.unbind_command(command_name)
            self.refresh_keybindings()

    def press_bound_key(self, keysym: str, extra_modifiers: list[int] | None = None) -> None:
        """Presses an Orca-modified key by keysym name (as returned by available_keybindings)."""

        self.press_orca_key(Gdk.keyval_from_name(keysym), extra_modifiers)

    def _resolve_orca_binary(self) -> str:
        """Returns the path to the Orca binary to launch."""

        if override := os.environ.get(self._BINARY_ENV_VAR):
            return override
        if found := shutil.which("orca"):
            return found
        raise RuntimeError("Orca binary not found on PATH and ORCA_TEST_BINARY is not set")

    def _wait_for_service(self, timeout: float) -> None:
        """Waits until Orca's D-Bus service answers a GetVersion call."""

        deadline = time.monotonic() + timeout
        proxy = self._bus.get_proxy(self._BUS_NAME, self._BASE_PATH)
        while time.monotonic() < deadline:
            if self._process is not None and (code := self._process.poll()) is not None:
                raise RuntimeError(f"Orca exited early with code {code}")
            try:
                proxy.GetVersion()
                return
            except (DBusError, ConnectionError):
                time.sleep(0.05)
        raise TimeoutError(f"Orca D-Bus service did not become ready within {timeout}s")


def _to_variant(value: bool | str | list[str]) -> GLib.Variant:
    """Wraps value in a GLib.Variant for the D-Bus setter call."""

    if isinstance(value, bool):
        return GLib.Variant("b", value)
    if isinstance(value, list):
        return GLib.Variant("as", value)
    return GLib.Variant("s", value)
