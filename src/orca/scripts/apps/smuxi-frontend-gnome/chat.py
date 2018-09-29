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

"""Custom chat module for Smuxi."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.chat as chat


class Chat(chat.Chat):

    def __init__(self, script, buddyListAncestries):

        super().__init__(script, buddyListAncestries)

    def isFocusedChat(self, obj):
        """Returns True if we plan to treat this chat as focused."""

        isPageTab = lambda x: x and x.getRole() == pyatspi.ROLE_PAGE_TAB
        pageTab = pyatspi.findAncestor(obj, isPageTab)
        if pageTab is None:
            return super().isFocusedChat(obj)

        return pageTab.getState().contains(pyatspi.STATE_SHOWING)
