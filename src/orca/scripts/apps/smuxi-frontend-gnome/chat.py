# Orca
#
# Copyright 2018 Igalia, S.L.
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

"""Custom chat module for Smuxi."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018 Igalia, S.L."
__license__   = "LGPL"


from orca import chat
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


class Chat(chat.Chat):
    """Custom chat module for Smuxi."""

    def isFocusedChat(self, obj):
        """Returns True if we plan to treat this chat as focused."""

        page_tab = AXObject.find_ancestor(obj, AXUtilities.is_page_tab)
        if page_tab is None:
            return super().isFocusedChat(obj)

        return AXUtilities.is_showing(page_tab)
