# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state
import orca.keybindings as keybindings

from speech_generator import SpeechGenerator
from formatting import Formatting

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

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """

        # The Java platform chooses to give us keycodes different from
        # the native platform keycodes.  So, we hack here by converting
        # the keysym we get from Java into a keycode.

        keysym = keyboardEvent.event_string

        # We need to make sure we have a keysym-like thing.  The space
        # character is not a keysym, so we convert it into the string,
        # 'space', which is.
        #
        if keysym == " ":
            keysym = "space"

        keyboardEvent.hw_code = keybindings.getKeycode(keysym)
        return default.Script.consumesKeyboardEvent(self, keyboardEvent)

    def getNodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return -1

        treeLikeThing = self.getAncestor(obj,
                                         [pyatspi.ROLE_TREE,
                                          pyatspi.ROLE_TABLE,
                                          pyatspi.ROLE_TREE_TABLE],
                                         None)
        if not treeLikeThing:
            return -1

        count = 0
        while True:
            state = obj.getState()
            if state.contains(pyatspi.STATE_EXPANDABLE) \
               or state.contains(pyatspi.STATE_COLLAPSED):
                if state.contains(pyatspi.STATE_VISIBLE):
                    count += 1
                obj = obj.parent
            else:
                break

        return count - 1

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        role = event.source.getRole()

        if role == pyatspi.ROLE_MENU:
            # Override default.py's onFocus decision to ignore focus
            # events on MENU items with selected children.  This is
            # because JMenu's pop up without their children selected,
            # but for some reason they always have
            # selection.nSelectedChildren > 0.  I suspect this is a
            # bug in JMenu.java:getAccessibleSelectionCount, but the
            # details of Swing's MenuSelectionManager are foreign to
            # me.  So, for now, we'll just be happy knowing that
            # Java's menu items will give us focus events when they
            # are selected.
            #
            orca.setLocusOfFocus(event, event.source)
            return

        default.Script.onFocus(self, event)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        # In Java comboboxes, when the list of options is popped up via
        # an up or down action, control (but not focus) goes to a LIST
        # object that manages the descendants.  So, we detect that here
        # and keep focus on the combobox.
        #
        if event.source.getRole() == pyatspi.ROLE_COMBO_BOX:
            orca.visualAppearanceChanged(event, event.source)
            return

        if event.source.getRole() == pyatspi.ROLE_LIST:
            combobox = self.getAncestor(event.source,
                                        [pyatspi.ROLE_COMBO_BOX],
                                        [pyatspi.ROLE_PANEL])
            if combobox:
                orca.visualAppearanceChanged(event, combobox)
                return

        default.Script.onActiveDescendantChanged(self, event)

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
        isSpinBox = self.isDesiredFocusedItem(event.source,
                                              [pyatspi.ROLE_TEXT,
                                               pyatspi.ROLE_PANEL,
                                               pyatspi.ROLE_SPIN_BUTTON])
        if isSpinBox:
            if isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent):
                eventStr = orca_state.lastNonModifierKeyEvent.event_string
            else:
                eventStr = None
            if (eventStr in ["Up", "Down"]) \
               or isinstance(orca_state.lastInputEvent,
                             input_event.MouseButtonEvent):
                return

        default.Script.onCaretMoved(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

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

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # Handle state changes when JTree labels become expanded
        # or collapsed.
        #
        if (event.source.getRole() == pyatspi.ROLE_LABEL) and \
            event.type.startswith("object:state-changed:expanded"):
            orca.visualAppearanceChanged(event, event.source)
            return

        # This is a workaround for a java-access-bridge bug (Bug 355011)
        # where popup menu events are not sent to Orca.
        #
        # When a root pane gets focus, a popup menu may have been invoked.
        # If there is a popup menu, give locus of focus to the armed menu
        # item.
        #
        if event.source.getRole() == pyatspi.ROLE_ROOT_PANE and \
               event.type.startswith("object:state-changed:focused") and \
               event.detail1 == 1:

            for child in event.source:
                # search the layered pane for a popup menu
                if child.getRole() == pyatspi.ROLE_LAYERED_PANE:
                    popup = self.findByRole(child,
                                            pyatspi.ROLE_POPUP_MENU, False)
                    if len(popup) > 0:
                        # set the locus of focus to the armed menu item
                        items = self.findByRole(popup[0],
                                                pyatspi.ROLE_MENU_ITEM, False)
                        for item in items:
                            if item.getState().contains(pyatspi.STATE_ARMED):
                                orca.setLocusOfFocus(event, item)
                                return

        # Present a value change in case of an focused popup menu.
        # Fix for Swing file chooser.
        #
        if event.type.startswith("object:state-changed:visible") and \
                event.source.getRole() == pyatspi.ROLE_POPUP_MENU and \
                event.source.parent.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source.parent)
            return

        default.Script.onStateChanged(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.

        Arguments:
        - event: the Event
        """

        # We'll ignore value changed events for Java's toggle buttons since
        # they also send a redundant object:state-changed:checked event.
        #
        if event.source.getRole() == pyatspi.ROLE_TOGGLE_BUTTON:
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
