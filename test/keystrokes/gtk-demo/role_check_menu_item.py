#!/usr/bin/python

"""Test of menu checkbox output using the gtk-demo Application Main Window
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
# Once gtk-demo is running, invoke the Application Main Window demo.
# We need the Down/Up to force focus on the tree item
#
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Up"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# When the demo comes up, go to the Bold check menu item in the
# Preferences menu.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
# "Open"
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 0], pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction         ("<Alt>p"))

# "Color"
sequence.append(WaitForFocus        ([1, 0, 3, 1, 1], pyatspi.ROLE_MENU))
sequence.append(KeyComboAction         ("Up"))

# "Bold"
sequence.append(WaitForFocus        ([1, 0, 3, 1, 3], pyatspi.ROLE_CHECK_MENU_ITEM))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction         ("Escape"))
sequence.append(WaitForFocus        ([1, 0, 2, 0, 0, 0], pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction         ("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

sequence.start()
