# Orca
#
# Copyright 2008 Sun Microsystems Inc.
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

"""Exposes Orca as a DBus service for testing and watchdog purposes."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

import dbus
import dbus.service
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

import debug
import logger

# pylint: disable-msg=R0923
# Server: Interface not implemented

bus = None
name = None
obj = None

class Server(dbus.service.Object):

    def __init__(self, object_path, bus_name):
        dbus.service.Object.__init__(self, None, object_path, bus_name)
        self._logger = logger.Logger()

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='si', out_signature='')
    def setDebug(self, debugFile, debugLevel):
        self._logger.setDebug(debugFile, debugLevel)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='s', out_signature='')
    def setLogFile(self, logFile):
        self._logger.setLogFile(logFile)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='', out_signature='')
    def startRecording(self):
        self._logger.startRecording()

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logging',
                         in_signature='', out_signature='s')
    def stopRecording(self):
        return self._logger.stopRecording()

def init():
    """Sets up the Orca DBus service.  This will only take effect once
    the Orca main loop starts."""

    global bus
    global name
    global obj

    if obj or bus or name:
        return

    try:
        bus = dbus.SessionBus()
        name = dbus.service.BusName('org.gnome.Orca',
                                    bus=bus,
                                    allow_replacement=False,
                                    replace_existing=False)
        obj = Server('/', name)
    except:
        debug.println(debug.LEVEL_WARNING,
                      "dbusserver.py: Could not initialize DBus server")
        debug.printException(debug.LEVEL_WARNING)

def shutdown():
    pass

def main():
    import pyatspi
    init()
    debug.println(debug.LEVEL_FINEST, 'INFO: dbusserver starting registry')
    pyatspi.Registry.start()

if __name__ == "__main__":
    main()
