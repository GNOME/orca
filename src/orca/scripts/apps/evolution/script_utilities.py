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

import pyatspi

import orca.scripts.toolkits.gtk as gtk
import orca.scripts.toolkits.WebKitGtk as WebKitGtk

class Utilities(WebKitGtk.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def isComposeMessageBody(self, obj):
        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        return self.isEmbeddedDocument(obj)

    def isReceivedMessage(self, obj):
        if obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        return self.isEmbeddedDocument(obj)

    def isReceivedMessageHeader(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE):
            return False

        return self.isReceivedMessage(obj.parent)

    def isReceivedMessageContent(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_SECTION):
            return False

        return self.isReceivedMessage(obj.parent)

    def isComposeAutocomplete(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_TABLE):
            return False

        if not obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS):
            return False

        topLevel = self.topLevelObject(obj)
        return topLevel and topLevel.getRole() == pyatspi.ROLE_WINDOW

    def findMessageBodyChild(self, root):
        roles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]
        isDocument = lambda x: x and x.getRole() in roles
        candidate = pyatspi.findDescendant(root, isDocument)
        if self.isEmbeddedDocument(candidate):
            return self.findMessageBodyChild(candidate)

        return candidate

    def isMessageListStatusCell(self, obj):
        if not self.isMessageListToggleCell(obj):
            return False

        header = self.columnHeaderForCell(obj)
        return header and header.name != obj.name

    def isMessageListToggleCell(self, obj):
        if self.isWebKitGtk(obj):
            return False

        if not gtk.Utilities.hasMeaningfulToggleAction(self, obj):
            return False

        if not obj.name:
            return False

        return True

    def realActiveDescendant(self, obj):
        if self.isWebKitGtk(obj):
            return super().realActiveDescendant(obj)

        # This is some mystery child of the 'Messages' panel which fails to show
        # up in the hierarchy or emit object:state-changed:focused events.
        if obj.getRole() == pyatspi.ROLE_LAYERED_PANE:
            isTreeTable = lambda x: x and x.getRole() == pyatspi.ROLE_TREE_TABLE
            return pyatspi.utils.findDescendant(obj, isTreeTable) or obj

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

        isSplitPane = lambda x: x and x.getRole() == pyatspi.ROLE_SPLIT_PANE
        if pyatspi.utils.findAncestor(obj, isSplitPane):
            return False

        return True
