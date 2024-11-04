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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position

"""Utilities for obtaining information about accessible applications."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023-2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import subprocess
import threading
import time

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject

class AXUtilitiesApplication:
    """Utilities for obtaining information about accessible applications."""

    REAL_APP_FOR_MUTTER_FRAME: dict = {}
    REAL_FRAME_FOR_MUTTER_FRAME: dict = {}

    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data():
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            AXUtilitiesApplication._clear_all_dictionaries()

    @staticmethod
    def _clear_all_dictionaries(reason=""):
        msg = "AXUtilitiesApplication: Clearing local cache."
        if reason:
            msg += f" Reason: {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        with AXUtilitiesApplication._lock:
            AXUtilitiesApplication.REAL_APP_FOR_MUTTER_FRAME.clear()
            AXUtilitiesApplication.REAL_FRAME_FOR_MUTTER_FRAME.clear()

    @staticmethod
    def clear_cache_now(reason=""):
        """Clears all cached information immediately."""

        AXUtilitiesApplication._clear_all_dictionaries(reason)

    @staticmethod
    def start_cache_clearing_thread():
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXUtilitiesApplication._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def application_as_string(obj):
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
    def find_real_app_and_window_for(obj, app=None):
        """Work around for window events coming from mutter-x11-frames."""

        if app is None:
            try:
                app = Atspi.Accessible.get_application(obj)
            except Exception as error:
                msg = f"AXUtilitiesApplication: Exception in find_real_app_and_window_for: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return None, None

        if AXObject.get_name(app) != "mutter-x11-frames":
            return app, obj

        real_app = AXUtilitiesApplication.REAL_APP_FOR_MUTTER_FRAME.get(hash(obj))
        real_frame = AXUtilitiesApplication.REAL_FRAME_FOR_MUTTER_FRAME.get(hash(obj))
        if real_app is not None and real_frame is not None:
            return real_app, real_frame

        tokens = ["AXUtilitiesApplication:", app, "is not valid app for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        try:
            desktop = Atspi.get_desktop(0)
        except Exception as error:
            msg = f"AXUtilitiesApplication: Exception in find_real_app_and_window_for: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None, None

        unresponsive_apps = []
        name = AXObject.get_name(obj)
        for desktop_app in AXObject.iter_children(desktop):
            if AXUtilitiesApplication.is_application_unresponsive(desktop_app):
                unresponsive_apps.append(desktop_app)
                continue
            if AXObject.get_name(desktop_app) == "mutter-x11-frames":
                continue
            for frame in AXObject.iter_children(desktop_app):
                if name == AXObject.get_name(frame):
                    real_app = desktop_app
                    real_frame = frame

        tokens = ["AXUtilitiesApplication:", real_app, "is real app for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if real_frame != obj:
            msg = "AXUtilitiesApplication: Updated frame to frame from real app"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        AXUtilitiesApplication.REAL_APP_FOR_MUTTER_FRAME[hash(obj)] = real_app
        AXUtilitiesApplication.REAL_FRAME_FOR_MUTTER_FRAME[hash(obj)] = real_frame
        return real_app, real_frame

    @staticmethod
    def get_all_applications(must_have_window=False, exclude_unresponsive=False, is_debug=False):
        """Returns a list of running applications known to Atspi."""

        desktop = AXUtilitiesApplication.get_desktop()
        if desktop is None:
            return []

        def pred(obj):
            if exclude_unresponsive and AXUtilitiesApplication.is_application_unresponsive(obj):
                return False
            if must_have_window:
                return AXObject.get_child_count(obj) > 0
            if AXObject.get_name(obj) == "mutter-x11-frames":
                return is_debug
            return True

        return list(AXObject.iter_children(desktop, pred))

    @staticmethod
    def get_application(obj, sanity_check=True):
        """Returns the accessible application associated with obj"""

        if obj is None:
            return None

        app = AXUtilitiesApplication.REAL_APP_FOR_MUTTER_FRAME.get(hash(obj))
        if app is not None:
            return app

        try:
            app = Atspi.Accessible.get_application(obj)
        except Exception as error:
            msg = f"AXUtilitiesApplication: Exception in get_application: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        if not sanity_check or AXObject.get_name(app) != "mutter-x11-frames":
            return app

        real_app = AXUtilitiesApplication.find_real_app_and_window_for(obj, app)[0]
        if real_app is not None:
            app = real_app

        return app

    @staticmethod
    def get_application_toolkit_name(obj):
        """Returns the toolkit name reported for obj's application."""

        app = AXUtilitiesApplication.get_application(obj)
        if app is None:
            return ""

        try:
            name = Atspi.Accessible.get_toolkit_name(app)
        except Exception as error:
            msg = f"AXUtilitiesApplication: Exception in get_application_toolkit_name: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return name

    @staticmethod
    def get_application_toolkit_version(obj):
        """Returns the toolkit version reported for obj's application."""

        app = AXUtilitiesApplication.get_application(obj)
        if app is None:
            return ""

        try:
            version = Atspi.Accessible.get_toolkit_version(app)
        except Exception as error:
            msg = f"AXUtilitiesApplication: Exception in get_application_toolkit_version: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        return version

    @staticmethod
    def get_application_with_pid(pid):
        """Returns the accessible application with the specified pid"""

        applications = AXUtilitiesApplication.get_all_applications()
        for child in applications:
            if AXUtilitiesApplication.get_process_id(child) == pid:
                return child

        tokens = ["WARNING: app with pid", pid, "is not in the accessible desktop"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return None

    @staticmethod
    def get_desktop():
        """Returns the accessible desktop"""

        try:
            desktop = Atspi.get_desktop(0)
        except Exception as error:
            tokens = ["ERROR: Exception getting desktop from Atspi:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        return desktop

    @staticmethod
    def get_process_id(obj):
        """Returns the process id associated with obj"""

        try:
            pid = Atspi.Accessible.get_process_id(obj)
        except Exception as error:
            msg = f"AXUtilitiesApplication: Exception in get_process_id: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        return pid

    @staticmethod
    def is_application_in_desktop(app):
        """Returns true if app is known to Atspi"""

        applications = AXUtilitiesApplication.get_all_applications()
        for child in applications:
            if child == app:
                return True

        tokens = ["WARNING:", app, "is not in the accessible desktop"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    @staticmethod
    def is_application_unresponsive(app):
        """Returns true if app's process is known to be unresponsive."""

        pid = AXUtilitiesApplication.get_process_id(app)
        try:
            state = subprocess.getoutput(f"cat /proc/{pid}/status | grep State")
            state = state.split()[1]
        except Exception as error:
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

AXUtilitiesApplication.start_cache_clearing_thread()
