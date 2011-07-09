#!/usr/bin/python

"""Test of page tab output using the gtk-demo Printing demo
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Printing demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Button Boxes", 1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "OK button",
    ["BRAILLE LINE:  'gtk-demo Application Window  $l'",
     "     VISIBLE:  'gtk-demo Application Window  $l', cursor=29",
     "BRAILLE LINE:  'gtk-demo Application Window  $l'",
     "     VISIBLE:  'gtk-demo Application Window  $l', cursor=29",
     "BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) Page ScrollPane TreeTable Widget (double click for demo) ColumnHeader Button Boxes TREE LEVEL 1",
     "     VISIBLE:  'Button Boxes TREE LEVEL 1', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Button Boxes Frame'",
     "     VISIBLE:  'Button Boxes Frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Spread Panel OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'Widget (double click for demo) page Widget (double click for demo) column header Button Boxes tree level 1'",
     "SPEECH OUTPUT: 'Button Boxes frame'",
     "SPEECH OUTPUT: 'Horizontal Button Boxes panel Spread panel OK button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "OK button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Spread Panel OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'OK",
     "SPEECH OUTPUT: 'button.",
     "SPEECH OUTPUT: 'Alt o'"]))

########################################################################
# Tab to the Cancel button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Cancel button",
    ["BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Spread Panel Cancel Button'",
     "     VISIBLE:  'Cancel Button', cursor=1",
     "SPEECH OUTPUT: 'Cancel button'"]))

########################################################################
# Tab to the next "OK" button in the "Edge" panel.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Help", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "OK Edge button",
    ["BRAILLE LINE:  'gtk-demo Application Button Boxes Frame Horizontal Button Boxes Panel Edge Panel OK Button'",
     "     VISIBLE:  'OK Button', cursor=1",
     "SPEECH OUTPUT: 'Edge panel OK button'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
