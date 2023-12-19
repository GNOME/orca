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
import re
import subprocess
import sys
import types

from datetime import datetime

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .ax_object import AXObject
from .ax_utilities import AXUtilities

# Used to turn off all debugging.
#
LEVEL_OFF = 10000

# Used to describe events of considerable importance and which will prevent
# normal program execution.
#
LEVEL_SEVERE = 1000

# Used to describe events of interest to end users or system managers or which
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
# aspects of whether a particular feature (e.g., speech, braille, etc.)
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

# What role(s) should be traced if traceit is being used. By
# default, we'll trace everything. An example of what you might wish
# to do to narrow things down, if you know buttons trigger the problem:
#
# TRACE_ROLES = [Atspi.Role.PUSH_BUTTON, Atspi.Role.TOGGLE_BUTTON]
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

def _asString(obj):
    if isinstance(obj, Atspi.Accessible):
        result = AXObject.get_role_name(obj)
        name = AXObject.get_name(obj)
        if name:
            result += f": '{name}'"
        if not result:
            result = "DEAD"

        return f"[{result}]"

    if isinstance(obj, Atspi.Event):
        return (
            f"{obj.type} for {_asString(obj.source)} in "
            f"{_asString(AXObject.get_application(obj.source))} "
            f"({obj.detail1}, {obj.detail2}, {_asString(obj.any_data)})"
        )

    if isinstance(obj, (Atspi.Role, Atspi.StateType, Atspi.CollectionMatchType)):
        return obj.value_nick

    if isinstance(obj, list):
        return f"[{', '.join(map(_asString, obj))}]"

    if isinstance(obj, types.FunctionType):
        if hasattr(obj, "__self__"):
            return f"{obj.__module__}.{obj.__self__.__class__.__name__}.{obj.__name__}"
        return f"{obj.__module__}.{obj.__name__}"

    if isinstance(obj, types.MethodType):
        if hasattr(obj, "__self__"):
            return f"{obj.__self__.__class__.__name__}.{obj.__name__}"
        return f"{obj.__name__}"

    if isinstance(obj, types.FrameType):
        module_name = inspect.getmodulename(obj.f_code.co_filename)
        return f"{module_name}.{obj.f_code.co_name}"

    if isinstance(obj, inspect.FrameInfo):
        module_name = inspect.getmodulename(obj.filename)
        return f"{module_name}.{obj.function}"

    return str(obj)

def printTokens(level, tokens, timestamp=False, stack=False):
    if level < debugLevel:
        return

    text = " ".join(map(_asString, tokens))
    text = re.sub(r"[ \u00A0]+", " ", text)
    text = re.sub(r" (?=[,.:)])(?![\n])", "", text)
    println(level, text, timestamp, stack)

def printMessage(level, text, timestamp=False, stack=False):
    if level < debugLevel:
        return

    println(level, text, timestamp, stack)

def _stackAsString(max_frames=4):
    callers = []
    current_module = inspect.getmodule(inspect.currentframe())
    stack = inspect.stack()
    for i in range(1, len(stack)):
        frame = stack[i]
        module = inspect.getmodule(frame[0])
        if module == current_module:
            continue
        if frame.function == 'main':
            continue
        if module is None or module.__name__ is None:
            continue
        callers.append(frame)
        if len(callers) >= max_frames:
            break

    callers.reverse()
    return " > ".join(map(_asString, callers))

def println(level, text="", timestamp=False, stack=False):
    """Prints the text to stderr unless debug is enabled.

    If debug is enabled the text will be redirected to the
    file debugFile.

    Arguments:
    - level: the accepted debug level
    - text: the text to print (default is a blank line)
    """

    if level >= debugLevel:
        text = text.replace("\ufffc", "[OBJ]")
        if timestamp:
            text = text.replace("\n", f"\n{' ' * 18}")
            text = f"{datetime.now().strftime('%H:%M:%S.%f')} - {text}"
        if stack:
            text += f" {_stackAsString()}"

        if debugFile:
            try:
                debugFile.writelines([text, "\n"])
            except TypeError:
                text = "TypeError when trying to write text"
                debugFile.writelines([text, "\n"])
            except Exception:
                text = "Exception when trying to write text"
                debugFile.writelines([text, "\n"])
        else:
            try:
                sys.stderr.writelines([text, "\n"])
            except TypeError:
                text = "TypeError when trying to write text"
                sys.stderr.writelines([text, "\n"])
            except Exception:
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

    callString = (
        f"CALL:   {inspect.getmodulename(prev[1])}.{prev[3]} (line {prev[2]})"
        f" -> {inspect.getmodulename(current[1])}.{current[3]}{fArgs}"
    )
    string = f"{callString}\nRESULT: {result}"
    println(level, f"{string}")

def printObjectEvent(level, event, sourceInfo=None, timestamp=False):
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

    anydata = event.any_data
    if isinstance(anydata, str) and len(anydata) > 100:
        anydata = f"{anydata[0:100]} (...)"

    text = "OBJECT EVENT: %s (%d, %d, %s)" \
           % (event.type, event.detail1, event.detail2, anydata)
    println(level, text, timestamp)

    if sourceInfo:
        println(level, f"{' ' * 18}{sourceInfo}", timestamp)

def printDetails(level, indent, accessible, includeApp=True, timestamp=False):
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
                getAccessibleDetails(level, accessible, indent, includeApp),
                timestamp)

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
        string = indent + f"app='{AXObject.application_as_string(acc)}' "
    else:
        string = indent

    if AXObject.is_dead(acc):
        string += "(exception fetching data)"
        return string

    name_string = "name='%s'".replace("\n", "\\n") % AXObject.get_name(acc)
    desc_string = "%sdescription='%s'".replace("\n", "\\n") % \
        (indent, AXObject.get_description(acc))
    role_string = f"role='{AXObject.get_role_name(acc)}'"
    path_string = f"{indent}path={AXObject.get_path(acc)}"
    state_string = f"{indent}states='{AXObject.state_set_as_string(acc)}'"
    rel_string = f"{indent}relations='{AXObject.relations_as_string(acc)}'"
    actions_string = f"{indent}actions='{AXObject.actions_as_string(acc)}'"
    iface_string = f"{indent}interfaces='{AXObject.supported_interfaces_as_string(acc)}'"
    attr_string = f"{indent}attributes='{AXObject.attributes_as_string(acc)}'"
    string += (
        f"{name_string} {role_string}\n"
        f"{desc_string}\n"
        f"{state_string}\n"
        f"{rel_string}\n"
        f"{actions_string}\n"
        f"{iface_string}\n"
        f"{attr_string}\n"
        f"{path_string}\n"
    )
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
    except Exception:
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
        app = AXObject.get_application(eventSource)
        if AXObject.get_name(app) not in TRACE_APPS:
            return False

    if TRACE_ROLES and AXObject.get_role(eventSource) not in TRACE_ROLES:
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
    if TRACE_MODULES and module.split('.')[0] not in TRACE_MODULES:
        return traceit
    if event not in ['call', 'line', 'return']:
        return traceit

    lineno = frame.f_lineno
    line = linecache.getline(filename, lineno).rstrip()
    output = f'TRACE {module}:{lineno}: {line}'

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
            output += f'\n  ARG {key}={values[i]}'

    lineElements = line.strip().split()
    if lineElements and lineElements[0] == 'return':
        if event == 'line':
            return traceit
        output = f'{output} (rv: {arg})'

    println(LEVEL_ALL, output)

    return traceit

def getOpenFDCount(pid):
    procs = subprocess.check_output([ 'lsof', '-w', '-Ff', '-p', str(pid)])
    procs = procs.decode('UTF-8').split('\n')
    files = list(filter(lambda s: s and s[0] == 'f' and s[1:].isdigit(), procs))

    return len(files)

def getCmdline(pid):
    try:
        openFile = os.popen(f'cat /proc/{pid}/cmdline')
        cmdline = openFile.read()
        openFile.close()
    except Exception:
        cmdline = '(Could not obtain cmdline)'
    cmdline = cmdline.replace('\x00', ' ')

    return cmdline

def pidOf(procName):
    openFile = subprocess.Popen(f'pgrep {procName}',
                                shell=True,
                                stdout=subprocess.PIPE).stdout
    pids = openFile.read()
    openFile.close()
    return [int(p) for p in pids.split()]

def examineProcesses(force=False):
    if force:
        level = LEVEL_OFF
    else:
        level = LEVEL_ALL

    desktop = AXUtilities.get_desktop()
    println(level, 'INFO: Desktop has %i apps:' % AXObject.get_child_count(desktop), True)
    for i, app in enumerate(AXObject.iter_children(desktop)):
        pid = AXObject.get_process_id(app)
        cmd = getCmdline(pid)
        fds = getOpenFDCount(pid)
        name = AXObject.get_name(app)
        if name == '':
            name = 'WARNING: Possible hang or dead app'
        println(level, '%3i. %s (pid: %s) %s file descriptors: %i' \
                    % (i+1, name, pid, cmd, fds), True)

    # Other 'suspect' processes which might not show up as accessible apps.
    otherApps = ['apport']
    for app in otherApps:
        pids = pidOf(app)
        if not pids:
            println(level, f'INFO: no pid for {app}', True)
            continue

        for pid in pids:
            cmd = getCmdline(pid)
            fds = getOpenFDCount(pid)
            println(level, 'INFO: %s (pid: %s) %s file descriptors: %i' \
                        % (app, pid, cmd, fds), True)
