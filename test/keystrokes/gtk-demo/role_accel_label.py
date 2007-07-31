#!/usr/bin/python

"""Test of menu accelerator label output using the gtk-demo UI Manager
   demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running.  Down arrow to the UI Manager demo and
# invoke it.
#
sequence.append(KeyComboAction         ("End"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# Once the UI Manager window is up, open the file menu, arrow down
# over the menu items, and then close the menu.
#
#sequence.append(WaitForWindowActivate("UI Manager",None))
# "close"
sequence.append(WaitForFocus        ([1, 0, 3, 0], pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction         ("<Alt>f"))
# "New"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 1], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction         ("Down"))
# "Open"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 2], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction         ("Down"))
# "Save"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 3], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction         ("Down"))
# "Save As..."
sequence.append(WaitForFocus        ([1, 0, 0, 0, 4], pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction         ("Down"))
# "Quit"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 6], pyatspi.ROLE_MENU_ITEM))

########################################################################
# Dismiss the menu and close the UI Manager demo
#
sequence.append(KeyComboAction         ("Escape"))
# "close"
sequence.append(WaitForFocus        ([1, 0, 3, 0], pyatspi.ROLE_PUSH_BUTTON))
sequence.append(TypeAction           (" "))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Home"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))

sequence.start()
