#!/usr/bin/python

"""Test of toggle button output using the gtk-demo Expander button demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Expander demo
#
sequence.append(TypeAction           ("Expander"))
sequence.append(WaitForFocus        ([1, 0, 0, 0], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# Once the demo is up, toggle the toggle button a few times and then
# close the dialog.
#
#sequence.append(WaitForWindowActivate("GtkExpander",None))
# "Details"
sequence.append(WaitForFocus        ([1, 0, 0, 1], pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction         ("Return"))

sequence.append(WaitForEvent("object:state-changed:expanded",
                             [1, 0, 0, 1],
                             pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction         ("Return"))

sequence.append(WaitForEvent("object:state-changed:expanded",
                             [1, 0, 0, 1],
                             pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction         ("Return"))

sequence.append(WaitForEvent("object:state-changed:expanded",
                             [1, 0, 0, 1],
                             pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction         ("Return"))

sequence.append(WaitForEvent("object:state-changed:expanded",
                             [1, 0, 0, 1],
                             pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction         ("Tab"))

# "Close"
sequence.append(WaitForFocus        ([1, 0, 2, 0], pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction         ("Return"))

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
