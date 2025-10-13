# Orca
#
# Copyright 2025 Red Hat
# Author: Adrian Vovk <avovk@redhat.com>
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

"""Orca's integration with the systemd service manager"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2025 Red Hat"
__license__   = "LGPL"

import errno
import os
import socket
import time
from gi.repository import GLib

from . import debug

class Systemd:
    """Orca's integration with the systemd service manager"""

    def __init__(self) -> None:
        self._notify_socket: socket.socket | None = None
        self._watchdog_interval: int | None = None
        self._last_ping: float = 0.0

        socket_path = os.environ.get("NOTIFY_SOCKET")
        if socket_path:
            if socket_path[0] == "@": # Abstract socket
                socket_path = "\0" + socket_path[1:]
            elif socket_path[0] == "/": # Normal filesystem socket
                pass
            else: # VSOCK, etc
                raise OSError(errno.EAFNOSUPPORT, "Unsupported NOTIFY_SOCKET type")

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC)
            sock.connect(socket_path)
            self._notify_socket = sock

        watchdog_usec = os.environ.get("WATCHDOG_USEC")
        if watchdog_usec:
            self._watchdog_interval = int(watchdog_usec) // 1000 # µs -> ms

    def _notify(self, message: bytes) -> None:
        """Send systemd a raw sd_notify notification"""
        # Reference:
        # https://freedesktop.org/software/systemd/man/sd_notify.html#Standalone%20Implementations
        if self._notify_socket:
            debug.print_message(
                debug.LEVEL_INFO, f"SYSTEMD: Sending: {message.decode('utf-8')}", True)
            self._notify_socket.sendall(message)

    def notify_ready(self) -> None:
        """Tell systemd that Orca has finished starting up / reloading"""
        self._notify(b"READY=1")

    def notify_reloading(self) -> None:
        """Tell systemd that Orca has started reloading"""
        reload_timestamp = time.clock_gettime_ns(time.CLOCK_MONOTONIC) // 1000
        message = f"RELOADING=1\nMONOTONIC_USEC={reload_timestamp}"
        self._notify(message.encode())

    def notify_stopping(self) -> None:
        """Tell systemd that Orca is shutting down"""
        self._notify(b"STOPPING=1")

    def _ping_watchdog(self) -> None:
        """Send a watchdog ping and update last-ping timestamp"""
        self._notify(b"WATCHDOG=1")
        self._last_ping = time.time()

    def notify_alive(self, reason: str = "") -> None:
        """Tell systemd that Orca is still alive"""

        if not self._watchdog_interval:
            return

        msg = f"SYSTEMD: notify_alive called. {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        elapsed_ms = (time.time() - self._last_ping) * 1000
        if elapsed_ms >= self._watchdog_interval // 2:
            self._ping_watchdog()

    def start_watchdog(self) -> None:
        """Start regularly sending keepalive pings to the systemd watchdog"""
        if not self._watchdog_interval:
            return

        def _on_watchdog_tick() -> bool:
            """Send a keepalive ping to the watchdog"""
            self._ping_watchdog()
            return GLib.SOURCE_CONTINUE

        # The interval systemd reports to us is the deadline: if we miss it,
        # systemd will restart Orca. So, we want to ping more quickly than
        # requested, to avoid a situation where timer inaccuracies will
        # cause us to miss the deadline. systemd's code for this pings
        # anywhere from 133% - 200% faster than necessary. For us it's
        # easier to just ping 2x as fast. Use a high priority so that it is
        # scheduled ahead of other work done on the main loop (e.g. event
        # processing during a flood).
        GLib.timeout_add(self._watchdog_interval // 2, _on_watchdog_tick,
                         priority=GLib.PRIORITY_HIGH)

    def is_systemd_managed(self) -> bool:
        """Returns whether or not Orca is being managed by systemd"""
        return self._notify_socket is not None

_manager: Systemd = Systemd()

def get_manager() -> Systemd:
    """Returns the Systemd singleton."""
    return _manager
