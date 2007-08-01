#!/usr/bin/python

"""Test of multiline editable text using the gtk-demo Application Main Window
   demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, go to the text area and type.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("This is a test.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("I'm just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("The keyboard sure can get sticky.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("Tis this and thus thou art in Rome?", 500))
sequence.append(KeyComboAction("Return", 500))

# Go to the beginning of the text area and arrow past "This "
#
sequence.append(KeyComboAction("<Control>Home", 500))
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("Right", 500))
sequence.append(KeyComboAction("Right", 500))

# Select "is a test" word by word
#
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))

# Unselect "test"
#
sequence.append(KeyComboAction("<Shift><Control>Left", 500))

# Arrow down to "I'm typing away..."
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))

# Select to the end of the line
#
sequence.append(KeyComboAction("<Shift>End", 500))

# Right arrow to the beginning of the next line
#
sequence.append(KeyComboAction("Right", 500))

# Try a "SayAll"
#
sequence.append(KeyComboAction("KP_Add", 500))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
