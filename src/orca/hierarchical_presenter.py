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

"""Provides an experimental hierarchical navigation presentation manager for
Orca.  This is mostly for exploratory purposes.  The main entry points into
this module are for the presentation manager contract:

    processKeyboardEvent - handles all keyboard events
    processBrailleEvent  - handles all Braille input events
    locusOfFocusChanged  - notified when orca's locusOfFocus changes
    activate             - called when this manager is enabled
    deactivate           - called when this manager is disabled

When activated, this module consumes all keyboard events (or at least those
not already consumed by the main orca module) and uses the arrow and tab keys
for navigation.  The main concepts for navigation include:

    Perceive the component hierarchy as being displayed in a list,
    much like a tree view.

    Use the up/down arrow keys to go between the children of a parent.
    When the first/last child is reached, the navigation will not wrap.

    Use the left/right arrow keys to go to the parent of a child or
    to the first child of a parent.

    Use the Tab key to explore the AT-SPI specializations (e.g.,
    action, component, text, etc.) of a child.  The up/down arrow
    keys will take you between the specializations that the child
    implements.  If the child does not implement any specializations,
    Tab will not do anything.

    To go back to hierarchical navigation from specialization exploration
    mode, press Shift+Tab.

Again, this is very experimental and is designed more for script writers
than end users.
"""

import sys

import a11y
import braille
import debug
import core
import speech
import orca

from orca_i18n import _                          # for gettext support
from rolenames import getShortBrailleForRoleName # localized role names


# NAVIGATION_MODE_INTEROBJECT = between objects
# Press Shift+Tab to enter this mode.
#
_NAVIGATION_MODE_INTEROBJECT = 0

# NAVIGATION_MODE_INTRAOBJECT = between specializations in object
# Press Tab to enter this mode.
#
_NAVIGATION_MODE_INTRAOBJECT = 1

# Current navigation mode.
#
_navigationMode = _NAVIGATION_MODE_INTEROBJECT

# The currently active object.
#
_currentObject = None

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

_currentObjectSpecializations = []
_currentSpecialization = _SPECIALIZATION_ACTION


########################################################################
#                                                                      #
# Methods for dealing with INTEROBJECT navigation.                     #
#                                                                      #
########################################################################

def _getApplicationIndex(accessible):
    """Determines the desktop index of the application for the given
    accessible
    """

    i = 0
    while i < len(orca.apps):
        if accessible.app == orca.apps[i]:
            return i
        i = i + 1

    sys.stderr.write("ERROR: hierarchical_presenter._getApplicationIndex:\n")
    sys.stderr.write("ERROR: accessible does not have an application!\n")
    

def _getIndentText(accessible):
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


def _displayAccessible(accessible):
    """Displays an accessible."""
    
    if accessible.childCount:
        brltext = "o "
    else:
        brltext = "  "

    brltext = brltext + ("%d " % _getApplicationIndex(accessible))
    indentText = _getIndentText(accessible)
    if indentText != "":
        brltext = brltext + indentText + " "

    brltext = brltext + getShortBrailleForRoleName(accessible) + " " \
              + accessible.name + " " \
              + accessible.description + " " \
              + a11y.getStateString(accessible)

    debug.println(debug.LEVEL_OFF, brltext)
        
    braille.displayMessage(brltext)

    orca.outlineAccessible(accessible)

    
def _navigateInterObject(keystring):
    """Navigates between objects in the component hierarchy."""

    global _currentObject

    if keystring == "Up":
        if _currentObject.app == _currentObject:
            index = max(_getApplicationIndex(_currentObject) - 1, 0)
            _currentObject = orca.apps[index]
            _displayAccessible(_currentObject)
        else:
            parent = _currentObject.parent
            index = max(_currentObject.index - 1, 0)
            _currentObject = parent.child(index)
            _displayAccessible(_currentObject)
    elif keystring == "Down":
        if _currentObject.app == _currentObject:
            index = min(_getApplicationIndex(_currentObject) + 1,
                        len(orca.apps) - 1)
            _currentObject = orca.apps[index]
            _displayAccessible(_currentObject)
        else:
            parent = _currentObject.parent
            index = min(_currentObject.index + 1, parent.childCount - 1)
            _currentObject = parent.child(index)
            _displayAccessible(_currentObject)
    elif keystring == "Left":
        parent = _currentObject.parent
        if parent:
            _currentObject = _currentObject.parent
            _displayAccessible(_currentObject)
    elif keystring == "Right":
        if _currentObject.childCount:
            _currentObject = _currentObject.child(0)
            _displayAccessible(_currentObject)
    

########################################################################
#                                                                      #
# Methods for dealing with INTRAOBJECT navigation.                     #    
#                                                                      #
########################################################################

def _getSpecializations(accessible):
    """Gets all the specializations for an accessible and populates
    the global currentObjectSpecializations list with them."""

    global _currentObjectSpecializations
    
    _currentObjectSpecializations = []
    i = 0
    while i < _SPECIALIZATION_LENGTH:
        _currentObjectSpecializations.append(None)
        i = i + 1
        
    _currentObjectSpecializations[_SPECIALIZATION_ACTION] = \
        accessible.action
    _currentObjectSpecializations[_SPECIALIZATION_COMPONENT] = \
        accessible.component
    _currentObjectSpecializations[_SPECIALIZATION_HYPERTEXT] = \
        accessible.hypertext
    _currentObjectSpecializations[_SPECIALIZATION_SELECTION] = \
        accessible.selection
    _currentObjectSpecializations[_SPECIALIZATION_TABLE] = \
        accessible.table
    _currentObjectSpecializations[_SPECIALIZATION_TEXT] = \
        accessible.text
    _currentObjectSpecializations[_SPECIALIZATION_VALUE] = \
        accessible.value


def _displayActionSpecialization(action):
    """Displays the contents of an accessible action."""

    if action is None:
        return

    brltext = "Actions:"
    i = 0
    while i < action.nActions:
        brltext = brltext + " " + action.getName(i)
        i = i + 1

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)

    
def _displayComponentSpecialization(component):
    """Displays the contents of an accessible component."""

    if component is None:
        return

    extents = component.getExtents(0) # coord type = screen
    
    brltext = "Component: x=%d y=%d w=%d h=%d" \
              % (extents.x, extents.y, extents.width, extents.height)

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)

    
def _displayHypertextSpecialization(hypertext):
    """Displays the contents of an accessible hypertext."""

    if hypertext is None:
        return

    brltext = "Hypertext: %d links" % hypertext.getNLinks()

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)

    
def _displaySelectionSpecialization(selection):
    """Displays the contents of an accessible selection."""

    if selection is None:
        return

    brltext = "Selection: %d selected children" % selection.nSelectedChildren

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)

    
def _displayTableSpecialization(table):
    """Displays the contents of an accessible table."""

    if table is None:
        return

    brltext = "Table: rows=%d cols=%d" % (table.nRows, table.nColumns)

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)

    
def _displayTextSpecialization(text):
    """Displays the contents of an accessible text."""

    if text is None:
        return

    brltext = "Text: "

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)


def _displayValueSpecialization(value):
    """Displays the contents of an accessible value."""

    if value is None:
        return

    brltext = "Value: min=%f current=%f max=%f" \
              % (value.minimumValue, value.currentValue, value.maximumValue)

    debug.println(debug.LEVEL_INFO, brltext)
        
    braille.displayMessage(brltext)


def _displaySpecialization(specialization):
    """Displays a specialization.  Will do nothing if the object
    does not have this specialization.

    Arguments:
    - specialization: index into currentObjectSpecializations
    """

    # [[[TODO: WDW - Some things are commented out below because
    # a11y.py doesn't give them to us yet.]]]
    #
    if specialization == _SPECIALIZATION_ACTION:
        _displayActionSpecialization(
            _currentObjectSpecializations[specialization])
    elif specialization == _SPECIALIZATION_COMPONENT:
        _displayComponentSpecialization(
            _currentObjectSpecializations[specialization])
#    elif specialization == _SPECIALIZATION_EDITABLE_TEXT:
#        _displayTextSpecialization(
#            _currentObjectSpecializations[specialization])
    elif specialization == _SPECIALIZATION_HYPERTEXT:
        _displayHypertextSpecialization(
            _currentObjectSpecializations[specialization])
#    elif specialization == _SPECIALIZATION_IMAGE:
#        _displayImageSpecialization(
#            _currentObjectSpecializations[specialization])
#    elif specialization == _SPECIALIZATION_RELATION:
#        _displayRelationSpecialization(
#            _currentObjectSpecializations[specialization])
    elif specialization == _SPECIALIZATION_SELECTION:
        _displaySelectionSpecialization(
            _currentObjectSpecializations[specialization])
    elif specialization == _SPECIALIZATION_TABLE:
        _displayTableSpecialization(
            _currentObjectSpecializations[specialization])
    elif specialization == _SPECIALIZATION_TEXT:
        _displayTextSpecialization(
            _currentObjectSpecializations[specialization])
    elif specialization == _SPECIALIZATION_VALUE:
        _displayValueSpecialization(
            _currentObjectSpecializations[specialization])

        
def _navigateIntraObject(keystring):
    """Navigates between specializations of an object."""

    global _currentSpecialization

    # Want to find the previous non-None specialization
    #
    if keystring == "Up":
        i = _currentSpecialization - 1
        while i >= 0:
            if _currentObjectSpecializations[i]:
                break
            i = i - 1
        if i >= 0:
            _currentSpecialization = i
            _displaySpecialization(_currentSpecialization)
            
    # Want to find the next non-None specialization
    #
    if keystring == "Down":
        i = _currentSpecialization + 1
        while i < len(_currentObjectSpecializations):
            if _currentObjectSpecializations[i]:
                break
            i = i + 1
        if i < len(_currentObjectSpecializations):
            _currentSpecialization = i
            _displaySpecialization(_currentSpecialization)
            

########################################################################
#                                                                      #
# Methods that are part of the presentation manager contract.          #
#                                                                      #
########################################################################

def processKeyboardEvent(keyboardEvent):
    """Processes the given keyboard event based on the keybinding from the
    currently active script. This method is called synchronously from the
    at-spi registry and should be performant.  In addition, it must return
    True if it has consumed the event (and False if not).
    
    Arguments:
    - keyboardEvent: an instance of input_event.KeyboardEvent

    Returns True if the event should be consumed.
    """

    global _navigationMode
    global _currentSpecialization

    if keyboardEvent.type != core.Accessibility.KEY_PRESSED_EVENT:
        return
    
    keystring = keyboardEvent.event_string

    # [[[TODO: WDW - probably should set these up as keybindings
    # rather than hardcoding them.]]]
    #
    if keystring == "Tab":
        _getSpecializations(_currentObject)
        i = 0
        _currentSpecialization = _SPECIALIZATION_NONE
        while i < len(_currentObjectSpecializations):
            if _currentObjectSpecializations[i]:
                _currentSpecialization = i
                break
            i = i + 1
        if _currentSpecialization != _SPECIALIZATION_NONE:
            _navigationMode = _NAVIGATION_MODE_INTRAOBJECT
            _displaySpecialization(_currentSpecialization)
        else:
            _navigationMode = _NAVIGATION_MODE_INTEROBJECT
            _displayAccessible(_currentObject)
    elif keystring == "ISO_Left_Tab":
        _navigationMode = _NAVIGATION_MODE_INTEROBJECT
        _displayAccessible(_currentObject)
    elif _navigationMode == _NAVIGATION_MODE_INTEROBJECT:
        _navigateInterObject(keystring)
    elif _navigationMode == _NAVIGATION_MODE_INTRAOBJECT:
        _navigateIntraObject(keystring)
        
    return True


def processBrailleEvent(brailleEvent):
    """Called whenever a cursor key is pressed on the Braille display.
    
    Arguments:
    - brailleEvent: an instance of input_event.BrailleEvent

    Returns True if the command was consumed; otherwise False
    """

    return False
        

def locusOfFocusChanged(event, oldLocusOfFocus, newLocusOfFocus):
    """Called when the visual object with focus changes.

    Arguments:
    - event: if not None, the Event that caused the change
    - oldLocusOfFocus: Accessible that is the old locus of focus
    - newLocusOfFocus: Accessible that is the new locus of focus
    """
    pass


def activate():
    """Called when this presentation manager is activated."""

    global _currentObject
    
    speech.speak(_("Switching to hierarchical navigation mode."))

    win = orca.findActiveWindow()
    
    if win:
        _currentObject = win.app
        _displayAccessible(_currentObject)
        
def deactivate():
    """Called when this presentation manager is deactivated."""
    
    orca.outlineAccessible(None)

