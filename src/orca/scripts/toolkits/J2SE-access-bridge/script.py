# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc., "  \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.scripts.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state

from .script_utilities import Utilities
from .speech_generator import SpeechGenerator
from .formatting import Formatting

########################################################################
#                                                                      #
# The Java script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for Java applications.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

        # Some objects which issue descendant changed events lack
        # STATE_MANAGES_DESCENDANTS. As a result, onSelectionChanged
        # doesn't ignore these objects. That in turn causes Orca to
        # double-speak some items and/or set the locusOfFocus to a
        # parent it shouldn't. See bgo#616582. [[[TODO - JD: remove
        # this hack if and when we get a fix for that bug]]]
        # 
        self.lastDescendantChangedSource = None

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""
        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilites for this script."""
        return Utilities(self)

    def checkKeyboardEventData(self, keyboardEvent):
        """Checks the data on the keyboard event.

        Some toolkits don't fill all the key event fields, and/or fills
        them out with unexpected data. This method tries to fill in the
        missing fields and validate/standardize the data we've been given.
        While any script can override this method, it is expected that
        this will only be done at the toolkit script level.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        default.Script.checkKeyboardEventData(self, keyboardEvent)

        if not keyboardEvent.keyval_name:
            return

        from gi.repository import Gdk

        keymap = Gdk.Keymap.get_default()
        keyval = Gdk.keyval_from_name(keyboardEvent.keyval_name)
        success, entries = keymap.get_entries_for_keyval(keyval)
        for entry in entries:
            if entry.group == 0:
                keyboardEvent.hw_code = entry.keycode
                break

        # Put the event_string back to what it was prior to the Java
        # Atk Wrapper hack which gives us the keyname and not the
        # expected and needed printable character for punctuation
        # marks.
        #
        if keyboardEvent.event_string == keyboardEvent.keyval_name \
           and len(keyboardEvent.event_string) > 1:
            keyval = Gdk.keyval_from_name(keyboardEvent.keyval_name)
            if 0 < keyval < 256:
                keyboardEvent.event_string = chr(keyval)

    def onCaretMoved(self, event):
        # Java's SpinButtons are the most caret movement happy thing
        # I've seen to date.  If you Up or Down on the keyboard to
        # change the value, they typically emit three caret movement
        # events, first to the beginning, then to the end, and then
        # back to the beginning.  It's a very excitable little widget.
        # Luckily, it only issues one value changed event.  So, we'll
        # ignore caret movement events caused by value changes and
        # just process the single value changed event.
        #
        isSpinBox = self.utilities.hasMatchingHierarchy(
            event.source, [pyatspi.ROLE_TEXT,
                           pyatspi.ROLE_PANEL,
                           pyatspi.ROLE_SPIN_BUTTON])
        if isSpinBox:
            eventStr, mods = self.utilities.lastKeyAndModifiers()
            if eventStr in ["Up", "Down"] or isinstance(
               orca_state.lastInputEvent, input_event.MouseButtonEvent):
                return

        default.Script.onCaretMoved(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        # Avoid doing this with objects that manage their descendants
        # because they'll issue a descendant changed event. (Note: This
        # equality check is intentional; utilities.isSameObject() is
        # especially thorough with trees and tables, which is not
        # performant.
        #
        if event.source == self.lastDescendantChangedSource:
            return

        # We treat selected children as the locus of focus. When the
        # selection changes in a list we want to update the locus of
        # focus. If there is no selection, we default the locus of
        # focus to the containing object.
        #
        if (event.source.getRole() in [pyatspi.ROLE_LIST,
                                       pyatspi.ROLE_PAGE_TAB_LIST,
                                       pyatspi.ROLE_TREE]) \
            and event.source.getState().contains(pyatspi.STATE_FOCUSED):
            newFocus = event.source
            if event.source.childCount:
                selection = event.source.querySelection()
                if selection.nSelectedChildren > 0:
                    newFocus = selection.getSelectedChild(0)
            orca.setLocusOfFocus(event, newFocus)
        else:
            default.Script.onSelectionChanged(self, event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        obj = event.source
        role = obj.getRole()

        # Accessibility support for menus in Java is badly broken: Missing
        # events, missing states, bogus events from other objects, etc.
        # Therefore if we get an event, however broken, for menus or their
        # their items that suggests they are selected, we'll just cross our
        # fingers and hope that's true.
        menuRoles = [pyatspi.ROLE_MENU,
                     pyatspi.ROLE_MENU_BAR,
                     pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM,
                     pyatspi.ROLE_POPUP_MENU]

        if role in menuRoles or obj.parent.getRole() in menuRoles:
            orca.setLocusOfFocus(event, obj)
            return

        try:
            focusRole = orca_state.locusOfFocus.getRole()
        except:
            focusRole = None

        if focusRole in menuRoles and role == pyatspi.ROLE_ROOT_PANE:
            return

        default.Script.onFocusedChanged(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.

        Arguments:
        - event: the Event
        """

        # We'll ignore value changed events for Java's toggle buttons since
        # they also send a redundant object:state-changed:checked event.
        #
        ignoreRoles = [pyatspi.ROLE_TOGGLE_BUTTON,
                       pyatspi.ROLE_RADIO_BUTTON,
                       pyatspi.ROLE_CHECK_BOX]
        if event.source.getRole() in ignoreRoles:
            return

        # Java's SpinButtons are the most caret movement happy thing
        # I've seen to date.  If you Up or Down on the keyboard to
        # change the value, they typically emit three caret movement
        # events, first to the beginning, then to the end, and then
        # back to the beginning.  It's a very excitable little widget.
        # Luckily, it only issues one value changed event.  So, we'll
        # ignore caret movement events caused by value changes and
        # just process the single value changed event.
        #
        if event.source.getRole() == pyatspi.ROLE_SPIN_BUTTON:
            try:
                thisBox = orca_state.locusOfFocus.parent.parent == event.source
            except:
                thisBox = False
            if thisBox:
                self._presentTextAtNewCaretPosition(event,
                                                    orca_state.locusOfFocus)
                return

        default.Script.onValueChanged(self, event)

    def skipObjectEvent(self, event):

        # Accessibility support for menus in Java is badly broken. One problem
        # is bogus focus claims following menu-related focus claims. Therefore
        # in this particular toolkit, we mustn't skip events for menus.

        menuRoles = [pyatspi.ROLE_MENU,
                     pyatspi.ROLE_MENU_BAR,
                     pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM,
                     pyatspi.ROLE_POPUP_MENU]

        if event.source.getRole() in menuRoles:
            return False

        return default.Script.skipObjectEvent(self, event)
