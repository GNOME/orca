#!/usr/bin/python

"""Test of spin button output using the gtk-demo Color Selector demo
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Color Selector
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Color Selector", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, navigate to the radio buttons
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("Change the above color",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_UNKNOWN))
sequence.append(KeyComboAction("Tab", 500))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SPIN_BUTTON))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SPIN_BUTTON))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Tab", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_SPIN_BUTTON))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Down", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Up", 500))
sequence.append(KeyComboAction("Tab", 500))

########################################################################
# Close the Color Chooser dialog
#
sequence.append(KeyComboAction         ("<Alt>c", 500))

########################################################################
# Close the Color Chooser demo
#
sequence.append(WaitForFocus("Change the above color",
                             acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
