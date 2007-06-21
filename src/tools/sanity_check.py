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

"""Performs a sanity check on a keystroke file."""

# Keystroke modifier keys.
#
# ToDo (LMS) make sure the list is complete. Meta keys are defined
# in the AT-SPI, but I don't know what they map to, except for Esc.
#
modifierKeys = [ "(Control_L)", "(Shift_L)", "(Alt_L)", \
                 "(Control_R)", "(Shift_R)", "(Alt_R)",
                 "(KP_Insert)"]

def main():
    """Expects to find lines of the following form on stdin:

    KEYEVENT: type=1
              hw_code=38
              modifiers=0
              event_string=(a)
              is_text=True
              time=111223442.987959
    """

    keycodePresses = {}
    keyPressCount = 0
    
    lineCount = 0
    errorCount = 0
    try:
        while True:
            line = raw_input()
            lineCount += 1            
            if line.startswith("KEYEVENT:"):
                type = eval(line[-1])
            
                line = raw_input()
                hw_code = eval(line[line.index("=") + 1 :])
                
                line = raw_input() # modifiers
            
                line = raw_input()
                event_string = line[line.index("=") + 1 :]
            
                line = raw_input() # is_text            
                line = raw_input() # event_time

                # Record the line number for each key press we receive.
                # These are stored in a dictionary where the keys are
                # key codes.
                #
                if type == 0:
                    if keycodePresses.has_key(hw_code):
                        [line, string] = keycodePresses[hw_code]
                        print "ERROR: Too many key presses for " \
                              + "code=%d string=%s" % (hw_code, string)
                        print "       First press at line=%d" % line
                        print "       Second press at line=%d" % lineCount
                        errorCount += 1
                    else:
                        keycodePresses[hw_code] = [lineCount, event_string]
                elif keycodePresses.has_key(hw_code):
                    del keycodePresses[hw_code]
                else:
                    print "ERROR: No key press for key release for " \
                          + "code=%d string=%s at line=%d" \
                          % (hw_code, event_string, lineCount)
                    errorCount += 1

                # Verify all key presses, except for modifier keys,
                # have been released.
                if modifierKeys.count(event_string) == 0:
                    if type == 0: # key press
                        keyPressCount = keyPressCount + 1
                    else:
                        keyPressCount = keyPressCount - 1
                        
                if type == 1 and keyPressCount != 0:
                    # There is still a key pressed.
                    print "ERROR: key still pressed when current key is released: " \
                          + "code=%d key still pressed=%s at line=%d" \
                          % (hw_code, event_string, lineCount)
                    errorCount += 1

                lineCount += 5
    except EOFError:
        pass

    for key in keycodePresses.keys():
        [line, string] = keycodePresses[key]
        print "ERROR: No key release for key press for " \
              + "code=%d string=%s at line=%d" % (key, string, line)
        errorCount += 1
        
    print "Checked", lineCount, "lines. ", errorCount, "error(s)."

    
if __name__ == "__main__":
    main()
