#!/usr/bin/python

"""Test of toggle button output using the gtk-demo Expander button demo.
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
sequence.append(WaitForFocus("Details", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Toggle button initial focus",
    ["BRAILLE LINE:  'Window Expander $l'",
     "     VISIBLE:  'Window Expander $l', cursor=16",
     "BRAILLE LINE:  'Window Expander $l'",
     "     VISIBLE:  'Window Expander $l', cursor=8",
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
    "Toggle button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'",
     "     VISIBLE:  '& y Details ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'Details toggle button not pressed'"]))

########################################################################
# Toggle the state of the "Details" button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:state-changed:expanded",
                           "Details",
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Toggle button pressed",
    ["BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog &=y Details ToggleButton'",
     "     VISIBLE:  '&=y Details ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'pressed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Toggle button pressed Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog &=y Details ToggleButton'",
     "     VISIBLE:  '&=y Details ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'Details toggle button pressed'"]))

########################################################################
# Toggle the state of the "Details" button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:state-changed:expanded",
                           "Details",
                           None,
                           pyatspi.ROLE_TOGGLE_BUTTON,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Toggle button not pressed",
    ["BRAILLE LINE:  'gtk-demo Application GtkExpander Dialog & y Details ToggleButton'",
     "     VISIBLE:  '& y Details ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

########################################################################
# Close the demo.
#
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Close", acc_role=pyatspi.ROLE_PUSH_BUTTON))
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
