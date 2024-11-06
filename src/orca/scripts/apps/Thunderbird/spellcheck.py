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

# pylint: disable=duplicate-code

"""Customized support for spellcheck in Thunderbird."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class SpellCheck(spellcheck.SpellCheck):
    """Customized support for spellcheck in Thunderbird."""

    def _is_candidate_window(self, window):
        if not (AXUtilities.is_dialog(window) or AXUtilities.is_modal(window)):
            tokens = ["THUNDERBIRD SPELL CHECK:", window, "is not a dialog or modal window"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        def is_non_spell_check_child(x):
            return AXUtilities.is_page_tab_list(x) or AXUtilities.is_split_pane(x)

        if AXObject.find_descendant(window, is_non_spell_check_child):
            return False

        return True
