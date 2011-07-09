#!/usr/bin/python

"""Test of dialog autoreading using the gtk-demo Expander button demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Expander demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Expander", 1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
#sequence.append(WaitForWindowActivate("GtkExpander",None))
sequence.append(WaitAction("object:state-changed:focused",
                           None,
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Dialog automatic reading",
    ["BRAILLE LINE:  'gtk-demo Application Window Expander $l'",
     "     VISIBLE:  'emo Application Window Exp $l ', cursor=32",
     "BRAILLE LINE:  'gtk-demo Application Window  $l'",
     "     VISIBLE:  'gtk-demo Application Window  $l', cursor=29",
     "BRAILLE LINE:  'gtk-demo Application Window  $l'",
     "     VISIBLE:  'gtk-demo Application Window  $l', cursor=29",
     "BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) Page ScrollPane TreeTable Widget (double click for demo) ColumnHeader Expander TREE LEVEL 1'",
     "     VISIBLE:  'Expander TREE LEVEL 1', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog'",
     "     VISIBLE:  'GtkExpander Dialog', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'",
     "     VISIBLE:  '& y Details ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'Widget (double click for demo) page Widget (double click for demo) column header Expander tree level 1'",
     "SPEECH OUTPUT: 'GtkExpander Expander demo. Click on the triangle for details.'",
     "SPEECH OUTPUT: 'Details toggle button not pressed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Dialog Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'",
     "     VISIBLE:  '& y Details ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'Details'",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

########################################################################
# Now close the demo and leave.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
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
