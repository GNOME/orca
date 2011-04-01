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

import debug
import settings

import orca
_settingsManager = getattr(orca, '_settingsManager')

# Handlers for logging speech and braille output.
#
loggingFileHandlers = {}
loggingStreamHandlers = {}

# pylint: disable-msg=R0923
# Server: Interface not implemented

bus = None
name = None
obj = None

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

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='', out_signature='aas')
    def availableProfiles(self):
        return _settingsManager._backend.availableProfiles()

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='s', out_signature='a{sv}a{sv}a{sv}')
    def getPreferences(self, profile):
        return _settingsManager.getPreferences(profile)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='s', out_signature='a{sv}')
    def getGeneralSettings(self, profile='default'):
        return _settingsManager.getGeneralSettings(profile)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='s', out_signature='a{sv}')
    def getPronunciations(self, profile='default'):
        return _settingsManager.getPronunciations(profile)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='s', out_signature='a{sv}')
    def getKeybindings(self, profile='default'):
        return _settingsManager.getKeybindings(profile)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='s', out_signature='v')
    def getSetting(self, settingName):
        return _settingsManager.getSetting(settingName)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='sv', out_signature='')
    def setSetting(self, settingName, settingValue):
        _settingsManager.setSetting(settingName, settingValue)

        settingValueToUpdate = {dbus.Boolean:   bool,
                                dbus.Int32:     int,
                                dbus.String:    str,
                                dbus.Double:    float}

        _settingsManager.updateSetting(settingName, 
                settingValueToUpdate[type(settingValue)](settingValue))

        self.saveSettings()

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings')
    def saveSettings(self):
        _settingsManager.saveSettings(_settingsManager.general, 
                                      _settingsManager.pronunciations, 
                                      _settingsManager.keybindings)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='s', out_signature='')
    def setProfile(self, profile):
        _settingsManager.setProfile(profile)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Settings',
                         in_signature='', out_signature='')
    def quitOrca(self):
        orca.quitOrca()

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
    pyatspi.Registry.start()

if __name__ == "__main__":
    main()
