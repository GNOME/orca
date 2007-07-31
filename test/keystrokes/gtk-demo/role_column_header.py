#!/usr/bin/python

"""Test of column header output using the gtk-demo List Store demo
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
# Once gtk-demo is running, invoke the List Store demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View"))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("List Store"))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the GtkListStore demo window appears, navigate the table headers
# 
#sequence.append(WaitForWindowActivate("GtkListStore demo",None))
# "Bug number"
sequence.append(WaitForFocus("Bug number",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitForFocus("Severity",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitForFocus("Description",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))

########################################################################
# Now go down into the table to see if we read the column headers as we
# move from column to column.
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction("<Control>Left", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(KeyComboAction("<Control>Left", 500))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(KeyComboAction("<Control>Left", 500))

########################################################################
# Close the GtkListStore demo
#
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View"))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

sequence.start()
