#!/usr/bin/python3

# N.B. Orca's only use of dbus-python is this logger service which is only
# used by the regression tests. It does not introduce a dependency, is not
# encountered by end users, and will be removed in favor for pygi once bugs
# 656325 and 656330 are resolved.

import argparse
import dbus
import dbus.service
import sys

from orca import orca
from dbus.mainloop.glib import DBusGMainLoop

class LoggerService(dbus.service.Object):

    def __init__(self):
        self._logger = orca.getLogger()

        DBusGMainLoop(set_as_default=True)
        busname = dbus.service.BusName('org.gnome.Orca', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, busname, '/org/gnome/Orca')

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logger', in_signature='', out_signature='')
    def startRecording(self):
        names = self._logger.getLogNames()
        for name in names:
            self._logger.clearLog(name)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logger', in_signature='', out_signature='s')
    def stopRecording(self):
        contents = ''
        names = self._logger.getLogNames()
        for name in names:
            contents += self._logger.getLogContent(name)

        return contents

def main():
    sys.argv[0] = 'orca'

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user-prefs", action="store")
    args = parser.parse_args()

    manager = orca.getSettingsManager()
    manager.activate(args.user_prefs)
    sys.path.insert(0, manager.getPrefsDir())

    service = LoggerService()

    return orca.main()

if __name__ == "__main__":
    sys.exit(main())
