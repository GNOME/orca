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

    def __init__(self, filePrefix):
        self._logger = orca.getLogger()
        self._logNames = ['braille', 'speech']
        self._filePrefix = filePrefix

        DBusGMainLoop(set_as_default=True)
        busname = dbus.service.BusName('org.gnome.Orca', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, busname, '/org/gnome/Orca')

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logger', in_signature='', out_signature='')
    def startRecording(self):
        for name in self._logNames:
            self._logger.clearLog(name)

    @dbus.service.method(dbus_interface='org.gnome.Orca.Logger', in_signature='', out_signature='s')
    def stopRecording(self):
        contents = ''
        for name in self._logNames:
            content = self._logger.getLogContent(name)
            contents += content
            fileName = open('%s.%s' % (self._filePrefix, name), 'a', encoding='utf-8')
            fileName.writelines(content)
            fileName.close()

        return contents

def main():
    sys.argv[0] = 'orca'

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user-prefs", action="store")
    parser.add_argument("--debug-file", action="store")
    args = parser.parse_args()

    orca.debug.debugFile = open('%s.debug' % args.debug_file, 'w')

    manager = orca.getSettingsManager()
    manager.activate(args.user_prefs)
    sys.path.insert(0, manager.getPrefsDir())

    service = LoggerService(args.debug_file)

    return orca.main()

if __name__ == "__main__":
    sys.exit(main())
