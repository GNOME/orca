#!/usr/bin/python

"""Test of table output using the gtk-demo Editable Cells demo
   under the Tree View area.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Editable Cells demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(PauseAction(1000))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(PauseAction(1000))
sequence.append(TypeAction("Editable Cells", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Table Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 3 bottles of coke'",
     "     VISIBLE:  '3 bottles of coke', cursor=1",
     "SPEECH OUTPUT: 'table Number cell 3 column 1 of 3 row 1 of 5'"]))

########################################################################
# Down arrow to the next line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Table down one line",
    ["BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 5 packages of noodles'",
     "     VISIBLE:  '5 packages of noodles', cursor=1",
     "SPEECH OUTPUT: '5 packages of noodles'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "Table Where Am I (again)",
    ["BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 5 packages of noodles'",
     "     VISIBLE:  '5 packages of noodles', cursor=1",
     "SPEECH OUTPUT: 'table Number cell 5 column 1 of 3 row 2 of 5'"]))

########################################################################
# Turn reading of rows off.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None,"KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None,"KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Turn row reading off",
    ["BRAILLE LINE:  'Speak cell'",
     "     VISIBLE:  'Speak cell', cursor=0",
     "SPEECH OUTPUT: 'Speak cell'"]))

########################################################################
# Move right one cell to the "packages of noodles" cell and then go
# up one line to "bottles of coke".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right", 500))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Table Right to the Product column in the packages of noodles row",
    ["BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Number ColumnHeader 5 packages of noodles'",
     "     VISIBLE:  '5 packages of noodles', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Product ColumnHeader packages of noodles Cell'",
     "     VISIBLE:  'packages of noodles Cell', cursor=1",
     "SPEECH OUTPUT: 'Product column header packages of noodles'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up", 500))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Table up to bottles of coke",
    ["BRAILLE LINE:  'gtk-demo Application Shopping list Frame ScrollPane Table Product ColumnHeader bottles of coke Cell'",
     "     VISIBLE:  'bottles of coke Cell', cursor=1",
     "SPEECH OUTPUT: 'bottles of coke'"]))

########################################################################
# Close the Shopping list demo
#
sequence.append(KeyComboAction("<Alt>F4", 1000))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(PauseAction(1000))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
