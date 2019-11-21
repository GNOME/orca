# Orca
#
# Copyright (C) 2013-2014 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2013-2014 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import time

import orca.debug as debug
import orca.mouse_review as mouse_review
import orca.orca as orca
import orca.orca_state as orca_state
import orca.scripts.default as default
import orca.speech as speech

from .script_utilities import Utilities

class Script(default.Script):

    def __init__(self, app):
        default.Script.__init__(self, app)

    def getUtilities(self):
        return Utilities(self)

    def deactivate(self):
        """Called when this script is deactivated."""

        self.utilities.clearCachedObjects()
        super().deactivate()

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if self.utilities.isToggleDescendantOfComboBox(newFocus):
            isComboBox = lambda x: x and x.getRole() == pyatspi.ROLE_COMBO_BOX
            newFocus = pyatspi.findAncestor(newFocus, isComboBox) or newFocus
            orca.setLocusOfFocus(event, newFocus, False)
        elif self.utilities.isInOpenMenuBarMenu(newFocus):
            window = self.utilities.topLevelObject(newFocus)
            windowChanged = window and orca_state.activeWindow != window
            if windowChanged:
                orca_state.activeWindow = window
                self.windowActivateTime = time.time()

        super().locusOfFocusChanged(event, oldFocus, newFocus)

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not self.utilities.isTypeahead(orca_state.locusOfFocus):
            super().onActiveDescendantChanged(event)
            return

        msg = "GTK: locusOfFocus believed to be typeahead. Presenting change."
        debug.println(debug.LEVEL_INFO, msg, True)
        self.presentObject(event.any_data)

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        obj = event.source
        if self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            default.Script.onCheckedChanged(self, event)
            return

        # Present changes of child widgets of GtkListBox items
        isListBox = lambda x: x and x.getRole() == pyatspi.ROLE_LIST_BOX
        if not pyatspi.findAncestor(obj, isListBox):
            return

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # that fail to reliably emit object:state-changed:focused events.

        if self.utilities.eventIsCanvasNoise(event):
            return

        if self.utilities.isLayoutOnly(event.source):
            return

        if event.source == mouse_review.reviewer.getCurrentItem():
            msg = "GTK: Event source is current mouse review item"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        if self.utilities.isTypeahead(orca_state.locusOfFocus) \
           and "Table" in pyatspi.listInterfaces(event.source) \
           and not event.source.getState().contains(pyatspi.STATE_FOCUSED):
            return

        if "Table" in pyatspi.listInterfaces(event.source):
            selectedChildren = self.utilities.selectedChildren(event.source)
            if selectedChildren:
                orca.setLocusOfFocus(event, selectedChildren[0])
                return

        ancestor = pyatspi.findAncestor(orca_state.locusOfFocus, lambda x: x == event.source)
        if not ancestor:
            orca.setLocusOfFocus(event, event.source)
            return

        if ancestor and "Table" in pyatspi.listInterfaces(ancestor):
            return

        isMenu = lambda x: x and x.getRole() == pyatspi.ROLE_MENU
        if isMenu(ancestor) and not pyatspi.findAncestor(ancestor, isMenu):
            return

        orca.setLocusOfFocus(event, event.source)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self.utilities.isUselessPanel(event.source):
            msg = "GTK: Event source believed to be useless panel"
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().onFocusedChanged(event)

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self.utilities.isEntryCompletionPopupItem(event.source):
            if event.detail1:
                orca.setLocusOfFocus(event, event.source)
                return
            if orca_state.locusOfFocus == event.source:
                orca.setLocusOfFocus(event, None)
                return

        role = event.source.getRole()
        if role in [pyatspi.ROLE_CANVAS, pyatspi.ROLE_ICON] \
           and self.utilities.handleContainerSelectionChange(event.source.parent):
            return

        super().onSelectedChanged(event)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.isComboBoxWithToggleDescendant(event.source) \
            and self.utilities.isOrDescendsFrom(orca_state.locusOfFocus, event.source):
            super().onSelectionChanged(event)
            return

        isFocused = event.source.getState().contains(pyatspi.STATE_FOCUSED)
        role = event.source.getRole()
        if role == pyatspi.ROLE_COMBO_BOX and not isFocused:
            return

        if not isFocused and self.utilities.isTypeahead(orca_state.locusOfFocus):
            msg = "GTK: locusOfFocus believed to be typeahead. Presenting change."
            debug.println(debug.LEVEL_INFO, msg, True)

            selectedChildren = self.utilities.selectedChildren(event.source)
            for child in selectedChildren:
                if not self.utilities.isLayoutOnly(child):
                    self.presentObject(child)
            return

        if role == pyatspi.ROLE_LAYERED_PANE \
           and self.utilities.selectedChildCount(event.source) > 1:
            return

        super().onSelectionChanged(event)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if not event.detail1:
            super().onShowingChanged(event)
            return

        obj = event.source
        if self.utilities.isPopOver(obj) \
           or obj.getRole() in [pyatspi.ROLE_ALERT, pyatspi.ROLE_INFO_BAR]:
            if obj.parent and obj.parent.getRole() == pyatspi.ROLE_APPLICATION:
                return
            self.presentObject(event.source)
            return

        super().onShowingChanged(event)

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not self.utilities.isShowingAndVisible(event.source):
            msg = "GTK: %s is not showing and visible" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().onTextDeleted(event)

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not self.utilities.isShowingAndVisible(event.source):
            msg = "GTK: %s is not showing and visible" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        super().onTextInserted(event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        default.Script.onTextSelectionChanged(self, event)

    def isActivatableEvent(self, event):
        if self.utilities.eventIsCanvasNoise(event):
            return False

        if self.utilities.isUselessPanel(event.source):
            return False

        return super().isActivatableEvent(event)
