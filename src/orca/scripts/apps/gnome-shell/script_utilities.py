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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

from orca import debug
from orca import script_utilities
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from orca.ax_text import AXText

class Utilities(script_utilities.Utilities):

    def insertedText(self, event):
        if event.any_data:
            return event.any_data

        if event.detail1 == -1:
            msg = "GNOME SHELL: Broken text insertion event"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            string = AXText.get_all_text(event.source)
            if string:
                msg = f"GNOME SHELL: Returning last char in '{string}'"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return string[-1]

            msg = "GNOME SHELL: Unable to correct broken text insertion event"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        return ""

    def unrelatedLabels(self, root, onlyShowing=True, minimumWords=3):
        if not root:
            return []

        def hasRole(x):
            return AXUtilities.is_dialog(x) \
                or AXUtilities.is_notification(x) \
                or AXUtilities.is_menu_item(x)

        if not hasRole(root) and AXObject.find_ancestor(root, hasRole) is None:
            tokens = ["GNOME SHELL: Not seeking unrelated labels for", root]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        return super().unrelatedLabels(root, onlyShowing, minimumWords)
