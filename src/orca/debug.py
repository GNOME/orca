# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Provides debug utilities for Orca.  Debugging is managed by a debug
level, which is held in the debugLevel field.  All other methods take
a debug level, which is compared to the current debug level to
determine if the content should be output."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import traceback
import pyatspi

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
# For the purposes of Orca, LEVEL_INFO means display the text being sent to
# speech and braille.
#
LEVEL_INFO = 800

# Used to indicate static configuration information to assist in debugging
# problems that may be associated with a particular configuration.
#
# For the purposes of Orca, LEVEL_CONFIGURATION means display the various
# apsects of whether a particular feature (e.g., speech, braille, etc.)
# is enabled or not as well as details about that feature.
#
LEVEL_CONFIGURATION = 700

# Used for lowest volume of detailed tracing information.
#
# For the purposes of Orca, this is braille and keyboard input, script
# activation and deletion, locus of focus changes, and visual changes
# to the locus of focus.
#
LEVEL_FINE = 600

# Used for medium volume of detailed tracing information.
#
# For the purposes of Orca, this is for debugging speech and braille
# generators and tracking the synthesis of device events.
#
LEVEL_FINER = 500

# Used for maximum volume of detailed tracing information.
#
# For the purposes of Orca, this is for tracking all AT-SPI object
# events.  NOTE that one can up the debug level of AT-SPI object
# events by setting the eventDebugLevel.  In addition, one can filter
# events by setting eventDebugFilter to a regular expression that
# matches event type names.
#
LEVEL_FINEST = 400

# Used for all detailed tracing information, even finer than LEVEL_FINEST
#
LEVEL_ALL = 0

debugLevel = LEVEL_SEVERE

# The debug file.  If this is not set, then all debug output is done
# via stdout.  If this is set, then all debug output is sent to the
# file.  This can be useful for debugging because one can pass in a
# non-buffered file to better track down hangs.
#
debugFile = None

# The debug filter should be either None (which means to match all
# events) or a compiled regular expression from the 're' module (see
# http://www.amk.ca/python/howto/regex/).  The regular expression will
# be used as a matching function - if the event type creates a match
# in the regular expression, then it will be considered for output.  A
# typical call to this method might look like:
#
# debug.eventDebugFilter = rc.compile('focus:|window:activate')
#
eventDebugLevel  = LEVEL_FINEST
eventDebugFilter = None

def printException(level):
    """Prints out information regarding the current exception.

    Arguments:
    - level: the accepted debug level
    """

    if level >= debugLevel:
        println(level)
        traceback.print_exc(100, debugFile)
        println(level)

def printStack(level):
    """Prints out the current stack.

    Arguments:
    - level: the accepted debug level
    """

    if level >= debugLevel:
        println(level)
        traceback.print_stack(None, 100, debugFile)
        println(level)

def println(level, text = ""):
    """Prints the text to stdout if debug is enabled.

    Arguments:
    - level: the accepted debug level
    - text: the text to print (default is a blank line)
    """

    if level >= debugLevel:
        if debugFile:
            debugFile.writelines([text, "\n"])
        else:
            print text

def printObjectEvent(level, event, sourceInfo=None):
    """Prints out an Python Event object.  The given level may be
    overridden if the eventDebugLevel is greater.  Furthermore, only
    events with event types matching the eventDebugFilter regular
    expression will be printed.

    Arguments:
    - level: the accepted debug level
    - event: the Python Event to print
    - sourceInfo: additional string to print out
    """

    if eventDebugFilter and not eventDebugFilter.match(event.type):
        return

    level = max(level, eventDebugLevel)

    text = "OBJECT EVENT: %-40s detail=(%d,%d)" \
           % (event.type, event.detail1, event.detail2)
    println(level, text)

    if sourceInfo:
        println(level, "             %s" % sourceInfo)

def printInputEvent(level, string):
    """Prints out an input event.  The given level may be overridden
    if the eventDebugLevel (see setEventDebugLevel) is greater.

    Arguments:
    - level: the accepted debug level
    - string: the string representing the input event
    """

    println(max(level, eventDebugLevel), string)

def printDetails(level, indent, accessible, includeApp=True):
    """Lists the details of the given accessible with the given
    indentation.

    Arguments:
    - level: the accepted debug level
    - indent: a string containing spaces for indentation
    - accessible: the accessible whose details are to be listed
    - includeApp: if True, include information about the app
    """

    if level >= debugLevel and accessible:
        println(level, getAccessibleDetails(accessible, indent, includeApp))

def getAccessibleDetails(acc, indent="", includeApp=True):
    """Returns a string, suitable for printing, that describes the
    given accessible.

    Arguments:
    - indent: A string to prefix the output with
    - includeApp: If True, include information about the app
                  for this accessible.
    """

    if includeApp:
        app = acc.getApplication()
        if app:
            string = indent + "app.name='%s' " % app.name
        else:
            string = indent + "app=None "
    else:
        string = indent

    # create the States string
    stateSet = acc.getState()
    states = stateSet.getStates()
    state_strings = []
    for state in states:
        state_strings.append(pyatspi.stateToString(state))
    state_string = ' '.join(state_strings)

    # create the relations string
    relations = acc.getRelationSet()
    if relations:
        relation_strings = []
        for relation in relations:
            relation_strings.append( \
                          pyatspi.relationToString(relation.getRelationType()))
        rel_string = ' '.join(relation_strings)
    else:
        rel_string = ''

    string += "name='%s' role='%s' state='%s' relations='%s'" \
              % (acc.name or 'None', acc.getRoleName(),
                 state_string, rel_string)

    return string


# The following code has been borrowed from the following URL:
# 
# http://www.dalkescientific.com/writings/diary/archive/ \
#                                     2005/04/20/tracing_python_code.html
#
import linecache

def traceit(frame, event, arg):
    """Line tracing utility to output all lines as they are executed by
    the interpreter.  This is to be used by sys.settrace and is for 
    debugging purposes.
   
    Arguments:
    - frame: is the current stack frame
    - event: 'call', 'line', 'return', 'exception', 'c_call', 'c_return',
             or 'c_exception'
    - arg:   depends on the event type (see docs for sys.settrace)
    """ 

    if event == "line":
        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        if name == "gettext" \
           or name == "locale" \
           or name == "posixpath" \
           or name == "UserDict":
            return traceit
        line = linecache.getline(filename, lineno)
        println(LEVEL_ALL, "TRACE %s:%s: %s" % (name, lineno, line.rstrip()))
    return traceit
