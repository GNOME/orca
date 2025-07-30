# Orca
#
# Copyright 2019 Igalia, S.L.
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


"""Custom script utilities for kwin."""

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2019 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import switcher
from orca.scripts.toolkits.Qt.script_utilities import Utilities as QtUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Utilities(switcher.Utilities, QtUtilities):
    """Custom script utilities for kwin."""

    def is_switcher_container(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if obj is the switcher container."""

        return AXUtilities.is_filler(obj) and AXUtilities.is_focused(obj)

    def is_switcher_selection_change_event_type(self, event: Atspi.Event) -> bool:
        """Returns True if this event is the one we use to present changes."""

        if event.type.startswith("object:state-changed:focused"):
            return event.detail1

        return False

    def get_selection_name(self, container: Atspi.Accessible | None = None) -> str:
        """Returns the name of the currently-selected item."""

        if self.is_switcher_container(container):
            return AXObject.get_name(container)

        return ""
