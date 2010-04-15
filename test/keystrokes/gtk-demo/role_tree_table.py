#!/usr/bin/python

"""Test of tree table output using the gtk-demo Tree Store demo
   under the Tree View area.
"""

from macaroon.playback import *
import utils

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

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
#sequence.append(WaitForWindowActivate("Card planning sheet",None))
sequence.append(WaitForFocus("Holiday",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(utils.AssertPresentationAction(
    "Tree table initial focus",
    ["BRAILLE LINE:  'Window Tree Store $l'",
     "     VISIBLE:  'Window Tree Store $l', cursor=18",
     "BRAILLE LINE:  'Window Tree Store $l'",
     "     VISIBLE:  'Window Tree Store $l', cursor=8",
     "BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) Page ScrollPane TreeTable Widget (double click for demo) ColumnHeader Tree Store TREE LEVEL 2'",
     "     VISIBLE:  'Tree Store TREE LEVEL 2', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame'",
     "     VISIBLE:  'Card planning sheet Frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader'",
     "     VISIBLE:  'Holiday ColumnHeader', cursor=1",
     "SPEECH OUTPUT: 'Widget (double click for demo) page Widget (double click for demo) column header Tree Store tree level 2'",
     "SPEECH OUTPUT: 'Card planning sheet frame'",
     "SPEECH OUTPUT: 'Holiday column header'"]))

########################################################################
# Down arrow twice to select the "January" cell.
#
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "January cell focus",
    ["SPEECH OUTPUT: 'selected'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "January cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday cell January column 1 of 6 row 1 of 53 expanded tree level 1'"]))

########################################################################
# Do a detailed "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "January cell detailed Where Am I",
    ["KNOWN ISSUE - We used to speak that there were three items in the second speech output line; now we do not. Need to investigate.",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday cell January column 1 of 6 row 1 of 53 expanded tree level 1'",
     "SPEECH OUTPUT: 'tree table Holiday cell January column 1 of 6 row 1 of 53 January expanded Alex check box not checked Havoc check box not checked Tim check box not checked Owen check box not checked Dave check box not checked expanded tree level 1'"]))

########################################################################
# Collapse the cell.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Left", 500))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "January cell collapsed",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "January cell collapsed basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday cell January column 1 of 6 row 1 of 50 collapsed tree level 1'"]))

########################################################################
# Do a detailed "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "January cell collapsed detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January collapsed < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January collapsed < > Alex < > H', cursor=1",
     "SPEECH OUTPUT: 'tree table Holiday cell January column 1 of 6 row 1 of 50 collapsed tree level 1'",
     "SPEECH OUTPUT: 'tree table Holiday cell January column 1 of 6 row 1 of 50 January collapsed Alex check box not checked Havoc check box not checked Tim check box not checked Owen check box not checked Dave check box not checked collapsed tree level 1'"]))

########################################################################
# Expand the cell again.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "January cell expanded",
    ["KNOWN ISSUE - We used to speak that there were three items in the second speech output line; now we do not. Need to investigate.",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader January expanded < > Alex < > Havoc < > Tim < > Owen < > Dave TREE LEVEL 1'",
     "     VISIBLE:  'January expanded < > Alex < > Ha', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

########################################################################
# Arrow down a row.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "New Year's Day cell",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Holiday ColumnHeader New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave TREE LEVEL 2'",
     "     VISIBLE:  'New Years Day <x> Alex <x> Havoc', cursor=1",
     "SPEECH OUTPUT: 'New Years Day Alex check box checked Havoc check box checked Tim check box checked Owen check box checked Dave check box not checked tree level 2'"]))

########################################################################
# Arrow right to a column.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right", 500))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'Alex column header check box checked'"]))

#
# [[[BUG?: Somewhere around here, the demo flakes out.]]]
#

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'tree table Alex cell check box checked column 2 of 6 row 2 of 53'"]))

########################################################################
# Do a detailed "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'tree table Alex cell check box checked column 2 of 6 row 2 of 53'",
     "SPEECH OUTPUT: 'tree table Alex cell check box checked column 2 of 6 row 2 of 53 New Years Day Alex check box checked Havoc check box checked Tim check box checked Owen check box checked Dave check box not checked'"]))

########################################################################
# Change the state of the checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell unchecked",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader New Years Day < > Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '< > Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'not checked'"]))

########################################################################
# Change the state of the checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:state-changed:checked",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Alex checkbox cell checked",
    ["BRAILLE LINE:  'gtk-demo Application Card planning sheet Frame ScrollPane TreeTable Alex ColumnHeader New Years Day <x> Alex <x> Havoc <x> Tim <x> Owen < > Dave'",
     "     VISIBLE:  '<x> Alex <x> Havoc <x> Tim <x> O', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
