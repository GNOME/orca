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

"""Uses the AT-SPI to play keystrokes recorded using record_keystrokes.py.
Quits automatically when no more keystrokes can be read."""

import os
import signal
import sys
import time

import orca.core

# Maximum time, in seconds, to sleep.  This allows us to compress the
# playback some for users who took their sweet time entering key strokes.
#
MAX_SLEEP = 1.0

# Factor to speed up the playback.  This will compress time by the
# given amount.
#
SPEED_UP  = 2.0

def exit(signum, frame):
    sys.exit()

def init():
    orca.core.init()

def go():
    """Expects to find lines of the following form on stdin:

    KEYEVENT: type=1
              hw_code=38
              modifiers=0
              event_string=(a)
              is_text=True
              time=111223442.987959
    """

    d = orca.core.registry.getDeviceEventController()

    lastTime = None
    
    while True:
        line = raw_input()
        if line.startswith("KEYEVENT:"):
            type = eval(line[-1])
            
            line = raw_input()
            hw_code = eval(line[line.index("=") + 1 :])
                
            line = raw_input() # modifiers
            line = raw_input() # event_string
            line = raw_input() # is_text
            
            line = raw_input()
            event_time = eval(line[line.index("=") + 1 :])
                
            if not lastTime:
                lastTime = event_time

            delta = min(MAX_SLEEP, (event_time - lastTime) / SPEED_UP)
            if delta > 0:
                time.sleep(delta)
            lastTime = event_time

            d.generateKeyboardEvent(hw_code, "", type)

def main():
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGQUIT, exit)

    init()
    try:
        go()
    except EOFError:
        pass
    
if __name__ == "__main__":
    main()
