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
from orca import focus_manager
from orca import orca_state
from orca.scripts import web
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


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
        if AXUtilities.is_table_row(obj):
            return not AXObject.get_child_count(obj)

        return super()._treatAsLeafNode(obj)

    def containsPoint(self, obj, x, y, coordType, margin=2):
        if not super().containsPoint(obj, x, y, coordType, margin):
            return False

        if (AXUtilities.is_menu(obj) or AXUtilities.is_tool_tip(obj)) \
           and self.topLevelObject(obj) == AXObject.get_parent(obj):
            tokens = ["GECKO:", obj, "is suspected to be off screen object"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        return True

    def isLayoutOnly(self, obj):
        if super().isLayoutOnly(obj):
            return True

        if AXUtilities.is_tool_bar(obj) and AXObject.get_child_count(obj):
            return AXUtilities.is_page_tab_list(AXObject.get_child(obj, 0))

        return False

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False,
                     ignoreDescriptions=True):
        if super().isSameObject(obj1, obj2, comparePaths, ignoreNames, ignoreDescriptions):
            return True

        roles = self._topLevelRoles()
        if not (AXObject.get_role(obj1) in roles and AXObject.get_role(obj2) in roles):
            return False

        rv = AXObject.get_name(obj1) == AXObject.get_name(obj2)
        tokens = ["GECKO: Treating", obj1, "and", obj2, "as same object:", rv]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def isOnScreen(self, obj, boundingbox=None):
        if not super().isOnScreen(obj, boundingbox):
            return False
        if not AXUtilities.is_unknown(obj):
            return True

        if self.topLevelObject(obj) == AXObject.get_parent(obj):
            tokens = ["INFO:", obj, "is suspected to be off screen object"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        return True

    def getOnScreenObjects(self, root, extents=None):
        objects = super().getOnScreenObjects(root, extents)

        # For things like Thunderbird's "Select columns to display" button
        if AXUtilities.is_tree_table(root) and AXObject.get_child_count(root):

            def isExtra(x):
                return not AXUtilities.is_column_header(x)

            child = AXObject.get_child(root, 0)
            objects.extend([x for x in AXObject.iter_children(child, isExtra)])

        return objects

    def isEditableMessage(self, obj):
        """Returns True if this is an editable message."""

        if not AXUtilities.is_editable(obj):
            return False

        document = self.getDocumentForObject(obj)
        if AXUtilities.is_editable(document):
            tokens = ["GECKO:", obj, "is in an editable document:", document]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["GECKO: Editable", obj, "not in an editable document"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
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
        if AXUtilities.is_section(obj) and AXUtilities.is_frame(AXObject.get_parent(obj)):
            tokens = ["GECKO:", obj, "is believed to be a bogus object"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def treatAsEntry(self, obj):
        if not obj or self.inDocumentContent(obj):
            return super().treatAsEntry(obj)

        # Firefox seems to have turned its accessible location widget into a
        # childless editable combobox.
        if not AXUtilities.is_combo_box(obj):
            return False

        if AXObject.get_child_count(obj):
            return False

        if not AXUtilities.is_focused(obj):
            return False

        if not AXObject.supports_editable_text(obj):
            return False

        tokens = ["GECKO: Treating", obj, "as entry"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return True

    def _isQuickFind(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if not AXUtilities.is_tool_bar(obj):
            return False

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        if len(AXUtilities.find_all_entries(obj)) != 1:
            tokens = ["GECKO:", obj, "not believed to be quick-find container (entry count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_push_buttons(obj)) != 1:
            tokens = ["GECKO:", obj, "not believed to be quick-find container (button count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["GECKO:", obj, "believed to be quick-find container (accessibility tree)"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self._findContainer = obj
        return True

    def isFindContainer(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if not AXUtilities.is_tool_bar(obj):
            return False

        result = self.getFindResultsCount(obj)
        if result:
            tokens = ["GECKO:", obj, "believed to be find-in-page container (", result, ")"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self._findContainer = obj
            return True

        # TODO: This would be far easier if Gecko gave us an object attribute to look for....

        if len(AXUtilities.find_all_entries(obj)) != 1:
            tokens = ["GECKO:", obj, "not believed to be find-in-page container (entry count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_push_buttons(obj)) < 5:
            tokens = ["GECKO:", obj, "not believed to be find-in-page container (button count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["GECKO:", obj, "believed to be find-in-page container (accessibility tree)"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self._findContainer = obj
        return True

    def inFindContainer(self, obj=None):
        if not obj:
            obj = focus_manager.getManager().get_locus_of_focus()

        if not obj or self.inDocumentContent(obj):
            return False

        if not (AXUtilities.is_entry(obj) or AXUtilities.is_push_button(obj)):
            return False

        toolbar = AXObject.find_ancestor(obj, AXUtilities.is_tool_bar)
        result = self.isFindContainer(toolbar)
        if result:
            tokens = ["GECKO:", obj, "believed to be find-in-page widget (toolbar)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self._isQuickFind(toolbar):
            tokens = ["GECKO:", obj, "believed to be find-in-page widget (quick find)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def getFindResultsCount(self, root=None):
        root = root or self._findContainer
        if not root:
            return ""

        def isMatch(x):
            return len(re.findall(r"\d+", AXObject.get_name(x))) == 2

        labels = AXUtilities.find_all_labels(root, isMatch)
        if len(labels) != 1:
            return ""

        label = labels[0]
        AXObject.clear_cache(label, False, "Ensuring we have correct name for find results.")
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
            debug.printMessage(debug.LEVEL_INFO, msg, True)
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
