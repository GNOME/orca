#!/usr/bin/python

"""Test "Where Am I" in a tree table using the gtk-demo Tree Store demo 
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
# Once gtk-demo is running, invoke the Tree Store demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree Store", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Card planning sheet demo window appears, navigate the table
# cells.  Expand and collapse them, too.
#
#sequence.append(WaitForWindowActivate("Card planning sheet",None))
sequence.append(WaitForFocus("Holiday",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("<Shift>Left", 500))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(KeyComboAction("<Shift>Right", 500))

sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("<Shift>Left", 500))

sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("<Shift>Right", 500))

sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

sequence.append(KeyComboAction("Down", 500))

sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitAction("object:active-descendants-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))


########################################################################
# Close the Card planning sheet demo
#
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
