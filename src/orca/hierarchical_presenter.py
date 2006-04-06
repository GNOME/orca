# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""Provides an experimental hierarchical navigation presentation
manager for Orca.  This is mostly for exploratory purposes."""

import atspi
import braille
import debug
import speech
import orca
import presentation_manager

from orca_i18n import _                          # for gettext support
from rolenames import getShortBrailleForRoleName # localized role names

class HierarchicalPresenter(presentation_manager.PresentationManager):
    """When activated, this module consumes all keyboard events (or at
    least those not already consumed by the main orca module) and uses the
    arrow and tab keys for navigation.  The main concepts for navigation
    include:

      Perceive the component hierarchy as being displayed in a list,
      much like a tree view.

      Use the up/down arrow keys to go between the children of a
      parent.  When the first/last child is reached, the navigation
      will not wrap.

      Use the left/right arrow keys to go to the parent of a child or
      to the first child of a parent.

      Use the Tab key to explore the AT-SPI specializations (e.g.,
      action, component, text, etc.) of a child.  The up/down arrow
      keys will take you between the specializations that the child
      implements.  If the child does not implement any specializations,
      Tab will not do anything.

      To go back to hierarchical navigation from specialization
      exploration mode, press Shift+Tab.

    Again, this is very experimental and is designed more for script
    writers than end users.
    """

    # NAVIGATION_MODE_INTEROBJECT = between objects
    # Press Shift+Tab to enter this mode.
    #
    _NAVIGATION_MODE_INTEROBJECT = 0

    # NAVIGATION_MODE_INTRAOBJECT = between specializations in object
    # Press Tab to enter this mode.
    #
    _NAVIGATION_MODE_INTRAOBJECT = 1

    _SPECIALIZATION_NONE               = -1
    _SPECIALIZATION_ACTION             = 0
    _SPECIALIZATION_COMPONENT          = 1
    _SPECIALIZATION_EDITABLE_TEXT      = 2
    _SPECIALIZATION_HYPERTEXT          = 3
    _SPECIALIZATION_IMAGE              = 4
    _SPECIALIZATION_RELATION           = 5
    _SPECIALIZATION_SELECTION          = 6
    _SPECIALIZATION_STREAMABLE_CONTENT = 7
    _SPECIALIZATION_TABLE              = 8
    _SPECIALIZATION_TEXT               = 9
    _SPECIALIZATION_VALUE              = 10
    _SPECIALIZATION_LENGTH             = 11

    def __init__(self):
    	self._navigationMode               = self._NAVIGATION_MODE_INTEROBJECT
    	self._currentObject                = None
    	self._currentObjectSpecializations = []
    	self._currentSpecialization        = self._SPECIALIZATION_ACTION

    ########################################################################
    #                                                                      #
    # Methods for dealing with INTEROBJECT navigation.                     #
    #                                                                      #
    ########################################################################

    def _getApplicationIndex(self, accessible):
        """Determines the desktop index of the application for the given
        accessible
        """

        apps = atspi.getKnownApplications()
	for i in range(0, len(apps)):
            if accessible.app == apps[i]:
                return i

	return -1

    def _getIndentText(self, accessible):
        """Creates a string of numbers where each number represents a child
        index in the parent.  For example, '8 5 4' means the 4th child of
        the 5th child of the 8th child.
        """

        text = ""
        while accessible != accessible.app:
            if text == "":
                text = ("%d" % accessible.index)
            else:
                text = ("%d" % accessible.index) + " " + text
            accessible = accessible.parent

        return text

    def _displayAccessible(self, accessible):
        """Displays an accessible."""

        if accessible.childCount:
            brltext = "o "
        else:
            brltext = "  "

        brltext = brltext + ("%d " % self._getApplicationIndex(accessible))
        indentText = self._getIndentText(accessible)
        if indentText != "":
            brltext = brltext + indentText + " "

        brltext = brltext + getShortBrailleForRoleName(accessible) + " " \
                  + accessible.name + " " \
                  + accessible.description + " " \
                  + accessible.getStateString()

        debug.println(debug.LEVEL_OFF, brltext)
        braille.displayMessage(brltext)
        orca.outlineAccessible(accessible)

    def _navigateInterObject(self, keystring):
        """Navigates between objects in the component hierarchy."""

        apps = atspi.getKnownApplications()
        if keystring == "Up":
            if self._currentObject == self._currentObject.app:
                index = max(self._getApplicationIndex(self._currentObject) - 1,
                            0)
                self._currentObject = apps[index]
                self._displayAccessible(self._currentObject)
            else:
                parent = self._currentObject.parent
                index = max(self._currentObject.index - 1, 0)
                self._currentObject = parent.child(index)
                self._displayAccessible(self._currentObject)
        elif keystring == "Down":
            if self._currentObject == self._currentObject.app:
                index = min(self._getApplicationIndex(self._currentObject) + 1,
                            len(apps) - 1)
                self._currentObject = apps[index]
                self._displayAccessible(self._currentObject)
            else:
                parent = self._currentObject.parent
                index = min(self._currentObject.index + 1,
			    parent.childCount - 1)
                self._currentObject = parent.child(index)
                self._displayAccessible(self._currentObject)
        elif keystring == "Left":
            parent = self._currentObject.parent
            if parent:
                self._currentObject = self._currentObject.parent
                self._displayAccessible(self._currentObject)
        elif keystring == "Right":
            if self._currentObject.childCount:
                self._currentObject = self._currentObject.child(0)
                self._displayAccessible(self._currentObject)

    ########################################################################
    #                                                                      #
    # Methods for dealing with INTRAOBJECT navigation.                     #
    #                                                                      #
    ########################################################################

    def _getSpecializations(self, accessible):
        """Gets all the specializations for an accessible and populates
        the global currentObjectSpecializations list with them."""

        self._currentObjectSpecializations = []
        for i in range(0, self._SPECIALIZATION_LENGTH):
            self._currentObjectSpecializations.append(None)
            i = i + 1

        self._currentObjectSpecializations[self._SPECIALIZATION_ACTION]    = \
            accessible.action
        self._currentObjectSpecializations[self._SPECIALIZATION_COMPONENT] = \
            accessible.component
        self._currentObjectSpecializations[self._SPECIALIZATION_HYPERTEXT] = \
            accessible.hypertext
        self._currentObjectSpecializations[self._SPECIALIZATION_SELECTION] = \
            accessible.selection
        self._currentObjectSpecializations[self._SPECIALIZATION_TABLE]     = \
            accessible.table
        self._currentObjectSpecializations[self._SPECIALIZATION_TEXT]      = \
            accessible.text
        self._currentObjectSpecializations[self._SPECIALIZATION_VALUE]     = \
            accessible.value

    def _displayActionSpecialization(self, action):
        """Displays the contents of an accessible action."""

        if not action:
            return

        brltext = "Actions:"
        i = 0
        while i < action.nActions:
            brltext = brltext + " " + action.getName(i)
            i = i + 1

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displayComponentSpecialization(self, component):
        """Displays the contents of an accessible component."""

        if not component:
            return

        extents = component.getExtents(0) # coord type = screen

        brltext = "Component: x=%d y=%d w=%d h=%d" \
                  % (extents.x, extents.y, extents.width, extents.height)

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displayHypertextSpecialization(self, hypertext):
        """Displays the contents of an accessible hypertext."""

        if not hypertext:
            return

        brltext = "Hypertext: %d links" % hypertext.getNLinks()

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displaySelectionSpecialization(self, selection):
        """Displays the contents of an accessible selection."""

        if not selection:
            return

        brltext = "Selection: %d selected children" \
		  % selection.nSelectedChildren

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displayTableSpecialization(self, table):
        """Displays the contents of an accessible table."""

        if not table:
            return

        brltext = "Table: rows=%d cols=%d" % (table.nRows, table.nColumns)

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displayTextSpecialization(self, text):
        """Displays the contents of an accessible text."""

        if not text:
            return

        brltext = "Text (len=%d): %s" \
                  % (text.characterCount, text.getText(0, -1))

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displayValueSpecialization(self, value):
        """Displays the contents of an accessible value."""

        if not value:
            return

        brltext = "Value: min=%f current=%f max=%f" \
                  % (value.minimumValue, value.currentValue, value.maximumValue)

        debug.println(debug.LEVEL_OFF, brltext)

        braille.displayMessage(brltext)

    def _displaySpecialization(self, specialization):
        """Displays a specialization.  Will do nothing if the object
        does not have this specialization.

        Arguments:
        - specialization: index into currentObjectSpecializations
        """

        # [[[TODO: WDW - Some things are commented out below because
        # atspi.py doesn't give them to us yet.]]]
        #
        if specialization == self._SPECIALIZATION_ACTION:
            self._displayActionSpecialization(
                self._currentObjectSpecializations[specialization])
        elif specialization == self._SPECIALIZATION_COMPONENT:
            self._displayComponentSpecialization(
                self._currentObjectSpecializations[specialization])
    #    elif specialization == self._SPECIALIZATION_EDITABLE_TEXT:
    #        self._displayTextSpecialization(
    #            self._currentObjectSpecializations[specialization])
        elif specialization == self._SPECIALIZATION_HYPERTEXT:
            self._displayHypertextSpecialization(
                self._currentObjectSpecializations[specialization])
    #    elif specialization == self._SPECIALIZATION_IMAGE:
    #        self._displayImageSpecialization(
    #            self._currentObjectSpecializations[specialization])
    #    elif specialization == self._SPECIALIZATION_RELATION:
    #        self._displayRelationSpecialization(
    #            self._currentObjectSpecializations[specialization])
        elif specialization == self._SPECIALIZATION_SELECTION:
            self._displaySelectionSpecialization(
                self._currentObjectSpecializations[specialization])
        elif specialization == self._SPECIALIZATION_TABLE:
            self._displayTableSpecialization(
                self._currentObjectSpecializations[specialization])
        elif specialization == self._SPECIALIZATION_TEXT:
            self._displayTextSpecialization(
                self._currentObjectSpecializations[specialization])
        elif specialization == self._SPECIALIZATION_VALUE:
            self._displayValueSpecialization(
                self._currentObjectSpecializations[specialization])

    def _navigateIntraObject(self, keystring):
        """Navigates between specializations of an object."""

        # Want to find the previous non-None specialization
        #
        if keystring == "Up":
            i = self._currentSpecialization - 1
            while i >= 0:
                if self._currentObjectSpecializations[i]:
                    break
                i = i - 1
            if i >= 0:
                self._currentSpecialization = i
                self._displaySpecialization(self._currentSpecialization)

        # Want to find the next non-None specialization
        #
        if keystring == "Down":
            i = self._currentSpecialization + 1
            while i < len(self._currentObjectSpecializations):
                if self._currentObjectSpecializations[i]:
                    break
                i = i + 1
            if i < len(self._currentObjectSpecializations):
                self._currentSpecialization = i
                self._displaySpecialization(self._currentSpecialization)

    ########################################################################
    #                                                                      #
    # Methods that are part of the PresentationManager contract.           #
    #                                                                      #
    ########################################################################

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event based on the keybinding from the
        currently active script. This method is called synchronously from the
        at-spi registry and should be performant.  In addition, it must return
        True if it has consumed the event (and False if not).

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event should be consumed.
        """

        if keyboardEvent.type != atspi.Accessibility.KEY_PRESSED_EVENT:
            return

        keystring = keyboardEvent.event_string

        # [[[TODO: WDW - probably should set these up as keybindings
        # rather than hardcoding them.]]]
        #
        if keystring == "Tab":
            self._getSpecializations(self._currentObject)
            self._currentSpecialization = self._SPECIALIZATION_NONE
            for i in range(0, len(self._currentObjectSpecializations)):
                if self._currentObjectSpecializations[i]:
                    self._currentSpecialization = i
                    break
            if self._currentSpecialization != self._SPECIALIZATION_NONE:
                self._navigationMode = self._NAVIGATION_MODE_INTRAOBJECT
                self._displaySpecialization(self._currentSpecialization)
            else:
                self._navigationMode = self._NAVIGATION_MODE_INTEROBJECT
                self._displayAccessible(self._currentObject)
        elif keystring == "ISO_Left_Tab":
            self._navigationMode = self._NAVIGATION_MODE_INTEROBJECT
            self._displayAccessible(self._currentObject)
        elif self._navigationMode == self._NAVIGATION_MODE_INTEROBJECT:
            self._navigateInterObject(keystring)
        elif self._navigationMode == self._NAVIGATION_MODE_INTRAOBJECT:
            self._navigateIntraObject(keystring)

        return True

    def activate(self):
        """Called when this presentation manager is activated."""

        speech.speak(_("Switching to hierarchical navigation mode."))

        apps = atspi.getKnownApplications()
        
        win = orca.findActiveWindow()

        if win:
            self._currentObject = win.app
            self._displayAccessible(self._currentObject)
        else:
            self._currentObject = apps[0]
            self._displayAccessible(self._currentObject)
            
    def deactivate(self):
        """Called when this presentation manager is deactivated."""
        orca.outlineAccessible(None)

