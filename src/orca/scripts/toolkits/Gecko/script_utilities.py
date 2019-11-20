# Orca
#
# Copyright 2010 Joanmarie Diggs.
# Copyright 2014-2015 Igalia, S.L.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import re
import time

from orca import debug
from orca import orca_state
from orca.scripts import web


class Utilities(web.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._lastAutoTextObjectEvent = None
        self._lastAutoTextInputEvent = None
        self._lastAutoTextEventTime = 0

    def _attemptBrokenTextRecovery(self, obj, **args):
        boundary = args.get('boundary')

        # Gecko fails to implement this boundary type.
        if boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START:
            return True

        if self.isContentEditableWithEmbeddedObjects(obj):
            return boundary == pyatspi.TEXT_BOUNDARY_WORD_START

        return True

    def _treatAsLeafNode(self, obj):
        if obj.getRole() == pyatspi.ROLE_TABLE_ROW:
            return not obj.childCount

        return super()._treatAsLeafNode(obj)

    def containsPoint(self, obj, x, y, coordType, margin=2):
        if not super().containsPoint(obj, x, y, coordType, margin):
            return False

        roles = [pyatspi.ROLE_MENU, pyatspi.ROLE_TOOL_TIP]
        if obj.getRole() in roles and self.topLevelObject(obj) == obj.parent:
            msg = "GECKO: %s is suspected to be off screen object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def isLayoutOnly(self, obj):
        if super().isLayoutOnly(obj):
            return True

        if obj.getRole() == pyatspi.ROLE_TOOL_BAR and obj.childCount:
            return obj[0] and obj[0].getRole() == pyatspi.ROLE_PAGE_TAB_LIST

        return False

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False):
        if super().isSameObject(obj1, obj2, comparePaths, ignoreNames):
            return True
        try:
            role1 = obj1.getRole()
            role2 = obj2.getRole()
        except:
            msg = "GECKO: Exception getting role for %s and %s" % (obj1, obj2)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        roles = self._topLevelRoles()
        if not (role1 in roles and role2 in roles):
            return False

        try:
            name1 = obj1.name
            name2 = obj2.name
        except:
            msg = "GECKO: Exception getting name for %s and %s" % (obj1, obj2)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = name1 == name2
        msg = "GECKO: Treating %s and %s as same object: %s" % (obj1, obj2, rv)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def isOnScreen(self, obj, boundingbox=None):
        if not super().isOnScreen(obj, boundingbox):
            return False
        if obj.getRole() != pyatspi.ROLE_UNKNOWN:
            return True

        if self.topLevelObject(obj) == obj.parent:
            msg = "INFO: %s is suspected to be off screen object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def getOnScreenObjects(self, root, extents=None):
        objects = super().getOnScreenObjects(root, extents)

        # For things like Thunderbird's "Select columns to display" button
        if root.getRole() == pyatspi.ROLE_TREE_TABLE and root.childCount:
            isExtra = lambda x: x and x.getRole() != pyatspi.ROLE_COLUMN_HEADER
            objects.extend([x for x in root[0] if isExtra(x)])

        return objects

    def isEditableMessage(self, obj):
        """Returns True if this is an editable message."""

        if not obj:
            return False

        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        if self.isDocument(obj):
            msg = "GECKO: %s is believed to be an editable message" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        document = self.getContainingDocument(obj)
        if document and document.getState().contains(pyatspi.STATE_EDITABLE):
            msg = "GECKO: %s is in an editable document: %s" % (obj, document)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "GECKO: Editable %s not in an editable document" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def isNotRealDocument(self, obj):
        try:
            name = obj.name
        except:
            msg = "GECKO: Exception getting name for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if name.startswith("moz-extension"):
            return True

        if "self-repair.mozilla.org" in name:
            return True

        uri = self.documentFrameURI(obj)
        if uri.startswith("moz-extension"):
            return True

        if not uri and "pixels" in name:
            return True

        return False

    def _objectMightBeBogus(self, obj):
        if not obj:
            return False

        if obj.getRole() == pyatspi.ROLE_SECTION and obj.parent.getRole() == pyatspi.ROLE_FRAME:
            msg = "GECKO: %s is believed to be a bogus object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def canBeActiveWindow(self, window, clearCache=False):
        # We apparently having missing events from Gecko requiring
        # we update the cache. This is not performant. :(
        return super().canBeActiveWindow(window, True)

    def treatAsEntry(self, obj):
        if not obj or self.inDocumentContent(obj):
            return super().treatAsEntry(obj)

        # Firefox seems to have turned its accessible location widget into a
        # childless editable combobox.

        try:
            role = obj.getRole()
            state = obj.getState()
            childCount = obj.childCount
        except:
            msg = "GECKO: Exception getting role, state, and child count for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role != pyatspi.ROLE_COMBO_BOX:
            return False

        if not state.contains(pyatspi.STATE_FOCUSED):
            return False

        if childCount:
            return False

        if not "EditableText" in pyatspi.listInterfaces(obj):
            return False

        msg = "GECKO: Treating %s as entry" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return True

    def _isQuickFind(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if obj.getRole() != pyatspi.ROLE_TOOL_BAR:
            return False

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        isEntry = lambda x: x.getRole() == pyatspi.ROLE_ENTRY
        if len(self.findAllDescendants(obj, isEntry)) != 1:
            msg = "GECKO: %s not believed to be quick-find container (entry count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isButton = lambda x: x.getRole() == pyatspi.ROLE_PUSH_BUTTON
        if len(self.findAllDescendants(obj, isButton)) != 1:
            msg = "GECKO: %s not believed to be quick-find container (button count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = "GECKO: %s believed to be quick-find container (accessibility tree)" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        self._findContainer = obj
        return True

    def isFindContainer(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if obj.getRole() != pyatspi.ROLE_TOOL_BAR:
            return False

        result = self.getFindResultsCount(obj)
        if result:
            msg = "GECKO: %s believed to be find-in-page container (%s)" % (obj, result)
            debug.println(debug.LEVEL_INFO, msg, True)
            self._findContainer = obj
            return True

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        isEntry = lambda x: x.getRole() == pyatspi.ROLE_ENTRY
        if len(self.findAllDescendants(obj, isEntry)) != 1:
            msg = "GECKO: %s not believed to be find-in-page container (entry count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isButton = lambda x: x.getRole() == pyatspi.ROLE_PUSH_BUTTON
        if len(self.findAllDescendants(obj, isButton)) < 5:
            msg = "GECKO: %s not believed to be find-in-page container (button count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = "GECKO: %s believed to be find-in-page container (accessibility tree)" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        self._findContainer = obj
        return True

    def inFindContainer(self, obj=None):
        if not obj:
            obj = orca_state.locusOfFocus

        if not obj or self.inDocumentContent(obj):
            return False

        if obj.getRole() not in [pyatspi.ROLE_ENTRY, pyatspi.ROLE_PUSH_BUTTON]:
            return False

        isToolbar = lambda x: x and x.getRole() == pyatspi.ROLE_TOOL_BAR
        toolbar = pyatspi.findAncestor(obj, isToolbar)
        result = self.isFindContainer(toolbar)
        if result:
            msg = "GECKO: %s believed to be find-in-page widget (toolbar)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._isQuickFind(toolbar):
            msg = "GECKO: %s believed to be find-in-page widget (quick find)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def getFindResultsCount(self, root=None):
        root = root or self._findContainer
        if not root:
            return ""

        isMatch = lambda x: x and x.getRole() == pyatspi.ROLE_LABEL \
            and len(re.findall("\d+", x.name)) == 2

        labels = self.findAllDescendants(root, isMatch)
        if len(labels) != 1:
            return ""

        label = labels[0]
        label.clearCache()
        return label.name

    def isAutoTextEvent(self, event):
        if not super().isAutoTextEvent(event):
            return False

        if self.inDocumentContent(event.source):
            return True

        if self.treatAsDuplicateEvent(self._lastAutoTextObjectEvent, event) \
           and time.time() - self._lastAutoTextEventTime < 0.5 \
           and orca_state.lastInputEvent.isReleaseFor(self._lastAutoTextInputEvent):
            msg = "GECKO: Event believed to be duplicate auto text event."
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        self._lastAutoTextObjectEvent = event
        self._lastAutoTextInputEvent = orca_state.lastInputEvent
        self._lastAutoTextEventTime = time.time()
        return True
