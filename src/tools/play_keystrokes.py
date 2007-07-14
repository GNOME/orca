# Orca Tools
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

import orca.atspi

# Maximum time, in seconds, to sleep.  This allows us to compress the
# playback some for users who took their sweet time entering key strokes.
#
MAX_SLEEP = 10.0

# Minimum time to wait for a keypress.  This helps ensure that
# we don't skip things (e.g., the toolkit can skip over a list
# item and not let us know about intervening items) or generate
# oddness, such as text areas compressing text input events
# (e.g., "th" instead of two distinct events "t" and "h" when
# typing quickly).
#
MIN_PRESS_DELAY = 0.35

# Factor to speed up the playback.  This will compress time by the
# given amount.  For example, 2.0 will play the events back twice
# as fast.
#
SPEED_UP  = 1.0

def exit(signum, frame):
    sys.exit()

def go():
    """Expects to find lines of the following form on stdin:

    KEYEVENT: type=1
              hw_code=38
              modifiers=0
              event_string=(a)
              is_text=True
              time=111223442.987959

    WAIT: wait_time=180
    """

    d = orca.atspi.Registry().registry.getDeviceEventController()

    while True:
        line = raw_input()

        if line.startswith("WAIT:"):
            # Sleep for the specified wait time.  This can be used
            # to handle applications that have unexpected delays in
            # responding to keyboard actions.  For example, OOo can
            # take a long time to open a menu sometimes.
            #
            waitTime = eval(line[line.index("=") + 1 :])
            time.sleep(waitTime)

        elif line.startswith("KEYEVENT:"):
            type = eval(line[-1])

            line = raw_input()
            hw_code = eval(line[line.index("=") + 1 :])

            line = raw_input() # modifiers
            line = raw_input() # event_string
            line = raw_input() # is_text

            line = raw_input()
            delta = eval(line[line.index("=") + 1 :])
            delta = min(MAX_SLEEP, delta / SPEED_UP)
            if type == 0:
                delta = max(MIN_PRESS_DELAY, delta)
            if delta > 0:
                time.sleep(delta)
            d.generateKeyboardEvent(hw_code, "", type)

def main():
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGQUIT, exit)

    try:
        go()
    except EOFError:
        pass

if __name__ == "__main__":
    main()
