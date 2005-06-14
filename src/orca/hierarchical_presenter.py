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

    processObjectEvent  - handles all object events
    processKeyEvent     - handles all keyboard events
    processBrailleEvent - handles all Braille input events
    activate            - called when this manager is enabled
    deactivate          - called when this manager is disabled

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
import core
import brl
import speech
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import script
import debug

import orca

from orca_i18n import _                          # for gettext support
from rolenames import getShortBrailleForRoleName # localized role names


# NAVIGATION_MODE_INTEROBJECT = between objects
# Press Shift+Tab to enter this mode.
#
NAVIGATION_MODE_INTEROBJECT = 0

# NAVIGATION_MODE_INTRAOBJECT = between specializations in object
# Press Tab to enter this mode.
#
NAVIGATION_MODE_INTRAOBJECT = 1

# Current navigation mode.
#
navigationMode = NAVIGATION_MODE_INTEROBJECT

# The currently active object.
#
currentObject = None

SPECIALIZATION_NONE               = -1
SPECIALIZATION_ACTION             = 0
SPECIALIZATION_COMPONENT          = 1
SPECIALIZATION_EDITABLE_TEXT      = 2
SPECIALIZATION_HYPERTEXT          = 3
SPECIALIZATION_IMAGE              = 4
SPECIALIZATION_RELATION           = 5
SPECIALIZATION_SELECTION          = 6
SPECIALIZATION_STREAMABLE_CONTENT = 7
SPECIALIZATION_TABLE              = 8
SPECIALIZATION_TEXT               = 9
SPECIALIZATION_VALUE              = 10
SPECIALIZATION_LENGTH             = 11

currentObjectSpecializations = []
currentSpecialization = SPECIALIZATION_ACTION


########################################################################
#                                                                      #
# Methods for dealing with INTEROBJECT navigation.                     #
#                                                                      #
########################################################################

def getApplicationIndex(accessible):
    """Determines the desktop index of the application for the given
    accessible
    """

    i = 0
    while i < len(orca.apps):
        if accessible.app == orca.apps[i]:
            return i
        i = i + 1

    sys.stderr.write("ERROR: hierarchical_presenter.getApplicationIndex:\n")
    sys.stderr.write("ERROR: accessible does not have an application!\n")
    

def getIndentText(accessible):
    """Creates a string of numbers where each number represents a child
    index in the parent.  For example, '8 5 4' means the 4th child of
    the 5th child of the 8th child.
    """
    
    level = 0

    text = ""
    while accessible != accessible.app:
        if text == "":
            text = ("%d" % accessible.index)
        else:
            text = ("%d" % accessible.index) + " " + text
        accessible = accessible.parent

    return text


def displayAccessible(accessible):
    """Displays an accessible."""
    
    if accessible.childCount:
        brltext = "o "
    else:
        brltext = "  "

    brltext = brltext + ("%d " % getApplicationIndex(accessible))
    indentText = getIndentText(accessible)
    if indentText != "":
        brltext = brltext + indentText + " "

    brltext = brltext + getShortBrailleForRoleName(accessible) + " " \
              + accessible.name + " " \
              + accessible.description + " " \
              + debug.getStates(accessible)

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()

    orca.outlineAccessible(accessible)

    
def navigateInterObject(keystring):
    """Navigates between objects in the component hierarchy."""

    global currentObject

    if keystring == "Up":
        if currentObject.app == currentObject:
            index = max(getApplicationIndex(currentObject) - 1, 0)
            currentObject = orca.apps[index]
            displayAccessible(currentObject)
        else:
            parent = currentObject.parent
            index = max(currentObject.index - 1, 0)
            currentObject = parent.child(index)
            displayAccessible(currentObject)
    elif keystring == "Down":
        if currentObject.app == currentObject:
            index = min(getApplicationIndex(currentObject) + 1,
                        len(orca.apps) - 1)
            currentObject = orca.apps[index]
            displayAccessible(currentObject)
        else:
            parent = currentObject.parent
            index = min(currentObject.index + 1, parent.childCount - 1)
            currentObject = parent.child(index)
            displayAccessible(currentObject)
    elif keystring == "Left":
        parent = currentObject.parent
        if parent:
            currentObject = currentObject.parent
            displayAccessible(currentObject)
    elif keystring == "Right":
        if currentObject.childCount:
            currentObject = currentObject.child(0)
            displayAccessible(currentObject)
    

########################################################################
#                                                                      #
# Methods for dealing with INTRAOBJECT navigation.                     #    
#                                                                      #
########################################################################

def getSpecializations(accessible):
    """Gets all the specializations for an accessible and populates
    the global currentObjectSpecializations list with them."""

    global currentObjectSpecializations
    
    currentObjectSpecializations = []
    i = 0
    while i < SPECIALIZATION_LENGTH:
        currentObjectSpecializations.append(None)
        i = i + 1
        
    currentObjectSpecializations[SPECIALIZATION_ACTION] = \
        a11y.getAction(accessible)
    currentObjectSpecializations[SPECIALIZATION_COMPONENT] = \
        a11y.getComponent(accessible)
    currentObjectSpecializations[SPECIALIZATION_HYPERTEXT] = \
        a11y.getHypertext(accessible)
    currentObjectSpecializations[SPECIALIZATION_SELECTION] = \
        a11y.getSelection(accessible)
    currentObjectSpecializations[SPECIALIZATION_TABLE] = \
        a11y.getTable(accessible)
    currentObjectSpecializations[SPECIALIZATION_TEXT] = \
        a11y.getText(accessible)
    currentObjectSpecializations[SPECIALIZATION_VALUE] = \
        a11y.getValue(accessible)


def displayActionSpecialization(action):
    """Displays the contents of an accessible action."""

    if action is None:
        return

    brltext = "Actions:"
    i = 0
    while i < action.nActions:
        brltext = brltext + " " + action.getName(i)
        i = i + 1

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()

    
def displayComponentSpecialization(component):
    """Displays the contents of an accessible component."""

    if component is None:
        return

    extents = component.getExtents(0) # coord type = screen
    
    brltext = "Component: x=%d y=%d w=%d h=%d" \
              % (extents.x, extents.y, extents.width, extents.height)

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()

    
def displayHypertextSpecialization(hypertext):
    """Displays the contents of an accessible hypertext."""

    if hypertext is None:
        return

    brltext = "Hypertext: %d links" % hypertext.getNLinks()

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()

    
def displaySelectionSpecialization(selection):
    """Displays the contents of an accessible selection."""

    if selection is None:
        return

    brltext = "Selection: %d selected children" % selection.nSelectedChildren

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()

    
def displayTableSpecialization(table):
    """Displays the contents of an accessible table."""

    if table is None:
        return

    brltext = "Table: rows=%d cols=%d" % (table.nRows, table.nColumns)

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()

    
def displayTextSpecialization(text):
    """Displays the contents of an accessible text."""

    if text is None:
        return

    brltext = "Text: "

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()


def displayValueSpecialization(value):
    """Displays the contents of an accessible value."""

    if value is None:
        return

    brltext = "Value: min=%f current=%f max=%f" \
              % (value.minimumValue, value.currentValue, value.maximumValue)

    debug.println(debug.LEVEL_INFO, brltext)
        
    brl.writeMessage(brltext)
    brl.refresh()


def displaySpecialization(specialization):
    """Displays a specialization.  Will do nothing if the object
    does not have this specialization.

    Arguments:
    - specialization: index into currentObjectSpecializations
    """

    global currentObjectSpecializations
    global currentSpecialization

    # [[[TODO: WDW - Some things are commented out below because
    # a11y.py doesn't give them to us yet.]]]
    #
    if currentSpecialization == SPECIALIZATION_ACTION:
        displayActionSpecialization(
            currentObjectSpecializations[currentSpecialization])
    elif currentSpecialization == SPECIALIZATION_COMPONENT:
        displayComponentSpecialization(
            currentObjectSpecializations[currentSpecialization])
#    elif currentSpecialization == SPECIALIZATION_EDITABLE_TEXT:
#        displayTextSpecialization(
#            currentObjectSpecializations[currentSpecialization])
    elif currentSpecialization == SPECIALIZATION_HYPERTEXT:
        displayHypertextSpecialization(
            currentObjectSpecializations[currentSpecialization])
#    elif currentSpecialization == SPECIALIZATION_IMAGE:
#        displayImageSpecialization(
#            currentObjectSpecializations[currentSpecialization])
#    elif currentSpecialization == SPECIALIZATION_RELATION:
#        displayRelationSpecialization(
#            currentObjectSpecializations[currentSpecialization])
    elif currentSpecialization == SPECIALIZATION_SELECTION:
        displaySelectionSpecialization(
            currentObjectSpecializations[currentSpecialization])
    elif currentSpecialization == SPECIALIZATION_TABLE:
        displayTableSpecialization(
            currentObjectSpecializations[currentSpecialization])
    elif currentSpecialization == SPECIALIZATION_TEXT:
        displayTextSpecialization(
            currentObjectSpecializations[currentSpecialization])
    elif currentSpecialization == SPECIALIZATION_VALUE:
        displayValueSpecialization(
            currentObjectSpecializations[currentSpecialization])

        
def navigateIntraObject(keystring):
    """Navigates between specializations of an object."""

    global currentObjectSpecializations
    global currentSpecialization

    # Want to find the previous non-None specialization
    #
    if keystring == "Up":
        i = currentSpecialization - 1
        while i >= 0:
            if currentObjectSpecializations[i]:
                break
            i = i - 1
        if i >= 0:
            currentSpecialization = i
            displaySpecialization(currentSpecialization)
            
    # Want to find the next non-None specialization
    #
    if keystring == "Down":
        i = currentSpecialization + 1
        while i < len(currentObjectSpecializations):
            if currentObjectSpecializations[i]:
                break
            i = i + 1
        if i < len(currentObjectSpecializations):
            currentSpecialization = i
            displaySpecialization(currentSpecialization)
            

########################################################################
#                                                                      #
# Methods that are part of the presentation manager contract.          #
#                                                                      #
########################################################################

def processObjectEvent(event):
    """Handles all events destined for scripts.  We don't care about
    this for now, but we might want to do something clever, such as
    set the currentObject at some point.[[[TODO: WDW - the event

    Arguments:
    - event: a Python Event (the one created from an at-spi event).
    """
    pass


def processKeyEvent(keystring):
    """Processes the given keyboard event based on the keybinding from the
    currently active script. This method is called synchronously from the
    at-spi registry and should be performant.  In addition, it must return
    True if it has consumed the event (and False if not).
    
    Arguments:
    - keystring: a keyboard event string from kbd.py

    Returns True if the event should be consumed.
    """

    global navigationMode
    global currentObjectSpecializations
    global currentSpecialization
    
    if keystring == "Tab":
        getSpecializations(currentObject)
        i = 0
        currentSpecialization = SPECIALIZATION_NONE
        while i < len(currentObjectSpecializations):
            if currentObjectSpecializations[i]:
                currentSpecialization = i
                break
            i = i + 1
        if currentSpecialization != SPECIALIZATION_NONE:
            navigationMode = NAVIGATION_MODE_INTRAOBJECT
            displaySpecialization(currentSpecialization)
        else:
            navigationMode = NAVIGATION_MODE_INTEROBJECT
            displayAccessible(currentObject)
    elif keystring == "ISO_Left_Tab":
        navigationMode = NAVIGATION_MODE_INTEROBJECT
        displayAccessible(currentObject)
    elif navigationMode == NAVIGATION_MODE_INTEROBJECT:
        navigateInterObject(keystring)
    elif navigationMode == NAVIGATION_MODE_INTRAOBJECT:
        navigateIntraObject(keystring)
        
    return True


def processBrailleEvent(region, position):
    """Called whenever a cursor key is pressed on the Braille display.

    Arguments:
    - region: the Braille region which generated the press
    - position: the offset within the region
    """
    pass
        

def activate():
    """Called when this presentation manager is activated."""

    global currentObject
    
    speech.say("default", _("Switching to hierarchical navigation mode."))

    win = orca.findActiveWindow()
    
    if win:
        currentObject = win.app
        displayAccessible(currentObject)
        
def deactivate():
    """Called when this presentation manager is deactivated."""
    pass
