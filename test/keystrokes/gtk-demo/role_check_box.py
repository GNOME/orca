#!/usr/bin/python

"""Test of checkbox output using the gtk-demo Paned Widgets demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Paned Widgets demo
#
sequence.append(TypeAction           ("Paned Widgets"))
sequence.append(WaitForFocus        ([1, 0, 0, 0], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# When the demo comes up, interact with a few check boxes
#
#sequence.append(WaitForWindowActivate("Panes",None))
# "Hi there"
sequence.append(WaitForFocus        ([1, 0, 0, 0, 0, 0], pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction         ("Tab"))

# "Resize"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 4], pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 1, 0, 4],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 1, 0, 4],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "Resize"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 1], pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 1, 0, 1],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 1, 0, 1],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "Shrink"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 3], pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction         ("Tab"))
# "Shrink"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 0], pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "Resize"
sequence.append(WaitForFocus        ([1, 0, 2, 0, 4], pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 2, 0, 4],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 2, 0, 4],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction         ("Tab"))

# "Resize"
sequence.append(WaitForFocus        ([1, 0, 2, 0, 1], pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 2, 0, 1],
                             pyatspi.ROLE_CHECK_BOX))
sequence.append(TypeAction           (" "))
sequence.append(WaitForEvent("object:state-changed:checked",
                             [1, 0, 2, 0, 1],
                             pyatspi.ROLE_CHECK_BOX))

########################################################################
# Close the Panes demo window
#
sequence.append(KeyComboAction         ("<Alt>F4"))

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
