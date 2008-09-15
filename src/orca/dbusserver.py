# Orca
#
# Copyright 2008 Sun Microsystems Inc.
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

"""Exposes Orca as a DBus service for testing and watchdog purposes."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

import dbus
import dbus.service
import dbus.mainloop.glib

import debug
import settings

# Handlers for logging speech and braille output.
#
loggingFileHandlers = {}
loggingStreamHandlers = {}

# pylint: disable-msg=R0923
# Server: Interface not implemented

class Server(dbus.service.Object):

    def __init__(self, object_path, bus_name):
        dbus.service.Object.__init__(self, None, object_path, bus_name)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='si', out_signature='')
    def setDebug(self, debugFile, debugLevel):
        """Sets the file to send detailed debug information."""
        if not settings.enableRemoteLogging:
            return
        debug.println(debug.LEVEL_FINEST,
                      "DBus Logging.setDebug(%s, %d)" \
                      % (debugFile, debugLevel))
        if debug.debugFile:
            debug.debugFile.close()
            debug.debugFile = None
        if debugFile and len(debugFile):
            debug.debugFile = open('%s.debug' % debugFile, 'w', 0)
        debug.debugLevel = debugLevel

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='s', out_signature='')
    def setLogFile(self, logFile):
        """Sets the file to send speech and braille logging information."""
        if not settings.enableRemoteLogging:
            return
        import logging
        debug.println(debug.LEVEL_FINEST,
                      "DBus Logging.setLogFile(%s)" % logFile)
        for logger in ['braille', 'speech']:
            log = logging.getLogger(logger)
            formatter = logging.Formatter('%(message)s')
            try:
                loggingFileHandlers[logger].flush()
                loggingFileHandlers[logger].close()
                log.removeHandler(loggingFileHandlers[logger])
            except:
                pass
            if logFile and len(logFile):
                loggingFileHandlers[logger] = logging.FileHandler(
                    '%s.%s' % (logFile, logger), 'w')
                loggingFileHandlers[logger].setFormatter(formatter)
                log.addHandler(loggingFileHandlers[logger])
            log.setLevel(logging.INFO)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='', out_signature='')
    def startRecording(self):
        """Tells Orca to start logging speech and braille output."""
        if not settings.enableRemoteLogging:
            return
        debug.println(debug.LEVEL_FINEST, "DBus Logging.startRecording")
        import logging
        import StringIO
        for logger in ['braille', 'speech']:
            log = logging.getLogger(logger)
            try:
                [stringIO, handler] = loggingStreamHandlers[logger]
                handler.close()
                log.removeHandler(handler)
                stringIO.close()
            except:
                pass
            formatter = logging.Formatter('%(message)s')
            stringIO = StringIO.StringIO()
            handler = logging.StreamHandler(stringIO)
            handler.setFormatter(formatter)
            log.addHandler(handler)
            loggingStreamHandlers[logger] = [stringIO, handler]
            log.setLevel(logging.INFO)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='', out_signature='s')
    def stopRecording(self):
        """Tells Orca to stop logging speech and braille output and
        to return whatever was recorded since the last call to
        startRecording."""
        if not settings.enableRemoteLogging:
            return ""
        debug.println(debug.LEVEL_FINEST, "DBus Logging.stopRecording")
        import logging
        import StringIO
        result = ''
        for logger in ['braille', 'speech']:
            log = logging.getLogger(logger)
            try:
                [stringIO, handler] = loggingStreamHandlers[logger]
                handler.flush()
                handler.close()
                log.removeHandler(handler)
                result += stringIO.getvalue()
                stringIO.close()
            except:
                debug.printException(debug.LEVEL_OFF)
            stringIO = StringIO.StringIO()
        return result

obj = None

def init():
    """Sets up the Orca DBus service.  This will only take effect once
    the Orca main loop starts."""

    global obj

    if obj:
        return

    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        name = dbus.service.BusName('org.gnome.Orca', bus=bus)
        obj = Server('/', name)
    except:
        debug.println(debug.LEVEL_WARNING,
                      "dbusserver.py: Could not initialize DBus server")

def shutdown():
    pass
