#!/usr/bin/python

"""Test of tree table output using the gtk-demo Tree Store demo
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
# Once gtk-demo is running, invoke the Tree Store demo
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
sequence.append(TypeAction("Tree Store", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Card planning sheet demo window appears, the following should
# be presented [[[BUG?: is the duplication of Holiday ColumnHeader in
# braille a bug?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader Holiday ColumnHeader'
#      VISIBLE:  'Holiday ColumnHeader', cursor=1
#
# SPEECH OUTPUT: 'Card planning sheet frame'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Holiday column header'
#
#sequence.append(WaitForWindowActivate("Card planning sheet",None))
sequence.append(WaitForFocus("Holiday",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))

########################################################################
# Down arrow twice to select the "January" cell.  The following should
# be presented when the "January" cell is selected:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded TREE LEVEL 1 < > Alex < > Havoc < > Tim < > Owen < > Dave'
#      VISIBLE:  'January expanded TREE LEVEL 1 < ', cursor=1
#
# SPEECH OUTPUT: 'January expanded 3 items Alex check box not checked  Havoc check box not checked  Tim check box not checked  Owen check box not checked  Dave check box not checked '
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should column header be presented?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded TREE LEVEL 1 < > Alex < > Havoc < > Tim < > Owen < > Dave'
#      VISIBLE:  'January expanded TREE LEVEL 1 < ', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: 'January'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 1 of 53'
# SPEECH OUTPUT: 'expanded'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("KP_Enter"))

########################################################################
# Collapse the cell.  The following should be presented [[[BUG?: should
# "January" be spoken -- it violates the rule of not speaking the name
# if the object already has focus.]]]:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January collapsed TREE LEVEL 1 < > Alex < > Havoc < > Tim < > Owen < > Dave'
#      VISIBLE:  'January collapsed TREE LEVEL 1 <', cursor=1
#
# SPEECH OUTPUT: 'January collapsed'
#
sequence.append(KeyComboAction("<Shift>Left", 500))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should column header be presented?]]]:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January collapsed TREE LEVEL 1 < > Alex < > Havoc < > Tim < > Owen < > Dave'
#      VISIBLE:  'January collapsed TREE LEVEL 1 <', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: 'January'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 1 of 50'
# SPEECH OUTPUT: 'collapsed'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Expand the cell again.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded TREE LEVEL 1 < > Alex < > Havoc < > Tim < > Owen < > Dave'
#      VISIBLE:  'January expanded TREE LEVEL 1 < ', cursor=1
#
# SPEECH OUTPUT: 'January expanded 3 items'
#
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

########################################################################
# Arrow down a row.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader New Years Day TREE LEVEL 2'
#      VISIBLE:  'New Years Day TREE LEVEL 2', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New Years Day Alex check box checked  Havoc check box checked  Tim check box checked  Owen check box checked  Dave check box not checked '
# SPEECH OUTPUT: 'tree level 2'
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

########################################################################
# Arrow right to a column.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader <x> Alex'
#      VISIBLE:  '<x> Alex', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Alex column header'
# SPEECH OUTPUT: 'check box checked '
#
sequence.append(KeyComboAction("<Control>Right", 500))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))


#
# [[[BUG?: Somewhere around here, the demo flakes out.]]]
#

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented [[[BUG?: should column header be presented?]]] [[[BUG?: why
# is 'New Years Day' presented?  It should be the check box.]]]:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader New Years Day TREE LEVEL 2'
#      VISIBLE:  'New Years Day TREE LEVEL 2', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'cell'
# SPEECH OUTPUT: 'New Years Day'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'row 2 of 53'
# SPEECH OUTPUT: 'tree level 2'
#
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Change the state of the checkbox.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader < > Alex'
#      VISIBLE:  '< > Alex', cursor=1
#
# SPEECH OUTPUT: 'not checked '
#
sequence.append(KeyComboAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

########################################################################
# Change the state of the checkbox.  The following should be presented:
#
# BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader <x> Alex'
#      VISIBLE:  '<x> Alex', cursor=1
#
# SPEECH OUTPUT: 'checked '
#
sequence.append(KeyComboAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

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
