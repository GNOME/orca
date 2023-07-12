# Utilities for performing tasks not specific to a particular object.
#
# Copyright 2023 Igalia, S.L.
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

"""
Utilities for performing tasks not specific to a particular object.
These utilities are app-type- and toolkit-agnostic. Utilities that might have
different implementations or results depending on the type of app (e.g. terminal,
chat, web) or toolkit (e.g. Qt, Gtk) should be in script_utilities.py file(s).

N.B. There are currently utilities that should never have custom implementations
that live in script_utilities.py files. These will be moved over time.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject


class AXUtilities:

    @staticmethod
    def get_desktop():
        """Returns the accessible desktop"""

        try:
            desktop = Atspi.get_desktop(0)
        except Exception as e:
            msg = "ERROR: Exception getting desktop from Atspi: %s" % e
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        return desktop

    @staticmethod
    def get_all_applications(must_have_window=False):
        """Returns a list of running applications known to Atspi, filtering out
        those which have no child windows if must_have_window is True."""

        desktop = AXUtilities.get_desktop()
        if desktop is None:
            return []

        def pred(x):
            if must_have_window:
                return AXObject.get_child_count(x) > 0
            return True

        return [app for app in AXObject.iter_children(desktop, pred)]

    @staticmethod
    def is_application_in_desktop(app):
        """Returns true if app is known to Atspi"""

        desktop = AXUtilities.get_desktop()
        if desktop is None:
            return False

        for child in AXObject.iter_children(desktop):
            if child == app:
                return True

        msg = "WARNING: %s is not in %s" % (app, desktop)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False


    @staticmethod
    def get_application_with_pid(pid):
        """Returns the accessible application with the specified pid"""

        desktop = AXUtilities.get_desktop()
        if desktop is None:
            return None

        for app in AXObject.iter_children(desktop):
            if AXObject.get_process_id(app) == pid:
                return app

        msg = "WARNING: app with pid %i is not in %s" % (pid, desktop)
        debug.println(debug.LEVEL_INFO, msg, True)
        return None
