#!/usr/bin/python

"""Test of menu accelerator label output using the gtk-demo UI Manager
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
# Once gtk-demo is running, invoke the UI Manager demo.
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("UI Manager", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the UI Manager window is up, open the file menu, arrow down
# over the menu items, and then close the menu.
#
#sequence.append(WaitForWindowActivate("UI Manager"))

sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>f"))

########################################################################
# Once we have focus on the "New" menu item, do a "where am i"
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Now do detailed information "where am i", double press KP_Enter.
# But first, wait 3 seconds.

sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Dismiss the menu.
#
sequence.append(KeyComboAction("Escape"))

########################################################################
# Title bar, KP_Insert+KP_Enter.
# But first, wait for close button to gain focus.
sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyPressAction(0, 90, "KP_Insert"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyReleaseAction( 0, 90, "KP_Insert"))

########################################################################
# Close the UI Manager demo
sequence.append(TypeAction(" "))

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
