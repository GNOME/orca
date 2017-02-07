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

import orca.debug as debug
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
            orca_state.activeWindow = self.utilities.topLevelObject(newFocus)

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

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        role = event.source.getRole()
        try:
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            focusRole = None

        if role == pyatspi.ROLE_FRAME and focusRole == pyatspi.ROLE_TABLE_CELL:
            return

        default.Script.onNameChanged(self, event)

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # during the remainder of the unstable (3.11) development cycle.

        role = event.source.getRole()

        # https://bugzilla.gnome.org/show_bug.cgi?id=711397
        if role == pyatspi.ROLE_COMBO_BOX:
            orca.setLocusOfFocus(event, event.source)
            return

        # The above issue also seems to happen with spin buttons.
        if role == pyatspi.ROLE_SPIN_BUTTON:
            orca.setLocusOfFocus(event, event.source)
            return

        # And with sliders.
        if role == pyatspi.ROLE_SLIDER:
            orca.setLocusOfFocus(event, event.source)
            return

        # https://bugzilla.gnome.org/show_bug.cgi?id=720987
        if role == pyatspi.ROLE_TABLE_COLUMN_HEADER:
            orca.setLocusOfFocus(event, event.source)
            return

        # https://bugzilla.gnome.org/show_bug.cgi?id=720989
        if role == pyatspi.ROLE_MENU == event.source.parent.getRole():
            if event.source.name:
                orca.setLocusOfFocus(event, event.source)
            else:
                msg = "GTK: Nameless menu with parent %s" % event.source.parent
                debug.println(debug.LEVEL_INFO, msg, True)
            return

        # Unfiled, but a similar case of the above issue with combo boxes.
        # Seems to happen for checkboxes too. This is why we can't have
        # nice things.
        if role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_CHECK_BOX]:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. Happens in Evolution, but for what seems to be a generic
        # Gtk+ toggle button. So we'll handle it here.
        if role == pyatspi.ROLE_TOGGLE_BUTTON:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. But this happens when you are in Gedit, get into a menu
        # and then press Escape. The text widget emits a focus: event, but
        # not a state-changed:focused event.
        #
        # A similar issue can be seen when a text widget starts out having
        # focus, such as in the old gnome-screensaver dialog.
        if role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_PASSWORD_TEXT]:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. When a context menu first appears and an item is already
        # selected, we get a focus: event for that menu item, but there is
        # not a state-changed event for that item, nor a selection-changed
        # event for the menu.
        menuItems = [pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM]
        if role in menuItems:
            if orca_state.locusOfFocus \
               and orca_state.locusOfFocus.parent != event.source.parent:
                orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. When a canvas item gets focus but is not selected, we
        # are only getting a focus event. This happens in Nautilus.
        if role == pyatspi.ROLE_CANVAS and not self.utilities.eventIsCanvasNoise(event):
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled, but yet another case of only getting a focus: event when
        # a widget appears in a parent container and is already focused.
        # An example of this particular case is the list of elements dialogs.
        if role == pyatspi.ROLE_TABLE:
            obj = event.source
            selectedChildren = self.utilities.selectedChildren(obj)
            if selectedChildren:
                obj = selectedChildren[0]

            orca.setLocusOfFocus(event, obj)
            return

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self.utilities.isEntryCompletionPopupItem(event.source):
            if event.detail1:
                orca.setLocusOfFocus(event, event.source)
                return
            if orca_state.locusOfFocus == event.source:
                orca.setLocusOfFocus(event, None)
                return

        super().onSelectedChanged(event)

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.isComboBoxWithToggleDescendant(event.source):
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

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        default.Script.onTextSelectionChanged(self, event)

    def isActivatableEvent(self, event):
        if self.utilities.eventIsCanvasNoise(event):
            return False

        return super().isActivatableEvent(event)
