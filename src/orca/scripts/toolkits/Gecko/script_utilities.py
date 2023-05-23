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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import re
import time

from orca import debug
from orca import orca_state
from orca.scripts import web
from orca.ax_object import AXObject


class Utilities(web.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._lastAutoTextObjectEvent = None
        self._lastAutoTextInputEvent = None
        self._lastAutoTextEventTime = 0

    def _attemptBrokenTextRecovery(self, obj, **args):
        boundary = args.get('boundary')

        # Gecko fails to implement this boundary type.
        if boundary == Atspi.TextBoundaryType.SENTENCE_START:
            return True

        if self.isContentEditableWithEmbeddedObjects(obj):
            return boundary == Atspi.TextBoundaryType.WORD_START

        return True

    def _treatAsLeafNode(self, obj):
        if AXObject.get_role(obj) == Atspi.Role.TABLE_ROW:
            return not AXObject.get_child_count(obj)

        return super()._treatAsLeafNode(obj)

    def containsPoint(self, obj, x, y, coordType, margin=2):
        if not super().containsPoint(obj, x, y, coordType, margin):
            return False

        roles = [Atspi.Role.MENU, Atspi.Role.TOOL_TIP]
        if AXObject.get_role(obj) in roles and self.topLevelObject(obj) == AXObject.get_parent(obj):
            msg = "GECKO: %s is suspected to be off screen object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def isLayoutOnly(self, obj):
        if super().isLayoutOnly(obj):
            return True

        if AXObject.get_role(obj) == Atspi.Role.TOOL_BAR and AXObject.get_child_count(obj):
            child = AXObject.get_child(obj, 0)
            return AXObject.get_role(child) == Atspi.Role.PAGE_TAB_LIST

        return False

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False):
        if super().isSameObject(obj1, obj2, comparePaths, ignoreNames):
            return True

        role1 = AXObject.get_role(obj1)
        role2 = AXObject.get_role(obj2)
        roles = self._topLevelRoles()
        if not (role1 in roles and role2 in roles):
            return False

        name1 = AXObject.get_name(obj1)
        name2 = AXObject.get_name(obj2)
        rv = name1 == name2
        msg = "GECKO: Treating %s and %s as same object: %s" % (obj1, obj2, rv)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def isOnScreen(self, obj, boundingbox=None):
        if not super().isOnScreen(obj, boundingbox):
            return False
        if AXObject.get_role(obj) != Atspi.Role.UNKNOWN:
            return True

        if self.topLevelObject(obj) == AXObject.get_parent(obj):
            msg = "INFO: %s is suspected to be off screen object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def getOnScreenObjects(self, root, extents=None):
        objects = super().getOnScreenObjects(root, extents)

        # For things like Thunderbird's "Select columns to display" button
        if AXObject.get_role(root) == Atspi.Role.TREE_TABLE and AXObject.get_child_count(root):
            isExtra = lambda x: x and AXObject.get_role(x) != Atspi.Role.COLUMN_HEADER
            child = AXObject.get_child(root, 0)
            objects.extend([x for x in AXObject.iter_children(child, isExtra)])

        return objects

    def isEditableMessage(self, obj):
        """Returns True if this is an editable message."""

        if not obj:
            return False

        if not obj.getState().contains(Atspi.StateType.EDITABLE):
            return False

        document = self.getDocumentForObject(obj)
        if document and document.getState().contains(Atspi.StateType.EDITABLE):
            msg = "GECKO: %s is in an editable document: %s" % (obj, document)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "GECKO: Editable %s not in an editable document" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def isNotRealDocument(self, obj):
        name = AXObject.get_name(obj)
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

        if AXObject.get_role(obj) == Atspi.Role.SECTION \
            and AXObject.get_role(AXObject.get_parent(obj)) == Atspi.Role.FRAME:
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
        role = AXObject.get_role(obj)
        if role != Atspi.Role.COMBO_BOX:
            return False

        try:
            state = obj.getState()
            childCount = AXObject.get_child_count(obj)
        except:
            msg = "GECKO: Exception getting state and child count for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not state.contains(Atspi.StateType.FOCUSED):
            return False

        if childCount:
            return False

        if not AXObject.supports_editable_text(obj):
            return False

        msg = "GECKO: Treating %s as entry" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return True

    def _isQuickFind(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if AXObject.get_role(obj) != Atspi.Role.TOOL_BAR:
            return False

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        isEntry = lambda x: AXObject.get_role(x) == Atspi.Role.ENTRY
        if len(self.findAllDescendants(obj, isEntry)) != 1:
            msg = "GECKO: %s not believed to be quick-find container (entry count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isButton = lambda x: AXObject.get_role(x) == Atspi.Role.PUSH_BUTTON
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

        if AXObject.get_role(obj) != Atspi.Role.TOOL_BAR:
            return False

        result = self.getFindResultsCount(obj)
        if result:
            msg = "GECKO: %s believed to be find-in-page container (%s)" % (obj, result)
            debug.println(debug.LEVEL_INFO, msg, True)
            self._findContainer = obj
            return True

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        isEntry = lambda x: AXObject.get_role(x) == Atspi.Role.ENTRY
        if len(self.findAllDescendants(obj, isEntry)) != 1:
            msg = "GECKO: %s not believed to be find-in-page container (entry count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isButton = lambda x: AXObject.get_role(x) == Atspi.Role.PUSH_BUTTON
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

        if AXObject.get_role(obj) not in [Atspi.Role.ENTRY, Atspi.Role.PUSH_BUTTON]:
            return False

        isToolbar = lambda x: x and AXObject.get_role(x) == Atspi.Role.TOOL_BAR
        toolbar = AXObject.find_ancestor(obj, isToolbar)
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

        isMatch = lambda x: x and AXObject.get_role(x) == Atspi.Role.LABEL \
            and len(re.findall("\d+", AXObject.get_name(x))) == 2

        labels = self.findAllDescendants(root, isMatch)
        if len(labels) != 1:
            return ""

        label = labels[0]
        label.clearCache()
        return AXObject.get_name(label)

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

    def localizeTextAttribute(self, key, value):
        value = value.replace("-moz-", "")
        return super().localizeTextAttribute(key, value)

    def unrelatedLabels(self, root, onlyShowing=True, minimumWords=3):
        return super().unrelatedLabels(root, onlyShowing, minimumWords=1)

    def _shouldUseTableCellInterfaceForCoordinates(self):
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1794100
        return False
