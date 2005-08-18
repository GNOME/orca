# Orca Tools
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

"""Uses the AT-SPI to listen for keyboard events and sends an output
of them to stdout.  To quit, press F12.
"""

import os
import signal
import sys
import time

import orca.core
import orca.kbd

def processKeyEvent(event):
    """
    Arguments:
    - event: an at-spi DeviceEvent

    Returns True if the event should be consumed.
    """

    if event.event_string == "F12":
        exit(None, None)
        
    print "KEYEVENT: type=%d" % event.type
    print "          hw_code=%d" % event.hw_code
    print "          modifiers=%d" % event.modifiers
    print "          event_string=(%s)" % event.event_string
    print "          is_text=%s" % event.is_text
    print "          time=%f" % time.time()

    return False

def exit(signum, frame):
    orca.core.bonobo.main_quit()
    sys.exit()

def init():
    # Record information about the system where this was run.
    #
    pipe = os.popen("uname -a")
    sysinfo = pipe.readlines()
    pipe.close()
    print "# DATE=%s" % time.strftime('%X %x %Z')
    print "# SYSTEM=%s" % sysinfo[0]
    
    orca.core.init()
    orca.kbd.init(processKeyEvent)

def go():
    orca.core.bonobo.main()

def main():
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGQUIT, exit)

    init()
    go()

if __name__ == "__main__":
    main()
