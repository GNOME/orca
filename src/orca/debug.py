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

"""Provides debug utilities for Orca."""

import a11y
import core
import orca
import settings                   # user settings
from rolenames import getRoleName # localized role names


def getStates (obj):
    """Returns a space-delimited string composed of the given object's
    Accessible state attribute.

    Arguments:
    - obj: an Accessible
    """
    
    set = obj.state
    stateString = " "
    if set.count (core.Accessibility.STATE_INVALID):
        stateString += "INVALID "
    if set.count (core.Accessibility.STATE_ACTIVE):
        stateString += "ACTIVE "
    if set.count (core.Accessibility.STATE_ARMED):
        stateString += "ARMED "
    if set.count (core.Accessibility.STATE_BUSY):
        stateString += "BUSY "
    if set.count (core.Accessibility.STATE_CHECKED):
        stateString += "CHECKED "
    if set.count (core.Accessibility.STATE_COLLAPSED):
        stateString += "COLLAPSED "
    if set.count (core.Accessibility.STATE_DEFUNCT):
        stateString += "DEFUNCT "
    if set.count (core.Accessibility.STATE_EDITABLE):
        stateString += "EDITABLE "
    if set.count (core.Accessibility.STATE_ENABLED):
        stateString += "ENABLED "
    if set.count (core.Accessibility.STATE_EXPANDABLE):
        stateString += "EXPANDABLE "
    if set.count (core.Accessibility.STATE_EXPANDED):
        stateString += "EXPANDED "
    if set.count (core.Accessibility.STATE_FOCUSABLE):
        stateString += "FOCUSABLE "
    if set.count (core.Accessibility.STATE_FOCUSED):
        stateString += "FOCUSED "
    if set.count (core.Accessibility.STATE_HAS_TOOLTIP):
        stateString += "HAS_TOOLTIP "
    if set.count (core.Accessibility.STATE_HORIZONTAL):
        stateString += "HORIZONTAL "
    if set.count (core.Accessibility.STATE_ICONIFIED):
        stateString += "ICONIFIED "
    if set.count (core.Accessibility.STATE_MODAL):
        stateString += "MODAL "
    if set.count (core.Accessibility.STATE_MULTI_LINE):
        stateString += "MULTI_LINE "
    if set.count (core.Accessibility.STATE_MULTISELECTABLE):
        stateString += "MULTISELECTABLE "
    if set.count (core.Accessibility.STATE_OPAQUE):
        stateString += "OPAQUE "
    if set.count (core.Accessibility.STATE_PRESSED):
        stateString += "PRESSED "
    if set.count (core.Accessibility.STATE_RESIZABLE):
        stateString += "RESIZABLE "
    if set.count (core.Accessibility.STATE_SELECTABLE):
        stateString += "SELECTABLE "
    if set.count (core.Accessibility.STATE_SELECTED):
        stateString += "SELECTED "
    if set.count (core.Accessibility.STATE_SENSITIVE):
        stateString += "SENSITIVE "
    if set.count (core.Accessibility.STATE_SHOWING):
        stateString += "SHOWING "
    if set.count (core.Accessibility.STATE_SINGLE_LINE):
        stateString += "SINGLE_LINE " 
    if set.count (core.Accessibility.STATE_STALE):
        stateString += "STALE "
    if set.count (core.Accessibility.STATE_TRANSIENT):
        stateString += "TRANSIENT " 
    if set.count (core.Accessibility.STATE_VERTICAL):
        stateString += "VERTICAL "
    if set.count (core.Accessibility.STATE_VISIBLE):
        stateString += "VISIBLE "
    if set.count (core.Accessibility.STATE_MANAGES_DESCENDANTS):
        stateString += "MANAGES_DESCENDANTS "
    if set.count (core.Accessibility.STATE_INDETERMINATE):
        stateString += "INDETERMINATE "

    return stateString;


def println (text):
    """Prints the text to stdout if settings.debug is enabled.
    
    Arguments:
    - text: the text to print
    """

    # There may not even be a debug field in settings, so we need to
    # catch this.
    #
    try:
        if settings.debug:
            print text
    except:
        pass

def listDetails (indent, accessible):
    """Lists the details of the given accessible with the given
    indentation.

    Arguments:
    - indent: a string containing spaces for indentation
    - accessible: the accessible whose details are to be listed
    """

    println ("%sname   = (%s)" % (indent, accessible.name))
    println ("%srole   = (%s)" % (indent, getRoleName(accessible)))
    println ("%sstate  = (%s)" % (indent, getStates(accessible)))

    if accessible.app is None:
        println ("%sapp    = (None)" % indent)
    else:
        println ("%sapp    = (%s)" % (indent, accessible.app.name))
        
    
def listApps ():
    """Prints a list of all applications to stdout"""

    println ("There are %d apps" % len(orca.apps))
    for app in orca.apps:
        println ("  %s (childCount=%d)" % (app.name, app.childCount))
        count = 0
        while count < app.childCount:
            println ("    Child %d:" % count)
            child = app.child (count)
            listDetails ("      ", child)
            if child.parent != app:
                println("      WARNING: child's parent is not app!!!")
            count += 1


def listActiveApp ():
    """Prints the active application."""

    println ("Current active application:")
    window = orca.findActiveWindow ()
    if window is None:
        println ("  None")
    else:
        app = window.app
        if app is None:
            println ("  None")
        else:
            listDetails("  ", app)
            count = 0
            while count < app.childCount:
                println ("    Child %d:" % count)
                child = app.child (count)
                listDetails ("    ", child)
                if child.parent != app:
                    println("      WARNING: child's parent is not app!!!")
                count += 1
