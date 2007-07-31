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
sequence.append(TypeAction("UI Manager"))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Once the UI Manager window is up, open the file menu, arrow down
# over the menu items, and then close the menu.
#
#sequence.append(WaitForWindowActivate("UI Manager"))

sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>f"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Save As...", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Dismiss the menu and close the UI Manager demo
#
sequence.append(KeyComboAction("Escape"))

sequence.append(WaitForFocus("close", acc_role=pyatspi.ROLE_PUSH_BUTTON))
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

sequence.start()
