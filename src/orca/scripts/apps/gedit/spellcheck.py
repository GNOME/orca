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

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpellCheck(spellcheck.SpellCheck):
    """Customized support for spellcheck in Gedit."""

    def _is_candidate_window(self, window):
        if not window:
            return False

        if AXUtilities.is_dialog(window):
            return True

        if not AXUtilities.is_frame(window):
            return False

        if AXObject.find_descendant(window, AXUtilities.is_split_pane):
            return False

        return True
