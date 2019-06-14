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

    def isStaticTextLeaf(self, obj, checkSiblings=True):
        if not (obj and self.inDocumentContent(obj)):
            return super().isStaticTextLeaf(obj)

        rv = self._isStaticTextLeaf.get(hash(obj))
        if rv is not None:
            return rv

        rv = obj.getRole() == pyatspi.ROLE_TEXT and self._getTag(obj) in (None, "br")
        if rv:
            msg = "CHROMIUM: %s believed to be static text leaf" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        if rv and obj.parent:
            if self.isDocument(obj.parent):
                msg = "CHROMIUM: %s is direct child of document so ignore leaf finding" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = False
            elif checkSiblings:
                i = obj.getIndexInParent()
                if i > 0 and not self.isStaticTextLeaf(obj.parent[i - 1], False) \
                   and not self.isListItemMarker(obj.parent[0]):
                    msg = "CHROMIUM: previous sibling of %s is not leaf so ignore leaf finding" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)
                    rv = False
                elif i + 1 < obj.parent.childCount and not self.isStaticTextLeaf(obj.parent[i + 1], False):
                    msg = "CHROMIUM: next sibling of %s is not leaf so ignore leaf finding" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)
                    rv = False

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

        rv = obj.getRole() == pyatspi.ROLE_STATIC and not self._getTag(obj) \
            and obj.parent.getRole() == pyatspi.ROLE_LIST_ITEM \
            and obj.getIndexInParent() == 0

        self._isListItemMarker[hash(obj)] = rv
        return rv

    def getListItemMarkerText(self, obj):
        if obj.getRole() != pyatspi.ROLE_LIST_ITEM:
            return ""

        listItemMarker = pyatspi.findDescendant(obj, self.isListItemMarker)
        if listItemMarker:
            return listItemMarker.name

        return ""

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

    def topLevelObject(self, obj):
        if not obj:
            return None

        result = super().topLevelObject(obj)
        if result and result.getRole() in self._topLevelRoles():
            return result

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
