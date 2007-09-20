#!/usr/bin/python

"""Test of table output using the gtk-demo Editable Cells demo
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
# Once gtk-demo is running, invoke the Editable Cells demo
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
sequence.append(TypeAction("Editable Cells", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Shopping list demo window appears, the following should be
# presented:
#
# BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 3 bottles of coke'
#      VISIBLE:  '3 bottles of coke', cursor=1
#
# SPEECH OUTPUT: 'Shopping list frame'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Number column header'
# SPEECH OUTPUT: '3 bottles of coke'
#
#sequence.append(WaitForWindowActivate("Shopping list",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TABLE))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: No column header information output?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 3 bottles of coke'
#      VISIBLE:  '3 bottles of coke', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: '3'
# SPEECH OUTPUT: 'bottles of coke'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 1 of 5'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Down arrow to the next line.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 5 packages of noodles'
#      VISIBLE:  '5 packages of noodles', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: '5 packages of noodles'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: No column header information output?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 5'
#      VISIBLE:  '5', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: '5'
# SPEECH OUTPUT: 'packages of noodles'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 2 of 5'
#
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Turn reading of rows off.
#
sequence.append(KeyPressAction(0, None,"KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None,"KP_Insert"))

########################################################################
# Move right one cell to the "packages of noodles" cell and then go
# up one line to "bottles of coke".  The following should be presented
# when "bottles of coke" gets focus:
#
# BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Product ColumnHeader bottles of coke Cell'
#      VISIBLE:  'bottles of coke Cell', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'bottles of coke'
#
sequence.append(KeyComboAction("<Control>Right", 500))
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
