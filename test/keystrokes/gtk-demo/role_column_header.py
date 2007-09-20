#!/usr/bin/python

"""Test of column header output using the gtk-demo List Store demo
   under the Tree View area.
"""

from macaroon.playback import *

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
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("List Store", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the GtkListStore demo window appears, navigate the table headers.
# Presentation similar to the following should appear when each column
# header gets focus [[[BUG?: is the repeat of "Bug number ColumnHeader"
# in braille a bug???]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Bug number ColumnHeader Bug number ColumnHeader'
#      VISIBLE:  'Bug number ColumnHeader', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Bug number column header'
# 
#sequence.append(WaitForWindowActivate("GtkListStore demo",None))
sequence.append(WaitForFocus("Bug number",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Right"))

sequence.append(WaitForFocus("Severity",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitForFocus("Description",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))

########################################################################
# Now go down into the table to see if we read the column headers as we
# move from column to column.  You should end up in the "scrollable
# notebooks and hidden tabs" cell.
#
# When first going into the table, the entire row should be read.  The
# presentation in speech and braille should be as follows [[[BUG?: is the
# mentioning of "Fixed? ColumnHeader" in both speech and braille a bug?
# The actual column header we're under at this point is "Description"]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader
#                 < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'
#      VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Fixed? column header'
# SPEECH OUTPUT: 'Fixed? check box not checked  60482 Normal scrollable notebooks and hidden tabs'
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TABLE))

########################################################################
# Now move to the cell to the left containing the word "Normal".  The
# following should be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader Normal'
#      VISIBLE:  'Normal', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Severity column header'
# SPEECH OUTPUT: 'Normal'
#
sequence.append(KeyComboAction("<Control>Left", 5000))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille [[[BUG?: shouldn't the contents of
# the cell be spoken?]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'
#      VISIBLE:  'Normal scrollable notebooks and ', cursor=1
#      
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: '60482'
# SPEECH OUTPUT: 'Normal'
# SPEECH OUTPUT: 'scrollable notebooks and hidden tabs'
# SPEECH OUTPUT: 'row 1 of 14'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Now move to the cell to the left containing the number "60482".  The
# following should be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Bug number ColumnHeader 60482'
#      VISIBLE:  '60482', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Bug number column header'
# SPEECH OUTPUT: '60482'
#
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

########################################################################
# Now move to the cell to the left containing the checkbox.  The
# following should be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader < > Fixed?'
#      VISIBLE:  '< > Fixed?', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Fixed? column header'
# SPEECH OUTPUT: 'check box not checked '
#
sequence.append(KeyComboAction("<Control>Left", 500))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille [[[BUG?: shouldn't the contents/state
# of the cell be spoken?]]]:
#
# BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'
#      VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: '60482'
# SPEECH OUTPUT: 'Normal'
# SPEECH OUTPUT: 'scrollable notebooks and hidden tabs'
# SPEECH OUTPUT: 'row 1 of 14'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
 
########################################################################
# Close the GtkListStore demo
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
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
