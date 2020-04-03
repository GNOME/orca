# Orca
#
# Copyright 2018-2019 Igalia, S.L.
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2018-2019 Igalia, S.L."
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
        self._isStaticTextLeaf = {}
        self._isPseudoElement = {}
        self._isListItemMarker = {}
        self._topLevelObject = {}

    def clearCachedObjects(self):
        super().clearCachedObjects()
        self._isStaticTextLeaf = {}
        self._isPseudoElement = {}
        self._isListItemMarker = {}
        self._topLevelObject = {}

    def isStaticTextLeaf(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isStaticTextLeaf(obj)

        if obj.childCount:
            return False

        if self.isListItemMarker(obj):
            return False

        rv = self._isStaticTextLeaf.get(hash(obj))
        if rv is not None:
            return rv

        roles = [pyatspi.ROLE_STATIC, pyatspi.ROLE_TEXT]
        rv = obj.getRole() in roles and self._getTag(obj) in (None, "br")
        if rv:
            msg = "CHROMIUM: %s believed to be static text leaf" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        self._isStaticTextLeaf[hash(obj)] = rv
        return rv

    def isPseudoElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isPseudoElement(obj)

        rv = self._isPseudoElement.get(hash(obj))
        if rv is not None:
            return rv

        rv = self._getTag(obj) in ["<pseudo:before>", "<pseudo:after>"]
        if rv:
            msg = "CHROMIUM: %s believed to be pseudo element" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        self._isPseudoElement[hash(obj)] = rv
        return rv

    def isListItemMarker(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isListItemMarker.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if obj.parent and obj.parent.getRole() == pyatspi.ROLE_LIST_ITEM:
            rv = self._getTag(obj) in ["::marker", None] and obj.parent[0] == obj

        self._isListItemMarker[hash(obj)] = rv
        return rv

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

        try:
            childCount = obj.childCount
        except:
            msg = "CHROMIUM: Exception getting child count of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return result

        # HACK: Ideally, we'd use the selection interface to get the selected
        # children. But that interface is not implemented yet. This hackaround
        # is extremely non-performant.
        for i in range(childCount):
            child = obj[i]
            if child and child.getState().contains(pyatspi.STATE_SELECTED):
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

    def isMenuInCollapsedSelectElement(self, obj):
        try:
            role = obj.getRole()
        except:
            msg = "CHROMIUM: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role != pyatspi.ROLE_MENU or self._getTag(obj.parent) != 'select':
            return False

        try:
            parentState = obj.parent.getState()
        except:
            msg = "CHROMIUM: Exception getting state for %s" % obj.parent
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return not parentState.contains(pyatspi.STATE_EXPANDED)

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

    def isTopLevelMenu(self, obj):
        if obj.getRole() == pyatspi.ROLE_MENU:
            return self.isFrameForPopupMenu(self.topLevelObject(obj))

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

    def _getActionNames(self, obj):
        names = super()._getActionNames(obj)

        # click-ancestor is meant to bubble up to an ancestor which is actually
        # clickable. But attempting to perform this action doesn't reliably work;
        # and the clickable ancestor is what we want to click on anyway. Treating
        # this as a valid action is causing us to include otherwise ignorable
        # elements such as sections with no semantic meaning.
        if "click-ancestor" in names:
            names = list(filter(lambda x: x != "click-ancestor", names))
            msg = "CHROMIUM: Ignoring 'click-ancestor' action on %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        return names

    def topLevelObject(self, obj):
        if not obj:
            return None

        result = super().topLevelObject(obj)
        if result and result.getRole() in self._topLevelRoles():
            if not self.isFindContainer(result):
                return result
            else:
                msg = "CHROMIUM: Top level object for %s is %s" % (obj, result.parent)
                debug.println(debug.LEVEL_INFO, msg, True)
                return result.parent

        cached = self._topLevelObject.get(hash(obj))
        if cached is not None:
            return cached

        msg = "CHROMIUM: WARNING: Top level object for %s is %s" % (obj, result)
        debug.println(debug.LEVEL_INFO, msg, True)

        # The only (known) object giving us a broken ancestry is the omnibox popup.
        roles = [pyatspi.ROLE_LIST_ITEM, pyatspi.ROLE_LIST_BOX]
        if not (obj and obj.getRole() in roles):
            return result

        listbox = obj
        if obj.getRole() == pyatspi.ROLE_LIST_ITEM:
            listbox = listbox.parent

        # The listbox sometimes claims to be a redundant object rather than a listbox.
        # Clearing the AT-SPI2 cache seems to be the trigger.
        if not (listbox and listbox.getRole() in roles):
            if listbox.getRole() == pyatspi.ROLE_REDUNDANT_OBJECT:
                msg = "CHROMIUM: WARNING: Suspected bogus role on listbox %s" % listbox
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                return result

        autocomplete = self.autocompleteForPopup(listbox)
        if autocomplete:
            result = self.topLevelObject(autocomplete)
            msg = "CHROMIUM: Top level object for %s is %s" % (autocomplete, result)
            debug.println(debug.LEVEL_INFO, msg, True)

        self._topLevelObject[hash(obj)] = result
        return result

    def autocompleteForPopup(self, obj):
        popupFor = lambda r: r.getRelationType() == pyatspi.RELATION_POPUP_FOR
        relations = list(filter(popupFor, obj.getRelationSet()))
        if not relations:
            return None

        target = relations[0].getTarget(0)
        if target and target.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            return target

        return None

    def isBrowserAutocompletePopup(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        return self.autocompleteForPopup(obj) is not None

    def isRedundantAutocompleteEvent(self, event):
        if event.source.getRole() != pyatspi.ROLE_AUTOCOMPLETE:
            return False

        if event.type.startswith("object:text-caret-moved"):
            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey in ["Down", "Up"]:
                return True

        return False

    def setCaretPosition(self, obj, offset, documentFrame=None):
        super().setCaretPosition(obj, offset, documentFrame)

        isLink = lambda x: x and x.getRole() == pyatspi.ROLE_LINK
        link = pyatspi.utils.findAncestor(obj, isLink)
        if link:
            msg = "CHROMIUM: HACK: Grabbing focus on %s's ancestor %s" % (obj, link)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.grabFocus(link)

    def handleAsLiveRegion(self, event):
        if not super().handleAsLiveRegion(event):
            return False

        if not event.type.startswith("object:children-changed:add"):
            return True

        # At least some of the time, we're getting text insertion events immediately
        # followed by children-changed events to tell us that the object whose text
        # changed is now being added to the accessibility tree. Furthermore the
        # additions are not always coming to us in presentational order, whereas
        # the text changes appear to be. So most of the time, we can ignore the
        # children-changed events. Except for when we can't.

        if event.any_data.getRole() == pyatspi.ROLE_TABLE:
            return True

        msg = "CHROMIUM: Event is believed to be redundant live region notification"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def getFindResultsCount(self, root=None):
        root = root or self._findContainer
        if not root:
            return ""

        isMatch = lambda x: x and x.getRole() == pyatspi.ROLE_STATUS_BAR
        statusBars = self.findAllDescendants(root, isMatch)
        if len(statusBars) != 1:
            return ""

        bar = statusBars[0]
        bar.clearCache()
        if len(re.findall("\d+", bar.name)) == 2:
            return bar.name

        return ""

    def isFindContainer(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if obj.getRole() != pyatspi.ROLE_DIALOG:
            return False

        result = self.getFindResultsCount(obj)
        if result:
            msg = "CHROMIUM: %s believed to be find-in-page container (%s)" % (obj, result)
            debug.println(debug.LEVEL_INFO, msg, True)
            self._findContainer = obj
            return True

        # When there are no results due to the absence of a search term, the status
        # bar lacks a name. When there are no results due to lack of match, the name
        # of the status bar is "No results" (presumably localized). Therefore fall
        # back on the widgets. TODO: This would be far easier if Chromium gave us an
        # object attribute we could look for....

        isEntry = lambda x: x.getRole() == pyatspi.ROLE_ENTRY
        if len(self.findAllDescendants(obj, isEntry)) != 1:
            msg = "CHROMIUM: %s not believed to be find-in-page container (entry count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isButton = lambda x: x.getRole() == pyatspi.ROLE_PUSH_BUTTON
        if len(self.findAllDescendants(obj, isButton)) != 3:
            msg = "CHROMIUM: %s not believed to be find-in-page container (button count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isSeparator = lambda x: x.getRole() == pyatspi.ROLE_SEPARATOR
        if len(self.findAllDescendants(obj, isSeparator)) != 1:
            msg = "CHROMIUM: %s not believed to be find-in-page container (separator count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = "CHROMIUM: %s believed to be find-in-page container (accessibility tree)" % obj
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

        isDialog = lambda x: x and x.getRole() == pyatspi.ROLE_DIALOG
        result = self.isFindContainer(pyatspi.findAncestor(obj, isDialog))
        if result:
            msg = "CHROMIUM: %s believed to be find-in-page widget" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        return result

    def isHidden(self, obj):
        if not super().isHidden(obj):
            return False

        if self.isMenuInCollapsedSelectElement(obj):
            return False

        return True

    def supportsLandmarkRole(self):
        return True

    def findAllDescendants(self, root, includeIf=None, excludeIf=None):
        if not root:
            return []

        # Don't bother if the root is a 'pre' or 'code' element. Those often have
        # nothing but a TON of static text leaf nodes, which we want to ignore.
        if self._getTag(root) in ('pre', 'code'):
            msg = "CHROMIUM: Returning 0 descendants for pre/code %s" % root
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        return super().findAllDescendants(root, includeIf, excludeIf)

    def _accessibleAtPoint(self, root, x, y, coordType=None):
        if self.isHidden(root):
            return None

        try:
            component = root.queryComponent()
        except:
            msg = "CHROMIUM: Exception querying component of %s" % root
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        result = component.getAccessibleAtPoint(x, y, coordType)

        # Chromium cannot do a hit test of web content synchronously. So what it
        # does is return a guess, then fire off an async hit test. The next time
        # one calls it, Chromium returns the previous async hit test result if
        # the point is still within its bounds. Therefore, we need to call
        # getAccessibleAtPoint() twice to be safe.
        result = component.getAccessibleAtPoint(x, y, coordType)

        msg = "CHROMIUM: %s is descendant of %s at (%i, %i)" % (result, root, x, y)
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    def descendantAtPoint(self, root, x, y, coordType=None):
        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        result = None
        if self.isDocument(root):
            result = self._accessibleAtPoint(root, x, y, coordType)

        root = result or root
        result = super().descendantAtPoint(root, x, y, coordType)
        if self.isListItemMarker(result) or self.isStaticTextLeaf(result):
            return result.parent

        return result
