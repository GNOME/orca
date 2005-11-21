# Orca
#
# Copyright 2005 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import orca.core as core
import orca.default as default
import orca.rolenames as rolenames
import orca.orca as orca
import orca.keybindings as keybindings

########################################################################
#                                                                      #
# The StarOffice script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        # [[[TODO: HACK to blank out keybindings because the
        # java-access-bridge gives us wrong keycodes.
        #
        # See: http://bugzilla.gnome.org/show_bug.cgi?id=318615]]]
        #
        self.keybindings = keybindings.KeyBindings()

        self._display = None
        self._display_txt = None

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # [[[TODO: richb - Need to investigate further.
        # If we subclass this method here, and simple call the same
        # method in the parent class, then movement from one line in
        # a text document to the next, just results in the new line
        # being spoken once (compared with both the last line and the
        # new line being spoken upto two times each).]]]
        #
        default.Script.onFocus(self, event)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # If this is a focus event for a menu or one of the various
        # types of menu item, then just ignore it. Otherwise pass the
        # event onto the parent class to be processed.

        role = event.source.role

        if (role == rolenames.ROLE_MENU) \
           or (role == rolenames.ROLE_MENU_ITEM) \
           or (role == rolenames.ROLE_CHECK_MENU_ITEM) \
           or (role == rolenames.ROLE_RADIO_MENU_ITEM):
            return
        else:
            default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        # If this is an "armed" object-state-changed event for a menu
        # or one of the various types of menu item, and this object has
        # the focus, then set the locus of focus. Otherwise pass the
        # event onto the parent class to be processed.

        if event.type.endswith("armed"):
            role = event.source.role

            if event.source.state.count(core.Accessibility.STATE_FOCUSED) \
               and ((role == rolenames.ROLE_MENU) or \
                    (role == rolenames.ROLE_MENU_ITEM) or \
                    (role == rolenames.ROLE_CHECK_MENU_ITEM) or \
                    (role == rolenames.ROLE_RADIO_MENU_ITEM)):
                orca.setLocusOfFocus(event, event.source)
                return

        default.Script.onStateChanged(self, event)
