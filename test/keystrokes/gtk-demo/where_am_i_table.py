#!/usr/bin/python

"""Test "Where Am I" on a table using the gtk-demo Editable Cells demo
   under the Tree View area.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Editable Cells demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Editable Cells", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Shopping list demo window appears, navigate the table cells
# using both read table cell row and read table cell (Insert+F11).
#
#sequence.append(WaitForWindowActivate("Shopping list",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction("Down", 1000))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("<Control>Right", 1000))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Up", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Up", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Up", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(KeyComboAction("Up", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("<Control>Left", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Down", 500))

########################################################################
# Close the Shopping list demo
#
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(KeyComboAction("<Alt>F4", 1000))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
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
