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

# For the "AXUtilities has no ... member"
# pylint: disable=E1101

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

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca.scripts import web
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities


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

        rv = AXUtilities.is_static(obj) or AXUtilities.is_text(obj) \
            and self._getTag(obj) in (None, "", "br")
        if rv:
            tokens = ["CHROMIUM:", obj, "believed to be static text leaf"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

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
            tokens = ["CHROMIUM:", obj, "believed to be pseudo element"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

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
        if AXUtilities.is_list_item(parent):
            tag = self._getTag(obj)
            if tag == "::marker":
                rv = True
            elif tag:
                rv = False
            elif AXObject.get_child_count(parent) > 1:
                rv = AXObject.get_child(parent, 0) == obj
            else:
                rv = AXObject.get_name(obj) != self.displayedText(parent)

        self._isListItemMarker[hash(obj)] = rv
        return rv

    def isMenuInCollapsedSelectElement(self, obj):
        if not AXUtilities.is_menu(obj):
            return False

        parent = AXObject.get_parent(obj)
        if self._getTag(parent) != 'select':
            return False

        return not AXUtilities.is_expanded(parent)

    def treatAsMenu(self, obj):
        # Unlike other apps and toolkits, submenus in Chromium have the menu item
        # role rather than the menu role, but we can identify them as submenus via
        # the has-popup state.
        return AXUtilities.is_menu_item(obj) and AXUtilities.has_popup(obj)

    def isPopupMenuForCurrentItem(self, obj):
        # When a submenu is closed, it has role menu item. But when that submenu
        # is opened/expanded, a menu with that same name appears. It would be
        # nice if there were a connection (parent/child or an accessible relation)
        # between the two....
        return self.treatAsMenu(focus_manager.get_manager().get_locus_of_focus()) \
            and super().isPopupMenuForCurrentItem(obj)

    def isFrameForPopupMenu(self, obj):
        # The ancestry of a popup menu appears to be a menu bar (even though
        # one is not actually showing) contained in a nameless frame. It would
        # be nice if these things were pruned from the accessibility tree....
        if not AXUtilities.is_frame(obj):
            return False
        if AXObject.get_name(obj):
            return False
        if AXObject.get_child_count(obj) != 1:
            return False
        return AXUtilities.is_menu_bar(AXObject.get_child(obj, 0))

    def isTopLevelMenu(self, obj):
        return AXUtilities.is_menu(obj) and self.isFrameForPopupMenu(self.topLevelObject(obj))

    def popupMenuForFrame(self, obj):
        if not self.isFrameForPopupMenu(obj):
            return None

        menu = AXObject.find_descendant(obj, AXUtilities.is_menu)
        tokens = ["CHROMIUM: Popup menu for", obj, ":", menu]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return menu

    def topLevelObject(self, obj, useFallbackSearch=False):
        if not obj:
            return None

        result = super().topLevelObject(obj)
        if AXObject.get_role(result) in self._topLevelRoles():
            if not self.isFindContainer(result):
                return result
            else:
                parent = AXObject.get_parent(result)
                tokens = ["CHROMIUM: Top level object for", obj, "is", parent]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return parent

        cached = self._topLevelObject.get(hash(obj))
        if cached is not None:
            return cached

        tokens = ["CHROMIUM: WARNING: Top level object for", obj, "is", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # The only (known) object giving us a broken ancestry is the omnibox popup.
        if not (AXUtilities.is_list_item(obj or AXUtilities.is_list_box(obj))):
            return result

        listbox = obj
        if AXUtilities.is_list_item(obj):
            listbox = AXObject.get_parent(listbox)

        if listbox is None:
            return result

        # The listbox sometimes claims to be a redundant object rather than a listbox.
        # Clearing the AT-SPI2 cache seems to be the trigger.
        if not AXUtilities.is_list_box(listbox):
            if AXUtilities.is_redundant_object(listbox):
                tokens = ["CHROMIUM: WARNING: Suspected bogus role on listbox", listbox]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
            else:
                return result

        autocomplete = self.autocompleteForPopup(listbox)
        if autocomplete:
            result = self.topLevelObject(autocomplete)
            tokens = ["CHROMIUM: Top level object for", autocomplete, "is", result]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        self._topLevelObject[hash(obj)] = result
        return result

    def autocompleteForPopup(self, obj):
        relation = AXObject.get_relation(obj, Atspi.RelationType.POPUP_FOR)
        if not relation:
            return None

        target = relation.get_target(0)
        if AXUtilities.is_autocomplete(target):
            return target

        return None

    def isBrowserAutocompletePopup(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        return self.autocompleteForPopup(obj) is not None

    def isRedundantAutocompleteEvent(self, event):
        if not AXUtilities.is_autocomplete(event.source):
            return False

        if event.type.startswith("object:text-caret-moved"):
            return input_event_manager.get_manager().last_event_was_up_or_down()

        return False

    def setCaretPosition(self, obj, offset, documentFrame=None):
        super().setCaretPosition(obj, offset, documentFrame)

        # TODO - JD: Is this hack still needed?
        link = AXObject.find_ancestor(obj, AXUtilities.is_link)
        if link is not None:
            tokens = ["CHROMIUM: HACK: Grabbing focus on", obj, "'s ancestor", link]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            AXObject.grab_focus(link)

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
        if AXUtilities.is_table(event.any_data):
            return True

        msg = "CHROMIUM: Event is believed to be redundant live region notification"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return False

    def getFindResultsCount(self, root=None):
        root = root or self._findContainer
        if not root:
            return ""

        statusBars = AXUtilities.find_all_status_bars(root)
        if len(statusBars) != 1:
            return ""

        bar = statusBars[0]
        # TODO - JD: Is this still needed?
        AXObject.clear_cache(bar, False, "Ensuring we have correct name for find results.")
        if len(re.findall(r"\d+", AXObject.get_name(bar))) == 2:
            return AXObject.get_name(bar)

        return ""

    def isFindContainer(self, obj):
        if not obj or self.inDocumentContent(obj):
            return False

        if obj == self._findContainer:
            return True

        if not AXUtilities.is_dialog(obj):
            return False

        result = self.getFindResultsCount(obj)
        if result:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page container (", result, ")"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self._findContainer = obj
            return True

        # When there are no results due to the absence of a search term, the status
        # bar lacks a name. When there are no results due to lack of match, the name
        # of the status bar is "No results" (presumably localized). Therefore fall
        # back on the widgets. TODO: This would be far easier if Chromium gave us an
        # object attribute we could look for....

        if len(AXUtilities.find_all_entries(obj)) != 1:
            tokens = ["CHROMIUM:", obj, "not believed to be find-in-page container (entry count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_push_buttons(obj)) != 3:
            tokens = ["CHROMIUM:", obj, "not believed to be find-in-page container (button count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(AXUtilities.find_all_separators(obj)) != 1:
            tokens = ["CHROMIUM:", obj,
                      "not believed to be find-in-page container (separator count)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = ["CHROMIUM:", obj, "believed to be find-in-page container (accessibility tree)"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self._findContainer = obj
        return True

    def inFindContainer(self, obj=None):
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not (AXUtilities.is_entry(obj) or AXUtilities.is_push_button(obj)):
            return False
        if self.inDocumentContent(obj):
            return False

        result = self.isFindContainer(AXObject.find_ancestor(obj, AXUtilities.is_dialog))
        if result:
            tokens = ["CHROMIUM:", obj, "believed to be find-in-page widget"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        return result

    def isHidden(self, obj):
        if not super().isHidden(obj):
            return False

        if self.isMenuInCollapsedSelectElement(obj):
            return False

        return True

    def findAllDescendants(self, root, includeIf=None, excludeIf=None):
        if not root:
            return []

        # Don't bother if the root is a 'pre' or 'code' element. Those often have
        # nothing but a TON of static text leaf nodes, which we want to ignore.
        if AXUtilities.is_code(root):
            tokens = ["CHROMIUM: Returning 0 descendants for pre/code", root]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        return super().findAllDescendants(root, includeIf, excludeIf)

    def _shouldCalculatePositionAndSetSize(self, obj):
        # Chromium calculates posinset and setsize for description lists based on the
        # number of terms present. If we want to present the number of values associated
        # with a given term, we need to work those values out ourselves.
        if AXUtilities.is_description_value(obj):
            return True

        if self.inDocumentContent(obj):
            return super()._shouldCalculatePositionAndSetSize(obj)

        # Chromium has accessible menu items which are not focusable and therefore do not
        # have a posinset and setsize calculated. But they may claim to be the selected
        # item when an accessible child is selected (e.g. "zoom" when "+" or "-" gains focus.
        # Normally we calculate posinset and setsize when the application hasn't provided it.
        # We don't want to do that in the case of menu items like "zoom" because our result
        # will not jibe with the values of its siblings. Thus if a sibling has a value,
        # assume that the missing attributes are missing on purpose.
        for sibling in AXObject.iter_children(AXObject.get_parent(obj)):
            if isinstance(AXUtilities.get_position_in_set(sibling), int):
                tokens = ["CHROMIUM:", obj, "'s sibling", sibling, "has posinset."]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return False

        return True
