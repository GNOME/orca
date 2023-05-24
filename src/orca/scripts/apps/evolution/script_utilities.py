# Orca
#
# Copyright (C) 2015 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.scripts.toolkits.gtk as gtk
import orca.scripts.toolkits.WebKitGtk as WebKitGtk
from orca.ax_object import AXObject


class Utilities(WebKitGtk.Utilities, gtk.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def isComposeMessageBody(self, obj):
        if not AXObject.has_state(obj, Atspi.StateType.EDITABLE):
            return False

        return self.isEmbeddedDocument(obj)

    def isReceivedMessage(self, obj):
        if AXObject.has_state(obj, Atspi.StateType.EDITABLE):
            return False

        return self.isEmbeddedDocument(obj)

    def isReceivedMessageHeader(self, obj):
        if not (obj and AXObject.get_role(obj) == Atspi.Role.TABLE):
            return False

        return self.isReceivedMessage(AXObject.get_parent(obj))

    def isReceivedMessageContent(self, obj):
        if not (obj and AXObject.get_role(obj) == Atspi.Role.SECTION):
            return False

        return self.isReceivedMessage(AXObject.get_parent(obj))

    def isComposeAutocomplete(self, obj):
        if not (obj and AXObject.get_role(obj) == Atspi.Role.TABLE):
            return False

        if not AXObject.has_state(obj, Atspi.StateType.MANAGES_DESCENDANTS):
            return False

        topLevel = self.topLevelObject(obj)
        return topLevel and AXObject.get_role(topLevel) == Atspi.Role.WINDOW

    def findMessageBodyChild(self, root):
        candidate = AXObject.find_descendant(root, self.isDocument)
        if self.isEmbeddedDocument(candidate):
            return self.findMessageBodyChild(candidate)

        return candidate

    def isMessageListStatusCell(self, obj):
        if not self.isMessageListToggleCell(obj):
            return False

        header = self.columnHeaderForCell(obj)
        return header and AXObject.get_name(header) != AXObject.get_name(obj)

    def isMessageListToggleCell(self, obj):
        if self.isWebKitGtk(obj):
            return False

        if not gtk.Utilities.hasMeaningfulToggleAction(self, obj):
            return False

        if not AXObject.get_name(obj):
            return False

        return True

    def realActiveDescendant(self, obj):
        if self.isWebKitGtk(obj):
            return super().realActiveDescendant(obj)

        # This is some mystery child of the 'Messages' panel which fails to show
        # up in the hierarchy or emit object:state-changed:focused events.
        if AXObject.get_role(obj) == Atspi.Role.LAYERED_PANE:
            isTreeTable = lambda x: x and AXObject.get_role(x) == Atspi.Role.TREE_TABLE
            return AXObject.find_descendant(obj, isTreeTable) or obj

        return gtk.Utilities.realActiveDescendant(self, obj)

    def setCaretAtStart(self, obj):
        if self.isReceivedMessageContent(obj):
            obj = self.findMessageBodyChild(obj) or obj

        child, index = super().setCaretAtStart(obj)
        if child and index == -1:
            child, index = super().setCaretAtStart(child)

        return child, index

    def treatAsBrowser(self, obj):
        if not self.isEmbeddedDocument(obj):
            return False

        isSplitPane = lambda x: x and AXObject.get_role(x) == Atspi.Role.SPLIT_PANE
        if AXObject.find_ancestor(obj, isSplitPane):
            return False

        return True
