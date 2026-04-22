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

import os
import shutil
import subprocess
import time
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

    _BUS_NAME = "org.gnome.Orca.Service"
    _BASE_PATH = "/org/gnome/Orca/Service"
    _BINARY_ENV_VAR = "ORCA_TEST_BINARY"

    def __init__(self, env: dict[str, str]) -> None:
        self._env = env
        self._process: subprocess.Popen | None = None
        self._bus = SessionMessageBus()

    def launch(self, readiness_timeout: float = 45.0) -> None:
        """Starts Orca as a subprocess and waits for the D-Bus service to come up."""

        self._process = subprocess.Popen([self._resolve_orca_binary()], env=self._env)
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
        """Calls an Orca D-Bus runtime setter; lets errors bubble up."""

        proxy = self._bus.get_proxy(self._BUS_NAME, f"{self._BASE_PATH}/{module}")
        proxy.ExecuteRuntimeSetter(name, _to_variant(value))

    def get(self, module: str, name: str) -> Any:
        """Calls an Orca D-Bus runtime getter and returns the unpacked value."""

        proxy = self._bus.get_proxy(self._BUS_NAME, f"{self._BASE_PATH}/{module}")
        return proxy.ExecuteRuntimeGetter(name)

    def press_orca_key(self, keysym: int) -> None:
        """Presses keysym with Orca's current modifier key held (Orca+key chord)."""

        is_desktop = self.get("CommandManager", "KeyboardLayoutIsDesktop")
        modifier_getter = "DesktopModifierKeys" if is_desktop else "LaptopModifierKeys"
        modifier_keysym = Gdk.keyval_from_name(self.get("CommandManager", modifier_getter)[0])
        keyboard.press_key(modifier_keysym)
        try:
            keyboard.press_key(keysym)
            keyboard.release_key(keysym)
        finally:
            keyboard.release_key(modifier_keysym)

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


def _to_variant(value: bool | str) -> GLib.Variant:
    """Wraps value in a GLib.Variant for the D-Bus setter call."""

    return GLib.Variant("b" if isinstance(value, bool) else "s", value)
