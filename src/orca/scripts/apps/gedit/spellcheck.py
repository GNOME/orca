# Orca
#
# Copyright 2014 Igalia, S.L.
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

"""Customized support for spellcheck in Gedit."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class SpellCheck(spellcheck.SpellCheck):
    """Customized support for spellcheck in Gedit."""

    def _is_candidate_window(self, window: Atspi.Accessible) -> bool:
        """Returns True if window could be the spellcheck window pending other checks."""

        if window is None:
            return False

        if AXUtilities.is_dialog(window):
            return True

        if not AXUtilities.is_frame(window):
            return False

        if AXObject.find_descendant(window, AXUtilities.is_split_pane):
            return False

        return True
