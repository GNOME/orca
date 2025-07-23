# Utilities for obtaining information about accessible applications.
#
# Copyright 2023-2024 Igalia, S.L.
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

# pylint: disable=wrong-import-position

"""Utilities for obtaining information about accessible applications."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023-2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import subprocess

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from .ax_object import AXObject

class AXUtilitiesApplication:
    """Utilities for obtaining information about accessible applications."""

    @staticmethod
    def application_as_string(obj: Atspi.Accessible) -> str:
        """Returns the application details of obj as a string."""

        app = AXUtilitiesApplication.get_application(obj)
        if app is None:
            return ""

        string = (
            f"{AXObject.get_name(app)} "
            f"({AXUtilitiesApplication.get_application_toolkit_name(obj)} "
            f"{AXUtilitiesApplication.get_application_toolkit_version(obj)})"
        )
        return string

    @staticmethod
    def get_all_applications(
        must_have_window: bool = False,
        exclude_unresponsive: bool = False,
        is_debug: bool = False
    ) -> list[Atspi.Accessible]:
        """Returns a list of running applications known to Atspi."""

        desktop = AXUtilitiesApplication.get_desktop()
        if desktop is None:
            return []

        def pred(obj: Atspi.Accessible) -> bool:
            if exclude_unresponsive and AXUtilitiesApplication.is_application_unresponsive(obj):
                return False
            if AXObject.get_name(obj) == "mutter-x11-frames":
                return is_debug
            if must_have_window:
                return AXObject.get_child_count(obj) > 0
            return True

        return list(AXObject.iter_children(desktop, pred))

    @staticmethod
    def get_application(obj: Atspi.Accessible) -> Atspi.Accessible | None:
        """Returns the accessible application associated with obj"""

        if obj is None:
            return None

        try:
            app = Atspi.Accessible.get_application(obj)
        except GLib.GError as error:
            msg = f"AXUtilitiesApplication: Exception in get_application: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None
        return app

    @staticmethod
    def get_application_toolkit_name(obj: Atspi.Accessible) -> str:
        """Returns the toolkit name reported for obj's application."""

        app = AXUtilitiesApplication.get_application(obj)
        if app is None:
            return ""

        try:
            name = Atspi.Accessible.get_toolkit_name(app)
        except GLib.GError as error:
            msg = f"AXUtilitiesApplication: Exception in get_application_toolkit_name: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return name

    @staticmethod
    def get_application_toolkit_version(obj: Atspi.Accessible) -> str:
        """Returns the toolkit version reported for obj's application."""

        app = AXUtilitiesApplication.get_application(obj)
        if app is None:
            return ""

        try:
            version = Atspi.Accessible.get_toolkit_version(app)
        except GLib.GError as error:
            msg = f"AXUtilitiesApplication: Exception in get_application_toolkit_version: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return version

    @staticmethod
    def get_application_with_pid(pid: int) -> Atspi.Accessible | None:
        """Returns the accessible application with the specified pid"""

        applications = AXUtilitiesApplication.get_all_applications()
        for child in applications:
            if AXUtilitiesApplication.get_process_id(child) == pid:
                return child

        tokens = ["WARNING: app with pid", pid, "is not in the accessible desktop"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return None

    @staticmethod
    def get_desktop() -> Atspi.Accessible | None:
        """Returns the accessible desktop"""

        try:
            desktop = Atspi.get_desktop(0)
        except GLib.GError as error:
            tokens = ["ERROR: Exception getting desktop from Atspi:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return desktop

    @staticmethod
    def get_process_id(obj: Atspi.Accessible) -> int:
        """Returns the process id associated with obj"""

        try:
            pid = Atspi.Accessible.get_process_id(obj)
        except GLib.GError as error:
            msg = f"AXUtilitiesApplication: Exception in get_process_id: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        return pid

    @staticmethod
    def is_application_in_desktop(app: Atspi.Accessible) -> bool:
        """Returns true if app is known to Atspi"""

        applications = AXUtilitiesApplication.get_all_applications()
        for child in applications:
            if child == app:
                return True

        tokens = ["WARNING:", app, "is not in the accessible desktop"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    @staticmethod
    def is_application_unresponsive(app: Atspi.Accessible) -> bool:
        """Returns true if app's process is known to be unresponsive."""

        pid = AXUtilitiesApplication.get_process_id(app)
        try:
            state = subprocess.getoutput(f"cat /proc/{pid}/status | grep State")
            state = state.split()[1]
        except (GLib.GError, IndexError) as error:
            tokens = [f"AXUtilitiesApplication: Exception checking state of pid {pid}: {error}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if state == "Z":
            tokens = [f"AXUtilitiesApplication: pid {pid} is zombie process"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if state == "T":
            tokens = [f"AXUtilitiesApplication: pid {pid} is suspended/stopped process"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False
