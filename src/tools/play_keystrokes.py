# Orca Tools
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

import orca.debug as debug
import orca.atspi

# Time to sleep after a key is pressed
#
KEY_PRESS_SLEEP_TIME = 0.2

# Time to sleep after a key is released
#
KEY_RELEASE_SLEEP_TIME = 3.0

# Keystroke modifier keys.
#
# ToDo (LMS) make sure the list is complete. Meta keys are defined
# in the AT-SPI, but I don't know what they map to, except for Esc.
#
modifierKeys = [ "(Control_L)", "(Shift_L)", "(Alt_L)", \
                 "(Control_R)", "(Shift_R)", "(Alt_R)" ]

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

    keyPressCount = 0
    sleepTime = 0
    
    while True:
        line = raw_input()
        
        if line.startswith("WAIT:"):
            # Sleep for the specified wait time. This allows Orca
            # to speak and braille long documents.
            waitTime = eval(line[line.index("=") + 1 :])
            time.sleep(waitTime)

        elif line.startswith("KEYEVENT:"):
            type = eval(line[-1])
            
            line = raw_input()
            hw_code = eval(line[line.index("=") + 1 :])
                
            line = raw_input() # modifiers
            line = raw_input() # event_string
            keyString = line[line.index("=") + 1 :]

            if modifierKeys.count(keyString) == 0:
                # Keep track of the number of keys pressed down.
                if type == 0:
                    keyPressCount = keyPressCount + 1
                else:
                    keyPressCount = keyPressCount - 1

            line = raw_input() # is_text
            line = raw_input() # time

            # Play the keystroke.
            d.generateKeyboardEvent(hw_code, "", type)

            # Sleep after the keystroke.
            if type == 0: # key press
                sleepTime = KEY_PRESS_SLEEP_TIME
            else: # key release
                if keyPressCount == 0:
                    sleepTime = KEY_RELEASE_SLEEP_TIME
                else: 
                    # A non-modifier key is still pressed, so don't sleep
                    # so long that auto-repeat occurs.
                    sleepTime = KEY_PRESS_SLEEP_TIME
                    
            time.sleep(sleepTime)

def main():
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGQUIT, exit)

    try:
        go()
    except EOFError:
        pass
    
if __name__ == "__main__":
    main()
