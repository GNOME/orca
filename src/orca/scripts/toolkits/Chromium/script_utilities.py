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

"""Custom script utilities for Chromium"""

# Please note: ATK support in Chromium needs much work. Until that work has been
# done, Orca will not be able to provide access to Chromium. These utilities are
# a work in progress.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import time

from orca import debug
from orca import orca_state
from orca.scripts import web


class Utilities(web.Utilities):

    def __init__(self, script):
        super().__init__(script)
        self._documentsEmbeddedBy = {} # Needed for HACK

    def clearCachedObjects(self):
        super().clearCachedObjects()
        self._documentsEmbeddedBy = {} # Needed for HACK

    def _getDocumentsEmbeddedBy(self, frame):
        result = super()._getDocumentsEmbeddedBy(frame)
        if result:
            return result

        # HACK: This tree dive is not efficient and should be removed once Chromium
        # implements support for the embeds/embedded-by relation pair.
        cached = self._documentsEmbeddedBy.get(hash(frame), [])
        result = list(filter(self.isShowingAndVisible, cached))
        if not result:
            def _include(x):
                if x and x.getRole() == pyatspi.ROLE_DOCUMENT_WEB:
                    return self.isShowingAndVisible(x)
                return False

            def _exclude(x):
                roles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_INTERNAL_FRAME]
                if not x or x.getRole() in roles:
                    return True
                return False

            startTime = time.time()
            result = self.findAllDescendants(frame, _include, _exclude)
            msg = "CHROMIUM: NO EMBEDDED RELATION HACK - %.4fs" % (time.time()-startTime)
            debug.println(debug.LEVEL_INFO, msg, True)

        self._documentsEmbeddedBy[hash(frame)] = result
        return result

    def isZombie(self, obj):
        if not super().isZombie(obj):
            return False

        # Things (so far) seem to work as expected for document content -- except the
        # document frame itself.
        if not self.isDocument(obj) and self.inDocumentContent(obj):
            return True

        # HACK for other items, including (though possibly not limited to) menu items
        # (e.g. when you press Alt+F and arrow) and the location bar popup.
        try:
            index = obj.getIndexInParent()
        except:
            msg = "CHROMIUM: Exception getting index in parent for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if index == -1 and self.isShowingAndVisible(obj):
            msg = "CHROMIUM: INDEX IN PARENT OF -1 HACK: Ignoring bad index of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def selectedChildCount(self, obj):
        count = super().selectedChildCount(obj)
        if count or "Selection" in pyatspi.listInterfaces(obj):
            return count

        # HACK: Ideally, we'd use the selection interface to get the selected
        # child count. But that interface is not implemented yet. This hackaround
        # is extremely non-performant.
        for child in obj:
            if child.getState().contains(pyatspi.STATE_SELECTED):
                count += 1

        msg = "CHROMIUM: NO SELECTION INTERFACE HACK: Selected children: %i" % count
        debug.println(debug.LEVEL_INFO, msg, True)
        return count

    def selectedChildren(self, obj):
        result = super().selectedChildren(obj)
        if result or "Selection" in pyatspi.listInterfaces(obj):
            return result

        # HACK: Ideally, we'd use the selection interface to get the selected
        # children. But that interface is not implemented yet. This hackaround
        # is extremely non-performant.
        for child in obj:
            if child.getState().contains(pyatspi.STATE_SELECTED):
                result.append(child)

        return result

    def isMenuWithNoSelectedChild(self, obj):
        if not obj:
            return False

        try:
            role = obj.getRole()
        except:
            msg = "CHROMIUM: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role != pyatspi.ROLE_MENU:
            return False

        return not self.selectedChildCount(obj)

    def _isFrameContainerForBrowserUIPopUp(self, frame):
        if not frame or self.isDead(frame):
            return False

        # So far, the frame containers which lack the active state also lack names.
        # Tree diving can be expensive....
        if frame.name:
            return False

        roles = [pyatspi.ROLE_LIST_BOX, pyatspi.ROLE_MENU]
        try:
            child = pyatspi.findDescendant(frame, lambda x: x and x.getRole() in roles)
        except:
            msg = "CHROMIUM: Exception finding descendant of %s" % frame
            debug.println(debug.LEVEL_INFO, msg, True)
            child = None

        return child and not self.inDocumentContent(child)

    def canBeActiveWindow(self, window, clearCache=False):
        if super().canBeActiveWindow(window, clearCache):
            return True

        if window and window.toolkitName != "Chromium":
            return False

        # HACK: Remove this once Chromium adds active state to popup frames.
        startTime = time.time()
        result = self._isFrameContainerForBrowserUIPopUp(window)
        msg = "CHROMIUM: _isFrameContainerForBrowser() - %.4fs" % (time.time()-startTime)
        debug.println(debug.LEVEL_INFO, msg, True)

        if result:
            msg = "CHROMIUM: POPUP MISSING STATE ACTIVE HACK: %s can be active window" % window
            debug.println(debug.LEVEL_INFO, msg, True)

        return result

    def treatAsMenu(self, obj):
        if not obj:
            return False

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "CHROMIUM: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        # Unlike other apps and toolkits, submenus in Chromium have the menu item
        # role rather than the menu role, but we can identify them as submenus via
        # the has-popup state.
        if role == pyatspi.ROLE_MENU_ITEM:
            return state.contains(pyatspi.STATE_HAS_POPUP)

        return False

    def isPopupMenuForCurrentItem(self, obj):
        # When a submenu is closed, it has role menu item. But when that submenu
        # is opened/expanded, a menu with that same name appears. It would be
        # nice if there were a connection (parent/child or an accessible relation)
        # between the two....
        if not self.treatAsMenu(orca_state.locusOfFocus):
            return False

        if obj.name and obj.name == orca_state.locusOfFocus.name:
            return obj.getRole() == pyatspi.ROLE_MENU

        return False

    def isFrameForPopupMenu(self, obj):
        try:
            name = obj.name
            role = obj.getRole()
            childCount = obj.childCount
        except:
            msg = "CHROMIUM: Exception getting properties of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        # The ancestry of a popup menu appears to be a menu bar (even though
        # one is not actually showing) contained in a nameless frame. It would
        # be nice if these things were pruned from the accessibility tree....
        if name or role != pyatspi.ROLE_FRAME or childCount != 1:
            return False

        if obj[0].getRole() == pyatspi.ROLE_MENU_BAR:
            return True

        return False

    def popupMenuForFrame(self, obj):
        if not self.isFrameForPopupMenu(obj):
            return None

        try:
            menu = pyatspi.findDescendant(obj, lambda x: x and x.getRole() == pyatspi.ROLE_MENU)
        except:
            msg = "CHROMIUM: Exception finding descendant of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        msg = "CHROMIUM: HACK: Popup menu for %s: %s" % (obj, menu)
        debug.println(debug.LEVEL_INFO, msg, True)
        return menu

    def grabFocusWhenSettingCaret(self, obj):
        # HACK: Remove this when setting the caret updates focus.
        msg = "CHROMIUM: HACK: Doing focus grab when setting caret on %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return True

    def topLevelObject(self, obj):
        # HACK: Remove this once we can ascend ancestry and get top level
        # object from within web content.
        topLevel = super().topLevelObject(obj)
        if not topLevel or topLevel.getRole() in self._topLevelRoles():
            return topLevel

        msg = "CHROMIUM: ERROR: Top level object for %s is %s" % (obj, topLevel)
        debug.println(debug.LEVEL_INFO, msg, True)

        if self.isDocument(topLevel) and orca_state.activeWindow \
           and orca_state.activeWindow.getApplication() == self._script.app:
            startTime = time.time()
            descendant = pyatspi.findDescendant(orca_state.activeWindow, lambda x: x == topLevel)
            msg = "CHROMIUM: findDescendant() - %.4fs" % (time.time()-startTime)
            debug.println(debug.LEVEL_INFO, msg, True)
            if descendant:
                msg = "CHROMIUM: HACK: Returning %s as top level" % orca_state.activeWindow
                debug.println(debug.LEVEL_INFO, msg, True)
                return orca_state.activeWindow

        return topLevel

    def frameAndDialog(self, obj):
        # HACK: Remove this once we can ascend the ancestry.
        frame, dialog = super().frameAndDialog(obj)
        if frame or dialog:
            return frame, dialog

        frame = self.topLevelObject(obj)
        if not frame and not self.inDocumentContent(obj) \
           and self.canBeActiveWindow(orca_state.activeWindow) \
           and orca_state.activeWindow.getApplication() == self._script.app:
            frame = orca_state.activeWindow

        msg = "CHROMIUM: CAN'T ASCEND TREE HACK: Returning %s as frame" % frame
        debug.println(debug.LEVEL_INFO, msg, True)
        return frame, dialog
