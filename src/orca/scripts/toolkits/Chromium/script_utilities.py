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

        if AXObject.get_child_count(obj):
            return False

        if self.isListItemMarker(obj):
            return False

        rv = self._isStaticTextLeaf.get(hash(obj))
        if rv is not None:
            return rv

        roles = [Atspi.Role.STATIC, Atspi.Role.TEXT]
        rv = AXObject.get_role(obj) in roles and self._getTag(obj) in (None, "br")
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
        parent = AXObject.get_parent(obj)
        if parent and AXObject.get_role(parent) == Atspi.Role.LIST_ITEM:
            tag = self._getTag(obj)
            if tag == "::marker":
                rv = True
            elif tag is not None:
                rv = False
            elif AXObject.get_child_count(parent) > 1:
                rv = AXObject.get_child(parent, 0) == obj
            else:
                rv = AXObject.get_name(obj) != self.displayedText(parent)

        self._isListItemMarker[hash(obj)] = rv
        return rv

    def isMenuInCollapsedSelectElement(self, obj):
        if AXObject.get_role(obj) != Atspi.Role.MENU:
            return False

        parent = AXObject.get_parent(obj)
        if self._getTag(parent) != 'select':
            return False

        return not AXObject.has_state(parent, Atspi.StateType.EXPANDED)

    def treatAsMenu(self, obj):
        # Unlike other apps and toolkits, submenus in Chromium have the menu item
        # role rather than the menu role, but we can identify them as submenus via
        # the has-popup state.
        if AXObject.get_role(obj) == Atspi.Role.MENU_ITEM:
            return AXObject.has_state(obj, Atspi.StateType.HAS_POPUP)

        return False

    def isPopupMenuForCurrentItem(self, obj):
        # When a submenu is closed, it has role menu item. But when that submenu
        # is opened/expanded, a menu with that same name appears. It would be
        # nice if there were a connection (parent/child or an accessible relation)
        # between the two....
        if not self.treatAsMenu(orca_state.locusOfFocus):
            return False

        return super().isPopupMenuForCurrentItem(obj)

    def isFrameForPopupMenu(self, obj):
        # The ancestry of a popup menu appears to be a menu bar (even though
        # one is not actually showing) contained in a nameless frame. It would
        # be nice if these things were pruned from the accessibility tree....
        if AXObject.get_role(obj) != Atspi.Role.FRAME:
            return False
        if AXObject.get_name(obj):
            return False
        if AXObject.get_child_count(obj) != 1:
            return False
        if AXObject.get_role(AXObject.get_child(obj, 0)) == Atspi.Role.MENU_BAR:
            return True

        return False

    def isTopLevelMenu(self, obj):
        if AXObject.get_role(obj) == Atspi.Role.MENU:
            return self.isFrameForPopupMenu(self.topLevelObject(obj))

        return False

    def popupMenuForFrame(self, obj):
        if not self.isFrameForPopupMenu(obj):
            return None

        menu = AXObject.find_descendant(obj, lambda x: x and AXObject.get_role(x) == Atspi.Role.MENU)
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
        if result and AXObject.get_role(result) in self._topLevelRoles():
            if not self.isFindContainer(result):
                return result
            else:
                parent = AXObject.get_parent(result)
                msg = "CHROMIUM: Top level object for %s is %s" % (obj, parent)
                debug.println(debug.LEVEL_INFO, msg, True)
                return parent

        cached = self._topLevelObject.get(hash(obj))
        if cached is not None:
            return cached

        msg = "CHROMIUM: WARNING: Top level object for %s is %s" % (obj, result)
        debug.println(debug.LEVEL_INFO, msg, True)

        # The only (known) object giving us a broken ancestry is the omnibox popup.
        roles = [Atspi.Role.LIST_ITEM, Atspi.Role.LIST_BOX]
        if not (obj and AXObject.get_role(obj) in roles):
            return result

        listbox = obj
        if AXObject.get_role(obj) == Atspi.Role.LIST_ITEM:
            listbox = AXObject.get_parent(listbox)

        if not listbox:
            return result

        # The listbox sometimes claims to be a redundant object rather than a listbox.
        # Clearing the AT-SPI2 cache seems to be the trigger.
        if not (listbox and AXObject.get_role(listbox) in roles):
            if AXObject.get_role(listbox) == Atspi.Role.REDUNDANT_OBJECT:
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
        relation = AXObject.get_relation(obj, Atspi.RelationType.POPUP_FOR)
        if not relation:
            return None

        target = relation.get_target(0)
        if AXObject.get_role(target) == Atspi.Role.AUTOCOMPLETE:
            return target

        return None

    def isBrowserAutocompletePopup(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        return self.autocompleteForPopup(obj) is not None

    def isRedundantAutocompleteEvent(self, event):
        if AXObject.get_role(event.source) != Atspi.Role.AUTOCOMPLETE:
            return False

        if event.type.startswith("object:text-caret-moved"):
            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey in ["Down", "Up"]:
                return True

        return False

    def setCaretPosition(self, obj, offset, documentFrame=None):
        super().setCaretPosition(obj, offset, documentFrame)

        isLink = lambda x: x and AXObject.get_role(x) == Atspi.Role.LINK
        link = AXObject.find_ancestor(obj, isLink)
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

        if AXObject.get_role(event.any_data) == Atspi.Role.TABLE:
            return True

        msg = "CHROMIUM: Event is believed to be redundant live region notification"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def getFindResultsCount(self, root=None):
        root = root or self._findContainer
        if not root:
            return ""

        isMatch = lambda x: x and AXObject.get_role(x) == Atspi.Role.STATUS_BAR
        statusBars = self.findAllDescendants(root, isMatch)
        if len(statusBars) != 1:
            return ""

        bar = statusBars[0]
        AXObject.clear_cache(bar)
        if len(re.findall("\d+", AXObject.get_name(bar))) == 2:
            return AXObject.get_name(bar)

        return ""

    def isFindContainer(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if AXObject.get_role(obj) != Atspi.Role.DIALOG:
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

        isEntry = lambda x: AXObject.get_role(x) == Atspi.Role.ENTRY
        if len(self.findAllDescendants(obj, isEntry)) != 1:
            msg = "CHROMIUM: %s not believed to be find-in-page container (entry count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isButton = lambda x: AXObject.get_role(x) == Atspi.Role.PUSH_BUTTON
        if len(self.findAllDescendants(obj, isButton)) != 3:
            msg = "CHROMIUM: %s not believed to be find-in-page container (button count)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        isSeparator = lambda x: AXObject.get_role(x) == Atspi.Role.SEPARATOR
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

        if AXObject.get_role(obj) not in [Atspi.Role.ENTRY, Atspi.Role.PUSH_BUTTON]:
            return False

        isDialog = lambda x: x and AXObject.get_role(x) == Atspi.Role.DIALOG
        result = self.isFindContainer(AXObject.find_ancestor(obj, isDialog))
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

    def accessibleAtPoint(self, root, x, y, coordType=None):
        result = super().accessibleAtPoint(root, x, y, coordType)

        # Chromium cannot do a hit test of web content synchronously. So what it
        # does is return a guess, then fire off an async hit test. The next time
        # one calls it, Chromium returns the previous async hit test result if
        # the point is still within its bounds. Therefore, we need to call
        # accessibleAtPoint() twice to be safe.
        msg = "CHROMIUM: Getting accessibleAtPoint again due to async hit test result."
        debug.println(debug.LEVEL_INFO, msg, True)
        result = super().accessibleAtPoint(root, x, y, coordType)
        return result

    def _isActiveAndShowingAndNotIconified(self, obj):
        if super()._isActiveAndShowingAndNotIconified(obj):
            return True

        if obj and AXObject.get_application(obj) != self._script.app:
            return False

        # FIXME: This can potentially be non-performant because AT-SPI2 will recursively
        # clear the cache of all descendants. This is an attempt to work around what may
        # be a lack of window:activate and object:state-changed events from Chromium
        # windows in at least some environments.
        try:
            msg = "CHROMIUM: Clearing cache for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            AXObject.clear_cache(obj)
        except:
            msg = "CHROMIUM: Exception clearing cache for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if super()._isActiveAndShowingAndNotIconified(obj):
            msg = "CHROMIUM: %s deemed to be active and showing after cache clear" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _shouldCalculatePositionAndSetSize(self, obj):
        # Chromium calculates posinset and setsize for description lists based on the
        # number of terms present. If we want to present the number of values associated
        # with a given term, we need to work those values out ourselves.
        if self.isDescriptionListDescription(obj):
            return True

        # Chromium has accessible menu items which are not focusable and therefore do not
        # have a posinset and setsize calculated. But they may claim to be the selected
        # item when an accessible child is selected (e.g. "zoom" when "+" or "-" gains focus.
        # Normally we calculate posinset and setsize when the application hasn't provided it.
        # We don't want to do that in the case of menu items like "zoom" because our result
        # will not jibe with the values of its siblings. Thus if a sibling has a value,
        # assume that the missing attributes are missing on purpose.
        for sibling in AXObject.iter_children(AXObject.get_parent(obj)):
            if self.getPositionInSet(sibling) is not None:
                msg = "CHROMIUM: %s's sibling %s has posinset." % (obj, sibling)
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

        return True
