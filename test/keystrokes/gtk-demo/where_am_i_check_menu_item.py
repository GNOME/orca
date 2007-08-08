#!/usr/bin/python

"""Test "Where Am I" on a menu checkbox using the gtk-demo Application Main
   Window demo.
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
# When the demo comes up, go to the Bold check menu item in the
# Preferences menu.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>p"))

sequence.append(WaitForFocus("Color", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Up"))
########################################################################
# Once we have focus on the "Bold" menu item, do a "where am i"
sequence.append(WaitForFocus("Bold", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Now do detailed information "where am i", double press KP_Enter.
# But first, wait 3 seconds.

sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
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
