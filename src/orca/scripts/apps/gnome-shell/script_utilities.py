# Orca
#
# Copyright (C) 2014 Igalia, S.L.
#
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

"""Custom script utilities for gnome-shell."""

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import script_utilities
from orca.ax_text import AXText

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(script_utilities.Utilities):
    """Custom script utilities for gnome-shell."""

    def inserted_text(self, event: Atspi.Event) -> str:
        if event.any_data:
            return event.any_data

        # https://gitlab.gnome.org/GNOME/mutter/-/issues/3826
        if event.detail1 == -1:
            msg = "GNOME SHELL: Broken text insertion event"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            string = AXText.get_all_text(event.source)
            if string:
                msg = f"GNOME SHELL: Returning last char in '{string}'"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return string[-1]

            msg = "GNOME SHELL: Unable to correct broken text insertion event"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        return ""
