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

"""Provides debug utilities for Orca.  Debugging is managed by a
debug level, which is set by calling the setDebugLevel method.  All
other methods take a debug level, which is compared to the current
debug level to determine if the content should be output."""

import core
import orca
from rolenames import getRoleName # localized role names
import traceback

# Used to turn off all debugging.
#
LEVEL_OFF = 10000

# Used to describe events of considerable importance and which will prevent
# normal program execution.
#
LEVEL_SEVERE = 1000

# Used to decribe events of interest to end users or system managers or which
# indicate potential problems, but which Orca can deal with without crashing.
#
LEVEL_WARNING = 900

# Used to indicate reasonably significant messages that make sense to end users
# and system managers.
#
LEVEL_INFO = 800

# Used to indicate static configuration information to assist in debugging
# problems that may be associated with a particular configuration.  For
# example, used to say if a particular feature (e.g., speech, braille, etc.)
# is enabled or not.
#
LEVEL_CONFIGURATION = 700

# Used for lowest volume of detailed tracing information.  For example,
# used to indicate a script has been activated.
#
LEVEL_FINE = 600

# Used for medium volume of detailed tracing information.  For example,
# used to indicate a particular focus tracking presenter has been called.
#
LEVEL_FINER = 500

# Used for maximum volume of detailed tracing information.  For example,
# used to display all AT-SPI object events.
#
LEVEL_FINEST = 400

# Used for all detailed tracing information, even finer than LEVEL_FINEST
#
LEVEL_ALL = 0


debugLevel = LEVEL_SEVERE

def setDebugLevel(newLevel):
    """Sets the debug level.  The various levels can be LEVEL_OFF,
    LEVEL_SEVERE, LEVEL_WARNING, LEVEL_INFO, LEVEL_CONFIG, LEVEL_FINE,
    LEVEL_FINER, LEVEL_FINEST, LEVEL_ALL.

    Arguments:
    - newLevel: the new debugLevel
    """

    global debugLevel
    
    println(debugLevel, "Changing debugLevel to %d" % newLevel)
    debugLevel = newLevel
    println(debugLevel, "Changed debugLevel to %d" % debugLevel)
    
    
def getStates(obj):
    """Returns a space-delimited string composed of the given object's
    Accessible state attribute.

    Arguments:
    - obj: an Accessible
    """
    
    set = obj.state
    stateString = " "
    if set.count(core.Accessibility.STATE_INVALID):
        stateString += "INVALID "
    if set.count(core.Accessibility.STATE_ACTIVE):
        stateString += "ACTIVE "
    if set.count(core.Accessibility.STATE_ARMED):
        stateString += "ARMED "
    if set.count(core.Accessibility.STATE_BUSY):
        stateString += "BUSY "
    if set.count(core.Accessibility.STATE_CHECKED):
        stateString += "CHECKED "
    if set.count(core.Accessibility.STATE_COLLAPSED):
        stateString += "COLLAPSED "
    if set.count(core.Accessibility.STATE_DEFUNCT):
        stateString += "DEFUNCT "
    if set.count(core.Accessibility.STATE_EDITABLE):
        stateString += "EDITABLE "
    if set.count(core.Accessibility.STATE_ENABLED):
        stateString += "ENABLED "
    if set.count(core.Accessibility.STATE_EXPANDABLE):
        stateString += "EXPANDABLE "
    if set.count(core.Accessibility.STATE_EXPANDED):
        stateString += "EXPANDED "
    if set.count(core.Accessibility.STATE_FOCUSABLE):
        stateString += "FOCUSABLE "
    if set.count(core.Accessibility.STATE_FOCUSED):
        stateString += "FOCUSED "
    if set.count(core.Accessibility.STATE_HAS_TOOLTIP):
        stateString += "HAS_TOOLTIP "
    if set.count(core.Accessibility.STATE_HORIZONTAL):
        stateString += "HORIZONTAL "
    if set.count(core.Accessibility.STATE_ICONIFIED):
        stateString += "ICONIFIED "
    if set.count(core.Accessibility.STATE_MODAL):
        stateString += "MODAL "
    if set.count(core.Accessibility.STATE_MULTI_LINE):
        stateString += "MULTI_LINE "
    if set.count(core.Accessibility.STATE_MULTISELECTABLE):
        stateString += "MULTISELECTABLE "
    if set.count(core.Accessibility.STATE_OPAQUE):
        stateString += "OPAQUE "
    if set.count(core.Accessibility.STATE_PRESSED):
        stateString += "PRESSED "
    if set.count(core.Accessibility.STATE_RESIZABLE):
        stateString += "RESIZABLE "
    if set.count(core.Accessibility.STATE_SELECTABLE):
        stateString += "SELECTABLE "
    if set.count(core.Accessibility.STATE_SELECTED):
        stateString += "SELECTED "
    if set.count(core.Accessibility.STATE_SENSITIVE):
        stateString += "SENSITIVE "
    if set.count(core.Accessibility.STATE_SHOWING):
        stateString += "SHOWING "
    if set.count(core.Accessibility.STATE_SINGLE_LINE):
        stateString += "SINGLE_LINE " 
    if set.count(core.Accessibility.STATE_STALE):
        stateString += "STALE "
    if set.count(core.Accessibility.STATE_TRANSIENT):
        stateString += "TRANSIENT " 
    if set.count(core.Accessibility.STATE_VERTICAL):
        stateString += "VERTICAL "
    if set.count(core.Accessibility.STATE_VISIBLE):
        stateString += "VISIBLE "
    if set.count(core.Accessibility.STATE_MANAGES_DESCENDANTS):
        stateString += "MANAGES_DESCENDANTS "
    if set.count(core.Accessibility.STATE_INDETERMINATE):
        stateString += "INDETERMINATE "

    return stateString;


def printException(level):
    """Prints out information regarding the current exception.

    Arguments:
    - level: the accepted debug level
    """

    if level >= debugLevel:
        println(level)
        traceback.print_exc()
        println(level)


def printStack(level):
    """Prints out the current stack.

    Arguments:
    - level: the accepted debug level
    """

    if level >= debugLevel:
        println(level)
        traceback.print_stack()
        println(level)


def println(level, text = ""):
    """Prints the text to stdout if debug is enabled.
    
    Arguments:
    - level: the accepted debug level
    - text: the text to print (default is a blank line)
    """

    if level >= debugLevel:
        print text


def listDetails(level, indent, accessible):
    """Lists the details of the given accessible with the given
    indentation.

    Arguments:
    - level: the accepted debug level
    - indent: a string containing spaces for indentation
    - accessible: the accessible whose details are to be listed
    """

    if level < debugLevel:
        return
    
    println(level, "%sname   = (%s)" % (indent, accessible.name))
    println(level, "%srole   = (%s)" % (indent, getRoleName(accessible)))
    println(level, "%sstate  = (%s)" % (indent, getStates(accessible)))

    if accessible.app is None:
        println(level, "%sapp    = (None)" % indent)
    else:
        println(level, "%sapp    = (%s)" % (indent, accessible.app.name))
        
    
def listApps(level):
    """Prints a list of all applications to stdout

    Arguments:
    - level: the accepted debug level
    """

    if level < debugLevel:
        return
    
    println(level, "There are %d apps" % len(orca.apps))
    for app in orca.apps:
        println(level, "  %s (childCount=%d)" % (app.name, app.childCount))
        count = 0
        while count < app.childCount:
            println(level, "    Child %d:" % count)
            child = app.child(count)
            listDetails(level, "      ", child)
            if child.parent != app:
                println(level, "      WARNING: child's parent is not app!!!")
            count += 1


def listActiveApp(level):
    """Prints the active application.

    Arguments:
    - level: the accepted debug level
    """

    if level < debugLevel:
        return    
    
    println(level, "Current active application:")
    window = orca.findActiveWindow()
    if window is None:
        println(level, "  None")
    else:
        app = window.app
        if app is None:
            println(level, "  None")
        else:
            listDetails(level, "  ", app)
            count = 0
            while count < app.childCount:
                println(level, "    Child %d:" % count)
                child = app.child(count)
                listDetails(level, "    ", child)
                if child.parent != app:
                    println(level,
                            "      WARNING: child's parent is not app!!!")
                count += 1
