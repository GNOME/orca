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

import orca.orca as orca
import orca.orca_state as orca_state
import orca.scripts.default as default

from .script_utilities import Utilities

class Script(default.Script):

    def __init__(self, app):
        default.Script.__init__(self, app)

    def getUtilities(self):
        return Utilities(self)

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        role = event.source.getRole()

        try:
            focusedRole = orca_state.locusOfFocus.getRole()
        except:
            pass
        else:
            # This is very likely typeahead search and not a real focus change.
            tableRoles = [pyatspi.ROLE_TABLE, pyatspi.ROLE_TREE_TABLE]
            if focusedRole == pyatspi.ROLE_TEXT and role in tableRoles:
                orca.setLocusOfFocus(event, event.source, False)

        default.Script.onActiveDescendantChanged(self, event)

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

        # https://bugzilla.gnome.org/show_bug.cgi?id=720987
        if role == pyatspi.ROLE_TABLE_COLUMN_HEADER:
            orca.setLocusOfFocus(event, event.source)
            return

        # https://bugzilla.gnome.org/show_bug.cgi?id=720989
        if role == pyatspi.ROLE_MENU == event.source.parent.getRole():
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. But this happens when you are in gtk-demo's application demo,
        # get into a menu and then press Escape. The text widget emits a focus:
        # event, but not a state-changed:focused event.
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
        if role == pyatspi.ROLE_MENU_ITEM:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled, but in at least some dialogs, the first time a push
        # button gains focus, we only get a focus: event for it.
        # Seems to happen for checkboxes too. This is why we can't have
        # nice things.
        if role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_CHECK_BOX]:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled, but yet another case of only getting a focus: event when
        # a widget appears in a parent container and is already focused.
        if role == pyatspi.ROLE_TABLE:
            obj = event.source
            selectedChildren = self.utilities.selectedChildren(obj)
            if selectedChildren:
                obj = selectedChildren[0]

            orca.setLocusOfFocus(event, obj)
            return

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        obj = event.source
        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        default.Script.onTextSelectionChanged(self, event)
