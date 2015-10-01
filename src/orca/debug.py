# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Provides debug utilities for Orca.  Debugging is managed by a debug
level, which is held in the debugLevel field.  All other methods take
a debug level, which is compared to the current debug level to
determine if the content should be output."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import inspect
import traceback
import os
import pyatspi
import subprocess
import sys

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

# If True, we output debug information for the event queue.  We
# use this in addition to log level to prevent debug logic from
# bogging down event handling.
#
debugEventQueue = False

# What module(s) should be traced if traceit is being used. By default
# we'll just attend to ourself. (And by default, we will not enable
# traceit.) Note that enabling this functionality will drag your system
# to a complete and utter halt and should only be used in extreme
# desperation by developers who are attempting to reproduce a very
# specific, immediate issue. Trust me. :-) Disabling braille monitor in
# this case is also strongly advised.
#
TRACE_MODULES = ['orca']

# Specific modules to ignore with traceit.
#
TRACE_IGNORE_MODULES = ['traceback', 'linecache', 'locale', 'gettext',
                        'logging', 'UserDict', 'encodings', 'posixpath',
                        'genericpath', 're']

# Specific apps to trace with traceit.
#
TRACE_APPS = []

# What AT-SPI event(s) should be traced if traceit is being used. By
# default, we'll trace everything. Examples of what you might wish to
# do to narrow things down include:
#
# TRACE_EVENTS = ['object:state-changed', 'focus:']
#     (for any and all object:state-changed events plus focus: events)
# TRACE_EVENTS = ['object:state-changed:selected']
#     (if you know the exact event type of interest)
#
TRACE_EVENTS = []

# What pyatspi role(s) should be traced if traceit is being used. By
# default, we'll trace everything. An example of what you might wish
# to do to narrow things down, if you know buttons trigger the problem:
#
# TRACE_ROLES = [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_TOGGLE_BUTTON]
#
TRACE_ROLES = []

# Whether or not traceit should only trace the work being done when
# processing an actual event. This is when most bad things happen.
# So we'll default to True.
#
TRACE_ONLY_PROCESSING_EVENTS = True

objEvent = None

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
    """Prints the text to stderr unless debug is enabled.

    If debug is enabled the text will be redirected to the
    file debugFile.

    Arguments:
    - level: the accepted debug level
    - text: the text to print (default is a blank line)
    """

    if level >= debugLevel:
        text = text.replace("\ufffc", "[OBJ]")
        if debugFile:
            try:
                debugFile.writelines([text, "\n"])
            except TypeError:
                text = "TypeError when trying to write text"
                debugFile.writelines([text, "\n"])
            except:
                text = "Exception when trying to write text"
                debugFile.writelines([text, "\n"])
        else:
            try:
                sys.stderr.writelines([text, "\n"])
            except TypeError:
                text = "TypeError when trying to write text"
                sys.stderr.writelines([text, "\n"])
            except:
                text = "Exception when trying to write text"
                sys.stderr.writelines([text, "\n"])

def printResult(level, result=None):
    """Prints the return result, along with information about the
    method, arguments, and any errors encountered."""

    if level < debugLevel:
        return

    stack = inspect.stack()
    current, prev = stack[1], stack[2]
    frame = current[0]

    # To better print arguments which are accessible objects
    args = inspect.getargvalues(frame)
    for key, value in list(args.locals.items()):
        args.locals[key] = str(value)
    fArgs = str.replace(inspect.formatargvalues(*args), "'", "")

    callString = 'CALL:   %s.%s (line %s) -> %s.%s%s' % (
        inspect.getmodulename(prev[1]), prev[3], prev[2],
        inspect.getmodulename(current[1]), current[3], fArgs)
    string = '%s\n%s %s' % (callString, 'RESULT:', result)
    println(level, '%s' % string)

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

    text = "OBJECT EVENT: %-40s detail=(%d,%d,%s)" \
           % (event.type, event.detail1, event.detail2, event.any_data)
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
        println(level,
                getAccessibleDetails(level, accessible, indent, includeApp))

def getAccessibleDetails(level, acc, indent="", includeApp=True):
    """Returns a string, suitable for printing, that describes the
    given accessible.

    Arguments:
    - indent: A string to prefix the output with
    - includeApp: If True, include information about the app
                  for this accessible.
    """

    if level < debugLevel:
        return ""

    if includeApp:
        try:
            app = acc.getApplication()
        except:
            string = indent + "app=(exception getting app) "
            app = None
        else:
            if app:
                try:
                    string = indent + "app.name='%s' " % app.name
                except (LookupError, RuntimeError):
                    string = indent + "app.name='(exception getting name)' "
            else:
                string = indent + "app=None "
    else:
        string = indent

    # create the States string
    try:
        stateSet = acc.getState()
    except:
        string += "(exception getting state set)"
    try:
        states = stateSet.getStates()
    except:
        string += "(exception getting states)"
        states = []
    state_strings = []
    for state in states:
        state_strings.append(pyatspi.stateToString(state))
    state_string = ' '.join(state_strings)

    # create the relations string
    try:
        relations = acc.getRelationSet()
    except:
        string += "(exception getting relation set)"
        relations = None
    if relations:
        relation_strings = []
        for relation in relations:
            relation_strings.append( \
                          pyatspi.relationToString(relation.getRelationType()))
        rel_string = ' '.join(relation_strings)
    else:
        rel_string = ''

    try:
        iface_string = " ".join(pyatspi.utils.listInterfaces(acc))
    except:
        iface_string = "(exception calling listInterfaces)"

    try:
        string += "name='%s' role='%s' state='%s' relations='%s' interfaces='%s'" \
                  % (acc.name or 'None', acc.getRoleName(),
                     state_string, rel_string, iface_string)
    except:
        string += "(exception fetching data)"

    return string


# The following code originated from the following URL:
# 
# http://www.dalkescientific.com/writings/diary/archive/ \
#                                     2005/04/20/tracing_python_code.html
#
import linecache

def _getFileAndModule(frame):
    filename, module = None, None
    try:
        filename = frame.f_globals["__file__"]
        module = frame.f_globals["__name__"]
    except:
        pass
    else:
        if (filename.endswith(".pyc") or filename.endswith(".pyo")):
            filename = filename[:-1]

    return filename, module

def _shouldTraceIt():
    if not objEvent:
        return not TRACE_ONLY_PROCESSING_EVENTS

    eventSource = objEvent.source
    if TRACE_APPS:
        app = objEvent.host_application or eventSource.getApplication()
        try:
            app = objEvent.host_application or eventSource.getApplication()
        except:
            pass
        else:
            if not app.name in TRACE_APPS:
                return False

    if TRACE_ROLES and not eventSource.getRole() in TRACE_ROLES:
        return False

    if TRACE_EVENTS and \
       not [x for x in map(objEvent.type.startswith, TRACE_EVENTS) if x]:
        return False

    return True

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

    if not _shouldTraceIt():
        return None

    filename, module = _getFileAndModule(frame)
    if not (filename and module):
        return traceit
    if module in TRACE_IGNORE_MODULES:
        return traceit
    if TRACE_MODULES and not module.split('.')[0] in TRACE_MODULES:
        return traceit
    if not event in ['call', 'line', 'return']:
        return traceit

    lineno = frame.f_lineno
    line = linecache.getline(filename, lineno).rstrip()
    output = 'TRACE %s:%s: %s' % (module, lineno, line)

    if event == 'call':
        argvals = inspect.getargvalues(frame)
        keys = [x for x in argvals[0] if x != 'self']
        try:
            values = list(map(argvals[3].get, keys))
        except TypeError:
            if len(keys) == 1 and isinstance(keys[0], list):
                values = list(map(argvals[3].get, keys[0]))
            else:
                return traceit
        for i, key in enumerate(keys):
            output += '\n  ARG %s=%s' % (key, values[i])

    lineElements = line.strip().split()
    if lineElements and lineElements[0] == 'return':
        if event == 'line':
            return traceit
        output = '%s (rv: %s)' % (output, arg)

    println(LEVEL_ALL, output)

    return traceit

def getOpenFDCount(pid):
    procs = subprocess.check_output([ 'lsof', '-w', '-Ff', '-p', str(pid)])
    procs = procs.decode('UTF-8').split('\n')
    files = list(filter(lambda s: s and s[0] == 'f' and s[1:].isdigit(), procs))

    return len(files)

def getCmdline(pid):
    try:
        openFile = os.popen('cat /proc/%s/cmdline' % pid)
        cmdline = openFile.read()
        openFile.close()
    except:
        cmdline = '(Could not obtain cmdline)'
    cmdline = cmdline.replace('\x00', ' ')

    return cmdline

def pidOf(procName):
    openFile = subprocess.Popen('pgrep %s' % procName,
                                shell=True,
                                stdout=subprocess.PIPE).stdout
    pids = openFile.read()
    openFile.close()
    return [int(p) for p in pids.split()]

def examineProcesses():
    desktop = pyatspi.Registry.getDesktop(0)
    println(LEVEL_ALL, 'INFO: Desktop has %i apps:' % desktop.childCount)
    for i, app in enumerate(desktop):
        pid = app.get_process_id()
        cmd = getCmdline(pid)
        fds = getOpenFDCount(pid)
        try:
            name = app.name
        except:
            name = 'ERROR: Could not get name'
        else:
            if name == '':
                name = 'WARNING: Possible hang'
        println(LEVEL_ALL, '%3i. %s (pid: %s) %s file descriptors: %i' \
                    % (i+1, name, pid, cmd, fds))

    # Other 'suspect' processes which might not show up as accessible apps.
    otherApps = ['apport']
    for app in otherApps:
        pids = pidOf(app)
        if not pids:
            println(LEVEL_ALL, 'INFO: no pid for %s' % app)
            continue

        for pid in pids:
            cmd = getCmdline(pid)
            fds = getOpenFDCount(pid)
            println(LEVEL_ALL, 'INFO: %s (pid: %s) %s file descriptors: %i' \
                        % (app, pid, cmd, fds))
