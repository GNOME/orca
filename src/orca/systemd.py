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

class Systemd:
    """Orca's integration with the systemd service manager"""

    def __init__(self) -> None:
        self._notify_socket: socket.socket | None = None

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

    def _notify(self, message: bytes) -> None:
        """Send systemd a raw sd_notify notification"""
        # Reference:
        # https://freedesktop.org/software/systemd/man/sd_notify.html#Standalone%20Implementations
        if self._notify_socket:
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

_manager: Systemd = Systemd()

def get_manager() -> Systemd:
    """Returns the Systemd singleton."""
    return _manager
